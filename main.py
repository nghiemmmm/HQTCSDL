# import tensorflow as tf
from fastapi import Depends, FastAPI, Request# pip install "fastapi[standard]"
from fastapi.staticfiles import StaticFiles
from core.templates import Jinja2Templates
import uvicorn
import os
import datetime
import json
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse, RedirectResponse
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache import FastAPICache
from fastapi.middleware.cors import CORSMiddleware
from db.database import engine
from db import model
from router import user_router, giaovien_router, monHoc_router, lophoc_router,sinhvien_router, bode_router, dangKyThi_router, thi_router
from logs.logging_config import logger
from core.auth import get_current_user
from db.roles import Permission, has_permission

app = FastAPI(
    docs_url="/myapi",  # Đặt đường dẫn Swagger UI thành "/myapi"
    redoc_url=None  # Tắt Redoc UI
)

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")

# Vì các api này kết quả trả về không phải json mà là html, dẫn đến lỗi
EXCLUDED_PATHS = ["/myapi", "/redoc", "/openapi.json", "/modelane/getmode"]
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Middleware để ghi log mỗi khi có API được gọi.
    Cấu trúc log: `time - IP - API Name - Params - Result`
    Ví dụ: 2024-11-13 10:24:54,615 - 192.168.0.100 - / - {} - {"Message":"World"}
    """
    # Lấy thời gian hiện tại
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]

    # Lấy địa chỉ IP của người gọi API
    client_ip = request.client.host

    # Lấy tên endpoint và các tham số truyền vào
    api_name = request.url.path
    params = dict(request.query_params)  # Lấy query parameters nếu có

    # Bỏ qua log nếu đường dẫn nằm trong danh sách EXCLUDED_PATHS
    if api_name in EXCLUDED_PATHS:
        # Ghi log với thông tin "nothing"
        logger.info(
            "",
            extra={
                "ip": client_ip,
                "api_name": api_name,
                "params": "nothing",
                "result": "nothing",
            }
        )
        return await call_next(request)

    # Goi API va lay ket qua
    response = await call_next(request)

    content_type = response.headers.get("Content-Type", "")
    content_length = response.headers.get("Content-Length", "unknown")
    log_result = json.dumps({
        "status_code": response.status_code,
        "content_type": content_type,
        "content_length": content_length,
    })

    logger.info(
        "",
        extra={
            "ip": client_ip,
            "api_name": api_name,
            "params": json.dumps(params),
            "result": log_result,
        }
    )

    return response

# Khởi tạo in-memory cache trong event startup
@app.on_event("startup")
async def on_startup() -> None:
    in_memory_cache = InMemoryBackend()
    FastAPICache.init(in_memory_cache)
    print("Thong bao: FastAPI da khoi chay thanh cong!")

# app.include_router(employee_router.router)
app.include_router(user_router.router)
app.include_router(giaovien_router.router)
app.include_router(monHoc_router.router)
app.include_router(lophoc_router.router)
app.include_router(dangKyThi_router.router)
app.include_router(sinhvien_router.router)
app.include_router(bode_router.router)
# app.include_router(authentication.router)
# app.include_router(license_plate_router.router)
# app.include_router(vehicles_router.router)
# app.include_router(image_router.router)
# app.include_router(mode_lane_router.router)
# app.include_router(update_app_router.router)
# app.include_router(get_file_router.router)
# app.include_router(update_app.router)

app.include_router(thi_router.router)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/home")
async def home(user=Depends(get_current_user)):
    role = user.get("role")
    if has_permission(role, Permission.VIEW_CLASS):
        return RedirectResponse(url="/lop/", status_code=303)
    if has_permission(role, Permission.VIEW_EXAM_REGISTRATION):
        return RedirectResponse(url="/dangkythi", status_code=303)
    if has_permission(role, Permission.TAKE_EXAM) or has_permission(role, Permission.PRACTICE_EXAM):
        return RedirectResponse(url="/thi/", status_code=303)
    return RedirectResponse(url="/user/info", status_code=303)

# Tạo icon cho trang web api, nó sẽ hiển thị hình ảnh favicon ở thư mục `static/favicon.ico`
@app.get('/favicon.ico')
async def favicon():
    file_name = "favicon.ico"
    file_path = os.path.join(app.root_path, "static", file_name)
    return FileResponse(path=file_path, headers={"Content-Disposition": "attachment; filename=" + file_name})


# Tạo Bảng trong DB nếu nó chưa tồn tại
model.Base.metadata.create_all(engine)

"""
Cho phép các trang web, app, api trên cùng 1 máy tính có thể truy cập đến api này
Mặc định các api trên cùng 1 máy không thể chia sẻ tài nguyên cho nhau
Điều này phục vụ cho mục đích test, vì không thể lúc nào cũng có sẵn 2 máy tính khác nhau để test
"""
# origins = [
#     "http://localhost:3000",
#     "http://192.168.0.145"
# ]

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\\d+)?$",
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"]
)

if __name__ == "__main__":
    #Thêm tham số log_config= "logs\\logging_config.json" để chuyển các log của uvicorn vào tệp
    uvicorn.run("__main__:app", host="0.0.0.0", port=8000, log_level= "error", log_config= "logs\\logging_config.json")  # log_config= "logs\\logging_config.json"

    # Hoặc gõ trực tiếp lệnh `fastapi dev main.py` để vào chế độ developer
    # Hoặc gõ trực tiếp lệnh `fastapi run main.py` để vào chế độ lấy máy chạy làm server
