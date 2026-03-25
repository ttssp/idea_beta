# 代理原生通信控制层 - 详细开发计划

基于代码审查报告 `code_review_agent_native_comm_control.md`，本文件制定可执行的详细开发计划。

---

## 总体判断

| 维度 | 状态 |
|------|------|
| 文档成熟度 | 高 |
| 局部模块成熟度 | 中等 |
| 统一工程成熟度 | 低 |
| 真实 MVP 可交付性 | 低 |

**结论**：需要先做仓库稳定化 + 契约统一 + MVP 闭环打通，而不是继续堆功能。

---

## Phase A: 仓库稳定化（P0 - 1 周）

### 目标
让仓库重新具备"能安装、能启动、能测试"的最小工程属性。

---

### A.1 修复顶层构建配置

#### 任务 1：重建 package.json
**问题**：当前文件是两个 package.json 粗暴拼接，JSON 格式错误

**文件**：`/package.json`

**行动**：
- [ ] 创建合理的 monorepo 结构
- [ ] 使用 npm workspaces 或 pnpm workspaces
- [ ] 保留 E4（前端）和 E5（AI 层）的依赖
- [ ] 添加统一的 scripts

**预期结构**：
```json
{
  "name": "agent-comm-control",
  "version": "0.1.0",
  "private": true,
  "workspaces": [
    "apps/web",
    "apps/e5-ai-layer",
    "packages/contracts",
    "packages/ui"
  ],
  "scripts": {
    "dev": "turbo run dev",
    "build": "turbo run build",
    "test": "turbo run test",
    "lint": "turbo run lint",
    "typecheck": "turbo run typecheck",
    "format": "prettier --write ."
  },
  "devDependencies": {
    "turbo": "^2.0.0",
    "prettier": "^3.3.3",
    "typescript": "^5.6.2"
  }
}
```

**验收标准**：
- `npm install` 成功执行
- `npm pkg get name` 返回正确值

---

#### 任务 2：拆分 tsconfig.json
**问题**：当前文件是两套 tsconfig 直接拼接

**文件**：`/tsconfig.json`

**行动**：
- [ ] 创建 `/tsconfig.base.json` - 基础配置
- [ ] 创建 `/apps/web/tsconfig.json` - 前端配置
- [ ] 创建 `/apps/e5-ai-layer/tsconfig.json` - E5 配置
- [ ] 创建 `/packages/contracts/tsconfig.json` - 契约包配置

**验收标准**：
- `tsc --noEmit -p apps/web/tsconfig.json` 成功
- `tsc --noEmit -p apps/e5-ai-layer/tsconfig.json` 成功

---

#### 任务 3：重建 vitest.config.ts
**问题**：当前文件是两段 `defineConfig` 粗暴拼接

**文件**：`/vitest.config.ts`

**行动**：
- [ ] 删除根目录 vitest.config.ts
- [ ] 在 `/apps/web/vitest.config.ts` 配置前端测试
- [ ] 在 `/apps/e5-ai-layer/vitest.config.ts` 配置 E5 测试
- [ ] 使用 workspace 配置继承

**验收标准**：
- 每个子项目可以独立运行 `vitest`

---

#### 任务 4：清理并重建 README.md
**问题**：多份 README 直接拼接

**文件**：`/README.md`

**行动**：
- [ ] 保留 PRD 中的产品定位
- [ ] 新增 monorepo 结构说明
- [ ] 新增快速启动指南
- [ ] 新增各服务端口说明

**验收标准**：
- 新开发者能按 README 启动项目

---

### A.2 批量修复 HTML 转义污染

#### 任务 5：扫描并修复所有 Python 文件
**问题**：45 个 Python 文件包含 `-&gt;`、`&gt;=`、`&lt;=`、`&amp;`

**影响范围**：
- `src/policy_control/` - 24 个文件
- `backend/e3/` - 19 个文件

**行动**：
- [ ] 编写批量修复脚本
- [ ] 执行全量替换：
  - `&gt;` → `>`
  - `&lt;` → `<`
  - `&amp;` → `&`
  - `&quot;` → `"`
  - `&apos;` → `'`
