import sys
sys.path.append('.')
from db.database import SessionLocal
from db import db_exam
from services.exam_service import build_history

db = SessionLocal()
try:
    user = {"role": "SINHVIEN", "ma": "SV001"}
    student = db_exam.get_student(db, "SV001")
    for registration in db_exam.list_registrations_for_class(db, student.malop):
        exam_date = registration.ngaythi.date() if registration.ngaythi else None
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
        
        result_url = (
            f"/thi/xem-lai?session_id={submitted.id}"
            if submitted
            else "/thi/xem-lai"
        )
        print(f"MAMH: {registration.mamh}, LAN: {registration.lan} -> submitted: {submitted}, url: {result_url}")
finally:
    db.close()
