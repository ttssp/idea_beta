#!/usr/bin/env python3
"""
Communication OS v1 - 测试演示
演示5大契约和核心概念
"""

import json
from datetime import datetime, UTC
from uuid import uuid4

print("=" * 70)
print("Communication OS v1 - 测试演示")
print("=" * 70)

# ============================================================================
# 测试 1: AuthorityGrant（权威授予）
# ============================================================================
print("\n" + "=" * 70)
print("测试 1: AuthorityGrant（权威授予）")
print("演示: Identity First 原则 - 谁可以代表谁")
print("=" * 70)

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
    "created_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
}

print(f"""
✅ 权威授予创建成功:

   👤 授予者: {authority_grant['grantor']['display_name']} ({authority_grant['grantor']['principal_kind']})
   🤖 被授予者: {authority_grant['grantee']['display_name']} ({authority_grant['grantee']['principal_kind']})

   ✅ 允许动作: {', '.join(authority_grant['allowed_actions'])}
   ❌ 禁止动作: {', '.join(authority_grant['forbidden_actions'])}

   🎯 风险级别: {authority_grant['risk_level_allowed']}
   🔍 披露要求: {authority_grant['disclosure_required']}

💡 v0 vs v1 区别:
   v0: 简单的"委托开关"
   v1: 完整的AuthorityGrant契约 - 有明确的边界、风险级别、披露要求
""")

# ============================================================================
# 测试 2: SenderStack（发送者栈）
# ============================================================================
print("\n" + "=" * 70)
print("测试 2: SenderStack（发送者栈）")
print("演示: 完整的责任链 - 谁写的、谁批准的、谁发出的")
print("=" * 70)

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

print(f"""
✅ 发送者栈构建成功:

   👤 Owner (最终责任人): {sender_stack['owner']['display_name']}
   🤖 Delegate (代理): {sender_stack['delegate']['display_name']}
   ✍️  Author (起草者): {sender_stack['author']['display_name']}
   ✅ Approver (批准者): {sender_stack['approver']['display_name']}
   📤 Executor (执行者): {sender_stack['executor']['display_name']}

   🔍 披露模式: {sender_stack['disclosure_mode']}
   🔗 授权来源: {sender_stack['authority_source'][:8]}...

💡 v0 vs v1 区别:
   v0: 单一"sender"字段
   v1: 完整的SenderStack - 可追溯每一步是谁做的
""")

# ============================================================================
# 测试 3: DisclosurePolicy（披露策略）
# ============================================================================
print("\n" + "=" * 70)
print("测试 3: DisclosurePolicy（披露策略）")
print("演示: 对方能看到什么 - 透明性 vs 简洁性的平衡")
print("=" * 70)

disclosure_policy = {
    "policy_id": str(uuid4()),
    "relationship_class": "candidate",
    "default_mode": "full",
    "visible_fields": {
        "full": ["owner", "delegate", "author", "approver", "authority_source"],
        "semi": ["owner", "delegate"],
        "template": ["owner"],
    },
    "requires_recipient_notice": True,
    "notice_template": "此邮件由助手协助起草，经张明批准后发出",
}

disclosure_preview = {
    "policy_id": disclosure_policy["policy_id"],
    "resolved_mode": "full",
    "requires_recipient_notice": True,
    "notice_text": disclosure_policy["notice_template"],
}

print(f"""
✅ 披露策略应用成功:

   👥 关系类别: {disclosure_policy['relationship_class']}
   🔍 披露模式: {disclosure_preview['resolved_mode']}
   📢 需要接收者通知: {disclosure_preview['requires_recipient_notice']}

📝 接收者看到的披露:
   ┌─────────────────────────────────────────────────┐
   │ 发件人: 张明                                    │
   │ 协助: Agent Assistant                           │
   │ 批准: 张明                                      │
   └─────────────────────────────────────────────────┘

💡 v0 vs v1 区别:
   v0: "透明/不透明"二元选择
   v1: 完整的DisclosurePolicy - 根据关系类别调整披露程度
""")

# ============================================================================
# 测试 4: ActionEnvelope + RiskPosture（动作信封 + 风险姿态）
# ============================================================================
print("\n" + "=" * 70)
print("测试 4: ActionEnvelope + RiskPosture")
print("演示: 完整的动作执行前评估 - 四层风险判断")
print("=" * 70)

