from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from app.exceptions.auth_exception import (
    ForbiddenError, InvalidCredentialsError,
    InvalidTokenError
)
from app.exceptions.common import *
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.schemas.common import ErrorResponse


def _error_response(code: str, message: str, status_code: int, details: dict | None = None) -> JSONResponse:
    body = ErrorResponse(code=code, message=message, details=details)
    return JSONResponse(status_code=status_code, content=body.model_dump())


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(NotFoundError)
    async def handle_not_found(request: Request, exc: NotFoundError):
        return _error_response("not_found", str(exc), status.HTTP_404_NOT_FOUND)

    @app.exception_handler(ConflictError)
    async def handle_conflict(request: Request, exc: ConflictError):
        return _error_response("conflict", str(exc), status.HTTP_409_CONFLICT)

    @app.exception_handler(ValidationAppError)
    async def handle_validation(request: Request, exc: ValidationAppError):
        return _error_response("validation_error", str(exc), status.HTTP_400_BAD_REQUEST)

    @app.exception_handler(InvalidCredentialsError)
    async def handle_invalid_credentials(request: Request, exc: InvalidCredentialsError):
        return _error_response("invalid_credentials", str(exc), status.HTTP_401_UNAUTHORIZED)

    @app.exception_handler(InvalidTokenError)
    async def handle_invalid_token(request: Request, exc: InvalidTokenError):
        return _error_response("invalid_token", str(exc), status.HTTP_401_UNAUTHORIZED)

    @app.exception_handler(ForbiddenError)
    async def handle_forbidden(request: Request, exc: ForbiddenError):
        return _error_response("forbidden", str(exc), status.HTTP_403_FORBIDDEN)

    @app.exception_handler(ValueError)
    async def handle_value_error(request: Request, exc: ValueError):
        return _error_response("invalid_input", str(exc), status.HTTP_400_BAD_REQUEST)

    @app.exception_handler(RequestValidationError)
    async def handle_pydantic_validation(
        request: Request,
        exc: RequestValidationError,
    ):
        return _error_response(
            "invalid_input",
            "Request validation failed",
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            details={
                "errors": jsonable_encoder(exc.errors()),
            },
        )

    @app.exception_handler(IntegrityError)
    async def handle_integrity_error(request: Request, exc: IntegrityError):
        return _error_response(
            "conflict",
            "This operation violates a database constraint (e.g. a duplicate value).",
            status.HTTP_409_CONFLICT
        )
    
    @app.exception_handler(StarletteHTTPException)
    async def handle_raw_http_exception(request: Request, exc: StarletteHTTPException):

        return _error_response(
            code="http_error",
            message=str(exc.detail),
            status_code=exc.status_code,
        )