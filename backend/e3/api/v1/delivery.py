
"""
Delivery Status API

API endpoints for delivery status management.
"""

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..deps import get_db

router = APIRouter(tags=["delivery"])


@router.post("/delivery/status")
async def delivery_status_callback(
    request: dict[str, Any],
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    外部回执回调
    """
    delivery_id = request.get("delivery_id")
    status = request.get("status")

    if not delivery_id or not status:
        raise HTTPException(status_code=400, detail="delivery_id and status are required")

    # 在真实场景中，这里会更新对应的ActionRun状态
    # 如果status是delivered，调用engine.acknowledge()

    return {"status": "acknowledged"}


@router.get("/delivery/{delivery_id}/status")
async def get_delivery_status(
    delivery_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    查询发送状态
    """
    # 在真实场景中，这里会查询OutboxMessage或ActionRun
    return {
        "delivery_id": str(delivery_id),
        "status": "pending",
        "external_id": None,
        "timestamp": None,
        "detail": None
    }
