"""仓储接口"""

from myproj.core.repositories.base import BaseRepository
from myproj.core.repositories.event_repository import EventRepository
from myproj.core.repositories.message_repository import MessageRepository
from myproj.core.repositories.principal_repository import PrincipalRepository
from myproj.core.repositories.relationship_repository import RelationshipRepository
from myproj.core.repositories.thread_repository import ThreadRepository

__all__ = [
    "BaseRepository",
    "EventRepository",
    "MessageRepository",
    "PrincipalRepository",
    "RelationshipRepository",
    "ThreadRepository",
]
