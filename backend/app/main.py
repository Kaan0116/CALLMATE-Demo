"""
CallMate AI - FastAPI Application Entry Point
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import structlog

from prometheus_fastapi_instrumentator import Instrumentator
from app.core.config import get_settings
from app.api.routes import auth, calls, analysis, reports, websocket_routes
from app.db.redis_client import close_redis

log = structlog.get_logger()
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("startup", env=settings.app_env)
    # Pre-warm AI models in background (optional - lazy loading is default)
    yield
    await close_redis()
    log.info("shutdown")


app = FastAPI(
    title="CallMate AI",
    description="Real-time AI analysis platform for call centers",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# Middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus metrics — /metrics endpoint
Instrumentator().instrument(app).expose(app)

# Routers
app.include_router(auth.router, prefix="/api")
app.include_router(calls.router, prefix="/api")
app.include_router(analysis.router, prefix="/api")
app.include_router(reports.router, prefix="/api")
app.include_router(websocket_routes.router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "CallMate AI", "version": "1.0.0"}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    log.error("unhandled_exception", path=request.url.path, error=str(exc))
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
