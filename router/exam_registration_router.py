"""HTTP routes for exam registration."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from db.roles import Permission
from router.dependencies import DatabaseDep, require_permission
from router.error_mapping import raise_http_error
from schemas.schemas import DangKyThi, LopDisplay, MonHocDisplay
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


@router.put("/{malop}/{mamh}/{lan}")
def update(
    malop: str,
    mamh: str,
    lan: int,
    request: DangKyThi,
    db: DatabaseDep,
    user: Annotated[
        dict,
        Depends(require_permission(Permission.UPDATE_EXAM_REGISTRATION)),
    ],
):
    """Update an unused exam registration."""
    try:
        updated = exam_registration_service.update_registration(
            db,
            malop,
            mamh,
            lan,
            request,
            user,
        )
        return exam_registration_service._registration_to_dict(updated)
    except ServiceError as exc:
        raise_http_error(exc)


@router.delete("/{malop}/{mamh}/{lan}")
def delete(
    malop: str,
    mamh: str,
    lan: int,
    db: DatabaseDep,
    user: Annotated[
        dict,
        Depends(require_permission(Permission.DELETE_EXAM_REGISTRATION)),
    ],
):
    """Delete an unused exam registration."""
    try:
        return exam_registration_service.delete_registration(db, malop, mamh, lan, user)
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


@router.get("/lophoc", response_model=list[LopDisplay])
def get_lophoc(
    db: DatabaseDep,
    user: Annotated[
        dict,
        Depends(require_permission(Permission.VIEW_EXAM_REGISTRATION)),
    ],
):
    """Return classes for exam registration."""
    try:
        return exam_registration_service.list_classes(db)
    except ServiceError as exc:
        raise_http_error(exc)


@router.get("/monhoc", response_model=list[MonHocDisplay])
def get_monhoc(
    db: DatabaseDep,
    user: Annotated[
        dict,
        Depends(require_permission(Permission.VIEW_EXAM_REGISTRATION)),
    ],
):
    """Return subjects for exam registration."""
    try:
        return exam_registration_service.list_subjects(db)
    except ServiceError as exc:
        raise_http_error(exc)


@router.get("/api")
def get_registrations(
    db: DatabaseDep,
    user: Annotated[
        dict,
        Depends(require_permission(Permission.VIEW_EXAM_REGISTRATION)),
    ],
    keyword: str | None = None,
):
    """Return exam registrations for the management table."""
    try:
        return exam_registration_service.list_registrations(db, user, keyword)
    except ServiceError as exc:
        raise_http_error(exc)


@router.get("/check-cauhoi")
def check_question_count(
    db: DatabaseDep,
    user: Annotated[
        dict,
        Depends(require_permission(Permission.CREATE_EXAM_REGISTRATION)),
    ],
    mamh: Annotated[str, Query(min_length=1, max_length=5)],
    trinhdo: Annotated[str, Query(pattern="^[ABC]$")],
    socauthi: Annotated[int, Query(ge=10, le=100)],
):
    """Check whether there are enough questions before saving a registration."""
    try:
        return exam_registration_service.check_question_availability(
            db,
            mamh,
            trinhdo,
            socauthi,
        )
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
