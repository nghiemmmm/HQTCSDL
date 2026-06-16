# Quy tắc đặt tên và chuẩn viết mã Python theo PEP 8

## I. Giới thiệu

Quy tắc đặt tên là tập hợp các chuẩn dùng để đặt tên biến, hàm, lớp, module, package và các thành phần khác trong chương trình.

Mục tiêu:

* Tăng khả năng đọc hiểu mã nguồn.
* Dễ bảo trì và mở rộng.
* Giúp các thành viên viết code thống nhất.
* Giảm lỗi do đặt tên mơ hồ.
* Chuẩn hóa phong cách viết code trong dự án.

---

## II. Nguyên tắc chung

### 1. Tên phải mô tả đúng mục đích

Tên biến, hàm, lớp nên cho người đọc biết ngay nó dùng để làm gì.

```python
customer_age = 20

def calculate_total_price():
    pass
```

---

### 2. Nhất quán trong toàn dự án

Không trộn nhiều kiểu đặt tên khác nhau cho cùng một loại thành phần.

Đúng:

```python
get_user_name()
get_user_email()
```

Sai:

```python
getUserName()
get_user_email()
```

---

### 3. Ưu tiên rõ nghĩa

Không viết tắt quá mức nếu làm người đọc khó hiểu.

Đúng:

```python
calculate_average_score()
```

Sai:

```python
calc_avg_scr()
```

---

### 4. Cân bằng giữa ngắn gọn và đủ nghĩa

Tên không nên quá ngắn gây mơ hồ, cũng không nên quá dài gây khó đọc.

Đúng:

```python
user_login_count
```

Sai:

```python
number_of_times_a_user_has_logged_into_the_system
```

---

## III. Quy tắc đặt tên theo loại thành phần

### 1. Biến

Dùng `snake_case`.

```python
user_name = "Nghiem"
total_price = 1000
is_active = True
```

---

### 2. Hàm

Dùng `snake_case`.

```python
def get_user():
    pass

def calculate_total():
    pass
```

---

### 3. Hàm hoặc biến kiểu boolean

Nên bắt đầu bằng:

* `is_`
* `has_`
* `can_`
* `should_`

```python
def is_valid():
    pass

def has_permission():
    pass

def can_edit():
    pass

def should_retry():
    pass
```

---

### 4. Lớp

Dùng `PascalCase`.

```python
class User:
    pass

class UserAccount:
    pass

class StudentService:
    pass
```

---

### 5. Phương thức

Phương thức trong lớp dùng `snake_case`.

```python
class User:

    def get_name(self):
        pass

    def update_email(self):
        pass
```

---

### 6. Hằng số

Dùng `UPPER_CASE`.

```python
MAX_LOGIN_ATTEMPTS = 5

JWT_SECRET_KEY = "secret"

ACCESS_TOKEN_EXPIRE_MINUTES = 30
```

---

### 7. Module

Tên file Python dùng `snake_case`.

```text
user_service.py
database.py
auth_utils.py
attendance_repository.py
```

---

### 8. Package

Tên thư mục package dùng chữ thường.

```text
app/
services/
repositories/
schemas/
models/
```

---

## IV. Quy tắc đặt tên trong lập trình hướng đối tượng

### Thành phần public

Dùng tên bình thường, không có dấu gạch dưới đầu tên.

```python
name

get_name()
```

---

### Thành phần protected

Chỉ là quy ước trong Python, dùng một dấu gạch dưới đầu tên.

```python
_name

_update_cache()
```

---

### Thành phần private

Dùng hai dấu gạch dưới đầu tên để Python áp dụng name mangling.

```python
__password

__encrypt()
```

---

### Phương thức dunder

Chỉ dùng các phương thức dunder khi đúng mục đích đặc biệt của Python.

```python
__init__
__str__
__repr__
__len__
__eq__
```

Ví dụ:

```python
class User:

    def __init__(self, name: str):
        self.name = name
```

---

## V. Hiểu đúng về `self`

```python
class User:

    def get_name(self):
        return self.name
```

