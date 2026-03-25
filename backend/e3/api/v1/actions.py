
"""
Actions API

API endpoints for ActionRun management.
"""

from typing import Optional, List, Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..deps import get_db, get_idempotency_manager, get_idempotency_key
from ...action_runtime.engine import ActionRunEngine
from ...action_runtime.models import ActionRun
from ...core.idempotency import IdempotencyManager

router = APIRouter(prefix="/threads/{thread_id}/actions", tags=["actions"])


@router.post(":prepare")
async def prepare_action(
    thread_id: UUID,
    request: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    idempotency: IdempotencyManager = Depends(get_idempotency_manager),
) -&gt; Dict[str, Any]:
    """
    准备动作（生成ActionRun）
    """
    action_type = request.get("action_type")
    input_payload = request.get("input_payload", {})

    if not action_type:
        raise HTTPException(status_code=400, detail="action_type is required")

    # 生成幂等键
    idempotency_key = idempotency.generate_key("prepare", thread_id, action_type, input_payload)

    # 检查幂等
    can_proceed, previous_result = await idempotency.check_and_set(idempotency_key)
    if not can_proceed and previous_result:
        import json
        return json.loads(previous_result)

    # 创建ActionRun
    engine = ActionRunEngine(db, idempotency)
    action_run = await engine.create_action_run(
        thread_id=thread_id,
        action_type=action_type,
        input_payload=input_payload,
        idempotency_key=idempotency_key
    )

    # 规划动作
    action_run = await engine.plan_action(action_run.id)

    result = _action_run_to_dict(action_run)

    # 存储结果
    import json
    await idempotency.store_result(idempotency_key, json.dumps(result))

    return result


@router.post(":execute")
async def execute_action(
    thread_id: UUID,
    request: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    idempotency: IdempotencyManager = Depends(get_idempotency_manager),
) -&gt; Dict[str, Any]:
    """
    执行动作
    """
    action_run_id = request.get("action_run_id")
    if not action_run_id:
        raise HTTPException(status_code=400, detail="action_run_id is required")

    try:
        action_run_uuid = UUID(action_run_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid action_run_id")

    # 生成幂等键
    idempotency_key = idempotency.generate_key("execute", thread_id, action_run_id)

    # 检查幂等
    can_proceed, previous_result = await idempotency.check_and_set(idempotency_key)
    if not can_proceed and previous_result:
        import json
        return json.loads(previous_result)

    # 执行动作
    engine = ActionRunEngine(db, idempotency)

    try:
        # 先获取并验证
        action_run = await engine.get_action_run(action_run_uuid)
        if not action_run:
            raise HTTPException(status_code=404, detail="ActionRun not found")

        if action_run.thread_id != thread_id:
            raise HTTPException(status_code=400, detail="ActionRun does not belong to this thread")

        # 根据当前状态决定下一步
        from ...action_runtime.state_machine import ActionRunStatus

        if action_run.status == ActionRunStatus.PLANNED:
            action_run = await engine.submit_for_approval(action_run_uuid)
            # 在真实场景中，这里可能需要等待审批
            # 为了demo，我们自动批准
            action_run = await engine.approve(action_run_uuid)
            action_run = await engine.start_execution(action_run_uuid)
        elif action_run.status == ActionRunStatus.READY_FOR_APPROVAL:
            action_run = await engine.approve(action_run_uuid)
            action_run = await engine.start_execution(action_run_uuid)
        elif action_run.status == ActionRunStatus.APPROVED:
            action_run = await engine.start_execution(action_run_uuid)
        elif action_run.status == ActionRunStatus.FAILED_RETRYABLE:
            action_run = await engine.retry(action_run_uuid)
        else:
            raise HTTPException(
                status_code=409,
                detail=f"Cannot execute action in status: {action_run.status}"
            )

        # 模拟发送成功（在真实场景中由Celery任务处理）
        action_run = await engine.mark_send_success(
            action_run_uuid,
            output_payload={"status": "simulated"}
        )
        action_run = await engine.acknowledge(action_run_uuid)

        result = _action_run_to_dict(action_run)

        # 存储结果
        import json
        await idempotency.store_result(idempotency_key, json.dumps(result))

        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{action_id}:cancel")
async def cancel_action(
    thread_id: UUID,
    action_id: UUID,
    db: AsyncSession = Depends(get_db),
) -&gt; Dict[str, Any]:
    """
    取消动作
    """
    engine = ActionRunEngine(db)

    try:
        action_run = await engine.get_action_run(action_id)
        if not action_run:
            raise HTTPException(status_code=404, detail="ActionRun not found")

        if action_run.thread_id != thread_id:
            raise HTTPException(status_code=400, detail="ActionRun does not belong to this thread")

        action_run = await engine.cancel(action_id)
        return _action_run_to_dict(action_run)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("")
async def list_actions(
    thread_id: UUID,
    status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -&gt; Dict[str, Any]:
    """
    查询动作列表
    """
    engine = ActionRunEngine(db)
    actions = await engine.list_by_thread(thread_id, status=status, limit=limit)

    return {
        "items": [_action_run_to_dict(a) for a in actions],
        "total": len(actions)
    }


def _action_run_to_dict(action_run: ActionRun) -&gt; Dict[str, Any]:
    """将ActionRun转换为字典"""
    return {
        "id": str(action_run.id),
        "thread_id": str(action_run.thread_id),
        "action_type": action_run.action_type,
        "status": action_run.status,
        "idempotency_key": action_run.idempotency_key,
        "input_payload": action_run.input_payload,
        "output_payload": action_run.output_payload,
        "risk_decision": action_run.risk_decision,
        "risk_reason": action_run.risk_reason,
        "retry_count": action_run.retry_count,
        "max_retries": action_run.max_retries,
        "last_error": action_run.last_error,
        "external_message_id": action_run.external_message_id,
        "external_thread_id": action_run.external_thread_id,
        "created_at": action_run.created_at.isoformat() if action_run.created_at else None,
        "updated_at": action_run.updated_at.isoformat() if action_run.updated_at else None,
        "scheduled_for": action_run.scheduled_for.isoformat() if action_run.scheduled_for else None,
        "executed_at": action_run.executed_at.isoformat() if action_run.executed_at else None,
    }

