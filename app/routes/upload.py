from fastapi import APIRouter, UploadFile
import os

router = APIRouter()

UPLOAD_DIR = "data/uploads"

@router.post("/upload")
async def upload_file(file: UploadFile):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    content = await file.read()
    
    with open(file_path, "wb") as f:
        f.write(content)
    
    return {"filename": file.filename}