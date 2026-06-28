# CÁC LỖI NGHIỆP VỤ ĐÃ BẮT TRONG CHỨC NĂNG ĐĂNG KÝ THI

Dưới đây là danh sách chi tiết các lỗi nghiệp vụ và ràng buộc đã được thiết lập, kiểm tra và xử lý (bắt lỗi) trong chức năng **Đăng ký thi** của hệ thống. Các ràng buộc này được phân bổ ở cả tầng Schema (FastAPI Pydantic Validation) và tầng Nghiệp vụ (Service Layer / Stored Procedures).

---

## 1. Ràng buộc dữ liệu đầu vào (Schema Validation)
Được định nghĩa tại lớp `DangKyThi` trong tệp `schemas/schemas.py`:
* **Trình độ thi**: Chỉ nhận một trong các giá trị trình độ viết hoa: `A`, `B` hoặc `C` (định dạng regex `^[ABC]$`).
* **Lần thi**: Chỉ được phép là lần `1` hoặc lần `2` (`1 <= lan <= 2`).
* **Số câu thi**: Số câu hỏi thi bắt buộc phải nằm trong khoảng từ `10` đến `100` câu (`10 <= socauthi <= 100`).
* **Thời gian thi**: Thời gian thi (phút) phải nằm trong khoảng từ `5` đến `60` phút (`5 <= thoigian <= 60`).

---

## 2. Kiểm tra sự tồn tại của thực thể (Entity Existence Checks)
Được kiểm tra tại tệp `services/exam_registration_service.py`:
* **Môn học không tồn tại**: Hệ thống từ chối đăng ký nếu mã môn học (`mamh`) không tồn tại trong cơ sở dữ liệu.
* **Lớp học không tồn tại**: Hệ thống từ chối đăng ký nếu mã lớp học (`malop`) không tồn tại trong cơ sở dữ liệu.
* **Giáo viên không tồn tại**: Hệ thống từ chối đăng ký nếu mã giáo viên (`magv`) được chỉ định không tồn tại.

---

## 3. Các quy tắc nghiệp vụ đặc thù (Business Logic Rules)
Được xử lý tại tệp `services/exam_registration_service.py`:

### A. Thời gian đăng ký thi
* **Ngày thi tối thiểu**: Ngày thi đăng ký bắt buộc phải từ **ngày mai trở đi** (lớn hơn hoặc bằng `00:00` của ngày tiếp theo). Giảng viên không được phép đăng ký lịch thi diễn ra trong ngày hôm nay, ngăn chặn tuyệt đối học sinh vào thi ngay trong ngày tạo lịch.

### B. Môn học được phép đăng ký (Dành cho Giảng viên)
* **Giới hạn môn học soạn đề**: Nếu người đăng ký là Giảng viên (`GIANGVIEN`), họ chỉ được phép đăng ký lịch thi cho các môn học mà **chính họ đã soạn ít nhất một câu hỏi trong bộ đề**. Giảng viên không được phép đăng ký thi cho các môn học mà họ chưa từng đóng góp câu hỏi.

### C. Tránh đăng ký trùng lịch
* **Trùng lịch thi**: Một lớp, một môn học và một lần thi chỉ được đăng ký tối đa một lần. Nếu đã tồn tại lịch thi cho tổ hợp `(malop, mamh, lan)`, hệ thống sẽ báo lỗi trùng lịch (`ConflictError`).

### D. Trình tự các lần thi và khoảng cách thời gian
* **Yêu cầu lần thi trước**: Không được phép đăng ký thi lần `2` nếu lớp học và môn học đó **chưa từng được đăng ký thi lần 1**.
* **Khoảng cách giữa hai lần thi**: Ngày thi của lần `2` bắt buộc phải **sau ngày thi lần 1 ít nhất là 1 ngày**.

