import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.api.routes import analytics, assessment, assignments, auth, curriculum, gamification, learning, recommendations, tutor, users
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.core.middleware import RateLimitMiddleware, RequestLoggingMiddleware
from app.db.session import engine

settings = get_settings()
configure_logging()
app = FastAPI(title="AdaptiveAI API", version="0.1.0")
logger = logging.getLogger("adaptiveai.error")
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RateLimitMiddleware, requests_per_minute=settings.rate_limit_requests_per_minute)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "PUT", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(curriculum.router, prefix="/api/v1")
app.include_router(learning.router, prefix="/api/v1")
app.include_router(tutor.router, prefix="/api/v1")
app.include_router(assessment.router, prefix="/api/v1")
app.include_router(recommendations.router, prefix="/api/v1")
app.include_router(gamification.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")
app.include_router(assignments.router, prefix="/api/v1")


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, error: Exception) -> JSONResponse:
    logger.exception("Unhandled request error method=%s path=%s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/health", tags=["operations"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready", tags=["operations"], response_model=None)
def readiness_check() -> dict[str, str] | JSONResponse:
    """Verify that the API can reach its required persistent store."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError:
        logger.warning("Readiness check failed because the database is unavailable")
        return JSONResponse(status_code=503, content={"status": "unavailable"})
    return {"status": "ready"}
