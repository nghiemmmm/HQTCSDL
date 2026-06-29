"""Teacher repository containing database operations only."""

from sqlalchemy import or_, text
from sqlalchemy.orm import Session

from db.model import DbGiaoVien
from schemas.schemas import GiaoVienCreate, GiaoVienUpdate


def get_all_gv(db: Session) -> list[DbGiaoVien]:
    """Return all teachers."""
    return db.query(DbGiaoVien).all()


def get_ds_gv_chua_quyen(db: Session) -> list:
    """Return rows from the unregistered-teacher stored procedure using raw query."""
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
    return db.execute(query).fetchall()


def get_all(db: Session) -> list[DbGiaoVien]:
    """Return all teachers."""
    return db.query(DbGiaoVien).all()


def get_by_id(db: Session, magv: str) -> DbGiaoVien | None:
    """Return one teacher."""
    return db.query(DbGiaoVien).filter(DbGiaoVien.magv == magv).first()


def create(db: Session, request: GiaoVienCreate) -> DbGiaoVien:
    """Insert a teacher."""
    teacher = DbGiaoVien(**request.model_dump())
    db.add(teacher)
    db.commit()
    db.refresh(teacher)
    return teacher


def update(db: Session, teacher: DbGiaoVien, request: GiaoVienUpdate) -> DbGiaoVien:
    """Persist teacher changes."""
    for field, value in request.model_dump(exclude={"magv"}).items():
        setattr(teacher, field, value)
    db.commit()
    db.refresh(teacher)
    return teacher


def delete(db: Session, teacher: DbGiaoVien) -> None:
    """Delete a teacher."""
    db.delete(teacher)
    db.commit()


def search(db: Session, keyword: str) -> list[DbGiaoVien]:
    """Search teachers by code or name."""
    return db.query(DbGiaoVien).filter(
        or_(
            DbGiaoVien.magv.ilike(f"%{keyword}%"),
            DbGiaoVien.ho.ilike(f"%{keyword}%"),
            DbGiaoVien.ten.ilike(f"%{keyword}%"),
        )
    ).all()