Khi gọi:

```python
user.get_name()
```

Python hiểu tương đương:

```python
User.get_name(user)
```

`self` đại diện cho chính đối tượng hiện tại.

---

## VI. Đặt tên theo ngữ cảnh

### Biến trong vòng lặp

Đúng:

```python
for student in students:
    pass
```

Nên tránh:

```python
for s in students:
    pass
```

---

### Exception

Tên exception nên mô tả lỗi cụ thể.

```python
ValidationError

DatabaseConnectionError

AuthenticationError
```

---

### Context manager

Tên biến trong context manager nên rõ nghĩa.

```python
with open(file_path) as file:
    pass
```

---

### Biến boolean

```python
is_active

has_permission

can_edit

should_retry
```

---

## VII. Type hint

Luôn dùng type hint cho biến quan trọng, tham số hàm và kiểu trả về.

Biến:

```python
user_name: str

age: int

scores: list[int]
```

Hàm:

```python
def get_user(user_id: int) -> str:
    pass
```

---

### Giá trị có thể rỗng

```python
from typing import Optional

email: Optional[str]
```

---

### Danh sách

```python
list[User]
```

---

### Từ điển

```python
dict[str, str]
```

---

## VIII. Lỗi đặt tên thường gặp

### Viết tắt quá mức

Sai:

```python
usr_nm

calc_avg_scr
```

Đúng:

```python
user_name

calculate_average_score
```

---

### Tên quá dài

Sai:

```python
number_of_times_a_user_has_logged_into_the_system
```

Đúng:

```python
user_login_count
```

---

### Không nhất quán

Sai:

```python
getUserName()

get_user_email()
```

---

## IX. Quy tắc đặt tên trong FastAPI

### Router

```python
user_router

auth_router

attendance_router
```

---

### Service

```python
UserService

AuthService

AttendanceService
```

---

### Repository

```python
UserRepository

AttendanceRepository
```

---

### Schema

```python
UserCreate

UserUpdate

UserResponse
```

---

### Model

```python
User

AttendanceLog

FaceEmbedding
```

---

## X. Quy tắc đặt tên trong AI / Machine Learning

### Dataset

```python
train_dataset

test_dataset

validation_dataset
```

---

### Model

```python
face_recognition_model

light_estimation_model
```

---

### Hàm huấn luyện và dự đoán

```python
train_model()

evaluate_model()

predict_image()
```

---

### Siêu tham số

```python
learning_rate

batch_size

num_epochs

weight_decay
```

---

## XI. Quy tắc viết tài liệu trong code

### Docstring cho module

Mỗi file Python nên bắt đầu bằng docstring mô tả trách nhiệm chính của file.

```python
"""
User Service Module

Handles user-related business logic.

Responsibilities:
- Create user
- Update profile
- Change password
"""
```

---

### Docstring cho lớp

```python
class UserService:
    """
    Service responsible for user business logic.
    """
```

---

### Docstring cho hàm

```python
def calculate_total_price(
    price: float,
    quantity: int
) -> float:
    """
    Calculate total price.

    Args:
        price: Product unit price.
        quantity: Number of products.

    Returns:
        Total price.
    """
```

---

### Docstring cho hàm bất đồng bộ

```python
async def get_user_by_id(
    user_id: int
) -> User:
    """
    Retrieve user by identifier.

    Args:
        user_id: User identifier.

    Returns:
        User entity.

    Raises:
        NotFoundException:
            If user does not exist.
    """
```

---

## XII. Quy tắc import

### Thứ tự import chuẩn

```python
# Standard Library
from datetime import datetime

# Third Party
from fastapi import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

# Local Application
from app.schemas.user_schema import UserCreate
from app.services.user_service import UserService
```

---

### Tránh import toàn bộ

Sai:

```python
from user_service import *
```

Đúng:

```python
from user_service import UserService
```

---

## XIII. Cấu trúc dự án FastAPI

```text
app/
├── api/
├── routers/
├── services/
├── repositories/
├── models/
├── schemas/
├── core/
├── utils/
├── database/
```

