from typing import List

from fastapi import HTTPException, status
from sqlalchemy import exc
from sqlalchemy.orm.session import Session

from db.model import DbLop, DbSinhVien
from schemas.schemas import LopDisplay


def get_all_lop(db: Session) -> List[LopDisplay]:
        """
        Lấy danh sách tất cả các lớp
        """
        try:
                rows = db.query(DbLop).order_by(DbLop.malop.asc()).all()
                return [LopDisplay.model_validate(row) for row in rows]
        except exc.SQLAlchemyError as e:
                raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail={"message": f"Loi khi lay danh sach lop: {str(e)}"},
                )
def them_lop(db: Session, lop: LopDisplay) -> LopDisplay:
        """
        Thêm lớp mới vào database
        """
        ma_lop = (lop.malop or "").strip()
        ten_lop = (lop.tenlop or "").strip()
        
        if not ma_lop:
                raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail={"message": "Ma lop khong duoc de trong"},
                )
        
        if not ten_lop:
                raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail={"message": "Ten lop khong duoc de trong"},
                )
        
        try:
                # Kiểm tra mã lớp đã tồn tại chưa
                existing_lop = db.query(DbLop).filter(DbLop.malop == ma_lop).first()
                if existing_lop:
                        raise HTTPException(
                                status_code=status.HTTP_400_BAD_REQUEST,
                                detail={"message": f"Ma lop {ma_lop} da ton tai"},
                        )
                
                # Kiểm tra tên lớp đã tồn tại chưa
                existing_tenlop = db.query(DbLop).filter(DbLop.tenlop == ten_lop).first()
                if existing_tenlop:
                        raise HTTPException(
                                status_code=status.HTTP_400_BAD_REQUEST,
                                detail={"message": f"Ten lop {ten_lop} da ton tai"},
                        )
                
                new_lop = DbLop(malop=ma_lop, tenlop=ten_lop)
                db.add(new_lop)
                db.commit()
                db.refresh(new_lop)
                return LopDisplay.model_validate(new_lop)
        except HTTPException:
                raise
        except exc.SQLAlchemyError as e:
                db.rollback()
                raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail={"message": f"Loi khi them lop: {str(e)}"},
                )
def sua_lop(db: Session, malop: str, lop: LopDisplay) -> LopDisplay:
        """
        Cập nhật thông tin lớp
        """
        ma_lop = (malop or "").strip()
        ten_lop = (lop.tenlop or "").strip()
        
        if not ma_lop:
                raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail={"message": "Ma lop khong duoc de trong"},
                )
        
        if not ten_lop:
                raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail={"message": "Ten lop khong duoc de trong"},
                )
        
        try:
                existing_lop = db.query(DbLop).filter(DbLop.malop == ma_lop).first()
                if not existing_lop:
                        raise HTTPException(
                                status_code=status.HTTP_404_NOT_FOUND,
                                detail={"message": f"Khong tim thay lop co ma: {ma_lop}"},
                        )
                
                # Kiểm tra tên lớp mới đã tồn tại chưa (ngoại trừ chính nó)
                existing_tenlop = db.query(DbLop).filter(
                        DbLop.tenlop == ten_lop,
                        DbLop.malop != ma_lop
                ).first()
                if existing_tenlop:
                        raise HTTPException(
                                status_code=status.HTTP_400_BAD_REQUEST,
                                detail={"message": f"Ten lop {ten_lop} da ton tai"},
                        )
                
                existing_lop.tenlop = ten_lop
                db.commit()
                db.refresh(existing_lop)
                return LopDisplay.model_validate(existing_lop)
        except HTTPException:
                raise
        except exc.SQLAlchemyError as e:
                db.rollback()
                raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail={"message": f"Loi khi sua lop: {str(e)}"},
                )
def xoa_lop(db: Session, malop: str) -> None:
        """
        Xóa lớp (chỉ có thể xóa lớp không có sinh viên)
        """
        ma_lop = (malop or "").strip()
        
        if not ma_lop:
                raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail={"message": "Ma lop khong duoc de trong"},
                )
        
        try:
                existing_lop = db.query(DbLop).filter(DbLop.malop == ma_lop).first()
                if not existing_lop:
                        raise HTTPException(
                                status_code=status.HTTP_404_NOT_FOUND,
                                detail={"message": f"Khong tim thay lop co ma: {ma_lop}"},
                        )
                
                # Kiểm tra số lượng sinh viên trong lớp
                sl = db.query(DbSinhVien).filter(DbSinhVien.malop == ma_lop).count()
                if sl > 0:
                        raise HTTPException(
                                status_code=status.HTTP_400_BAD_REQUEST,
                                detail={"message": f"Khong the xoa lop co {sl} sinh vien"},
                        )
                
                db.delete(existing_lop)
                db.commit()
        except HTTPException:
                raise
        except exc.SQLAlchemyError as e:
                db.rollback()
                raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail={"message": f"Loi khi xoa lop: {str(e)}"},
                )