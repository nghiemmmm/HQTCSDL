"""
Session Tests Module

Validates in-memory login session lifecycle behavior.
"""

import time

from pytest import MonkeyPatch

from core import session as session_store


def setup_function() -> None:
    """Clear in-memory sessions before each test."""
    session_store.sessions.clear()


def test_create_session_stores_user_identity_without_password() -> None:
    """Create session should store identity fields without sensitive data."""
    session_id = session_store.create_session(
        {"ma": "SV001", "role": "SINHVIEN", "password": "secret"}
    )

    stored_session = session_store.sessions[session_id]

    assert stored_session["ma"] == "SV001"
    assert stored_session["role"] == "SINHVIEN"
    assert "created_at" in stored_session
    assert "password" not in stored_session


def test_get_session_returns_existing_session() -> None:
    """Existing session ID should return stored user data."""
    session_id = session_store.create_session({"ma": "GV001", "role": "GIANGVIEN"})

    assert session_store.get_session(session_id)["ma"] == "GV001"


def test_get_session_returns_none_for_missing_session() -> None:
    """Unknown session ID should return None."""
    assert session_store.get_session("missing-session") is None


def test_get_session_removes_expired_session(monkeypatch: MonkeyPatch) -> None:
    """Expired session should be removed and return None."""
    session_id = session_store.create_session({"ma": "SV001", "role": "SINHVIEN"})
    expired_at = time.time() + session_store.SESSION_EXPIRE_SECONDS + 1
    monkeypatch.setattr(session_store.time, "time", lambda: expired_at)

    assert session_store.get_session(session_id) is None
    assert session_id not in session_store.sessions


def test_delete_session_removes_existing_session() -> None:
    """Delete session should remove an existing session ID."""
    session_id = session_store.create_session({"ma": "SV001", "role": "SINHVIEN"})

    session_store.delete_session(session_id)

    assert session_id not in session_store.sessions
