from typing import Optional
import uuid
from datetime import datetime
from sqlmodel import SQLModel, Field

class User(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, index=True)
    email: str = Field(unique=True, index=True, nullable=False)
    hashed_password: str
    otp: Optional[str] = None
    otp_expires_at: Optional[datetime] = None
    is_verified: bool = Field(default=False)
    otp_attempts: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.now)  
    last_login_at: Optional[datetime] = None 
    password_changed_at: Optional[datetime] = None
    registered_ip: Optional[str] = None 
    last_login_ip: Optional[str] = None
