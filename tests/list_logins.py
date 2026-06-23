import sys
from sqlalchemy import text
sys.path.append(r"c:\Users\ASUS\Documents\PTIT\DOAN\HQTCSDL")
from db.database import engine

def main():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT name, is_disabled FROM sys.server_principals WHERE type_desc = 'SQL_LOGIN'")).fetchall()
            print("--- LIST OF SQL LOGINS ---")
            for row in result:
                print(f"Login Name: '{row.name}' (Length: {len(row.name)}) | Disabled: {row.is_disabled}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
