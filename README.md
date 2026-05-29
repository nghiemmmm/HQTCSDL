# He thong thi trac nghiem

Du an web quan ly thi trac nghiem dung FastAPI, Jinja2, SQLAlchemy va SQL Server.

## Cau truc chinh

- `main.py`: khoi tao FastAPI, static files, templates, middleware log request va include router.
- `router/`: cac endpoint HTML/API theo nghiep vu.
- `db/`: ket noi database, model SQLAlchemy va cac ham thao tac CSDL.
- `schemas/`: Pydantic schema cho request/response.
- `core/session.py`: quan ly session dang nhap trong RAM.
- `core/auth.py`: dependency xac thuc cookie session va kiem tra permission.
- `templates/base_dashboard.html`: layout dashboard dung chung cho cac trang sau dang nhap.
- `static/js/dashboard.js`: render sidebar/card/button dong theo role va permission.
- `static/css/dashboard.css`: design system dung chung cho dashboard.
- `templates/`: giao dien Jinja2.
- `static/`: CSS, JavaScript va asset tinh.

## Co che dang nhap

He thong dang dung cookie session:

1. User dang nhap qua `POST /user/login`.
2. Backend tao `session_id` bang `create_session(user_data)`.
3. `session_id` duoc gan vao cookie `httponly`.
4. Thong tin session duoc luu trong RAM tai `core/session.py`.
5. Session het han sau 1 gio.

Cookie chi luu ma session, khong luu truc tiep thong tin user.

## Phan quyen RBAC

He thong dung RBAC:

- User co `role`.
- Moi `role` co danh sach `Permission`.
- Router/API dung dependency de kiem tra permission truoc khi xu ly.
- Frontend dung `data-permission`, `data-any-permission` va `data-roles` de an/hien sidebar, card va nut bam theo role.
- Backend van la lop bao ve chinh, nen user khong the truy cap route bi cam bang URL truc tiep.

File dinh nghia role va permission:

- `db/roles.py`

File dependency xac thuc/phan quyen:

- `core/auth.py`

Dependency chinh:

```python
get_current_user()
require_permission(permission)
require_any_permission(*permissions)
```

Neu chua dang nhap, API tra `401`.
Neu da dang nhap nhung thieu quyen, API tra `403`.

## Role hien co

- `PGV`: quan ly mon hoc, lop, sinh vien, giao vien, tai khoan/phan quyen va bao cao; khong duoc tham gia thi, quan ly cau hoi hoac dang ky thi.
- `GIANGVIEN`: quan ly cau hoi cua minh, dang ky/sua lich thi, xem lich thi, xem bao cao diem va duoc thi thu khong luu diem.
- `SINHVIEN`: lam bai thi va xem diem/bai thi cua minh.

## Doi chieu yeu cau phan quyen

### PGV

PGV co quyen quan tri:

- Quan ly mon hoc: xem, them, sua, xoa, tim kiem.
- Quan ly lop hoc.
- Quan ly sinh vien.
- Quan ly giao vien.
- Tao tai khoan nguoi dung qua `/user/register`.
- Xem ket qua thi, bai thi sinh vien va in bang diem thong qua cac permission bao cao.

PGV bi han che:

- Khong co `TAKE_EXAM`.
- Khong co `PRACTICE_EXAM`.
- Khong co permission `*_QUESTION` va `*_EXAM_REGISTRATION`, nen khong truy cap duoc `/bode` va `/dangkythi`.
- Vi `/thi` chi chap nhan `TAKE_EXAM` hoac `PRACTICE_EXAM`, PGV khong duoc tham gia thi.

### Giang vien

Giang vien co quyen:

- Xem, them, sua, xoa cau hoi thi.
- Dang ky va cap nhat lich thi cho lop.
- Xem lich thi.
- Xem lai bai thi cua sinh vien.
- Xem/in bang diem mon hoc.
- Thi thu bang `PRACTICE_EXAM`, khong luu diem.

Giang vien bi han che:

- Khong co `CREATE_USER`, nen khong tao duoc tai khoan PGV/Giang vien.
- Khong co permission quan ly mon hoc, lop, sinh vien, giao vien.
- Khi thao tac `/bode`, giang vien chi xem/sua/xoa cau hoi co `magv` trung voi ma user dang dang nhap.

### Sinh vien

Sinh vien co quyen:

