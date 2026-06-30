"""Exam workflow, question selection, autosave, grading, and view models."""

import json
import math
import random
from datetime import date, datetime, timedelta
from typing import Any

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from db import db_exam
from db.model import DbBangDiem, DbBoDe, DbPhienThi
from schemas.schemas import AutoSaveRequest, BaiNopRequest
from services.exceptions import (
    ConflictError,
    PermissionDeniedError,
    RepositoryError,
    ResourceNotFoundError,
    ValidationError,
)

LOWER_LEVEL = {"A": "B", "B": "C"}


def parse_exam_date(value: str) -> date:
    """Parse the public API exam-date format."""
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise ValidationError("Ngay thi phai co dinh dang YYYY-MM-DD") from exc


def parse_json_dict(value: str | None) -> dict:
    """Parse a JSON object, returning an empty object for invalid data."""
    try:
        data = json.loads(value or "{}")
        return data if isinstance(data, dict) else {}
    except (TypeError, ValueError):
        return {}


def parse_json_list(value: str | None) -> list[int]:
    """Parse a JSON integer list."""
    try:
        data = json.loads(value or "[]")
        return [int(item) for item in data]
    except (TypeError, ValueError):
        return []



def calculate_remaining_seconds(session: DbPhienThi) -> int:
    """Calculate authoritative remaining seconds from the start time."""
    elapsed = int((datetime.now() - session.batdau_luc).total_seconds())
    return max(0, int(session.thoigian or 0) * 60 - elapsed)


def sync_session_time(db: Session, session: DbPhienThi) -> int:
    """Update stored time and expire a session when needed."""
    remaining = calculate_remaining_seconds(session)
    session.thoigian_conlai = remaining
    session.capnhat_luc = datetime.now()
    if remaining <= 0 and session.trangthai == "DANG_LAM":
        session.trangthai = "HET_GIO"
    db_exam.save_session(db, session)
    return remaining


def serialize_question(item: DbBoDe) -> dict:
    """Serialize a question without exposing its correct answer."""
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


def _student_for_user(db: Session, user: dict[str, Any]):
    student = db_exam.get_student(db, user.get("ma", ""))
    if student is None:
        raise ResourceNotFoundError("Khong tim thay sinh vien dang dang nhap")
    return student


def _assert_student_class(student, class_id: str, detail: str) -> None:
    if not student.malop:
        raise ResourceNotFoundError("Sinh vien chua duoc phan lop")
    if student.malop.strip() != class_id.strip():
        raise PermissionDeniedError(detail)


def get_student_class(db: Session, student_id: str, user: dict[str, Any]):
    """Return a student's class while enforcing ownership."""
    if user.get("role") == "SINHVIEN" and student_id != user.get("ma"):
        raise PermissionDeniedError(
            "Khong duoc xem thong tin lop cua sinh vien khac"
        )
    student = db_exam.get_student(db, student_id)
    if student is None:
        raise ResourceNotFoundError("Không tìm thấy sinh viên với mã này")
    if student.lop is None:
        raise ResourceNotFoundError("Sinh viên chưa được phân lớp")
    return student.lop


def list_available_subjects(db: Session, user: dict[str, Any]):
    """Return subjects available to the current exam actor."""
    if user.get("role") == "SINHVIEN":
        student = _student_for_user(db, user)
        if not student.malop:
            raise ResourceNotFoundError("Sinh vien chua duoc phan lop")
        return db_exam.list_subjects_for_class(db, student.malop)

    from db.model import DbMonHoc, DbGiaoVienDangKy
    magv = user.get("ma")
    return (
        db.query(DbMonHoc)
        .join(DbGiaoVienDangKy, DbMonHoc.mamh == DbGiaoVienDangKy.mamh)
        .filter(DbGiaoVienDangKy.magv == magv)
        .distinct()
        .all()
    )


def _get_row_value(row, key: str, index: int):
    mapping = getattr(row, "_mapping", None)
    if mapping is not None and key in mapping:
        return mapping[key]
    return row[index]


def _to_bool(value) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value == 1
    if isinstance(value, str):
        return value.strip() in {"1", "True", "true"}
    return bool(value)


