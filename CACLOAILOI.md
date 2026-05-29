# Cac loai loi da bat

## THI - Lay thong tin thi

Luồng lấy thông tin thi chạy từ trang `formBatDauThi.html`, file JS `static/js/batDauThi.js`, gọi route:

```text
GET /thi/layTTThi?mamonhoc=...&lanthi=...&malop=...&ngaythi=...
```

Các tham số bắt buộc:

- `mamonhoc`: mã môn học.
- `lanthi`: lần thi, kiểu số.
- `malop`: mã lớp của sinh viên.
- `ngaythi`: ngày thi, định dạng `YYYY-MM-DD`.

## Loi backend da bat

### 401 - Chua dang nhap hoac session het han

Xảy ra khi:

- Không có cookie `session_id`.
- Session trong RAM đã hết hạn.
- Server restart làm mất session.

Xử lý:

- Dependency `get_current_user` trả lỗi `401`.
- Frontend báo hết phiên đăng nhập và chuyển về `/user/login`.

### 403 - Khong co quyen

Xảy ra khi:

- User không có `TAKE_EXAM` hoặc `PRACTICE_EXAM`.
- PGV truy cập route thi.
- Sinh viên cố lấy thông tin thi của lớp khác.

Xử lý:

- Backend dùng `require_any_permission(Permission.TAKE_EXAM, Permission.PRACTICE_EXAM)`.
- Backend kiểm tra nếu role là `SINHVIEN` thì `malop` phải trùng lớp của sinh viên đang đăng nhập.
- Frontend hiển thị: không có quyền xem thông tin thi.

### 404 - Khong tim thay du lieu

Xảy ra khi:

- Không tìm thấy sinh viên đang đăng nhập.
- Sinh viên chưa được phân lớp.
- Không tìm thấy lịch thi phù hợp với môn, lớp, ngày thi và lần thi.

Xử lý:

- Backend trả `404` với thông báo cụ thể.
- Frontend hiển thị trạng thái `Khong co lich` và thông báo lỗi.

### 422 - Du lieu dau vao khong hop le

Xảy ra khi:

- Thiếu query param bắt buộc.
- `lanthi` không phải số.
- `ngaythi` không đúng định dạng `YYYY-MM-DD`.

Xử lý:

- FastAPI tự validate tham số thiếu/sai kiểu.
- Backend tự validate định dạng ngày bằng `datetime.strptime(ngaythi, "%Y-%m-%d")`.
- Frontend hiển thị thông báo thông tin môn/ngày thi/lần thi không hợp lệ.

### 500 - Loi database hoac server

Xảy ra khi:

- Query database lỗi.
- Mất kết nối SQL Server.
- Lỗi không mong muốn khi lấy thông tin thi.

Xử lý:

- Backend bọc query lấy thông tin thi bằng `try/except`.
- Backend trả `500` với thông báo lỗi database.
- Frontend hiển thị lỗi máy chủ khi lấy thông tin thi.

## Loi frontend da bat

### Khong co thong tin user dang nhap

Xảy ra khi:

- `window.currentUser` không tồn tại.
- Local/session frontend chưa có mã sinh viên.

Xử lý:

- Không gọi API.
- Hiển thị `Khong tim thay thong tin dang nhap`.

### Khong du cac truong de lay thong tin thi

Xảy ra khi thiếu một trong các trường:

- Môn học.
- Ngày thi.
- Lần thi.
- Mã lớp.

Xử lý:

- Không gọi `/thi/layTTThi`.
- Reset thông tin số câu, thời gian, trình độ về `...`.

### Loi ket noi

Xảy ra khi:

- Không gọi được API.
- Server không phản hồi.
- Network lỗi.

Xử lý:

- Bắt lỗi bằng `catch`.
- Hiển thị trạng thái `Loi`.
- Gọi notification báo lỗi kết nối máy chủ.

## THI - Lay cau hoi thi

Luong lay cau hoi thi chay tu trang `formThi.html`, file JS `static/js/thi.js`, goi route:

```text
GET /thi/cau-hoi?mamonhoc=...&lanthi=...&malop=...&ngaythi=...
```

Cac tham so bat buoc:

