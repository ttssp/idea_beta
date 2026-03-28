#!/usr/bin/env python3
"""
Communication OS v1 - 交互式测试体验脚本

这个脚本让你可以手动体验 Communication OS 的核心功能。
"""

import sys
from pathlib import Path

# 设置路径
project_root = Path(__file__).parent
src_dir = project_root / "src"
backend_dir = project_root / "backend" / "e3"

if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from datetime import datetime, UTC, timedelta
from uuid import uuid4

# 导入合同
from myproj.core.contracts import (
    AuthorityGrant,
    AuthorityGrantStatus,
    SenderStack,
    DisclosurePolicy,
    DisclosurePreview,
    AttentionDecision,
    AttentionDisposition,
    ActionEnvelope,
    ActionExecutionMode,
    ActionTarget,
    ChannelKind,
    RiskLevel,
    RiskPosture,
    DelegationMode,
    PrincipalKind,
    ActorRef,
    ThreadContextRef,
    RelationshipContextRef,
    DisclosureMode,
)

# 颜色输出
class Colors:
    GREEN = "\033[92m"
    BLUE = "\033[94m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    ENDC = "\033[0m"


def print_section(title: str):
    print(f"\n{Colors.BOLD}{'=' * 60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{title}{Colors.ENDC}")
    print(f"{Colors.BOLD}{'=' * 60}{Colors.ENDC}\n")


def print_success(msg: str):
    print(f"{Colors.GREEN}✅ {msg}{Colors.ENDC}")


def print_info(msg: str):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.ENDC}")


def print_warning(msg: str):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.ENDC}")


def pause():
    input(f"\n{Colors.BLUE}按 Enter 继续...{Colors.ENDC}")


def test_1_authority_grant():
    """测试 1: 创建权限授予 (AuthorityGrant)"""
    print_section("测试 1: 创建权限授予 (AuthorityGrant)")

    print_info("权限授予定义了谁可以代表谁行事，以及在什么约束下行事。")
    pause()

    # 创建参与者
    print("\n1. 创建参与者...")

    alicia = ActorRef(
        principal_id=uuid4(),
        principal_kind=PrincipalKind.HUMAN,
        display_name="Alicia Chen",
        affiliation_name="Company",
        is_human_controlled=True,
    )
    print_success(f"创建了: {alicia.display_name} ({alicia.principal_kind})")

    assistant = ActorRef(
        principal_id=uuid4(),
        principal_kind=PrincipalKind.PERSONAL_AGENT,
        display_name="Alicia's Assistant",
        affiliation_name="Company",
        is_human_controlled=False,
    )
    print_success(f"创建了: {assistant.display_name} ({assistant.principal_kind})")

    pause()

    # 创建披露策略（AuthorityGrant 需要）
    print("\n2. 创建披露策略...")
    disclosure_policy = DisclosurePolicy(
        default_mode=DisclosureMode.SEMI,
    )
    print_success("披露策略创建成功")

    pause()

    # 创建权限授予
    print("\n3. 创建权限授予...")

    grant = AuthorityGrant(
        authority_grant_id=uuid4(),
        grantor=alicia,
        delegate=assistant,
        status=AuthorityGrantStatus.ACTIVE,
        delegation_mode=DelegationMode.APPROVE_TO_SEND,
        allowed_actions=["draft_message", "send_message", "propose_time"],
        requires_approval_for=["send_message"],
        disclosure_policy=disclosure_policy,
        granted_at=datetime.now(UTC),
        expires_at=datetime.now(UTC) + timedelta(days=30),
    )

    print_success(f"权限授予 ID: {grant.authority_grant_id}")
    print(f"   授权者: {grant.grantor.display_name}")
    print(f"   被授权者: {grant.delegate.display_name}")
    print(f"   模式: {grant.delegation_mode}")
    print(f"   允许的动作: {grant.allowed_actions}")
    print(f"   需要审批: {grant.requires_approval_for}")
    print(f"   状态: {grant.status} (active={grant.is_currently_active})")

    pause()

    # 测试序列化
    print("\n4. 测试序列化/反序列化...")

    grant_json = grant.model_dump(mode="json")
    print_success("序列化为 JSON 成功")

    grant_restored = AuthorityGrant.model_validate(grant_json)
    print_success("从 JSON 反序列化成功")

    assert grant_restored.authority_grant_id == grant.authority_grant_id
    print_success("往返验证通过！")

    return grant


