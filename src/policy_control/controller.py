
"""
Policy & Control Controller

主控制器：整合所有模块，提供统一的8步决策链接口
"""
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from .common.constants import Decision, RiskLevel, PolicyScope, PolicyEffect
from .common.types import PolicyContext, RiskContext
from .common.exceptions import KillSwitchActiveError
from .delegation.service import DelegationService
from .policy.engine import PolicyEngine
from .policy.evaluator import PolicyEvaluator
from .approval.service import ApprovalService
from .risk.synthesizer import RiskSynthesizer
from .kill_switch.service import KillSwitchService
from .decision_trace.recorder import DecisionRecorder


class PolicyControlController:
    """
    策略控制主控制器

    提供统一的8步决策链接口
    """

    def __init__(self):
        # 初始化各服务
        self.delegation_service = DelegationService()
        self.policy_engine = PolicyEngine()
        self.policy_evaluator = PolicyEvaluator(
            self.delegation_service,
            self.policy_engine,
        )
        self.approval_service = ApprovalService()
        self.risk_synthesizer = RiskSynthesizer()
        self.kill_switch_service = KillSwitchService()
        self.decision_recorder = DecisionRecorder()

        # 初始化一些默认策略规则
        self._initialize_default_policies()

    def _initialize_default_policies(self):
        """初始化默认策略规则"""
        from .policy.models import PolicyRule

        # 默认规则：低风险动作允许
        self.policy_engine.add_rule(PolicyRule(
            name="default_low_risk_allow",
            description="Allow low risk actions",
            scope=PolicyScope.GLOBAL,
            action="*",
            effect=PolicyEffect.ALLOW,
            conditions={},
            priority=0,
        ))

        # 默认规则：高风险动作需要审批
        self.policy_engine.add_rule(PolicyRule(
            name="default_high_risk_require_approval",
            description="High risk actions require approval",
            scope=PolicyScope.GLOBAL,
            action="*",
            effect=PolicyEffect.REQUIRE_APPROVAL,
            conditions={"action_risk": {"greater_than": 3}},
            priority=10,
        ))

    def evaluate_action(
        self,
        thread_id: UUID,
        action: str,
        action_type: str,
        content: Optional[str] = None,
        relationship_class: Optional[str] = None,
        relationship_id: Optional[UUID] = None,
        thread_objective: Optional[str] = None,
        thread_status: Optional[str] = None,
        action_run_id: Optional[UUID] = None,
    ) -> Dict[str, Any]:
        """
        8步决策链主入口

        执行流程：
        1. 读取 thread objective 与当前状态
        2. 读取 relationship class 与 delegation profile
        3. 生成候选动作
        4. 进行规则命中与预算检查
        5. 进行内容/语义风险评估
        6. 进行结果代价评估
        7. 决定：自动执行/进入审批/升级人工或拒绝
        8. 记录完整 decision trace

        Returns:
            {
                "decision": Decision,
                "decision_reason": str,
                "decision_trace_id": UUID,
                "risk_assessment": Optional[Dict],
                "policy_hits": Optional[List],
            }
        """
        # 开始记录决策追踪
        trace = self.decision_recorder.start_trace(
            thread_id=thread_id,
            action_run_id=action_run_id,
        )

        step_data = []
        final_decision = Decision.ESCALATE_TO_HUMAN
        final_reason = "Error during evaluation"
        policy_hits = []
        risk_assessment_id = None
        kill_switch_affected = False

        try:
            # Step 1: 读取 thread objective 与当前状态
            step1_input = {
                "thread_id": str(thread_id),
                "thread_objective": thread_objective,
                "thread_status": thread_status,
            }
            self.decision_recorder.record_step_sync(
                trace, 1, "Read Thread State",
                "Reading thread objective and current state",
                input_data=step1_input,
            )
            step_data.append({
                "name": "Read Thread State",
                "description": "Reading thread objective and current state",
                "input": step1_input,
            })

            # Step 2: 读取 relationship class 与 delegation profile
            profile = self.delegation_service.get_effective_profile(
                thread_id=thread_id,
                relationship_id=relationship_id,
            )
            step2_output = {
                "profile_id": str(profile.id),
                "profile_name": profile.name,
                "profile_level": profile.profile_level.value,
            }
            self.decision_recorder.record_step_sync(
                trace, 2, "Read Delegation Profile",
                f"Using profile: {profile.name}",
                output_data=step2_output,
            )
            step_data.append({
                "name": "Read Delegation Profile",
                "description": f"Using profile: {profile.name}",
                "output": step2_output,
            })

            # Step 3: 生成候选动作（略过，由调用方提供）
            self.decision_recorder.record_step_sync(
                trace, 3, "Generate Candidate Action",
                f"Candidate action: {action}",
            )
            step_data.append({
                "name": "Generate Candidate Action",
                "description": f"Candidate action: {action}",
            })

            # Step 4: 检查熔断
            from .common.constants import KillSwitchLevel
            if self.kill_switch_service.check(KillSwitchLevel.THREAD, thread_id):
                kill_switch_affected = True
                final_decision = Decision.DENY
                final_reason = "Kill switch active"
                self.decision_recorder.record_step_sync(
                    trace, 4, "Check Kill Switch",
                    "Kill switch is active, denying action",
                )
            else:
                self.decision_recorder.record_step_sync(
                    trace, 4, "Check Kill Switch",
                    "No kill switch active",
                )
            step_data.append({
                "name": "Check Kill Switch",
                "description": "Check if kill switch is active",
            })

            if not kill_switch_affected:
                # Step 4 (cont): 进行规则命中与预算检查
                policy_context = PolicyContext(
                    thread_id=thread_id,
                    action=action,
                    relationship_class=relationship_class,
                    thread_objective=thread_objective,
                    thread_status=thread_status,
                )
                policy_decision = self.policy_evaluator.evaluate(
                    context=policy_context,
                    thread_id=thread_id,
                    relationship_id=relationship_id,
                )
                policy_hits = policy_decision.matched_rules or []
                step4b_output = {
                    "policy_decision": policy_decision.decision.value,
                    "policy_reason": policy_decision.reason,
                }
                self.decision_recorder.record_step_sync(
                    trace, 4, "Policy & Budget Check",
                    policy_decision.reason,
                    output_data=step4b_output,
                )
                step_data.append({
                    "name": "Policy & Budget Check",
                    "description": policy_decision.reason,
                    "output": step4b_output,
                })

                # Step 5: 进行内容/语义风险评估
                # Step 6: 进行结果代价评估
                risk_context = RiskContext(
                    thread_id=thread_id,
                    action=action_run_id or thread_id,
                    content=content,
                    relationship_class=relationship_class,
                    action_type=action_type,
                )
                risk_decision = self.risk_synthesizer.evaluate(risk_context)
                risk_assessment_id = risk_decision.overall_risk_level  # 简化处理
                step56_output = {
                    "overall_risk": risk_decision.overall_risk_level.value,
                    "relationship_risk": risk_decision.relationship_risk,
                    "action_risk": risk_decision.action_risk,
                    "content_risk": risk_decision.content_risk,
                    "consequence_risk": risk_decision.consequence_risk,
                    "recommendation": risk_decision.recommendation.value,
                }
                self.decision_recorder.record_step_sync(
                    trace, 5, "Content Risk Assessment",
                    "Evaluating content risk",
                    output_data=step56_output,
                )
                self.decision_recorder.record_step_sync(
                    trace, 6, "Consequence Risk Assessment",
                    "Evaluating consequence risk",
                )
                step_data.append({
                    "name": "Risk Assessment",
                    "description": risk_decision.reason,
                    "output": step56_output,
                })

                # Step 7: 合成最终决策
                final_decision = self._synthesize_final_decision(
                    policy_decision.decision,
                    risk_decision.recommendation,
                    profile.profile_level,
                )
                final_reason = f"Policy: {policy_decision.decision.value}, Risk: {risk_decision.recommendation.value}"
                self.decision_recorder.record_step_sync(
                    trace, 7, "Synthesize Decision",
                    final_reason,
                    output_data={"final_decision": final_decision.value},
                )
                step_data.append({
                    "name": "Synthesize Decision",
                    "description": final_reason,
                    "output": {"final_decision": final_decision.value},
                })

        except KillSwitchActiveError:
            final_decision = Decision.DENY
            final_reason = "Kill switch active"
            kill_switch_affected = True
        except Exception as e:
            # 默认保守策略：异常情况一律 escalate
            final_decision = Decision.ESCALATE_TO_HUMAN
            final_reason = f"Error: {str(e)}"

        # Step 8: 记录完整 decision trace
        self.decision_recorder.complete_trace(
            trace=trace,
            decision=final_decision,
            decision_reason=final_reason,
            policy_hits=policy_hits,
            risk_assessment_id=risk_assessment_id,
            kill_switch_affected=kill_switch_affected,
        )
        step_data.append({
            "name": "Record Decision Trace",
            "description": "Recording complete decision trace",
        })

        return {
            "decision": final_decision,
            "decision_reason": final_reason,
            "decision_trace_id": trace.id,
            "decision_trace": trace.to_dict(),
            "policy_hits": policy_hits,
            "kill_switch_affected": kill_switch_affected,
        }

    def _synthesize_final_decision(
        self,
        policy_decision: Decision,
        risk_decision: Decision,
        profile_level: Any,
    ) -> Decision:
        """
        合成最终决策

        策略：最保守优先
        DENY > ESCALATE_TO_HUMAN > REQUIRE_APPROVAL > DRAFT_ONLY > BOUNDED_EXECUTION > ALLOW
        """
        priority_order = [
            Decision.DENY,
            Decision.ESCALATE_TO_HUMAN,
            Decision.REQUIRE_APPROVAL,
            Decision.DRAFT_ONLY,
            Decision.BOUNDED_EXECUTION,
            Decision.ALLOW,
        ]

        decisions = [policy_decision, risk_decision]
        for d in priority_order:
            if d in decisions:
                return d

        return Decision.ESCALATE_TO_HUMAN  # 默认保守

    def get_decision_trace(self, trace_id: UUID):
        """获取决策追踪"""
        return self.decision_recorder.get_trace(trace_id)

    def get_thread_traces(self, thread_id: UUID, limit: int = 100):
        """获取线程的决策追踪列表"""
        return self.decision_recorder.get_traces_for_thread(thread_id, limit)
