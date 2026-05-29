from datetime import datetime, time
import math
import random
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm.session import Session
from sqlalchemy import and_, func
from schemas.schemas import SinhVienDisplay, SinhVienBase, SinhVienWithLopDisplay, LopDisplay, ThongTinThi, MonHocDisplay
from db.database import get_db
from db import db_lop, db_monhoc, db_sinhvien
from core.auth import require_any_permission, require_permission
from db.roles import Permission


router = APIRouter(
    prefix="/thi",
    tags=["Thi"]
)
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
def read_root(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_any_permission(Permission.TAKE_EXAM, Permission.PRACTICE_EXAM)),
):
    return templates.TemplateResponse("formBatDauThi.html", {"request": request, "user": user})


@router.get("/lam-bai", response_class=HTMLResponse)
def lam_bai_thi(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_any_permission(Permission.TAKE_EXAM, Permission.PRACTICE_EXAM)),
):
    return templates.TemplateResponse("formThi.html", {"request": request, "user": user})


@router.get("/lich-su", response_class=HTMLResponse)
def lich_su_thi(
    request: Request,
    user=Depends(require_permission(Permission.VIEW_OWN_EXAM)),
):
    return templates.TemplateResponse("placeholder.html", {
        "request": request,
        "user": user,
        "title": "Lich su thi",
        "kicker": "Sinh vien",
        "description": "Danh sach cac lan thi da thuc hien cua sinh vien dang dang nhap.",
    })


@router.get("/xem-lai", response_class=HTMLResponse)
def xem_lai_bai_thi(
    request: Request,
    user=Depends(require_permission(Permission.VIEW_OWN_EXAM)),
):
    return templates.TemplateResponse("placeholder.html", {
        "request": request,
        "user": user,
        "title": "Xem lai bai thi",
        "kicker": "Sinh vien",
        "description": "Man hinh xem lai cau hoi, dap an da chon va ket qua cua cac bai thi da lam.",
    })


@router.get("/diem", response_class=HTMLResponse)
def diem_thi(
    request: Request,
    user=Depends(require_permission(Permission.VIEW_OWN_SCORE)),
):
    return templates.TemplateResponse("placeholder.html", {
        "request": request,
        "user": user,
        "title": "Diem thi",
        "kicker": "Sinh vien",
        "description": "Bang diem ca nhan cua sinh vien dang dang nhap.",
    })


@router.get("/ket-qua", response_class=HTMLResponse)
def ket_qua_sinh_vien(
    request: Request,
    user=Depends(require_permission(Permission.VIEW_STUDENT_SCORE)),
):
    return templates.TemplateResponse("placeholder.html", {
        "request": request,
        "user": user,
        "title": "Ket qua thi sinh vien",
        "kicker": "Bao cao",
        "description": "Man hinh xem ket qua thi va xem lai bai lam cua sinh vien.",
    })


@router.get("/bang-diem", response_class=HTMLResponse)
def bang_diem(
    request: Request,
    user=Depends(require_permission(Permission.PRINT_SCORE_TABLE)),
):
    return templates.TemplateResponse("placeholder.html", {
        "request": request,
        "user": user,
        "title": "Bang diem mon hoc",
        "kicker": "Bao cao",
        "description": "Man hinh tong hop va in bang diem mon hoc.",
    })

from db.model import DbSinhVien, DbGiaoVienDangKy, DbMonHoc, DbBoDe

LOWER_LEVEL = {
    "A": "B",
    "B": "C",
}

@router.post("/nhanLop", response_model=LopDisplay)
def nhapLop(
    masv: str,
    db: Session = Depends(get_db),
    user=Depends(require_any_permission(Permission.TAKE_EXAM, Permission.PRACTICE_EXAM)),
):
    if user.get("role") == "SINHVIEN" and masv != user.get("ma"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Khong duoc xem thong tin lop cua sinh vien khac"
        )

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


@router.get("/monhoc-duoc-thi", response_model=List[MonHocDisplay])
def mon_hoc_duoc_thi(
    db: Session = Depends(get_db),
    user=Depends(require_any_permission(Permission.TAKE_EXAM, Permission.PRACTICE_EXAM)),
):
    if user.get("role") == "SINHVIEN":
        sinh_vien = db.query(DbSinhVien).filter(DbSinhVien.masv == user.get("ma")).first()

        if not sinh_vien:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Khong tim thay sinh vien dang dang nhap"
            )

        if not sinh_vien.malop:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sinh vien chua duoc phan lop"
            )

        return (
            db.query(DbMonHoc)
            .join(DbGiaoVienDangKy, DbMonHoc.mamh == DbGiaoVienDangKy.mamh)
            .filter(DbGiaoVienDangKy.malop == sinh_vien.malop)
            .distinct()
            .all()
        )

    return db.query(DbMonHoc).all()

