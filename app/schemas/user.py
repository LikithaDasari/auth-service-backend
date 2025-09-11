from pydantic import constr, BaseModel, EmailStr
class CreateUser(BaseModel):
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