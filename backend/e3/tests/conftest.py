
"""
Test Configuration
"""

import sys
from pathlib import Path

# Add project roots to path for imports
backend_dir = Path(__file__).parent.parent
project_root = backend_dir.parent
src_dir = project_root / "src"

if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

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
