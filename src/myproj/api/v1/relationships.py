"""Relationship API 端点"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from myproj.api.deps import DbSession, Pagination, get_relationship_id
from myproj.api.exceptions import NotFoundError
from myproj.core.domain.relationship import (
    Relationship,
    RelationshipId,
    RelationshipClass,
    SensitivityLevel,
)
from myproj.core.domain.principal import PrincipalId

router = APIRouter(prefix="/relationships", tags=["relationships"])

# ============================================
# Pydantic Schemas
# ============================================

class RelationshipCreateSchema(BaseModel):
    """创建Relationship请求"""
    from_principal_id: UUID
    to_principal_id: UUID
    relationship_class: RelationshipClass
    sensitivity: SensitivityLevel = SensitivityLevel.MEDIUM
    alias: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = Field(None, max_length=2000)
    tags: List[str] = Field(default_factory=list)


class RelationshipUpdateSchema(BaseModel):
    """更新Relationship请求"""
    relationship_class: Optional[RelationshipClass] = None
    sensitivity: Optional[SensitivityLevel] = None
    alias: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = Field(None, max_length=2000)
    tags: Optional[List[str]] = None
    is_active: Optional[bool] = None
    is_favorite: Optional[bool] = None


class RelationshipResponseSchema(BaseModel):
    """Relationship响应"""
    id: UUID
    from_principal_id: UUID
    to_principal_id: UUID
    relationship_class: RelationshipClass
    sensitivity: SensitivityLevel
    alias: Optional[str]
    notes: Optional[str]
    tags: List[str]
    is_active: bool
    is_favorite: bool
    interaction_count: int
    first_interaction_at: Optional[datetime]
    last_interaction_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    version: int

    @classmethod
    def from_domain(cls, rel: Relationship) -> "RelationshipResponseSchema":
        return cls(
            id=rel.id.value,
            from_principal_id=rel.from_principal_id.value,
            to_principal_id=rel.to_principal_id.value,
            relationship_class=rel.relationship_class,
            sensitivity=rel.sensitivity,
            alias=rel.alias,
            notes=rel.notes,
            tags=rel.tags,
            is_active=rel.is_active,
            is_favorite=rel.is_favorite,
            interaction_count=rel.interaction_count,
            first_interaction_at=rel.first_interaction_at,
            last_interaction_at=rel.last_interaction_at,
            created_at=rel.created_at,
            updated_at=rel.updated_at,
            version=rel.version,
        )


class RelationshipListResponseSchema(BaseModel):
    """Relationship列表响应"""
    items: List[RelationshipResponseSchema]
    total: int
    offset: int
    limit: int


# ============================================
# 内存存储（临时，后续替换为数据库仓储）
# ============================================

_relationships: dict[RelationshipId, Relationship] = {}


# ============================================
# API 端点
# ============================================

@router.post(
    "",
    response_model=RelationshipResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="创建关系",
)
async def create_relationship(
    data: RelationshipCreateSchema,
) -> RelationshipResponseSchema:
    """创建新的Relationship"""
    try:
        relationship = Relationship.create(
            from_principal_id=PrincipalId(value=data.from_principal_id),
            to_principal_id=PrincipalId(value=data.to_principal_id),
            relationship_class=data.relationship_class,
            sensitivity=data.sensitivity,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e

    if data.alias:
        relationship.set_alias(data.alias)
    if data.notes:
        relationship.set_notes(data.notes)
    for tag in data.tags:
        relationship.add_tag(tag)

    _relationships[relationship.id] = relationship
    return RelationshipResponseSchema.from_domain(relationship)


@router.get(
    "",
    response_model=RelationshipListResponseSchema,
    summary="查询关系列表",
)
async def list_relationships(
    from_principal_id: Optional[UUID] = Query(None, description="发起方ID"),
    to_principal_id: Optional[UUID] = Query(None, description="目标方ID"),
    relationship_class: Optional[List[RelationshipClass]] = Query(None, description="关系类别过滤"),
    sensitivity: Optional[List[SensitivityLevel]] = Query(None, description="敏感度过滤"),
    is_active: Optional[bool] = Query(None, description="是否启用过滤"),
    is_favorite: Optional[bool] = Query(None, description="是否收藏过滤"),
    pagination: Pagination = Depends(),
) -> RelationshipListResponseSchema:
    """查询Relationship列表"""
    rels = list(_relationships.values())

    if from_principal_id:
        rels = [r for r in rels if r.from_principal_id.value == from_principal_id]

    if to_principal_id:
        rels = [r for r in rels if r.to_principal_id.value == to_principal_id]

    if relationship_class:
        rels = [r for r in rels if r.relationship_class in relationship_class]

    if sensitivity:
        rels = [r for r in rels if r.sensitivity in sensitivity]

    if is_active is not None:
        rels = [r for r in rels if r.is_active == is_active]

    if is_favorite is not None:
        rels = [r for r in rels if r.is_favorite == is_favorite]

    # 按更新时间倒序
    rels.sort(key=lambda r: r.updated_at, reverse=True)

    total = len(rels)
    items = rels[pagination.offset : pagination.offset + pagination.limit]

    return RelationshipListResponseSchema(
        items=[RelationshipResponseSchema.from_domain(r) for r in items],
        total=total,
        offset=pagination.offset,
        limit=pagination.limit,
    )


@router.get(
    "/{relationship_id}",
    response_model=RelationshipResponseSchema,
    summary="查询关系详情",
)
async def get_relationship(
    relationship_id: UUID = Depends(get_relationship_id),
) -> RelationshipResponseSchema:
    """获取Relationship详情"""
    rid = RelationshipId(value=relationship_id)
    rel = _relationships.get(rid)
    if not rel:
        raise NotFoundError(f"Relationship not found: {relationship_id}")

    return RelationshipResponseSchema.from_domain(rel)


@router.patch(
    "/{relationship_id}",
    response_model=RelationshipResponseSchema,
    summary="更新关系",
)
async def update_relationship(
    data: RelationshipUpdateSchema,
    relationship_id: UUID = Depends(get_relationship_id),
) -> RelationshipResponseSchema:
    """更新Relationship"""
    rid = RelationshipId(value=relationship_id)
    rel = _relationships.get(rid)
    if not rel:
        raise NotFoundError(f"Relationship not found: {relationship_id}")

    if data.relationship_class is not None:
        rel.update_relationship_class(data.relationship_class)

    if data.sensitivity is not None:
        rel.update_sensitivity(data.sensitivity)

    if data.alias is not None:
        rel.set_alias(data.alias)

    if data.notes is not None:
        rel.set_notes(data.notes)

    if data.tags is not None:
        rel.tags = data.tags
        rel.updated_at = datetime.utcnow()

    if data.is_favorite is not None and data.is_favorite != rel.is_favorite:
        rel.toggle_favorite()

    if data.is_active is not None:
        if data.is_active:
            rel.activate()
        else:
            rel.deactivate()

    rel.increment_version()
    return RelationshipResponseSchema.from_domain(rel)


@router.post(
    "/{relationship_id}/record-interaction",
    response_model=RelationshipResponseSchema,
    summary="记录交互",
)
async def record_interaction(
    relationship_id: UUID = Depends(get_relationship_id),
) -> RelationshipResponseSchema:
    """记录一次交互"""
    rid = RelationshipId(value=relationship_id)
    rel = _relationships.get(rid)
    if not rel:
        raise NotFoundError(f"Relationship not found: {relationship_id}")

    rel.record_interaction()
    rel.increment_version()
    return RelationshipResponseSchema.from_domain(rel)
