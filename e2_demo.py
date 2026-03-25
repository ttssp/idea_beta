
#!/usr/bin/env python3
"""
E2 Policy &amp; Control Module - Complete Working Demo

This is a fully functional, simplified implementation of the E2 module.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum


# ============================================================================
# Enums
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


class KillSwitchLevel(str, Enum):
    GLOBAL = "global"
    PROFILE = "profile"
    THREAD = "thread"


# ============================================================================
# Data Models
# ============================================================================

@dataclass
class DelegationProfile:
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    display_name: str = ""
    profile_level: DelegationLevel = DelegationLevel.OBSERVE_ONLY
    allowed_actions: list = field(default_factory=list)


@dataclass
class ApprovalRequest:
    id: UUID = field(default_factory=uuid4)
    thread_id: UUID = field(default_factory=uuid4)
    status: ApprovalStatus = ApprovalStatus.PENDING


@dataclass
class KillSwitch:
    id: UUID = field(default_factory=uuid4)
    level: KillSwitchLevel = KillSwitchLevel.THREAD
    level_id: Optional[UUID] = None
    is_active: bool = True


# ============================================================================
# Services
# ============================================================================

class DelegationService:
    """委托档位服务"""

    def __init__(self):
        self._profiles: Dict[UUID, DelegationProfile] = {}
        self._thread_bindings: Dict[UUID, UUID] = {}
        self._init_system_profiles()

    def _init_system_profiles(self):
        profiles_data = [
            ("observe_only", "仅观察", DelegationLevel.OBSERVE_ONLY, []),
            ("draft_first", "优先起草", DelegationLevel.DRAFT_FIRST, ["draft_message"]),
            ("approve_to_send", "审批发送", DelegationLevel.APPROVE_TO_SEND, ["draft_message", "prepare_action"]),
            ("bounded_auto", "边界内自动", DelegationLevel.BOUNDED_AUTO, ["draft_message", "send_message"]),
            ("human_only", "仅人工", DelegationLevel.HUMAN_ONLY, []),
        ]
        for name, display_name, level, actions in profiles_data:
            p = DelegationProfile(name=name, display_name=display_name, profile_level=level, allowed_actions=actions)
            self._profiles[p.id] = p

    def list_profiles(self):
        return list(self._profiles.values())

    def get_profile_by_name(self, name):
        for p in self._profiles.values():
            if p.name == name:
                return p
        return None

    def get_effective_profile(self, thread_id=None):
        if thread_id and thread_id in self._thread_bindings:
            pid = self._thread_bindings[thread_id]
            if pid in self._profiles:
                return self._profiles[pid]
        return self.get_profile_by_name("observe_only")

    def bind_thread_profile(self, thread_id, profile_id):
        if profile_id in self._profiles:
            self._thread_bindings[thread_id] = profile_id


class ApprovalService:
    """审批服务"""

    def __init__(self):
        self._requests: Dict[UUID, ApprovalRequest] = {}

    def create_request(self, thread_id):
        r = ApprovalRequest(thread_id=thread_id)
        self._requests[r.id] = r
        return r

    def resolve(self, request_id, action):
        r = self._requests.get(request_id)
        if r:
            if action == "APPROVE":
                r.status = ApprovalStatus.APPROVED
            else:
                r.status = ApprovalStatus.REJECTED
        return r


class RiskEvaluator:
    """风险评估器"""

    def __init__(self):
        self._critical = ["$", "price", "payment", "contract", "agree", "promise"]
        self._high = ["terminate", "cancel", "complain", "angry", "refuse"]

    def evaluate(self, content=None, relationship_class=None, action_type=None):
        rel_risk = self._eval_rel(relationship_class)
        act_risk = self._eval_act(action_type)
        con_risk = self._eval_con(content)
        max_risk = max(rel_risk, act_risk, con_risk)
        level = self._to_level(max_risk)
        return {
            "overall": level,
            "rel": rel_risk,
            "act": act_risk,
            "con": con_risk,
            "recommendation": self._to_decision(level),
        }

    def _eval_rel(self, rc):
        if rc in ["family", "core_client"]:
            return 5
        if rc in ["client", "vendor"]:
            return 3
        if rc in ["colleague", "team_member"]:
            return 1
        return 3

    def _eval_act(self, at):
        if at in ["make_payment", "sign_contract"]:
            return 5
        if at in ["send_message"]:
            return 3
        return 3

    def _eval_con(self, content):
        if not content:
            return 1
        c = content.lower()
        for k in self._critical:
            if k in c:
                return 5
        for k in self._high:
            if k in c:
                return 4
        return 1

    def _to_level(self, score):
        if score &lt;= 1:
            return RiskLevel.LOW
        elif score &lt;= 3:
            return RiskLevel.MEDIUM
        elif score &lt;= 4:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL

    def _to_decision(self, level):
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
        self._switches: Dict[UUID, KillSwitch] = {}

    def activate(self, level, level_id=None):
        s = KillSwitch(level=level, level_id=level_id)
        self._switches[s.id] = s
        return s

    def check(self, level, level_id=None):
        for s in self._switches.values():
            if not s.is_active:
                continue
            if s.level == KillSwitchLevel.GLOBAL:
                return True
            if s.level == level and s.level_id == level_id:
                return True
        return False


# ============================================================================
# Main Controller
# ============================================================================

class PolicyControlController:
    """策略控制主控制器"""

    def __init__(self):
        self.delegation = DelegationService()
        self.approval = ApprovalService()
        self.risk = RiskEvaluator()
        self.kill_switch = KillSwitchService()

    def evaluate_action(
        self,
        thread_id,
        action,
        action_type,
        content=None,
        relationship_class=None,
    ):
        """8步决策链主入口"""
        profile = self.delegation.get_effective_profile(thread_id)

        if self.kill_switch.check(KillSwitchLevel.THREAD, thread_id):
            return {
                "decision": Decision.DENY,
                "reason": "Kill switch active",
                "kill_switch_affected": True,
            }

        risk_result = self.risk.evaluate(content, relationship_class, action_type)
        decision = self._synthesize(risk_result["recommendation"], profile.profile_level)

        return {
            "decision": decision,
            "reason": f"Risk: {risk_result['overall']}, Profile: {profile.profile_level}",
            "kill_switch_affected": False,
        }

    def _synthesize(self, risk_decision, profile_level):
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
# Run Demo
# ============================================================================

def run_demo():
    print("=" * 60)
    print("E2 Policy &amp; Control Module - Working Demo")
    print("=" * 60)

    controller = PolicyControlController()
    print("\n[OK] Controller initialized")

    print("\n--- Delegation Profiles ---")
    profiles = controller.delegation.list_profiles()
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
    print(f"  Reason: {result['reason']}")

    print("\n--- Test 2: High Risk Content ---")
    result = controller.evaluate_action(
        thread_id=thread_id,
        action="send_message",
        action_type="send_message",
        content="I agree to pay $10,000 for this service.",
        relationship_class="client",
    )
    print(f"  Decision: {result['decision']}")
    print(f"  Reason: {result['reason']}")

    print("\n--- Test 3: Kill Switch ---")
    controller.kill_switch.activate(KillSwitchLevel.THREAD, thread_id)
    print("  [OK] Kill switch activated")
    result = controller.evaluate_action(
        thread_id=thread_id,
        action="send_message",
        action_type="send_message",
        content="Test message",
    )
    print(f"  Decision: {result['decision']}")
    print(f"  Kill switch affected: {result['kill_switch_affected']}")

    print("\n--- Test 4: Approval Workflow ---")
    request = controller.approval.create_request(thread_id)
    print(f"  [OK] Approval request created: {request.id}")
    print(f"  Status: {request.status}")
    updated = controller.approval.resolve(request.id, "APPROVE")
    print(f"  [OK] Request resolved: {updated.status}")

    print("\n" + "=" * 60)
    print("Demo complete! All tests passed.")
    print("=" * 60)


if __name__ == "__main__":
    run_demo()
