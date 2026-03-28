# Communication OS v1 - 测试指南

📖 本文档指导你如何测试 Communication OS v1 的所有功能。

---

## 目录

1. [快速开始](#1-快速开始)
2. [后端测试](#2-后端测试)
3. [前端测试](#3-前端测试)
4. [完整测试套件](#4-完整测试套件)
5. [v0 vs v1 测试重点对比](#5-v0-vs-v1-测试重点对比)
6. [测试文件说明](#6-测试文件说明)

---

## 1. 快速开始

### 环境要求

- Python 3.11+
- Node.js 18+
- npm 或 yarn

### 一键启动测试

```bash
# 方式1: 运行所有测试
./run_all_tests.sh

# 方式2: 只运行后端契约演示
python3 test_demo.py

# 方式3: 只运行前端测试（需要先启动前端）
cd src
npm run dev
# 然后打开 http://localhost:3000，按 FRONTEND_TEST_GUIDE.md 测试
```

---

## 2. 后端测试

### 2.1 后端契约测试演示

这是理解 v1 核心概念的最快方式。

```bash
python3 test_demo.py
```

**测试内容**:
- ✅ **AuthorityGrant** - 权威授予，验证"Identity First"原则
- ✅ **SenderStack** - 发送者栈，验证"可解释的责任链"
- ✅ **DisclosurePolicy** - 披露策略，验证"透明性"
- ✅ **ActionEnvelope + RiskPosture** - 动作信封+四层风险判断
- ✅ **AttentionDecision + Replay Events** - 注意力决策+完整可回放

**输出示例**:
```
======================================================================
测试 1: AuthorityGrant（权威授予）
演示: Identity First 原则 - 谁可以代表谁
======================================================================

✅ 权威授予创建成功:

   👤 授予者: 张明 (HUMAN)
   🤖 被授予者: Agent Assistant (PERSONAL_AGENT)

   ✅ 允许动作: draft_message, propose_time, send_low_risk_email
   ❌ 禁止动作: negotiate_price, make_commitment, terminate_relationship
...
```

### 2.2 交互式后端测试

```bash
python3 test_interactive.py
```

这个脚本会逐步引导你完成每个测试，需要按Enter继续。

### 2.3 后端单元测试和集成测试

```bash
cd backend/e3
pytest tests/ -v
```

**测试结构**:
```
backend/e3/tests/
├── unit/
│   ├── test_action_envelope.py      # ActionEnvelope契约测试
│   ├── test_action_state_machine.py # 状态机测试
│   └── test_idempotency.py          # 幂等性测试
├── integration/
│   ├── test_email_adapter.py        # Email适配器集成测试
│   └── test_calendar_adapter.py     # Calendar适配器集成测试
└── conftest.py                       # pytest配置
```

---

## 3. 前端测试

### 3.1 启动前端开发服务器

```bash
cd src
npm run dev
```

然后打开: http://localhost:3000

### 3.2 前端测试场景

详细测试指南请查看: [FRONTEND_TEST_GUIDE.md](FRONTEND_TEST_GUIDE.md)

#### 场景1: Thread Over Message（线程优先）
**验证点**:
- [ ] 看到的是"线程列表"，不是"消息列表"
- [ ] 每个线程有明确的目标（objective）
- [ ] 每个线程有状态标签（planning/active/awaiting_approval等）
- [ ] 每个线程有委托档位和风险级别

#### 场景2: Replayable Trust（可回放信任）
**验证点**:
- [ ] 时间线（Timeline）显示完整事件链
- [ ] 每个事件有明确的类型标签
- [ ] 决策追踪（Decision Trace）显示四层风险评估
- [ ] 能看到"为什么"做了某个决策

#### 场景3: Delegation Is Layered（分层委托）
**验证点**:
- [ ] 新建线程时有5个委托档位可选
- [ ] 不同线程可以有不同的委托档位
- [ ] 委托档位在线程详情页清晰展示

#### 场景4: Identity First（身份优先）
**验证点**:
- [ ] 能区分不同类型的participant（Human/Agent/External）
- [ ] 时间线中的每个事件都明确显示actor
- [ ] 有avatar和显示名称

#### 场景5: Human Sovereignty（人类主权）
**验证点**:
- [ ] 有Pause/Resume按钮
- [ ] 有Takeover（接管）按钮
- [ ] 高风险动作需要审批

#### 场景6: Action Over Text（动作优先）
**验证点**:
- [ ] 时间线中有不同类型的事件（state_change/decision/approval等）
- [ ] 不是所有内容都被当作"消息"
- [ ] 不同类型的事件有不同的视觉呈现

---

## 4. 完整测试套件

### 运行所有测试

```bash
./run_all_tests.sh
```

这个脚本会:
1. ✅ 运行Python类型检查
2. ✅ 运行后端单元测试（pytest）
3. ✅ 运行前端类型检查（TypeScript）
4. ✅ 运行前端构建（Next.js build）
5. ✅ 显示测试总结

### 测试统计

当前测试覆盖:
- **后端单元测试**: 166个
- **E3单元测试**: 30个
- **E3集成测试**: 15个
- **核心集成测试**: 7个
- **总计**: 218个测试

---

## 5. v0 vs v1 测试重点对比

这是理解产品演进的关键！

| 维度 | v0 测试重点 | v1 测试重点 |
|------|-------------|-------------|
| **产品定位** | "做一个能委托的聊天工具" | "做一个通信操作系统" |
| **核心概念** | Delegation Profile（5个档位） | 5大契约 + 9大实体 + 8大原则 |
| **身份模型** | 简单的"sender"字段 | SenderStack（owner/delegate/author/approver/executor） |
| **风险判断** | 简单的风险级别字段 | 四层风险判断（关系/动作/内容/结果） |
| **测试重点** | 功能流程（起草→审批→发送） | 契约 + 状态机 + 可重放性 |
| **前端感觉** | "更聪明的聊天工具" | "可委托、可审计、可接管的工作区" |

### 为什么有这个区别？

**v0 的思路**:
- 先做一个实用的工具
- 从Email+Calendar切入
- 强调"功能可用"

**v1 的思路**:
- 要做一个操作系统级的基础设施
- 定义明确的契约（Contracts）
- 强调"可治理、可审计、可追溯"

---

## 6. 测试文件说明

### 6.1 快速测试文件

| 文件 | 用途 | 运行方式 |
|------|------|---------|
| `test_demo.py` | 后端契约演示（非交互式） | `python3 test_demo.py` |
| `test_examples.py` | 后端契约演示（交互式） | `python3 test_examples.py` |
| `test_interactive.py` | Python交互式测试脚本 | `python3 test_interactive.py` |
| `run_all_tests.sh` | 一键运行所有测试 | `./run_all_tests.sh` |

### 6.2 测试文档

| 文件 | 用途 |
|------|------|
| `TEST_README.md` | 本文档 - 总览 |
| `FRONTEND_TEST_GUIDE.md` | 前端测试详细指南 |
| `docs/testing/TEST_DOCUMENTATION.md` | 完整测试策略文档 |
| `docs/testing/TEST_MANUAL.md` | 测试手册 |
| `docs/engineering/PRD_VERSION_COMPARISON.md` | PRD版本对比分析 |

### 6.3 实际测试代码

| 位置 | 用途 |
|------|------|
| `backend/e3/tests/` | 后端Python测试 |
| `backend/e3/tests/unit/` | 后端单元测试 |
| `backend/e3/tests/integration/` | 后端集成测试 |

---

## 7. 推荐测试流程

### 第一次接触?

1. **先看概念演示**
   ```bash
   python3 test_demo.py
   ```

2. **再玩前端**
   ```bash
   cd src && npm run dev
   ```
   打开 http://localhost:3000，按 FRONTEND_TEST_GUIDE.md 测试

3. **最后看完整文档**
   - `docs/engineering/PRD_VERSION_COMPARISON.md` - 理解版本差异
   - `docs/testing/TEST_DOCUMENTATION.md` - 完整测试策略

### 想深入理解?

1. 阅读 `docs/product/COMMUNICATION_OS_V1_SPEC.md` - v1产品规格
2. 运行 `cd backend/e3 && pytest tests/ -v` - 看实际测试
3. 阅读 `backend/e3/tests/unit/test_action_envelope.py` - 看契约如何测试

---

## 8. 常见问题

### Q: 前端看起来很简单，v1的变化体现在哪里?

A: v1的变化主要在**后端架构和测试层**，前端只是最终呈现的结果。你看到的"简单"界面背后是:
- 完整的契约系统（Contracts）
- 四层风险判断
- 可回放的事件链
- 明确的责任链（SenderStack）

按 `FRONTEND_TEST_GUIDE.md` 测试，你会发现这些概念都在前端有所体现！

### Q: 我应该先测后端还是先测前端?

A: 推荐顺序:
1. 先运行 `test_demo.py` 理解v1核心概念
2. 再玩前端，直观感受这些概念如何呈现
3. 最后看实际测试代码，深入理解

### Q: 218个测试都测了什么?

A: 测试金字塔:
```
        /\
       /  \      E2E Tests (7)
      /----\
     /      \    Integration Tests (22)
    /--------\
   /          \  Unit Tests (196)
  /------------\
```

- **单元测试**: 领域模型、核心逻辑、契约验证
- **集成测试**: 通道适配器、端到端合同流程
- **E2E测试**: 完整场景（面试安排等）

---

## 9. 下一步

读完本文档后，你可以:

1. **立即开始测试**:
   ```bash
   python3 test_demo.py
   ```

2. **深入学习**:
   - 阅读 `docs/product/COMMUNICATION_OS_V1_SPEC.md`
   - 阅读 `docs/engineering/PRD_VERSION_COMPARISON.md`

3. **贡献测试**:
   - 查看 `backend/e3/tests/` 了解现有测试
   - 添加新的测试用例

---

## 附录: 8大产品原则快速参考

| 原则 | 测试场景 |
|------|---------|
| 1. Identity First | 场景4 |
| 2. Delegation Is Layered | 场景3 |
| 3. Thread Over Message | 场景1 |
| 4. Action Over Text | 场景6 |
| 5. Replayable Trust | 场景2 |
| 6. Human Sovereignty | 场景5 |
| 7. Relationship-Aware Behavior | (通过关系类别和风险体现) |
| 8. Transport-Agnostic Execution | (前端不关心Email/Calendar) |

---

**祝测试愉快！** 🎉

如有问题，请查看相关文档或联系开发团队。
