from typing import List

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm.session import Session

from db.model import DbGiaoVien
from schemas.schemas import GiaoVienDisplay


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

