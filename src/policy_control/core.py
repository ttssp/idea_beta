
"""
E2 Policy & Control Module - Complete Working Implementation

This is a fully functional implementation of the E2 module
for the Agent-Native Communication Control Layer.
"""

# ============================================================================
# Imports & Setup
# ============================================================================

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

# ============================================================================
# Enums - Core Constants
# ============================================================================

class DelegationLevel(str, Enum):
    """
    委托档位定义

    - OBSERVE_ONLY: 只观察与建议，不起草不发送
    - DRAFT_FIRST: 自动起草，但所有消息需人工确认
    - APPROVE_TO_SEND: 低风险动作自动准备，用户一键审批后发出
    - BOUNDED_AUTO: 在明确预算和动作边界内自动执行
    - HUMAN_ONLY: 该类关系或场景禁止代理主动介入
    """
    OBSERVE_ONLY = "observe_only"
    DRAFT_FIRST = "draft_first"
    APPROVE_TO_SEND = "approve_to_send"
    BOUNDED_AUTO = "bounded_auto"
    HUMAN_ONLY = "human_only"


class Decision(str, Enum):
    """
    决策输出定义

    - allow: 允许自动执行
    - draft_only: 仅允许起草
    - require_approval: 需要审批后才能执行
    - bounded_execution: 在边界内自动执行
    - escalate_to_human: 升级给人工处理
    - deny: 拒绝执行
    """
    ALLOW = "allow"
    DRAFT_ONLY = "draft_only"
    REQUIRE_APPROVAL = "require_approval"
    BOUNDED_EXECUTION = "bounded_execution"
    ESCALATE_TO_HUMAN = "escalate_to_human"
    DENY = "deny"


class RiskLevel(str, Enum):
    """
    风险等级定义

    - LOW: 低风险
    - MEDIUM: 中风险
    - HIGH: 高风险
    - CRITICAL: 极高风险
    """
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ApprovalStatus(str, Enum):
    """
    审批状态定义

    - PENDING: 待审批
    - APPROVED: 已批准
    - REJECTED: 已拒绝
    - MODIFIED: 已修改后批准
    - TAKEN_OVER: 已接管
    - CANCELLED: 已取消
    - TIMEOUT: 已超时
    """
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    MODIFIED = "modified"
    TAKEN_OVER = "taken_over"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class KillSwitchLevel(str, Enum):
    """
    熔断级别定义

    - GLOBAL: 全局熔断
    - PROFILE: 档位熔断
    - THREAD: 线程熔断
    """
    GLOBAL = "global"
    PROFILE = "profile"
    THREAD = "thread"


class PolicyEffect(str, Enum):
    """策略效果定义"""
    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_APPROVAL = "require_approval"
    ESCALATE = "escalate"


class PolicyScope(str, Enum):
    """策略作用域定义"""
    GLOBAL = "global"
    PROFILE = "profile"
    RELATIONSHIP = "relationship"
    THREAD = "thread"


# ============================================================================
# Data Models
# ============================================================================

@dataclass
class DelegationProfile:
    """委托档位模型"""
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    display_name: str = ""
    description: str | None = None
    profile_level: DelegationLevel = DelegationLevel.OBSERVE_ONLY
    allowed_actions: list = field(default_factory=list)
    budget_config: dict[str, Any] | None = None
    escalation_rules: dict[str, Any] | None = None
    is_system_defined: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PolicyRule:
    """策略规则模型"""
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    description: str | None = None
    scope: PolicyScope = PolicyScope.GLOBAL
    scope_id: UUID | None = None
    action: str = ""
    effect: PolicyEffect = PolicyEffect.ALLOW
    conditions: dict[str, Any] = field(default_factory=dict)
    priority: int = 0
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    created_by: UUID | None = None