def list_student_exam_schedules(db: Session, user: dict[str, Any]) -> list[dict]:
    """Return exam schedules for the logged-in student only."""
    if user.get("role") != "SINHVIEN":
        raise PermissionDeniedError("Chi sinh vien moi duoc xem lich thi cua minh")

    student = _student_for_user(db, user)
    if not student.malop:
        raise ResourceNotFoundError("Sinh vien chua duoc phan lop")

    try:
        rows = db_exam.list_exam_schedules_for_student(db, student.masv)
    except SQLAlchemyError as exc:
        raise RepositoryError(f"Khong the lay lich thi cua sinh vien: {exc}") from exc

    schedules: list[dict] = []
    for row in rows:
        exam_date = _get_row_value(row, "NGAYTHI", 3)
        thoigian = int(_get_row_value(row, "THOIGIAN", 5) or 0)
        if exam_date and datetime.now() > exam_date + timedelta(minutes=thoigian):
            continue

        schedules.append(
            {
                "mamh": (_get_row_value(row, "MAMH", 0) or "").strip(),
                "tenmh": (_get_row_value(row, "TENMH", 1) or "").strip(),
                "lan": int(_get_row_value(row, "LAN", 2) or 0),
                "ngaythi": exam_date.isoformat() if exam_date else "",
                "ngaythi_text": (
                    exam_date.strftime("%d/%m/%Y %H:%M") if exam_date else ""
                ),
                "socauthi": int(_get_row_value(row, "SOCAUTHI", 4) or 0),
                "thoigian": thoigian,
                "trangthai": (_get_row_value(row, "TRANGTHAI", 6) or "").strip(),
                "duoc_bat_dau_thi": _to_bool(
                    _get_row_value(row, "DUOC_BAT_DAU_THI", 7)
                ),
                "malop": (student.malop or "").strip(),
            }
        )

    today_val = date.today()
    def sort_key(s_dict: dict) -> tuple:
        dt_str = s_dict["ngaythi"]
        dt = datetime.fromisoformat(dt_str) if dt_str else datetime.max
        is_today = (dt.date() == today_val)
        return (0 if is_today else 1, dt)

    schedules.sort(key=sort_key)
    return schedules


def list_available_classes(db: Session, user: dict[str, Any]):
    """Return classes registered by the teacher for practice."""
    from db.model import DbLop, DbGiaoVienDangKy
    magv = user.get("ma")
    return (
        db.query(DbLop)
        .join(DbGiaoVienDangKy, DbLop.malop == DbGiaoVienDangKy.malop)
        .filter(DbGiaoVienDangKy.magv == magv)
        .distinct()
        .all()
    )


def get_exam_info(
    db: Session,
    subject_id: str,
    attempt: int,
    class_id: str,
    exam_date_value: str,
    user: dict[str, Any],
):
    """Return a validated exam registration."""
    exam_date = parse_exam_date(exam_date_value)
    if user.get("role") == "SINHVIEN":
        _assert_student_class(
            _student_for_user(db, user),
            class_id,
            "Khong duoc xem lich thi cua lop khac",
        )
    registration = db_exam.get_registration(
        db, subject_id, attempt, class_id, exam_date
    )
    if registration is None:
        raise ResourceNotFoundError(
            "Khong tim thay lich thi phu hop voi mon, lop, ngay thi va lan thi da chon"
        )
    if user.get("role") == "SINHVIEN":
        active_session = db_exam.get_latest_session(
            db,
            user.get("ma", ""),
            subject_id,
            attempt,
            class_id,
            exam_date,
            "DANG_LAM",
        )
        if active_session:
            sync_session_time(db, active_session)
            if active_session.trangthai == "DANG_LAM":
                registration.active_session_status = "DANG_LAM"
                registration.active_session_message = (
                    "Bai thi nay chua hoan thanh. "
                    "Tiep tuc lam bai de hoan tat bai thi nay."
                )
    return registration


def _select_questions(db: Session, registration) -> list[DbBoDe]:
    """Select exam questions applying the 70/30 distribution rule."""
    from db.model import DbBoDe
    import random
    import math

    required = int(registration.socauthi or 0)
    level = (registration.trinhdo or "").strip()
    mamh = (registration.mamh or "").strip()

    main_questions = db.query(DbBoDe).filter(
        DbBoDe.mamh == mamh,
        DbBoDe.trinhdo == level
    ).all()
    
    if len(main_questions) >= required:
        return random.sample(main_questions, required)
        
    min_main_required = math.ceil(0.7 * required)
    if len(main_questions) < min_main_required:
        raise ConflictError(
            f"Không đủ câu hỏi thi cho môn {mamh} trình độ {level}. "
            f"Yêu cầu tối thiểu {min_main_required} câu (70%), hệ thống chỉ có {len(main_questions)} câu."
        )
        
    lower_level = 'B' if level == 'A' else ('C' if level == 'B' else None)
    if not lower_level:
        raise ConflictError(
            f"Không đủ câu hỏi thi cho môn {mamh} trình độ {level}. "
            f"Yêu cầu {required} câu, hệ thống chỉ có {len(main_questions)} câu."
        )
        
    needed_from_lower = required - len(main_questions)
    lower_questions = db.query(DbBoDe).filter(
        DbBoDe.mamh == mamh,
        DbBoDe.trinhdo == lower_level
    ).all()
    
    if len(lower_questions) < needed_from_lower:
        raise ConflictError(
            f"Không đủ câu hỏi thi bù từ trình độ {lower_level}. "
            f"Cần thêm {needed_from_lower} câu, hệ thống chỉ có {len(lower_questions)} câu."
        )
        
    selected_main = main_questions
    selected_lower = random.sample(lower_questions, needed_from_lower)
    
    final_selection = selected_main + selected_lower
    random.shuffle(final_selection)
    return final_selection


