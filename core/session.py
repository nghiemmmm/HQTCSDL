"""
Session store in RAM (in-memory)
Dùng cho FastAPI demo / học tập
KHÔNG dùng production
"""

import time
import uuid
from typing import Dict, Any

# =========================
# SESSION STORAGE (RAM)
# =========================
sessions: Dict[str, Dict[str, Any]] = {}

# =========================
# CONFIG
# =========================
SESSION_EXPIRE_SECONDS = 60 * 60  # 1 giờ


# =========================
# CREATE SESSION
# =========================
def create_session(user: dict) -> str:
    """
    Tạo session mới khi login
    """
    session_id = str(uuid.uuid4())

    sessions[session_id] = {
        "ma": user.get("ma"),
        "role": user.get("role"),
        "created_at": time.time()
    }

    return session_id


# =========================
# GET SESSION
# =========================
def get_session(session_id: str):
    """
    Lấy session từ RAM
    """
    session = sessions.get(session_id)

    if not session:
        return None

    # check expire
    if time.time() - session["created_at"] > SESSION_EXPIRE_SECONDS:
        del sessions[session_id]
        return None

    return session


# =========================
# DELETE SESSION (LOGOUT)
# =========================
def delete_session(session_id: str):
    """
    Xoá session khi logout
    """
    if session_id in sessions:
        del sessions[session_id]


# =========================
# CLEAN EXPIRED SESSIONS
# =========================
def cleanup_sessions():
    """
    Dọn session hết hạn (có thể chạy background task)
    """
    now = time.time()
    expired = []

    for sid, data in sessions.items():
        if now - data["created_at"] > SESSION_EXPIRE_SECONDS:
            expired.append(sid)

    for sid in expired:
        del sessions[sid]