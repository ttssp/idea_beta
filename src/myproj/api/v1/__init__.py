"""API v1 路由"""

from fastapi import APIRouter

from myproj.api.v1.threads import router as threads_router
from myproj.api.v1.principals import router as principals_router
from myproj.api.v1.relationships import router as relationships_router
from myproj.api.v1.messages import router as messages_router
from myproj.api.v1.events import router as events_router

router = APIRouter(prefix="/api/v1", tags=["v1"])

router.include_router(threads_router)
router.include_router(principals_router)
router.include_router(relationships_router)
router.include_router(messages_router)
router.include_router(events_router)

__all__ = ["router"]
