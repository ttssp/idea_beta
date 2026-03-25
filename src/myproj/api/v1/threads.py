"""Thread API 端点"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from myproj.api.deps import DbSession, Pagination, get_thread_id
from myproj.api.exceptions import NotFoundError, StateTransitionError
from myproj.core.domain.thread import (
    Thread,
    ThreadId,
    ThreadStatus,
    DelegationProfile,
    DelegationLevel,
    RiskLevel,
)
from myproj.core.services.thread_service import ThreadService

router = APIRouter(prefix="/threads", tags=["threads"])

# ============================================
# Pydantic Schemas
# ============================================

class ThreadObjectiveSchema(BaseModel):
    """Thread目标"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    due_at: Optional[datetime] = None


class DelegationProfileSchema(BaseModel):
    """委托档位"""
    profile_name: str = Field(..., min_length=1, max_length=100)
    level: DelegationLevel = DelegationLevel.OBSERVE_ONLY
    max_actions_per_hour: int = 10
    max_messages_per_thread: int = 50
    max_consecutive_touches: int = 3
    allowed_actions: List[str] = Field(default_factory=list)
    escalation_rules: dict = Field(default_factory=dict)


class ThreadCreateSchema(BaseModel):
    """创建Thread请求"""
    objective: ThreadObjectiveSchema
    owner_id: UUID
    delegation_profile: Optional[DelegationProfileSchema] = None
    participant_ids: List[UUID] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)


class ThreadUpdateSchema(BaseModel):
    """更新Thread请求"""
    objective: Optional[ThreadObjectiveSchema] = None
    summary: Optional[str] = Field(None, max_length=500)
    risk_level: Optional[RiskLevel] = None
    delegation_profile: Optional[DelegationProfileSchema] = None
    add_participant_ids: List[UUID] = Field(default_factory=list)
    remove_participant_ids: List[UUID] = Field(default_factory=list)


class ThreadResponseSchema(BaseModel):
    """Thread响应"""
    id: UUID
    objective: ThreadObjectiveSchema
    status: ThreadStatus
    risk_level: RiskLevel
    delegation_profile: Optional[DelegationProfileSchema]
    owner_id: UUID
    responsible_principal_id: Optional[UUID]
    participant_ids: List[UUID]
    summary: Optional[str]
    tags: List[str]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    version: int

    @classmethod
    def from_domain(cls, thread: Thread) -> "ThreadResponseSchema":
        return cls(
            id=thread.id.value,
            objective=ThreadObjectiveSchema(
                title=thread.objective.title,
                description=thread.objective.description,
                due_at=thread.objective.due_at,
            ),
            status=thread.status,
            risk_level=thread.risk_level,
            delegation_profile=DelegationProfileSchema(
                profile_name=thread.delegation_profile.profile_name,
                level=thread.delegation_profile.level,
                max_actions_per_hour=thread.delegation_profile.max_actions_per_hour,
                max_messages_per_thread=thread.delegation_profile.max_messages_per_thread,
                max_consecutive_touches=thread.delegation_profile.max_consecutive_touches,
                allowed_actions=thread.delegation_profile.allowed_actions,
                escalation_rules=thread.delegation_profile.escalation_rules,
            ) if thread.delegation_profile else None,
            owner_id=thread.owner_id,
            responsible_principal_id=thread.responsible_principal_id,
            participant_ids=thread.participant_ids,
            summary=thread.summary,
            tags=thread.tags,
            created_at=thread.created_at,
            updated_at=thread.updated_at,
            completed_at=thread.completed_at,
            version=thread.version,
        )


class ThreadListResponseSchema(BaseModel):
    """Thread列表响应"""
    items: List[ThreadResponseSchema]
    total: int
    offset: int
    limit: int


# ============================================
# 内存服务（临时，后续替换为数据库仓储）
# ============================================

_thread_service = ThreadService()


# ============================================
# API 端点
# ============================================

@router.post(
    "",
    response_model=ThreadResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="创建线程",
)
async def create_thread(
    data: ThreadCreateSchema,
) -> ThreadResponseSchema:
    """创建新的Thread"""
    delegation_profile = None
    if data.delegation_profile:
        delegation_profile = DelegationProfile(
            profile_name=data.delegation_profile.profile_name,
            level=data.delegation_profile.level,
            max_actions_per_hour=data.delegation_profile.max_actions_per_hour,
            max_messages_per_thread=data.delegation_profile.max_messages_per_thread,
            max_consecutive_touches=data.delegation_profile.max_consecutive_touches,
            allowed_actions=data.delegation_profile.allowed_actions,
            escalation_rules=data.delegation_profile.escalation_rules,
        )

    thread, _ = _thread_service.create_thread(
        title=data.objective.title,
        owner_id=data.owner_id,
        description=data.objective.description,
        due_at=data.objective.due_at,
        delegation_profile=delegation_profile,
        participant_ids=data.participant_ids,
        tags=data.tags,
    )

    return ThreadResponseSchema.from_domain(thread)


@router.get(
    "",
    response_model=ThreadListResponseSchema,
    summary="查询线程列表",
)
async def list_threads(
    owner_id: Optional[UUID] = Query(None, description="所有者ID过滤"),
    status: Optional[List[ThreadStatus]] = Query(None, description="状态过滤"),
    risk_level: Optional[List[RiskLevel]] = Query(None, description="风险等级过滤"),
    tags: Optional[List[str]] = Query(None, description="标签过滤"),
    pagination: Pagination = Depends(),
) -> ThreadListResponseSchema:
    """查询Thread列表，支持过滤和分页"""
    threads = _thread_service.list_threads(
        owner_id=owner_id,
        statuses=status,
        risk_levels=risk_level,
        tags=tags,
        limit=pagination.limit,
        offset=pagination.offset,
    )

    total = _thread_service.count_threads(
        owner_id=owner_id,
        statuses=status,
    )

    return ThreadListResponseSchema(
        items=[ThreadResponseSchema.from_domain(t) for t in threads],
        total=total,
        offset=pagination.offset,
        limit=pagination.limit,
    )