- `mamonhoc`: ma mon hoc.
- `lanthi`: lan thi, kieu so.
- `malop`: ma lop cua sinh vien.
- `ngaythi`: ngay thi, dinh dang `YYYY-MM-DD`.

Backend khong nhan `socauthi` hoac `trinhdo` tu frontend. Hai gia tri nay duoc lay tu bang `GIAOVIEN_DANGKY` sau khi tim thay lich thi hop le.

### 400 - Khong du cau hoi dung trinh do

Xay ra khi:

- Lich thi yeu cau trinh do `A` nhung so cau trinh do `A` khong du.
- Lich thi yeu cau trinh do `B` nhung so cau trinh do `B` khong du.
- Lich thi yeu cau trinh do `C` nhung khong co trinh do thap hon de bu.

Xu ly:

- Backend uu tien lay cau hoi dung trinh do da dang ky.
- Neu thieu cau, backend chi duoc bu bang trinh do thap hon mot bac:
  - `A` duoc bu bang `B`.
  - `B` duoc bu bang `C`.
  - `C` khong duoc bu.
- Neu so cau thieu lon hon gioi han duoc phep bu thi tra `400`.

### 400 - Vuot gioi han 30% cau hoi bu

Xay ra khi:

- So cau can bu tu trinh do thap hon vuot qua `floor(30% * socauthi)`.
- Khi do so cau dung trinh do khong dat toi thieu 70% tong so cau thi.

Xu ly:

- Backend tinh `max_lower_count = floor(socauthi * 0.3)`.
- Neu `missing_count > max_lower_count`, backend tra `400`.
- Frontend hien thi thong bao loi tu backend va khong vao bai thi.

### 400 - Khong du cau hoi de bu trinh do thap hon

Xay ra khi:

- So cau thieu nam trong gioi han 30%.
- Nhung ngan hang cau hoi o trinh do thap hon mot bac cung khong du de bu.

Xu ly:

- Backend tra `400` voi thong bao so cau can bu va so cau hien co.
- Frontend hien thi thong bao loi va dung tai man hinh phong thi.

### 403 - Lay cau hoi cua lop khac

Xay ra khi:

- User co role `SINHVIEN`.
- Query param `malop` khong trung voi lop cua sinh vien dang dang nhap.

Xu ly:

- Backend tra `403` voi thong bao `Khong duoc lay cau hoi thi cua lop khac`.

### 404 - Khong tim thay lich thi

Xay ra khi:

- Khong tim thay lich thi trong `GIAOVIEN_DANGKY` theo `mamonhoc`, `lanthi`, `malop`, `ngaythi`.

Xu ly:

- Backend tra `404`.
- Frontend hien thi loi khong the tai cau hoi thi.

### 422 - Sai dinh dang tham so

Xay ra khi:

- Thieu query param bat buoc.
- `lanthi` khong phai so.
- `ngaythi` khong dung dinh dang `YYYY-MM-DD`.

Xu ly:

- FastAPI validate tham so thieu/sai kieu.
- Backend validate ngay thi bang `datetime.strptime(ngaythi, "%Y-%m-%d")`.

### 500 - Loi database khi lay cau hoi thi

Xay ra khi:

- Query bang `GIAOVIEN_DANGKY` loi.
- Query bang `BODE` loi.
- Mat ket noi SQL Server.

Xu ly:

- Backend boc query bang `try/except`.
- Backend tra `500` voi thong bao loi database.
- Frontend hien thi thong bao loi khi tai cau hoi.

## Luu y

- Frontend chỉ hiển thị lỗi thân thiện cho người dùng.
- Backend vẫn là lớp kiểm tra bảo mật chính.
- Sinh viên không được gọi route quản trị `/monhoc/danhsachMH`; danh sách môn thi phải lấy qua `/thi/monhoc-duoc-thi`.
- Khi so sánh ngày thi, backend không so sánh trực tiếp `DateTime == string`, mà lọc theo khoảng thời gian trong ngày từ `00:00:00` đến `23:59:59`.
Note : khi bắt đầu thi nên load tất cả môn học có trong table môn học hay chỉ load tất cả các môn đã được giáo viên đăng ký 
khi chọn đủ đầu đủ các trường thì nên có nút lọc hay cho nó tự động , nếu các nút tự động lọc thì nó nên hiển thị supform cho chi tiết bài thi 
