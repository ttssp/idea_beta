
#!/usr/bin/env python3
"""
E2 Policy &amp; Control Module - Final Working Version
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum


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


class DelegationService:
    def __init__(self):
        self._profiles = {}
        self._thread_bindings = {}
        self._init_profiles()

    def _init_profiles(self):
        data = [
            ("observe_only", "Only Observe", DelegationLevel.OBSERVE_ONLY, []),
            ("draft_first", "Draft First", DelegationLevel.DRAFT_FIRST, ["draft_message"]),
            ("approve_to_send", "Approve to Send", DelegationLevel.APPROVE_TO_SEND, ["draft", "prepare"]),
            ("bounded_auto", "Bounded Auto", DelegationLevel.BOUNDED_AUTO, ["draft", "send"]),
            ("human_only", "Human Only", DelegationLevel.HUMAN_ONLY, []),
        ]
        for name, display, level, actions in data:
            p = DelegationProfile(name=name, display_name=display, profile_level=level, allowed_actions=actions)
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
    def __init__(self):
        self._requests = {}

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
    def __init__(self):
        self._critical = ["$", "price", "payment", "contract", "agree", "promise"]
        self._high = ["terminate", "cancel", "complain", "angry", "refuse"]

    def evaluate(self, content=None, relationship_class=None, action_type=None):
        rel = 3
        if relationship_class in ["family", "core_client"]:
            rel = 5
        elif relationship_class in ["colleague", "team_member"]:
            rel = 1

        act = 3
        if action_type in ["make_payment", "sign_contract"]:
            act = 5
        elif action_type in ["send_message"]:
            act = 3

        con = 1
        if content:
            c = content.lower()
            for k in self._critical:
                if k in c:
                    con = 5
                    break
            if con == 1:
                for k in self._high:
                    if k in c:
                        con = 4
                        break

        max_score = max(rel, act, con)
        level = RiskLevel.LOW
        if max_score &gt; 4:
            level = RiskLevel.CRITICAL
        elif max_score &gt; 3:
            level = RiskLevel.HIGH
        elif max_score &gt; 1:
            level = RiskLevel.MEDIUM

        rec = Decision.ALLOW
        if level == RiskLevel.CRITICAL:
            rec = Decision.DENY
        elif level == RiskLevel.HIGH:
            rec = Decision.ESCALATE_TO_HUMAN
        elif level == RiskLevel.MEDIUM:
            rec = Decision.REQUIRE_APPROVAL

        return {
            "overall": level,
            "rel": rel,
            "act": act,
            "con": con,
            "recommendation": rec,
        }


class KillSwitchService:
    def __init__(self):
        self._switches = {}

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


class PolicyControlController:
    def __init__(self):
        self.delegation = DelegationService()
        self.approval = ApprovalService()
        self.risk = RiskEvaluator()
        self.kill_switch = KillSwitchService()

    def evaluate_action(self, thread_id, action, action_type, content=None, relationship_class=None):
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
            "reason": "Risk: " + str(risk_result["overall"]) + ", Profile: " + str(profile.profile_level),
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


def run_demo():
    print("=" * 60)
    print("E2 Policy &amp; Control Module - Demo")
    print("=" * 60)

    controller = PolicyControlController()
    print("\n[OK] Controller initialized")

    print("\n--- Delegation Profiles ---")
    profiles = controller.delegation.list_profiles()
    for p in profiles:
        print("  - " + p.name + ": " + p.display_name)

    print("\n--- Test 1: Low Risk Action ---")
    thread_id = uuid4()
    result = controller.evaluate_action(
        thread_id=thread_id,
        action="send_message",
        action_type="send_message",
        content="Hi, just checking in to confirm our meeting tomorrow.",
        relationship_class="colleague",
    )
    print("  Decision: " + str(result["decision"]))
    print("  Reason: " + result["reason"])

    print("\n--- Test 2: High Risk Content ---")
    result = controller.evaluate_action(
        thread_id=thread_id,
        action="send_message",
        action_type="send_message",
        content="I agree to pay $10,000 for this service.",
        relationship_class="client",
    )
    print("  Decision: " + str(result["decision"]))
    print("  Reason: " + result["reason"])

    print("\n--- Test 3: Kill Switch ---")
    controller.kill_switch.activate(KillSwitchLevel.THREAD, thread_id)
    print("  [OK] Kill switch activated")
    result = controller.evaluate_action(
        thread_id=thread_id,
        action="send_message",
        action_type="send_message",
        content="Test message",
    )
    print("  Decision: " + str(result["decision"]))
    print("  Kill switch affected: " + str(result["kill_switch_affected"]))

    print("\n--- Test 4: Approval Workflow ---")
    request = controller.approval.create_request(thread_id)
    print("  [OK] Approval request created")
    print("  Status: " + str(request.status))
    updated = controller.approval.resolve(request.id, "APPROVE")
    print("  [OK] Request resolved: " + str(updated.status))

    print("\n" + "=" * 60)
    print("Demo complete!")
    print("=" * 60)


if __name__ == "__main__":
    run_demo()