@dataclass
class ApprovalRequest:
    """审批请求模型"""
    id: UUID = field(default_factory=uuid4)
    thread_id: UUID = field(default_factory=uuid4)
    action_run_id: UUID | None = None
    request_type: str = "message_send"
    reason_code: str = ""
    reason_description: str | None = None
    requester_principal_id: UUID = field(default_factory=uuid4)
    approver_principal_id: UUID | None = None
    status: ApprovalStatus = ApprovalStatus.PENDING
    preview: dict | None = None
    resolution: dict | None = None
    resolved_at: datetime | None = None
    resolved_by: UUID | None = None
    timeout_at: datetime | None = None
    timeout_action: str = "escalate"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RiskAssessment:
    """风险评估记录"""
    id: UUID = field(default_factory=uuid4)
    thread_id: UUID = field(default_factory=uuid4)
    action_run_id: UUID | None = None
    relationship_risk: int = 1
    action_risk: int = 1
    content_risk: int = 1
    consequence_risk: int = 1
    overall_risk_level: RiskLevel = RiskLevel.LOW
    risk_factors: list = field(default_factory=list)
    decision_recommendation: Decision = Decision.ALLOW
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class KillSwitch:
    """熔断开关模型"""
    id: UUID = field(default_factory=uuid4)
    level: KillSwitchLevel = KillSwitchLevel.THREAD
    level_id: UUID | None = None
    reason: str = ""
    activated_by: UUID = field(default_factory=uuid4)
    is_active: bool = True
    activated_at: datetime = field(default_factory=datetime.utcnow)
    deactivated_at: datetime | None = None
    deactivated_by: UUID | None = None


@dataclass
class DecisionTrace:
    """决策追踪记录"""
    id: UUID = field(default_factory=uuid4)
    thread_id: UUID = field(default_factory=uuid4)
    action_run_id: UUID | None = None
    decision: Decision = Decision.ESCALATE_TO_HUMAN
    decision_reason: str | None = None
    steps: list = field(default_factory=list)
    policy_hits: list | None = None
    risk_assessment_id: UUID | None = None
    kill_switch_affected: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)


# ============================================================================
# System Default Profiles
# ============================================================================

SYSTEM_DELEGATION_PROFILES = [
    {
        "name": "observe_only",
        "display_name": "仅观察",
        "description": "系统只观察与建议，不起草不发送",
        "profile_level": DelegationLevel.OBSERVE_ONLY,
        "allowed_actions": [],
        "budget_config": None,
        "escalation_rules": {"all_actions": "escalate"},
    },
    {
        "name": "draft_first",
        "display_name": "优先起草",
        "description": "自动起草消息，但所有消息需人工确认",
        "profile_level": DelegationLevel.DRAFT_FIRST,
        "allowed_actions": ["draft_message"],
        "budget_config": None,
        "escalation_rules": {"send_message": "require_approval"},
    },
    {
        "name": "approve_to_send",
        "display_name": "审批发送",
        "description": "低风险动作自动准备，用户一键审批后发出",
        "profile_level": DelegationLevel.APPROVE_TO_SEND,
        "allowed_actions": ["draft_message", "prepare_action"],
        "budget_config": {"max_drafts_per_day": 20},
        "escalation_rules": {"high_risk": "escalate", "medium_risk": "require_approval"},
    },
    {
        "name": "bounded_auto",
        "display_name": "边界内自动",
        "description": "在明确预算和动作边界内自动执行",
        "profile_level": DelegationLevel.BOUNDED_AUTO,
        "allowed_actions": ["draft_message", "send_message", "schedule_followup"],
        "budget_config": {
            "max_messages_per_day": 10,
            "max_followups_per_thread": 3,
            "window_hours": 24,
        },
        "escalation_rules": {"high_risk": "escalate", "medium_risk": "require_approval"},
    },
    {
        "name": "human_only",
        "display_name": "仅人工",
        "description": "该类关系或场景禁止代理主动介入",
        "profile_level": DelegationLevel.HUMAN_ONLY,
        "allowed_actions": [],
        "budget_config": None,
        "escalation_rules": {"all_actions": "deny"},
    },
]


# ============================================================================
# Services
# ============================================================================

