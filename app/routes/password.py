from fastapi import Depends, HTTPException, APIRouter
from sqlmodel import Session, select
from app.auth.dependencies import get_current_user
from app.db.database import get_session
from app.models.user import User
from app.schemas.user import ChangePassword, ChangePasswordResponse
from app.utils.email import send_password_change_email, reset_password_email
from app.utils.password_validation import validate_password
from app.utils.security import hash_password, verify_password
from datetime import datetime, timedelta, timezone
import pytz 
import random


router = APIRouter()



@router.post("/change-password", response_model = ChangePasswordResponse)
def change_password(
    data: ChangePassword,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    
    if data.new_password != data.confirm_password:
        raise HTTPException(status_code=400, detail="New passwords do not match")

    if not verify_password(data.old_password, current_user.hashed_password):
        raise HTTPException(status_code=401, detail="Old password is incorrect")

    if verify_password(data.new_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="New password must be different from old password")

    validate_password(data.new_password)

    current_user.hashed_password = hash_password(data.new_password)
    current_user.password_changed_at = datetime.now()

    session.add(current_user)
    session.commit()
    session.refresh(current_user)

    send_password_change_email(current_user.email)

    return ChangePasswordResponse(
        message = "Password changed successfully"
    )
@router.post("/forgot-password")
def forgot_password(email: str, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == email)).first()
    if not user:
        raise HTTPException(status_code=404, detail="Email not registered")

    otp = str(random.randint(100000, 999999))

    expiry_time = datetime.now(timezone.utc) + timedelta(minutes=5)

    ist = pytz.timezone("Asia/Kolkata")
    expiry_time_ist = expiry_time.astimezone(ist)

    user.otp = otp
    user.otp_expires_at = expiry_time
    session.add(user)
    session.commit()
    session.refresh(user)

    reset_password_email(user.email, otp)
    return {"message": f"OTP sent to {user.email}. Valid till {expiry_time_ist} UTC"}

@router.post("/reset-password")
def reset_password(email: str, otp: str, new_password: str, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == email)).first()
    if not user:
        raise HTTPException(status_code=404, detail="Email not registered")

    if not user.otp or not user.otp_expires_at or user.otp_expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="OTP expired or invalid")

    if user.otp != otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    # Update password
    user.hashed_password = hash_password(new_password)
    user.otp = None
    user.otp_expires_at = None
    session.add(user)
    session.commit()
    session.refresh(user)

    return {"message": "Password reset successful"}