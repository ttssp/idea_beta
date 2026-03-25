
"""
Delegation Runtime Service

委托档位管理、预算管理
"""
from typing import Dict, List, Optional
from uuid import UUID
from datetime import datetime, timedelta

from ..common.constants import DelegationLevel, SYSTEM_DELEGATION_PROFILES
from ..common.exceptions import (
    InvalidDelegationProfileError,
    BudgetExceededError,
)
from .models import (
    DelegationProfile,
    BudgetUsage,
    ThreadDelegationBinding,
    RelationshipDelegationBinding,
)


class DelegationService:
    """委托档位服务"""

    def __init__(self):
        # 内存存储（实际项目中应使用数据库）
        self._profiles: Dict[UUID, DelegationProfile] = {}
        self._thread_bindings: Dict[UUID, ThreadDelegationBinding] = {}
        self._relationship_bindings: Dict[UUID, RelationshipDelegationBinding] = {}
        self._budget_usages: Dict[UUID, List[BudgetUsage]] = {}
        self._initialize_system_profiles()

    def _initialize_system_profiles(self):
        """初始化系统默认档位"""
        for profile_data in SYSTEM_DELEGATION_PROFILES:
            profile = DelegationProfile(
                name=profile_data["name"],
                display_name=profile_data["display_name"],
                description=profile_data["description"],
                profile_level=profile_data["profile_level"],
                allowed_actions=profile_data["allowed_actions"],
                budget_config=profile_data["budget_config"],
                escalation_rules=profile_data["escalation_rules"],
                is_system_defined=profile_data["is_system_defined"],
            )
            self._profiles[profile.id] = profile

    def get_profile(self, profile_id: UUID) -> Optional[DelegationProfile]:
        """获取委托档位"""
        return self._profiles.get(profile_id)

    def get_profile_by_name(self, name: str) -> Optional[DelegationProfile]:
        """通过名称获取委托档位"""
        for profile in self._profiles.values():
            if profile.name == name:
                return profile
        return None

    def list_profiles(self, include_system: bool = True) -> List[DelegationProfile]:
        """列出所有可用档位"""
        profiles = list(self._profiles.values())
        if not include_system:
            profiles = [p for p in profiles if not p.is_system_defined]
        return profiles

    def create_profile(
        self,
        name: str,
        display_name: str,
        profile_level: DelegationLevel,
        allowed_actions: List[str],
        description: Optional[str] = None,
        budget_config: Optional[Dict] = None,
        escalation_rules: Optional[Dict] = None,
    ) -> DelegationProfile:
        """创建自定义委托档位"""
        if self.get_profile_by_name(name):
            raise InvalidDelegationProfileError(f"Profile with name '{name}' already exists")

        profile = DelegationProfile(
            name=name,
            display_name=display_name,
            description=description,
            profile_level=profile_level,
            allowed_actions=allowed_actions,
            budget_config=budget_config,
            escalation_rules=escalation_rules,
            is_system_defined=False,
        )
        self._profiles[profile.id] = profile
        return profile

    def update_profile(
        self,
        profile_id: UUID,
        **kwargs,
    ) -> Optional[DelegationProfile]:
        """更新委托档位"""
        profile = self._profiles.get(profile_id)
        if not profile:
            return None
        if profile.is_system_defined:
            raise InvalidDelegationProfileError("Cannot modify system-defined profiles")

        for key, value in kwargs.items():
            if hasattr(profile, key):
                setattr(profile, key, value)
        profile.updated_at = datetime.utcnow()
        return profile

    def bind_thread_profile(
        self,
        thread_id: UUID,
        profile_id: UUID,
        bound_by: Optional[UUID] = None,
    ) -> ThreadDelegationBinding:
        """绑定线程委托档位"""
        if profile_id not in self._profiles:
            raise InvalidDelegationProfileError(f"Profile {profile_id} not found")

        binding = ThreadDelegationBinding(
            thread_id=thread_id,
            profile_id=profile_id,
            bound_by=bound_by,
            bound_at=datetime.utcnow(),
            is_active=True,
        )
        self._thread_bindings[thread_id] = binding
        return binding

    def bind_relationship_profile(
        self,
        relationship_id: UUID,
        profile_id: UUID,
        bound_by: Optional[UUID] = None,
    ) -> RelationshipDelegationBinding:
        """绑定关系默认委托档位"""
        if profile_id not in self._profiles:
            raise InvalidDelegationProfileError(f"Profile {profile_id} not found")

        binding = RelationshipDelegationBinding(
            relationship_id=relationship_id,
            profile_id=profile_id,
            bound_by=bound_by,
            bound_at=datetime.utcnow(),
            is_active=True,
        )
        self._relationship_bindings[relationship_id] = binding
        return binding

    def get_effective_profile(
        self,
        thread_id: Optional[UUID] = None,
        relationship_id: Optional[UUID] = None,
    ) -> DelegationProfile:
        """
        获取有效委托档位

        优先级：Thread > Relationship > System Default (Observe Only)
        """
        # 1. 检查线程级绑定
        if thread_id and thread_id in self._thread_bindings:
            binding = self._thread_bindings[thread_id]
            if binding.is_active and binding.profile_id in self._profiles:
                return self._profiles[binding.profile_id]

        # 2. 检查关系级绑定
        if relationship_id and relationship_id in self._relationship_bindings:
            binding = self._relationship_bindings[relationship_id]
            if binding.is_active and binding.profile_id in self._profiles:
                return self._profiles[binding.profile_id]

        # 3. 返回系统默认（Observe Only）
        default_profile = self.get_profile_by_name("observe_only")
        if not default_profile:
            # 兜底：返回第一个系统定义的档位
            for profile in self._profiles.values():
                if profile.is_system_defined:
                    return profile
        return default_profile

    def check_budget(
        self,
        thread_id: UUID,
        action_type: str,
        profile: DelegationProfile,
    ) -> bool:
        """
        检查动作预算是否超限

        Returns:
            True if budget is available, False otherwise
        """
        if not profile.budget_config:
            return True

        budget_config = profile.budget_config
        max_count = budget_config.get("max_messages_per_day", 100)
        window_hours = budget_config.get("window_hours", 24)

        # 计算当前窗口
        now = datetime.utcnow()
        window_start = now - timedelta(hours=window_hours)

        # 获取当前使用量
        current_usage = self._get_budget_usage(thread_id, action_type, window_start, now)
        return current_usage < max_count

    def consume_budget(
        self,
        thread_id: UUID,
        action_type: str,
        profile: DelegationProfile,
    ) -> bool:
        """
        消耗预算计数

        Returns:
            True if budget was consumed, False if budget exceeded
        """
        if not self.check_budget(thread_id, action_type, profile):
            raise BudgetExceededError(f"Budget exceeded for action {action_type}")

        # 记录预算使用
        now = datetime.utcnow()
        window_hours = profile.budget_config.get("window_hours", 24) if profile.budget_config else 24
        window_start = now - timedelta(hours=window_hours)
        window_end = window_start + timedelta(hours=window_hours)

        if thread_id not in self._budget_usages:
            self._budget_usages[thread_id] = []

        usage = BudgetUsage(
            thread_id=thread_id,
            profile_id=profile.id,
            action_type=action_type,
            count=1,
            window_start=window_start,
            window_end=window_end,
        )
        self._budget_usages[thread_id].append(usage)
        return True

    def _get_budget_usage(
        self,
        thread_id: UUID,
        action_type: str,
        window_start: datetime,
        window_end: datetime,
    ) -> int:
        """获取预算使用量"""
        if thread_id not in self._budget_usages:
            return 0

        count = 0
        for usage in self._budget_usages[thread_id]:
            if (
                usage.action_type == action_type
                and usage.window_start <= window_end
                and usage.window_end >= window_start
            ):
                count += usage.count
        return count

    def reset_budget(self, thread_id: UUID):
        """重置线程预算"""
        if thread_id in self._budget_usages:
            self._budget_usages[thread_id] = []