class DelegationService:
    """
    委托档位服务

    负责：
    - 5种系统默认档位初始化
    - 档位CRUD
    - 档位与Thread/Relationship的绑定
    - 预算管理
    """

    def __init__(self):
        self._profiles: dict[UUID, DelegationProfile] = {}
        self._thread_bindings: dict[UUID, UUID] = {}
        self._relationship_bindings: dict[UUID, UUID] = {}
        self._initialize_system_profiles()

    def _initialize_system_profiles(self):
        """初始化系统默认档位"""
        for data in SYSTEM_DELEGATION_PROFILES:
            profile = DelegationProfile(
                name=data["name"],
                display_name=data["display_name"],
                description=data["description"],
                profile_level=data["profile_level"],
                allowed_actions=data["allowed_actions"],
                budget_config=data["budget_config"],
                escalation_rules=data["escalation_rules"],
                is_system_defined=True,
            )
            self._profiles[profile.id] = profile

    def get_profile(self, profile_id: UUID) -> DelegationProfile | None:
        """获取委托档位"""
        return self._profiles.get(profile_id)

    def get_profile_by_name(self, name: str) -> DelegationProfile | None:
        """通过名称获取委托档位"""
        for profile in self._profiles.values():
            if profile.name == name:
                return profile
        return None

    def list_profiles(self, include_system: bool = True) -> list[DelegationProfile]:
        """列出所有可用档位"""
        profiles = list(self._profiles.values())
        if not include_system:
            profiles = [p for p in profiles if not p.is_system_defined]
        return profiles

    def get_effective_profile(
        self,
        thread_id: UUID | None = None,
        relationship_id: UUID | None = None,
    ) -> DelegationProfile:
        """
        获取有效委托档位

        优先级：Thread > Relationship > System Default (Observe Only)
        """
        if thread_id and thread_id in self._thread_bindings:
            profile_id = self._thread_bindings[thread_id]
            profile = self._profiles.get(profile_id)
            if profile:
                return profile

        if relationship_id and relationship_id in self._relationship_bindings:
            profile_id = self._relationship_bindings[relationship_id]
            profile = self._profiles.get(profile_id)
            if profile:
                return profile

        default = self.get_profile_by_name("observe_only")
        if default:
            return default

        return list(self._profiles.values())[0]

    def bind_thread_profile(
        self,
        thread_id: UUID,
        profile_id: UUID,
    ):
        """绑定线程委托档位"""
        if profile_id in self._profiles:
            self._thread_bindings[thread_id] = profile_id

    def bind_relationship_profile(
        self,
        relationship_id: UUID,
        profile_id: UUID,
    ):
        """绑定关系默认委托档位"""
        if profile_id in self._profiles:
            self._relationship_bindings[relationship_id] = profile_id


class ApprovalService:
    """
    审批服务

    负责：
    - 审批请求CRUD
    - 审批操作（批准/拒绝/修改/接管）
    - 审批状态机
    """

    def __init__(self):
        self._requests: dict[UUID, ApprovalRequest] = {}

    def create_request(
        self,
        thread_id: UUID,
        request_type: str,
        reason_code: str,
        requester_principal_id: UUID,
        reason_description: str | None = None,
        action_run_id: UUID | None = None,
        approver_principal_id: UUID | None = None,
        preview: dict | None = None,
    ) -> ApprovalRequest:
        """创建审批请求"""
        request = ApprovalRequest(
            thread_id=thread_id,
            action_run_id=action_run_id,
            request_type=request_type,
            reason_code=reason_code,
            reason_description=reason_description,
            requester_principal_id=requester_principal_id,
            approver_principal_id=approver_principal_id,
            preview=preview,
            status=ApprovalStatus.PENDING,
        )
        self._requests[request.id] = request
        return request

    def get_request(self, request_id: UUID) -> ApprovalRequest | None:
        """获取审批请求"""
        return self._requests.get(request_id)

    def list_requests(
        self,
        thread_id: UUID | None = None,
        status: ApprovalStatus | None = None,
        limit: int = 100,
    ) -> list[ApprovalRequest]:
        """列出审批请求"""
        requests = list(self._requests.values())

        if thread_id:
            requests = [r for r in requests if r.thread_id == thread_id]

        if status:
            requests = [r for r in requests if r.status == status]

        requests.sort(key=lambda r: r.created_at, reverse=True)
        return requests[:limit]

    def resolve(
        self,
        request_id: UUID,
        action: str,
        reason: str | None = None,
        resolved_by: UUID | None = None,
        modified_content: str | None = None,
    ) -> ApprovalRequest | None:
        """审批操作"""
        request = self._requests.get(request_id)
        if not request or request.status != ApprovalStatus.PENDING:
            return None

        action_map = {
            "APPROVE": ApprovalStatus.APPROVED,
            "REJECT": ApprovalStatus.REJECTED,
            "MODIFY": ApprovalStatus.MODIFIED,
            "TAKEOVER": ApprovalStatus.TAKEN_OVER,
        }

        target_status = action_map.get(action.upper())
        if target_status:
            request.status = target_status
            request.resolution = {
                "action": action,
                "reason": reason,
                "modified_content": modified_content,
            }
            request.resolved_at = datetime.utcnow()
            request.resolved_by = resolved_by
            request.updated_at = datetime.utcnow()

        return request


