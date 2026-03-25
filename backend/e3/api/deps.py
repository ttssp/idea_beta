
"""
API Dependencies

FastAPI dependency injection.
"""

from typing import AsyncGenerator
from fastapi import Depends, HTTPException, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db as get_db_session
from ..core.redis import get_redis
from ..core.idempotency import IdempotencyManager
from ..config import settings


async def get_db() -&gt; AsyncGenerator[AsyncSession, None]:
    """获取数据库会话"""
    async for session in get_db_session():
        yield session


async def get_idempotency_manager(
    redis=Depends(get_redis)
) -&gt; IdempotencyManager:
    """获取幂等键管理器"""
    from datetime import timedelta
    return IdempotencyManager(
        redis,
        ttl=timedelta(hours=settings.idempotency_ttl_hours)
    )


async def get_idempotency_key(
    idempotency_key: str = Header(None, alias="Idempotency-Key")
) -&gt; str:
    """从Header获取幂等键"""
    if not idempotency_key:
        raise HTTPException(
            status_code=400,
            detail="Idempotency-Key header is required"
        )
    return idempotency_key

