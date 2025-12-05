from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class VerifyRequest(BaseModel):
    token: str

@router.post('/verify-token')
def verify_token(req: VerifyRequest):
    # demo token check
    if req.token == "12345":
        return {"ok": True}
    raise HTTPException(status_code=401, detail="Invalid token")