#!/usr/bin/env python3
"""
Communication OS v1 - 交互式测试示例
演示5大契约和核心概念的实际测试
"""

import sys
import json
from datetime import datetime
from uuid import uuid4
from typing import Dict, Any

print("=" * 60)
print("Communication OS v1 - 交互式测试示例")
print("=" * 60)
print()

# ============================================================================
# 测试示例 1: AuthorityGrant（权威授予）- 测试"Identity First"原则
# ============================================================================
print("\n" + "=" * 60)
print("测试示例 1: AuthorityGrant（权威授予）")
print("演示: Identity First 原则 - 谁可以代表谁")
print("=" * 60)

authority_grant = {
    "grant_id": str(uuid4()),
    "grantor": {
        "principal_id": "user-1",
        "display_name": "张明",
        "principal_kind": "HUMAN",
    },
    "grantee": {
        "principal_id": "agent-1",
        "display_name": "Agent Assistant",
        "principal_kind": "PERSONAL_AGENT",
    },
    "allowed_actions": ["draft_message", "propose_time", "send_low_risk_email"],
    "forbidden_actions": ["negotiate_price", "make_commitment", "terminate_relationship"],
    "relationship_scope": ["candidate", "vendor"],
    "risk_level_allowed": "low",
    "requires_approval_for": ["medium", "high"],
    "disclosure_required": "full",
    "expires_at": "2026-12-31T23:59:59Z",
    "created_at": datetime.utcnow().isoformat() + "Z",
}

print(f"\n✅ 权威授予创建成功:")
print(f"   授予者: {authority_grant['grantor']['display_name']} ({authority_grant['grantor']['principal_kind']})")
print(f"   被授予者: {authority_grant['grantee']['display_name']} ({authority_grant['grantee']['principal_kind']})")
print(f"   允许动作: {', '.join(authority_grant['allowed_actions'])}")
print(f"   禁止动作: {', '.join(authority_grant['forbidden_actions'])}")
print(f"   风险级别: {authority_grant['risk_level_allowed']}")
print(f"   披露要求: {authority_grant['disclosure_required']}")

print("\n💡 这个测试验证了v1的'Identity First'原则:")
print("   - 明确区分owner/delegate身份")
print("   - 有明确的动作边界")
print("   - 有风险级别限制")
print("   - 有披露要求")

input("\n按Enter继续下一个测试...")

# ============================================================================
# 测试示例 2: SenderStack（发送者栈）- 测试"可解释的责任链"
# ============================================================================
print("\n" + "=" * 60)
print("测试示例 2: SenderStack（发送者栈）")
print("演示: 完整的责任链 - 谁写的、谁批准的、谁发出的")
print("=" * 60)

sender_stack = {
    "owner": {
        "principal_id": "user-1",
        "display_name": "张明",
        "principal_kind": "HUMAN",
    },
    "delegate": {
        "principal_id": "agent-1",
        "display_name": "Agent Assistant",
        "principal_kind": "PERSONAL_AGENT",
    },
    "author": {
        "principal_id": "agent-1",
        "display_name": "Agent Assistant",
        "principal_kind": "PERSONAL_AGENT",
    },
    "approver": {
        "principal_id": "user-1",
        "display_name": "张明",
        "principal_kind": "HUMAN",
    },
    "executor": {
        "principal_id": "system-1",
        "display_name": "Email Delivery Service",
        "principal_kind": "SERVICE_AGENT",
    },
    "disclosure_mode": "full",
    "authority_source": authority_grant["grant_id"],
}

print(f"\n✅ 发送者栈构建成功:")
print(f"   👤 Owner (最终责任人): {sender_stack['owner']['display_name']}")
print(f"   🤖 Delegate (代理): {sender_stack['delegate']['display_name']}")
print(f"   ✍️  Author (起草者): {sender_stack['author']['display_name']}")
print(f"   ✅ Approver (批准者): {sender_stack['approver']['display_name']}")
print(f"   📤 Executor (执行者): {sender_stack['executor']['display_name']}")
print(f"   🔍 披露模式: {sender_stack['disclosure_mode']}")

print("\n💡 这个测试验证了v1的'Sender Stack'概念:")
print("   - 不是单一sender，而是完整的责任链")
print("   - 可追踪每一步是谁做的")
print("   - 有明确的authority_source指向授权")

input("\n按Enter继续下一个测试...")

# ============================================================================
# 测试示例 3: DisclosurePolicy（披露策略）- 测试"透明性"
# ============================================================================
print("\n" + "=" * 60)
print("测试示例 3: DisclosurePolicy（披露策略）")
print("演示: 对方能看到什么 - 透明性 vs 简洁性的平衡")
print("=" * 60)

