from fastapi import Depends, HTTPException, status, APIRouter, Request
from sqlmodel import Session, select
from app.auth.dependencies import get_current_user
from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM
from app.core.middleware import limiter
from app.db.database import get_session
from app.models.user import User
from app.schemas.user import UserLogin, UserLoginResponse
from app.utils.jwt_handler import create_access_token, create_refresh_token
from app.utils.security import verify_password
from datetime import datetime, timedelta
from jose import jwt, JWTError
import pytz 


router = APIRouter()



@router.post("/login", response_model = UserLoginResponse)
@limiter.limit("5/minute")
def login(form_data: UserLogin, 
          request: Request, 
          session: Session = Depends(get_session)
):
    statement = select(User).where(User.email == form_data.email)
    result = session.exec(statement).first()

    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not result.is_verified:
        raise HTTPException(status_code=403, detail="Account not verified")
    
    if not verify_password(form_data.password, result.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect password")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": result.email}, expires_delta=access_token_expires
    )

    refresh_token_expires = timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    refresh_token = create_refresh_token(
        data={"sub": result.email}, expires_delta=refresh_token_expires
    )

    ist = pytz.timezone("Asia/Kolkata")
    result.last_login_at = datetime.now(ist)

    client_host = request.client.host
    result.last_login_ip = client_host

    session.add(result)
    session.commit()
    session.refresh(result)

    return UserLoginResponse(
        message = "Login successful", 
        user_id = result.id, 
        first_name = result.first_name or "User",
        last_login = result.last_login_at.strftime("%Y-%m-%d %H:%M:%S %Z"),
        last_login_ip = client_host,  
        access_token = access_token, 
        refresh_token = refresh_token
    )



@router.post("/refresh-token")
async def refresh_access_token(refresh_token: str):
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        token_type: str = payload.get("token_type")

        if user_id is None or token_type != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        new_access_token = create_access_token(data={"sub": user_id},)
        return {"access_token": new_access_token, "token_type": "bearer"}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate refresh token")
    


@router.get("/profile")
def read_profile(current_user: User = Depends(get_current_user)):
    return {"email": current_user.email, "user_id": current_user.id}