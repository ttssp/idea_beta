"""测试配置"""

import pytest


@pytest.fixture(autouse=True)
def reset_api_state():
    """隔离API模块中的进程内状态，避免测试互相污染。"""
    from myproj.api.v1.events import _thread_service
    from myproj.api.v1.messages import _messages
    from myproj.api.v1.principals import _principals
    from myproj.api.v1.relationships import _relationships

    _messages.clear()
    _principals.clear()
    _relationships.clear()
    _thread_service._threads.clear()
    _thread_service.event_store = _thread_service.event_store.__class__()

    yield

    _messages.clear()
    _principals.clear()
    _relationships.clear()
    _thread_service._threads.clear()
    _thread_service.event_store = _thread_service.event_store.__class__()


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
