"""数据库会话管理"""

from collections.abc import Generator
from contextlib import contextmanager
from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from myproj.config import get_settings

settings = get_settings()

# 基类
Base = declarative_base()


@lru_cache
def get_engine() -> Engine:
    """延迟创建数据库引擎，避免仅导入模块时就强依赖数据库驱动。"""
    return create_engine(
        settings.DATABASE_URL,
        pool_size=settings.DATABASE_POOL_SIZE,
        max_overflow=settings.DATABASE_MAX_OVERFLOW,
        echo=settings.APP_DEBUG,
    )


@lru_cache
def get_session_factory() -> sessionmaker[Session]:
    """获取数据库会话工厂。"""
    return sessionmaker(autocommit=False, autoflush=False, bind=get_engine())


engine = get_engine


def init_db() -> None:
    """初始化数据库 - 创建所有表"""
    Base.metadata.create_all(bind=get_engine())


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """获取数据库会话（上下文管理器）"""
    db = get_session_factory()()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_db() -> Generator[Session, None, None]:
    """获取数据库会话（FastAPI依赖注入用）"""
    db = get_session_factory()()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
