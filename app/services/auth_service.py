"""Authentication / registration service."""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.schemas.user import UserCreate


class AuthError(Exception):
    """Raised on registration/login failures."""


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.users = UserRepository(db)

    def register(self, data: UserCreate, is_admin: bool = False) -> User:
        if self.users.get_by_email(data.email):
            raise AuthError("A user with this email already exists.")
        user = User(
            full_name=data.full_name.strip(),
            email=data.email.lower(),
            hashed_password=hash_password(data.password),
            is_admin=is_admin,
        )
        return self.users.add(user)

    def authenticate(self, email: str, password: str) -> User:
        user = self.users.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise AuthError("Invalid email or password.")
        if not user.is_active:
            raise AuthError("This account is disabled.")
        return user

    def login_token(self, email: str, password: str) -> str:
        user = self.authenticate(email, password)
        return create_access_token(user.id, extra={"is_admin": user.is_admin})
