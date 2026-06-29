import sys
sys.path.append('.')
from sqlalchemy import text
from db.database import SessionLocal

db = SessionLocal()
try:
    query = text("""
        SELECT 
            GV.MAGV, 
            GV.HO, 
            GV.TEN,
            CASE WHEN DP.name IS NOT NULL THEN 'Da co tai khoan' ELSE '' END AS TRANGTHAI,
            SP.name AS LOGINNAME,
            R.name AS ROLENAME
        FROM GIAOVIEN GV
        LEFT JOIN sys.database_principals DP ON GV.MAGV = DP.name
        LEFT JOIN sys.server_principals SP ON DP.sid = SP.sid
        LEFT JOIN sys.database_role_members RM ON DP.principal_id = RM.member_principal_id
        LEFT JOIN sys.database_principals R ON RM.role_principal_id = R.principal_id
    """)
    rows = db.execute(query).fetchall()
    for row in rows:
        print(row)
finally:
    db.close()
