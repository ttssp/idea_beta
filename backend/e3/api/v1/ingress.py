
"""
Ingress Webhook API

API endpoints for receiving external webhooks.
"""

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.idempotency import IdempotencyManager
from ...outbox_inbox.inbox import InboxProcessor
from ..deps import get_db, get_idempotency_manager

router = APIRouter(prefix="/ingress", tags=["ingress"])


@router.post("/email/gmail")
async def gmail_webhook(
    request: Request,
    x_gmail_signature: str | None = Header(None),
    x_gmail_timestamp: str | None = Header(None),
    db: AsyncSession = Depends(get_db),
    idempotency: IdempotencyManager = Depends(get_idempotency_manager),
) -> dict[str, Any]:
    """
    Gmail Webhook入口
    """
    # 1. 验签（生产环境需要完整实现）
    # adapter = GmailAdapter()
    # payload_bytes = await request.body()
    # if not adapter.validate_webhook_signature(payload_bytes, x_gmail_signature, x_gmail_timestamp):
    #     raise HTTPException(status_code=403, detail="Invalid signature")

    # 2. 解析payload
    payload = await request.json()

    # 3. 提取外部消息/线程Key
    # 简化处理，实际需要从Gmail payload中解析
    message_id = payload.get("message", {}).get("message_id", "test-msg-id")
    thread_id = payload.get("message", {}).get("thread_id", "test-thread-id")
    external_message_key = f"gmail:{message_id}"
    external_thread_key = f"gmail:{thread_id}" if thread_id else None

    # 4. 写入Inbox
    processor = InboxProcessor(db, idempotency)
    event, is_new = await processor.receive(
        channel_type="email",
        event_type="gmail_history",
        external_thread_key=external_thread_key,
        external_message_key=external_message_key,
        payload=payload,
        raw_payload=await request.body(),
        webhook_signature=x_gmail_signature,
        webhook_timestamp=datetime.fromtimestamp(int(x_gmail_timestamp)) if x_gmail_timestamp else None
    )

    if not is_new:
        return {"status": "duplicate", "event_id": str(event.id)}

    # 5. 触发解析（在真实场景中由Celery任务处理）
    # from ...ingress.tasks import process_inbox_event
    # process_inbox_event.delay(str(event.id))

    return {"status": "accepted", "event_id": str(event.id)}


@router.post("/email/outlook")
async def outlook_mail_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
    idempotency: IdempotencyManager = Depends(get_idempotency_manager),
) -> dict[str, Any]:
    """
    Outlook Mail Webhook入口
    """
    await request.json()
    return {"status": "accepted", "note": "Not implemented yet"}


@router.post("/calendar/google")
async def google_calendar_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
    idempotency: IdempotencyManager = Depends(get_idempotency_manager),
) -> dict[str, Any]:
    """
    Google Calendar Webhook入口
    """
    await request.json()
    return {"status": "accepted", "note": "Not implemented yet"}


@router.post("/calendar/outlook")
async def outlook_calendar_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
    idempotency: IdempotencyManager = Depends(get_idempotency_manager),
) -> dict[str, Any]:
    """
    Outlook Calendar Webhook入口
    """
    await request.json()
    return {"status": "accepted", "note": "Not implemented yet"}
