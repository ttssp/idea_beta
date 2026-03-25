
"""
Messages API

API endpoints for message drafting and sending.
"""

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ...action_runtime.engine import ActionRunEngine
from ...core.idempotency import IdempotencyManager
from ..deps import get_db, get_idempotency_manager

router = APIRouter(prefix="/threads/{thread_id}/messages", tags=["messages"])


@router.post(":draft")
async def draft_message(
    thread_id: UUID,
    request: dict[str, Any],
    db: AsyncSession = Depends(get_db),
    idempotency: IdempotencyManager = Depends(get_idempotency_manager),
) -> dict[str, Any]:
    """
    起草消息（挂载到thread）
    """
    channel_type = request.get("channel_type", "email")
    subject = request.get("subject")
    body = request.get("body")
    to = request.get("to", [])

    if not body:
        raise HTTPException(status_code=400, detail="body is required")

    # 创建ActionRun
    idempotency_key = idempotency.generate_key("draft", thread_id, channel_type, subject, body)

    engine = ActionRunEngine(db, idempotency)
    action_run = await engine.create_action_run(
        thread_id=thread_id,
        action_type="send_email" if channel_type == "email" else f"send_{channel_type}",
        input_payload={
            "channel_type": channel_type,
            "to": to,
            "subject": subject,
            "body": body
        },
        idempotency_key=idempotency_key
    )

    action_run = await engine.plan_action(action_run.id)

    return {
        "id": str(action_run.id),
        "thread_id": str(thread_id),
        "action_run_id": str(action_run.id),
        "channel_type": channel_type,
        "subject": subject,
        "body": body,
        "created_at": action_run.created_at.isoformat() if action_run.created_at else None
    }


@router.post(":send")
async def send_message(
    thread_id: UUID,
    request: dict[str, Any],
    db: AsyncSession = Depends(get_db),
    idempotency: IdempotencyManager = Depends(get_idempotency_manager),
) -> dict[str, Any]:
    """
    发送消息（通过egress）
    """
    channel_type = request.get("channel_type", "email")
    subject = request.get("subject")
    body = request.get("body")
    to = request.get("to", [])

    if not to:
        raise HTTPException(status_code=400, detail="to is required")
    if not body:
        raise HTTPException(status_code=400, detail="body is required")

    # 创建并执行ActionRun
    idempotency_key = idempotency.generate_key("send", thread_id, channel_type, to, subject, body)

    engine = ActionRunEngine(db, idempotency)
    action_run = await engine.create_action_run(
        thread_id=thread_id,
        action_type="send_email" if channel_type == "email" else f"send_{channel_type}",
        input_payload={
            "channel_type": channel_type,
            "to": to,
            "cc": request.get("cc", []),
            "subject": subject,
            "body": body,
            "in_reply_to": request.get("in_reply_to"),
            "references": request.get("references")
        },
        idempotency_key=idempotency_key
    )

    action_run = await engine.plan_action(action_run.id)
    action_run = await engine.submit_for_approval(action_run.id)
    action_run = await engine.approve(action_run.id)
    action_run = await engine.start_execution(action_run.id)

    # 模拟发送成功
    action_run = await engine.mark_send_success(
        action_run.id,
        output_payload={"status": "simulated", "external_id": "simulated-123"}
    )

    return {
        "action_run_id": str(action_run.id),
        "status": action_run.status,
        "external_message_id": action_run.external_message_id
    }

