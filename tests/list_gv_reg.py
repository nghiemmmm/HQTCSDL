import sys
from sqlalchemy import text
sys.path.append(r"c:\Users\ASUS\Documents\PTIT\DOAN\HQTCSDL")
from db.database import engine

def main():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT malop, mamh, lan, magv FROM GIAOVIEN_DANGKY WHERE magv = 'GV003'")).fetchall()
            print("--- GV003 REGISTRATIONS IN DB ---")
            for row in result:
                print(f"Lop: {row.malop.strip()} | Mon: {row.mamh.strip()} | Lan: {row.lan} | GV: {row.magv.strip()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