def _ensure_student_can_start_exam(
    db: Session,
    user: dict[str, Any],
    registration,
    exam_date: date,
) -> None:
    """Prevent students from starting exams outside the registered date."""
    if user.get("role") != "SINHVIEN":
        return

    student_id = user.get("ma", "")
    if db_exam.get_score(db, student_id, registration.mamh, registration.lan):
        raise ConflictError("Đã thi")

    today = date.today()
    if exam_date > today:
        raise ConflictError("Chưa đến ngày thi")
    if exam_date < today:
        raise ConflictError("Đã quá hạn")


def get_or_create_exam(
    db: Session,
    subject_id: str,
    attempt: int,
    class_id: str,
    exam_date_value: str,
    user: dict[str, Any],
) -> dict:
    """Resume an active session or create a new randomized exam."""
    exam_date = parse_exam_date(exam_date_value)
    registration = get_exam_info(
        db, subject_id, attempt, class_id, exam_date_value, user
    )
    _ensure_student_can_start_exam(db, user, registration, exam_date)
    if user.get("role") == "SINHVIEN":
        existing = db_exam.get_latest_session(
            db,
            user.get("ma", ""),
            subject_id,
            attempt,
            class_id,
            exam_date,
        )
        if existing:
            remaining = sync_session_time(db, existing)
            if existing.trangthai != "DANG_LAM":
                if existing.trangthai == "DA_NOP":
                    raise ConflictError(
                        "Ban da hoan thanh bai thi nay roi, khong duoc phep thi lai"
                    )
                raise ConflictError(
                    f"Phien thi dang o trang thai {existing.trangthai}, "
                    "khong the tao phien moi"
                )
            ids = parse_json_list(existing.danhsach_cauhoi)
            by_id = {
                item.cauhoi: item
                for item in db_exam.get_questions_by_ids(db, ids)
            }
            questions = [by_id[item] for item in ids if item in by_id]
            return _exam_payload(existing, questions, remaining)

    questions = _select_questions(db, registration)
    started_at = datetime.now()
    remaining = int(registration.thoigian or 0) * 60
    session = None
    if user.get("role") == "SINHVIEN":
        session = DbPhienThi(
            masv=user.get("ma"),
            malop=class_id,
            mamh=(registration.mamh or "").strip(),
            trinhdo=(registration.trinhdo or "").strip(),
            lan=registration.lan,
            socauthi=registration.socauthi,
            thoigian=registration.thoigian,
            ngaythi=exam_date,
            batdau_luc=started_at,
            thoigian_conlai=remaining,
            trangthai="DANG_LAM",
            danhsach_cauhoi=json.dumps([item.cauhoi for item in questions]),
            dapan_dachon="{}",
            cauhoi_hientai=0,
            capnhat_luc=started_at,
        )
        try:
            session = db_exam.create_session(db, session)
        except SQLAlchemyError as exc:
            db.rollback()
            raise RepositoryError(
                f"Loi database khi tao phien thi: {exc}"
            ) from exc
    return {
        "session_id": session.id if session else None,
        "session_status": "DANG_LAM",
        "mamonhoc": (registration.mamh or "").strip(),
        "malop": (registration.malop or "").strip(),
        "lanthi": registration.lan,
        "ngaythi": exam_date.isoformat(),
        "trinhdo": (registration.trinhdo or "").strip(),
        "socauthi": registration.socauthi,
        "thoigian": registration.thoigian,
        "remaining_seconds": remaining,
        "started_at": started_at.isoformat(),
        "current_index": 0,
        "answers": {},
        "cauhoi": [serialize_question(item) for item in questions],
    }


