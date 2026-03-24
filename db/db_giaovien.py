from sqlalchemy.orm.session import Session
from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.engine import URL
from sqlalchemy import create_engine
from db.database import engine
from schemas.schemas import DangNhapBase, UserBase,GiaoVienChuaDK
from pydantic import BaseModel
from typing import List, Optional


def get_all_gv(db: Session) -> List[GiaoVienChuaDK]:
    """
    Lấy danh sách giảng viên chưa đăng ký từ stored procedure SP_GET_GV_CHUA_DK
    """
    try:
        query = text("EXEC SP_GET_GV_CHUA_DK")
        result = db.execute(query).fetchall()
        
        giao_vien_list = []
        for row in result:
            gv = GiaoVienChuaDK(
                magv=row.MAGV,
                ho=row.HO,
                ten=row.TEN
            )
            giao_vien_list.append(gv)
        
        return giao_vien_list
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi lấy danh sách giảng viên: {str(e)}"
        )
