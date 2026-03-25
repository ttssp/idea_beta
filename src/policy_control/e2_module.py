
"""
E2 Policy & Control Module - Simplified Working Version

This is a complete, working implementation of the E2 module.
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

# ============================================================================
# Enums & Constants
# ============================================================================

class DelegationLevel(str, Enum):
    OBSERVE_ONLY = "observe_only"
    DRAFT_FIRST = "draft_first"
    APPROVE_TO_SEND = "approve_to_send"
    BOUNDED_AUTO = "bounded_auto"
    HUMAN_ONLY = "human_only"


class Decision(str, Enum):
    ALLOW = "allow"
    DRAFT_ONLY = "draft_only"
    REQUIRE_APPROVAL = "require_approval"
    BOUNDED_EXECUTION = "bounded_execution"
    ESCALATE_TO_HUMAN = "escalate_to_human"
    DENY = "deny"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    MODIFIED = "modified"
    TAKEN_OVER = "taken_over"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class KillSwitchLevel(str, Enum):
    GLOBAL = "global"
    PROFILE = "profile"
    THREAD = "thread"


SYSTEM_PROFILES = [
    {
        "name": "observe_only",
        "display_name": "仅观察",
        "description": "系统只观察与建议，不起草不发送",
        "profile_level": DelegationLevel.OBSERVE_ONLY,
        "allowed_actions": [],
    },
    {
        "name": "draft_first",
        "display_name": "优先起草",
        "description": "自动起草消息，但所有消息需人工确认",
        "profile_level": DelegationLevel.DRAFT_FIRST,
        "allowed_actions": ["draft_message"],
    },
    {
        "name": "approve_to_send",
        "display_name": "审批发送",
        "description": "低风险动作自动准备，用户一键审批后发出",
        "profile_level": DelegationLevel.APPROVE_TO_SEND,
        "allowed_actions": ["draft_message", "prepare_action"],
    },
    {
        "name": "bounded_auto",
        "display_name": "边界内自动",
        "description": "在明确预算和动作边界内自动执行",
        "profile_level": DelegationLevel.BOUNDED_AUTO,
        "allowed_actions": ["draft_message", "send_message", "schedule_followup"],
    },
    {
        "name": "human_only",
        "display_name": "仅人工",
        "description": "该类关系或场景禁止代理主动介入",
        "profile_level": DelegationLevel.HUMAN_ONLY,
        "allowed_actions": [],
    },
]


# ============================================================================
# Data Models
# ============================================================================

@dataclass
class DelegationProfile:
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    display_name: str = ""
    description: str | None = None
    profile_level: DelegationLevel = DelegationLevel.OBSERVE_ONLY
    allowed_actions: list = field(default_factory=list)
    is_system_defined: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ApprovalRequest:
    id: UUID = field(default_factory=uuid4)
    thread_id: UUID = field(default_factory=uuid4)
    request_type: str = "message_send"
    reason_code: str = ""
    reason_description: str | None = None
    status: ApprovalStatus = ApprovalStatus.PENDING
    preview: dict | None = None
    resolution: dict | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class KillSwitch:
    id: UUID = field(default_factory=uuid4)
    level: KillSwitchLevel = KillSwitchLevel.THREAD
    level_id: UUID | None = None
    reason: str = ""
    is_active: bool = True
    activated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class DecisionTrace:
    id: UUID = field(default_factory=uuid4)
    thread_id: UUID = field(default_factory=uuid4)
    decision: Decision = Decision.ESCALATE_TO_HUMAN
    decision_reason: str = ""
    steps: list = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)


# ============================================================================
# Services
# ============================================================================

class DelegationService:
    """委托档位服务"""

    def __init__(self):
        self._profiles: dict[UUID, DelegationProfile] = {}
        self._thread_bindings: dict[UUID, UUID] = {}
        self._initialize_system_profiles()

    def _initialize_system_profiles(self):
        for data in SYSTEM_PROFILES:
            profile = DelegationProfile(
                name=data["name"],
                display_name=data["display_name"],
                description=data["description"],
                profile_level=data["profile_level"],
                allowed_actions=data["allowed_actions"],
                is_system_defined=True,
            )
            self._profiles[profile.id] = profile

    def list_profiles(self):
        return list(self._profiles.values())

    def get_profile(self, profile_id):
        return self._profiles.get(profile_id)

    def get_profile_by_name(self, name):
        for p in self._profiles.values():
            if p.name == name:
                return p
        return None

    def get_effective_profile(self, thread_id=None):
        if thread_id and thread_id in self._thread_bindings:
            profile_id = self._thread_bindings[thread_id]
            profile = self._profiles.get(profile_id)
            if profile:
                return profile
        return self.get_profile_by_name("observe_only")

    def bind_thread_profile(self, thread_id, profile_id):
        if profile_id in self._profiles:
            self._thread_bindings[thread_id] = profile_id


class ApprovalService:
    """审批服务"""

    def __init__(self):
        self._requests: dict[UUID, ApprovalRequest] = {}

    def create_request(self, thread_id, reason_code, preview=None):
        request = ApprovalRequest(
            thread_id=thread_id,
            reason_code=reason_code,
            preview=preview,
            status=ApprovalStatus.PENDING,
        )
        self._requests[request.id] = request
        return request

    def get_request(self, request_id):
        return self._requests.get(request_id)

    def list_requests(self, thread_id=None, status=None):
        requests = list(self._requests.values())
        if thread_id:
            requests = [r for r in requests if r.thread_id == thread_id]
        if status:
            requests = [r for r in requests if r.status == status]
        return requests

    def resolve(self, request_id, action, reason=None):
        request = self._requests.get(request_id)
        if not request:
            return None
        if action == "APPROVE":
            request.status = ApprovalStatus.APPROVED
        elif action == "REJECT":
            request.status = ApprovalStatus.REJECTED
        elif action == "TAKEOVER":
            request.status = ApprovalStatus.TAKEN_OVER
        request.resolution = {"action": action, "reason": reason}
        return request


class RiskEvaluator:
    """风险评估器"""

    def __init__(self):
        self._critical_keywords = ["$", "price", "discount", "payment", "contract", "agree", "promise"]
        self._high_keywords = ["terminate", "cancel", "complain", "angry", "refuse", "reject"]

    def evaluate(self, content=None, relationship_class=None, action_type=None):
        rel_risk = self._evaluate_relationship(relationship_class)
        act_risk = self._evaluate_action(action_type)
        con_risk = self._evaluate_content(content)

        max_risk = max(rel_risk, act_risk, con_risk)
        overall = self._score_to_level(max_risk)

        recommendation = self._risk_to_decision(overall)

        return {
            "overall_risk_level": overall,
            "relationship_risk": rel_risk,
            "action_risk": act_risk,
            "content_risk": con_risk,
            "recommendation": recommendation,
        }

    def _evaluate_relationship(self, rc):
        if rc in ["family", "core_client", "executive"]:
            return 5
        if rc in ["client", "vendor"]:
            return 3
        if rc in ["colleague", "team_member", "internal_collaborator"]:
            return 1
        return 3

    def _evaluate_action(self, at):
        if at in ["make_payment", "sign_contract", "make_commitment"]:
            return 5
        if at in ["send_message", "schedule_meeting"]:
            return 3
        if at in ["draft_message", "suggest_action"]:
            return 1
        return 3

    def _evaluate_content(self, content):
        if not content:
            return 1
        content_lower = content.lower()
        for k in self._critical_keywords:
            if k in content_lower:
                return 5
        for k in self._high_keywords:
            if k in content_lower:
                return 4
        return 1

    def _score_to_level(self, score):
        if score <= 1:
            return RiskLevel.LOW
        elif score <= 3:
            return RiskLevel.MEDIUM
        elif score <= 4:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL

    def _risk_to_decision(self, level):
        if level == RiskLevel.LOW:
            return Decision.ALLOW
        elif level == RiskLevel.MEDIUM:
            return Decision.REQUIRE_APPROVAL
        elif level == RiskLevel.HIGH:
            return Decision.ESCALATE_TO_HUMAN
        else:
            return Decision.DENY


class KillSwitchService:
    """熔断服务"""

    def __init__(self):
        self._switches: dict[UUID, KillSwitch] = {}

    def activate(self, level, reason, activated_by, level_id=None):
        switch = KillSwitch(
            level=level,
            level_id=level_id,
            reason=reason,
            is_active=True,
        )
        self._switches[switch.id] = switch
        return switch

    def deactivate(self, switch_id):
        switch = self._switches.get(switch_id)
        if switch:
            switch.is_active = False
        return switch

    def check(self, level, level_id=None):
        for s in self._switches.values():
            if not s.is_active:
                continue
            if s.level == KillSwitchLevel.GLOBAL:
                return True
            if s.level == level and s.level_id == level_id:
                return True
        return False

    def get_active_switches(self):
        return [s for s in self._switches.values() if s.is_active]


class DecisionRecorder:
    """决策记录器"""

    def __init__(self):
        self._traces: dict[UUID, DecisionTrace] = {}

    def start_trace(self, thread_id):
        trace = DecisionTrace(thread_id=thread_id)
        self._traces[trace.id] = trace
        return trace

    def complete_trace(self, trace, decision, reason):
        trace.decision = decision
        trace.decision_reason = reason
        return trace

    def get_trace(self, trace_id):
        return self._traces.get(trace_id)


# ============================================================================
# Main Controller
# ============================================================================

class PolicyControlController:
    """
    策略控制主控制器 - 8步决策链
    """

    def __init__(self):
        self.delegation_service = DelegationService()
        self.approval_service = ApprovalService()
        self.risk_evaluator = RiskEvaluator()
        self.kill_switch_service = KillSwitchService()
        self.decision_recorder = DecisionRecorder()

    def evaluate_action(
        self,
        thread_id,
        action,
        action_type,
        content=None,
        relationship_class=None,
    ):
        """
        8步决策链主入口
        """
        trace = self.decision_recorder.start_trace(thread_id)

        final_decision = Decision.ESCALATE_TO_HUMAN
        final_reason = "Error during evaluation"
        kill_switch_affected = False

        # Step 1 & 2: Get delegation profile
        profile = self.delegation_service.get_effective_profile(thread_id)
        trace.steps.append({
            "step": 2,
            "name": "Read Delegation Profile",
            "profile": profile.name,
        })

        # Step 3: Candidate action (provided)
        trace.steps.append({
            "step": 3,
            "name": "Candidate Action",
            "action": action,
        })

        # Step 4: Check kill switch
        if self.kill_switch_service.check(KillSwitchLevel.THREAD, thread_id):
            kill_switch_affected = True
            final_decision = Decision.DENY
            final_reason = "Kill switch active"
        else:
            # Step 5 & 6: Risk evaluation
            risk_result = self.risk_evaluator.evaluate(
                content=content,
                relationship_class=relationship_class,
                action_type=action_type,
            )
            trace.steps.append({
                "step": 5,
                "name": "Risk Evaluation",
                "result": risk_result["overall_risk_level"],
            })

            # Step 7: Synthesize decision
            final_decision = self._synthesize_decision(
                risk_result["recommendation"],
                profile.profile_level,
            )
            final_reason = f"Risk: {risk_result['overall_risk_level']}, Profile: {profile.profile_level}"

        # Step 8: Record trace
        self.decision_recorder.complete_trace(trace, final_decision, final_reason)

        return {
            "decision": final_decision,
            "decision_reason": final_reason,
            "decision_trace_id": trace.id,
            "kill_switch_affected": kill_switch_affected,
        }

    def _synthesize_decision(self, risk_decision, profile_level):
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
        return risk_decision


# ============================================================================
# Demo
# ============================================================================

def run_demo():
    """演示E2模块功能"""
    print("="*60)
    print("E2 Policy & Control Module - Demo")
    print("="*60)

    controller = PolicyControlController()
    print("\n✓ Controller initialized")

    # Test 1: List delegation profiles
    print("\n--- Delegation Profiles ---")
    profiles = controller.delegation_service.list_profiles()
    for p in profiles:
        print(f"  - {p.name}: {p.display_name} ({p.profile_level})")

    # Test 2: Evaluate low risk action
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

    # Test 3: Evaluate high risk content
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

    # Test 4: Kill Switch
    print("\n--- Test 3: Kill Switch ---")
    user_id = uuid4()
    controller.kill_switch_service.activate(
        level=KillSwitchLevel.THREAD,
        level_id=thread_id,
        reason="Emergency stop",
        activated_by=user_id,
    )
    print("  ✓ Kill switch activated")

    result = controller.evaluate_action(
        thread_id=thread_id,
        action="send_message",
        action_type="send_message",
        content="Test message",
    )
    print(f"  Decision: {result['decision']}")
    print(f"  Reason: {result['decision_reason']}")
    print(f"  Kill switch affected: {result['kill_switch_affected']}")

    # Test 5: Approval workflow
    print("\n--- Test 4: Approval Workflow ---")
    request = controller.approval_service.create_request(
        thread_id=thread_id,
        reason_code="RISK_ASSESSMENT",
        preview={"content": "Please review"},
    )
    print(f"  ✓ Approval request created: {request.id}")
    print(f"  Status: {request.status}")

    updated = controller.approval_service.resolve(request.id, "APPROVE", "Looks good")
    print(f"  ✓ Request resolved: {updated.status}")

    print("\n" + "="*60)
    print("Demo complete!")
    print("="*60)


if __name__ == "__main__":
    run_demo()
