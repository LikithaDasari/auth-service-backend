from fastapi import Depends, HTTPException, status, APIRouter
from sqlmodel import Session, select
from app.db.database import get_session
from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_MINUTES
from app.models.user import User
from app.schemas.user import CreateUser
from app.utils.security import hash_password, verify_password
from app.core.config import SECRET_KEY, ALGORITHM
from app.utils.jwt_handler import create_access_token, create_refresh_token
from app.auth.dependencies import get_current_user
from datetime import timedelta
from jose import jwt, JWTError

router = APIRouter()


@router.post("/registration")
def register_user(user_data: CreateUser, session: Session =Depends(get_session)):

    hashed_password = hash_password(user_data.password)
    new_user = User(username = user_data.username, hashed_password = hashed_password)

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return {"message":"User registered successfully", "user_id": new_user.id}


@router.post("/login")
def login(form_data: CreateUser = Depends(), session: Session = Depends(get_session)):
    statement = select(User).where(User.username == form_data.username)
    result = session.exec(statement).first()

    if not result:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(form_data.password, result.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect password")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": result.username}, expires_delta=access_token_expires
    )

    refresh_token_expires = timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    refresh_token = create_refresh_token(
        data={"sub": result.username}, expires_delta=refresh_token_expires
    )

    return {"message": "Login successful", "user_id": result.id, "access_token": access_token, "refresh_token": refresh_token}


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
    return {"username": current_user.username, "user_id": current_user.id}