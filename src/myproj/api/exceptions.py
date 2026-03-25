"""API 异常处理"""

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse


class NotFoundError(HTTPException):
    """资源未找到"""

    def __init__(self, detail: str = "Resource not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
        )


class ConflictError(HTTPException):
    """资源冲突"""

    def __init__(self, detail: str = "Resource conflict"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
        )


class ValidationError(HTTPException):
    """验证错误"""

    def __init__(self, detail: str = "Validation error"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
        )


class StateTransitionError(HTTPException):
    """状态流转错误"""

    def __init__(self, detail: str = "Invalid state transition"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
        )


# ============================================
# 异常处理器注册
# ============================================

def register_exception_handlers(app: FastAPI) -> None:
    """注册所有异常处理器"""

    @app.exception_handler(NotFoundError)
    async def not_found_error_handler(request: Request, exc: NotFoundError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": "not_found", "message": exc.detail},
        )

    @app.exception_handler(ConflictError)
    async def conflict_error_handler(request: Request, exc: ConflictError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": "conflict", "message": exc.detail},
        )

    @app.exception_handler(ValidationError)
    async def validation_error_handler(request: Request, exc: ValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": "validation_error", "message": exc.detail},
        )

    @app.exception_handler(StateTransitionError)
    async def state_transition_error_handler(
        request: Request,
        exc: StateTransitionError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": "state_transition_error", "message": exc.detail},
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": "http_error", "message": exc.detail},
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "internal_error", "message": "An unexpected error occurred"},
        )
