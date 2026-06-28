"""HTTP routes for exam participation, history, autosave, and submission."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import HTMLResponse
from core.templates import Jinja2Templates

from db.roles import Permission
from router.dependencies import DatabaseDep, require_any_permission, require_permission
from router.error_mapping import raise_http_error
from schemas.schemas import (
    AutoSaveRequest,
    BaiNopRequest,
    LopDisplay,
    MonHocDisplay,
    ThongTinThi,
    StudentShortResponse,
    TraCuuBaiThiResponse,
    BangDiemMonHocResponse,
)
from services import exam_service
from services.exceptions import ServiceError

router = APIRouter(prefix="/thi", tags=["Thi"])
templates = Jinja2Templates(directory="templates")

ExamUserDep = Annotated[
    dict,
    Depends(
        require_any_permission(
            Permission.TAKE_EXAM,
            Permission.PRACTICE_EXAM,
        )
    ),
]


@router.get("/", response_class=HTMLResponse)
def read_root(request: Request, user: ExamUserDep):
    """Render the exam selection page."""
    return templates.TemplateResponse(
        "formBatDauThi.html",
        {"request": request, "user": user},
    )


@router.get("/lam-bai", response_class=HTMLResponse)
def lam_bai_thi(request: Request, user: ExamUserDep):
    """Render the exam-taking page."""
    return templates.TemplateResponse(
        "formThi.html",
        {"request": request, "user": user},
    )


@router.get("/lich-su", response_class=HTMLResponse)
def lich_su_thi(
    request: Request,
    db: DatabaseDep,
    user: Annotated[dict, Depends(require_permission(Permission.VIEW_OWN_EXAM))],
):
    """Render the current student's exam history."""
    try:
        context = exam_service.build_history(db, user)
    except ServiceError as exc:
        raise_http_error(exc)
    return templates.TemplateResponse(
        "lichSuThi.html",
        {"request": request, "user": user, **context},
    )


@router.get("/xem-lai", response_class=HTMLResponse)
def xem_lai_bai_thi(
    request: Request,
    db: DatabaseDep,
    user: Annotated[
        dict,
        Depends(
            require_any_permission(
                Permission.VIEW_OWN_EXAM,
                Permission.VIEW_STUDENT_EXAM,
            )
        ),
    ],
    session_id: Annotated[int | None, Query()] = None,
):
    """Render a submitted exam review."""
    try:
        context = exam_service.build_review(db, user, session_id)
    except ServiceError as exc:
        raise_http_error(exc)
    return templates.TemplateResponse(
        "xemLaiThi.html",
        {"request": request, "user": user, **context},
    )


@router.get("/diem", response_class=HTMLResponse)
def diem_thi(
    request: Request,
    db: DatabaseDep,
    user: Annotated[dict, Depends(require_permission(Permission.VIEW_OWN_SCORE))],
):
    """Render the student's personal scores page."""
    try:
        context = exam_service.build_student_scores(db, user)
    except ServiceError as exc:
        raise_http_error(exc)
    return templates.TemplateResponse(
        "formDiemThiCaNhan.html",
        {"request": request, "user": user, **context},
    )


@router.get("/ket-qua", response_class=HTMLResponse)
def ket_qua_sinh_vien(
    request: Request,
    db: DatabaseDep,
    user: Annotated[
        dict,
        Depends(require_permission(Permission.VIEW_STUDENT_SCORE)),
    ],
):
    """Render the student-result query page."""
    try:
        classes = exam_service.list_all_classes(db, user)
        subjects = exam_service.list_all_subjects(db, user)
    except ServiceError as exc:
        raise_http_error(exc)
    return templates.TemplateResponse(
        "formKetQua.html",
        {
            "request": request,
            "user": user,
            "classes": classes,
            "subjects": subjects,
        },
    )


@router.get("/bang-diem", response_class=HTMLResponse)
def bang_diem(
    request: Request,
    db: DatabaseDep,
    user: Annotated[
        dict,
        Depends(require_permission(Permission.PRINT_SCORE_TABLE)),
    ],
):
    """Render the class scoreboard print page."""
    try:
        classes = exam_service.list_all_classes(db, user)
        subjects = exam_service.list_all_subjects(db, user)
    except ServiceError as exc:
        raise_http_error(exc)
    return templates.TemplateResponse(
        "formBangDiem.html",
        {
            "request": request,
            "user": user,
            "classes": classes,
            "subjects": subjects,
        },
    )


@router.get("/api/sinhvien-by-lop", response_model=list[StudentShortResponse])
def get_sinhvien_by_lop(
    malop: str,
    db: DatabaseDep,
    user: Annotated[dict, Depends(require_permission(Permission.VIEW_STUDENT))],
):
    """Return short student list for a class."""
    try:
        return exam_service.list_students_by_class(db, malop)
    except ServiceError as exc:
        raise_http_error(exc)


@router.get("/api/tra-cuu-bai-thi", response_model=TraCuuBaiThiResponse)
def tra_cuu_bai_thi(
    masv: str,
    mamh: str,
    lan: int,
    db: DatabaseDep,
    user: Annotated[dict, Depends(require_permission(Permission.VIEW_STUDENT_SCORE))],
):
    """Look up student exam result details."""
    try:
        return exam_service.lookup_exam_result(db, masv, mamh, lan)
    except ServiceError as exc:
        raise_http_error(exc)


