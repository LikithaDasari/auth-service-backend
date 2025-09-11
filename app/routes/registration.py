from fastapi import Depends, HTTPException, APIRouter, Request, BackgroundTasks
from sqlmodel import Session, select
from app.core.middleware import limiter
from app.db.database import get_session
from app.models.user import User
from app.schemas.user import CreateUser, UserVerify
from app.utils.email import send_otp_email, send_success_email
from app.utils.password_validation import validate_password
from app.utils.security import hash_password
from datetime import datetime, timedelta, timezone
import pytz  
import random


router = APIRouter()



@router.post("/registration")
@limiter.limit("3/minute")
def register_user(user_data: CreateUser, request: Request, session: Session =Depends(get_session)):

    existing = session.exec(select(User).where(User.email == user_data.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    validate_password(user_data.password)


    hashed_password = hash_password(user_data.password)
    otp = str(random.randint(100000, 999999))
    expiry_time = datetime.now(timezone.utc) + timedelta(minutes=5)

    ist = pytz.timezone("Asia/Kolkata")
    expiry_time_ist = expiry_time.astimezone(ist)
    client_host = request.client.host

    new_user = User(email=user_data.email, 
                    hashed_password = hashed_password, 
                    otp = otp, 
                    otp_expires_at=expiry_time,
                    otp_attempts=0,
                    created_at=datetime.now(ist), 
                    registered_ip = client_host 
                    )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    send_otp_email(new_user.email, otp)

    return {
        "message": f"User registered. Verify with OTP before it expires.",
        "user_id": new_user.id,
        "otp_expires_at": expiry_time_ist.strftime("%Y-%m-%d %H:%M:%S UTC"),
        "registered_ip": client_host}



@router.post("/verify")
@limiter.limit("5/minute")
async def verify_account(data: UserVerify, 
                         request: Request, 
                         session: Session = Depends(get_session), 
                         background_tasks: BackgroundTasks = None
):
    user = session.query(User).filter(User.id == data.user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.is_verified:
        raise HTTPException(status_code=400, detail="Account already verified")
        
    if datetime.utcnow() > user.otp_expires_at:
        raise HTTPException(status_code=400, detail="OTP has expired. Please request a new one.")
    
    if user.otp_attempts >= 2:   
        raise HTTPException(status_code=403, detail="Too many failed attempts. Please request a new OTP.")

    if user.otp != data.otp:
        user.otp_attempts += 1
        session.add(user)
        session.commit()
        raise HTTPException(status_code=400, detail=f"Invalid OTP. Attempts left: {3 - user.otp_attempts}")

    user.is_verified = True
    user.otp = None  
    user.otp_expires_at = None
    session.add(user)
    session.commit()


    background_tasks.add_task(send_success_email, user.email)

    return {"message": "Account verified successfully. Confirmation mail sent."}



@router.post("/resend-otp/{user_id}")
@limiter.limit("5/minute")
def resend_otp(user_id: str, 
               request: Request, 
               session: Session = Depends(get_session)
):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.is_verified:
        raise HTTPException(status_code=400, detail="Account already verified")

    new_otp = str(random.randint(100000, 999999))
    expiry_time = datetime.now(timezone.utc) + timedelta(minutes=5)

    user.otp = new_otp
    user.otp_expires_at = expiry_time

    session.add(user)
    session.commit()

    send_otp_email(user.email, new_otp)

    ist = pytz.timezone("Asia/Kolkata")
    new_expiry_time_ist = expiry_time.astimezone(ist)

    return {"message": "New OTP sent to email", 
            "user_id": user.id, 
            "otp_expires_at": new_expiry_time_ist.strftime("%Y-%m-%d %H:%M:%S UTC")}