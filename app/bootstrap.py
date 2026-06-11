"""Startup helpers: ensure tables exist and seed the first admin user."""
from __future__ import annotations

from sqlalchemy import select

from app.core.config import settings
from app.core.database import Base, SessionLocal, engine
from app.core.logging import get_logger
from app.core.security import hash_password
from app.models.user import User

logger = get_logger(__name__)


def init_db() -> None:
    """Create tables if Alembic hasn't run (e.g. local non-docker dev)."""
    Base.metadata.create_all(bind=engine)


def seed_admin() -> None:
    with SessionLocal() as db:
        existing = db.scalars(
            select(User).where(User.email == settings.first_admin_email.lower())
        ).first()
        if existing:
            return
        admin = User(
            full_name="Administrator",
            email=settings.first_admin_email.lower(),
            hashed_password=hash_password(settings.first_admin_password),
            is_admin=True,
        )
        db.add(admin)
        db.commit()
        logger.info("Seeded admin account: %s", admin.email)