def _exam_payload(
    session: DbPhienThi,
    questions: list[DbBoDe],
    remaining: int,
) -> dict:
    return {
        "session_id": session.id,
        "session_status": session.trangthai,
        "mamonhoc": (session.mamh or "").strip(),
        "malop": (session.malop or "").strip(),
        "lanthi": session.lan,
        "ngaythi": session.ngaythi.isoformat(),
        "trinhdo": (session.trinhdo or "").strip(),
        "socauthi": session.socauthi,
        "thoigian": session.thoigian,
        "remaining_seconds": remaining,
        "started_at": session.batdau_luc.isoformat(),
        "current_index": session.cauhoi_hientai,
        "answers": parse_json_dict(session.dapan_dachon),
        "cauhoi": [serialize_question(item) for item in questions],
    }


def autosave(
    db: Session,
    request: AutoSaveRequest,
    user: dict[str, Any],
) -> dict:
    """Persist answer progress for an active student session."""
    session = db_exam.get_session(db, request.session_id, user.get("ma", ""))
    if session is None:
        raise ResourceNotFoundError("Khong tim thay phien thi")
    remaining = calculate_remaining_seconds(session)
    if remaining <= 0:
        session.thoigian_conlai = 0
        session.trangthai = "HET_GIO"
    elif session.trangthai == "DANG_LAM":
        session.dapan_dachon = json.dumps(request.answers)
        session.cauhoi_hientai = max(0, int(request.current_index or 0))
        session.thoigian_conlai = min(
            max(0, int(request.remaining_seconds or 0)),
            remaining,
        )
    session.capnhat_luc = datetime.now()
    db_exam.save_session(db, session)
    return {
        "status": session.trangthai,
        "remaining_seconds": session.thoigian_conlai,
    }


def submit(
    db: Session,
    request: BaiNopRequest,
    user: dict[str, Any],
) -> dict:
    """Grade and atomically persist a submitted exam."""
    role = user.get("role")
    is_practice = (role != "SINHVIEN")
    exam_date = parse_exam_date(request.ngaythi)

    registration = db_exam.get_registration(
        db,
        request.mamonhoc,
        request.lanthi,
        request.malop,
        exam_date,
    )
    if registration is None:
        raise ResourceNotFoundError("Khong tim thay lich thi phu hop")

    total = int(registration.socauthi or 0)

    if is_practice:
        # Grade the practice exam temporarily on the backend (no DB session writes)
        q_ids = [int(k) for k in request.answers.keys() if str(k).isdigit()]
        questions = db_exam.get_questions_by_ids(db, q_ids, registration.mamh)
        correct = sum(
            1
            for question in questions
            if (request.answers.get(str(question.cauhoi)) or "").strip().upper()
            == (question.dap_an or "").strip().upper()
        )
        score_value = round(correct / total * 10, 2) if total else 0
        return {
            "message": "Nop bai thi thu thanh cong",
            "session_id": None,
            "masv": user.get("ma", ""),
            "mamonhoc": request.mamonhoc.strip(),
            "lanthi": request.lanthi,
            "socauthi": total,
            "socaudung": correct,
            "diem": score_value,
            "practice": True,
        }

    # Student submission flow (persisted in DB)
    student = _student_for_user(db, user)
    actor_id = student.masv
    _assert_student_class(
        student,
        request.malop,
        "Khong duoc nop bai thi cua lop khac",
    )

    if db_exam.has_student_taken_exam(db, actor_id, request.mamonhoc, request.lanthi):
        raise ConflictError("Bai thi nay da duoc nop, khong the nop lai")

    session = (
        db_exam.get_session(db, request.session_id, actor_id)
        if request.session_id
        else db_exam.get_latest_session(
            db,
            actor_id,
            request.mamonhoc,
            request.lanthi,
            request.malop,
            exam_date,
            "DANG_LAM",
        )
    )
    if session is None:
        raise ResourceNotFoundError("Khong tim thay phien thi dang lam")
    if session.trangthai != "DANG_LAM":
        raise ConflictError(
            f"Phien thi dang o trang thai {session.trangthai}, khong the nop bai"
        )

    answers = {
        int(question_id): (answer or "").strip().upper()
        for question_id, answer in request.answers.items()
        if str(question_id).isdigit()
    }
    ids = parse_json_list(session.danhsach_cauhoi)
    answers = {key: value for key, value in answers.items() if key in ids}
    questions = db_exam.get_questions_by_ids(db, ids, registration.mamh)
    correct = sum(
        1
        for question in questions
        if answers.get(question.cauhoi)
        == (question.dap_an or "").strip().upper()
    )
    score_value = round(correct / total * 10, 2) if total else 0
    session.thoigian_conlai = calculate_remaining_seconds(session)
    session.cauhoi_hientai = 0

    try:
        db_exam.submit_exam_with_procedure(
            db,
            session_id=session.id,
            score_value=score_value,
            answers_json=json.dumps(request.answers),
        )
        db.commit()
        db.refresh(session)
    except SQLAlchemyError as exc:
        db.rollback()
        raise RepositoryError(f"Loi database khi luu diem thi: {exc}") from exc

    return {
        "message": "Nop bai thanh cong",
        "session_id": session.id,
        "masv": actor_id,
        "mamonhoc": request.mamonhoc.strip(),
        "lanthi": request.lanthi,
        "socauthi": total,
        "socaudung": correct,
        "diem": score_value,
        "practice": False,
    }


