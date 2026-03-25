"""数据库会话管理测试"""

import pytest

from myproj.infra.db import session as db_session


class DummySession:
    def __init__(self) -> None:
        self.committed = False
        self.rolled_back = False
        self.closed = False

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.rolled_back = True

    def close(self) -> None:
        self.closed = True


def test_get_db_commits_and_closes(monkeypatch):
    """FastAPI 依赖在正常执行后应提交事务并关闭会话"""
    dummy = DummySession()
    monkeypatch.setattr(db_session, "get_session_factory", lambda: lambda: dummy)

    generator = db_session.get_db()
    yielded = next(generator)

    assert yielded is dummy

    with pytest.raises(StopIteration):
        next(generator)

    assert dummy.committed is True
    assert dummy.rolled_back is False
    assert dummy.closed is True


def test_get_db_rolls_back_on_error(monkeypatch):
    """FastAPI 依赖在异常路径上应回滚事务并关闭会话"""
    dummy = DummySession()
    monkeypatch.setattr(db_session, "get_session_factory", lambda: lambda: dummy)

    generator = db_session.get_db()
    next(generator)

    with pytest.raises(RuntimeError):
        generator.throw(RuntimeError("boom"))

    assert dummy.committed is False
    assert dummy.rolled_back is True
    assert dummy.closed is True
