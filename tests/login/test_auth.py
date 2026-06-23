"""
Authentication Dependency Tests Module

Validates session authentication and role permission checks.
"""

import pytest
from fastapi import HTTPException, status
from pytest import MonkeyPatch
from starlette.requests import Request

from router import dependencies as auth
from db.roles import Permission


def make_request(cookie: str | None = None) -> Request:
    """Build a Starlette request with an optional cookie header."""
    headers = []
    if cookie:
        headers.append((b"cookie", cookie.encode()))
    return Request({"type": "http", "headers": headers})


def test_get_current_user_raises_when_cookie_is_missing() -> None:
    """Missing session cookie should raise an unauthorized error."""
    with pytest.raises(HTTPException) as exc_info:
        auth.get_current_user(make_request())

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_current_user_raises_when_session_is_invalid(
    monkeypatch: MonkeyPatch,
) -> None:
    """Invalid session cookie should raise an unauthorized error."""
    monkeypatch.setattr(auth, "get_session", lambda session_id: None)

    with pytest.raises(HTTPException) as exc_info:
        auth.get_current_user(make_request("session_id=invalid"))

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_current_user_returns_session_user(monkeypatch: MonkeyPatch) -> None:
    """Valid session cookie should return the session user."""
    user = {"ma": "SV001", "role": "SINHVIEN"}
    monkeypatch.setattr(auth, "get_session", lambda session_id: user)

    assert auth.get_current_user(make_request("session_id=valid")) == user


def test_require_permission_allows_role_with_permission() -> None:
    """A role with the required permission should pass the checker."""
    checker = auth.require_permission(Permission.CREATE_USER)

    assert checker({"ma": "PGV001", "role": "PGV"})["role"] == "PGV"


def test_require_permission_rejects_role_without_permission() -> None:
    """A role without the required permission should raise forbidden."""
    checker = auth.require_permission(Permission.CREATE_USER)

    with pytest.raises(HTTPException) as exc_info:
        checker({"ma": "SV001", "role": "SINHVIEN"})

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN


def test_require_any_permission_allows_one_matching_permission() -> None:
    """A role with one of the accepted permissions should pass."""
    checker = auth.require_any_permission(Permission.TAKE_EXAM, Permission.PRACTICE_EXAM)

    assert checker({"ma": "GV001", "role": "GIANGVIEN"})["role"] == "GIANGVIEN"


def test_require_any_permission_rejects_when_no_permission_matches() -> None:
    """A role without any accepted permission should raise forbidden."""
    checker = auth.require_any_permission(Permission.TAKE_EXAM, Permission.PRACTICE_EXAM)

    with pytest.raises(HTTPException) as exc_info:
        checker({"ma": "PGV001", "role": "PGV"})

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
