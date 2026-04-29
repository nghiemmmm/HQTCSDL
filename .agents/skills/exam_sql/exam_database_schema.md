# Database Schema

## 1. Overview

This database is used for a multiple-choice exam system (THITRACNGHIEM), supporting question banks, exam scheduling, and student scoring.

---

## 2. Tables

### SINHVIEN

* MASV (NCHAR(8), PRIMARY KEY): Student ID
* HO (NVARCHAR): Last name
* TEN (NVARCHAR): First name
* NGAYSINH (DATE): Date of birth
* DIACHI (NVARCHAR): Address
* MALOP (NCHAR(15), FOREIGN KEY → LOP.MALOP)
* PASSWORD (NVARCHAR(255), NOT NULL, DEFAULT '123456'): Login password

---

### LOP

* MALOP (NCHAR(15), PRIMARY KEY): Class ID
* TENLOP (NVARCHAR): Class name

---

### MONHOC

* MAMH (NCHAR(5), PRIMARY KEY): Subject ID
* TENMH (NVARCHAR): Subject name

---

### GIAOVIEN

* MAGV (NCHAR(8), PRIMARY KEY): Teacher ID
* HO (NVARCHAR): Last name
* TEN (NVARCHAR): First name
* DIACHI (NVARCHAR): Address
* SODTLL (NCHAR): Phone number

---

### BODE (Question Bank)

* CAUHOI (INT, PRIMARY KEY): Question ID
* MAMH (NCHAR(5), FOREIGN KEY → MONHOC.MAMH)
* TRINHDO (CHAR(1)): Difficulty level (A/B/C)
* NOIDUNG (NVARCHAR): Question content
* A, B, C, D (NVARCHAR): Answer options
* DAP_AN (CHAR(1)): Correct answer (A/B/C/D)
* MAGV (NCHAR(8), FOREIGN KEY → GIAOVIEN.MAGV)

---

### GIAOVIEN_DANGKY (Exam Schedule)

* MAMH (NCHAR(5), PRIMARY KEY)
* MALOP (NCHAR(15), PRIMARY KEY)
* LAN (SMALLINT, PRIMARY KEY): Attempt number
* MAGV (NCHAR(8))
* TRINHDO (CHAR(1))
* NGAYTHI (DATETIME)
* SOCAUTHI (SMALLINT): Number of questions
* THOIGIAN (SMALLINT): Duration (minutes)

---

### BANGDIEM

* MASV (NCHAR(8), PRIMARY KEY)
* MAMH (NCHAR(5), PRIMARY KEY)
* LAN (SMALLINT, PRIMARY KEY)
* NGAYTHI (DATE)
* DIEM (FLOAT): Score (0–10)

---

## 3. Relationships

* One SINHVIEN belongs to one LOP
* One SINHVIEN has many BANGDIEM records
* One MONHOC has many BODE questions
* One GIAOVIEN creates many BODE questions
* GIAOVIEN_DANGKY links MONHOC and LOP for exam scheduling
* BANGDIEM references SINHVIEN and MONHOC

---

## 4. Business Rules

* Score (DIEM) must be between 0 and 10
* Exam attempt (LAN) must be 1 or 2
* Question difficulty (TRINHDO) must be A, B, or C
* Answer (DAP_AN) must be A, B, C, or D
* Number of questions (SOCAUTHI) must be between 10 and 100
* Exam duration (THOIGIAN) must be between 15 and 60 minutes
* Each student can take a subject at most 2 times

---

## 5. Query Rules (IMPORTANT)

* Always JOIN SINHVIEN and BANGDIEM when retrieving scores
* Use MASV as the main identifier for students
* Use MAMH for subject-based filtering
* Do NOT assume undefined columns
* Always consider LAN when querying exam results

---

## 6. Common Queries

### Get all students with scores

SELECT sv.MASV, sv.TEN, bd.MAMH, bd.DIEM
FROM SINHVIEN sv
LEFT JOIN BANGDIEM bd ON sv.MASV = bd.MASV

---

### Get students who failed (DIEM < 5)

SELECT *
FROM BANGDIEM
WHERE DIEM < 5

---

### Get exam schedule for a class

SELECT *
FROM GIAOVIEN_DANGKY
WHERE MALOP = 'D15CQCP01'

---

### Get random questions for a subject

SELECT TOP 10 *
FROM BODE
WHERE MAMH = 'CTDL'
ORDER BY NEWID()

---

### Insert new student (auto PASSWORD)

SELECT * FROM SINHVIEN

INSERT INTO SINHVIEN (MASV, HO, TEN, MALOP)
VALUES ('SV001', 'Nguyen', 'A', 'D15CQCP01')

---

# End of Schema