def test_2_sender_stack(grant):
    """测试 2: 构建发送者堆栈 (SenderStack)"""
    print_section("测试 2: 构建发送者堆栈 (SenderStack)")

    print_info("发送者堆栈显示了完整的责任链：所有者、代理、作者等。")
    pause()

    print("\n1. 创建完整的发送者堆栈...")

    scheduler = ActorRef(
        principal_id=uuid4(),
        principal_kind=PrincipalKind.SERVICE_AGENT,
        display_name="Scheduling Agent",
        is_human_controlled=False,
    )

    stack = SenderStack(
        owner=grant.grantor,
        delegate=grant.delegate,
        author=scheduler,
        disclosure_mode=DisclosureMode.FULL,
        authority_source=grant.authority_grant_id,
        authority_label="candidate_scheduling_policy_v1",
    )

    print_success("发送者堆栈创建成功！")
    print(f"   所有者 (Owner): {stack.owner.display_name}")
    print(f"   代理 (Delegate): {stack.delegate.display_name if stack.delegate else 'None'}")
    print(f"   作者 (Author): {stack.author.display_name}")
    print(f"   披露模式: {stack.disclosure_mode}")
    print(f"   权限来源: {stack.authority_label}")

    pause()

    # 测试可见参与者
    print("\n2. 测试可见参与者...")

    visible = stack.visible_actor_ids()
    print(f"   可见参与者数量: {len(visible)}")
    print_success("可见参与者去重排序成功！")

    pause()

    # 测试序列化
    print("\n3. 测试序列化/反序列化...")

    stack_json = stack.model_dump(mode="json")
    print_success("序列化为 JSON 成功")

    stack_restored = SenderStack.model_validate(stack_json)
    print_success("从 JSON 反序列化成功")

    assert stack_restored.owner.principal_id == stack.owner.principal_id
    print_success("往返验证通过！")

    return stack


def test_3_disclosure():
    """测试 3: 披露策略 (DisclosurePolicy)"""
    print_section("测试 3: 披露策略 (DisclosurePolicy)")

    print_info("披露策略决定了接收者能看到多少关于代理参与的信息。")
    pause()

    print("\n1. 创建披露策略...")

    policy = DisclosurePolicy(
        default_mode=DisclosureMode.SEMI,
        require_at_least_semi_for_external=True,
        require_full_for_sensitive_relationships=True,
        require_full_for_high_risk=True,
    )

    print_success("披露策略创建成功！")
    print(f"   默认模式: {policy.default_mode}")
    print(f"   外部至少需要 SEMI: {policy.require_at_least_semi_for_external}")
    print(f"   敏感关系需要 FULL: {policy.require_full_for_sensitive_relationships}")
    print(f"   高风险需要 FULL: {policy.require_full_for_high_risk}")

    pause()

    # 测试模式解析
    print("\n2. 测试模式解析...")

    # 测试外部、非敏感、中风险
    mode1 = policy.resolve_mode(
        is_external=True,
        is_sensitive_relationship=False,
        risk_level=RiskLevel.MEDIUM,
    )
    print(f"   外部+非敏感+中风险: {mode1}")

    # 测试外部、敏感、中风险
    mode2 = policy.resolve_mode(
        is_external=True,
        is_sensitive_relationship=True,
        risk_level=RiskLevel.MEDIUM,
    )
    print(f"   外部+敏感+中风险: {mode2}")

    # 测试外部、非敏感、高风险
    mode3 = policy.resolve_mode(
        is_external=True,
        is_sensitive_relationship=False,
        risk_level=RiskLevel.HIGH,
    )
    print(f"   外部+非敏感+高风险: {mode3}")

    print_success("模式解析测试通过！")

    pause()

    # 创建披露预览
    print("\n3. 创建披露预览...")

    preview = DisclosurePreview.from_policy(
        policy,
        is_external=True,
        is_sensitive_relationship=False,
        risk_level=RiskLevel.MEDIUM,
        rendered_text="Sent on behalf of Alicia with delegated scheduling assistance.",
    )

    print_success("披露预览创建成功！")
    print(f"   解析模式: {preview.resolved_mode}")
    print(f"   需要接收者通知: {preview.requires_recipient_notice}")
    print(f"   披露文本: {preview.rendered_text}")

    pause()

    return policy, preview


def test_4_attention_decision():
    """测试 4: 注意力决策 (AttentionDecision)"""
    print_section("测试 4: 注意力决策 (AttentionDecision)")

    print_info("注意力决策决定了是否需要中断人类。")
    pause()

    print("\n1. 创建需要审批的决策...")

    decision_approval = AttentionDecision(
        target_principal_id=uuid4(),
        disposition=AttentionDisposition.APPROVAL_REQUIRED,
        reason_code="approval_gate",
        summary="This interview scheduling message requires human approval before send.",
        requires_human_action=True,
        notify_now=True,
    )

    print_success("审批决策创建成功！")
    print(f"   处置: {decision_approval.disposition}")
    print(f"   需要人工操作: {decision_approval.requires_human_action}")
    print(f"   立即通知: {decision_approval.notify_now}")
    print(f"   原因: {decision_approval.summary}")

    pause()

    print("\n2. 创建自动解决的决策...")

    decision_auto = AttentionDecision(
        target_principal_id=uuid4(),
        disposition=AttentionDisposition.AUTO_RESOLVABLE,
        reason_code="low_risk_reminder",
        summary="Low-risk follow-up reminder, auto-executed.",
        requires_human_action=False,
        notify_now=False,
    )

    print_success("自动决策创建成功！")
    print(f"   处置: {decision_auto.disposition}")
    print(f"   需要人工操作: {decision_auto.requires_human_action}")
    print(f"   立即通知: {decision_auto.notify_now}")

    pause()

    return decision_approval


