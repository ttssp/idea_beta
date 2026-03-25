"""核心领域模型"""

from myproj.core.domain.thread import (
    Thread,
    ThreadId,
    ThreadStatus,
    ThreadObjective,
    DelegationProfile,
    DelegationLevel,
    RiskLevel,
)
from myproj.core.domain.principal import (
    Principal,
    PrincipalId,
    PrincipalType,
    TrustTier,
    DisclosureMode,
)
from myproj.core.domain.relationship import (
    Relationship,
    RelationshipId,
    RelationshipClass,
    SensitivityLevel,
)
from myproj.core.domain.message import (
    Message,
    MessageId,
    AuthoredMode,
    ChannelType,
)
from myproj.core.domain.event import (
    ThreadEvent,
    EventId,
    EventType,
)
from myproj.core.domain.external_binding import (
    ExternalBinding,
    BindingId,
    ChannelType as ExternalChannelType,
    SyncState,
)

__all__ = [
    # Thread
    "Thread",
    "ThreadId",
    "ThreadStatus",
    "ThreadObjective",
    "DelegationProfile",
    "DelegationLevel",
    "RiskLevel",
    # Principal
    "Principal",
    "PrincipalId",
    "PrincipalType",
    "TrustTier",
    "DisclosureMode",
    # Relationship
    "Relationship",
    "RelationshipId",
    "RelationshipClass",
    "SensitivityLevel",
    # Message
    "Message",
    "MessageId",
    "AuthoredMode",
    "ChannelType",
    # Event
    "ThreadEvent",
    "EventId",
    "EventType",
    # ExternalBinding
    "ExternalBinding",
    "BindingId",
    "ExternalChannelType",
    "SyncState",
]