- [ ] 逐文件验证语法

**修复脚本示例**：
```bash
# 批量修复
find . -name "*.py" -type f -exec sed -i '' \
  -e 's/&gt;/>/g' \
  -e 's/&lt;/</g' \
  -e 's/&amp;/\&/g' {} +

# 语法检查
python -m py_compile **/*.py
```

**验收标准**：
- `python -m py_compile` 扫描全仓无错误
- 所有 Python 模块可 import

---

### A.3 建立最小 CI

#### 任务 6：创建 GitHub Actions 工作流
**文件**：`.github/workflows/ci.yml`

**行动**：
- [ ] Python 语法检查
- [ ] TypeScript 类型检查
- [ ] ESLint 检查
- [ ] pytest 最小执行
- [ ] vitest 最小执行

**验收标准**：
- PR 必须通过 CI 才能合并

---

## Phase B: 模块可运行化（P0/P1 - 1-2 周）

### 目标
让 E1/E2/E3/E5 分别能独立启动，并可通过健康检查。

---

### B.1 E1 - Thread Core 修复

#### 任务 7：修复 BaseRepository.save()
**问题**：`merge()` 返回值没有接住，`refresh()` 可能刷新 detached 实例

**文件**：`src/myproj/core/repositories/base.py`

**当前代码**：
```python
if existing:
    model = self._to_model(entity)
    self.session.merge(model)
else:
    model = self._to_model(entity)
    self.session.add(model)

self.session.flush()
self.session.refresh(model)  # ❌ merge 返回的才是 attached 实例
```

**修复方案**：
```python
if existing:
    model = self._to_model(entity)
    model = self.session.merge(model)  # ✅ 接住返回值
else:
    model = self._to_model(entity)
    self.session.add(model)

self.session.flush()
self.session.refresh(model)
```

**验收标准**：
- 单测覆盖更新路径

---

#### 任务 8：修复 JSON UUID 序列化
**问题**：`Thread.participant_ids` 直接把 UUID 对象写进 JSON 列

**文件**：`src/myproj/infra/db/models.py`

**当前问题**：
```python
participant_ids = Column(JSON, default=list)  # ❌ UUID 无法直接 JSON 序列化
```

**修复方案**：
方案 A（推荐）：使用 ARRAY(UUID)（PostgreSQL）
```python
from sqlalchemy.dialects.postgresql import ARRAY, UUID

participant_ids = Column(ARRAY(UUID(as_uuid=True)), default=list)
```

方案 B（通用）：UUID 转字符串列表
```python
# 在 _to_model/_to_entity 中做转换
def _to_model(self, entity: Thread) -> ThreadModel:
    return ThreadModel(
        participant_ids=[str(pid) for pid in entity.participant_ids],
        ...
    )

def _to_entity(self, model: ThreadModel) -> Thread:
    return Thread(
        participant_ids=[UUID(pid) for pid in model.participant_ids],
        ...
    )
```

**验收标准**：
- 仓储读写 UUID 列表正常

---

#### 任务 9：把 API 从内存服务切到数据库仓储
**问题**：当前 API 使用内存 `_thread_service`，没有用到数据库

**文件**：`src/myproj/api/v1/threads.py`

**行动**：
- [ ] 注入 `DbSession`
- [ ] 注入 `ThreadRepository`
- [ ] 替换所有 `_thread_service` 调用
- [ ] 保留内存服务作为 fallback 或测试用

**代码迁移示例**：
```python
# ❌ 当前
_thread_service = ThreadService()

@router.post("")
async def create_thread(data: ThreadCreateSchema):
    thread, _ = _thread_service.create_thread(...)

# ✅ 修复后
from myproj.core.repositories.thread_repository import ThreadRepository

@router.post("")
async def create_thread(
    data: ThreadCreateSchema,
    db: DbSession = Depends(),
):
    repo = ThreadRepository(db)
    thread = build_thread_from_schema(data)
    saved = repo.save(thread)
    return ThreadResponseSchema.from_domain(saved)
```