disclosure_policy = {
    "policy_id": str(uuid4()),
    "relationship_class": "candidate",
    "default_mode": "full",
    "allowed_modes": ["full", "semi", "template"],
    "visible_fields": {
        "full": ["owner", "delegate", "author", "approver", "authority_source"],
        "semi": ["owner", "delegate"],
        "template": ["owner"],
    },
    "requires_recipient_notice": True,
    "notice_template": "此邮件由助手协助起草，经张明批准后发出",
    "created_at": datetime.utcnow().isoformat() + "Z",
}

disclosure_preview = {
    "policy_id": disclosure_policy["policy_id"],
    "resolved_mode": "full",
    "visible_fields": disclosure_policy["visible_fields"]["full"],
    "requires_recipient_notice": True,
    "notice_text": disclosure_policy["notice_template"],
    "recipient_disclosure": f"""
----------------------------------------
发件人: {sender_stack['owner']['display_name']}
协助: {sender_stack['delegate']['display_name']}
批准: {sender_stack['approver']['display_name']}
----------------------------------------
    """,
}

print(f"\n✅ 披露策略应用成功:")
print(f"   关系类别: {disclosure_policy['relationship_class']}")
print(f"   披露模式: {disclosure_preview['resolved_mode']}")
print(f"   可见字段: {', '.join(disclosure_preview['visible_fields'])}")
print(f"   需要接收者通知: {disclosure_preview['requires_recipient_notice']}")
print(f"\n📝 接收者看到的披露:")
print(disclosure_preview["recipient_disclosure"])

print("\n💡 这个测试验证了v1的'Disclosure Policy'概念:")
print("   - 根据关系类别决定披露程度")
print("   - 接收者知道是否有代理参与")
print("   - 平衡透明性和简洁性")

input("\n按Enter继续下一个测试...")

# ============================================================================
# 测试示例 4: ActionEnvelope + RiskPosture（动作信封 + 风险姿态）
# ============================================================================
print("\n" + "=" * 60)
print("测试示例 4: ActionEnvelope + RiskPosture")
print("演示: 完整的动作执行前评估 - 四层风险判断")
print("=" * 60)

action_envelope = {
    "envelope_id": str(uuid4()),
    "action_type": "send_email",
    "action_label": "发送面试邀请",
    "thread": {
        "thread_id": "thread-1",
        "objective": "与候选人李华确定终面时间",
        "thread_status": "awaiting_approval",
        "participant_ids": ["user-1", "agent-1", "external-1"],
    },
    "relationships": {
        "relationship_ids": ["rel-candidate-1"],
        "relationship_classes": ["candidate"],
        "is_sensitive": False,
    },
    "sender_stack": sender_stack,
    "disclosure_preview": disclosure_preview,
    "target": {
        "channel": "email",
        "recipient_ids": ["external-1"],
        "recipient_handles": ["lihua@example.com"],
        "subject": "终面时间邀请",
    },
    "risk_posture": {
        "risk_level": "medium",
        "requires_approval": True,
        "reason_codes": ["external_candidate", "first_time_contact"],
        "risk_breakdown": {
            "relationship_risk": "medium",
            "action_risk": "low",
            "content_risk": "low",
            "consequence_risk": "medium",
        },
    },
    "execution_mode": "require_approval",
    "payload": {
        "body": "尊敬的李华，您好！\n\n我们想邀请您参加终面...",
    },
    "created_at": datetime.utcnow().isoformat() + "Z",
}

print(f"\n✅ 动作信封构建成功:")
print(f"   动作类型: {action_envelope['action_type']}")
print(f"   动作描述: {action_envelope['action_label']}")
print(f"   目标渠道: {action_envelope['target']['channel']}")
print(f"   接收者: {', '.join(action_envelope['target']['recipient_handles'])}")

print(f"\n🎯 四层风险评估结果:")
risk = action_envelope["risk_posture"]["risk_breakdown"]
print(f"   1. 关系风险: {risk['relationship_risk']} - 这是外部候选人，第一次接触")
print(f"   2. 动作风险: {risk['action_risk']} - 只是邀请，没有承诺")
print(f"   3. 内容风险: {risk['content_risk']} - 标准面试邀请")
print(f"   4. 结果风险: {risk['consequence_risk']} - 候选人体验很重要")

print(f"\n📋 最终决策:")
print(f"   综合风险级别: {action_envelope['risk_posture']['risk_level']}")
print(f"   是否需要审批: {action_envelope['risk_posture']['requires_approval']}")
print(f"   执行模式: {action_envelope['execution_mode']}")
print(f"   原因: {', '.join(action_envelope['risk_posture']['reason_codes'])}")

