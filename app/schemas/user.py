from pydantic import constr, BaseModel, EmailStr
from datetime import datetime
from typing import Optional
class CreateUser(BaseModel):
    first_name: str
    email : EmailStr
    password: constr(min_length=8, strip_whitespace=True) # type: ignore
    
class UserVerify(BaseModel):
    user_id: str
    otp: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class ChangePassword(BaseModel):
    old_password: str 
    new_password: str 
    confirm_password: str

class CreateUserResponse(BaseModel):
    message: str
    user_id: str
    otp_expires_at: str
    registered_ip: Optional[str] = None

    class Config:
        orm_mode = True


class UserVerifyResponse(BaseModel):
    message: str

class UserLoginResponse(BaseModel):
    message : str
    first_name: str
    user_id: str 
    last_login : str
    last_login_ip : Optional[str] = None  
    access_token : str 
    refresh_token : str

    class Config:
        orm_mode = True



class ChangePasswordResponse(BaseModel):
    message : str