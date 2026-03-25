# 代码审查报告：代理原生通信控制层

## 1. 审查结论

这份仓库**不是“只需要微调”**，而是需要先完成一次**工程层面的修复与整合**，然后才能进入正常功能开发。

更准确地说：

- **文档方向是对的**，PRD/研发计划对产品边界、模块拆分、阶段目标的定义比较清楚。
- **代码实现处于“多工程师产物被粗暴合并后的半成品状态”**。
- 当前仓库同时存在：
  - **构建系统损坏**
  - **配置文件合并冲突残留**
  - **E2/E3 Python 代码大面积语法损坏**
  - **前后端接口契约不一致**
  - **前端大量页面仍直接依赖 mock 数据**
  - **真正的端到端闭环尚未形成**

因此建议判断为：

> **需要额外开发，且优先级最高的不是“继续加功能”，而是先做仓库修复、契约收敛、模块打通。**

---

## 2. 我认为当前仓库里相对好的部分

### 2.1 E1（Thread Core）是目前最接近可用基础的部分

我本地做了最小验证：

- `pytest -q tests` 可以通过（但它只覆盖 Python 顶层单测，不代表全仓可用）
- `src/myproj/core/domain/*`
- `src/myproj/core/services/*`
- `src/myproj/api/v1/*`

这部分的优点：

- Thread 状态模型比较完整
- 领域对象拆分较清晰
- State machine / event store / thread service 的方向正确
- ORM 与 Alembic 基础骨架已经搭起来

### 2.2 E5（AI 层）有一些可保留的“种子代码”

以下内容值得保留并继续演进：

- `src/e5/core/planner/*`
- `src/e5/core/risk/rules.ts`
- `src/e5/prompts/*`

这些文件体现出比较明确的模块边界：

- Goal Parser
- Action Generator
- Rule-first risk fallback
- Prompt library

虽然还远不能算“可上线”，但设计思路是合理的。

### 2.3 E4 UI 组件层有不错的雏形

- `src/components/ui/*`
- `src/components/thread/*`
- `src/components/approval/*`
- `src/components/replay/*`

从信息架构看，已经不是聊天 UI，而是在尝试做 control surface，这和 PRD 是一致的。

---

## 3. P0 级问题（必须先修，不修无法推进）

## 3.1 顶层构建配置已经损坏

### 证据

- `package.json` 被合并成了两个不同项目的内容，JSON 无法解析
- `tsconfig.json` 被两套配置直接拼接，JSON 非法
- `vitest.config.ts` 被两段 `defineConfig` 粗暴拼接，语法非法
- `README.md` 也是多份 README 直接拼接

### 直接影响

- `npm` 无法读取 `package.json`
- TypeScript 无法编译
- Vitest 无法运行
- 前端/E5 的标准开发流程全部中断

### 我本地验证到的现象

- `npm pkg get name` 报 `EJSONPARSE`
- `tsc --noEmit -p tsconfig.json` 直接报 `root value must be an object`

### 结论

这是**最高优先级阻断项**。

---

## 3.2 E2 / E3 大量 Python 文件包含 HTML 转义残留，语法层面不可运行

### 证据

大量文件里出现了：

- `-&gt;` 代替 `->`
- `&gt;=` 代替 `>=`
- `&lt;=` 代替 `<=`
- `&amp;` 代替 `&`

典型文件包括：

- `src/policy_control/controller.py`
- `src/policy_control/core.py`
- `src/policy_control/risk/*`
- `src/policy_control/api/*`
- `backend/e3/action_runtime/*`
- `backend/e3/api/*`
- `backend/e3/channel_adapters/*`
- `backend/e3/core/*`

### 我本地验证到的现象

用 `py_compile` 扫描后：

- Python 文件总数：132
- 编译失败：45
- 其中：
  - `src/policy_control` 下失败 24 个
  - `backend/e3` 下失败 19 个

### 直接影响

- E2 基本不可导入
- E3 基本不可导入
- 这些模块既无法运行，也无法测试，更无法联调

### 结论

这不是“小 bug”，而是**代码资产在合并/导出时被破坏**。

---

## 3.3 当前仓库并不是一个真正可运行的 monorepo

### 现象

仓库里同时存在：

