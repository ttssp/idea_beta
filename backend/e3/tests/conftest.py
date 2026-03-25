
"""
Test Configuration
"""

import asyncio
from datetime import UTC, datetime
from uuid import uuid4

import pytest


@pytest.fixture(scope="session")
def event_loop():
    """Event loop fixture"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def random_uuid():
    """生成随机UUID"""
    return uuid4()


@pytest.fixture
def now():
    """当前时间"""
    return datetime.now(UTC)
