"""代理原生通信控制层 - Thread Core (E1)

主应用入口
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from myproj import __version__
from myproj.config import get_settings
from myproj.api import api_v1_router
from myproj.api.exceptions import register_exception_handlers

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """应用生命周期管理"""
    # 启动
    print(f"Starting {settings.APP_NAME} v{__version__}...")
    print(f"Environment: {settings.APP_ENV}")

    yield

    # 关闭
    print(f"Shutting down {settings.APP_NAME}...")


def create_app() -> FastAPI:
    """创建FastAPI应用"""
    app = FastAPI(
        title="代理原生通信控制层 - Thread Core API",
        description="Thread Engine、Event Store、对象模型等核心模块的REST API",
        version=__version__,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 注册异常处理器
    register_exception_handlers(app)

    # 注册路由
    app.include_router(api_v1_router)

    # 健康检查端点
    @app.get("/health", tags=["health"])
    async def health_check() -> dict:
        """健康检查"""
        return {
            "status": "healthy",
            "version": __version__,
            "environment": settings.APP_ENV,
        }

    @app.get("/", tags=["root"])
    async def root() -> dict:
        """根路径"""
        return {
            "name": settings.APP_NAME,
            "version": __version__,
            "docs": "/docs",
            "health": "/health",
        }

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "myproj.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.is_development,
        log_level=settings.LOG_LEVEL.lower(),
    )