- Truy cap chuc nang thi bang `TAKE_EXAM`.
- Xem diem cua minh bang `VIEW_OWN_SCORE`.
- Xem lai bai thi cua minh bang `VIEW_OWN_EXAM`.

Sinh vien bi han che:

- Khong co permission quan ly mon hoc, lop, sinh vien, giao vien, cau hoi.
- Khong co permission dang ky lich thi.
- Khong co `CREATE_USER`, nen khong tao tai khoan.
- Khong truy cap duoc cac chuc nang quan tri.

## Nhom permission chinh

- User: `CREATE_USER`
- Mon hoc: `VIEW_SUBJECT`, `CREATE_SUBJECT`, `UPDATE_SUBJECT`, `DELETE_SUBJECT`
- Lop: `VIEW_CLASS`, `CREATE_CLASS`, `UPDATE_CLASS`, `DELETE_CLASS`
- Sinh vien: `VIEW_STUDENT`, `CREATE_STUDENT`, `UPDATE_STUDENT`, `DELETE_STUDENT`
- Giao vien: `VIEW_TEACHER`, `CREATE_TEACHER`, `UPDATE_TEACHER`, `DELETE_TEACHER`
- Cau hoi/bo de: `VIEW_QUESTION`, `CREATE_QUESTION`, `UPDATE_QUESTION`, `DELETE_QUESTION`
- Dang ky thi: `VIEW_EXAM_REGISTRATION`, `CREATE_EXAM_REGISTRATION`, `UPDATE_EXAM_REGISTRATION`, `DELETE_EXAM_REGISTRATION`
- Thi: `TAKE_EXAM`, `PRACTICE_EXAM`
- Diem/bai thi: `VIEW_OWN_SCORE`, `VIEW_STUDENT_SCORE`, `VIEW_SCORE_REPORT`, `VIEW_OWN_EXAM`, `VIEW_STUDENT_EXAM`, `PRINT_SCORE_TABLE`

## Mapping quyen theo router

- `/home`: can dang nhap hop le; card dashboard duoc loc dong theo role.
- `/user/register`: can `CREATE_USER`.
- `/user/info`: can dang nhap hop le.
- `/monhoc`: dung cac permission `*_SUBJECT`.
- `/lop`: dung cac permission `*_CLASS`; lay sinh vien theo lop can `VIEW_STUDENT`.
- `/sinhvien`: dung cac permission `*_STUDENT`.
- `/giaovien`: dung cac permission `*_TEACHER`.
- `/bode`: dung cac permission `*_QUESTION`.
- `/dangkythi`: dung cac permission `*_EXAM_REGISTRATION`.
- `/thi`: can `TAKE_EXAM` hoac `PRACTICE_EXAM`; PGV khong co hai quyen nay nen khong duoc tham gia thi.
- `/thi/lich-su`, `/thi/xem-lai`: can `VIEW_OWN_EXAM`.
- `/thi/diem`: can `VIEW_OWN_SCORE`.
- `/thi/ket-qua`: can `VIEW_STUDENT_SCORE`.
- `/thi/bang-diem`: can `PRINT_SCORE_TABLE`.

## Kiem tra so huu du lieu

Permission chi tra loi user co duoc thuc hien loai thao tac do hay khong.
Voi du lieu co chu so huu, he thong can kiem tra them owner.

Hien tai `/bode` da kiem tra:

- `GIANGVIEN` chi duoc sua/xoa cau hoi co `magv` trung voi ma user dang dang nhap.
- Khi `GIANGVIEN` tao/sua cau hoi, `magv` duoc gan theo session hien tai.

## Luu y hien tai

- Session dang luu trong RAM, phu hop demo/do an; neu deploy that nen chuyen sang Redis/database session.
- Password sinh vien hien van dang so sanh truc tiep trong database; nen hash bang bcrypt truoc khi dung thuc te.
- Khi parse toan bo repo, `test.py` dang co loi cu phap cu tai dong 16, khong lien quan phan RBAC.

Log này cho thấy browser vẫn đang chạy bản JS cũ: nó còn gọi masv=001 và /monhoc/monhoc, trong khi file tôi đã sửa phải gọi /thi/monhoc-duoc-thi. Tôi sẽ bump version script trong template để phá cache trình duyệt.
 bump version script trong template để phá cache trình duyệt.