def test_5_action_envelope(stack, preview, decision):
    """测试 5: 动作信封 (ActionEnvelope)"""
    print_section("测试 5: 动作信封 (ActionEnvelope)")

    print_info("动作信封是完整的执行包，包含执行动作所需的所有上下文。")
    pause()

    print("\n1. 创建完整的动作信封...")

    thread_id = uuid4()

    envelope = ActionEnvelope(
        action_type="send_message",
        action_label="Send candidate scheduling proposal",
        thread=ThreadContextRef(
            thread_id=thread_id,
            objective="Coordinate final-round interview times",
            thread_status="awaiting_approval",
            participant_ids=[stack.owner.principal_id],
        ),
        sender_stack=stack,
        disclosure_preview=preview,
        target=ActionTarget(
            channel=ChannelKind.EMAIL,
            recipient_handles=["candidate@example.com"],
            subject="Interview scheduling options",
        ),
        risk_posture=RiskPosture(
            risk_level=RiskLevel.MEDIUM,
            requires_approval=True,
            reason_codes=["external_send", "candidate_thread"],
            summary="External candidate communication requires human approval.",
        ),
        execution_mode=ActionExecutionMode.EXECUTE_AFTER_APPROVAL,
        approval_request_id=decision.decision_id,
        payload={
            "content": "Here are three scheduling windows that work on our side!",
            "content_type": "text/plain",
        },
    )

    print_success("动作信封创建成功！")
    print(f"   信封 ID: {envelope.envelope_id}")
    print(f"   动作类型: {envelope.action_type}")
    print(f"   线程目标: {envelope.thread.objective}")
    print(f"   执行模式: {envelope.execution_mode}")
    print(f"   风险等级: {envelope.risk_posture.risk_level}")
    print(f"   需要审批: {envelope.risk_posture.requires_approval}")
    print(f"   目标渠道: {envelope.target.channel}")
    print(f"   收件人: {envelope.target.recipient_handles}")

    pause()

    # 测试序列化
    print("\n2. 测试序列化/反序列化...")

    envelope_json = envelope.model_dump(mode="json")
    print_success("序列化为 JSON 成功")

    envelope_restored = ActionEnvelope.model_validate(envelope_json)
    print_success("从 JSON 反序列化成功")

    assert envelope_restored.envelope_id == envelope.envelope_id
    print_success("往返验证通过！")

    return envelope


