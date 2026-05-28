from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import exc

from schemas.schemas import MonHocBase, MonHocDisplay
from db.database import get_db
from db import db_monhoc
from db.model import DbMonHoc
from core.auth import require_permission
from db.roles import Permission

router = APIRouter(
    prefix="/monhoc",
    tags=["MonHoc"]
)

templates = Jinja2Templates(directory="templates")


# =========================
# VIEW HTML FORM
# =========================
@router.get("", response_class=HTMLResponse)
def form_monhoc(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_permission(Permission.VIEW_SUBJECT)),
):
    return templates.TemplateResponse(
        "formMonHoc.html",
        {"request": request}
    )


# =========================
# GET ALL (JSON)
# =========================
@router.get("/danhsachMH", response_model=List[MonHocDisplay])
def get_all_monhoc(
    db: Session = Depends(get_db),
    user=Depends(require_permission(Permission.VIEW_SUBJECT)),
):
    return db_monhoc.get_all(db)


# =========================
# SEARCH
# =========================
@router.get("/search/{keyword}")
def search(
    keyword: str,
    db: Session = Depends(get_db),
    user=Depends(require_permission(Permission.VIEW_SUBJECT)),
):
    return db_monhoc.search(db, keyword)


# =========================
# GET BY ID
# =========================
@router.get("/{mamh}")
def get_one(
    mamh: str,
    db: Session = Depends(get_db),
    user=Depends(require_permission(Permission.VIEW_SUBJECT)),
):
    return db_monhoc.get_by_id(db, mamh)


# =========================
# CREATE (POST)
# =========================
@router.post("", status_code=status.HTTP_201_CREATED)
def create(
    request: MonHocBase,
    db: Session = Depends(get_db),
    user=Depends(require_permission(Permission.CREATE_SUBJECT)),
):
    return db_monhoc.create(db, request)


# =========================
# UPDATE (PUT)
# =========================
@router.put("/{mamh}")
def update(
    mamh: str,
    request: MonHocBase,
    db: Session = Depends(get_db),
    user=Depends(require_permission(Permission.UPDATE_SUBJECT)),
):
    return db_monhoc.update(db, mamh, request)


# =========================
# DELETE
# =========================
@router.delete("/{mamh}")
def delete(
    mamh: str,
    db: Session = Depends(get_db),
    user=Depends(require_permission(Permission.DELETE_SUBJECT)),
):
    return db_monhoc.delete(db, mamh)
