from uuid import uuid4
from fastapi import UploadFile, HTTPException
from .config import settings
ALLOWED={'image/jpeg':'.jpg','image/png':'.png','image/webp':'.webp'}
async def save_upload(file:UploadFile|None):
    if not file: return None
    if file.content_type not in ALLOWED: raise HTTPException(400,'Only JPEG, PNG, and WEBP images are allowed')
    data=await file.read()
    if len(data)>settings.max_upload_size: raise HTTPException(413,'File too large')
    name=f'{uuid4().hex}{ALLOWED[file.content_type]}'
    (settings.upload_path/name).write_bytes(data)
    return name