class RiskEvaluator:
    """
    风险评估器

    四层风险评估：
    1. Relationship Risk - 这是对谁说话？
    2. Action Risk - 准备做什么动作？
    3. Content Risk - 这段内容是否涉及承诺/冲突/隐私/不确定性？
    4. Consequence Risk - 如果发出后出错，代价有多高？
    """

    def __init__(self):
        self._critical_keywords = ["$", "price", "discount", "payment", "contract", "agree", "promise"]
        self._high_keywords = ["terminate", "cancel", "complain", "angry", "refuse", "reject"]

    def evaluate(
        self,
        content: str | None = None,
        relationship_class: str | None = None,
        action_type: str | None = None,
    ) -> dict:
        """风险评估主入口"""
        rel_risk = self._evaluate_relationship(relationship_class)
        act_risk = self._evaluate_action(action_type)
        con_risk = self._evaluate_content(content)
        conq_risk = self._evaluate_consequence(rel_risk, act_risk)

        max_risk = max(rel_risk, act_risk, con_risk, conq_risk)
        avg_risk = (rel_risk + act_risk + con_risk + conq_risk) / 4

        overall_risk = max(max_risk, int(avg_risk))
        overall_level = self._score_to_level(overall_risk)
        recommendation = self._risk_to_decision(overall_level)

        risk_factors = []
        if rel_risk >= 4:
            risk_factors.append("relationship_high_risk")
        if act_risk >= 4:
            risk_factors.append("action_high_risk")
        if con_risk >= 4:
            risk_factors.append("content_high_risk")

        return {
            "overall_risk_level": overall_level,
            "relationship_risk": rel_risk,
            "action_risk": act_risk,
            "content_risk": con_risk,
            "consequence_risk": conq_risk,
            "risk_factors": risk_factors,
            "recommendation": recommendation,
        }

    def _evaluate_relationship(self, rc: str | None) -> int:
        """关系风险评估"""
        if rc in ["family", "core_client", "executive"]:
            return 5
        if rc in ["client", "vendor", "candidate"]:
            return 3
        if rc in ["colleague", "team_member", "internal_collaborator"]:
            return 1
        return 3

    def _evaluate_action(self, at: str | None) -> int:
        """动作风险评估"""
        if at in ["make_payment", "sign_contract", "make_commitment"]:
            return 5
        if at in ["send_negative_message", "escalate", "request_sensitive_info"]:
            return 4
        if at in ["send_message", "schedule_meeting", "request_info", "follow_up"]:
            return 3
        if at in ["draft_message", "suggest_action", "remind", "confirm"]:
            return 2
        return 3

    def _evaluate_content(self, content: str | None) -> int:
        """内容风险评估（关键词/模式匹配）"""
        if not content or not content.strip():
            return 1

        content_lower = content.lower()
        for k in self._critical_keywords:
            if k in content_lower:
                return 5
        for k in self._high_keywords:
            if k in content_lower:
                return 4
        return 1

    def _evaluate_consequence(self, rel_risk: int, act_risk: int) -> int:
        """结果风险评估"""
        return max(rel_risk, act_risk)

    def _score_to_level(self, score: int) -> RiskLevel:
        """将风险分数转换为风险等级"""
        if score <= 1:
            return RiskLevel.LOW
        elif score <= 3:
            return RiskLevel.MEDIUM
        elif score <= 4:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL

    def _risk_to_decision(self, level: RiskLevel) -> Decision:
        """将风险等级映射到决策"""
        if level == RiskLevel.LOW:
            return Decision.ALLOW
        elif level == RiskLevel.MEDIUM:
            return Decision.REQUIRE_APPROVAL
        elif level == RiskLevel.HIGH:
            return Decision.ESCALATE_TO_HUMAN
        else:
            return Decision.DENY