### E. Kiểm tra ngân hàng đề thi (Số câu hỏi khả dụng)
* **Kiểm tra bộ đề**: Trước khi ghi nhận đăng ký thi, hệ thống sẽ gọi stored procedure để đếm số lượng câu hỏi hiện có trong bộ đề ở trình độ đã chọn.
* **Quy tắc bù câu hỏi**:
  * Đề thi phải có đủ số câu hỏi theo yêu cầu.
  * Nếu thiếu câu hỏi ở trình độ cao (A hoặc B), hệ thống hỗ trợ bù câu hỏi ở trình độ thấp hơn liền kề (bù tối đa 30% tổng số câu thi, đảm bảo ít nhất 70% số câu đúng trình độ đăng ký).
  * Nếu tổng số câu hỏi (bao gồm cả bù trình độ dưới) không đáp ứng đủ số câu cần thi, hệ thống sẽ **từ chối đăng ký thi** và yêu cầu bổ sung câu hỏi hoặc giảm số câu thi.

---

## 4. Ràng buộc khi Chỉnh sửa hoặc Xóa lịch thi
* **Không được sửa thông tin cốt lõi**: Khi sửa lịch thi, hệ thống không cho phép thay đổi `Lớp học`, `Môn học` hoặc `Lần thi`.
* **Quyền sở hữu**: Giảng viên chỉ được phép hiệu chỉnh hoặc xóa lịch thi do **chính mình tạo ra**. Giảng viên không thể can thiệp vào lịch thi của đồng nghiệp (PGV thì có quyền quản lý toàn bộ).
* **Thời gian lịch thi**: Chỉ cho phép chỉnh sửa hoặc xóa lịch đăng ký thi khi **chưa đến ngày thi**. Nếu lịch thi đã đến giờ thi hoặc đã trôi qua, hệ thống sẽ khóa chức năng sửa/xóa để đảm bảo an toàn.

---

# CÁC LỖI NGHIỆP VỤ ĐÃ BẮT TRONG CHỨC NĂNG THI TRẮC NGHIỆM

Dưới đây là danh sách chi tiết các lỗi nghiệp vụ và ràng buộc được áp dụng trong quá trình làm bài thi, lưu trữ tạm thời và nộp bài thi chính thức.

## 1. Ràng buộc quyền tham gia phòng thi (Authorization Checks)
* **Quyền làm bài thi chính thức**: Chỉ có tài khoản vai trò Sinh viên (`SINHVIEN`) mới được phép tham gia thi chính thức và ghi điểm vào bảng điểm (`BANGDIEM`).
* **Chế độ thi thử của Giảng viên**: Giảng viên (`GIANGVIEN`) được quyền gọi chức năng thi để làm bài thi thử nghiệm (`practice`), hệ thống vẫn chấm điểm nhưng không ghi nhận kết quả vào bảng điểm `BANGDIEM`. 
* **Phòng thi của lớp**: Sinh viên chỉ được phép tham gia thi đối với các lịch thi đăng ký cho đúng lớp học của mình. Việc truy cập lịch thi của lớp khác sẽ bị từ chối truy cập (`PermissionDeniedError` - "Khong duoc xem lich thi cua lop khac").

---

## 2. Kiểm tra tính hợp lệ của đợt thi (Date & Registration Checks)
* **Đăng ký đợt thi**: Phải tồn tại một lịch đăng ký thi hợp lệ được tạo bởi phòng giáo vụ hoặc giảng viên cho môn học, lần thi và lớp tương ứng.
* **Thời gian mở đề thi**:
  * **Chưa đến ngày thi**: Sinh viên không được phép vào thi trước ngày thi đã đăng ký trên lịch (`ConflictError` - "Chưa đến ngày thi").
  * **Đã quá hạn ngày thi**: Sinh viên không được phép làm bài thi nếu đã quá hạn ngày thi được đăng ký trên lịch (`ConflictError` - "Đã quá hạn"). Các lịch thi đã quá hạn (thời gian hiện tại > thời gian ngày thi + thời lượng làm bài) sẽ **bị ẩn hoàn toàn**, không hiển thị trong danh sách chọn của sinh viên.
* **Ưu tiên hiển thị lịch thi trong ngày**: Danh sách các lịch thi đổ ra cho sinh viên sẽ luôn ưu tiên sắp xếp các lịch thi diễn ra trong ngày hôm nay lên trên cùng, sau đó mới đến các lịch thi trong tương lai để sinh viên dễ dàng nhận biết và chọn đúng đợt thi của ngày hôm đó.