def build_history(db: Session, user: dict[str, Any]) -> dict:
    """Build the template context for a student's exam history."""
    student = _student_for_user(db, user)
    if not student.malop:
        raise ResourceNotFoundError("Sinh vien chua duoc phan lop")
    now = datetime.now()
    unfinished: list[dict] = []
    recent: list[dict] = []
    subjects: dict[str, str] = {}
    for registration in db_exam.list_registrations_for_class(db, student.malop):
        subject = db_exam.get_subject(db, registration.mamh)
        score = db_exam.get_score(
            db, student.masv, registration.mamh, registration.lan
        )
        code = (registration.mamh or "").strip()
        name = (subject.tenmh or "").strip() if subject else code
        subjects[code] = name
        start_at = registration.ngaythi
        duration = int(registration.thoigian or 0)
        end_at = start_at + timedelta(minutes=duration) if start_at else None
        exam_date = start_at.date() if start_at else None
        active = (
            db_exam.get_latest_session(
                db,
                student.masv,
                registration.mamh,
                registration.lan,
                registration.malop,
                exam_date,
                "DANG_LAM",
            )
            if exam_date
            else None
        )
        submitted = (
            db_exam.get_latest_session(
                db,
                student.masv,
                registration.mamh,
                registration.lan,
                registration.malop,
                exam_date,
                "DA_NOP",
            )
            if exam_date
            else None
        )
        remaining = sync_session_time(db, active) if active else None
        if active and active.trangthai != "DANG_LAM":
            active = None
        if score:
            label, key, action = "Đã nộp", "da-nop", "Xem kết quả"
        elif active:
            label, key, action = "Đang làm", "dang-lam", "Tiếp tục làm bài"
        elif start_at and now < start_at:
            label, key, action = "Chưa thi", "chua-thi", "Chưa mở"
        elif start_at and end_at and start_at <= now <= end_at:
            label, key, action = "Đang làm", "dang-lam", "Tiếp tục làm bài"
        else:
            label, key, action = "Hết hạn", "het-han", "Bỏ lỡ"
        date_text = exam_date.isoformat() if exam_date else ""
        exam_url = (
            f"/thi/lam-bai?mamonhoc={code}&lanthi={registration.lan}"
            f"&malop={(registration.malop or '').strip()}&ngaythi={date_text}"
        )
        result_url = (
            f"/thi/xem-lai?session_id={submitted.id}"
            if submitted
            else None
        )
        item = {
            "title": f"Đề thi {name} - Lần {registration.lan}",
            "subject_code": code,
            "subject_name": name,
            "status": label,
            "status_key": key,
            "start_at": (
                start_at.strftime("%d/%m/%Y %H:%M") if start_at else "Chưa có"
            ),
            "start_iso": start_at.isoformat() if start_at else "",
            "end_at": end_at.strftime("%d/%m/%Y %H:%M") if end_at else "Chưa có",
            "duration": f"{duration} phút" if duration else "Chưa có",
            "started_text": (
                active.batdau_luc.strftime("%d/%m/%Y %H:%M") if active else None
            ),
            "remaining_text": (
                f"{remaining // 3600:02d}:{(remaining % 3600) // 60:02d}:"
                f"{remaining % 60:02d}"
                if remaining is not None
                else None
            ),
            "score": score.diem if score else None,
            "action_label": action,
            "action_url": exam_url if key == "dang-lam" else (result_url if key != "chua-thi" else None),
            "detail_url": result_url,
        }
        (recent if score else unfinished).append(item)
    return {
        "unfinished_exams": unfinished,
        "recent_exams": recent,
        "subjects": [
            {"code": code, "name": name}
            for code, name in sorted(subjects.items(), key=lambda item: item[1])
        ],
    }


