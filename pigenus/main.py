import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pigenus.core.config import get_settings
from pigenus.core.logging import setup_logging
from pigenus.db.init_db import init_db
from pigenus.api.router import api_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    setup_logging(settings.log_level)
    logger.info("PiGenus starting up - version %s", settings.version)
    try:
        init_db()
    except Exception as e:
        logger.error("Failed to initialize database: %s", e)
    try:
        from pigenus.scheduler.nightly import start_scheduler
        start_scheduler()
    except Exception as e:
        logger.error("Failed to start scheduler: %s", e)
    yield
    try:
        from pigenus.scheduler.nightly import stop_scheduler
        stop_scheduler()
    except Exception as e:
        logger.error("Error stopping scheduler: %s", e)
    logger.info("PiGenus shutting down.")


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="PiGenus",
        description="Private Raspberry Pi Orchestration Core",
        version=settings.version,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def logging_middleware(request: Request, call_next):
        logger.info("Request: %s %s", request.method, request.url.path)
        response = await call_next(request)
        logger.info("Response: %s %s -> %d", request.method, request.url.path, response.status_code)
        return response

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        logger.exception("Unhandled exception: %s", exc)
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

    app.include_router(api_router, prefix="/api/v1")
    return app


app = create_app()