---

## 3. Quy tắc ngăn chặn thi lại (Prevent Retaking)
* **Một lần thi duy nhất**: Sinh viên không được phép tham gia làm bài thi nếu đã có kết quả điểm thi được ghi nhận trong bảng điểm `BANGDIEM` cho môn học và lần thi tương ứng (`ConflictError` - "Đã thi" hoặc "Ban da hoan thanh bai thi nay roi, khong duoc phep thi lai").

---

## 4. Cơ chế khôi phục phiên thi khi gặp sự cố (Resumption & Reconnect)
* **Tự động khôi phục bài thi đang làm**: Nếu sinh viên bị mất kết nối, tắt trình duyệt hoặc log out đột ngột, khi đăng nhập lại trong ngày thi, hệ thống sẽ tự động khôi phục phiên thi cũ (trạng thái `DANG_LAM`) thay vì tạo bộ đề mới.
* **Bảo toàn thứ tự câu hỏi**: Bộ đề câu hỏi được giữ nguyên thứ tự xáo trộn ngẫu nhiên ban đầu từ phiên thi đã tạo.
* **Giữ nguyên tiến độ bài làm**: Tất cả đáp án sinh viên đã click chọn trước đó và câu hỏi đang dừng lại được tải đầy đủ.
* **Bảo toàn thời gian thực tế**: Thời gian làm bài còn lại được tính toán tự động dựa trên thời điểm bắt đầu thi thực tế (`batdau_luc`) và thời gian làm bài tối đa. Sinh viên không thể gia tăng thời gian thi bằng cách thoát ứng dụng.
* **Chặn tiếp tục phiên đã kết thúc**: Nếu phiên thi đã chuyển sang trạng thái kết thúc (`DA_NOP` hoặc `HET_GIO`), hệ thống cấm sinh viên truy cập lại để tiếp tục làm bài.

---

## 5. Ràng buộc tự động nộp bài và chấm điểm (Autosave & Submit Rules)
* **Hết giờ làm bài**: Khi thời gian còn lại về `0`, mọi hành động tương tác hoặc lưu bài tiếp theo sẽ tự động chuyển trạng thái phiên thi thành `HET_GIO` và kích hoạt tự động nộp bài thi.
* **Không được nộp lại**: Bài thi đã nộp thành công (`DA_NOP`) không được phép nộp lại hoặc chỉnh sửa điểm số.
* **Làm tròn điểm số**: Điểm số được hệ thống tự động chấm dựa trên đáp án đúng của bộ đề, làm tròn đến `2` chữ số thập phân trước khi gọi thủ tục lưu điểm.
* **Tự động nộp bài khi rời tab thi**:
  * Hệ thống giám sát hành vi của sinh viên. Nếu sinh viên rời khỏi màn hình phòng thi (chuyển sang tab khác hoặc ẩn trình duyệt), hệ thống sẽ đếm và cảnh báo.
  * Nếu vượt quá giới hạn tối đa (**3 lần** rời màn hình), hệ thống sẽ khóa bài làm và tự động nộp bài thi ngay lập tức để đảm bảo tính minh bạch.


---

# CÁC LỖI NGHIỆP VỤ ĐÃ BẮT TRONG CHỨC NĂNG NHẬP CÂU HỎI THI (BỘ ĐỀ)

Dưới đây là danh sách chi tiết các lỗi nghiệp vụ và ràng buộc được áp dụng khi giảng viên hoặc phòng giáo vụ thêm mới, hiệu chỉnh hoặc xóa câu hỏi trong ngân hàng đề thi.

