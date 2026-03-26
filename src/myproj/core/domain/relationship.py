"""Relationship 领域模型 - 关系语义模型"""

from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from myproj.core.domain.principal import PrincipalId
from myproj.core.domain.thread import DelegationProfile

# ============================================
# 值对象 (Value Objects)
# ============================================

class RelationshipId(BaseModel):
    """Relationship ID 值对象"""
    value: UUID

    @classmethod
    def generate(cls) -> "RelationshipId":
        return cls(value=uuid4())

    def __str__(self) -> str:
        return str(self.value)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RelationshipId):
            return NotImplemented
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)


class RelationshipClass(StrEnum):
    """关系类别 - 5种核心关系"""
    INTERNAL_COLLEAGUE = "internal_colleague"
    EXTERNAL_CANDIDATE = "external_candidate"
    CUSTOMER = "customer"
    VENDOR = "vendor"
    SENSITIVE_PERSONAL = "sensitive_personal"


class SensitivityLevel(StrEnum):
    """敏感度等级"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ============================================
# Relationship 实体
# ============================================

class Relationship(BaseModel):
    """关系实体 - 表达"我如何看待这个对象" """
    model_config = {"arbitrary_types_allowed": True}

    # 标识
    id: RelationshipId = Field(default_factory=RelationshipId.generate)

    # 关系双方
    from_principal_id: PrincipalId
    to_principal_id: PrincipalId

    # 关系语义
    relationship_class: RelationshipClass
    sensitivity: SensitivityLevel = SensitivityLevel.MEDIUM

    # 委托配置 - E2依赖
    default_delegation_profile: DelegationProfile | None = None
    custom_delegation_profile: DelegationProfile | None = None

    # 关系元数据
    alias: str | None = Field(None, max_length=200)
    notes: str | None = Field(None, max_length=2000)
    tags: list[str] = Field(default_factory=list)

    # 状态
    is_active: bool = True
    is_favorite: bool = False

    # 交互历史
    first_interaction_at: datetime | None = None
    last_interaction_at: datetime | None = None
    interaction_count: int = 0

    # 时间戳
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # 乐观锁
    version: int = 1

    # 扩展数据
    metadata: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def create(
        cls,
        from_principal_id: PrincipalId,
        to_principal_id: PrincipalId,
        relationship_class: RelationshipClass,
        sensitivity: SensitivityLevel = SensitivityLevel.MEDIUM,
    ) -> "Relationship":
        """创建关系"""
        if from_principal_id == to_principal_id:
            raise ValueError("Cannot create relationship with self")

        # 根据关系类别设置默认敏感度
        if relationship_class == RelationshipClass.SENSITIVE_PERSONAL:
            sensitivity = SensitivityLevel.CRITICAL
        elif relationship_class == RelationshipClass.CUSTOMER:
            sensitivity = SensitivityLevel.HIGH

        return cls(
            from_principal_id=from_principal_id,
            to_principal_id=to_principal_id,
            relationship_class=relationship_class,
            sensitivity=sensitivity,
        )

    @property
    def effective_delegation_profile(self) -> DelegationProfile:
        """获取有效的委托档位 - 自定义优先于默认"""
        if self.custom_delegation_profile:
            return self.custom_delegation_profile
        if self.default_delegation_profile:
            return self.default_delegation_profile
        return DelegationProfile.default_observe()

    @property
    def is_high_sensitivity(self) -> bool:
        """是否为高敏感度"""
        return self.sensitivity in {SensitivityLevel.HIGH, SensitivityLevel.CRITICAL}

    def update_relationship_class(
        self,
        relationship_class: RelationshipClass,
    ) -> None:
        """更新关系类别"""
        self.relationship_class = relationship_class

        # 自动调整敏感度
        if relationship_class == RelationshipClass.SENSITIVE_PERSONAL:
            self.sensitivity = SensitivityLevel.CRITICAL
        elif relationship_class == RelationshipClass.CUSTOMER:
            self.sensitivity = SensitivityLevel.HIGH

        self._mark_updated()

    def update_sensitivity(self, level: SensitivityLevel) -> None:
        """更新敏感度"""
        self.sensitivity = level
        self._mark_updated()

    def set_custom_delegation_profile(self, profile: DelegationProfile) -> None:
        """设置自定义委托档位"""
        self.custom_delegation_profile = profile
        self._mark_updated()

    def clear_custom_delegation_profile(self) -> None:
        """清除自定义委托档位"""
        self.custom_delegation_profile = None
        self._mark_updated()

    def set_default_delegation_profile(self, profile: DelegationProfile) -> None:
        """设置默认委托档位"""
        self.default_delegation_profile = profile
        self._mark_updated()

    def add_tag(self, tag: str) -> None:
        """添加标签"""
        if tag not in self.tags:
            self.tags.append(tag)
            self._mark_updated()

    def remove_tag(self, tag: str) -> None:
        """移除标签"""
        if tag in self.tags:
            self.tags.remove(tag)
            self._mark_updated()

    def replace_tags(self, tags: list[str]) -> None:
        """替换标签集合，并保持去重顺序。"""
        self.tags = list(dict.fromkeys(tags))
        self._mark_updated()

    def record_interaction(self) -> None:
        """记录交互"""
        now = datetime.utcnow()
        if not self.first_interaction_at:
            self.first_interaction_at = now
        self.last_interaction_at = now
        self.interaction_count += 1
        self._mark_updated(now)

    def set_alias(self, alias: str) -> None:
        """设置别名"""
        self.alias = alias[:200]
        self._mark_updated()

    def set_notes(self, notes: str) -> None:
        """设置备注"""
        self.notes = notes[:2000]
        self._mark_updated()

    def toggle_favorite(self) -> None:
        """切换收藏状态"""
        self.is_favorite = not self.is_favorite
        self._mark_updated()

    def deactivate(self) -> None:
        """停用关系"""
        self.is_active = False
        self._mark_updated()

    def activate(self) -> None:
        """启用关系"""
        self.is_active = True
        self._mark_updated()

    def increment_version(self) -> None:
        """版本号递增"""
        self.version += 1

    def _mark_updated(self, at: datetime | None = None) -> None:
        """统一维护更新时间和版本号。"""
        self.updated_at = at or datetime.utcnow()
        self.increment_version()
