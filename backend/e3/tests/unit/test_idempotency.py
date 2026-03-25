
"""
Unit Tests: Idempotency Manager

Tests for AR-I01 to AR-I04
"""

from datetime import timedelta
from unittest.mock import AsyncMock

import pytest

from ...core.idempotency import IdempotencyManager


class TestIdempotencyManager:
    """幂等键管理器测试"""

    @pytest.fixture
    def redis_mock(self):
        """Redis mock"""
        redis = AsyncMock()
        redis.set = AsyncMock(return_value=True)
        redis.get = AsyncMock(return_value=None)
        redis.delete = AsyncMock()
        redis.setex = AsyncMock()
        return redis

    @pytest.fixture
    def idempotency(self, redis_mock):
        """IdempotencyManager实例"""
        return IdempotencyManager(redis_mock, ttl=timedelta(hours=24))

    def test_ar_i01_generate_key(self, idempotency):
        """AR-I01: 测试幂等键生成"""
        key1 = idempotency.generate_key("test", 123, {"a": 1})
        key2 = idempotency.generate_key("test", 123, {"a": 1})
        key3 = idempotency.generate_key("test", 456, {"a": 1})

        assert key1 == key2
        assert key1 != key3
        assert len(key1) == 64  # SHA256 hex

    def test_ar_i02_component_order_independent(self, idempotency):
        """AR-I02: 字典组件顺序不影响"""
        key1 = idempotency.generate_key({"b": 2, "a": 1})
        key2 = idempotency.generate_key({"a": 1, "b": 2})
        assert key1 == key2

    @pytest.mark.asyncio
    async def test_ar_i03_check_and_set_first_time(self, idempotency, redis_mock):
        """AR-I03: 首次检查通过"""
        redis_mock.set = AsyncMock(return_value=True)

        can_proceed, previous = await idempotency.check_and_set("test-key")

        assert can_proceed is True
        assert previous is None
        redis_mock.set.assert_called_once()

    @pytest.mark.asyncio
    async def test_ar_i04_check_and_set_duplicate(self, idempotency, redis_mock):
        """AR-I04: 重复请求返回已有结果"""
        redis_mock.set = AsyncMock(return_value=False)
        redis_mock.get = AsyncMock(return_value='{"result": "previous"}')

        can_proceed, previous = await idempotency.check_and_set("test-key")

        assert can_proceed is False
        assert previous == '{"result": "previous"}'

    @pytest.mark.asyncio
    async def test_ar_i05_store_result(self, idempotency, redis_mock):
        """AR-I05: 存储结果"""
        await idempotency.store_result("test-key", '{"result": "test"}')
        redis_mock.setex.assert_called_once()

    @pytest.mark.asyncio
    async def test_ar_i06_clear(self, idempotency, redis_mock):
        """AR-I06: 清除幂等键"""
        await idempotency.clear("test-key")
        assert redis_mock.delete.call_count == 2

