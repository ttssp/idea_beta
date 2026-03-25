
"""
Delegation Runtime Data Models
"""
from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from uuid import UUID, uuid4
from datetime import datetime

from ..common.constants import DelegationLevel


@dataclass
class DelegationProfile:
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    display_name: str = ""
    description: Optional[str] = None
    profile_level: DelegationLevel = DelegationLevel.OBSERVE_ONLY
    allowed_actions: list = field(default_factory=list)
    budget_config: Optional[Dict[str, Any]] = None
    escalation_rules: Optional[Dict[str, Any]] = None
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
    thread_id: Optional[UUID] = None
    relationship_id: Optional[UUID] = None
    profile_id: Optional[UUID] = None
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
    bound_by: Optional[UUID] = None
    bound_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True


@dataclass
class RelationshipDelegationBinding:
    id: UUID = field(default_factory=uuid4)
    relationship_id: UUID = field(default_factory=uuid4)
    profile_id: UUID = field(default_factory=uuid4)
    bound_by: Optional[UUID] = None
    bound_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True