@router.get("/layTTThi", response_model=ThongTinThi)
def layTTThi(
    mamonhoc: str,
    lanthi: int,
    malop: str,
    ngaythi: str,
    db: Session = Depends(get_db),
    user=Depends(require_any_permission(Permission.TAKE_EXAM, Permission.PRACTICE_EXAM)),
):
    try:
        exam_date = datetime.strptime(ngaythi, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Ngay thi phai co dinh dang YYYY-MM-DD"
        )

    if user.get("role") == "SINHVIEN":
        sinh_vien = db.query(DbSinhVien).filter(DbSinhVien.masv == user.get("ma")).first()

        if not sinh_vien:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Khong tim thay sinh vien dang dang nhap"
            )

        if not sinh_vien.malop:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sinh vien chua duoc phan lop"
            )

        if sinh_vien.malop.strip() != malop.strip():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Khong duoc xem lich thi cua lop khac"
            )

    start_at = datetime.combine(exam_date, time.min)
    end_at = datetime.combine(exam_date, time.max)

    try:
        exam_info = db.query(DbGiaoVienDangKy).filter(
            DbGiaoVienDangKy.mamh == mamonhoc,
            DbGiaoVienDangKy.lan == lanthi,
            DbGiaoVienDangKy.malop == malop,
            and_(
                DbGiaoVienDangKy.ngaythi >= start_at,
                DbGiaoVienDangKy.ngaythi <= end_at
            )
        ).first()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Loi database khi lay thong tin thi: {str(exc)}"
        )

    if not exam_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Khong tim thay lich thi phu hop voi mon, lop, ngay thi va lan thi da chon"
        )

    return exam_info


@router.get("/cau-hoi")
def lay_cau_hoi_thi(
    mamonhoc: str,
    lanthi: int,
    malop: str,
    ngaythi: str,
    db: Session = Depends(get_db),
    user=Depends(require_any_permission(Permission.TAKE_EXAM, Permission.PRACTICE_EXAM)),
):
    try:
        exam_date = datetime.strptime(ngaythi, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Ngay thi phai co dinh dang YYYY-MM-DD"
        )

    if user.get("role") == "SINHVIEN":
        sinh_vien = db.query(DbSinhVien).filter(DbSinhVien.masv == user.get("ma")).first()

        if not sinh_vien:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Khong tim thay sinh vien dang dang nhap"
            )

        if not sinh_vien.malop:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sinh vien chua duoc phan lop"
            )

        if sinh_vien.malop.strip() != malop.strip():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Khong duoc lay cau hoi thi cua lop khac"
            )

    start_at = datetime.combine(exam_date, time.min)
    end_at = datetime.combine(exam_date, time.max)

    try:
        exam_info = db.query(DbGiaoVienDangKy).filter(
            DbGiaoVienDangKy.mamh == mamonhoc,
            DbGiaoVienDangKy.lan == lanthi,
            DbGiaoVienDangKy.malop == malop,
            and_(
                DbGiaoVienDangKy.ngaythi >= start_at,
                DbGiaoVienDangKy.ngaythi <= end_at
            )
        ).first()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Loi database khi lay lich thi: {str(exc)}"
        )

    if not exam_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Khong tim thay lich thi phu hop"
        )

    try:
        required_count = int(exam_info.socauthi or 0)
        registered_level = (exam_info.trinhdo or "").strip()
        lower_level = LOWER_LEVEL.get(registered_level)
        max_lower_count = math.floor(required_count * 0.3)

        primary_questions = (
            db.query(DbBoDe)
            .filter(
                DbBoDe.mamh == exam_info.mamh,
                DbBoDe.trinhdo == registered_level
            )
            .order_by(func.newid())
            .limit(required_count)
            .all()
        )

        missing_count = required_count - len(primary_questions)
        lower_questions = []

        if missing_count > 0:
            if not lower_level:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Khong du cau hoi trinh do {registered_level}. Yeu cau: {required_count}, hien co: {len(primary_questions)}"
                )

            if missing_count > max_lower_count:
                min_primary_count = required_count - max_lower_count
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Khong du cau hoi trinh do {registered_level}. "
                        f"Can it nhat {min_primary_count} cau dung trinh do va chi duoc bu toi da {max_lower_count} cau trinh do {lower_level}."
                    )
                )

            lower_questions = (
                db.query(DbBoDe)
                .filter(
                    DbBoDe.mamh == exam_info.mamh,
                    DbBoDe.trinhdo == lower_level
                )
                .order_by(func.newid())
                .limit(missing_count)
                .all()
            )

            if len(lower_questions) < missing_count:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Khong du cau hoi de bu trinh do {lower_level}. "
                        f"Can bu: {missing_count}, hien co: {len(lower_questions)}"
                    )
                )

        cau_hois = primary_questions + lower_questions
        random.shuffle(cau_hois)
    except Exception as exc:
        if isinstance(exc, HTTPException):
            raise exc
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Loi database khi lay cau hoi thi: {str(exc)}"
        )

    if len(cau_hois) < exam_info.socauthi:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Khong du cau hoi thi. Yeu cau: {exam_info.socauthi}, hien co: {len(cau_hois)}"
        )

    return {
        "mamonhoc": (exam_info.mamh or "").strip(),
        "malop": (exam_info.malop or "").strip(),
        "lanthi": exam_info.lan,
        "ngaythi": exam_date.isoformat(),
        "trinhdo": (exam_info.trinhdo or "").strip(),
        "socauthi": exam_info.socauthi,
        "thoigian": exam_info.thoigian,
        "cauhoi": [
            {
                "cauhoi": item.cauhoi,
                "trinhdo": (item.trinhdo or "").strip(),
                "noidung": item.noidung,
                "options": [
                    {"key": "A", "text": item.a},
                    {"key": "B", "text": item.b},
                    {"key": "C", "text": item.c},
                    {"key": "D", "text": item.d},
                ],
            }
            for item in cau_hois
        ],
    }