---

### Đặt tên router

```python
user_router

attendance_router

report_router
```

---

### Đặt tên service

```python
UserService

AttendanceService

ReportService
```

---

### Đặt tên repository

```python
UserRepository

AttendanceRepository

ReportRepository
```

---

### Đặt tên schema

Schema cho request:

```python
UserCreate

UserUpdate

UserLogin
```

Schema cho response:

```python
UserResponse

UserDetailResponse
```

---

### Đặt tên model

```python
User

Attendance

ClassSection
```

---

## XIV. Quy tắc viết code sạch

### Độ dài hàm

Ưu tiên hàm ngắn, dễ đọc:

```python
< 50 lines
```

---

### Trách nhiệm của lớp

Mỗi lớp chỉ nên có một trách nhiệm chính.

Đúng:

```python
UserService
```

Sai:

```python
UserAndAttendanceAndReportService
```

---

### Tránh lặp code

Nếu một đoạn logic xuất hiện nhiều lần, hãy tách thành hàm hoặc lớp dùng lại được.

---

### Tên hàm phải rõ nghĩa

Đúng:

```python
calculate_average_score()
```

Sai:

```python
process()
```

---

## XV. Quy tắc kiến trúc FastAPI

### Tầng router

Trách nhiệm:

* Nhận request.
* Gọi validation/schema phù hợp.
* Gọi service.
* Trả response.

Không đặt logic nghiệp vụ phức tạp trong router.

---

### Tầng service

Trách nhiệm:

* Chứa logic nghiệp vụ.
* Kiểm tra quy tắc nghiệp vụ.
* Điều phối luồng xử lý của ứng dụng.

---

### Tầng repository

Trách nhiệm:

* Thao tác database.
* Thực thi truy vấn.

---

### Tầng schema

Trách nhiệm:

* Kiểm tra dữ liệu request.
* Chuẩn hóa dữ liệu response.

---

### Tầng model

Trách nhiệm:

* Định nghĩa entity/database model.

---

## XVI. Checklist PEP 8

### Đặt tên

* [ ] Tên mô tả rõ mục đích.
* [ ] Không viết tắt không cần thiết.
* [ ] Biến dùng `snake_case`.
* [ ] Hàm dùng `snake_case`.
* [ ] Lớp dùng `PascalCase`.
* [ ] Hằng số dùng `UPPER_CASE`.

---

### Tài liệu

* [ ] Có docstring cho module.
* [ ] Có docstring cho lớp.
* [ ] Có docstring cho hàm hoặc phương thức public.

---

### Type hint

* [ ] Tham số có type hint.
* [ ] Hàm có type hint cho kiểu trả về.

---

### FastAPI

* [ ] Router không chứa logic nghiệp vụ phức tạp.
* [ ] Service chứa logic nghiệp vụ.
* [ ] Repository xử lý truy cập database.
* [ ] Schema được dùng để validate request/response.

---

### Khả năng đọc hiểu

* [ ] Hàm ngắn gọn, dễ đọc.
* [ ] Lớp có trách nhiệm rõ ràng.
* [ ] Không lặp code không cần thiết.
* [ ] Import theo đúng thứ tự chuẩn.

---

## XVII. Ví dụ code FastAPI tốt

```python
"""
User Service Module

Handles user-related business logic.
"""

class UserService:
    """
    User business service.
    """

    async def get_user_by_id(
        self,
        user_id: int
    ) -> User:
        """
        Retrieve user by identifier.

        Args:
            user_id: User identifier.

        Returns:
            User entity.
        """
```

---

## XVIII. Nguyên tắc cuối cùng

Hãy viết code cho con người đọc trước, rồi mới đến máy tính thực thi.

Code tốt cần:

* Dễ đọc.
* Dễ bảo trì.
* Nhất quán.
* Có tài liệu phù hợp.
* Dễ dự đoán.
* Dễ mở rộng.

Một lập trình viên nên có thể đọc lại code sau nhiều tháng mà vẫn hiểu được mục đích và cách hoạt động của nó.
