from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm.session import Session
from schemas.schemas import UserBase, DangNhapBase, UserBase, DangKyBase
from db.database import get_db
from db import db_giaovien, db_user 
router = APIRouter(
    prefix = "/teacher",
    tags= ["teacher"]
)
templates = Jinja2Templates(directory="templates")
# Các đường dẫn cần bỏ qua khi log
# login 
# user_router.py
@router.get("/GVCHDK")
def get_giao_vien(db: Session = Depends(get_db)):
    return db_giaovien.get_all_gv(db=db)