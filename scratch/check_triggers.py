import sys
sys.path.append('.')
from sqlalchemy import text
from db.database import SessionLocal

db = SessionLocal()
try:
    triggers = db.execute(text("""
        SELECT name, object_definition(object_id) as definition 
        FROM sys.triggers 
        WHERE parent_id = OBJECT_ID('GIAOVIEN_DANGKY')
    """)).fetchall()
    for t in triggers:
        print(f"--- Trigger: {t.name} ---")
        print(t.definition)
finally:
    db.close()