def build_review(
    db: Session,
    user: dict[str, Any],
    session_id: int | None,
) -> dict:
    """Build the submitted-exam review context."""
    if user.get("role") == "SINHVIEN":
        student = _student_for_user(db, user)
        session = db_exam.get_latest_submitted_session(db, student.masv, session_id)
    else:
        query = db.query(DbPhienThi).filter(DbPhienThi.trangthai == "DA_NOP")
        if session_id is not None:
            query = query.filter(DbPhienThi.id == session_id)
        session = query.order_by(DbPhienThi.nopbai_luc.desc(), DbPhienThi.id.desc()).first()
        student = db_exam.get_student(db, session.masv) if session else None

    if session is None or student is None:
        return {"has_result": False}
    subject = db_exam.get_subject(db, session.mamh)
    class_info = db_exam.get_class(db, session.malop)
    score = db_exam.get_score(db, student.masv, session.mamh, session.lan)

    import json
    from db.model import DbBoDe

    try:
        question_ids = json.loads(session.danhsach_cauhoi) if session.danhsach_cauhoi else []
    except Exception:
        question_ids = []
        
    try:
        student_answers = json.loads(session.dapan_dachon) if session.dapan_dachon else {}
    except Exception:
        student_answers = {}

    questions = db.query(DbBoDe).filter(DbBoDe.cauhoi.in_(question_ids)).all() if question_ids else []
    q_map = {q.cauhoi: q for q in questions}

    rows = []
    for q_id in question_ids:
        q = q_map.get(q_id)
        if q:
            ans = student_answers.get(str(q_id), "")
            rows.append((q.cauhoi, q.noidung, q.a, q.b, q.c, q.d, q.dap_an, ans))

    results: list[dict] = []
    correct_count = wrong_count = unanswered_count = 0
    for number, row in enumerate(rows, start=1):
        q_id = row[0]
        noidung = row[1]
        q_a = row[2]
        q_b = row[3]
        q_c = row[4]
        q_d = row[5]
        correct = (row[6] or "").strip().upper()
        answer = (row[7] or "").strip().upper()

        if not answer:
            key, label = "unanswered", "Chưa trả lời"
            unanswered_count += 1
        elif answer == correct:
            key, label = "correct", "Đúng"
            correct_count += 1
        else:
            key, label = "wrong", "Sai"
            wrong_count += 1

        options = []
        for option_key, text_val in (
            ("A", q_a),
            ("B", q_b),
            ("C", q_c),
            ("D", q_d),
        ):
            state, icon = "neutral", ""
            if option_key == answer == correct:
                state, icon = "correct", "✓"
            elif option_key == answer and answer != correct:
                state, icon = "wrong", "✕"
            elif option_key == correct:
                state, icon = "missed-correct", "✓"
            options.append(
                {"key": option_key, "text": text_val, "state": state, "icon": icon}
            )
        results.append(
            {
                "number": number,
                "question_id": q_id,
                "text": noidung,
                "a": q_a,
                "b": q_b,
                "c": q_c,
                "d": q_d,
                "status_key": key,
                "status_label": label,
                "selected_answer": answer or "Chưa trả lời",
                "correct_answer": correct,
                "options": options,
            }
        )
    total = len(results)
    answered = total - unanswered_count
    final_score = score.diem if score else session.diem
    submitted_at = session.nopbai_luc or session.capnhat_luc
    used_seconds = (
        max(0, int((submitted_at - session.batdau_luc).total_seconds()))
        if submitted_at and session.batdau_luc
        else max(
            0,
            int(session.thoigian or 0) * 60
            - int(session.thoigian_conlai or 0),
        )
    )
    return {
        "has_result": True,
        "overview": {
            "exam_title": (
                f"Đề thi "
                f"{(subject.tenmh or '').strip() if subject else session.mamh} "
                f"- Lần {session.lan}"
            ),
            "subject": (
                (subject.tenmh or "").strip() if subject else session.mamh
            ),
            "class_name": (
                f"{(class_info.malop or '').strip()} - {class_info.tenlop}"
                if class_info
                else session.malop
            ),
            "class_code": (session.malop or "").strip(),
            "attempt": session.lan,
            "level": (session.trinhdo or "").strip(),
            "student_name": (
                f"{(student.ho or '').strip()} {(student.ten or '').strip()}"
            ).strip(),
            "student_code": (student.masv or "").strip(),
            "exam_date": (
                session.ngaythi.strftime("%d/%m/%Y") if session.ngaythi else ""
            ),
            "started_at": session.batdau_luc.strftime("%d/%m/%Y %H:%M:%S"),
            "duration": f"{used_seconds // 60} phút {used_seconds % 60:02d} giây",
            "submitted_at": (
                submitted_at.strftime("%d/%m/%Y %H:%M:%S")
                if submitted_at
                else "Chưa có"
            ),
            "total_count": total,
            "correct_count": correct_count,
            "wrong_count": wrong_count,
            "unanswered_count": unanswered_count,
            "final_score": final_score,
            "pass_status": "Đạt" if (final_score or 0) >= 5 else "Không đạt",
            "pass_key": "pass" if (final_score or 0) >= 5 else "fail",
        },
        "quick_stats": {
            "total_count": total,
            "correct_count": correct_count,
            "wrong_count": wrong_count,
            "unanswered_count": unanswered_count,
            "completion_rate": round(answered / total * 100) if total else 0,
            "accuracy_rate": round(correct_count / total * 100, 1) if total else 0,
            "correct_ratio": f"{correct_count}/{total} câu",
            "final_score": final_score,
        },
        "question_results": results,
    }


