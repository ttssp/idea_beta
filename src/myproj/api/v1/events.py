"""Event API 端点"""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from myproj.api.deps import get_thread_id
from myproj.core.domain.event import EventType, ThreadEvent
from myproj.core.domain.thread import ThreadId
from myproj.core.services.thread_service import ThreadService

router = APIRouter(prefix="/threads/{thread_id}/events", tags=["events"])

# ============================================
# Pydantic Schemas
# ============================================

class EventResponseSchema(BaseModel):
    """Event响应"""
    id: UUID
    thread_id: UUID
    event_type: EventType
    occurred_at: datetime
    sequence_number: int
    title: str
    description: str | None
    payload: dict
    thread_status_before: str | None
    thread_status_after: str | None
    is_replayed: bool

    @classmethod
    def from_domain(cls, event: ThreadEvent) -> "EventResponseSchema":
        return cls(
            id=event.id.value,
            thread_id=event.thread_id.value,
            event_type=event.event_type,
            occurred_at=event.occurred_at,
            sequence_number=event.sequence_number,
            title=event.title,
            description=event.description,
            payload=event.payload,
            thread_status_before=event.thread_status_before.value if event.thread_status_before else None,
            thread_status_after=event.thread_status_after.value if event.thread_status_after else None,
            is_replayed=event.is_replayed,
        )


class EventListResponseSchema(BaseModel):
    """Event列表响应"""
    items: list[EventResponseSchema]
    total: int
    offset: int
    limit: int


class TimelineResponseSchema(BaseModel):
    """时间线响应"""
    items: list[dict]
    total: int


class EventSummaryResponseSchema(BaseModel):
    """事件摘要响应"""
    total_events: int
    status_changes: int
    messages: int
    approvals: int
    risks: int
    first_event_at: str | None
    last_event_at: str | None


# 共享的事件服务实例
_thread_service = ThreadService()


# ============================================
# API 端点
# ============================================

@router.get(
    "",
    response_model=EventListResponseSchema,
    summary="查询线程事件流",
)
async def list_events(
    thread_id: UUID = Depends(get_thread_id),
    event_type: list[EventType] | None = Query(None, description="事件类型过滤"),
    from_sequence: int | None = Query(None, description="起始序列号"),
    to_sequence: int | None = Query(None, description="结束序列号"),
    limit: int = Query(100, ge=1, le=1000, description="返回数量限制"),
    offset: int = Query(0, ge=0, description="偏移量"),
    reverse: bool = Query(False, description="是否倒序"),
) -> EventListResponseSchema:
    """查询Thread的事件流（append-only）"""
    tid = ThreadId(value=thread_id)
    event_store = _thread_service.get_event_store()

    events = event_store.get_by_thread(
        thread_id=tid,
        from_sequence=from_sequence,
        to_sequence=to_sequence,
        event_types=event_type,
        reverse=reverse,
    )

    total = len(events)
    items = events[offset : offset + limit]

    return EventListResponseSchema(
        items=[EventResponseSchema.from_domain(e) for e in items],
        total=total,
        offset=offset,
        limit=limit,
    )


@router.get(
    "/timeline",
    response_model=TimelineResponseSchema,
    summary="获取时间线视图",
)
async def get_timeline(
    thread_id: UUID = Depends(get_thread_id),
    limit: int = Query(100, ge=1, le=1000, description="返回数量限制"),
) -> TimelineResponseSchema:
    """获取Thread的时间线视图"""
    tid = ThreadId(value=thread_id)
    event_store = _thread_service.get_event_store()

    timeline = event_store.get_timeline(tid, limit=limit)

    return TimelineResponseSchema(
        items=timeline,
        total=len(timeline),
    )


@router.get(
    "/summary",
    response_model=EventSummaryResponseSchema,
    summary="获取事件摘要",
)
async def get_event_summary(
    thread_id: UUID = Depends(get_thread_id),
) -> EventSummaryResponseSchema:
    """获取Thread的事件摘要"""
    tid = ThreadId(value=thread_id)
    event_store = _thread_service.get_event_store()

    summary = event_store.get_summary(tid)

    return EventSummaryResponseSchema(**summary)


@router.get(
    "/status-history",
    response_model=list[dict],
    summary="获取状态变更历史",
)
async def get_status_history(
    thread_id: UUID = Depends(get_thread_id),
) -> list[dict]:
    """获取Thread的状态变更历史"""
    tid = ThreadId(value=thread_id)
    event_store = _thread_service.get_event_store()

    return event_store.get_status_history(tid)
