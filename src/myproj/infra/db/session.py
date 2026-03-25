"""数据库会话管理"""

from contextlib import contextmanager
from typing import Generator, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base

from myproj.config import get_settings

settings = get_settings()

# 创建引擎
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    echo=settings.APP_DEBUG,
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 基类
Base = declarative_base()


def init_db() -> None:
    """初始化数据库 - 创建所有表"""
    from myproj.infra.db.models import (
        ThreadModel,
        PrincipalModel,
        RelationshipModel,
        MessageModel,
        ThreadEventModel,
        ExternalBindingModel,
    )
    Base.metadata.create_all(bind=engine)


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """获取数据库会话（上下文管理器）"""
    db = SessionLocal()
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
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
