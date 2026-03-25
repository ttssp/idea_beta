"""Principal 领域模型 - 统一主体模型（人/代理/外部方/服务方）"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


# ============================================
# 值对象 (Value Objects)
# ============================================

class PrincipalId(BaseModel):
    """Principal ID 值对象"""
    value: UUID

    @classmethod
    def generate(cls) -> "PrincipalId":
        return cls(value=uuid4())

    def __str__(self) -> str:
        return str(self.value)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PrincipalId):
            return NotImplemented
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)


class PrincipalType(str, Enum):
    """主体类型"""
    HUMAN = "human"
    AGENT = "agent"
    EXTERNAL = "external"
    SERVICE = "service"


class TrustTier(str, Enum):
    """信任等级"""
    TRUSTED = "trusted"
    KNOWN = "known"
    UNKNOWN = "unknown"
    BLOCKED = "blocked"


class DisclosureMode(str, Enum):
    """身份披露模式"""
    FULL = "full"
    SEMI = "semi"
    TEMPLATE = "template"
    HIDDEN = "hidden"


# ============================================
# Principal 实体
# ============================================

class Principal(BaseModel):
    """主体实体 - 统一"人/代理/外部方/服务方"身份"""
    model_config = {"arbitrary_types_allowed": True}

    # 标识
    id: PrincipalId = Field(default_factory=PrincipalId.generate)

    # 核心属性
    principal_type: PrincipalType
    display_name: str = Field(..., min_length=1, max_length=200)

    # 联系方式
    email: Optional[str] = None
    phone: Optional[str] = Field(None, max_length=50)
    external_id: Optional[str] = Field(None, max_length=255)

    # 信任与披露
    trust_tier: TrustTier = TrustTier.UNKNOWN
    disclosure_mode: DisclosureMode = DisclosureMode.SEMI
    disclosure_template: Optional[str] = Field(None, max_length=500)

    # 元数据
    is_active: bool = True
    is_verified: bool = False
    avatar_url: Optional[str] = Field(None, max_length=500)
    timezone: Optional[str] = Field(None, max_length=100)
    locale: Optional[str] = Field(None, max_length=20)

    # 时间戳
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_seen_at: Optional[datetime] = None

    # 乐观锁
    version: int = 1

    # 扩展数据
    metadata: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def create_human(
        cls,
        display_name: str,
        email: Optional[str] = None,
        is_verified: bool = False,
    ) -> "Principal":
        """创建人类主体"""
        return cls(
            principal_type=PrincipalType.HUMAN,
            display_name=display_name,
            email=email,
            trust_tier=TrustTier.KNOWN if is_verified else TrustTier.UNKNOWN,
            is_verified=is_verified,
        )

    @classmethod
    def create_agent(
        cls,
        display_name: str,
        agent_type: str,
    ) -> "Principal":
        """创建代理主体"""
        return cls(
            principal_type=PrincipalType.AGENT,
            display_name=display_name,
            trust_tier=TrustTier.TRUSTED,
            disclosure_mode=DisclosureMode.TEMPLATE,
            metadata={"agent_type": agent_type},
        )

    @classmethod
    def create_external(
        cls,
        display_name: str,
        email: Optional[str] = None,
        external_id: Optional[str] = None,
    ) -> "Principal":
        """创建外部方主体"""
        return cls(
            principal_type=PrincipalType.EXTERNAL,
            display_name=display_name,
            email=email,
            external_id=external_id,
            trust_tier=TrustTier.UNKNOWN,
        )

    @classmethod
    def create_service(
        cls,
        display_name: str,
        service_name: str,
    ) -> "Principal":
        """创建服务方主体"""
        return cls(
            principal_type=PrincipalType.SERVICE,
            display_name=display_name,
            trust_tier=TrustTier.TRUSTED,
            metadata={"service_name": service_name},
        )

    @property
    def is_human(self) -> bool:
        return self.principal_type == PrincipalType.HUMAN

    @property
    def is_agent(self) -> bool:
        return self.principal_type == PrincipalType.AGENT

    @property
    def is_external(self) -> bool:
        return self.principal_type == PrincipalType.EXTERNAL

    @property
    def is_service(self) -> bool:
        return self.principal_type == PrincipalType.SERVICE

    @property
    def is_trusted(self) -> bool:
        return self.trust_tier == TrustTier.TRUSTED

    @property
    def is_blocked(self) -> bool:
        return self.trust_tier == TrustTier.BLOCKED

    def update_display_name(self, name: str) -> None:
        """更新显示名称"""
        self.display_name = name[:200]
        self.updated_at = datetime.utcnow()

    def update_email(self, email: str, verified: bool = False) -> None:
        """更新邮箱"""
        self.email = email
        self.is_verified = verified
        self.updated_at = datetime.utcnow()

    def set_trust_tier(self, tier: TrustTier) -> None:
        """设置信任等级"""
        self.trust_tier = tier
        self.updated_at = datetime.utcnow()

    def set_disclosure_mode(self, mode: DisclosureMode) -> None:
        """设置披露模式"""
        self.disclosure_mode = mode
        self.updated_at = datetime.utcnow()

    def block(self) -> None:
        """阻止该主体"""
        self.trust_tier = TrustTier.BLOCKED
        self.is_active = False
        self.updated_at = datetime.utcnow()

    def unblock(self) -> None:
        """解除阻止"""
        self.trust_tier = TrustTier.UNKNOWN
        self.is_active = True
        self.updated_at = datetime.utcnow()

    def mark_seen(self) -> None:
        """标记为已见"""
        self.last_seen_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def increment_version(self) -> None:
        """版本号递增"""
        self.version += 1
