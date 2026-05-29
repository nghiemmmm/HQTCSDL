# MÔ TẢ QUY TẮC NGHIỆP VỤ HỆ THỐNG THI TRẮC NGHIỆM

## 1. Chức năng đăng nhập

### Quy tắc nghiệp vụ

* Người dùng phải đăng nhập trước khi sử dụng hệ thống.
* Tài khoản thuộc một trong ba nhóm quyền: `PGV`, `GIANGVIEN`, `SINHVIEN`.
* Giảng viên đăng nhập bằng login và password riêng.
* Sinh viên dùng chung login `sv`, sau đó nhập mã sinh viên để xác định thông tin cá nhân.
* Nếu đăng nhập sai tài khoản hoặc mật khẩu thì hệ thống không cho truy cập.
* Sau khi đăng nhập thành công, hệ thống hiển thị chức năng phù hợp với quyền của người dùng.

---

## 2. Chức năng nhập môn học

### Quy tắc nghiệp vụ

* Mã môn học là khóa chính, không được trùng.
* Mã môn học phải viết hoa.
* Tên môn học không được rỗng.
* Tên môn học không được trùng.
* Chỉ người có quyền PGV mới được thêm, xóa, sửa môn học.
* Không được xóa môn học nếu môn học đã có câu hỏi thi, đăng ký thi hoặc bảng điểm liên quan.
* Các thao tác chính gồm: Thêm, Xóa, Hiệu chỉnh, Phục hồi, Tìm, Ghi.

---

## 3. Chức năng nhập lớp và sinh viên

### Quy tắc nghiệp vụ

* Mỗi lớp có mã lớp duy nhất.
* Tên lớp không được rỗng và không được trùng.
* Mỗi sinh viên có mã sinh viên duy nhất.
* Sinh viên bắt buộc phải thuộc một lớp.
* Không được thêm sinh viên vào lớp không tồn tại.
* Không được xóa lớp nếu lớp còn sinh viên.
* Không được xóa sinh viên nếu sinh viên đã có điểm thi.
* PGV có quyền thêm, xóa, sửa lớp và sinh viên.
* Sinh viên không được tự cập nhật thông tin cá nhân.

---

## 4. Chức năng nhập giáo viên

### Quy tắc nghiệp vụ

* Mỗi giáo viên có mã giáo viên duy nhất.
* Họ và tên giáo viên không được để trống.
* Số điện thoại liên lạc dùng để lưu thông tin liên hệ.
* Chỉ PGV được thêm, xóa, sửa thông tin giáo viên.
* Không được xóa giáo viên nếu giáo viên đã soạn câu hỏi thi hoặc đã đăng ký lịch thi.
* Các thao tác chính gồm: Thêm, Xóa, Hiệu chỉnh, Phục hồi, Tìm, Ghi.

---

## 5. Chức năng nhập câu hỏi thi

### Quy tắc nghiệp vụ

* Chỉ giảng viên được nhập câu hỏi thi.
* Mỗi câu hỏi thuộc một môn học cụ thể.
* Mỗi câu hỏi có trình độ `A`, `B` hoặc `C`.
* Trình độ `A`: Đại học chuyên ngành.
* Trình độ `B`: Đại học không chuyên ngành.
* Trình độ `C`: Cao đẳng.
* Nội dung câu hỏi không được rỗng.
* Mỗi câu hỏi phải có đủ 4 đáp án A, B, C, D.
* Đáp án đúng chỉ được nhận một trong bốn giá trị: `A`, `B`, `C`, `D`.
* Giảng viên chỉ được xem và cập nhật các câu hỏi do chính mình soạn.
* PGV có thể quản lý toàn bộ dữ liệu nếu được phân quyền toàn quyền.

---

## 6. Chức năng đăng ký thi

### Quy tắc nghiệp vụ

* Giáo viên đăng ký thi cho một lớp, một môn học, một trình độ, một lần thi.
* Một lớp, một môn học, một lần thi chỉ được đăng ký một lần.
* Lần thi chỉ được nhận giá trị `1` hoặc `2`.
* Số câu thi phải từ 10 đến 100 câu.
* Thời gian thi phải từ 5 đến 60 phút.
* Ngày thi mặc định là ngày hiện tại nếu không nhập.
* Trước khi ghi đăng ký thi, hệ thống phải kiểm tra bộ đề có đủ số câu hỏi theo yêu cầu hay không.
* Nếu không đủ câu hỏi thì không cho đăng ký thi.
* Kết quả đăng ký thi được lưu vào bảng `GiaoVien_DangKy`.

