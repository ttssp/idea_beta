"""仓储接口"""

from myproj.core.repositories.base import BaseRepository
from myproj.core.repositories.thread_repository import ThreadRepository

__all__ = [
    "BaseRepository",
    "ThreadRepository",
]
