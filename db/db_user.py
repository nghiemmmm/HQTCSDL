"""User repository and SQL Server account persistence operations."""

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, URL
from sqlalchemy.orm import Session

from db.database import engine


def find_sql_login(db: Session, login_name: str):
    """Return a SQL login row when it exists."""
    return db.execute(
        text("EXEC SP_KiemTraLogin @login_name = :login_name"),
        {"login_name": login_name},
    ).fetchone()


def connect_as_user(username: str, password: str):
    """Open a SQL Server connection using supplied credentials."""
    connection_url = URL.create(
        "mssql+pyodbc",
        username=username,
        password=password,
        host="localhost",
        port=1433,
        database="THITRACNGHIEM",
        query={
            "driver": "ODBC Driver 18 for SQL Server",
            "TrustServerCertificate": "yes",
        },
    )
    return create_engine(connection_url).connect()


def get_login_profile(connection, login_name: str):
    """Return profile data for a SQL login."""
    return connection.execute(
        text("EXEC dbo.sp_ThongTinDangNhap :tenlogin"),
        {"tenlogin": login_name},
    ).fetchone()


def find_student(db: Session, student_id: str):
    """Return a student identity row."""
    return db.execute(
        text("SELECT MASV FROM SINHVIEN WHERE MASV = :masv"),
        {"masv": student_id},
    ).fetchone()


def authenticate_student(db: Session, student_id: str, password: str):
    """Return a student profile when credentials match."""
    return db.execute(
        text(
            """
            SELECT MASV, HO, TEN
            FROM SINHVIEN
            WHERE MASV = :masv AND PASSWORD = :password
            """
        ),
        {"masv": student_id, "password": password},
    ).fetchone()


def create_sql_account(
    login_name: str,
    password: str,
    username: str,
    sql_role: str,
    database_engine: Engine = engine,
) -> None:
    """Create a SQL Server account through the existing procedure."""
    with database_engine.connect().execution_options(
        isolation_level="AUTOCOMMIT"
    ) as connection:
        connection.execute(
            text(
                """
                EXEC sp_TaoTaiKhoan
                    :loginname,
                    :password,
                    :username,
                    :role
                """
            ),
            {
                "loginname": login_name,
                "password": password,
                "username": username,
                "role": sql_role,
            },
        )


def delete_sql_account(
    login_name: str,
    database_engine: Engine = engine,
) -> None:
    """Drop the database user and SQL Server login for an account."""
    with database_engine.connect().execution_options(
        isolation_level="AUTOCOMMIT"
    ) as connection:
        connection.execute(
            text(
                """
                DECLARE @login sysname = :loginname;
                DECLARE @db_user sysname;
                DECLARE @sql nvarchar(max);

                SELECT @db_user = dp.name
                FROM sys.database_principals dp
                INNER JOIN sys.server_principals sp ON dp.sid = sp.sid
                WHERE sp.name = @login;

                IF @db_user IS NOT NULL
                BEGIN
                    SET @sql = N'';
                    SELECT @sql = @sql
                        + CASE WHEN LEN(@sql) > 0 THEN N'; ' ELSE N'' END
                        + N'ALTER ROLE ' + QUOTENAME(role_principal.name)
                        + N' DROP MEMBER ' + QUOTENAME(member_principal.name)
                    FROM sys.database_role_members drm
                    INNER JOIN sys.database_principals role_principal
                        ON drm.role_principal_id = role_principal.principal_id
                    INNER JOIN sys.database_principals member_principal
                        ON drm.member_principal_id = member_principal.principal_id
                    WHERE member_principal.name = @db_user;

                    IF @sql IS NOT NULL AND LEN(@sql) > 0
                        EXEC sp_executesql @sql;

                    SET @sql = N'DROP USER ' + QUOTENAME(@db_user);
                    EXEC sp_executesql @sql;
                END

                IF EXISTS (SELECT 1 FROM sys.server_principals WHERE name = @login)
                BEGIN
                    SET @sql = N'DROP LOGIN ' + QUOTENAME(@login);
                    EXEC sp_executesql @sql;
                END
                """
            ),
            {"loginname": login_name},
        )