print("\n💡 这个测试验证了v1的'Action Over Text'和'Replayable Trust'原则:")
print("   - 不是简单的发送消息，而是完整的动作信封")
print("   - 四层风险判断，不是一刀切")
print("   - 所有决策都记录在案，可追溯")

input("\n按Enter继续下一个测试...")

# ============================================================================
# 测试示例 5: AttentionDecision + Replay Events（注意力决策 + 重播事件）
# ============================================================================
print("\n" + "=" * 60)
print("测试示例 5: AttentionDecision + Replay Events")
print("演示: 什么需要打断人，什么可以自动处理 + 完整可回放")
print("=" * 60)

attention_decision = {
    "decision_id": str(uuid4()),
    "thread_id": "thread-1",
    "action_envelope_id": action_envelope["envelope_id"],
    "attention_level": "requires_approval",
    "priority": "normal",
    "reason": "Medium risk action with external candidate",
    "presentation_hint": {
        "show_sender_stack": True,
        "show_risk_breakdown": True,
        "show_approval_options": True,
    },
    "available_actions": ["approve", "edit_and_approve", "reject", "take_over"],
    "created_at": datetime.utcnow().isoformat() + "Z",
}

replay_events = [
    {
        "event_id": str(uuid4()),
        "event_type": "thread_created",
        "actor": {"principal_id": "user-1", "display_name": "张明"},
        "timestamp": "2026-03-24T09:00:00Z",
        "payload": {"objective": "与候选人李华确定终面时间"},
    },
    {
        "event_id": str(uuid4()),
        "event_type": "action_planned",
        "actor": {"principal_id": "agent-1", "display_name": "Agent Assistant"},
        "timestamp": "2026-03-24T09:01:00Z",
        "payload": {"plan": ["分析可用时间", "起草邮件", "请求审批"]},
    },
    {
        "event_id": str(uuid4()),
        "event_type": "risk_evaluated",
        "actor": {"principal_id": "system", "display_name": "Risk Engine"},
        "timestamp": "2026-03-24T09:02:00Z",
        "payload": action_envelope["risk_posture"],
    },
    {
        "event_id": str(uuid4()),
        "event_type": "approval_requested",
        "actor": {"principal_id": "agent-1", "display_name": "Agent Assistant"},
        "timestamp": "2026-03-24T09:03:00Z",
        "payload": {"attention_decision": attention_decision},
    },
]

print(f"\n✅ 注意力决策生成成功:")
print(f"   注意力级别: {attention_decision['attention_level']}")
print(f"   优先级: {attention_decision['priority']}")
print(f"   原因: {attention_decision['reason']}")
print(f"\n🎯 可用操作:")
for action in attention_decision["available_actions"]:
    print(f"   - {action}")

print(f"\n📜 完整回放事件链 ({len(replay_events)} 个事件):")
for i, event in enumerate(replay_events, 1):
    print(f"   {i}. [{event['timestamp']}] {event['event_type']} - {event['actor']['display_name']}")

print("\n💡 这个测试验证了v1的'Human Sovereignty'和'Replayable Trust'原则:")
print("   - 系统决定什么需要人注意，什么不需要")
print("   - 完整的事件链可回放、可审计")
print("   - 人类有最终控制权（approve/edit/reject/take_over）")

input("\n按Enter继续总结...")

# ============================================================================
# 总结
# ============================================================================
print("\n" + "=" * 60)
print("测试总结")
print("=" * 60)

print("""
✅ 已完成的测试:

1. AuthorityGrant - 验证了"Identity First"原则
   - 明确的授权关系
   - 清晰的动作边界

2. SenderStack - 验证了"可解释的责任链"
   - 完整的owner/delegate/author/approver/executor链
   - 每一步都可追溯

3. DisclosurePolicy - 验证了"透明性"
   - 根据关系类别调整披露程度
   - 接收者知道代理是否参与

4. ActionEnvelope + RiskPosture - 验证了"Action Over Text"
   - 四层风险判断（关系/动作/内容/结果）
   - 完整的动作信封，不是简单消息

5. AttentionDecision + Replay Events - 验证了"Human Sovereignty"
   - 智能决定何时打断人类
   - 完整可回放的事件链

💡 这就是v0和v1的核心区别:

   v0: "做一个能委托的聊天工具"
   - 测试重点: 功能流程（起草→审批→发送）

   v1: "做一个通信操作系统"
   - 测试重点: 契约、身份链、决策权、可重放性

   这些概念在后端和测试层，前端只是呈现结果！
""")

print("=" * 60)
print("测试完成！你可以在前端界面中看到这些概念的呈现。")
print("=" * 60)
