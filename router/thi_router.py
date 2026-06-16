from datetime import datetime, time, timedelta
import json
import math
import random
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
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
    db: Session = Depends(get_db),
    user=Depends(require_permission(Permission.VIEW_OWN_EXAM)),
):
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

    now = datetime.now()
    registrations = (
        db.query(DbGiaoVienDangKy)
        .filter(DbGiaoVienDangKy.malop == sinh_vien.malop)
        .order_by(DbGiaoVienDangKy.ngaythi.desc())
        .all()
    )

    unfinished_exams = []
    recent_exams = []
    subjects = {}

    for registration in registrations:
        subject = db.query(DbMonHoc).filter(DbMonHoc.mamh == registration.mamh).first()
        score = db.query(DbBangDiem).filter(
            DbBangDiem.masv == sinh_vien.masv,
            DbBangDiem.mamh == registration.mamh,
            DbBangDiem.lan == registration.lan
        ).first()

        mamh = (registration.mamh or "").strip()
        tenmh = (subject.tenmh or "").strip() if subject else mamh
        subjects[mamh] = tenmh

        start_at = registration.ngaythi
        duration = int(registration.thoigian or 0)
        end_at = start_at + timedelta(minutes=duration) if start_at else None
        exam_date = start_at.date().isoformat() if start_at else ""
        active_session = None
        submitted_session = None
        remaining_seconds = None
        started_text = None

        if start_at:
            active_session = db.query(DbPhienThi).filter(
                DbPhienThi.masv == sinh_vien.masv,
                DbPhienThi.mamh == registration.mamh,
                DbPhienThi.lan == registration.lan,
                DbPhienThi.malop == registration.malop,
                DbPhienThi.ngaythi == start_at.date(),
                DbPhienThi.trangthai == "DANG_LAM"
            ).first()
            submitted_session = db.query(DbPhienThi).filter(
                DbPhienThi.masv == sinh_vien.masv,
                DbPhienThi.mamh == registration.mamh,
                DbPhienThi.lan == registration.lan,
                DbPhienThi.malop == registration.malop,
                DbPhienThi.ngaythi == start_at.date(),
                DbPhienThi.trangthai == "DA_NOP"
            ).order_by(DbPhienThi.nopbai_luc.desc(), DbPhienThi.id.desc()).first()

        if active_session:
            remaining_seconds = sync_session_time(db, active_session)
            started_text = active_session.batdau_luc.strftime("%d/%m/%Y %H:%M")
            if active_session.trangthai != "DANG_LAM":
                active_session = None

        if score:
            status_label = "Đã nộp"
            status_key = "da-nop"
            action_label = "Xem kết quả"
        elif active_session:
            status_label = "Đang làm"
            status_key = "dang-lam"
            action_label = "Tiếp tục làm bài"
        elif start_at and now < start_at:
            status_label = "Chưa thi"
            status_key = "chua-thi"
            action_label = "Vào thi"
        elif start_at and end_at and start_at <= now <= end_at:
            status_label = "Đang làm"
            status_key = "dang-lam"
            action_label = "Tiếp tục làm bài"
        else:
            status_label = "Hết hạn"
            status_key = "het-han"
            action_label = "Xem chi tiết"

        exam_url = (
            f"/thi/lam-bai?mamonhoc={mamh}&lanthi={registration.lan}"
            f"&malop={(registration.malop or '').strip()}&ngaythi={exam_date}"
        )
        result_url = (
            f"/thi/xem-lai?session_id={submitted_session.id}"
            if submitted_session else "/thi/xem-lai"
        )

        exam_item = {
            "title": f"Đề thi {tenmh} - Lần {registration.lan}",
            "subject_code": mamh,
            "subject_name": tenmh,
            "status": status_label,
            "status_key": status_key,
            "start_at": start_at.strftime("%d/%m/%Y %H:%M") if start_at else "Chưa có",
            "start_iso": start_at.isoformat() if start_at else "",
            "end_at": end_at.strftime("%d/%m/%Y %H:%M") if end_at else "Chưa có",
            "duration": f"{duration} phút" if duration else "Chưa có",
            "started_text": started_text,
            "remaining_text": (
                f"{remaining_seconds // 3600:02d}:{(remaining_seconds % 3600) // 60:02d}:{remaining_seconds % 60:02d}"
                if remaining_seconds is not None else None
            ),
            "score": score.diem if score else None,
            "action_label": action_label,
            "action_url": exam_url if status_key in ("chua-thi", "dang-lam") else result_url,
            "detail_url": result_url,
        }

        if score:
            recent_exams.append(exam_item)
        else:
            unfinished_exams.append(exam_item)

    return templates.TemplateResponse("lichSuThi.html", {
        "request": request,
        "user": user,
        "unfinished_exams": unfinished_exams,
        "recent_exams": recent_exams,
        "subjects": [
            {"code": code, "name": name}
            for code, name in sorted(subjects.items(), key=lambda item: item[1])
        ],
    })