def test_6_complete_flow():
    """测试 6: 完整的端到端流程"""
    print_section("测试 6: 完整的端到端流程 - 面试安排场景")

    print_info("这个场景模拟了完整的面试安排流程。")
    pause()

    print("\n" + "=" * 60)
    print("场景: 面试安排")
    print("=" * 60)

    # 步骤 1
    print("\n📍 步骤 1: 创建参与者和权限授予")

    alicia = ActorRef(
        principal_id=uuid4(),
        principal_kind=PrincipalKind.HUMAN,
        display_name="Alicia Chen (招聘经理)",
        affiliation_name="Company",
    )

    assistant = ActorRef(
        principal_id=uuid4(),
        principal_kind=PrincipalKind.PERSONAL_AGENT,
        display_name="Alicia's Assistant",
        affiliation_name="Company",
        is_human_controlled=False,
    )

    scheduler = ActorRef(
        principal_id=uuid4(),
        principal_kind=PrincipalKind.SERVICE_AGENT,
        display_name="Scheduling Agent",
        is_human_controlled=False,
    )

    disclosure_policy = DisclosurePolicy(default_mode=DisclosureMode.SEMI)

    grant = AuthorityGrant(
        authority_grant_id=uuid4(),
        grantor=alicia,
        delegate=assistant,
        status=AuthorityGrantStatus.ACTIVE,
        delegation_mode=DelegationMode.APPROVE_TO_SEND,
        allowed_actions=["draft_message", "send_message", "propose_time"],
        requires_approval_for=["send_message"],
        disclosure_policy=disclosure_policy,
        granted_at=datetime.now(UTC),
    )
    print_success(f"权限授予已创建: {grant.authority_grant_id}")

    # 步骤 2
    print("\n📍 步骤 2: 构建发送者堆栈")
    stack = SenderStack(
        owner=alicia,
        delegate=assistant,
        author=scheduler,
        disclosure_mode=DisclosureMode.FULL,
        authority_source=grant.authority_grant_id,
        authority_label="candidate_scheduling_policy_v1",
    )
    print_success("发送者堆栈已构建")

    # 步骤 3
    print("\n📍 步骤 3: 解析披露策略")
    policy = DisclosurePolicy(default_mode=DisclosureMode.SEMI)
    preview = DisclosurePreview.from_policy(
        policy,
        is_external=True,
        is_sensitive_relationship=False,
        risk_level=RiskLevel.MEDIUM,
        rendered_text="Sent on behalf of Alicia with delegated scheduling assistance.",
    )
    print_success(f"披露模式: {preview.resolved_mode}")

    # 步骤 4
    print("\n📍 步骤 4: 生成注意力决策")
    decision = AttentionDecision(
        target_principal_id=alicia.principal_id,
        disposition=AttentionDisposition.APPROVAL_REQUIRED,
        reason_code="approval_gate",
        summary="This interview scheduling message requires human approval before send.",
        requires_human_action=True,
        notify_now=True,
    )
    print_success(f"决策: {decision.disposition}")

    # 步骤 5
    print("\n📍 步骤 5: 构建动作信封")
    thread_id = uuid4()
    envelope = ActionEnvelope(
        action_type="send_message",
        action_label="Send candidate scheduling proposal",
        thread=ThreadContextRef(
            thread_id=thread_id,
            objective="Coordinate final-round interview times",
            thread_status="awaiting_approval",
            participant_ids=[alicia.principal_id],
        ),
        sender_stack=stack,
        disclosure_preview=preview,
        target=ActionTarget(
            channel=ChannelKind.EMAIL,
            recipient_handles=["bob@example.com"],
            subject="Interview scheduling options",
        ),
        risk_posture=RiskPosture(
            risk_level=RiskLevel.MEDIUM,
            requires_approval=True,
            reason_codes=["external_send", "candidate_thread"],
            summary="External candidate communication requires human approval.",
        ),
        execution_mode=ActionExecutionMode.EXECUTE_AFTER_APPROVAL,
        approval_request_id=decision.decision_id,
        payload={
            "content": "Here are three scheduling windows...",
            "content_type": "text/plain",
        },
    )
    print_success(f"动作信封已构建: {envelope.envelope_id}")

    # 总结
    print("\n" + "=" * 60)
    print_success("完整端到端流程测试成功！")
    print("=" * 60)
    print("\n流程回顾:")
    print("  1. ✅ 创建权限授予")
    print("  2. ✅ 构建发送者堆栈")
    print("  3. ✅ 解析披露策略")
    print("  4. ✅ 生成注意力决策")
    print("  5. ✅ 构建动作信封")
    print("\n所有合同正常工作！")


def main():
    """主函数"""
    print(f"\n{Colors.BOLD}{'=' * 60}{Colors.ENDC}")
    print(f"{Colors.BOLD}  Communication OS v1 - 交互式测试体验{Colors.ENDC}")
    print(f"{Colors.BOLD}{'=' * 60}{Colors.ENDC}")

    print_info("\n这个脚本将带你体验 Communication OS 的核心合同功能。")
    print("你将看到：")
    print("  1. AuthorityGrant - 权限授予")
    print("  2. SenderStack - 发送者堆栈")
    print("  3. DisclosurePolicy - 披露策略")
    print("  4. AttentionDecision - 注意力决策")
    print("  5. ActionEnvelope - 动作信封")
    print("  6. 完整的端到端流程")

    pause()

    try:
        # 运行测试
        grant = test_1_authority_grant()
        stack = test_2_sender_stack(grant)
        policy, preview = test_3_disclosure()
        decision = test_4_attention_decision()
        envelope = test_5_action_envelope(stack, preview, decision)
        test_6_complete_flow()

        print(f"\n{Colors.GREEN}{'=' * 60}{Colors.ENDC}")
        print(f"{Colors.GREEN}  🎉 所有交互式测试完成！{Colors.ENDC}")
        print(f"{Colors.GREEN}{'=' * 60}{Colors.ENDC}")

        print("\n📖 下一步:")
        print("  - 运行完整测试套件: ./run_all_tests.sh --quick")
        print("  - 阅读测试文档: docs/testing/TEST_DOCUMENTATION.md")
        print("  - 阅读测试手册: docs/testing/TEST_MANUAL.md")
        print("  - 查看验收报告: docs/engineering/PHASE3_ACCEPTANCE.md")

    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}测试被中断。{Colors.ENDC}")
    except Exception as e:
        print(f"\n\n{Colors.RED}错误: {e}{Colors.ENDC}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

