from typing import List

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm.session import Session

from db.model import DbGiaoVien
from schemas.schemas import GiaoVienDisplay,GiaoVien
from sqlalchemy import exc, or_

def get_all_gv(db: Session) -> List[GiaoVienDisplay]:
    """Lấy danh sách tất cả giáo viên trong bảng GIAOVIEN."""
    try:
        rows = db.query(DbGiaoVien).all()
        return [GiaoVienDisplay.model_validate(row) for row in rows]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi lấy danh sách giảng viên: {str(e)}",
        )


def get_ds_gv_chua_quyen(db: Session) -> List[GiaoVienDisplay]:
    """Lấy danh sách giảng viên chưa có quyền qua SP_GET_GV_CHUA_DK."""
    try:
        rows = db.execute(text("EXEC SP_GET_GV_CHUA_DK")).fetchall()
        return [
            GiaoVienDisplay(
                magv=(row.MAGV or "").strip(),
                ho=(row.HO or "").strip() if row.HO else None,
                ten=(row.TEN or "").strip() if row.TEN else None,
                diachi=None,
                sodtll=None,
            )
            for row in rows
        ]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi lấy danh sách giảng viên chưa quyền: {str(e)}",
        )



def get_all(db: Session):
    return db.query(DbGiaoVien).all()

def get_by_id(db: Session, magv: str):
    obj = db.query(DbGiaoVien).filter(DbGiaoVien.magv == magv).first()
    if not obj:
        raise HTTPException(404, f"Không tìm thấy giáo viên {magv}")
    return obj

def check_duplicate_magv(db: Session, magv: str):
    return db.query(DbGiaoVien).filter(DbGiaoVien.magv == magv).first() is not None

def create(db: Session, request: GiaoVien):
    if check_duplicate_magv(db, request.magv):
        raise HTTPException(400, f"Mã giáo viên {request.magv} đã tồn tại")
    
    obj = DbGiaoVien(
        magv=request.magv,
        ho=request.ho,
        ten=request.ten,
        diachi=request.diachi,
        sodtll=request.sodtll
    )
    try:
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return {
            "message": f"Thêm thành công giáo viên: {(obj.ho or '')} {(obj.ten or '')}".strip(),
            "data": {
                "magv": obj.magv,
                "ho": obj.ho,
                "ten": obj.ten,
                "diachi": obj.diachi,
                "sodtll": obj.sodtll
            }
        }
    except exc.SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(500, str(e))

def update(db: Session, magv: str, request: GiaoVien):
    obj = get_by_id(db, magv)
    try:
        obj.ho = request.ho
        obj.ten = request.ten
        obj.diachi = request.diachi
        obj.sodtll = request.sodtll
        db.commit()
        db.refresh(obj)
        return {
            "message": f"Sửa thành công giáo viên: {(obj.ho or '')} {(obj.ten or '')}".strip(),
            "data": {
                "magv": obj.magv,
                "ho": obj.ho,
                "ten": obj.ten,
                "diachi": obj.diachi,
                "sodtll": obj.sodtll
            }
        }
    except exc.SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(500, str(e))

def delete(db: Session, magv: str):
    obj = get_by_id(db, magv)
    try:
        db.delete(obj)
        db.commit()
        return {"message": f"Xóa thành công giáo viên: {(obj.ho or '')} {(obj.ten or '')}".strip()}
    except exc.SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(400, "Không thể xóa giáo viên này do ràng buộc dữ liệu.")

def search(db: Session, keyword: str):
    if not keyword:
        return get_all(db)
    
    return db.query(DbGiaoVien).filter(
        or_(
            DbGiaoVien.magv.ilike(f"%{keyword}%"),
            DbGiaoVien.ho.ilike(f"%{keyword}%"),
            DbGiaoVien.ten.ilike(f"%{keyword}%")
        )
    ).all()
