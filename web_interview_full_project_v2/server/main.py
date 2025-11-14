from fastapi import FastAPI, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os, datetime, json

app = FastAPI(title="Web Interview Recorder API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cho phép tất cả nguồn (có thể thay bằng http://127.0.0.1:5500 nếu bạn dùng Live Server)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_ROOT = "uploads"
os.makedirs(UPLOAD_ROOT, exist_ok=True)

class VerifyTokenBody(BaseModel):
    token: str

class StartSessionBody(BaseModel):
    token: str
    userName: str

class FinishSessionBody(BaseModel):
    token: str
    folder: str
    questionsCount: int

@app.post("/api/verify-token")
async def verify_token(body: VerifyTokenBody):
    if body.token == "12345":
        return {"ok": True}
    raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/api/session/start")
async def start_session(body: StartSessionBody):
    now = datetime.datetime.now().strftime("%d_%m_%Y_%H_%M_")
    folder_name = now + body.userName.replace(" ", "_")
    folder_path = os.path.join(UPLOAD_ROOT, folder_name)
    os.makedirs(folder_path, exist_ok=True)

    meta = {
        "userName": body.userName,
        "uploadedAt": datetime.datetime.now().isoformat(),
        "timeZone": "Asia/Bangkok",
        "questions": []
    }
    with open(os.path.join(folder_path, "meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)

    return {"ok": True, "folder": folder_name}

@app.post("/api/upload-one")
async def upload_one(
    token: str = Form(...),
    folder: str = Form(...),
    questionIndex: int = Form(...),
    video: UploadFile = Form(...)
):
    if token != "12345":
        raise HTTPException(status_code=401, detail="Invalid token")

    folder_path = os.path.join(UPLOAD_ROOT, folder)
    if not os.path.exists(folder_path):
        raise HTTPException(status_code=404, detail="Folder not found")

    filename = f"Q{questionIndex}.webm"
    save_path = os.path.join(folder_path, filename)

    with open(save_path, "wb") as f:
        f.write(await video.read())

    meta_path = os.path.join(folder_path, "meta.json")
    if os.path.exists(meta_path):
        with open(meta_path, "r+", encoding="utf-8") as f:
            data = json.load(f)
            data["questions"].append(filename)
            f.seek(0)
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.truncate()

    return {"ok": True, "savedAs": filename}

@app.post("/api/session/finish")
async def finish_session(body: FinishSessionBody):
    meta_path = os.path.join(UPLOAD_ROOT, body.folder, "meta.json")
    if not os.path.exists(meta_path):
        raise HTTPException(status_code=404, detail="Session not found")

    with open(meta_path, "r+", encoding="utf-8") as f:
        data = json.load(f)
        data["questionsCount"] = body.questionsCount
        f.seek(0)
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.truncate()

    return {"ok": True}

@app.get("/")
def root():
    return {"message": "✅ FastAPI Web Interview Recorder is running!"}
