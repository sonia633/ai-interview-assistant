"""Authentication API tests."""


def test_register_and_login(client):
    r = client.post(
        "/api/auth/register",
        json={"full_name": "Alice", "email": "alice@example.com", "password": "password1"},
    )
    assert r.status_code == 201, r.text
    assert r.json()["email"] == "alice@example.com"
    assert "hashed_password" not in r.json()

    r = client.post(
        "/api/auth/login",
        json={"email": "alice@example.com", "password": "password1"},
    )
    assert r.status_code == 200
    assert "access_token" in r.json()


def test_duplicate_email_rejected(client):
    payload = {"full_name": "Bob", "email": "bob@example.com", "password": "password1"}
    assert client.post("/api/auth/register", json=payload).status_code == 201
    assert client.post("/api/auth/register", json=payload).status_code == 400


def test_login_wrong_password(client):
    client.post(
        "/api/auth/register",
        json={"full_name": "Carol", "email": "carol@example.com", "password": "password1"},
    )
    r = client.post(
        "/api/auth/login",
        json={"email": "carol@example.com", "password": "wrong"},
    )
    assert r.status_code == 401


def test_me_requires_auth(client):
    assert client.get("/api/auth/me").status_code == 401


def test_me_returns_user(auth_client):
    r = auth_client.get("/api/auth/me")
    assert r.status_code == 200
    assert r.json()["email"] == "test@example.com"
