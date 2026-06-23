"""HTTP routes for exam registration."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from db.roles import Permission
from router.dependencies import DatabaseDep, require_permission
from router.error_mapping import raise_http_error
from schemas.schemas import DangKyThi, MonHocDisplay
from services import exam_registration_service
from services.exceptions import ServiceError

router = APIRouter(prefix="/dangkythi", tags=["DangKyThi"])
templates = Jinja2Templates(directory="templates")


@router.post("", status_code=status.HTTP_201_CREATED)
def create(
    request: DangKyThi,
    db: DatabaseDep,
    user: Annotated[
        dict,
        Depends(require_permission(Permission.CREATE_EXAM_REGISTRATION)),
    ],
):
    """Create an exam registration."""
    try:
        return exam_registration_service.create_registration(db, request, user)
    except ServiceError as exc:
        raise_http_error(exc)


@router.get("", response_class=HTMLResponse)
def read_root(
    request: Request,
    user: Annotated[
        dict,
        Depends(require_permission(Permission.VIEW_EXAM_REGISTRATION)),
    ],
):
    """Render the exam registration page."""
    return templates.TemplateResponse(
        "formDangKyThi.html", {"request": request, "user": user}
    )


@router.get("/monhocdk", response_model=list[MonHocDisplay])
def get_monhoc_dangky(
    magv: str,
    db: DatabaseDep,
    user: Annotated[
        dict,
        Depends(require_permission(Permission.VIEW_EXAM_REGISTRATION)),
    ],
):
    """Return subjects registered by a teacher."""
    try:
        return exam_registration_service.list_registered_subjects(db, magv)
    except ServiceError as exc:
        raise_http_error(exc)


@router.get("/danh-sach", response_class=HTMLResponse)
def get_danh_sach_dk_page(
    request: Request,
    user: Annotated[
        dict,
        Depends(require_permission(Permission.VIEW_EXAM_REGISTRATION)),
    ],
):
    """Render the exam registration report page."""
    return templates.TemplateResponse(
        "formDanhSachDK.html", {"request": request, "user": user}
    )


@router.get("/api/danh-sach-data")
def get_danh_sach_dk_data(
    from_date: str,
    to_date: str,
    db: DatabaseDep,
    user: Annotated[
        dict,
        Depends(require_permission(Permission.VIEW_EXAM_REGISTRATION)),
    ],
):
    """Return exam registrations between two dates."""
    try:
        f_date = from_date.strip() + " 00:00:00"
        t_date = to_date.strip() + " 23:59:59.997"
        return exam_registration_service.list_registrations_in_range(db, f_date, t_date)
    except ServiceError as exc:
        raise_http_error(exc)
