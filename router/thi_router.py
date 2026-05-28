from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm.session import Session
from schemas.schemas import SinhVienDisplay, SinhVienBase, SinhVienWithLopDisplay, LopDisplay,ThongTinThi
from db.database import get_db
from db import db_lop, db_monhoc, db_sinhvien

router = APIRouter(
    prefix="/thi",
    tags=["Thi"]
)
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
def read_root(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("formBatDauThi.html", {"request": request})

from db.model import DbSinhVien

@router.post("/nhanLop", response_model=LopDisplay)
def nhapLop(masv: str, db: Session = Depends(get_db)):
    sinh_vien = db.query(DbSinhVien).filter(DbSinhVien.masv == masv).first()
    
    if not sinh_vien:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,  
            detail="Không tìm thấy sinh viên với mã này"
        )
        
    if not sinh_vien.lop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Sinh viên chưa được phân lớp"
        )
        
    return sinh_vien.lop
from db.model import DbGiaoVienDangKy

@router.get("/layTTThi", response_model=ThongTinThi)
def layTTThi(mamonhoc: str, lanthi: int, malop: str, ngaythi: str, db: Session = Depends(get_db)):
    # Tìm lịch thi dựa trên mã môn học, lần thi và mã lớp
    exam_info = db.query(DbGiaoVienDangKy).filter(
        DbGiaoVienDangKy.mamh == mamonhoc,
        DbGiaoVienDangKy.lan == lanthi,
        DbGiaoVienDangKy.malop == malop,
        DbGiaoVienDangKy.ngaythi == ngaythi
    ).first()
    
    if not exam_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Không tìm thấy thông tin bài thi cho môn học và lớp này."
        )
        
    return exam_info
