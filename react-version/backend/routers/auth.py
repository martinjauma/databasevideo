from fastapi import APIRouter, HTTPException, Depends, Header
from services import auth_service
from pydantic import BaseModel

router = APIRouter(prefix="/api/auth", tags=["auth"])

class LoginRequest(BaseModel):
    token: str

@router.post("/verify")
async def verify_login(request: LoginRequest):
    try:
        user_info = auth_service.verify_google_token(request.token)
        if not user_info:
            raise HTTPException(status_code=401, detail="Invalid Google token")
        
        email = user_info.get("email")
        auth_service.log_login_event(email)
        
        access_token = auth_service.create_access_token(data={"sub": email, "name": user_info.get("name")})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "email": email,
                "name": user_info.get("name"),
                "picture": user_info.get("picture"),
                "subscription": auth_service.check_subscription_status(email)
            }
        }
    except Exception as e:
        print(f"CRITICAL ERROR in verify_login: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_status(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = authorization.split(" ")[1]
    try:
        from jose import jwt
        payload = jwt.decode(token, auth_service.SECRET_KEY, algorithms=[auth_service.ALGORITHM])
        email = payload.get("sub")
        return {
            "email": email,
            "subscription": auth_service.check_subscription_status(email)
        }
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid session")
