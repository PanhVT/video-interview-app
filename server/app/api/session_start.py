from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.time_utils import make_folder_name
from app.storage.file_manager import ensure_session_folder

router = APIRouter()

class StartRequest(BaseModel):
    token: str
    userName: str

@router.post('/session/start')
def session_start(req: StartRequest):
    if req.token != "12345":
        raise HTTPException(status_code=401, detail="Invalid token")
    folder = make_folder_name(req.userName)
    ensure_session_folder(folder)
    return {"ok": True, "folder": folder}