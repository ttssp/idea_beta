"""核心领域模型"""

from myproj.core.domain.event import (
    EventId,
    EventType,
    ThreadEvent,
)
from myproj.core.domain.external_binding import (
    BindingId,
    ExternalBinding,
    SyncState,
)
from myproj.core.domain.external_binding import (
    ChannelType as ExternalChannelType,
)
from myproj.core.domain.message import (
    AuthoredMode,
    ChannelType,
    Message,
    MessageId,
)
from myproj.core.domain.principal import (
    DisclosureMode,
    Principal,
    PrincipalId,
    PrincipalType,
    TrustTier,
)
from myproj.core.domain.relationship import (
    Relationship,
    RelationshipClass,
    RelationshipId,
    SensitivityLevel,
)
from myproj.core.domain.thread import (
    DelegationLevel,
    DelegationProfile,
    RiskLevel,
    Thread,
    ThreadId,
    ThreadObjective,
    ThreadStatus,
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
