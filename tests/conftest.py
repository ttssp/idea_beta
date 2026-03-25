"""测试配置"""

import pytest


@pytest.fixture
def app():
    """FastAPI应用fixture - 延迟导入"""
    from myproj.main import create_app
    return create_app()


@pytest.fixture
def client(app):
    """测试客户端fixture"""
    from fastapi.testclient import TestClient
    return TestClient(app)
