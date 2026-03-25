# 代理原生通信控制层 - 前端 (E4)

这是"代理原生通信控制层"项目的前端部分，由 E4（前端工程师 - Control Surface）负责开发。

## 项目概述
本项目是一个以"目标推进状态"为中心的通信控制界面，而非简单的聊天应用。用户在这里进行"审批、接管、放权"，建立对代理的信任。

## 技术栈

- **框架**: Next.js 15 (App Router)
- **语言**: TypeScript 5.6+
- **状态管理**: Zustand + React Query
- **UI组件库**: shadcn/ui + Tailwind CSS
- **表单**: React Hook Form + Zod
- **实时通信**: SSE (Server-Sent Events)
- **测试**: Vitest + Testing Library + Playwright

## 快速开始

### 前置要求

- Node.js >= 20.0.0
- npm 或 yarn

### 安装依赖

```bash
npm install
```

### 开发模式

```bash
npm run dev
```

访问 [http://localhost:3000](http://localhost:3000) 查看应用。

### 构建

```bash
npm run build
npm start
```

## 项目结构

```
src/
├── app/                    # Next.js App Router
│   ├── (app)/           # 主应用路由组
│   │   ├── page.tsx       # Thread Inbox (首页)
│   │   ├── threads/       # 线程相关页面
│   │   ├── approvals/     # 审批中心
│   │   ├── replay/        # 回放中心
│   │   └── settings/     # 设置页面
│   └── layout.tsx
├── components/
│   ├── ui/              # shadcn/ui 基础组件
│   ├── common/           # 通用业务组件
│   ├── thread/           # 线程相关组件
│   ├── approval/         # 审批相关组件
│   ├── replay/           # 回放相关组件
│   ├── delegation/       # 委托相关组件
│   └── layout/         # 布局组件
├── lib/
│   ├── api/            # API 客户端
│   ├── hooks/          # 自定义 hooks
│   ├── store/          # Zustand 状态管理
│   ├── types/          # TypeScript 类型定义
│   ├── utils/          # 工具函数
│   └── sse/            # SSE 实时通信
├── mocks/              # Mock 数据
└── styles/             # 全局样式
```

## 核心页面

1. **Thread Inbox** (`/`) - 工作队列视图，5种分组展示线程
2. **Thread Detail** (`/threads/[id]`) - 线程详情页面
3. **Approval Center** (`/approvals`) - 审批中心
4. **Replay Center** (`/replay`) - 回放中心
5. **Settings** (`/settings/delegation`) - 委托档位管理

## 开发计划

### Phase 0: 项目初始化与基础搭建 (Week 0-2) ✅
- [x] 初始化 Next.js + TypeScript 项目
- [x] 配置 Tailwind CSS + shadcn/ui
- [x] 搭建基础项目目录结构
- [x] 定义核心 TypeScript 类型
- [x] 创建通用组件库初始化
- [x] 搭建 Mock API 层
- [x] App Shell 布局
- [x] 核心页面线框图

### Phase 1A: 核心页面骨架 (Week 3-5)
- [ ] Thread Inbox 页面完善
- [ ] Thread 创建流程
- [ ] Thread Detail 页面完善
- [ ] Approval Center 页面完善
- [ ] SSE 实时推送接入

### Phase 1B-3: 后续开发
详见 `engineering_dev_plans_E4_v1.md

## 命令

```bash
npm run dev          # 开发模式
npm run build        # 构建
npm run lint         # 代码检查
npm run typecheck    # 类型检查
npm run test         # 单元测试
npm run test:e2e    # E2E 测试
```

## 相关文档

- `engineering_dev_plans_E4_v1.md - E4 详细开发计划
- agent_native_comm_control_PRD_Blueprint_RnDPlan_v1.md - 产品 PRD 和技术蓝图
