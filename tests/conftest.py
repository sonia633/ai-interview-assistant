"""Pytest fixtures: file-backed SQLite app + a transport-agnostic client.

We point the application at a temporary SQLite file *before* importing it,
then reuse the application's own engine so the request handlers and the
test setup share one database.

The HTTP client wraps httpx's ``ASGITransport`` directly (driven through a
private event loop) instead of Starlette's ``TestClient``. This keeps the
suite working across Starlette versions whose TestClient/httpx integration
is in flux, while exercising the real ASGI app.
"""
import asyncio
import os
import tempfile

# Configure environment BEFORE importing the app/settings (settings is cached).
_DB_FD, _DB_PATH = tempfile.mkstemp(suffix=".db")
os.close(_DB_FD)
os.environ["DATABASE_URL"] = f"sqlite+pysqlite:///{_DB_PATH}"
os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("JWT_SECRET_KEY", "test-jwt-secret")

import pytest
from httpx import ASGITransport, AsyncClient

import app.models  # noqa: F401  (register ORM models on Base.metadata first)
from app.core.database import Base, engine
from app.main import app as fastapi_app  # alias avoids shadowing by `import app.models`


class SyncClient:
    """Minimal synchronous facade over an async httpx client.

    Cookies persist across calls (so login -> authenticated requests work),
    mirroring how a browser session behaves.
    """

    def __init__(self) -> None:
        self._loop = asyncio.new_event_loop()
        self._client = AsyncClient(
            transport=ASGITransport(app=fastapi_app), base_url="http://testserver"
        )

    def _run(self, coro):
        return self._loop.run_until_complete(coro)

    def get(self, url, **kw):
        return self._run(self._client.get(url, **kw))

    def post(self, url, **kw):
        return self._run(self._client.post(url, **kw))

    def patch(self, url, **kw):
        return self._run(self._client.patch(url, **kw))

    def close(self):
        self._run(self._client.aclose())
        self._loop.close()


@pytest.fixture(autouse=True)
def _fresh_schema():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture
def client():
    c = SyncClient()
    try:
        yield c
    finally:
        c.close()


@pytest.fixture
def auth_client(client):
    """A client with a registered + logged-in user (auth cookie set)."""
    client.post(
        "/api/auth/register",
        json={"full_name": "Test User", "email": "test@example.com", "password": "secret123"},
    )
    client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "secret123"},
    )
    return client


def pytest_sessionfinish(session, exitstatus):
    try:
        os.remove(_DB_PATH)
    except OSError:
        pass