def get_class_score_table(
    db: Session,
    malop: str,
    mamh: str,
    lan: int,
    user: dict | None = None,
) -> list[dict]:
    """Get the score sheet for a class, subject, and attempt."""
    from sqlalchemy import text
    from core.report_utils import score_to_words, score_to_letter

    malop = malop.strip()
    mamh = mamh.strip()

    if user and user.get("role") == "GIANGVIEN":
        teacher_id = (user.get("ma") or "").strip()
        from db.model import DbGiaoVienDangKy
        reg = (
            db.query(DbGiaoVienDangKy)
            .filter(
                DbGiaoVienDangKy.malop == malop,
                DbGiaoVienDangKy.mamh == mamh,
                DbGiaoVienDangKy.lan == lan,
                DbGiaoVienDangKy.magv == teacher_id,
            )
            .first()
        )
        if reg is None:
            raise PermissionDeniedError(
                "Bạn không có quyền xem bảng điểm của lịch thi này."
            )

    query = text("""
        SELECT 
            SV.MASV,
            SV.HO,
            SV.TEN,
            BD.DIEM
        FROM SINHVIEN SV
        LEFT JOIN BANGDIEM BD ON SV.MASV = BD.MASV AND BD.MAMH = :mamh AND BD.LAN = :lan
        WHERE SV.MALOP = :malop
        ORDER BY SV.TEN, SV.HO
    """)
    rows = db.execute(query, {"malop": malop, "mamh": mamh, "lan": lan}).fetchall()

    results = []
    for idx, row in enumerate(rows, start=1):
        masv = row[0]
        ho = row[1]
        ten = row[2]
        score_val = row[3]

        results.append({
            "stt": idx,
            "masv": (masv or "").strip(),
            "ho": (ho or "").strip(),
            "ten": (ten or "").strip(),
            "diem": score_val if score_val is not None else "Chưa thi",
            "diem_chu": score_to_letter(score_val) if score_val is not None else "",
            "diem_chu_viet": score_to_words(score_val) if score_val is not None else "",
        })

    return results

def list_class_exam_results(
    db: Session, malop: str, mamh: str, lan: int, user: dict | None = None
) -> list[dict]:
    """Return all student results for a specific exam, used in Ket qua sinh vien."""
    from db.model import DbSinhVien, DbBangDiem, DbGiaoVienDangKy
    
    malop = malop.strip()
    mamh = mamh.strip()
    
    if user and user.get("role") == "GIANGVIEN":
        teacher_id = (user.get("ma") or "").strip()
        reg = (
            db.query(DbGiaoVienDangKy)
            .filter(
                DbGiaoVienDangKy.malop == malop,
                DbGiaoVienDangKy.mamh == mamh,
                DbGiaoVienDangKy.lan == lan,
                DbGiaoVienDangKy.magv == teacher_id,
            )
            .first()
        )
        if reg is None:
            raise PermissionDeniedError(
                "Bạn không có quyền xem kết quả của lịch thi này."
            )
            
    students = (
        db.query(DbSinhVien, DbBangDiem.diem)
        .outerjoin(
            DbBangDiem,
            (DbSinhVien.masv == DbBangDiem.masv) &
            (DbBangDiem.mamh == mamh) &
            (DbBangDiem.lan == lan)
        )
        .filter(DbSinhVien.malop == malop)
        .order_by(DbSinhVien.ten, DbSinhVien.ho)
        .all()
    )
    
    results = []
    for sv, diem in students:
        hoten = f"{sv.ho or ''} {sv.ten or ''}".strip()
        results.append({
            "masv": sv.masv.strip(),
            "hoten": hoten,
            "diem": diem if diem is not None else None
        })
    return results



def list_all_classes(db: Session, user: dict | None = None) -> list:
    """Return classes for selection. Teachers only see classes where they registered exams."""
    if user and user.get("role") == "GIANGVIEN":
        teacher_id = (user.get("ma") or "").strip()
        return db_exam.list_classes_by_teacher(db, teacher_id)
    from db.model import DbLop
    return db.query(DbLop).order_by(DbLop.malop.asc()).all()


