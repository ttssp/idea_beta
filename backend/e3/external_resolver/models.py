
"""
External Resolver Models (re-export from outbox_inbox)
"""

from ..outbox_inbox.models import BindingTypeEnum, ChannelTypeEnum, ExternalBinding, SyncStateEnum

__all__ = [
    "ExternalBinding",
    "BindingTypeEnum",
    "SyncStateEnum",
    "ChannelTypeEnum"
]

