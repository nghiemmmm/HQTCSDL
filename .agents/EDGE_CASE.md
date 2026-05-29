# EDGE CASE CHO CÁC NGHIỆP VỤ HỆ THỐNG THI TRẮC NGHIỆM

## 1. Đăng nhập

### Edge case

* Login đúng nhưng password sai.
* Login không tồn tại.
* Người dùng chọn sai loại đăng nhập, ví dụ sinh viên nhưng nhập login giảng viên.
* Sinh viên nhập mã sinh viên không tồn tại.
* Sinh viên dùng login `sv` nhưng để trống mã sinh viên.
* Tài khoản bị xóa nhưng vẫn còn session đăng nhập cũ.
* Người dùng đăng nhập thành công nhưng không thuộc role nào.
* Một tài khoản bị gán nhầm nhiều role.
* Mất kết nối cơ sở dữ liệu trong lúc đăng nhập.
* Người dùng nhập ký tự đặc biệt hoặc SQL injection trong login/password.

---

## 2. Nhập môn học

### Edge case

* Mã môn học trùng với môn đã tồn tại.
* Mã môn học nhập chữ thường thay vì chữ in hoa.
* Tên môn học trùng nhưng khác hoa/thường.
* Tên môn học chỉ chứa khoảng trắng.
* Mã môn học vượt quá 5 ký tự.
* Xóa môn học đã có câu hỏi trong bảng `BODE`.
* Xóa môn học đã có đăng ký thi.
* Xóa môn học đã có bảng điểm.
* Đang thêm môn học thì mất kết nối CSDL.
* Hai PGV cùng thêm một mã môn học tại cùng thời điểm.

---

## 3. Nhập lớp và sinh viên

### Edge case lớp

* Mã lớp trùng.
* Mã lớp nhập chữ thường.
* Tên lớp trùng.
* Tên lớp rỗng hoặc chỉ toàn khoảng trắng.
* Xóa lớp đang có sinh viên.
* Xóa lớp đã có đăng ký thi.
* Hai người cùng sửa tên một lớp cùng lúc.

### Edge case sinh viên

* Mã sinh viên trùng.
* Mã sinh viên vượt quá 8 ký tự.
* Sinh viên không thuộc lớp nào.
* Chọn mã lớp không tồn tại.
* Ngày sinh lớn hơn ngày hiện tại.
* Họ hoặc tên sinh viên để trống.
* Xóa sinh viên đã có điểm thi.
* Sinh viên đã thi nhưng bị đổi lớp.
* Sinh viên cùng lúc đăng nhập khi thông tin đang bị sửa.
* Nhập địa chỉ quá dài vượt giới hạn 100 ký tự.

---

## 4. Nhập giáo viên

### Edge case

* Mã giáo viên trùng.
* Mã giáo viên vượt quá 8 ký tự.
* Họ hoặc tên giáo viên rỗng.
* Số điện thoại chứa chữ cái.
* Số điện thoại vượt quá 15 ký tự.
* Xóa giáo viên đã soạn câu hỏi.
* Xóa giáo viên đã đăng ký lịch thi.
* Giáo viên đã có tài khoản nhưng bị xóa thông tin giáo viên.
* Hai PGV cùng cập nhật một giáo viên.
* Nhập địa chỉ vượt quá 50 ký tự.

---

## 5. Nhập câu hỏi thi

### Edge case

* Nội dung câu hỏi rỗng.
* Nội dung câu hỏi vượt quá 200 ký tự.
* Một trong bốn đáp án A, B, C, D bị rỗng.
* Đáp án đúng không thuộc A, B, C, D.
* Trình độ không thuộc A, B, C.
* Chọn môn học không tồn tại.
* Giáo viên sửa câu hỏi không phải do mình soạn.
* Câu hỏi đã được dùng trong bài thi nhưng giáo viên muốn xóa.
* Câu hỏi bị trùng nội dung trong cùng môn học.
* Đang lưu câu hỏi thì mất kết nối CSDL.
* Câu hỏi có ký tự đặc biệt gây lỗi hiển thị.
* Đáp án đúng bị xóa hoặc sửa nhưng không cập nhật lại.

---

## 6. Đăng ký thi

### Edge case

* Một lớp, một môn, một lần thi đã đăng ký rồi nhưng giáo viên đăng ký lại.
* Lần thi nhỏ hơn 1 hoặc lớn hơn 2.
* Số câu thi nhỏ hơn 10.
* Số câu thi lớn hơn 100.
* Thời gian thi nhỏ hơn 5 phút.
* Thời gian thi lớn hơn 60 phút.
* Ngày thi nhỏ hơn ngày hiện tại.
* Môn học chưa có đủ câu hỏi.
* Có đủ tổng số câu nhưng không đủ câu theo trình độ yêu cầu.
* Chọn lớp không tồn tại.
* Chọn môn học không tồn tại.
* Giáo viên đăng ký thi cho lớp không thuộc quyền quản lý nếu hệ thống có ràng buộc phân mảnh.
* Hai giáo viên cùng đăng ký một lớp, một môn, một lần thi cùng lúc.
* Đăng ký thi thành công nhưng sau đó câu hỏi bị xóa làm thiếu bộ đề.

