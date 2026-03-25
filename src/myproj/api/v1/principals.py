"""Principal API 端点"""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel, Field

from myproj.api.deps import Pagination, get_principal_id
from myproj.api.exceptions import NotFoundError
from myproj.core.domain.principal import (
    DisclosureMode,
    Principal,
    PrincipalId,
    PrincipalType,
    TrustTier,
)

router = APIRouter(prefix="/principals", tags=["principals"])

# ============================================
# Pydantic Schemas
# ============================================

class PrincipalCreateSchema(BaseModel):
    """创建Principal请求"""
    principal_type: PrincipalType
    display_name: str = Field(..., min_length=1, max_length=200)
    email: str | None = None
    phone: str | None = Field(None, max_length=50)
    external_id: str | None = Field(None, max_length=255)
    trust_tier: TrustTier = TrustTier.UNKNOWN
    disclosure_mode: DisclosureMode = DisclosureMode.SEMI
    timezone: str | None = Field(None, max_length=100)
    locale: str | None = Field(None, max_length=20)


class PrincipalUpdateSchema(BaseModel):
    """更新Principal请求"""
    display_name: str | None = Field(None, min_length=1, max_length=200)
    email: str | None = None
    phone: str | None = Field(None, max_length=50)
    trust_tier: TrustTier | None = None
    disclosure_mode: DisclosureMode | None = None
    disclosure_template: str | None = Field(None, max_length=500)
    timezone: str | None = Field(None, max_length=100)
    locale: str | None = Field(None, max_length=20)
    is_active: bool | None = None


class PrincipalResponseSchema(BaseModel):
    """Principal响应"""
    id: UUID
    principal_type: PrincipalType
    display_name: str
    email: str | None
    phone: str | None
    external_id: str | None
    trust_tier: TrustTier
    disclosure_mode: DisclosureMode
    is_active: bool
    is_verified: bool
    timezone: str | None
    locale: str | None
    created_at: datetime
    updated_at: datetime
    version: int

    @classmethod
    def from_domain(cls, principal: Principal) -> "PrincipalResponseSchema":
        return cls(
            id=principal.id.value,
            principal_type=principal.principal_type,
            display_name=principal.display_name,
            email=principal.email,
            phone=principal.phone,
            external_id=principal.external_id,
            trust_tier=principal.trust_tier,
            disclosure_mode=principal.disclosure_mode,
            is_active=principal.is_active,
            is_verified=principal.is_verified,
            timezone=principal.timezone,
            locale=principal.locale,
            created_at=principal.created_at,
            updated_at=principal.updated_at,
            version=principal.version,
        )


class PrincipalListResponseSchema(BaseModel):
    """Principal列表响应"""
    items: list[PrincipalResponseSchema]
    total: int
    offset: int
    limit: int


# ============================================
# 内存存储（临时，后续替换为数据库仓储）
# ============================================

_principals: dict[PrincipalId, Principal] = {}


# ============================================
# API 端点
# ============================================

@router.post(
    "",
    response_model=PrincipalResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="创建主体",
)
async def create_principal(
    data: PrincipalCreateSchema,
) -> PrincipalResponseSchema:
    """创建新的Principal"""
    principal = Principal(
        principal_type=data.principal_type,
        display_name=data.display_name,
        email=data.email,
        phone=data.phone,
        external_id=data.external_id,
        trust_tier=data.trust_tier,
        disclosure_mode=data.disclosure_mode,
        timezone=data.timezone,
        locale=data.locale,
    )

    _principals[principal.id] = principal
    return PrincipalResponseSchema.from_domain(principal)


@router.get(
    "",
    response_model=PrincipalListResponseSchema,
    summary="查询主体列表",
)
async def list_principals(
    pagination: Pagination,
    principal_type: list[PrincipalType] | None = Query(None, description="类型过滤"),
    trust_tier: list[TrustTier] | None = Query(None, description="信任等级过滤"),
    is_active: bool | None = Query(None, description="是否启用过滤"),
) -> PrincipalListResponseSchema:
    """查询Principal列表"""
    principals = list(_principals.values())

    if principal_type:
        principals = [p for p in principals if p.principal_type in principal_type]

    if trust_tier:
        principals = [p for p in principals if p.trust_tier in trust_tier]

    if is_active is not None:
        principals = [p for p in principals if p.is_active == is_active]

    # 按更新时间倒序
    principals.sort(key=lambda p: p.updated_at, reverse=True)

    total = len(principals)
    items = principals[pagination.offset : pagination.offset + pagination.limit]

    return PrincipalListResponseSchema(
        items=[PrincipalResponseSchema.from_domain(p) for p in items],
        total=total,
        offset=pagination.offset,
        limit=pagination.limit,
    )


@router.get(
    "/{principal_id}",
    response_model=PrincipalResponseSchema,
    summary="查询主体详情",
)
async def get_principal(
    principal_id: UUID = Depends(get_principal_id),
) -> PrincipalResponseSchema:
    """获取Principal详情"""
    pid = PrincipalId(value=principal_id)
    principal = _principals.get(pid)
    if not principal:
        raise NotFoundError(f"Principal not found: {principal_id}")

    return PrincipalResponseSchema.from_domain(principal)


@router.patch(
    "/{principal_id}",
    response_model=PrincipalResponseSchema,
    summary="更新主体",
)
async def update_principal(
    data: PrincipalUpdateSchema,
    principal_id: UUID = Depends(get_principal_id),
) -> PrincipalResponseSchema:
    """更新Principal"""
    pid = PrincipalId(value=principal_id)
    principal = _principals.get(pid)
    if not principal:
        raise NotFoundError(f"Principal not found: {principal_id}")

    if data.display_name is not None:
        principal.update_display_name(data.display_name)

    if data.email is not None:
        principal.update_email(data.email, principal.is_verified)

    if data.phone is not None:
        principal.update_phone(data.phone)

    if data.trust_tier is not None:
        principal.set_trust_tier(data.trust_tier)

    if data.disclosure_mode is not None:
        principal.set_disclosure_mode(data.disclosure_mode)

    if data.disclosure_template is not None:
        principal.set_disclosure_template(data.disclosure_template)

    if data.timezone is not None:
        principal.set_timezone(data.timezone)

    if data.locale is not None:
        principal.set_locale(data.locale)

    if data.is_active is not None:
        if data.is_active:
            principal.activate()
        else:
            principal.deactivate()

    return PrincipalResponseSchema.from_domain(principal)


@router.post(
    "/{principal_id}/block",
    response_model=PrincipalResponseSchema,
    summary="阻止主体",
)
async def block_principal(
    principal_id: UUID = Depends(get_principal_id),
) -> PrincipalResponseSchema:
    """阻止Principal"""
    pid = PrincipalId(value=principal_id)
    principal = _principals.get(pid)
    if not principal:
        raise NotFoundError(f"Principal not found: {principal_id}")

    principal.block()
    return PrincipalResponseSchema.from_domain(principal)


@router.post(
    "/{principal_id}/unblock",
    response_model=PrincipalResponseSchema,
    summary="解除阻止",
)
async def unblock_principal(
    principal_id: UUID = Depends(get_principal_id),
) -> PrincipalResponseSchema:
    """解除阻止Principal"""
    pid = PrincipalId(value=principal_id)
    principal = _principals.get(pid)
    if not principal:
        raise NotFoundError(f"Principal not found: {principal_id}")

    principal.unblock()
    return PrincipalResponseSchema.from_domain(principal)
