from fastapi import APIRouter, File, UploadFile, Form, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.security import verify_token, TokenError
from app.services.file_service import handle_upload
from typing import List

router = APIRouter()
security = HTTPBearer()

def require_role(token: str, required_role: str):
    try:
        payload = verify_token(token)
    except TokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    if payload.get("rol") != required_role:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
    return payload

@router.post("/upload")
async def upload_csv(
    parametro1: str = Form(...),
    parametro2: str = Form(...),
    file: UploadFile = File(...),
    creds: HTTPAuthorizationCredentials = Depends(security)
):
    # ensure role 'uploader' (demo)
    payload = require_role(creds.credentials, "uploader")
    result = await handle_upload(file, parametro1, parametro2, uploaded_by=payload.get("sub"))
    return result
