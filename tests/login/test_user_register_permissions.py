import pytest
from unittest.mock import Mock
from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from pytest import MonkeyPatch

from router import dependencies, user_router
from db.roles import Permission

def build_client(user_role: str) -> TestClient:
    """Build a test client with get_current_user overridden with a custom role."""
    app = FastAPI()
    app.include_router(user_router.router)

    def override_get_current_user():
        return {"ma": "TESTUSER", "role": user_role}

    def override_get_db():
        yield Mock()

    app.dependency_overrides[dependencies.get_current_user] = override_get_current_user
    app.dependency_overrides[dependencies.get_db] = override_get_db
    return TestClient(app)

def test_giangvien_role_cannot_access_register_page() -> None:
    """A GIANGVIEN user should not be allowed to access the register GET endpoint."""
    client = build_client("GIANGVIEN")
    response = client.get("/user/register")
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "Bạn không có quyền thực hiện chức năng này" in response.json()["detail"]["message"]

def test_giangvien_role_cannot_post_register() -> None:
    """A GIANGVIEN user should not be allowed to call the register POST endpoint to create accounts."""
    client = build_client("GIANGVIEN")
    response = client.post(
        "/user/register",
        json={"loginname": "NEWPGV", "password": "password123", "username": "GV002", "role": "PGV"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "Bạn không có quyền thực hiện chức năng này" in response.json()["detail"]["message"]

def test_giangvien_role_cannot_delete_register() -> None:
    """A GIANGVIEN user should not be allowed to call the register DELETE endpoint to remove accounts."""
    client = build_client("GIANGVIEN")
    response = client.delete("/user/register/ANYUSER")
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "Bạn không có quyền thực hiện chức năng này" in response.json()["detail"]["message"]

def test_pgv_role_can_access_register_page(monkeypatch: MonkeyPatch) -> None:
    """A PGV user should be allowed to access the register GET page."""
    monkeypatch.setattr(user_router.teacher_service, "list_registration_candidates", lambda db: [])
    client = build_client("PGV")
    response = client.get("/user/register")
    assert response.status_code == status.HTTP_200_OK

def test_pgv_role_can_post_register(monkeypatch: MonkeyPatch) -> None:
    """A PGV user should be allowed to register accounts."""
    monkeypatch.setattr(user_router.user_service, "register", lambda req: {"message": "Success"})
    client = build_client("PGV")
    response = client.post(
        "/user/register",
        json={"loginname": "NEWPGV", "password": "password123", "username": "GV002", "role": "PGV"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Success"

def test_pgv_role_can_delete_register(monkeypatch: MonkeyPatch) -> None:
    """A PGV user should be allowed to delete login accounts."""
    monkeypatch.setattr(user_router.user_service, "delete_login_account", lambda db, login, user: {"message": "Deleted"})
    client = build_client("PGV")
    response = client.delete("/user/register/SOMEUSER")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Deleted"
