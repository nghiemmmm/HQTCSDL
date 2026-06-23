"""HTTP routes for login, logout, and account management."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from core.session import create_session, delete_session
from db.roles import Permission
from router.dependencies import (
    CurrentUserDep,
    DatabaseDep,
    require_permission,
)
from router.error_mapping import raise_http_error
from schemas.schemas import DangKy, DangNhap, Message, UserBase
from services import teacher_service, user_service
from services.exceptions import ServiceError

router = APIRouter(prefix="/user", tags=["user"])
templates = Jinja2Templates(directory="templates")


@router.get("/login", response_class=HTMLResponse)
def login(request: Request):
    """Render the login page."""
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login", response_model=UserBase)
def dang_nhap(
    request: DangNhap,
    response: Response,
    db: DatabaseDep,
):
    """Authenticate a user and set the server-side session cookie."""
    try:
        user_data = user_service.login(db, request)
    except ServiceError as exc:
        raise_http_error(exc)

    session_id = create_session(user_data)
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        path="/",
    )
    return user_data


@router.get("/info", response_class=HTMLResponse)
def info(request: Request, user: CurrentUserDep):
    """Render the authenticated user information page."""
    return templates.TemplateResponse(
        "info.html",
        {"request": request, "user": user},
    )


@router.post("/register", response_model=Message)
def dang_ky(
    request: DangKy,
    db: DatabaseDep,
    user: Annotated[dict, Depends(require_permission(Permission.CREATE_USER))],
):
    """Create a system account."""
    del db
    try:
        return user_service.register(request)
    except ServiceError as exc:
        raise_http_error(exc)


@router.get("/register", response_class=HTMLResponse)
def register(
    request: Request,
    db: DatabaseDep,
    user: Annotated[dict, Depends(require_permission(Permission.CREATE_USER))],
):
    """Render the account registration page."""
    try:
        teachers = teacher_service.list_registration_candidates(db)
    except ServiceError as exc:
        raise_http_error(exc)
    return templates.TemplateResponse(
        "register.html",
        {"request": request, "user": user, "giang_viens": teachers},
    )


@router.get("/api/giao-vien")
def get_giao_vien(
    db: DatabaseDep,
    user: Annotated[dict, Depends(require_permission(Permission.VIEW_TEACHER))],
):
    """Return teachers for account registration."""
    try:
        return teacher_service.list_teacher_displays(db)
    except ServiceError as exc:
        raise_http_error(exc)


@router.get("/logout")
def logout(request: Request):
    """Delete the session and redirect to login."""
    session_id = request.cookies.get("session_id")
    if session_id:
        delete_session(session_id)
    response = RedirectResponse(url="/user/login")
    response.delete_cookie("session_id", path="/")
    return response
