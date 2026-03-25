
"""
Decision Trace Data Models
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from ..common.constants import Decision


@dataclass
class DecisionStep:
    """决策链中的单步记录"""

    step_number: int
    step_name: str
    description: str
    input_data: dict[str, Any] | None = None
    output_data: dict[str, Any] | None = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    duration_ms: int | None = None


@dataclass
class DecisionTrace:
    """决策追踪记录"""

    id: UUID = field(default_factory=uuid4)
    thread_id: UUID = field(default_factory=uuid4)
    action_run_id: UUID | None = None
    decision: Decision = Decision.REQUIRE_APPROVAL
    decision_reason: str | None = None
    steps: list[DecisionStep] = field(default_factory=list)
    policy_hits: list[dict] | None = None
    risk_assessment_id: UUID | None = None
    kill_switch_affected: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)

    def add_step(
        self,
        step_number: int,
        step_name: str,
        description: str,
        input_data: dict | None = None,
        output_data: dict | None = None,
        duration_ms: int | None = None,
    ):
        """添加决策步骤"""
        step = DecisionStep(
            step_number=step_number,
            step_name=step_name,
            description=description,
            input_data=input_data,
            output_data=output_data,
            timestamp=datetime.utcnow(),
            duration_ms=duration_ms,
        )
        self.steps.append(step)

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "id": str(self.id),
            "thread_id": str(self.thread_id),
            "action_run_id": str(self.action_run_id) if self.action_run_id else None,
            "decision": self.decision.value,
            "decision_reason": self.decision_reason,
            "steps": [
                {
                    "step_number": s.step_number,
                    "step_name": s.step_name,
                    "description": s.description,
                    "input_data": s.input_data,
                    "output_data": s.output_data,
                    "timestamp": s.timestamp.isoformat(),
                    "duration_ms": s.duration_ms,
                }
                for s in self.steps
            ],
            "policy_hits": self.policy_hits,
            "risk_assessment_id": str(self.risk_assessment_id) if self.risk_assessment_id else None,
            "kill_switch_affected": self.kill_switch_affected,
            "created_at": self.created_at.isoformat(),
        }