---

## 7. Thi trắc nghiệm

### Edge case

* Sinh viên chọn môn chưa được đăng ký thi.
* Sinh viên chọn sai ngày thi.
* Sinh viên chọn lần thi chưa tồn tại.
* Sinh viên đã thi lần đó rồi nhưng tiếp tục thi lại.
* Hệ thống không đủ câu hỏi để random.
* Câu hỏi random bị trùng.
* Không đủ 70% câu đúng trình độ yêu cầu.
* Số câu lấy từ trình độ thấp hơn vượt quá 30%.
* Sinh viên bắt đầu thi nhưng mất kết nối mạng.
* Sinh viên thoát chương trình giữa lúc thi.
* Hết thời gian nhưng sinh viên chưa bấm nộp bài.
* Sinh viên không trả lời câu nào.
* Sinh viên trả lời thiếu một số câu.
* Có câu trả lời không thuộc A, B, C, D.
* Timer trên client và server bị lệch.
* Hai tab/máy cùng đăng nhập một sinh viên để thi cùng lúc.
* Hệ thống tính điểm sai do làm tròn số.
* Ghi điểm thành công nhưng lưu chi tiết bài thi thất bại.
* Lưu chi tiết thành công nhưng ghi bảng điểm thất bại.
* Sinh viên reload form trong lúc đang thi.

---

## 8. Xem kết quả bài thi

### Edge case

* Sinh viên chưa thi nhưng bấm xem kết quả.
* Sinh viên xem kết quả của sinh viên khác.
* Giảng viên xem bài thi của lớp không liên quan.
* Bài thi có điểm nhưng thiếu chi tiết câu hỏi đã thi.
* Câu hỏi trong bộ đề đã bị sửa sau khi sinh viên thi.
* Câu hỏi trong bộ đề đã bị xóa sau khi sinh viên thi.
* Đáp án đúng hiện tại khác đáp án đúng tại thời điểm thi.
* Sinh viên thi nhiều lần, hệ thống hiển thị sai lần thi.
* Bộ lọc ngày thi sai định dạng.
* Không tìm thấy dữ liệu theo lớp, môn, lần thi.
* Lỗi khi in hoặc export kết quả.

---

## 9. Bảng điểm môn học

### Edge case

* Lớp chưa có sinh viên.
* Lớp có sinh viên nhưng chưa ai thi.
* Một số sinh viên đã thi, một số chưa thi.
* Sinh viên có điểm nhưng thiếu thông tin họ tên.
* Điểm nhỏ hơn 0 hoặc lớn hơn 10 do lỗi dữ liệu.
* Điểm chữ không khớp điểm số.
* Chọn môn học không có đăng ký thi.
* Chọn lần thi không tồn tại.
* Có nhiều bản ghi điểm trùng MASV, MAMH, LAN do lỗi dữ liệu.
* Giáo viên không có quyền vẫn cố in bảng điểm.
* Lỗi khi xuất báo cáo hoặc in file.

---

## 10. Phân quyền

### Edge case

* Tài khoản không thuộc nhóm quyền nào.
* Tài khoản thuộc nhiều nhóm quyền cùng lúc.
* Role tồn tại trong app nhưng không tồn tại trong SQL Server.
* Role tồn tại trong SQL Server nhưng app không nhận diện được.
* PGV truy cập chức năng thi.
* Giảng viên truy cập chức năng tạo tài khoản.
* Sinh viên truy cập chức năng nhập câu hỏi.
* Sinh viên truy cập bảng điểm lớp.
* Người dùng đổi role trong lúc đang đăng nhập.
* Session cũ vẫn còn quyền sau khi tài khoản bị đổi role.
* Tài khoản bị xóa nhưng vẫn còn đang sử dụng hệ thống.
* Người dùng nhập URL/form trực tiếp để vượt phân quyền.

---

## 11. Tạo tài khoản

### Edge case

* Login rỗng.
* Password rỗng.
* Nhóm quyền chưa chọn.
* Chọn giáo viên rỗng.
* Giáo viên đã có tài khoản.
* Login đã tồn tại trong SQL Server.
* User đã tồn tại trong database nhưng login chưa tồn tại.
* Login tồn tại nhưng user chưa tồn tại.
* Role PGV/GIANGVIEN chưa tồn tại.
* Tạo login thành công nhưng tạo user thất bại.
* Tạo user thành công nhưng gán role thất bại.
* Password chứa ký tự đặc biệt gây lỗi SQL.
* Login chứa khoảng trắng.
* Login vượt độ dài SQL Server cho phép.
* PGV tự xóa tài khoản đang đăng nhập.
* Giảng viên cố tạo tài khoản mới.
* Sinh viên cố truy cập form tạo tài khoản.
* Mất kết nối CSDL khi đang tạo tài khoản.
* Hai PGV cùng tạo một login cùng lúc.
* Xóa tài khoản nhưng chưa xóa user trong database.
