from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm.session import Session
from schemas.schemas import MonHocBase
from db.database import get_db
from db import db_monhoc
from db.model import DbMonHoc

router = APIRouter(
    prefix="/monhoc",
    tags=["MonHoc"]
)
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
def hienThiMonHoc(request: Request, db: Session = Depends(get_db)):
    
    mon_hocs = db.query(DbMonHoc).all()   # 🔥 lấy danh sách môn học
    mon_hocs_json = [
        {"mamh": mh.mamh, "tenmh": mh.tenmh}
        for mh in mon_hocs
    ]
    return templates.TemplateResponse(
        "formMonHoc.html",
        {
            "request": request,
            "mon_hocs": mon_hocs_json  # 🔥 truyền sang HTML
        }
    )


# @router.get("/")
# def get_all_monhoc(
#     q: Optional[str] = Query(default=None, description="Tu khoa tim theo ma/ten mon hoc"),
#     db: Session = Depends(get_db),
# ):
#     if q:
#         return db_monhoc.search(db, q)
#     return db_monhoc.get_all(db)


# @router.get("/check-duplicate")
# def check_duplicate_monhoc(
#     mamh: Optional[str] = Query(default=None, description="Ma mon hoc can kiem tra"),
#     tenmh: Optional[str] = Query(default=None, description="Ten mon hoc can kiem tra"),
#     exclude_mamh: Optional[str] = Query(default=None, description="Bo qua ma mon hoc hien tai khi sua"),
#     db: Session = Depends(get_db),
# ):
#     mamh_val = (mamh or "").strip()
#     tenmh_val = (tenmh or "").strip()

#     if not mamh_val and not tenmh_val:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail={"message": "Can truyen it nhat 1 gia tri: mamh hoac tenmh"},
#         )

#     result = db_monhoc.check_duplicate_monhoc(
#         db=db,
#         mamh=mamh_val,
#         tenmh=tenmh_val,
#         exclude_mamh=exclude_mamh,
#     )
#     result["is_duplicate"] = result["duplicate_mamh"] or result["duplicate_tenmh"]
#     return result


# @router.post("/checkda-dang-ky")
# def check_monhoc_da_dang_ky(
#     mamh: str = Query(..., description="Ma mon hoc can kiem tra"),
#     db: Session = Depends(get_db),
# ):
#     return db_monhoc.check_monhoc_da_dk(db, mamh)


# @router.get("/{mamh}")
# def get_monhoc_by_id(mamh: str, db: Session = Depends(get_db)):
#     return db_monhoc.get_by_id(db, mamh)


# @router.post("/")
# def create_monhoc(request: MonHocBase, db: Session = Depends(get_db)):
#     return db_monhoc.create(db, request)


# @router.put("/{mamh}")
# def update_monhoc(mamh: str, request: MonHocBase, db: Session = Depends(get_db)):
#     return db_monhoc.update(db, mamh, request)


# @router.delete("/{mamh}")
# def delete_monhoc(mamh: str, db: Session = Depends(get_db)):
#     return db_monhoc.delete(db, mamh)