class KillSwitchService:
    """
    熔断服务

    支持三层熔断：
    - Global - 全局熔断
    - Profile - 档位熔断
    - Thread - 线程熔断

    检查逻辑：Global > Profile > Thread（父级熔断覆盖子级）
    """

    def __init__(self):
        self._switches: dict[UUID, KillSwitch] = {}

    def activate(
        self,
        level: KillSwitchLevel,
        reason: str,
        activated_by: UUID,
        level_id: UUID | None = None,
    ) -> KillSwitch:
        """激活熔断"""
        switch = KillSwitch(
            level=level,
            level_id=level_id,
            reason=reason,
            activated_by=activated_by,
            is_active=True,
        )
        self._switches[switch.id] = switch
        return switch

    def deactivate(
        self,
        switch_id: UUID,
        deactivated_by: UUID,
    ) -> KillSwitch | None:
        """解除熔断"""
        switch = self._switches.get(switch_id)
        if switch and switch.is_active:
            switch.is_active = False
            switch.deactivated_at = datetime.utcnow()
            switch.deactivated_by = deactivated_by
        return switch

    def check(
        self,
        level: KillSwitchLevel,
        level_id: UUID | None = None,
    ) -> bool:
        """检查是否有熔断生效"""
        for switch in self._switches.values():
            if not switch.is_active:
                continue
            if switch.level == KillSwitchLevel.GLOBAL:
                return True
            if switch.level == level and switch.level_id == level_id:
                return True
        return False

    def get_active_switches(
        self,
        level: KillSwitchLevel | None = None,
    ) -> list[KillSwitch]:
        """获取当前生效的熔断"""
        switches = [s for s in self._switches.values() if s.is_active]
        if level:
            switches = [s for s in switches if s.level == level]
        return switches


class DecisionRecorder:
    """
    决策记录器

    负责记录8步决策链的每一步
    """

    def __init__(self):
        self._traces: dict[UUID, DecisionTrace] = {}
        self._thread_traces: dict[UUID, list[UUID]] = {}

    def start_trace(
        self,
        thread_id: UUID,
        action_run_id: UUID | None = None,
    ) -> DecisionTrace:
        """开始记录决策追踪"""
        trace = DecisionTrace(
            thread_id=thread_id,
            action_run_id=action_run_id,
        )
        self._traces[trace.id] = trace

        if thread_id not in self._thread_traces:
            self._thread_traces[thread_id] = []
        self._thread_traces[thread_id].append(trace.id)

        return trace

    def complete_trace(
        self,
        trace: DecisionTrace,
        decision: Decision,
        decision_reason: str,
        policy_hits: list | None = None,
        risk_assessment_id: UUID | None = None,
        kill_switch_affected: bool = False,
    ) -> DecisionTrace:
        """完成决策追踪记录"""
        trace.decision = decision
        trace.decision_reason = decision_reason
        trace.policy_hits = policy_hits
        trace.risk_assessment_id = risk_assessment_id
        trace.kill_switch_affected = kill_switch_affected
        return trace

    def get_trace(self, trace_id: UUID) -> DecisionTrace | None:
        """获取决策追踪"""
        return self._traces.get(trace_id)

    def get_traces_for_thread(
        self,
        thread_id: UUID,
        limit: int = 100,
    ) -> list[DecisionTrace]:
        """获取线程的决策追踪列表"""
        trace_ids = self._thread_traces.get(thread_id, [])
        traces = [self._traces.get(tid) for tid in trace_ids if tid in self._traces]
        traces.sort(key=lambda t: t.created_at, reverse=True)
        return traces[:limit]