@router.get("/api/bang-diem-data", response_model=BangDiemMonHocResponse)
def bang_diem_data(
    malop: str,
    mamh: str,
    lan: int,
    db: DatabaseDep,
    user: Annotated[dict, Depends(require_permission(Permission.PRINT_SCORE_TABLE))],
):
    """Return scores sheet data for a class."""
    try:
        students_data = exam_service.get_class_score_table(db, malop, mamh, lan, user)
        from schemas.schemas import BangDiemMonHocPublic
        mapped_students = []
        for s in students_data:
            mapped_students.append(
                BangDiemMonHocPublic(
                    stt=s["stt"],
                    masv=s["masv"],
                    ho=s["ho"],
                    ten=s["ten"],
                    diem=s["diem"],
                    diem_chu=s["diem_chu"],
                    diem_chu_viet=s["diem_chu_viet"]
                )
            )
        return BangDiemMonHocResponse(students=mapped_students)
    except ServiceError as exc:
        raise_http_error(exc)


@router.get("/api/danh-sach-ky-thi-gv")
def danh_sach_ky_thi_gv(
    db: DatabaseDep,
    user: Annotated[dict, Depends(require_permission(Permission.PRINT_SCORE_TABLE))],
):
    """Return all exam registrations for the current teacher, newest first."""
    try:
        data = exam_service.list_teacher_registrations(db, user)
        return {"registrations": data}
    except ServiceError as exc:
        raise_http_error(exc)


@router.get("/api/ket-qua-ky-thi")
def ket_qua_ky_thi(
    malop: str,
    mamh: str,
    lan: int,
    db: DatabaseDep,
    user: Annotated[dict, Depends(require_permission(Permission.VIEW_STUDENT_SCORE))],
):
    """Return all student results for a specific exam (malop, mamh, lan)."""
    try:
        results = exam_service.list_class_exam_results(db, malop, mamh, lan, user)
        return {"students": results}
    except ServiceError as exc:
        raise_http_error(exc)


@router.post("/nhanLop", response_model=LopDisplay)
def nhap_lop(
    masv: str,
    db: DatabaseDep,
    user: ExamUserDep,
):
    """Return a student's assigned class."""
    try:
        return exam_service.get_student_class(db, masv, user)
    except ServiceError as exc:
        raise_http_error(exc)


@router.get("/monhoc-duoc-thi", response_model=list[MonHocDisplay])
def mon_hoc_duoc_thi(db: DatabaseDep, user: ExamUserDep):
    """Return subjects available to the current exam actor."""
    try:
        return exam_service.list_available_subjects(db, user)
    except ServiceError as exc:
        raise_http_error(exc)


@router.get("/lich-thi-cua-toi")
def lich_thi_cua_toi(
    db: DatabaseDep,
    user: Annotated[dict, Depends(require_permission(Permission.TAKE_EXAM))],
):
    """Return exam schedules for the logged-in student."""
    try:
        return exam_service.list_student_exam_schedules(db, user)
    except ServiceError as exc:
        raise_http_error(exc)


@router.get("/lophoc-duoc-thi", response_model=list[LopDisplay])
def lop_hoc_duoc_thi(db: DatabaseDep, user: ExamUserDep):
    """Return classes available to the current exam actor for practice."""
    try:
        return exam_service.list_available_classes(db, user)
    except ServiceError as exc:
        raise_http_error(exc)


@router.get("/layTTThi", response_model=ThongTinThi)
def lay_thong_tin_thi(
    mamonhoc: str,
    lanthi: int,
    malop: str,
    ngaythi: str,
    db: DatabaseDep,
    user: ExamUserDep,
):
    """Return validated exam registration information."""
    try:
        return exam_service.get_exam_info(
            db,
            mamonhoc,
            lanthi,
            malop,
            ngaythi,
            user,
        )
    except ServiceError as exc:
        raise_http_error(exc)


@router.get("/cau-hoi")
def lay_cau_hoi_thi(
    mamonhoc: str,
    lanthi: int,
    malop: str,
    ngaythi: str,
    db: DatabaseDep,
    user: ExamUserDep,
):
    """Resume or create an exam and return its questions."""
    try:
        return exam_service.get_or_create_exam(
            db,
            mamonhoc,
            lanthi,
            malop,
            ngaythi,
            user,
        )
    except ServiceError as exc:
        raise_http_error(exc)


@router.post("/autosave")
def autosave_bai_thi(
    request: AutoSaveRequest,
    db: DatabaseDep,
    user: Annotated[dict, Depends(require_permission(Permission.TAKE_EXAM))],
):
    """Autosave an active exam session."""
    try:
        return exam_service.autosave(db, request, user)
    except ServiceError as exc:
        raise_http_error(exc)


@router.post("/nop-bai")
def nop_bai_thi(
    request: BaiNopRequest,
    db: DatabaseDep,
    user: ExamUserDep,
):
    """Grade and submit an official exam."""
    try:
        return exam_service.submit(db, request, user)
    except ServiceError as exc:
        raise_http_error(exc)
