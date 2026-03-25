
"""
Delegation Runtime Data Models
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from ..common.constants import DelegationLevel


@dataclass
class DelegationProfile:
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    display_name: str = ""
    description: str | None = None
    profile_level: DelegationLevel = DelegationLevel.OBSERVE_ONLY
    allowed_actions: list = field(default_factory=list)
    budget_config: dict[str, Any] | None = None
    escalation_rules: dict[str, Any] | None = None
    is_system_defined: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def can_perform_action(self, action):
        if self.profile_level == DelegationLevel.HUMAN_ONLY:
            return False
        if self.profile_level == DelegationLevel.OBSERVE_ONLY:
            return False
        return action in self.allowed_actions


@dataclass
class BudgetUsage:
    id: UUID = field(default_factory=uuid4)
    thread_id: UUID | None = None
    relationship_id: UUID | None = None
    profile_id: UUID | None = None
    action_type: str = ""
    count: int = 0
    window_start: datetime = field(default_factory=datetime.utcnow)
    window_end: datetime = field(default_factory=datetime.utcnow)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ThreadDelegationBinding:
    id: UUID = field(default_factory=uuid4)
    thread_id: UUID = field(default_factory=uuid4)
    profile_id: UUID = field(default_factory=uuid4)
    bound_by: UUID | None = None
    bound_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True


@dataclass
class RelationshipDelegationBinding:
    id: UUID = field(default_factory=uuid4)
    relationship_id: UUID = field(default_factory=uuid4)
    profile_id: UUID = field(default_factory=uuid4)
    bound_by: UUID | None = None
    bound_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True
