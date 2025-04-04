from typing import Optional
from pydantic import BaseModel, EmailStr

class EmailAuth(BaseModel):
    email: EmailStr
    password: str

class TelegramAuth(BaseModel):
    telegram_id: int
    user_name: str

class OAuthAuth(BaseModel):
    provider: str
    provider_user_id: str

class UserCreate(BaseModel):
    user_name: str
    email_auth: Optional[EmailAuth] = None
    telegram_auth: Optional[TelegramAuth] = None
    oauth_auth: Optional[OAuthAuth] = None

class UserResponse(BaseModel):
    id: int
    user_name: str

    class ConfigDict:
        from_attributes = True