@router.get("/xem-lai", response_class=HTMLResponse)
def xem_lai_bai_thi(
    request: Request,
    session_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    user=Depends(require_permission(Permission.VIEW_OWN_EXAM)),
):
    sinh_vien = db.query(DbSinhVien).filter(DbSinhVien.masv == user.get("ma")).first()
    if not sinh_vien:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Khong tim thay sinh vien dang dang nhap"
        )

    session_query = db.query(DbPhienThi).filter(
        DbPhienThi.masv == sinh_vien.masv,
        DbPhienThi.trangthai == "DA_NOP"
    )
    if session_id:
        session_query = session_query.filter(DbPhienThi.id == session_id)

    session = (
        session_query
        .order_by(DbPhienThi.nopbai_luc.desc(), DbPhienThi.id.desc())
        .first()
    )

    if not session:
        return templates.TemplateResponse("xemLaiThi.html", {
            "request": request,
            "user": user,
            "has_result": False,
        })

    subject = db.query(DbMonHoc).filter(DbMonHoc.mamh == session.mamh).first()
    class_info = db.query(DbLop).filter(DbLop.malop == session.malop).first()
    score = db.query(DbBangDiem).filter(
        DbBangDiem.masv == sinh_vien.masv,
        DbBangDiem.mamh == session.mamh,
        DbBangDiem.lan == session.lan
    ).first()

    question_ids = parse_json_list(session.danhsach_cauhoi)
    selected_answers = {
        int(question_id): (answer or "").strip().upper()
        for question_id, answer in parse_json_dict(session.dapan_dachon).items()
        if str(question_id).isdigit()
    }
    questions_by_id = {
        item.cauhoi: item
        for item in db.query(DbBoDe).filter(DbBoDe.cauhoi.in_(question_ids)).all()
    }

    question_results = []
    correct_count = 0
    wrong_count = 0
    unanswered_count = 0

    for index, question_id in enumerate(question_ids, start=1):
        question = questions_by_id.get(question_id)
        if not question:
            continue

        correct_answer = (question.dap_an or "").strip().upper()
        selected_answer = selected_answers.get(question_id, "")

        if not selected_answer:
            status_key = "unanswered"
            status_label = "Chưa trả lời"
            unanswered_count += 1
        elif selected_answer == correct_answer:
            status_key = "correct"
            status_label = "Đúng"
            correct_count += 1
        else:
            status_key = "wrong"
            status_label = "Sai"
            wrong_count += 1

        option_rows = []
        for key, text in (
            ("A", question.a),
            ("B", question.b),
            ("C", question.c),
            ("D", question.d),
        ):
            key = key.strip().upper()
            is_selected = selected_answer == key
            is_correct = correct_answer == key
            option_state = "neutral"
            icon = ""

            if is_selected and is_correct:
                option_state = "correct"
                icon = "✓"
            elif is_selected and not is_correct:
                option_state = "wrong"
                icon = "✕"
            elif is_correct:
                option_state = "missed-correct"
                icon = "✓"

            option_rows.append({
                "key": key,
                "text": text,
                "state": option_state,
                "icon": icon,
            })

        question_results.append({
            "number": index,
            "text": question.noidung,
            "status_key": status_key,
            "status_label": status_label,
            "selected_answer": selected_answer or "Chưa trả lời",
            "correct_answer": correct_answer,
            "options": option_rows,
        })

    total_count = len(question_results)
    answered_count = total_count - unanswered_count
    final_score = score.diem if score else session.diem
    completion_rate = round((answered_count / total_count) * 100) if total_count else 0
    accuracy_rate = round((correct_count / total_count) * 100, 1) if total_count else 0
    submitted_at = session.nopbai_luc or session.capnhat_luc
    used_seconds = 0
    if submitted_at and session.batdau_luc:
        used_seconds = max(0, int((submitted_at - session.batdau_luc).total_seconds()))
    elif session.thoigian:
        used_seconds = max(0, int(session.thoigian) * 60 - int(session.thoigian_conlai or 0))

    def format_used_time(total_seconds: int) -> str:
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes} phút {seconds:02d} giây"

    overview = {
        "exam_title": f"Đề thi {((subject.tenmh or '').strip() if subject else (session.mamh or '').strip())} - Lần {session.lan}",
        "subject": (subject.tenmh or "").strip() if subject else (session.mamh or "").strip(),
        "class_name": (
            f"{(class_info.malop or '').strip()} - {class_info.tenlop}"
            if class_info else (session.malop or "").strip()
        ),
        "attempt": session.lan,
        "level": (session.trinhdo or "").strip(),
        "student_name": f"{(sinh_vien.ho or '').strip()} {(sinh_vien.ten or '').strip()}".strip(),
        "student_code": (sinh_vien.masv or "").strip(),
        "started_at": session.batdau_luc.strftime("%d/%m/%Y %H:%M:%S") if session.batdau_luc else "Chưa có",
        "duration": format_used_time(used_seconds),
        "submitted_at": submitted_at.strftime("%d/%m/%Y %H:%M:%S") if submitted_at else "Chưa có",
        "total_count": total_count,
        "correct_count": correct_count,
        "wrong_count": wrong_count,
        "unanswered_count": unanswered_count,
        "final_score": final_score,
        "pass_status": "Đạt" if (final_score or 0) >= 5 else "Không đạt",
        "pass_key": "pass" if (final_score or 0) >= 5 else "fail",
    }

    return templates.TemplateResponse("xemLaiThi.html", {
        "request": request,
        "user": user,
        "has_result": True,
        "overview": overview,
        "quick_stats": {
            "total_count": total_count,
            "correct_count": correct_count,
            "wrong_count": wrong_count,
            "unanswered_count": unanswered_count,
            "completion_rate": completion_rate,
            "accuracy_rate": accuracy_rate,
            "correct_ratio": f"{correct_count}/{total_count} câu",
            "final_score": final_score,
        },
        "question_results": question_results,
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

from db.model import DbSinhVien, DbGiaoVienDangKy, DbMonHoc, DbLop, DbBoDe, DbBangDiem, DbPhienThi

LOWER_LEVEL = {
    "A": "B",
    "B": "C",
}


class BaiNopRequest(BaseModel):
    session_id: Optional[int] = None
    mamonhoc: str
    lanthi: int = Field(..., ge=1, le=2)
    malop: str
    ngaythi: str
    answers: Dict[str, str] = Field(default_factory=dict)


class AutoSaveRequest(BaseModel):
    session_id: int
    answers: Dict[str, str] = Field(default_factory=dict)
    current_index: int = 0
    remaining_seconds: int = 0


def parse_json_dict(value: str) -> dict:
    try:
        data = json.loads(value or "{}")
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def parse_json_list(value: str) -> list[int]:
    try:
        data = json.loads(value or "[]")
        return [int(item) for item in data]
    except Exception:
        return []


def calculate_remaining_seconds(session: DbPhienThi) -> int:
    elapsed = int((datetime.now() - session.batdau_luc).total_seconds())
    total = int(session.thoigian or 0) * 60
    return max(0, total - elapsed)


def sync_session_time(db: Session, session: DbPhienThi) -> int:
    remaining = calculate_remaining_seconds(session)
    session.thoigian_conlai = remaining
    session.capnhat_luc = datetime.now()
    if remaining <= 0 and session.trangthai == "DANG_LAM":
        session.trangthai = "HET_GIO"
    db.commit()
    return remaining


def serialize_question(item: DbBoDe):
    return {
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

    if user.get("role") == "SINHVIEN":
        existing_session = db.query(DbPhienThi).filter(
            DbPhienThi.masv == user.get("ma"),
            DbPhienThi.mamh == mamonhoc,
            DbPhienThi.lan == lanthi,
            DbPhienThi.malop == malop,
            DbPhienThi.ngaythi == exam_date
        ).order_by(DbPhienThi.id.desc()).first()

        if existing_session:
            remaining = sync_session_time(db, existing_session)
            if existing_session.trangthai != "DANG_LAM":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Phien thi dang o trang thai {existing_session.trangthai}, khong the tao phien moi"
                )

            question_ids = parse_json_list(existing_session.danhsach_cauhoi)
            questions_by_id = {
                item.cauhoi: item
                for item in db.query(DbBoDe).filter(DbBoDe.cauhoi.in_(question_ids)).all()
            }
            ordered_questions = [
                questions_by_id[question_id]
                for question_id in question_ids
                if question_id in questions_by_id
            ]

            return {
                "session_id": existing_session.id,
                "session_status": existing_session.trangthai,
                "mamonhoc": (existing_session.mamh or "").strip(),
                "malop": (existing_session.malop or "").strip(),
                "lanthi": existing_session.lan,
                "ngaythi": existing_session.ngaythi.isoformat(),
                "trinhdo": (existing_session.trinhdo or "").strip(),
                "socauthi": existing_session.socauthi,
                "thoigian": existing_session.thoigian,
                "remaining_seconds": remaining,
                "started_at": existing_session.batdau_luc.isoformat(),
                "current_index": existing_session.cauhoi_hientai,
                "answers": parse_json_dict(existing_session.dapan_dachon),
                "cauhoi": [serialize_question(item) for item in ordered_questions],
            }

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

    started_at = datetime.now()
    remaining_seconds = int(exam_info.thoigian or 0) * 60
    session = None

    if user.get("role") == "SINHVIEN":
        session = DbPhienThi(
            masv=user.get("ma"),
            malop=malop,
            mamh=(exam_info.mamh or "").strip(),
            trinhdo=(exam_info.trinhdo or "").strip(),
            lan=exam_info.lan,
            socauthi=exam_info.socauthi,
            thoigian=exam_info.thoigian,
            ngaythi=exam_date,
            batdau_luc=started_at,
            thoigian_conlai=remaining_seconds,
            trangthai="DANG_LAM",
            danhsach_cauhoi=json.dumps([item.cauhoi for item in cau_hois]),
            dapan_dachon="{}",
            cauhoi_hientai=0,
            capnhat_luc=started_at,
        )
        db.add(session)
        db.commit()
        db.refresh(session)

    return {
        "session_id": session.id if session else None,
        "session_status": "DANG_LAM",
        "mamonhoc": (exam_info.mamh or "").strip(),
        "malop": (exam_info.malop or "").strip(),
        "lanthi": exam_info.lan,
        "ngaythi": exam_date.isoformat(),
        "trinhdo": (exam_info.trinhdo or "").strip(),
        "socauthi": exam_info.socauthi,
        "thoigian": exam_info.thoigian,
        "remaining_seconds": remaining_seconds,
        "started_at": started_at.isoformat(),
        "current_index": 0,
        "answers": {},
        "cauhoi": [serialize_question(item) for item in cau_hois],
    }


@router.post("/autosave")
def autosave_bai_thi(
    request: AutoSaveRequest,
    db: Session = Depends(get_db),
    user=Depends(require_permission(Permission.TAKE_EXAM)),
):
    session = db.query(DbPhienThi).filter(
        DbPhienThi.id == request.session_id,
        DbPhienThi.masv == user.get("ma")
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Khong tim thay phien thi"
        )

    remaining = calculate_remaining_seconds(session)
    if remaining <= 0:
        session.thoigian_conlai = 0
        session.trangthai = "HET_GIO"
        session.capnhat_luc = datetime.now()
        db.commit()
        return {"status": session.trangthai, "remaining_seconds": 0}

    if session.trangthai != "DANG_LAM":
        return {"status": session.trangthai, "remaining_seconds": remaining}

    session.dapan_dachon = json.dumps(request.answers)
    session.cauhoi_hientai = max(0, int(request.current_index or 0))
    session.thoigian_conlai = min(max(0, int(request.remaining_seconds or 0)), remaining)
    session.capnhat_luc = datetime.now()
    db.commit()

    return {
        "status": session.trangthai,
        "remaining_seconds": session.thoigian_conlai,
    }


@router.post("/nop-bai")
def nop_bai_thi(
    request: BaiNopRequest,
    db: Session = Depends(get_db),
    user=Depends(require_any_permission(Permission.TAKE_EXAM, Permission.PRACTICE_EXAM)),
):
    try:
        exam_date = datetime.strptime(request.ngaythi, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Ngay thi phai co dinh dang YYYY-MM-DD"
        )

    if user.get("role") != "SINHVIEN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chi sinh vien moi duoc nop bai thi chinh thuc"
        )

    sinh_vien = db.query(DbSinhVien).filter(DbSinhVien.masv == user.get("ma")).first()
    if not sinh_vien:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Khong tim thay sinh vien dang dang nhap"
        )

    if not sinh_vien.malop or sinh_vien.malop.strip() != request.malop.strip():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Khong duoc nop bai thi cua lop khac"
        )

    start_at = datetime.combine(exam_date, time.min)
    end_at = datetime.combine(exam_date, time.max)

    exam_info = db.query(DbGiaoVienDangKy).filter(
        DbGiaoVienDangKy.mamh == request.mamonhoc,
        DbGiaoVienDangKy.lan == request.lanthi,
        DbGiaoVienDangKy.malop == request.malop,
        and_(
            DbGiaoVienDangKy.ngaythi >= start_at,
            DbGiaoVienDangKy.ngaythi <= end_at
        )
    ).first()

    if not exam_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Khong tim thay lich thi phu hop"
        )

    existing_score = db.query(DbBangDiem).filter(
        DbBangDiem.masv == sinh_vien.masv,
        DbBangDiem.mamh == request.mamonhoc,
        DbBangDiem.lan == request.lanthi
    ).first()

    if existing_score:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bai thi nay da duoc nop, khong the nop lai"
        )

    session = None
    if request.session_id:
        session = db.query(DbPhienThi).filter(
            DbPhienThi.id == request.session_id,
            DbPhienThi.masv == sinh_vien.masv
        ).first()
    else:
        session = db.query(DbPhienThi).filter(
            DbPhienThi.masv == sinh_vien.masv,
            DbPhienThi.mamh == request.mamonhoc,
            DbPhienThi.lan == request.lanthi,
            DbPhienThi.malop == request.malop,
            DbPhienThi.ngaythi == exam_date,
            DbPhienThi.trangthai == "DANG_LAM"
        ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Khong tim thay phien thi dang lam"
        )

    if session.trangthai != "DANG_LAM":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Phien thi dang o trang thai {session.trangthai}, khong the nop bai"
        )

    submitted_answers = {}
    for question_id, selected_answer in request.answers.items():
        try:
            submitted_answers[int(question_id)] = (selected_answer or "").strip().upper()
        except ValueError:
            continue

    session_question_ids = parse_json_list(session.danhsach_cauhoi)
    submitted_answers = {
        question_id: answer
        for question_id, answer in submitted_answers.items()
        if question_id in session_question_ids
    }

    questions = db.query(DbBoDe).filter(
        DbBoDe.cauhoi.in_(session_question_ids),
        DbBoDe.mamh == exam_info.mamh
    ).all() if session_question_ids else []

    correct_count = 0
    for question in questions:
        selected_answer = submitted_answers.get(question.cauhoi)
        if selected_answer and selected_answer == (question.dap_an or "").strip().upper():
            correct_count += 1

    total_count = int(exam_info.socauthi or 0)
    score = round((correct_count / total_count) * 10, 2) if total_count > 0 else 0

    bang_diem = DbBangDiem(
        masv=sinh_vien.masv,
        mamh=request.mamonhoc,
        lan=request.lanthi,
        ngaythi=exam_date,
        diem=score
    )

    try:
        db.add(bang_diem)
        session.dapan_dachon = json.dumps(request.answers)
        session.thoigian_conlai = calculate_remaining_seconds(session)
        session.cauhoi_hientai = 0
        session.trangthai = "DA_NOP"
        session.nopbai_luc = datetime.now()
        session.capnhat_luc = session.nopbai_luc
        session.diem = score
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Loi database khi luu diem thi: {str(exc)}"
        )

    return {
        "message": "Nop bai thanh cong",
        "session_id": session.id,
        "masv": (sinh_vien.masv or "").strip(),
        "mamonhoc": request.mamonhoc.strip(),
        "lanthi": request.lanthi,
        "socauthi": total_count,
        "socaudung": correct_count,
        "diem": score,
    }
