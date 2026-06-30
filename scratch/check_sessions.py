import sys
sys.path.append('.')
from db.database import SessionLocal
from db.model import DbPhienThi

db = SessionLocal()
try:
    print("All DA_NOP sessions:")
    for s in db.query(DbPhienThi).filter(DbPhienThi.trangthai == "DA_NOP").all():
        print(f"ID: {s.id}, MASV: {s.masv}, MAMH: {s.mamh}, LAN: {s.lan}")
finally:
    db.close()
