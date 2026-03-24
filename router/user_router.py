from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm.session import Session
from schemas.schemas import UserBase, DangNhapBase, UserBase, DangKyBase
from db.database import get_db
from db import db_user
from db import db_giaovien 
router = APIRouter(
    prefix = "/user",
    tags= ["user"]
)
templates = Jinja2Templates(directory="templates")
# Các đường dẫn cần bỏ qua khi log
# login 
@router.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login", response_model=UserBase)
def dangNhap(request: DangNhapBase, db: Session = Depends(get_db)):
    """
    Tạo thông tin người dùng vào CSDL
    """
    return db_user.dang_nhap(db=db, request=request)
# thong tin nguoi dung
@router.get("/info", response_class=HTMLResponse)
async def info(request: Request, user: UserBase = None):
    return templates.TemplateResponse("info.html", {"request": request, "user": user})

# dang ky
@router.post("/register")
def dangKy(request: DangKyBase, db: Session = Depends(get_db)):
    """
    Tạo thông tin người dùng vào CSDL
    """
    return db_user.dang_ky(db=db, request=request)

@router.get("/register",response_class=HTMLResponse)
def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

# API lấy danh sách giảng viên
@router.get("/api/giao-vien")
def get_giao_vien(db: Session = Depends(get_db)):
    """
    Lấy danh sách giảng viên chưa đăng ký từ stored procedure SP_GET_GV_CHUA_DK
    """
    return db_giaovien.get_all_gv(db)

