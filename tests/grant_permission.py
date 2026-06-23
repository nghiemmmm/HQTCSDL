import sys
from sqlalchemy import text
sys.path.append(r"c:\Users\ASUS\Documents\PTIT\DOAN\HQTCSDL")
from db.database import engine

def main():
    queries = [
        "USE THITRACNGHIEM;",
        "GRANT EXECUTE ON OBJECT::dbo.sp_ThongTinDangNhap TO public;"
    ]
    with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
        for q in queries:
            print(f"Executing: {q}")
            conn.execute(text(q))
        print("--- CAP QUYEN THANH CONG ---")

if __name__ == "__main__":
    main()