## 1. Ràng buộc dữ liệu đầu vào (Schema & Model Validation)
* **Thông tin bắt buộc**: Nội dung câu hỏi, mã môn học, trình độ, đáp án A, B, C, D và đáp án đúng không được phép để trống.
* **Định dạng đáp án đúng**: Chỉ chấp nhận các giá trị đáp án đúng viết hoa là `A`, `B`, `C` hoặc `D` (được validate qua biểu thức chính quy `^[ABCD]$`).
* **Định dạng trình độ**: Chỉ chấp nhận trình độ học thuật viết hoa là `A`, `B` hoặc `C` (được validate qua biểu thức chính quy `^[ABC]$`).
* **Độ dài giới hạn**:
  * Mã môn học (`mamh`) giới hạn tối đa **5 ký tự**.
  * Mã giáo viên (`magv`) giới hạn tối đa **8 ký tự**.
  * Các nội dung đáp án A, B, C, D giới hạn tối đa **200 ký tự** mỗi đáp án (được nâng lên từ 50 ký tự để hỗ trợ các câu hỏi chứa nội dung dài).

---

## 2. Các quy tắc nghiệp vụ đặc thù (Business Logic Rules)
* **Bảo vệ quyền tác giả (Ownership Enforcement)**:
  * Khi Giảng viên (`GIANGVIEN`) thêm mới hoặc sửa câu hỏi, hệ thống sẽ tự động gán thuộc tính `magv` theo mã giảng viên của tài khoản đang đăng nhập, ngăn chặn tuyệt đối hành vi giả mạo hoặc tạo câu hỏi thay cho đồng nghiệp khác.
  * Giảng viên chỉ được phép xem, sửa hoặc xóa các câu hỏi do **chính mình tạo ra**. Mọi hành vi can thiệp vào câu hỏi của giảng viên khác đều bị chặn lại (`PermissionDeniedError` - "Khong duoc thao tac cau hoi cua giao vien khac").
* **Ngăn chặn trùng lặp nội dung đáp án**: Bốn đáp án A, B, C, D bắt buộc phải có nội dung hoàn toàn khác biệt sau khi đã chuẩn hóa (bỏ khoảng trắng thừa và không phân biệt chữ hoa chữ thường). Nếu có bất kỳ đáp án nào trùng nội dung, hệ thống sẽ báo lỗi (`ValidationError` - "Bốn đáp án A, B, C, D không được trùng nội dung.").

---

## 3. Ràng buộc bảo toàn dữ liệu đề thi
* **Không sửa/xóa câu hỏi đã được thi**: Trước khi tiến hành hiệu chỉnh hoặc xóa một câu hỏi, hệ thống sẽ thực hiện kiểm tra trạng thái (`check-status`). Nếu câu hỏi đó đã từng được sử dụng để phát sinh đề thi cho bất kỳ sinh viên nào, hệ thống sẽ **khóa quyền hiệu chỉnh/xóa** để bảo toàn lịch sử thi cử và tránh làm sai lệch kết quả điểm của sinh viên.

---

## 4. Khả năng tương thích cơ sở dữ liệu (Database Compatibility & Replication)
* **Khắc phục lỗi xung đột trigger**: Khi thực hiện các câu lệnh INSERT/UPDATE trên bảng có trigger trong SQL Server, SQLAlchemy mặc định sử dụng mệnh đề `OUTPUT` sẽ gây ra lỗi `pyodbc.ProgrammingError (334)`. Hệ thống đã tắt tính năng này bằng cách khai báo tùy chọn `{"implicit_returning": False}` cho các bảng `BODE` và `PHIENTHI` trong tệp cấu hình Model.
* **Tự động sinh mã câu hỏi dự phòng (Identity Fallback)**: Trong môi trường Phân tán / Nhân bản (Merge Replication), bảng dữ liệu tại các phân mảnh phụ (Subscriber) có thể được đồng bộ schema mà không giữ thuộc tính tự tăng `IDENTITY` của cột khóa chính `CAUHOI`. 
  * Hệ thống tự động kiểm tra xem cột `CAUHOI` của bảng `BODE` có thuộc tính `IDENTITY` hay không bằng cách truy vấn thông tin metadata từ SQL Server.
  * Nếu **có**: Hệ thống để SQL Server tự động tạo mã tự tăng.
  * Nếu **không**: Hệ thống tự động tính toán mã tiếp theo thông qua truy vấn `MAX(CAUHOI) + 1` và gán trước khi ghi vào cơ sở dữ liệu. Nhờ đó, chức năng tạo câu hỏi có thể hoạt động hoàn hảo và không bị lỗi `NULL` trong mọi cấu hình sao chép CSDL.
