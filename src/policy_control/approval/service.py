
"""
Approval Engine Service

审批请求创建/审核/超时处理/批量操作
"""
from typing import List, Optional, Dict, Any, Callable
from uuid import UUID
from datetime import datetime, timedelta

from ..common.constants import ApprovalStatus, RequestType, TimeoutAction
from ..common.exceptions import ApprovalStateTransitionError
from .models import ApprovalRequest, ApprovalResolution
from .state_machine import ApprovalStateMachine


class ApprovalService:
    """审批服务"""

    def __init__(self):
        self._requests: Dict[UUID, ApprovalRequest] = {}
        self._state_machine = ApprovalStateMachine()
        self._on_resolved_callbacks: List[Callable] = []

    def on_resolved(self, callback: Callable):
        """注册审批解决回调"""
        self._on_resolved_callbacks.append(callback)

    def create_request(
        self,
        thread_id: UUID,
        request_type: RequestType,
        reason_code: str,
        requester_principal_id: UUID,
        reason_description: Optional[str] = None,
        action_run_id: Optional[UUID] = None,
        approver_principal_id: Optional[UUID] = None,
        preview: Optional[Dict[str, Any]] = None,
        timeout_hours: int = 24,
        timeout_action: TimeoutAction = TimeoutAction.ESCALATE,
    ) -&gt; ApprovalRequest:
        """
        创建审批请求

        Args:
            thread_id: 线程ID
            request_type: 请求类型
            reason_code: 原因代码
            requester_principal_id: 请求者ID
            reason_description: 原因描述
            action_run_id: 动作运行ID
            approver_principal_id: 审批者ID
            preview: 预览内容
            timeout_hours: 超时时间（小时）
            timeout_action: 超时动作

        Returns:
            创建的审批请求
        """
        request = ApprovalRequest(
            thread_id=thread_id,
            action_run_id=action_run_id,
            request_type=request_type,
            reason_code=reason_code,
            reason_description=reason_description,
            requester_principal_id=requester_principal_id,
            approver_principal_id=approver_principal_id,
            status=ApprovalStatus.PENDING,
            preview=preview,
            timeout_at=datetime.utcnow() + timedelta(hours=timeout_hours),
            timeout_action=timeout_action,
        )
        self._requests[request.id] = request
        return request

    def get_request(self, request_id: UUID) -&gt; Optional[ApprovalRequest]:
        """获取审批请求"""
        return self._requests.get(request_id)

    def list_requests(
        self,
        thread_id: Optional[UUID] = None,
        status: Optional[ApprovalStatus] = None,
        approver_principal_id: Optional[UUID] = None,
        limit: int = 100,
    ) -&gt; List[ApprovalRequest]:
        """
        列出审批请求

        Args:
            thread_id: 按线程过滤
            status: 按状态过滤
            approver_principal_id: 按审批者过滤
            limit: 返回数量限制

        Returns:
            审批请求列表
        """
        requests = list(self._requests.values())

        if thread_id:
            requests = [r for r in requests if r.thread_id == thread_id]

        if status:
            requests = [r for r in requests if r.status == status]

        if approver_principal_id:
            requests = [r for r in requests if r.approver_principal_id == approver_principal_id]

        # 按创建时间倒序
        requests.sort(key=lambda r: r.created_at, reverse=True)

        return requests[:limit]

    def resolve(
        self,
        request_id: UUID,
        resolution: ApprovalResolution,
    ) -&gt; ApprovalRequest:
        """
        审批操作

        Args:
            request_id: 审批请求ID
            resolution: 审批决议

        Returns:
            更新后的审批请求

        Raises:
            ApprovalStateTransitionError: 如果状态流转不允许
        """
        request = self._requests.get(request_id)
        if not request:
            raise ValueError(f"Approval request {request_id} not found")

        if not request.is_pending():
            raise ApprovalStateTransitionError(
                f"Cannot resolve request in status {request.status.value}"
            )

        # 映射到目标状态
        action_to_status = {
            "APPROVE": ApprovalStatus.APPROVED,
            "REJECT": ApprovalStatus.REJECTED,
            "MODIFY": ApprovalStatus.MODIFIED,
            "TAKEOVER": ApprovalStatus.TAKEN_OVER,
        }

        target_status = action_to_status.get(resolution.action.upper())
        if not target_status:
            raise ValueError(f"Invalid resolution action: {resolution.action}")

        # 执行状态流转
        self._state_machine.transition(request.status, target_status)

        # 更新请求
        request.status = target_status
        request.resolution = {
            "action": resolution.action,
            "modified_content": resolution.modified_content,
            "reason": resolution.reason,
        }
        request.resolved_at = datetime.utcnow()
        request.resolved_by = resolution.resolved_by
        request.updated_at = datetime.utcnow()

        # 触发回调
        for callback in self._on_resolved_callbacks:
            try:
                callback(request)
            except Exception:
                pass  # 记录日志但不影响主流程

        return request

    def cancel(self, request_id: UUID, reason: Optional[str] = None) -&gt; ApprovalRequest:
        """取消审批请求"""
        request = self._requests.get(request_id)
        if not request:
            raise ValueError(f"Approval request {request_id} not found")

        if not request.is_pending():
            raise ApprovalStateTransitionError(
                f"Cannot cancel request in status {request.status.value}"
            )

        self._state_machine.transition(request.status, ApprovalStatus.CANCELLED)
        request.status = ApprovalStatus.CANCELLED
        request.resolution = {"action": "CANCEL", "reason": reason}
        request.resolved_at = datetime.utcnow()
        request.updated_at = datetime.utcnow()

        return request

    def process_timeouts(self) -&gt; List[ApprovalRequest]:
        """
        处理超时审批

        Returns:
            超时处理的请求列表
        """
        timed_out_requests = []

        for request in self._requests.values():
            if request.is_pending() and request.is_timed_out():
                # 执行超时动作
                if request.timeout_action == TimeoutAction.ESCALATE:
                    target_status = ApprovalStatus.TIMEOUT
                elif request.timeout_action == TimeoutAction.DENY:
                    target_status = ApprovalStatus.REJECTED
                elif request.timeout_action == TimeoutAction.AUTO_APPROVE:
                    target_status = ApprovalStatus.APPROVED
                else:
                    target_status = ApprovalStatus.TIMEOUT

                self._state_machine.transition(request.status, target_status)
                request.status = target_status
                request.resolution = {
                    "action": "TIMEOUT",
                    "timeout_action": request.timeout_action.value,
                }
                request.resolved_at = datetime.utcnow()
                request.updated_at = datetime.utcnow()

                timed_out_requests.append(request)

                # 触发回调
                for callback in self._on_resolved_callbacks:
                    try:
                        callback(request)
                    except Exception:
                        pass

        return timed_out_requests

    def bulk_resolve(
        self,
        request_ids: List[UUID],
        action: str,
        resolved_by: UUID,
        reason: Optional[str] = None,
    ) -&gt; List[ApprovalRequest]:
        """
        批量审批操作

        Args:
            request_ids: 审批请求ID列表
            action: 审批动作
            resolved_by: 审批者ID
            reason: 原因

        Returns:
            更新后的审批请求列表
        """
        results = []
        for request_id in request_ids:
            try:
                resolution = ApprovalResolution(
                    action=action,
                    reason=reason,
                    resolved_by=resolved_by,
                )
                request = self.resolve(request_id, resolution)
                results.append(request)
            except Exception:
                pass  # 记录错误但继续处理其他请求

        return results
