# Communication OS v1 - 测试手册

**版本**: 1.0
**日期**: 2026-03-28
**状态**: ✅ 就绪

---

## 目录

1. [快速开始](#1-快速开始)
2. [测试环境设置](#2-测试环境设置)
3. [单元测试指南](#3-单元测试指南)
4. [集成测试指南](#4-集成测试指南)
5. [端到端测试指南](#5-端到端测试指南)
6. [手动测试场景](#6-手动测试场景)
7. [故障排查](#7-故障排查)

---

## 1. 快速开始

### 1.1 30 秒快速测试

想要快速验证系统是否正常？运行这两个命令：

```bash
# 1. 运行核心测试
cd /Users/admin/codes/idea_beta/myproj
python -m pytest tests/ -v

# 2. 运行 E3 测试
cd /Users/admin/codes/idea_beta/myproj/backend/e3
python -m pytest tests/ -v
```

预期结果：**211 个测试全部通过** ✅

---

## 2. 测试环境设置

### 2.1 系统要求

- **Python**: 3.11 或更高版本
- **Node.js**: 18 或更高版本（仅前端测试需要）
- **操作系统**: macOS / Linux / Windows
- **内存**: 至少 2GB 可用内存

### 2.2 环境设置步骤

#### 步骤 1: 克隆代码库

```bash
cd /Users/admin/codes/idea_beta/myproj
git status  # 应该在 main 分支上
```

#### 步骤 2: 设置 Python 虚拟环境

```bash
# 创建虚拟环境（如果还没有）
python -m venv venv

# 激活虚拟环境
# macOS/Linux:
source venv/bin/activate
# Windows:
# .\venv\Scripts\activate
```

#### 步骤 3: 安装 Python 依赖

```bash
# 安装核心依赖
pip install -e .
pip install pytest pytest-asyncio fastapi uvicorn pydantic sqlalchemy pybreaker

# 安装 E3 依赖
cd backend/e3
pip install -e .
```

#### 步骤 4: 验证安装

```bash
# 验证 Python 版本
python --version  # 应该是 3.11+

# 验证 pytest 安装
pytest --version

# 验证可以导入核心模块
python -c "import myproj.core.contracts; print('✅ 核心合同模块导入成功')"
python -c "import e3.action_runtime; print('✅ E3 模块导入成功')"
```

### 2.3 目录结构确认

确保你的目录结构如下：

```
myproj/
├── src/
│   └── myproj/
│       └── core/
│           ├── contracts/
│           ├── governance/
│           ├── approvals/
│           ├── risk/
│           └── repositories/
├── backend/
│   └── e3/
│       ├── action_runtime/
│       ├── channel_adapters/
│       ├── outbox_inbox/
│       ├── external_resolver/
│       ├── api/
│       └── tests/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
└── docs/
    └── testing/
        ├── TEST_DOCUMENTATION.md
        └── TEST_MANUAL.md (本文件)
```

---

## 3. 单元测试指南

### 3.1 运行所有单元测试

```bash
# 进入项目根目录
cd /Users/admin/codes/idea_beta/myproj

# 运行所有核心单元测试
python -m pytest tests/unit/ -v

# 运行所有 E3 单元测试
cd backend/e3
python -m pytest tests/unit/ -v
```

### 3.2 运行特定测试套件

#### 3.2.1 合同测试

```bash
# 运行所有合同测试
python -m pytest tests/unit/contracts/ -v

# 运行特定合同测试
python -m pytest tests/unit/contracts/test_authority.py -v
python -m pytest tests/unit/contracts/test_sender_stack.py -v
python -m pytest tests/unit/contracts/test_disclosure.py -v
python -m pytest tests/unit/contracts/test_attention.py -v
python -m pytest tests/unit/contracts/test_actions.py -v
```

**预期结果**: 约 15-20 个测试全部通过

#### 3.2.2 治理层测试

```bash
# 运行治理着陆区测试
python -m pytest tests/unit/governance/test_landing_zones.py -v
```

**预期结果**: 11 个测试全部通过

#### 3.2.3 仓储层测试

```bash
# 运行仓储测试
python -m pytest tests/unit/repositories/test_repositories.py -v
```

**预期结果**: 13 个测试全部通过

#### 3.2.4 E3 单元测试

```bash
cd backend/e3

# Action State Machine 测试
python -m pytest tests/unit/test_action_state_machine.py -v

# ActionEnvelope 测试
python -m pytest tests/unit/test_action_envelope.py -v

# Idempotency 测试
python -m pytest tests/unit/test_idempotency.py -v
```

**预期结果**: 30 个测试全部通过（9 + 15 + 6）

### 3.3 生成测试覆盖率报告

```bash
# 安装 coverage.py
pip install coverage pytest-cov

# 运行测试并生成覆盖率报告
python -m pytest tests/ --cov=src/myproj --cov-report=html

# 打开覆盖率报告
open htmlcov/index.html
```

---

## 4. 集成测试指南

### 4.1 运行核心集成测试

```bash
cd /Users/admin/codes/idea_beta/myproj

# 运行合同流程集成测试
python -m pytest tests/integration/test_contract_flow.py -v
```

**测试场景**:
1. 权限授予创建
2. 发送者堆栈构建
3. 披露预览解析
4. 注意力决策生成
5. 动作信封构建
6. 往返序列化
7. 面试安排完整场景

**预期结果**: 7 个测试全部通过

### 4.2 运行 E3 集成测试

```bash
cd /Users/admin/codes/idea_beta/myproj/backend/e3

# Gmail 适配器集成测试
python -m pytest tests/integration/test_email_adapter.py -v

# Calendar 适配器集成测试
python -m pytest tests/integration/test_calendar_adapter.py -v
```

**预期结果**: 15 个测试全部通过（7 + 8）

### 4.3 运行所有集成测试

```bash
# 核心集成测试
cd /Users/admin/codes/idea_beta/myproj
python -m pytest tests/integration/ -v

# E3 集成测试
cd backend/e3
python -m pytest tests/integration/ -v
```

---

## 5. 端到端测试指南

### 5.1 完整 E2E 测试流程

#### 场景 1: 面试安排（Interview Scheduling）

**目标**: 验证完整的面试安排端到端流程

**测试步骤**:

```bash
# 运行集成测试中的面试安排场景
cd /Users/admin/codes/idea_beta/myproj
python -m pytest tests/integration/test_contract_flow.py::TestEndToEndContractFlow::test_complete_interview_scheduling_scenario -v -s
```

**手动验证步骤**:

1. **步骤 1: 创建权限授予**
   - 授予调度代理代表用户安排面试的权限
   - 设置允许的动作: `draft_message`, `send_message`, `propose_time`
   - 设置需要审批的动作: `send_message`

2. **步骤 2: 构建发送者堆栈**
   - Owner: 招聘经理（人类）
   - Delegate: 调度代理（AI 代理）
   - Author: 调度代理
   - Authority Source: 指向步骤 1 中的权限授予

3. **步骤 3: 解析披露策略**
   - 关系类型: candidate（候选人）
   - 披露模式: SEMI（半透明）
   - 接收者通知: 必需

4. **步骤 4: 生成注意力决策**
   - 决策: APPROVAL_REQUIRED（需要审批）
   - 原因: approval_gate
   - 通知: 立即通知人类

5. **步骤 5: 构建动作信封**
   - 动作类型: send_message
   - 执行模式: EXECUTE_AFTER_APPROVAL
   - 风险等级: MEDIUM
   - 目标渠道: EMAIL
   - 收件人: candidate@example.com

6. **步骤 6: 执行并跟踪**
   - 人类审批通过
   - 动作通过 E3 执行
   - Gmail 适配器发送邮件
   - 跟踪投递状态
   - 记录所有事件

7. **步骤 7: 重播验证**
   - 在重播时间线中查看完整流程
   - 验证责任链可见
   - 验证所有事件正确记录

---

#### 场景 2: 客户跟进（Customer Follow-up）

**目标**: 验证低风险自动执行流程

**测试步骤**:

1. **创建客户跟进线程**
   - 目标: 跟进客户需求
   - 关系类型: customer

2. **设置权限和策略**
   - 低风险动作允许自动执行
   - 披露模式: FULL

3. **代理草拟消息**
   - 代理自动草拟跟进消息
   - 风险评估: LOW

4. **自动执行**
   - 无需人工审批
   - 自动发送
   - 跟踪投递确认

5. **验证重播**
   - 重播显示完整流程
   - 显示自动执行原因

---

#### 场景 3: 审批门控外部通信

**目标**: 验证需要审批的高风险外部通信

**测试步骤**:

1. **创建外部通信线程**
2. **设置高风险披露策略**
3. **代理草拟外部消息**
4. **注意力决策请求审批**
5. **审批预览显示发送者堆栈**
6. **人工批准**
7. **执行并发送**
8. **重播显示完整责任链**

---

## 6. 手动测试场景

### 6.1 场景 A: 合同验证

#### A.1 AuthorityGrant 验证

**目标**: 手动验证 AuthorityGrant 合同

**测试代码**:

```python
from myproj.core.contracts import (
    AuthorityGrant,
    AuthorityGrantStatus,
    DelegationMode,
    ActorRef,
    PrincipalKind,
)
from datetime import datetime, UTC
import uuid

# 创建 ActorRefs
grantor = ActorRef(
    principal_id=uuid.uuid4(),
    principal_kind=PrincipalKind.HUMAN,
    display_name="Alicia Chen",
    email="alicia@company.com",
)

delegate = ActorRef(
    principal_id=uuid.uuid4(),
    principal_kind=PrincipalKind.PERSONAL_AGENT,
    display_name="Alicia's Assistant",
    is_agent=True,
)

# 创建 AuthorityGrant
grant = AuthorityGrant(
    authority_grant_id=uuid.uuid4(),
    grantor=grantor,
    delegate=delegate,
    status=AuthorityGrantStatus.ACTIVE,
    delegation_mode=DelegationMode.APPROVE_TO_SEND,
    allowed_actions=["draft_message", "send_message"],
    requires_approval_for=["send_message"],
    granted_at=datetime.now(UTC),
)

print("✅ AuthorityGrant 创建成功!")
print(f"   Grant ID: {grant.authority_grant_id}")
print(f"   Grantor: {grant.grantor.display_name}")
print(f"   Delegate: {grant.delegate.display_name}")
print(f"   Status: {grant.status}")
print(f"   Is active: {grant.is_currently_active}")

# 测试序列化
grant_json = grant.model_dump(mode="json")
print("\n✅ 序列化成功!")

# 测试反序列化
grant_restored = AuthorityGrant.model_validate(grant_json)
print("✅ 反序列化成功!")
assert grant_restored.authority_grant_id == grant.authority_grant_id
print("✅ 往返验证通过!")
```

**运行方式**:
```bash
cd /Users/admin/codes/idea_beta/myproj
python  # 进入 Python REPL，然后粘贴上面的代码
```

---

#### A.2 SenderStack 验证

**测试代码**:

```python
from myproj.core.contracts import SenderStack, ActorRef, PrincipalKind
import uuid

# 创建 Actors
owner = ActorRef(
    principal_id=uuid.uuid4(),
    principal_kind=PrincipalKind.HUMAN,
    display_name="Alicia Chen",
)

delegate = ActorRef(
    principal_id=uuid.uuid4(),
    principal_kind=PrincipalKind.PERSONAL_AGENT,
    display_name="Alicia's Assistant",
    is_agent=True,
)

author = ActorRef(
    principal_id=uuid.uuid4(),
    principal_kind=PrincipalKind.PERSONAL_AGENT,
    display_name="Scheduling Agent",
    is_agent=True,
)

# 创建 SenderStack
stack = SenderStack(
    owner=owner,
    delegate=delegate,
    author=author,
    authority_source=uuid.uuid4(),
    authority_label="scheduling_policy_v1",
)

print("✅ SenderStack 创建成功!")
print(f"   Owner: {stack.owner.display_name} ({stack.owner.principal_kind})")
print(f"   Delegate: {stack.delegate.display_name} ({stack.delegate.principal_kind})")
print(f"   Author: {stack.author.display_name} ({stack.author.principal_kind})")
print(f"   Authority Source: {stack.authority_source}")

# 测试序列化
stack_json = stack.model_dump(mode="json")
print("\n✅ 序列化成功!")

# 测试反序列化
stack_restored = SenderStack.model_validate(stack_json)
print("✅ 反序列化成功!")
assert stack_restored.owner.principal_id == stack.owner.principal_id
print("✅ 往返验证通过!")
```

---

### 6.2 场景 B: Action State Machine 测试

**测试代码**:

```python
from e3.action_runtime.state_machine import (
    ActionRunState,
    ActionRunStateMachine,
    ActionRunEvent,
)

# 创建状态机
sm = ActionRunStateMachine()

print("测试 Action State Machine 转换...")
print(f"初始状态: {ActionRunState.CREATED}")

# 测试完整流程
current_state = ActionRunState.CREATED
print(f"\n1. {current_state} -> planned")
current_state = sm.transition(current_state, ActionRunEvent.PLAN)
print(f"   结果: {current_state}")

print(f"\n2. {current_state} -> ready_for_approval")
current_state = sm.transition(current_state, ActionRunEvent.SUBMIT_FOR_APPROVAL)
print(f"   结果: {current_state}")

print(f"\n3. {current_state} -> approved")
current_state = sm.transition(current_state, ActionRunEvent.APPROVE)
print(f"   结果: {current_state}")

print(f"\n4. {current_state} -> executing")
current_state = sm.transition(current_state, ActionRunEvent.START_EXECUTION)
print(f"   结果: {current_state}")

print(f"\n5. {current_state} -> sent")
current_state = sm.transition(current_state, ActionRunEvent.MARK_SENT)
print(f"   结果: {current_state}")

print(f"\n6. {current_state} -> acknowledged")
current_state = sm.transition(current_state, ActionRunEvent.ACKNOWLEDGE)
print(f"   结果: {current_state}")

print("\n✅ 完整状态机流程测试通过!")

# 测试所有有效转换
print("\n测试所有有效转换...")
all_valid = True
for from_state in ActionRunState:
    for event in ActionRunEvent:
        if sm.can_transition(from_state, event):
            to_state = sm.transition(from_state, event)
            print(f"  ✅ {from_state} + {event} -> {to_state}")

print("\n✅ 所有有效转换测试通过!")
```

---

### 6.3 场景 C: 端到端合同流程

**测试代码**:

```python
"""
端到端合同流程测试
模拟: thread -> approval -> execution -> replay
"""

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
)
from datetime import datetime, UTC
import uuid

print("=" * 60)
print("Communication OS - 端到端合同流程测试")
print("=" * 60)

# ===== 步骤 1: 创建参与者 =====
print("\n[步骤 1] 创建参与者...")

alicia = ActorRef(
    principal_id=uuid.uuid4(),
    principal_kind=PrincipalKind.HUMAN,
    display_name="Alicia Chen",
    email="alicia@company.com",
)

assistant = ActorRef(
    principal_id=uuid.uuid4(),
    principal_kind=PrincipalKind.PERSONAL_AGENT,
    display_name="Alicia's Assistant",
    is_agent=True,
)

scheduler = ActorRef(
    principal_id=uuid.uuid4(),
    principal_kind=PrincipalKind.SERVICE_AGENT,
    display_name="Scheduling Agent",
    is_agent=True,
)

candidate = ActorRef(
    principal_id=uuid.uuid4(),
    principal_kind=PrincipalKind.EXTERNAL_PARTICIPANT,
    display_name="Bob Candidate",
    email="bob@example.com",
)

print(f"  ✅ Alicia (招聘经理): {alicia.display_name}")
print(f"  ✅ Assistant (代理): {assistant.display_name}")
print(f"  ✅ Scheduler (调度): {scheduler.display_name}")
print(f"  ✅ Candidate (候选人): {candidate.display_name}")

# ===== 步骤 2: 创建权限授予 =====
print("\n[步骤 2] 创建权限授予...")

grant = AuthorityGrant(
    authority_grant_id=uuid.uuid4(),
    grantor=alicia,
    delegate=assistant,
    status=AuthorityGrantStatus.ACTIVE,
    delegation_mode=DelegationMode.APPROVE_TO_SEND,
    allowed_actions=["draft_message", "send_message", "propose_time"],
    requires_approval_for=["send_message"],
    granted_at=datetime.now(UTC),
)

print(f"  ✅ 权限授予 ID: {grant.authority_grant_id}")
print(f"  ✅ 授权模式: {grant.delegation_mode}")
print(f"  ✅ 允许动作: {grant.allowed_actions}")
print(f"  ✅ 需要审批: {grant.requires_approval_for}")
print(f"  ✅ 状态: {grant.status} (active={grant.is_currently_active})")

# ===== 步骤 3: 构建发送者堆栈 =====
print("\n[步骤 3] 构建发送者堆栈...")

stack = SenderStack(
    owner=alicia,
    delegate=assistant,
    author=scheduler,
    authority_source=grant.authority_grant_id,
    authority_label="candidate_scheduling_policy_v1",
)

print(f"  ✅ Owner: {stack.owner.display_name}")
print(f"  ✅ Delegate: {stack.delegate.display_name}")
print(f"  ✅ Author: {stack.author.display_name}")
print(f"  ✅ Authority Source: {stack.authority_label}")

# ===== 步骤 4: 解析披露策略 =====
print("\n[步骤 4] 解析披露策略...")

policy = DisclosurePolicy(
    policy_id=uuid.uuid4(),
    owner_principal_id=alicia.principal_id,
    default_external_mode="semi",
    default_internal_mode="hidden",
    sensitive_relationship_mode="full",
    requires_notice_for_external=True,
)

preview = DisclosurePreview.from_policy(
    policy,
    is_external=True,
    is_sensitive_relationship=False,
    risk_level=RiskLevel.MEDIUM,
    rendered_text="Sent on behalf of Alicia with delegated scheduling assistance.",
)

print(f"  ✅ 披露模式: {preview.resolved_mode}")
print(f"  ✅ 需要接收者通知: {preview.requires_recipient_notice}")
print(f"  ✅ 披露文本: {preview.rendered_text}")

# ===== 步骤 5: 生成注意力决策 =====
print("\n[步骤 5] 生成注意力决策...")

decision = AttentionDecision(
    decision_id=uuid.uuid4(),
    target_principal_id=alicia.principal_id,
    disposition=AttentionDisposition.APPROVAL_REQUIRED,
    reason_code="approval_gate",
    summary="This interview scheduling message requires human approval before send.",
    requires_human_action=True,
    notify_now=True,
)

print(f"  ✅ 决策 ID: {decision.decision_id}")
print(f"  ✅ 处置: {decision.disposition}")
print(f"  ✅ 需要人工操作: {decision.requires_human_action}")
print(f"  ✅ 立即通知: {decision.notify_now}")
print(f"  ✅ 原因: {decision.summary}")

# ===== 步骤 6: 构建动作信封 =====
print("\n[步骤 6] 构建动作信封...")

thread_id = uuid.uuid4()

envelope = ActionEnvelope(
    envelope_id=uuid.uuid4(),
    action_type="send_message",
    action_label="Send candidate scheduling proposal",
    thread=ThreadContextRef(
        thread_id=thread_id,
        objective="Coordinate final-round interview times",
        thread_status="awaiting_approval",
        participant_ids=[alicia.principal_id, candidate.principal_id],
    ),
    relationships=RelationshipContextRef(
        relationship_classes=["candidate"],
        is_sensitive=False,
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
        "content": "Here are three scheduling windows that work on our side:\n\n1. Tuesday 2-4pm\n2. Wednesday 10-12pm\n3. Friday 1-3pm\n\nPlease let me know what works best for you!",
        "content_type": "text/plain",
    },
)

print(f"  ✅ 信封 ID: {envelope.envelope_id}")
print(f"  ✅ 动作类型: {envelope.action_type}")
print(f"  ✅ 线程目标: {envelope.thread.objective}")
print(f"  ✅ 执行模式: {envelope.execution_mode}")
print(f"  ✅ 风险等级: {envelope.risk_posture.risk_level}")
print(f"  ✅ 需要审批: {envelope.risk_posture.requires_approval}")
print(f"  ✅ 目标渠道: {envelope.target.channel}")
print(f"  ✅ 收件人: {envelope.target.recipient_handles}")

# ===== 步骤 7: 测试往返序列化 =====
print("\n[步骤 7] 测试往返序列化...")

# AuthorityGrant
grant_json = grant.model_dump(mode="json")
grant_restored = AuthorityGrant.model_validate(grant_json)
assert grant_restored.authority_grant_id == grant.authority_grant_id
print("  ✅ AuthorityGrant 往返序列化")

# SenderStack
stack_json = stack.model_dump(mode="json")
stack_restored = SenderStack.model_validate(stack_json)
assert stack_restored.owner.principal_id == stack.owner.principal_id
print("  ✅ SenderStack 往返序列化")

# ActionEnvelope
envelope_json = envelope.model_dump(mode="json")
envelope_restored = ActionEnvelope.model_validate(envelope_json)
assert envelope_restored.envelope_id == envelope.envelope_id
print("  ✅ ActionEnvelope 往返序列化")

# ===== 完成 =====
print("\n" + "=" * 60)
print("✅ 端到端合同流程测试全部通过!")
print("=" * 60)
print("\n总结:")
print("  1. ✅ 参与者创建")
print("  2. ✅ 权限授予")
print("  3. ✅ 发送者堆栈")
print("  4. ✅ 披露策略")
print("  5. ✅ 注意力决策")
print("  6. ✅ 动作信封")
print("  7. ✅ 往返序列化")
print("\n所有合同流程正常工作!")
```

**运行方式**:
```bash
cd /Users/admin/codes/idea_beta/myproj

# 创建测试脚本
cat > test_e2e_flow.py << 'EOF'
# 粘贴上面的代码
EOF

# 或者直接运行
python -c "
# 粘贴上面的代码
"
```

---

## 7. 故障排查

### 7.1 常见问题

#### 问题 1: ImportError: No module named 'myproj'

**症状**:
```
ImportError: No module named 'myproj'
```

**解决方案**:
```bash
# 确保在项目根目录
cd /Users/admin/codes/idea_beta/myproj

# 以可编辑模式安装
pip install -e .

# 验证安装
python -c "import myproj; print('✅ 成功')"
```

---

#### 问题 2: ImportError: No module named 'e3'

**症状**:
```
ImportError: No module named 'e3'
```

**解决方案**:
```bash
cd /Users/admin/codes/idea_beta/myproj/backend/e3
pip install -e .

# 验证安装
python -c "import e3; print('✅ 成功')"
```

---

#### 问题 3: 测试失败 - ModuleNotFoundError

**症状**: 某些测试找不到模块

**解决方案**:
```bash
# 设置 PYTHONPATH
export PYTHONPATH=/Users/admin/codes/idea_beta/myproj/src:/Users/admin/codes/idea_beta/myproj/backend/e3:$PYTHONPATH

# 或者使用 pytest 的 pythonpath 选项
python -m pytest tests/ -v --pythonpath=src --pythonpath=backend/e3
```

---

#### 问题 4: 测试运行很慢

**症状**: 测试套件运行时间过长

**解决方案**:
```bash
# 只运行失败的测试
python -m pytest tests/ --lf

# 并行运行测试（需要安装 pytest-xdist）
pip install pytest-xdist
python -m pytest tests/ -n auto

# 只运行特定的测试文件
python -m pytest tests/unit/contracts/ -v
```

---

### 7.2 验证检查清单

在报告问题前，请确认：

- [ ] 你在正确的目录中 (`/Users/admin/codes/idea_beta/myproj`)
- [ ] 虚拟环境已激活
- [ ] 所有依赖已安装 (`pip install -e .`)
- [ ] Python 版本 >= 3.11 (`python --version`)
- [ ] 你在 main 分支上 (`git status`)
- [ ] 没有未提交的更改（或者知道为什么有）

---

### 7.3 获取帮助

如果以上解决方案都不能解决问题：

1. 检查 git 状态: `git status`
2. 检查最近的提交: `git log --oneline -10`
3. 运行完整测试并保存输出:
   ```bash
   python -m pytest tests/ -v > test_output.log 2>&1
   ```
4. 查看验收报告: `docs/engineering/PHASE3_ACCEPTANCE.md`

---

## 附录

### A. 快速参考命令

```bash
# 运行所有测试
./run_all_tests.sh

# 或者手动运行
cd /Users/admin/codes/idea_beta/myproj
python -m pytest tests/ -v
cd backend/e3
python -m pytest tests/ -v

# 运行特定测试
python -m pytest tests/integration/test_contract_flow.py -v

# 查看覆盖率
python -m pytest tests/ --cov=src/myproj --cov-report=html
```

### B. 相关文档

- [测试文档 - TEST_DOCUMENTATION.md](./TEST_DOCUMENTATION.md)
- [PRD - COMMUNICATION_OS_V1_SPEC.md](../product/COMMUNICATION_OS_V1_SPEC.md)
- [验收报告 - PHASE3_ACCEPTANCE.md](../engineering/PHASE3_ACCEPTANCE.md)

---

**测试手册结束**

祝你测试愉快! 🧪
