import sys
sys.path.append(r"c:\Users\ASUS\Documents\PTIT\DOAN\HQTCSDL")
from db.database import SessionLocal
from db import db_user

def main():
    db = SessionLocal()
    try:
        row = db_user.find_sql_login(db, "Trang")
        print("--- TEST find_sql_login ---")
        print(f"Result for 'Trang': {row}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
