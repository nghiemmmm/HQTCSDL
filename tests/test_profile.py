import sys
from sqlalchemy import text
sys.path.append(r"c:\Users\ASUS\Documents\PTIT\DOAN\HQTCSDL")
from db.database import engine

def main():
    try:
        with engine.connect() as conn:
            # Query 1: Check in GIAOVIEN table
            result = conn.execute(text("SELECT magv, ho, ten FROM GIAOVIEN WHERE magv = 'Trang'")).fetchone()
            print("--- QUERY GIAOVIEN TABLE FOR 'Trang' ---")
            print(f"Result in GIAOVIEN: {result}")
            
            # Query 2: Get all teachers to see if there is any 'Trang'
            all_teachers = conn.execute(text("SELECT magv, ho, ten FROM GIAOVIEN")).fetchall()
            print("\n--- ALL TEACHERS IN DATABASE ---")
            for t in all_teachers:
                print(f"MAGV: '{t.magv}' | Name: {t.ho} {t.ten}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
