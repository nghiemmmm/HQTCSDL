from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse
from core.templates import Jinja2Templates
from core.session import create_session
from sqlalchemy.orm.session import Session
from sqlalchemy import text
from schemas.schemas import UserBase, DangNhap, UserBase, DangKy
from db.database import get_db
from db import db_user
from db import db_giaovien 
from db.model import DbGiaoVien, DbSinhVien, DbLop
from core.session import delete_session
from core.auth import get_current_user, require_permission
from db.roles import Permission
from fastapi import Request
from fastapi.responses import RedirectResponse
router = APIRouter(
    prefix = "/user",
    tags= ["user"]
)
templates = Jinja2Templates(directory="templates")

@router.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login", response_model=UserBase)
def dangNhap(request: DangNhap, response: Response, db: Session = Depends(get_db)):
    """
    Tạo thông tin người dùng vào CSDL
    """
    user_data = db_user.dang_nhap(db=db, request=request)
    session_id = create_session(user_data)
    print("Session ID:", session_id)  # In session_id để kiểm tra

    # Set cookie on injected Response (FastAPI will send it with the response)
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        path='/'
    )
    return user_data
def _value(value):
    return (value or "").strip() if isinstance(value, str) else value


def _build_user_profile(db: Session, user: dict) -> dict:
    role = user.get("role")
    code = _value(user.get("ma"))
    profile = {
        "ma": code or "N/A",
        "role": role or "N/A",
        "hoten": _value(" ".join(filter(None, [user.get("ho"), user.get("ten")]))),
        "sodt": "",
        "diachi": "",
        "ngaysinh": "",
        "lop": "",
    }

    if role == "GIANGVIEN":
        teacher = db.query(DbGiaoVien).filter(DbGiaoVien.magv == code).first()
        if teacher:
            profile.update({
                "hoten": _value(f"{_value(teacher.ho)} {_value(teacher.ten)}"),
                "sodt": _value(teacher.sodtll),
                "diachi": _value(teacher.diachi),
            })
    elif role == "SINHVIEN":
        student = db.query(DbSinhVien).filter(DbSinhVien.masv == code).first()
        if student:
            class_info = db.query(DbLop).filter(DbLop.malop == student.malop).first() if student.malop else None
            class_text = ""
            if class_info:
                class_text = f"{_value(class_info.malop)} - {_value(class_info.tenlop)}"
            elif student.malop:
                class_text = _value(student.malop)

            profile.update({
                "hoten": _value(f"{_value(student.ho)} {_value(student.ten)}"),
                "diachi": _value(student.diachi),
                "ngaysinh": student.ngaysinh.strftime("%d/%m/%Y") if student.ngaysinh else "",
                "lop": class_text,
            })

    return profile


# thong tin nguoi dung
@router.get("/info", response_class=HTMLResponse)
def info(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    profile = _build_user_profile(db, user)
    return templates.TemplateResponse(
        "info.html",
        {"request": request, "user": user, "profile": profile},
    )

# dang ky
@router.post("/register")
def dangKy(
    request: DangKy,
    db: Session = Depends(get_db),
    user=Depends(require_permission(Permission.CREATE_USER)),
):
    """
    Tạo thông tin người dùng vào CSDL
    """
    return db_user.dang_ky(db=db, request=request)

@router.get("/register", response_class=HTMLResponse)
def register(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_permission(Permission.CREATE_USER)),
):

    try:
        result = db.execute(
            text("EXEC SP_GET_GV_CHUA_DK")
        ).fetchall()
    except Exception:
        result = db.execute(
            text("""
                SELECT
                    gv.MAGV,
                    LTRIM(RTRIM(COALESCE(gv.HO, '') + ' ' + COALESCE(gv.TEN, ''))) AS HOTEN,
                    CASE WHEN dp.name IS NULL THEN 0 ELSE 1 END AS TRANGTHAI
                FROM GIAOVIEN gv
                LEFT JOIN sys.database_principals dp
                    ON dp.name = gv.MAGV
                ORDER BY gv.MAGV
            """)
        ).fetchall()

    giang_viens = [
        {
            "magv": row.MAGV,
            "hoten": row.HOTEN,
            "trangthai": row.TRANGTHAI
        }
        for row in result
    ]

    return templates.TemplateResponse(
        "register.html",
        {
            "request": request,
            "user": user,
            "giang_viens": giang_viens
        }
    )

# API lấy danh sách giảng viên
@router.get("/api/giao-vien")
def get_giao_vien(
    db: Session = Depends(get_db),
    user=Depends(require_permission(Permission.VIEW_TEACHER)),
):
    """
    Lấy danh sách giảng viên chưa đăng ký từ stored procedure SP_GET_GV_CHUA_DK
    """
    return db_giaovien.get_all_gv(db)


@router.get("/logout")
def logout(request: Request):
    """Logout: delete server session and remove cookie, then redirect to login."""
    session_id = request.cookies.get("session_id")
    if session_id:
        try:
            delete_session(session_id)
        except Exception:
            pass

    response = RedirectResponse(url="/user/login")
    response.delete_cookie("session_id", path="/")
    return response