**验收标准**：
- 重启服务后数据不丢失
- `/health` 端点返回数据库连接状态

---

### B.2 E2 - Policy Control 修复

#### 任务 10：修复语法后跑通内存版服务
**前置条件**：A.2 任务已完成

**行动**：
- [ ] 验证所有文件可 import
- [ ] 启动纯内存版 policy/risk/approval 服务
- [ ] 测试 8 步决策链基本可执行
- [ ] 添加 `/health` 端点

**验收标准**：
- `python -m policy_control` 可启动
- `curl http://localhost:8002/health` 返回 200

---

### B.3 E3 - Integration Action 修复

#### 任务 11：修复语法后跑通单测
**前置条件**：A.2 任务已完成

**行动**：
- [ ] 验证所有文件可 import
- [ ] 让 ActionRun / Outbox / Inbox / ExternalResolver 单测可跑
- [ ] Email/Calendar adapter 先用 mock provider
- [ ] 添加 `/health` 端点

**验收标准**：
- `pytest backend/e3/tests/` 可执行
- `curl http://localhost:8003/health` 返回 200

---

### B.4 E5 - AI Layer 修复

#### 任务 12：修复 Fastify schema 注册
**问题**：
- Zod schema 直接放进 Fastify，但没有注册 Zod type provider
- `$ref: 'ErrorResponseSchema'` 没有 addSchema

**文件**：`src/e5/api/app.ts`

**行动**：
- [ ] 添加 `@fastify/type-provider-zod`
- [ ] 注册 Zod type provider
- [ ] 注册 ErrorResponseSchema
- [ ] 添加 schema compiler 适配

**修复示例**：
```typescript
import { serializerCompiler, validatorCompiler } from 'fastify-type-provider-zod';
import { ErrorResponseSchema } from './schemas.js';

export async function createApp() {
  const fastify = Fastify({ ... });

  // ✅ 注册 Zod
  fastify.setValidatorCompiler(validatorCompiler);
  fastify.setSerializerCompiler(serializerCompiler);

  // ✅ 注册共享 schema
  fastify.addSchema({
    $id: 'ErrorResponseSchema',
    ...ErrorResponseSchema.shape,
  });

  return fastify;
}
```

**验收标准**：
- schema 校验按预期工作
- response schema reference 生效

---

#### 任务 13：补全 summary route 注册
**问题**：`summary.ts` 存在，但 `app.ts` 没有注册

**文件**：`src/e5/api/app.ts`

**行动**：
- [ ] import summaryRoutes
- [ ] `fastify.register(summaryRoutes, { prefix: '/ai' })`

**验收标准**：
- `/ai/summary` 端点可访问

---

#### 任务 14：把 drafter / time slot / checklist 做成 deterministic fallback
**目标**：先可回归，再接入真实 LLM

**行动**：
- [ ] 基于 thread objective 模板生成 draft
- [ ] 基于 mock calendar 生成 time slots
- [ ] 基于 thread type 生成 checklist
- [ ] 所有输出可快照测试

**验收标准**：
- vitest 快照测试可通过

---

## Phase C: 统一契约与共享类型（P0/P1 - 1 周）

### 目标
把"大家都写了自己的模型"收敛成真正共享的 contract。

---

### C.1 建立 packages/contracts

#### 任务 15：创建契约包
**目录结构**：
```
packages/contracts/
├── package.json
├── tsconfig.json
└── src/
    ├── index.ts
    ├── thread.ts       # Thread DTO
    ├── approval.ts     # Approval DTO
    ├── replay.ts       # Replay DTO
    ├── delegation.ts   # Delegation DTO
    ├── risk.ts         # Risk DTO
    └── openapi/
        ├── e1.json     # E1 OpenAPI spec
        ├── e2.json     # E2 OpenAPI spec
        ├── e3.json     # E3 OpenAPI spec
        └── e5.json     # E5 OpenAPI spec
```

**行动**：
- [ ] 创建 `packages/contracts`
- [ ] 定义统一 DTO（Zod + TypeScript）
- [ ] 生成 Pydantic 模型（Python）
- [ ] 统一字段命名规范

