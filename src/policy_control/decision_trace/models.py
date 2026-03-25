
"""
Decision Trace Data Models
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4
from datetime import datetime

from ..common.constants import Decision


@dataclass
class DecisionStep:
    """决策链中的单步记录"""

    step_number: int
    step_name: str
    description: str
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    duration_ms: Optional[int] = None


@dataclass
class DecisionTrace:
    """决策追踪记录"""

    id: UUID = field(default_factory=uuid4)
    thread_id: UUID = field(default_factory=uuid4)
    action_run_id: Optional[UUID] = None
    decision: Decision = Decision.REQUIRE_APPROVAL
    decision_reason: Optional[str] = None
    steps: List[DecisionStep] = field(default_factory=list)
    policy_hits: Optional[List[Dict]] = None
    risk_assessment_id: Optional[UUID] = None
    kill_switch_affected: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)

    def add_step(
        self,
        step_number: int,
        step_name: str,
        description: str,
        input_data: Optional[Dict] = None,
        output_data: Optional[Dict] = None,
        duration_ms: Optional[int] = None,
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

    def to_dict(self) -&gt; Dict[str, Any]:
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
