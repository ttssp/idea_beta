
"""
Redis Connection Management
"""

from typing import Optional
from redis.asyncio import Redis as AsyncRedis, from_url
from ..config import settings

_redis_client: Optional[AsyncRedis] = None


async def get_redis() -&gt; AsyncRedis:
    """
    获取Redis客户端单例

    Returns:
        AsyncRedis实例
    """
    global _redis_client
    if _redis_client is None:
        _redis_client = from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True
        )
    return _redis_client


async def close_redis():
    """关闭Redis连接"""
    global _redis_client
    if _redis_client is not None:
        await _redis_client.close()
        _redis_client = None