**验收标准**：
- 前后端不再有双份 thread type

---

#### 任务 16：统一字段命名
**规则**：
- 网络传输（JSON）：`snake_case`
- TypeScript：`camelCase`
- Python：`snake_case`
- 数据库：`snake_case`

**需要统一的表示**：
- [ ] `Thread.objective` - 统一为 `{ title, description, due_at }`
- [ ] `participant` / `principal` / `relationship` - 明确边界
- [ ] `DelegationProfile` - 字段对齐

**验收标准**：
- create/update/get 的 request/response 统一

---

### C.2 生成 OpenAPI / JSON Schema

#### 任务 17：设置 OpenAPI 生成
**工具选型**：
- E1 FastAPI: 自带 OpenAPI 生成
- E2 FastAPI: 自带 OpenAPI 生成
- E3 FastAPI: 自带 OpenAPI 生成
- E5 Fastify: `@fastify/swagger` + `@fastify/swagger-ui`
- 前端: `openapi-typescript` 生成类型

**行动**：
- [ ] 各服务暴露 `/openapi.json`
- [ ] 契约包聚合所有 spec
- [ ] 前端代码生成类型安全 client
- [ ] API mock 由 contract 生成

**验收标准**：
- `npm run codegen` 可更新类型
- 类型不匹配时编译错误

---

## Phase D: 打通 MVP 主闭环（P1 - 2-3 周）

### 目标
至少打通一条真实 thread：
> 创建线程 → draft → approval → send → external reply → thread 更新 → replay 可见

**建议优先打通：时间协调线程**

---

### D.1 前端接真实 API

#### 任务 18：修复 ApiClient URL 构造 bug
**问题**：`API_BASE_URL = '/api'` 是相对路径，`new URL(endpoint, this.baseUrl)` 会报错

**文件**：`src/lib/api/client.ts`

**修复方案**：
```typescript
// ❌ 当前
const url = new URL(endpoint, this.baseUrl);  // 相对 base 会抛错

// ✅ 修复
private buildUrl(endpoint: string, params?: Record<string, string | number>): string {
  let url: string;
  if (this.baseUrl.startsWith('http')) {
    // 绝对 URL，正常使用
    url = new URL(endpoint, this.baseUrl).toString();
  } else {
    // 相对路径，直接拼接
    url = this.baseUrl.replace(/\/$/, '') + '/' + endpoint.replace(/^\//, '');
  }
  // ... 添加 search params
}
```

**验收标准**：
- 浏览器环境相对路径工作正常
- Node 环境绝对路径工作正常

---

#### 任务 19：新建线程页接真实 API
**文件**：`src/app/(app)/threads/new/page.tsx`

**行动**：
- [ ] 移除 mock 数据 import
- [ ] 使用 `useMutation` + `apiClient.post('/threads')`
- [ ] 处理 loading / error 状态
- [ ] 创建成功后跳转 `/threads/[id]`

**验收标准**：
- 新建线程真正写入 E1 数据库

---

#### 任务 20：Thread Detail 改为真实 query
**文件**：`src/app/(app)/threads/[id]/page.tsx`

**行动**：
- [ ] 移除 mock 数据
- [ ] 使用 `useQuery` + `apiClient.get('/threads/{id}')`
- [ ] 事件流用 SSE 或轮询
- [ ] 操作按钮调用真实 API

**验收标准**：
- 线程状态实时更新

---

#### 任务 21：Approval Center 改为真实审批流
**文件**：`src/app/(app)/approvals/page.tsx`

**行动**：
- [ ] 移除 mock 数据
- [ ] 接 E2 `/approvals` API
- [ ] 审批操作调用 E2 `/approvals/{id}/approve`
- [ ] 拒绝操作调用 E2 `/approvals/{id}/reject`

**验收标准**：
- 审批状态流转正常

---

### D.2 服务间联调

