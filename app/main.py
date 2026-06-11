"""FastAPI application factory and entrypoint."""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.api.routes import admin, auth, dashboard, interviews, pages, resumes
from app.bootstrap import init_db, seed_admin
from app.core.config import settings
from app.core.logging import configure_logging, get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    logger.info("Starting %s (env=%s)", settings.app_name, settings.environment)
    # Ensure schema + admin exist. Alembic is the source of truth in Docker,
    # but create_all keeps local dev frictionless and is idempotent.
    init_db()
    seed_admin()
    yield
    logger.info("Shutting down.")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="1.0.0",
        description="AI-powered platform that helps candidates prepare for job interviews.",
        lifespan=lifespan,
    )

    # Signed session cookies (used by flash messages / CSRF token storage).
    app.add_middleware(SessionMiddleware, secret_key=settings.secret_key, same_site="lax")

    # Static assets
    app.mount("/static", StaticFiles(directory="app/static"), name="static")

    # API routers
    app.include_router(auth.router)
    app.include_router(resumes.router)
    app.include_router(interviews.router)
    app.include_router(dashboard.router)
    app.include_router(admin.router)
    # HTML pages
    app.include_router(pages.router)

    @app.get("/health", tags=["system"])
    def health():
        return {"status": "ok", "app": settings.app_name}

    return app


app = create_app()