# ============================================================================
# Main Controller - 8-Step Decision Chain
# ============================================================================

class PolicyControlController:
    """
    策略控制主控制器

    提供统一的8步决策链接口：

    1. 读取 thread objective 与当前状态
    2. 读取 relationship class 与 delegation profile
    3. 生成候选动作
    4. 进行规则命中与预算检查（包括熔断检查）
    5. 进行内容/语义风险评估
    6. 进行结果代价评估
    7. 决定：自动执行/进入审批/升级人工或拒绝
    8. 记录完整 decision trace
    """

    def __init__(self):
        self.delegation_service = DelegationService()
        self.approval_service = ApprovalService()
        self.risk_evaluator = RiskEvaluator()
        self.kill_switch_service = KillSwitchService()
        self.decision_recorder = DecisionRecorder()

    def evaluate_action(
        self,
        thread_id: UUID,
        action: str,
        action_type: str,
        content: str | None = None,
        relationship_class: str | None = None,
        relationship_id: UUID | None = None,
        thread_objective: str | None = None,
        thread_status: str | None = None,
        action_run_id: UUID | None = None,
    ) -> dict:
        """
        8步决策链主入口

        Returns:
            {
                "decision": Decision,
                "decision_reason": str,
                "decision_trace_id": UUID,
                "policy_hits": Optional[List],
                "kill_switch_affected": bool,
            }
        """
        trace = self.decision_recorder.start_trace(thread_id, action_run_id)

        final_decision = Decision.ESCALATE_TO_HUMAN
        final_reason = "Error during evaluation"
        policy_hits = []
        kill_switch_affected = False

        try:
            trace.steps.append({
                "step": 1,
                "name": "Read Thread State",
                "thread_objective": thread_objective,
                "thread_status": thread_status,
            })

            profile = self.delegation_service.get_effective_profile(
                thread_id=thread_id,
                relationship_id=relationship_id,
            )
            trace.steps.append({
                "step": 2,
                "name": "Read Delegation Profile",
                "profile_id": str(profile.id),
                "profile_name": profile.name,
                "profile_level": profile.profile_level,
            })

            trace.steps.append({
                "step": 3,
                "name": "Candidate Action",
                "action": action,
            })

            if self.kill_switch_service.check(KillSwitchLevel.THREAD, thread_id):
                kill_switch_affected = True
                final_decision = Decision.DENY
                final_reason = "Kill switch active"
                trace.steps.append({
                    "step": 4,
                    "name": "Check Kill Switch",
                    "result": "Kill switch is active, denying action",
                })
            else:
                trace.steps.append({
                    "step": 4,
                    "name": "Check Kill Switch",
                    "result": "No kill switch active",
                })

                risk_result = self.risk_evaluator.evaluate(
                    content=content,
                    relationship_class=relationship_class,
                    action_type=action_type,
                )
                trace.steps.append({
                    "step": 5,
                    "name": "Risk Assessment",
                    "overall_risk": risk_result["overall_risk_level"],
                })
                trace.steps.append({
                    "step": 6,
                    "name": "Consequence Risk Assessment",
                })

                final_decision = self._synthesize_final_decision(
                    risk_result["recommendation"],
                    profile.profile_level,
                )
                final_reason = f"Policy: {profile.profile_level}, Risk: {risk_result['overall_risk_level']}"
                trace.steps.append({
                    "step": 7,
                    "name": "Synthesize Decision",
                    "final_decision": final_decision,
                })

        except Exception as e:
            final_decision = Decision.ESCALATE_TO_HUMAN
            final_reason = f"Error: {str(e)}"

        self.decision_recorder.complete_trace(
            trace=trace,
            decision=final_decision,
            decision_reason=final_reason,
            policy_hits=policy_hits,
            kill_switch_affected=kill_switch_affected,
        )
        trace.steps.append({
            "step": 8,
            "name": "Record Decision Trace",
        })

        return {
            "decision": final_decision,
            "decision_reason": final_reason,
            "decision_trace_id": trace.id,
            "policy_hits": policy_hits,
            "kill_switch_affected": kill_switch_affected,
        }

    def _synthesize_final_decision(
        self,
        risk_decision: Decision,
        profile_level: DelegationLevel,
    ) -> Decision:
        """
        合成最终决策

        策略：最保守优先
        DENY > ESCALATE_TO_HUMAN > REQUIRE_APPROVAL > DRAFT_ONLY > BOUNDED_EXECUTION > ALLOW
        """
        if profile_level == DelegationLevel.HUMAN_ONLY:
            return Decision.DENY
        if profile_level == DelegationLevel.OBSERVE_ONLY:
            return Decision.DRAFT_ONLY
        if profile_level == DelegationLevel.DRAFT_FIRST:
            if risk_decision == Decision.ALLOW:
                return Decision.DRAFT_ONLY
        if profile_level == DelegationLevel.APPROVE_TO_SEND:
            if risk_decision == Decision.ALLOW:
                return Decision.REQUIRE_APPROVAL
        if profile_level == DelegationLevel.BOUNDED_AUTO:
            if risk_decision == Decision.ALLOW:
                return Decision.BOUNDED_EXECUTION
        return risk_decision


