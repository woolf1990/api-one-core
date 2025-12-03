from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.security import create_access_token, verify_token, TokenError

router = APIRouter()
security = HTTPBearer()

@router.post("/refresh")
def refresh(creds: HTTPAuthorizationCredentials = Depends(security)):
    token = creds.credentials
    try:
        payload = verify_token(token)
    except TokenError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    # token is valid and not expired -> issue new one
    new = create_access_token({"sub": payload.get("sub"), "rol": payload.get("rol")})
    return {"access_token": new, "expires_in": 15*60}
