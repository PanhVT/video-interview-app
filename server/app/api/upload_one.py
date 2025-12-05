from fastapi import APIRouter, File, Form, UploadFile, HTTPException
from app.storage.file_manager import save_question_file, update_metadata

router = APIRouter()


@router.post('/upload-one')
async def upload_one(token: str = Form(...), folder: str = Form(...), questionIndex: str = Form(...), video: UploadFile = File(...)):
    """Upload single question video"""
    if token != "12345":
        raise HTTPException(status_code=401, detail="Invalid token")
    
    contents = await video.read()
    save_question_file(folder, int(questionIndex), contents)
    
    # Update metadata
    update_metadata(folder, int(questionIndex))
    
    return {
        "ok": True,
        "savedAs": f"Q{questionIndex}.webm"
    }