# Thi Trắc Nghiệm

> Backend FastAPI cho hệ thống thi trắc nghiệm nhiều môn học và nhiều trình độ khác nhau.  
> Hệ thống cho phép:
> - Quản lý câu hỏi thi
> - Tạo bộ đề
> - Đăng ký thi
> - Làm bài thi trắc nghiệm
> - Chấm điểm và lưu kết quả
> - Quản lý sinh viên, giáo viên, môn học và lớp học

---

## Tech Stack

- Framework: FastAPI
- Language: Python, JavaScript, HTML/CSS
- Database: SQL Server
- ORM/Database Access: pyodbc / SQLAlchemy
- Frontend: Jinja2 Templates + Vanilla JavaScript

---

## Project Structure


HQTCSDL
+-- .agents
|   \-- skills
|       +-- exam_sql
|       |   \-- exam_database_schema.md
|       \-- query-optimization
|           \-- query-optimization.md
|
+-- .claude
|   +-- rules
|   |   \-- design.md
|   \-- CLAUDE.md
|
+-- db
|   +-- database.py              # Database connection
|   +-- model.py                 # Database models
|   +-- hash.py                  # Password hashing
|   +-- roles.py                 # Role definitions
|   +-- db_bode.py               # Question set logic
|   +-- db_dangkythi.py          # Exam registration logic
|   +-- db_diem.py               # Score processing
|   +-- db_giaovien.py           # Teacher processing
|   +-- db_lop.py                # Class processing
|   +-- db_monhoc.py             # Subject processing
|   +-- db_sinhvien.py           # Student processing
|   +-- db_user.py               # User/authentication logic
|   \-- sp_kiemtra_cauhoi.sql    # Stored procedure
|
+-- logs
|   +-- logging_config.py
|   +-- logging_config.json
|   +-- log_middleeware.py
|   \-- server_logs.txt
|
+-- router
|   +-- bode_router.py
|   +-- dangKyThi_router.py
|   +-- giaovien_router.py
|   +-- lophoc_router.py
|   +-- monHoc_router.py
|   +-- sinhvien_router.py
|   +-- thi_router.py
|   \-- user_router.py
|
+-- schemas
|   \-- schemas.py               # Pydantic schemas
|
+-- static
|   +-- css
|   +-- js
|   \-- favicon.ico
|
+-- templates
|   +-- login.html
|   +-- register.html
|   +-- formThi.html
|   +-- formBoDe.html
|   +-- formDangKyThi.html
|   +-- formSinhVien.html
|   +-- formGiaoVien.html
|   +-- formMonHoc.html
|   \-- formBatDauThi.html
|
+-- .env
+-- main.py
+-- requirements.txt
+-- pyproject.toml
+-- README.md
\-- test.py

Commands

## Start development:
fastapi dev main.py
## Install dependencies:
pip install -r requirements.txt