action_envelope = {
    "envelope_id": str(uuid4()),
    "action_type": "send_email",
    "action_label": "发送面试邀请",
    "thread": {
        "thread_id": "thread-1",
        "objective": "与候选人李华确定终面时间",
        "thread_status": "awaiting_approval",
    },
    "sender_stack": sender_stack,
    "disclosure_preview": disclosure_preview,
    "target": {
        "channel": "email",
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
}

risk = action_envelope["risk_posture"]["risk_breakdown"]
print(f"""
✅ 动作信封构建成功:

   📋 动作类型: {action_envelope['action_type']}
   📝 动作描述: {action_envelope['action_label']}
   📧 目标渠道: {action_envelope['target']['channel']}
   👤 接收者: {', '.join(action_envelope['target']['recipient_handles'])}

🎯 四层风险评估结果:

   1. 关系风险: {risk['relationship_risk']}
      → 原因: 外部候选人，第一次接触

   2. 动作风险: {risk['action_risk']}
      → 原因: 只是邀请，没有承诺

   3. 内容风险: {risk['content_risk']}
      → 原因: 标准面试邀请

   4. 结果风险: {risk['consequence_risk']}
      → 原因: 候选人体验很重要

📋 最终决策:
   综合风险级别: {action_envelope['risk_posture']['risk_level']}
   是否需要审批: {action_envelope['risk_posture']['requires_approval']}
   执行模式: {action_envelope['execution_mode']}
   触发规则: {', '.join(action_envelope['risk_posture']['reason_codes'])}

💡 v0 vs v1 区别:
   v0: 简单的"风险级别"字段
   v1: 四层风险判断 + 完整的ActionEnvelope契约
""")

# ============================================================================
# 测试 5: AttentionDecision + Replay Events（注意力决策 + 重播事件）
# ============================================================================
print("\n" + "=" * 70)
print("测试 5: AttentionDecision + Replay Events")
print("演示: 什么需要打断人，什么可以自动处理 + 完整可回放")
print("=" * 70)

attention_decision = {
    "decision_id": str(uuid4()),
    "thread_id": "thread-1",
    "attention_level": "requires_approval",
    "priority": "normal",
    "reason": "Medium risk action with external candidate",
    "available_actions": ["approve", "edit_and_approve", "reject", "take_over"],
}

replay_events = [
    {
        "event_type": "thread_created",
        "actor": "张明",
        "timestamp": "2026-03-24T09:00:00Z",
        "description": "创建线程，目标: 与候选人李华确定终面时间",
    },
    {
        "event_type": "action_planned",
        "actor": "Agent Assistant",
        "timestamp": "2026-03-24T09:01:00Z",
        "description": "分析目标并制定计划: [分析可用时间, 起草邮件, 请求审批]",
    },
    {
        "event_type": "risk_evaluated",
        "actor": "Risk Engine",
        "timestamp": "2026-03-24T09:02:00Z",
        "description": "四层风险评估结果: medium",
    },
    {
        "event_type": "approval_requested",
        "actor": "Agent Assistant",
        "timestamp": "2026-03-24T09:03:00Z",
        "description": "提交审批请求，等待人类批准",
    },
]

print(f"""
✅ 注意力决策生成成功:

   🎯 注意力级别: {attention_decision['attention_level']}
   ⏰ 优先级: {attention_decision['priority']}
   📝 原因: {attention_decision['reason']}

🎮 可用操作:
   ✅ approve - 批准
   ✏️  edit_and_approve - 编辑并批准
   ❌ reject - 拒绝
   🔀 take_over - 接管

📜 完整回放事件链 ({len(replay_events)} 个事件):
""")

for i, event in enumerate(replay_events, 1):
    print(f"   {i}. [{event['timestamp']}]")
    print(f"      类型: {event['event_type']}")
    print(f"      执行者: {event['actor']}")
    print(f"      描述: {event['description']}")
    if i < len(replay_events):
        print()

print(f"""
💡 v0 vs v1 区别:
   v0: "通知中心"思路 - 什么都通知人
   v1: "注意力防火墙"思路 - 智能决定什么需要打断人

   v0: "消息历史"思路 - 按时间排序的消息
   v1: "回放中心"思路 - 可审计的决策链
""")

# ============================================================================
# 总结
# ============================================================================
print("\n" + "=" * 70)
print("总结: v0 vs v1 的核心区别")
print("=" * 70)

print("""
┌─────────────────────┬─────────────────────────────────────────────────┐
│     维度            │                    核心区别                      │
├─────────────────────┼─────────────────────────────────────────────────┤
│  产品定位           │  v0: 控制层/插件                                │
│                     │  v1: 完整的通信操作系统                         │
├─────────────────────┼─────────────────────────────────────────────────┤
│  测试重点           │  v0: 测试功能流程（起草→审批→发送）            │
│                     │  v1: 测试契约（Contracts）+ 状态机 + 可重放性   │
├─────────────────────┼─────────────────────────────────────────────────┤
│  核心概念           │  v0: Delegation Profile（5个档位）              │
│                     │  v1: 5大契约 + 9大实体 + 8大原则               │
├─────────────────────┼─────────────────────────────────────────────────┤
│  身份模型           │  v0: 单一sender字段                            │
│                     │  v1: SenderStack（owner/delegate/author/...） │
├─────────────────────┼─────────────────────────────────────────────────┤
│  风险判断           │  v0: 简单的风险级别字段                         │
│                     │  v1: 四层风险判断（关系/动作/内容/结果）       │
├─────────────────────┼─────────────────────────────────────────────────┤
│  前端感觉           │  v0: "更聪明的聊天工具"                        │
│                     │  v1: "可委托、可审计、可接管的工作区"          │
└─────────────────────┴─────────────────────────────────────────────────┘

📁 相关文件:
   - test_demo.py (本文件) - 后端契约测试演示
   - FRONTEND_TEST_GUIDE.md - 前端测试指南
   - docs/engineering/PRD_VERSION_COMPARISON.md - 完整版本对比

🎯 下一步:
   1. 运行前端: cd src && npm run dev
   2. 打开 http://localhost:3000
   3. 按照 FRONTEND_TEST_GUIDE.md 进行前端测试
""")

print("=" * 70)
print("测试演示完成！")
print("=" * 70)
