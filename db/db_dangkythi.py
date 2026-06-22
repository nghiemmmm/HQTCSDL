import math
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm.session import Session

from db.model import DbBoDe, DbGiaoVien, DbGiaoVienDangKy, DbLop, DbMonHoc
from schemas.schemas import DangKyThi

LOWER_LEVEL = {
    "A": "B",
    "B": "C",
}


def _clean(value: Optional[str]) -> str:
    return (value or "").strip()


def _registration_query(db: Session, malop: str, mamh: str, lan: int):
    return db.query(DbGiaoVienDangKy).filter(
        DbGiaoVienDangKy.malop == malop,
        DbGiaoVienDangKy.mamh == mamh,
        DbGiaoVienDangKy.lan == lan,
    )


def validate_question_pool(db: Session, mamh: str, trinhdo: str, socauthi: int) -> dict:
    mamh = _clean(mamh)
    trinhdo = _clean(trinhdo).upper()
    required_count = int(socauthi or 0)

    if not trinhdo or required_count <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can nhap trinh do va so cau thi",
        )

    primary_count = db.query(DbBoDe).filter(
        DbBoDe.mamh == mamh,
        DbBoDe.trinhdo == trinhdo,
    ).count()

    if primary_count >= required_count:
        return {
            "valid": True,
            "primary_count": primary_count,
            "lower_count": 0,
            "max_lower_count": math.floor(required_count * 0.3),
            "message": "Du cau hoi dung trinh do",
        }

    lower_level = LOWER_LEVEL.get(trinhdo)
    missing_count = required_count - primary_count
    max_lower_count = math.floor(required_count * 0.3)

    if not lower_level:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Khong du cau hoi trinh do {trinhdo}. "
                f"Yeu cau {required_count}, hien co {primary_count}."
            ),
        )

    if missing_count > max_lower_count:
        min_primary_count = required_count - max_lower_count
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Khong du cau hoi trinh do {trinhdo}. "
                f"Can it nhat {min_primary_count} cau dung trinh do va chi duoc bu toi da "
                f"{max_lower_count} cau trinh do {lower_level}."
            ),
        )

    lower_count = db.query(DbBoDe).filter(
        DbBoDe.mamh == mamh,
        DbBoDe.trinhdo == lower_level,
    ).count()

    if lower_count < missing_count:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Khong du cau hoi de bu trinh do {lower_level}. "
                f"Can bu {missing_count}, hien co {lower_count}."
            ),
        )

    return {
        "valid": True,
        "primary_count": primary_count,
        "lower_count": lower_count,
        "max_lower_count": max_lower_count,
        "message": f"Du cau hoi: {primary_count} cau {trinhdo}, bu {missing_count} cau {lower_level}",
    }


def _validate_references(db: Session, request: DangKyThi) -> None:
    monhoc = db.query(DbMonHoc).filter(DbMonHoc.mamh == request.mamh).first()
    if not monhoc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Mon hoc {request.mamh} khong ton tai")

    lop = db.query(DbLop).filter(DbLop.malop == request.malop).first()
    if not lop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Lop {request.malop} khong ton tai")

    if request.magv:
        giaovien = db.query(DbGiaoVien).filter(DbGiaoVien.magv == request.magv).first()
        if not giaovien:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Giao vien {request.magv} khong ton tai")

    validate_question_pool(db, request.mamh, request.trinhdo, request.socauthi)


def create(db: Session, request: DangKyThi):
    _validate_references(db, request)

    existing_reg = _registration_query(db, request.malop, request.mamh, request.lan).first()
    if existing_reg:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Lich thi cho lop {request.malop}, mon {request.mamh} lan {request.lan} da duoc dang ky.",
        )

    new_reg = DbGiaoVienDangKy(
        magv=request.magv,
        mamh=request.mamh,
        malop=request.malop,
        trinhdo=request.trinhdo,
        ngaythi=request.ngaythi,
        lan=request.lan,
        socauthi=request.socauthi,
        thoigian=request.thoigian,
    )

    db.add(new_reg)
    db.commit()
    db.refresh(new_reg)
    return new_reg


def update(db: Session, malop: str, mamh: str, lan: int, request: DangKyThi):
    reg = _registration_query(db, malop, mamh, lan).first()
    if not reg:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Khong tim thay lich dang ky thi")

    request.malop = malop
    request.mamh = mamh
    request.lan = lan
    _validate_references(db, request)

    reg.magv = request.magv
    reg.trinhdo = request.trinhdo
    reg.ngaythi = request.ngaythi
    reg.socauthi = request.socauthi
    reg.thoigian = request.thoigian

    db.commit()
    db.refresh(reg)
    return reg


def get_all(db: Session, keyword: Optional[str] = None, magv: Optional[str] = None):
    query = db.query(DbGiaoVienDangKy)

    if magv:
        query = query.filter(DbGiaoVienDangKy.magv == magv)

    if keyword:
        value = f"%{keyword.strip()}%"
        query = query.outerjoin(DbMonHoc, DbGiaoVienDangKy.mamh == DbMonHoc.mamh).outerjoin(
            DbLop, DbGiaoVienDangKy.malop == DbLop.malop
        ).filter(
            or_(
                DbGiaoVienDangKy.malop.ilike(value),
                DbGiaoVienDangKy.mamh.ilike(value),
                DbGiaoVienDangKy.magv.ilike(value),
                DbMonHoc.tenmh.ilike(value),
                DbLop.tenlop.ilike(value),
            )
        )

    return query.order_by(DbGiaoVienDangKy.ngaythi.desc(), DbGiaoVienDangKy.malop, DbGiaoVienDangKy.mamh).all()


def get_by_lop(db: Session, malop: str):
    return db.query(DbGiaoVienDangKy).filter(DbGiaoVienDangKy.malop == malop).all()


def delete(db: Session, malop: str, mamh: str, lan: int):
    reg = _registration_query(db, malop, mamh, lan).first()

    if not reg:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Khong tim thay lich dang ky thi")

    db.delete(reg)
    db.commit()
    return {"message": "Xoa lich thi thanh cong"}


def get_monhocdk(db: Session, magv: str):
    try:
        subjects = (
            db.query(DbMonHoc)
            .join(DbBoDe, DbMonHoc.mamh == DbBoDe.mamh)
            .filter(DbBoDe.magv == magv)
            .distinct()
            .order_by(DbMonHoc.mamh)
            .all()
        )
        if subjects:
            return subjects
        return db.query(DbMonHoc).order_by(DbMonHoc.mamh).all()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Loi khi lay mon hoc dang ky: {str(exc)}",
        )
