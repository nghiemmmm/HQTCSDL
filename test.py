from fastapi import APIRouter, UploadFile, File, HTTPException
import uuid
import os
import tempfile
import shutil
import asyncio


router = APIRouter()


# async def async_predict(image_path, image2_path):
#     # Chạy hàm predict trong luồng phụ để không làm nghẽn luồng chính
#     return await asyncio.to_thread(predict, image=image_path, image2=image2_path)

@router.post("/user")
