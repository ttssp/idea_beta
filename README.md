# 代理原生通信控制层 - Thread Core (E1)

## 概述

这是"代理原生通信控制层"项目的Thread Core模块，由E1工程师负责开发。本模块是整个系统的骨架，提供：

- **Thread Engine**: 线程内核（CRUD、状态机、目标管理、参与者管理）
- **对象模型**: Thread/Principal/Relationship/Message/ThreadEvent/ExternalBinding
- **Event Store**: append-only事件日志
- **数据库基础设施**: Postgres schema + migration
- **基础API**: RESTful接口供其他模块调用

## 技术栈

- **语言**: Python 3.12+
- **Web框架**: FastAPI
- **ORM**: SQLAlchemy 2.0 + Alembic
- **数据库**: PostgreSQL 16+
- **测试**: pytest + pytest-asyncio

## 快速开始

### 1. 环境设置

```bash
# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate  # Windows

# 安装依赖
pip install -e ".[dev]"
```

### 2. 启动数据库

```bash
docker-compose up -d postgres
```

### 3. 运行数据库迁移

```bash
alembic upgrade head
```

### 4. 启动应用

```bash
uvicorn myproj.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. 访问API文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 开发

### 代码质量

```bash
# 格式化
black src/ tests/

# Linting
ruff check src/ tests/
ruff fix src/ tests/

# 类型检查
mypy src/

# 运行测试
pytest
pytest --cov=src  # 带覆盖率
```

### 数据库迁移

```bash
# 创建新迁移
alembic revision --autogenerate -m "description"

# 应用迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

## 项目结构

```
myproj/
├── src/myproj/
│   ├── core/              # 核心领域层
│   │   ├── domain/        # 领域模型
│   │   ├── services/      # 领域服务
│   │   └── repositories/  # 仓储接口
│   ├── infra/             # 基础设施层
│   │   ├── db/            # 数据库
│   │   └── di/            # 依赖注入
│   └── api/               # API层
│       └── v1/            # API v1端点
├── alembic/               # 数据库迁移
├── tests/                 # 测试
└── docs/                  # 文档
```

## API端点

### Thread API
- `POST /api/v1/threads` - 创建线程
- `GET /api/v1/threads` - 查询线程列表
- `GET /api/v1/threads/{id}` - 查询线程详情
- `PATCH /api/v1/threads/{id}` - 更新线程
- `POST /api/v1/threads/{id}/pause` - 暂停线程
- `POST /api/v1/threads/{id}/resume` - 恢复线程
- `POST /api/v1/threads/{id}/takeover` - 接管线程

### Event API
- `GET /api/v1/threads/{id}/events` - 查询线程事件流
- `POST /api/v1/threads/{id}/events` - 写入事件（内部调用）

### Principal & Relationship API
- `POST /api/v1/principals` - 创建主体
- `GET /api/v1/principals/{id}` - 查询主体
- `POST /api/v1/relationships` - 创建关系
- `GET /api/v1/relationships` - 查询关系列表

### Message API
- `POST /api/v1/threads/{id}/messages` - 创建消息
- `GET /api/v1/threads/{id}/messages` - 查询线程消息

## Thread状态机

```
new → planning → active ─┬→ awaiting_external
                        ├→ awaiting_approval
                        ├→ blocked
                        ├→ paused
                        ├→ escalated
                        ├→ completed
                        └→ cancelled
```

10种状态：`new`, `planning`, `active`, `awaiting_external`, `awaiting_approval`, `blocked`, `paused`, `escalated`, `completed`, `cancelled`

## 质量要求

- 核心状态机单元测试覆盖率 ≥ 95%
- Event Store写入保证exactly-once
- Thread查询API P99 < 200ms
- 数据库migration支持前向/回滚

## License

Proprietary
