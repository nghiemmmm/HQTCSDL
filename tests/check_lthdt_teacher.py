import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.database import connection_url
from db.model import DbGiaoVienDangKy, DbGiaoVien, DbMonHoc

def main():
    engine = create_engine(connection_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        registrations = db.query(DbGiaoVienDangKy).filter(DbGiaoVienDangKy.mamh == 'LTHDT').all()
        if not registrations:
            print("No registrations found for subject LTHDT.")
            return
            
        print(f"Found {len(registrations)} registration(s) for LTHDT:")
        for reg in registrations:
            teacher = db.query(DbGiaoVien).filter(DbGiaoVien.magv == reg.magv).first()
            subject = db.query(DbMonHoc).filter(DbMonHoc.mamh == reg.mamh).first()
            teacher_name = f"{teacher.ho.strip()} {teacher.ten.strip()}" if teacher else "Unknown"
            subject_name = subject.tenmh.strip() if subject else "Unknown"
            print(f"- Class: {reg.malop.strip()}, Attempt: {reg.lan}, Date: {reg.ngaythi}, Teacher: {reg.magv.strip()} ({teacher_name}), Subject: {reg.mamh.strip()} ({subject_name})")
    finally:
        db.close()

if __name__ == "__main__":
    main()
