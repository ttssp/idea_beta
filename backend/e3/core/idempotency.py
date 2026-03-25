
"""
Idempotency Key Manager

Provides idempotency guarantee using Redis + PostgreSQL.
"""

import hashlib
import json
from typing import Any, Optional, Tuple
from datetime import timedelta
from redis.asyncio import Redis as AsyncRedis


class IdempotencyManager:
    """
    幂等键管理器

    三层幂等保障：
    1. Redis缓存（快速检查）
    2. 数据库UNIQUE约束（最终保障）
    3. 外部API幂等键（Gmail threadId, Calendar iCalUID）
    """

    def __init__(
        self,
        redis: AsyncRedis,
        ttl: timedelta = timedelta(hours=24)
    ):
        self.redis = redis
        self.ttl = ttl

    def generate_key(self, *components: Any) -&gt; str:
        """
        根据组件生成幂等键

        Args:
            *components: 用于生成幂等键的组件

        Returns:
            SHA256哈希后的幂等键
        """
        serialized = json.dumps(components, sort_keys=True, default=str)
        return hashlib.sha256(serialized.encode()).hexdigest()

    async def check_and_set(
        self,
        key: str,
        value: str = "processing"
    ) -&gt; Tuple[bool, Optional[str]]:
        """
        检查并设置幂等键

        Args:
            key: 幂等键
            value: 要设置的值

        Returns:
            (是否可以继续, 之前的结果如果有)
        """
        # 使用Redis SETNX
        was_set = await self.redis.set(
            f"idempotency:{key}",
            value,
            ex=int(self.ttl.total_seconds()),
            nx=True
        )

        if was_set:
            return True, None

        # 已存在，获取之前的结果
        previous_result = await self.redis.get(f"idempotency:result:{key}")
        if previous_result:
            if isinstance(previous_result, bytes):
                previous_result = previous_result.decode()
        return False, previous_result

    async def store_result(self, key: str, result: str):
        """
        存储幂等操作的结果

        Args:
            key: 幂等键
            result: 结果字符串（通常是JSON）
        """
        await self.redis.setex(
            f"idempotency:result:{key}",
            int(self.ttl.total_seconds()),
            result
        )

    async def mark_completed(self, key: str):
        """标记操作完成"""
        await self.redis.setex(
            f"idempotency:{key}",
            int(self.ttl.total_seconds()),
            "completed"
        )

    async def clear(self, key: str):
        """清除幂等键（用于测试/调试）"""
        await self.redis.delete(f"idempotency:{key}")
        await self.redis.delete(f"idempotency:result:{key}")

