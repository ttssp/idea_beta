
"""
E3: Integration & Action API - Main Application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .config import settings
from .core.database import init_db, close_db
from .core.redis import close_redis
from .api.v1 import actions, messages, ingress, delivery


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动
    await init_db()
    yield
    # 关闭
    await close_db()
    await close_redis()


# 创建FastAPI应用
app = FastAPI(
    title=settings.api_title,
    description="代理原生通信控制层 - 外部集成与动作执行API",
    version=settings.api_version,
    lifespan=lifespan
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 健康检查
@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy", "service": "e3-integration-action"}


@app.get("/")
async def root():
    """根路径"""
    return {
        "service": settings.api_title,
        "version": settings.api_version,
        "docs": "/docs"
    }


# 注册路由
api_prefix = settings.api_prefix
app.include_router(actions.router, prefix=api_prefix)
app.include_router(messages.router, prefix=api_prefix)
app.include_router(ingress.router, prefix=api_prefix)
app.include_router(delivery.router, prefix=api_prefix)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

