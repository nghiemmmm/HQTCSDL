import sys
from sqlalchemy import text
sys.path.append(r"c:\Users\ASUS\Documents\PTIT\DOAN\HQTCSDL")
from db.database import engine

def main():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("EXEC sp_helptext 'sp_ThongTinDangNhap'")).fetchall()
            print("--- DEFINITION OF sp_ThongTinDangNhap ---")
            for row in result:
                print(row[0], end="")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