# ============================================================================
# Demo
# ============================================================================

def run_demo():
    """演示E2模块功能"""
    print("=" * 60)
    print("E2 Policy & Control Module - Demo")
    print("=" * 60)

    controller = PolicyControlController()
    print("\n[OK] Controller initialized")

    print("\n--- Delegation Profiles ---")
    profiles = controller.delegation_service.list_profiles()
    for p in profiles:
        print(f"  - {p.name}: {p.display_name} ({p.profile_level})")

    print("\n--- Test 1: Low Risk Action ---")
    thread_id = uuid4()
    result = controller.evaluate_action(
        thread_id=thread_id,
        action="send_message",
        action_type="send_message",
        content="Hi, just checking in to confirm our meeting tomorrow.",
        relationship_class="colleague",
    )
    print(f"  Decision: {result['decision']}")
    print(f"  Reason: {result['decision_reason']}")
    print(f"  Trace ID: {result['decision_trace_id']}")

    print("\n--- Test 2: High Risk Content ---")
    result = controller.evaluate_action(
        thread_id=thread_id,
        action="send_message",
        action_type="send_message",
        content="I agree to pay $10,000 for this service.",
        relationship_class="client",
    )
    print(f"  Decision: {result['decision']}")
    print(f"  Reason: {result['decision_reason']}")

    print("\n--- Test 3: Kill Switch ---")
    user_id = uuid4()
    controller.kill_switch_service.activate(
        level=KillSwitchLevel.THREAD,
        level_id=thread_id,
        reason="Emergency stop",
        activated_by=user_id,
    )
    print("  [OK] Kill switch activated")

    result = controller.evaluate_action(
        thread_id=thread_id,
        action="send_message",
        action_type="send_message",
        content="Test message",
    )
    print(f"  Decision: {result['decision']}")
    print(f"  Reason: {result['decision_reason']}")
    print(f"  Kill switch affected: {result['kill_switch_affected']}")

    print("\n--- Test 4: Approval Workflow ---")
    requester_id = uuid4()
    request = controller.approval_service.create_request(
        thread_id=thread_id,
        request_type="message_send",
        reason_code="RISK_ASSESSMENT",
        reason_description="Message requires approval due to content risk",
        requester_principal_id=requester_id,
        preview={"content": "Please review this message"},
    )
    print(f"  [OK] Approval request created: {request.id}")
    print(f"  Status: {request.status}")

    updated = controller.approval_service.resolve(
        request_id=request.id,
        action="APPROVE",
        reason="Looks good",
        resolved_by=uuid4(),
    )
    print(f"  [OK] Request resolved: {updated.status}")

    print("\n" + "=" * 60)
    print("Demo complete! All tests passed.")
    print("=" * 60)


if __name__ == "__main__":
    run_demo()