- 顶层 Next.js / TS 工程
- 顶层 Python E1 工程（`src/myproj` + `pyproject.toml`）
- `backend/e3` 下独立 Python 工程
- `src/policy_control` 下另一套 E2 Python 代码
- `src/e5` 下 Node/TS AI 服务

但缺少一个真正统一的 monorepo 策略：

- 没有 workspace 规划
- 没有统一 task runner
- 没有统一 CI pipeline
- 没有统一接口契约生成/校验流程
- 没有统一环境管理

### 直接影响

每个模块都像“单独工程”，但又被放在一个仓库里，最终形成：

- 局部代码存在
- 全仓无法构建
- 联调路径缺失

---

## 4. P1 级问题（即使修完构建，也还不能形成 MVP）

## 4.1 E1 API 仍然使用内存服务，没有真正落到仓储/数据库

### 证据

在 `src/myproj/api/v1/threads.py` 中：

- 直接使用 `_thread_service = ThreadService()`
- 没有把 API 绑定到 `ThreadRepository`
- `DbSession` 虽然定义了，但线程 API 没有实际使用数据库会话

### 影响

这意味着：

- 线程数据仅存在进程内存里
- 重启即丢
- 无法支持多实例
- 无法支撑真正的 replay / integration / approval 联动

### 结论

E1 现在更像“领域层 demo + API prototype”，不是可联调的后端基础设施。

---

## 4.2 前端页面大量绕过 API 层，直接吃 mock 数据

### 证据

以下页面直接 import mock：

- `src/app/(app)/page.tsx`
- `src/app/(app)/approvals/page.tsx`
- `src/app/(app)/approvals/[id]/page.tsx`
- `src/app/(app)/replay/page.tsx`
- `src/app/(app)/replay/[id]/page.tsx`
- `src/app/(app)/threads/[id]/page.tsx`

同时：

- `src/lib/api/threads.ts` 真实 API 与 mock API 并存
- `src/lib/api/approvals.ts` 的真实 API 还是 `throw new Error('Not implemented')`

### 影响

即使后端修好了：

- 页面也不会自动接到真实数据
- UI 当前更像 demo 版静态原型
- 真实联调价值有限

### 结论

E4 目前完成的是“页面壳子”，不是“控制面工作流前端”。

---

## 4.3 前后端接口契约不一致

### 典型例子

前端 `Thread` 类型：

- `title: string`
- `objective: string`
- `delegationProfile: string`
- `ownerId: string`
- `participants: Principal[]`

后端创建线程接口却要求：

- `objective: { title, description, due_at }`
- `owner_id`
- `delegation_profile: { profile_name, level, ... }`
- `participant_ids: UUID[]`

### 影响

即使真实 API 接通：

- 前端的 `createThread/updateThread/getThread` 也无法直接对接后端返回结构
- 必须加 BFF/adapter 或统一 DTO

### 结论

当前仓库并没有真正冻结一个“前后端共享契约”。

---

## 4.4 `ApiClient` 默认 URL 构造有 bug

### 证据

`src/lib/api/client.ts`:

- `API_BASE_URL` 默认值是 `'/api'`
- `new URL(endpoint, this.baseUrl)` 需要一个绝对 base URL

在浏览器 / Node 标准实现里：

- `new URL('/threads', '/api')` 会报 `Invalid URL`

### 影响

即使 package / tsconfig 修复后，真实 API 模式下前端请求也可能直接失败。

### 结论

这是一个隐藏较深但会立刻影响联调的 runtime bug。

---

## 4.5 E5 的 Fastify schema 机制不完整

### 证据

在 `src/e5/api/routes/*.ts` 中：

- 直接把 Zod schema 放进 Fastify `schema.body` / `schema.response`
- 还使用了 `$ref: 'ErrorResponseSchema'`

但在 `src/e5/api/app.ts` 中：

- 没有注册任何 Zod type provider
- 没有做 schema compiler 适配
- 没有 `addSchema(ErrorResponseSchema)` 之类的注册

### 影响

这会导致：

- schema 校验未必按预期工作
- response schema reference 失效
- Swagger / runtime 校验链条不成立

### 结论

E5 API 层当前更像“代码草稿”，不是完整可运行服务。

---

## 4.6 E5 存在“可运行雏形”，但不少接口仍是 placeholder

### 证据

`src/e5/api/routes/drafter.ts` 中：

- draft-message 是模板拼接，不是真正的 drafter
- generate-time-slots 返回空数组 + placeholder 文案
- generate-checklist 只有一条固定 checklist

