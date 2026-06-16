"""
Login Router Tests Module

Validates the login endpoint response and session cookie behavior.
"""

from unittest.mock import Mock

from fastapi import FastAPI, HTTPException, status
from fastapi.testclient import TestClient
from pytest import MonkeyPatch

from router import user_router


def build_client() -> TestClient:
    """Build a test client with database dependency overridden."""
    app = FastAPI()
    app.include_router(user_router.router)

    def override_get_db():
        yield Mock()

    app.dependency_overrides[user_router.get_db] = override_get_db
    return TestClient(app)


def test_login_endpoint_sets_session_cookie(monkeypatch: MonkeyPatch) -> None:
    """Successful login should set an HTTP-only session cookie."""
    monkeypatch.setattr(
        user_router.db_user,
        "dang_nhap",
        lambda db, request: {"ma": "SV001", "ho": "Nguyen", "ten": "An", "role": "SINHVIEN"},
    )
    monkeypatch.setattr(user_router, "create_session", lambda user_data: "session-123")
    client = build_client()

    response = client.post(
        "/user/login",
        json={"username": "SV001", "password": "123456", "role": "SINHVIEN"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["ma"] == "SV001"
    assert response.json()["role"] == "SINHVIEN"
    assert response.cookies.get("session_id") == "session-123"
    assert "httponly" in response.headers["set-cookie"].lower()


def test_login_endpoint_returns_auth_error_from_business_logic(
    monkeypatch: MonkeyPatch,
) -> None:
    """Login endpoint should forward business logic authentication errors."""
    def raise_login_error(db, request):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"field": "password", "message": "Sai mat khau"},
        )

    monkeypatch.setattr(user_router.db_user, "dang_nhap", raise_login_error)
    client = build_client()

    response = client.post(
        "/user/login",
        json={"username": "SV001", "password": "wrong", "role": "SINHVIEN"},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"]["field"] == "password"