def list_all_subjects(db: Session, user: dict | None = None) -> list:
    """Return subjects for selection. Teachers only see subjects they registered exams for."""
    if user and user.get("role") == "GIANGVIEN":
        teacher_id = (user.get("ma") or "").strip()
        return db_exam.list_subjects_by_teacher(db, teacher_id)
    return db_exam.list_all_subjects(db)


def list_teacher_registrations(db: Session, user: dict) -> list:
    """Return all exam registrations for the current teacher, newest first."""
    if user.get("role") != "GIANGVIEN":
        raise PermissionDeniedError("Chỉ giảng viên mới có danh sách kỳ thi đăng ký.")
    teacher_id = (user.get("ma") or "").strip()
    return db_exam.list_registrations_by_teacher(db, teacher_id)


def list_students_by_class(db: Session, malop: str):
    """Return short student profile list in a class."""
    from db.model import DbSinhVien
    from schemas.schemas import StudentShortResponse
    students = (
        db.query(DbSinhVien)
        .filter(DbSinhVien.malop == malop.strip())
        .order_by(DbSinhVien.ten.asc(), DbSinhVien.ho.asc())
        .all()
    )
    return [
        StudentShortResponse(
            masv=s.masv.strip(),
            hoten=f"{(s.ho or '').strip()} {(s.ten or '').strip()}".strip()
        )
        for s in students
    ]


def lookup_exam_result(db: Session, masv: str, mamh: str, lan: int):
    """Look up details of a student's submitted exam."""
    from db.model import DbPhienThi, DbBoDe
    from schemas.schemas import TraCuuBaiThiResponse
    
    session = (
        db.query(DbPhienThi)
        .filter(
            DbPhienThi.masv == masv.strip(),
            DbPhienThi.mamh == mamh.strip(),
            DbPhienThi.lan == lan,
            DbPhienThi.trangthai == "DA_NOP"
        )
        .order_by(DbPhienThi.nopbai_luc.desc())
        .first()
    )
    
    if not session:
        return TraCuuBaiThiResponse()
        
    ids = parse_json_list(session.danhsach_cauhoi)
    total_count = len(ids)
    selected = {
        int(key): (value or "").strip().upper()
        for key, value in parse_json_dict(session.dapan_dachon).items()
        if str(key).isdigit()
    }
    
    correct_count = 0
    if total_count > 0:
        questions = (
            db.query(DbBoDe)
            .filter(DbBoDe.cauhoi.in_(ids))
            .all()
        )
        by_id = {q.cauhoi: (q.dap_an or "").strip().upper() for q in questions}
        for q_id in ids:
            ans = selected.get(q_id, "")
            if ans and ans == by_id.get(q_id):
                correct_count += 1
                
    submitted_at = session.nopbai_luc or session.capnhat_luc
    submitted_at_str = submitted_at.strftime("%d/%m/%Y %H:%M:%S") if submitted_at else None
    
    return TraCuuBaiThiResponse(
        session_id=session.id,
        score=session.diem,
        correct_count=correct_count,
        total_count=total_count,
        submitted_at=submitted_at_str
    )


def build_student_scores(db: Session, user: dict[str, Any]) -> dict:
    """Build the context for the student's personal scores page."""
    from core.report_utils import score_to_letter
    student = _student_for_user(db, user)
    
    rows = db_exam.get_student_subjects_taken(db, student.masv)
    scores_list = []
    
    for idx, row in enumerate(rows, start=1):
        mamh = (row[0] or "").strip()
        tenmh = (row[1] or "").strip()
        
        # Get attempt 1 score
        score1_obj = db_exam.get_score(db, student.masv, mamh, 1)
        score1 = score1_obj.diem if score1_obj else None
        
        # Get attempt 2 score
        score2_obj = db_exam.get_score(db, student.masv, mamh, 2)
        score2 = score2_obj.diem if score2_obj else None
        
        # Calculate highest score
        scores = [s for s in (score1, score2) if s is not None]
        highest = max(scores) if scores else None
        
        status_label = "Chưa đạt"
        status_class = "unpassed"
        if highest is not None and highest >= 4.0:
            status_label = "Đạt"
            status_class = "passed"
            
        scores_list.append({
            "stt": idx,
            "mamh": mamh,
            "tenmh": tenmh,
            "score1": f"{score1:.2f}" if score1 is not None else "-",
            "score2": f"{score2:.2f}" if score2 is not None else "-",
            "highest": f"{highest:.2f}" if highest is not None else "-",
            "highest_letter": score_to_letter(highest) if highest is not None else "-",
            "status_label": status_label,
            "status_class": status_class,
        })
        
    return {
        "student_name": f"{(student.ho or '').strip()} {(student.ten or '').strip()}",
        "student_code": student.masv,
        "class_name": student.malop,
        "scores": scores_list
    }