另外：

- `summary.ts` 存在，但 `app.ts` 没有注册 summary route

### 影响

E5 还不能支撑 PRD 里要求的：

- 时间协调
- 资料收集
- 跟进催办

三类标准线程闭环。

---

## 4.7 E1 底层仓储层还有几个真实 bug

### Bug 1：`BaseRepository.save()` 对 `merge()` 返回值处理错误

在 `src/myproj/core/repositories/base.py`：

- 更新路径里 `self.session.merge(model)` 的返回值没有接住
- 后面 `refresh(model)` 很可能刷新的是 detached 实例

这在真实数据库路径上容易出错。

### Bug 2：JSON 字段与 UUID 列表的序列化设计不一致

`Thread.participant_ids` 是 `list[UUID]`，但 ORM 里：

- `participant_ids = Column(JSON, default=list)`

直接把 UUID 对象写进 JSON 列，序列化行为不稳定；
而 `find_by_participant()` 又按字符串做 contains 查询，进一步说明领域层与持久化层表示不一致。

### Bug 3：仓储/API/服务层存在双轨实现

- 一套是 in-memory `ThreadService`
- 一套是 ORM + Repository

但没有完成切换与整合。

这会导致后续联调时非常容易出现“接口能跑，但数据不在一个世界里”的问题。

---

## 5. P2 级问题（不是立刻阻断，但会明显拖慢后续开发）

## 5.1 测试体系给出“虚假安全感”

### 现象

- `pytest -q tests` 可以通过
- 但它只跑了 Python 顶层测试
- `tests/unit/planner.test.ts`、`tests/unit/risk.test.ts` 需要 Vitest，而现在 Vitest 配置本身就是坏的
- E2 / E3 的测试也没有进入统一可执行流程

### 影响

团队很容易以为“测试是绿的”，但实际上：

- 前端没测
- E5 没测通
- E2/E3 没法 import
- 端到端也没测

### 结论

必须尽快建立真正的分层 CI：

- Python unit
- TS unit
- contract test
- e2e smoke

---

## 5.2 README 与工程说明已经失真

顶层 README 现在混入了：

- E1 说明
- E2 说明
- E3 说明

用户已经无法从 README 判断：

- 仓库如何启动
- 哪个服务先起
- 开发环境怎么搭
- MVP 真实入口是什么

这会直接影响后续协作效率。

---

## 5.3 Monorepo 边界不清晰，目录命名会增加维护成本

例如：

- `src/myproj` 是 E1
- `src/policy_control` 是 E2
- `backend/e3` 是 E3
- `src/e5` 是 E5
- `src/app` 是 E4

从一致性上看，E1/E2/E5 都在 `src` 下，E3 却在 `backend` 下。

建议统一成：

- `apps/web`
- `apps/e1-thread-core`
- `apps/e2-policy-control`
- `apps/e3-integration-action`
- `apps/e5-ai-layer`
- `packages/contracts`
- `packages/ui`
- `packages/shared`

这样后续 workspace / CI / Docker / contracts 才容易管理。

---

## 6. 最重要的判断：哪些只需微调，哪些必须额外开发

## 6.1 只需微调/修复的部分

这些更像“可保留资产”，修一修能继续用：

1. **E1 领域模型与状态机主骨架**
2. **E5 planner/risk 的部分种子代码**
3. **E4 的部分 UI 组件与页面信息架构**
4. **PRD/研发计划/模块拆分思路**

这些不建议推倒重来。

---

## 6.2 必须额外开发的部分

这些不是修补能解决，必须继续开发：

1. **仓库级 build/test/dev 环境重建**
2. **E2/E3 的代码修复与可运行化**
3. **统一 contract / DTO / OpenAPI**
4. **E1 从内存服务切到真实持久化路径**
5. **E4 从 mock 页面切到真实控制面前端**
6. **E5 drafter / time slot / summary / risk API 补全**
7. **Email + Calendar + Thread + Approval 的端到端闭环**
8. **统一 CI / integration / replay / smoke test**

所以结论非常明确：

> 当前项目**不适合继续在现状上边修边堆功能**，而是要先做一次“仓库稳定化 + 契约统一 + MVP 闭环打通”的专项。

---

## 7. 建议的详细修改计划

## Phase A：仓库稳定化（1 周，P0）

