# He thong thi trac nghiem

Du an web quan ly thi trac nghiem dung FastAPI, Jinja2, SQLAlchemy va SQL Server.

## Chuc nang chinh

- Dang nhap bang cookie session, session luu trong RAM va het han sau 1 gio.
- Phan quyen RBAC cho 3 role: PGV, GIANGVIEN, SINHVIEN.
- Quan ly mon hoc, lop, sinh vien, giao vien va tai khoan nguoi dung.
- Quan ly bo de/cau hoi theo giao vien so huu.
- Dang ky lich thi: xem danh sach, tim kiem, them, sua, xoa.
- Kiem tra du cau hoi khi dang ky thi theo luat 70/30: neu thieu cau dung trinh do thi chi duoc bu toi da 30% tu trinh do thap hon 1 bac.
- Sinh vien lam bai, autosave trang thai, tu dong nop bai khi het gio, cham diem va ghi BANGDIEM.
- Sinh vien xem diem va xem lai chi tiet bai thi: cau da thi, dap an da chon, dap an dung.
- Giang vien/PGV xem ket qua va bai thi chi tiet cua sinh vien theo lop, mon, lan thi.

## Cau truc chinh

- `main.py`: khoi tao FastAPI, static files, templates, middleware log request va include router.
- `router/`: cac endpoint HTML/API theo nghiep vu.
- `db/`: ket noi database, model SQLAlchemy va cac ham thao tac CSDL.
- `schemas/`: Pydantic schema cho request/response.
- `core/session.py`: quan ly session dang nhap trong RAM.
- `core/auth.py`: dependency xac thuc cookie session va kiem tra permission.
- `templates/`: giao dien Jinja2.
- `static/`: CSS, JavaScript va asset tinh.

## Phan quyen

### PGV

PGV co quyen:

- Quan ly mon hoc, lop, sinh vien, giao vien.
- Tao tai khoan nguoi dung.
- Xem ket qua thi, xem lai bai thi sinh vien va in bang diem.

PGV khong co quyen:

- Tham gia thi hoac thi thu.
- Quan ly bo de/cau hoi.
- Dang ky/sua/xoa lich thi.

### GIANGVIEN

Giang vien co quyen:

- Quan ly cau hoi cua minh.
- Dang ky, sua, xoa va tim lich thi cua minh.
- Thi thu, khong ghi diem vao BANGDIEM.
- Xem ket qua, xem lai bai thi sinh vien va in bang diem.

Giang vien khong co quyen:

- Tao tai khoan nguoi dung.
- Quan ly danh muc mon hoc, lop, sinh vien, giao vien.
- Sua/xoa cau hoi cua giao vien khac.

### SINHVIEN

Sinh vien co quyen:

- Lam bai thi chinh thuc.
- Xem diem cua minh.
- Xem lai bai thi cua minh.

Sinh vien khong co quyen quan tri danh muc, cau hoi, lich thi, tai khoan hay bao cao sinh vien khac.

## Mapping router

- `/home`: can dang nhap hop le.
- `/user/register`: can `CREATE_USER`.
- `/monhoc`: can cac permission `*_SUBJECT`.
- `/lop`: can cac permission `*_CLASS`.
- `/sinhvien`: can cac permission `*_STUDENT`.
- `/giaovien`: can cac permission `*_TEACHER`.
- `/bode`: can cac permission `*_QUESTION`.
- `/dangkythi`: can cac permission `*_EXAM_REGISTRATION`.
- `/thi`: can `TAKE_EXAM` hoac `PRACTICE_EXAM`.
- `/thi/lich-su`, `/thi/xem-lai`: sinh vien xem bai cua minh; GV/PGV xem bai sinh vien khi co quyen `VIEW_STUDENT_EXAM`.
- `/thi/diem`: can `VIEW_OWN_SCORE`.
- `/thi/ket-qua`: can `VIEW_STUDENT_SCORE`.
- `/thi/bang-diem`: can `PRINT_SCORE_TABLE`.

## Luu y ky thuat

- Session luu RAM phu hop demo/do an; neu deploy that nen chuyen sang Redis/database session.
- Password sinh vien hien van so sanh trong database; neu dung thuc te nen hash bang bcrypt.
- Can cai ODBC Driver 18 for SQL Server tren may chay ung dung.
- Cau hinh ket noi SQL Server nam trong `db/database.py`.

## Chay du an

```bash
pip install -r requirements.txt
python main.py
```

Mo Swagger UI tai `/myapi`.

## Kiem tra

```bash
python -m pytest
python -m compileall main.py core db router schemas tests test.py
```