---

## 7. Chức năng thi trắc nghiệm

### Quy tắc nghiệp vụ

* Chỉ sinh viên được thi chính thức.
* Sinh viên chọn môn học, ngày thi và lần thi.
* Hệ thống tự động lấy thông tin lớp, môn học, trình độ, số câu thi và thời gian thi từ đăng ký thi.
* Khi bắt đầu thi, hệ thống chọn ngẫu nhiên các câu hỏi từ bộ đề.
* Các câu hỏi được chọn không được trùng nhau.
* Câu hỏi phải lấy đúng theo trình độ đã đăng ký.
* Nếu thiếu câu ở trình độ cao, hệ thống được phép lấy thêm câu ở trình độ thấp hơn một bậc.
* Số câu lấy từ trình độ thấp hơn không được vượt quá 30% tổng số câu thi.
* Ít nhất 70% số câu phải đúng trình độ đã đăng ký.
* Mỗi câu hỏi có số điểm bằng nhau.
* Điểm tối đa là 10.
* Khi hết thời gian, hệ thống tự động kết thúc bài thi.
* Sau khi nộp bài, hệ thống tính điểm và thông báo điểm ngay cho sinh viên.
* Kết quả thi được ghi vào bảng `BangDiem`.
* Sinh viên được phép xem lại các câu đã thi ở lần thi trước.

---

## 8. Chức năng xem kết quả bài thi

### Quy tắc nghiệp vụ

* Sinh viên được xem lại bài thi của chính mình.
* Giảng viên được xem lại bài thi của sinh viên.
* Kết quả xem lại gồm: lớp, họ tên, mã sinh viên, môn thi, ngày thi, lần thi.
* Danh sách câu hỏi phải hiển thị:

  * Số thứ tự
  * Mã câu hỏi trong bộ đề
  * Nội dung câu hỏi
  * Đáp án A, B, C, D
  * Câu trả lời của sinh viên
  * Đáp án đúng
* Không được cho sinh viên xem bài thi của sinh viên khác.

---

## 9. Chức năng bảng điểm môn học

### Quy tắc nghiệp vụ

* Giảng viên chọn lớp, môn học và lần thi để in bảng điểm.
* Bảng điểm chỉ hiển thị sinh viên thuộc lớp được chọn.
* Mỗi sinh viên có một điểm tương ứng với môn học và lần thi.
* Điểm số có giá trị từ 0 đến 10.
* Bảng điểm gồm: STT, mã sinh viên, họ, tên, điểm số, điểm chữ.
* Giảng viên có quyền in bảng điểm môn học.
* Sinh viên không có quyền in bảng điểm của lớp.

---

## 10. Chức năng phân quyền

### Quy tắc nghiệp vụ

* Mỗi tài khoản chỉ thuộc một nhóm quyền.
* Nhóm `PGV` có toàn quyền quản lý hệ thống.
* PGV được tạo tài khoản mới cho nhóm PGV và Giảng viên.
* PGV không có chức năng thi.
* Nhóm `GIANGVIEN` chỉ được:

  * Cập nhật câu hỏi do mình soạn.
  * Thi thử nhưng không ghi điểm.
  * Xem lại bài thi của sinh viên.
  * In bảng điểm môn học.
* Nhóm `SINHVIEN` được:

  * Thi trắc nghiệm.
  * Xem lại bài thi đã thi.
* Sinh viên không được thêm, sửa, xóa dữ liệu hệ thống.

---

## 11. Chức năng tạo tài khoản

### Quy tắc nghiệp vụ

* Chỉ PGV được tạo tài khoản.
* Chỉ được tạo tài khoản cho PGV và Giảng viên.
* Không tạo tài khoản riêng cho sinh viên.
* Login không được rỗng.
* Password không được rỗng.
* Login không được trùng với login đã tồn tại.
* Một giáo viên chỉ được cấp một tài khoản.
* Khi tạo tài khoản, hệ thống phải tạo login, tạo user và gán role tương ứng.
* Nếu tạo thất bại ở bất kỳ bước nào thì hệ thống phải thông báo lỗi và không ghi nhận tài khoản không hợp lệ.
* Không được xóa tài khoản đang đăng nhập.