### 目标

让仓库重新具备“能安装、能启动、能测试”的最小工程属性。

### 任务

1. **修复所有被粗暴合并的配置文件**
   - 重建 `package.json`
   - 拆分 `tsconfig.json`
   - 重建 `vitest.config.ts`
   - 清理顶层 `README.md`

2. **批量修复 HTML 转义污染**
   - 全量替换源码中的 `&gt; &lt; &amp;`
   - 修复 E2 / E3 / demo 脚本 / pyproject / yaml 文档
   - 逐文件做语法回归

3. **建立最小 CI**
   - Python syntax check
   - TypeScript typecheck
   - lint
   - pytest / vitest 最小执行链

### 完成标准

- `npm install` 可执行
- `tsc --noEmit` 可执行
- Python 全仓可 import / compile
- 顶层 README 能指导启动

---

## Phase B：模块可运行化（1–2 周，P0/P1）

### 目标

让 E1/E2/E3/E5 分别能独立启动，并可通过健康检查。

### 任务

1. **E1**
   - 把 API 从 `_thread_service` 内存实例切换到 repository + DB session
   - 修复 BaseRepository.save / JSON UUID 等问题

2. **E2**
   - 修完语法后先跑通纯内存版 policy/risk/approval 服务
   - 暂不追求性能，先保证规则链可执行

3. **E3**
   - 修完语法后先让 ActionRun / Outbox/Inbox / ExternalResolver 单测可跑
   - Email/Calendar adapter 可先 mock provider

4. **E5**
   - 修复 Fastify schema 注册
   - 补全 summary route 注册
   - 先把 drafter / time slot / checklist 做成可回归的 deterministic fallback

### 完成标准

- 四个服务都能启动
- 每个服务至少有 `/health`
- 各自单测可执行

---

## Phase C：统一契约与共享类型（1 周，P0/P1）

### 目标

把“大家都写了自己的模型”收敛成真正共享的 contract。

### 任务

1. 建立 `packages/contracts`
   - Thread DTO
   - Approval DTO
   - Replay DTO
   - Delegation DTO
   - Risk DTO

2. 统一字段命名
   - `snake_case` / `camelCase` 明确边界
   - 统一 `Thread.objective` 的表示
   - 统一 participant / principal / relationship 表示

3. 生成或维护 OpenAPI / JSON Schema
   - 前端直接消费统一 DTO
   - 后端返回结构保持一致

### 完成标准

- 前后端不再有双份 thread type
- create/update/get 的 request/response 统一
- API mock 由 contract 自动生成或半自动同步

---

## Phase D：打通 MVP 主闭环（2–3 周，P1）

### 目标

至少打通一条真实 thread：

> 创建线程 → draft → approval → send → external reply → thread 更新 → replay 可见

### 建议先打的最小闭环

优先做：**时间协调线程**

原因：

- 最符合 PRD
- 风险相对低
- Calendar + Email 刚好能形成闭环
- approval / replay / takeover 都有自然落点

### 任务

1. 前端新建线程页接真实 API
2. Thread Detail 改为真实 query
3. Approval Center 改为真实审批流
4. E5 生成候选时间 + draft 邮件
5. E3 发送邮件 / 接收回复 / 回写 thread
6. E1 记录事件流并驱动 replay

### 完成标准

- 至少 1 条标准线程真实走通
- replay 能看到动作轨迹
- takeover 能切断自动推进

---

## Phase E：补齐 PRD 中真正关键但现在缺失的能力（后续）

1. Shadow / Observe 模式
2. Bounded Auto 最小预算模型
3. Relationship template 页面与规则绑定
4. Kill Switch 的 profile/thread 级真实落地
5. Summary / analytics / metrics
6. integration 监控与异常隔离

---

## 8. 我对当前项目的总判断

如果以“代码完成度”看，这个仓库现在只能算：

- **文档成熟度：高**
- **局部模块成熟度：中等**
- **统一工程成熟度：低**
- **真实 MVP 可交付性：低**

但如果以“是否值得继续做”看，我的判断是：

> **值得继续，而且方向是对的；但必须先从“继续写功能”切换到“先修工程、统一契约、打通一条闭环”。**

一句话总结：

> 这不是一个“细抛光项目”，而是一个“架构方向正确，但仓库集成失败，需要一次严肃收敛”的项目。

