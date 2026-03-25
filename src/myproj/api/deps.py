"""API 依赖注入"""

from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, Path, status
from sqlalchemy.orm import Session

from myproj.infra.db import get_db

# ============================================
# Database 依赖
# ============================================

DbSession = Annotated[Session, Depends(get_db)]


# ============================================
# 路径参数解析
# ============================================

def get_thread_id(
    thread_id: Annotated[UUID, Path(..., description="Thread ID")]
) -> UUID:
    """获取Thread ID路径参数"""
    return thread_id


def get_principal_id(
    principal_id: Annotated[UUID, Path(..., description="Principal ID")]
) -> UUID:
    """获取Principal ID路径参数"""
    return principal_id


def get_relationship_id(
    relationship_id: Annotated[UUID, Path(..., description="Relationship ID")]
) -> UUID:
    """获取Relationship ID路径参数"""
    return relationship_id


def get_message_id(
    message_id: Annotated[UUID, Path(..., description="Message ID")]
) -> UUID:
    """获取Message ID路径参数"""
    return message_id


def get_event_id(
    event_id: Annotated[UUID, Path(..., description="Event ID")]
) -> UUID:
    """获取Event ID路径参数"""
    return event_id


# ============================================
# 分页参数
# ============================================

class PaginationParams:
    """分页参数"""

    def __init__(
        self,
        offset: int = 0,
        limit: int = 100,
    ):
        if offset < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Offset must be non-negative",
            )
        if limit < 1 or limit > 1000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Limit must be between 1 and 1000",
            )
        self.offset = offset
        self.limit = limit


Pagination = Annotated[PaginationParams, Depends()]
