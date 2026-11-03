import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.session import Base, get_db
from app.models.user import User
from app.models.url import URLMapping
from app.security.rate_limiter import limiter

# In-memory test SQLite engine
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    limiter.clear()
    yield
    Base.metadata.drop_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"


def test_auth_registration_and_login_flow():
    # 1. Register
    reg_payload = {
        "email": "security.anuj@example.com",
        "password": "StrongPassword2026!",
        "full_name": "Anuj Security"
    }
    reg_res = client.post("/api/v1/auth/register", json=reg_payload)
    assert reg_res.status_code == 201
    data = reg_res.json()
    assert "access_token" in data
    assert data["user"]["email"] == "security.anuj@example.com"
    token = data["access_token"]

    # 2. Get profile with token
    me_res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "security.anuj@example.com"

    # 3. Login with credentials
    login_payload = {
        "email": "security.anuj@example.com",
        "password": "StrongPassword2026!"
    }
    login_res = client.post("/api/v1/auth/login", json=login_payload)
    assert login_res.status_code == 200
    assert "access_token" in login_res.json()

    # 4. Login with bad password -> 401
    bad_login = client.post("/api/v1/auth/login", json={
        "email": "security.anuj@example.com",
        "password": "WrongPassword!"
    })
    assert bad_login.status_code == 401


def test_ssrf_blocking_on_shorten():
    payload = {
        "long_url": "http://127.0.0.1:8080/admin",
        "custom_alias": "ssrf-test"
    }
    res = client.post("/api/v1/shorten", json=payload)
    assert res.status_code == 400
    assert "SSRF" in res.json()["detail"]


def test_javascript_protocol_blocking():
    payload = {
        "long_url": "javascript:alert(1)"
    }
    res = client.post("/api/v1/shorten", json=payload)
    assert res.status_code == 400
    assert "protocols are permitted" in res.json()["detail"]


def test_analytics_ownership_protection():
    # 1. Create User A
    user_a = client.post("/api/v1/auth/register", json={
        "email": "usera@example.com",
        "password": "PasswordUserA1!",
        "full_name": "User A"
    }).json()
    token_a = user_a["access_token"]

    # 2. Create User B
    user_b = client.post("/api/v1/auth/register", json={
        "email": "userb@example.com",
        "password": "PasswordUserB1!",
        "full_name": "User B"
    }).json()
    token_b = user_b["access_token"]

    # 3. User A shortens a link
    short_res = client.post(
        "/api/v1/shorten",
        json={"long_url": "https://example.com/protected-article"},
        headers={"Authorization": f"Bearer {token_a}"}
    )
    assert short_res.status_code == 201
    code = short_res.json()["short_code"]

    # 4. User A can view their stats
    stats_a = client.get(f"/api/v1/stats/{code}", headers={"Authorization": f"Bearer {token_a}"})
    assert stats_a.status_code == 200
    assert stats_a.json()["short_code"] == code

    # 5. User B attempts to access User A's stats -> 403 Forbidden!
    stats_b = client.get(f"/api/v1/stats/{code}", headers={"Authorization": f"Bearer {token_b}"})
    assert stats_b.status_code == 403
    assert "Access forbidden" in stats_b.json()["detail"]

    # 6. Anonymous caller attempts to access User A's stats -> 401 Unauthorized!
    stats_anon = client.get(f"/api/v1/stats/{code}")
    assert stats_anon.status_code == 401