#### 任务 22：E5 生成候选时间 + draft 邮件
**流程**：
1. E1 线程创建事件 → Event Bus
2. E5 消费事件 → 调用 `/ai/generate-time-slots`
3. E5 调用 `/ai/draft-message`
4. E5 回写 draft 到 E1 thread

**行动**：
- [ ] 定义 Event Bus 接口（可先用简单 HTTP webhook）
- [ ] E5 实现时间协调线程的 drafter
- [ ] E5 调用 E3 mock calendar
- [ ] draft 存入 E1 thread messages

**验收标准**：
- 创建时间协调线程后自动生成 draft

---

#### 任务 23：E3 发送邮件 / 接收回复 / 回写 thread
**流程**：
1. 审批通过 → E2 事件
2. E3 消费事件 → 调用 Email adapter send
3. E3 记录 outbox
4. E3 接收回复 ingress
5. E3 回写 E1 thread

**行动**：
- [ ] Email adapter 先用 MailHog 或 mock SMTP
- [ ] 实现 outbox 模式
- [ ] 实现 webhook ingress
- [ ] 回写 E1 `/threads/{id}/messages`

**验收标准**：
- 邮件可发送，回复可进入系统

---

#### 任务 24：E1 记录事件流并驱动 replay
**行动**：
- [ ] Event Store 落地数据库
- [ ] 所有状态变更写入 Event
- [ ] `/threads/{id}/events` API
- [ ] Replay UI 消费事件流

**验收标准**：
- Replay 页面能看到完整动作轨迹

---

## Phase E: 补齐 PRD 关键能力（后续）

1. [ ] Shadow / Observe 模式
2. [ ] Bounded Auto 最小预算模型
3. [ ] Relationship template 页面与规则绑定
4. [ ] Kill Switch 的 profile/thread 级真实落地
5. [ ] Summary / analytics / metrics
6. [ ] Integration 监控与异常隔离

---

## 目录重组建议（可选但推荐）

### 当前问题
```
src/
  myproj/          # E1
  policy_control/  # E2
  e5/              # E5
  app/             # E4
  components/      # E4
backend/
  e3/              # E3
```

### 建议重组为
```
apps/
  web/             # E4 (Next.js)
  e1-thread-core/  # E1 (FastAPI)
  e2-policy-control/  # E2 (FastAPI)
  e3-integration-action/  # E3 (FastAPI)
  e5-ai-layer/     # E5 (Fastify)
packages/
  contracts/       # 共享 DTO + OpenAPI
  ui/              # 共享 UI 组件
  shared/          # 共享工具
```

**迁移时机**：Phase A 完成后，Phase B 开始前

---

## 风险与依赖

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| HTML 转义修复遗漏 | 高 | 编写脚本批量修复 + py_compile 全量检查 |
| 内存切数据库引入 regression | 中 | 保留内存服务作为 feature flag，可快速回退 |
| 契约统一需要多端协调 | 中 | 先确定 DTO，各端按 DTO 适配，而不是互相等 |
| E2/E3 修复后仍不可用 | 高 | 先做最小可用，不追求一次性补全功能 |

---

## 完成标准检查清单

### Phase A
- [ ] `npm install` 成功
- [ ] `tsc --noEmit` 成功
- [ ] Python 全仓可 import / compile
- [ ] 顶层 README 能指导启动

### Phase B
- [ ] 四个服务都能启动
- [ ] 每个服务至少有 `/health`
- [ ] 各自单测可执行

### Phase C
- [ ] 前后端不再有双份 thread type
- [ ] create/update/get 的 request/response 统一
- [ ] API mock 由 contract 自动生成或半自动同步

### Phase D
- [ ] 至少 1 条标准线程真实走通
- [ ] replay 能看到动作轨迹
- [ ] takeover 能切断自动推进

---

## 时间估算

| Phase | 时间 | 人数 |
|-------|------|------|
| A: 仓库稳定化 | 1 周 | 1-2 |
| B: 模块可运行化 | 1-2 周 | 2-3 |
| C: 统一契约 | 1 周 | 1-2 |
| D: 打通 MVP | 2-3 周 | 2-3 |
| **总计** | **5-8 周** | - |