@router.get(
    "/{thread_id}",
    response_model=ThreadResponseSchema,
    summary="查询线程详情",
)
async def get_thread(
    thread_id: UUID = Depends(get_thread_id),
) -> ThreadResponseSchema:
    """获取Thread详情"""
    thread = _thread_service.get_thread_by_uuid(thread_id)
    if not thread:
        raise NotFoundError(f"Thread not found: {thread_id}")

    return ThreadResponseSchema.from_domain(thread)


@router.patch(
    "/{thread_id}",
    response_model=ThreadResponseSchema,
    summary="更新线程",
)
async def update_thread(
    data: ThreadUpdateSchema,
    thread_id: UUID = Depends(get_thread_id),
) -> ThreadResponseSchema:
    """更新Thread"""
    thread = _thread_service.get_thread_by_uuid(thread_id)
    if not thread:
        raise NotFoundError(f"Thread not found: {thread_id}")

    if thread.is_terminal:
        raise StateTransitionError("Cannot update terminal thread")

    # 更新目标
    if data.objective:
        _thread_service.update_objective(
            ThreadId(value=thread_id),
            title=data.objective.title,
            description=data.objective.description,
            due_at=data.objective.due_at,
        )

    # 更新摘要
    if data.summary is not None:
        _thread_service.update_summary(
            ThreadId(value=thread_id),
            data.summary,
        )

    # 更新风险等级
    if data.risk_level:
        _thread_service.update_risk_level(
            ThreadId(value=thread_id),
            data.risk_level,
            "Updated via API",
        )

    # 更新委托档位
    if data.delegation_profile:
        profile = DelegationProfile(
            profile_name=data.delegation_profile.profile_name,
            level=data.delegation_profile.level,
            max_actions_per_hour=data.delegation_profile.max_actions_per_hour,
            max_messages_per_thread=data.delegation_profile.max_messages_per_thread,
            max_consecutive_touches=data.delegation_profile.max_consecutive_touches,
            allowed_actions=data.delegation_profile.allowed_actions,
            escalation_rules=data.delegation_profile.escalation_rules,
        )
        _thread_service.update_delegation_profile(
            ThreadId(value=thread_id),
            profile,
        )

    # 添加参与者
    for pid in data.add_participant_ids:
        _thread_service.add_participant(
            ThreadId(value=thread_id),
            pid,
        )

    # 移除参与者
    for pid in data.remove_participant_ids:
        _thread_service.remove_participant(
            ThreadId(value=thread_id),
            pid,
        )

    thread = _thread_service.get_thread_by_uuid(thread_id)
    assert thread is not None
    return ThreadResponseSchema.from_domain(thread)


@router.post(
    "/{thread_id}/pause",
    response_model=ThreadResponseSchema,
    summary="暂停线程",
)
async def pause_thread(
    thread_id: UUID = Depends(get_thread_id),
) -> ThreadResponseSchema:
    """暂停Thread"""
    try:
        thread, _ = _thread_service.pause(ThreadId(value=thread_id))
    except ValueError as e:
        raise StateTransitionError(str(e)) from e

    return ThreadResponseSchema.from_domain(thread)


@router.post(
    "/{thread_id}/resume",
    response_model=ThreadResponseSchema,
    summary="恢复线程",
)
async def resume_thread(
    thread_id: UUID = Depends(get_thread_id),
) -> ThreadResponseSchema:
    """恢复Thread"""
    try:
        thread, _ = _thread_service.resume(ThreadId(value=thread_id))
    except ValueError as e:
        raise StateTransitionError(str(e)) from e

    return ThreadResponseSchema.from_domain(thread)


@router.post(
    "/{thread_id}/takeover",
    response_model=ThreadResponseSchema,
    summary="接管线程",
)
async def takeover_thread(
    reason: str = Body(..., embed=True, min_length=1),
    thread_id: UUID = Depends(get_thread_id),
) -> ThreadResponseSchema:
    """接管Thread - 升级到人工主导"""
    try:
        thread, _ = _thread_service.escalate(
            ThreadId(value=thread_id),
            reason,
        )
    except ValueError as e:
        raise StateTransitionError(str(e)) from e

    return ThreadResponseSchema.from_domain(thread)


@router.post(
    "/{thread_id}/complete",
    response_model=ThreadResponseSchema,
    summary="完成线程",
)
async def complete_thread(
    thread_id: UUID = Depends(get_thread_id),
) -> ThreadResponseSchema:
    """完成Thread"""
    try:
        thread, _ = _thread_service.complete(ThreadId(value=thread_id))
    except ValueError as e:
        raise StateTransitionError(str(e)) from e

    return ThreadResponseSchema.from_domain(thread)


@router.post(
    "/{thread_id}/cancel",
    response_model=ThreadResponseSchema,
    summary="取消线程",
)
async def cancel_thread(
    reason: Optional[str] = Body(None, embed=True),
    thread_id: UUID = Depends(get_thread_id),
) -> ThreadResponseSchema:
    """取消Thread"""
    try:
        thread, _ = _thread_service.cancel(
            ThreadId(value=thread_id),
            reason,
        )
    except ValueError as e:
        raise StateTransitionError(str(e)) from e

    return ThreadResponseSchema.from_domain(thread)
