from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from jose import jwt
import json

from db.session import get_db
from models.user import User, AuthMethod
from schemas.user_schema import EmailAuth, TelegramAuth, UserResponse
from services.auth_service import hash_password
from core.config import SECRET_KEY_EMAIL, ALGORITHM

router = APIRouter()

ACCESS_TOKEN_EXPIRE_MINUTES = 60
@router.post("/register", response_model=UserResponse)
def register_user(user_data: EmailAuth, db: Session = Depends(get_db)):
    existing = db.query(AuthMethod).filter(
        AuthMethod.provider == "email",
        AuthMethod.provider_user_id == user_data.email
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="A user with this email already exists")
    
    new_user = User(user_name=user_data.email)
    db.add(new_user)
    db.flush()

    hashed_pw = hash_password(user_data.password)
    auth_method = AuthMethod(
        provider="email",
        provider_user_id=user_data.email,
        hashed_password=hashed_pw,
        user_id=new_user.id
    )
    db.add(auth_method)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("/oauth/{provider}/callback", response_model=UserResponse)
def oauth_callback(provider: str, code: str, db: Session = Depends(get_db)):
    # TODO
    pass

@router.post("/telegram", response_model=UserResponse)
def telegram_login(data: TelegramAuth, db: Session = Depends(get_db)):
    tg_id = str(data.telegram_id)
    user_name = data.user_name
    
    auth = db.query(AuthMethod).filter(
        AuthMethod.provider == "telegram",
        AuthMethod.provider_user_id == tg_id
    ).first()
    
    if auth:
        return auth.user

    new_user = User(user_name=user_name)
    db.add(new_user)
    db.flush()
    
    new_auth = AuthMethod(
        provider="telegram",
        provider_user_id=tg_id,
        user_id=new_user.id
    )
    db.add(new_auth)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Endpoint для логина по email.

    Args:
        form_data (OAuth2PasswordRequestForm): Form data containing username (email) and password.
        db (Session): Database session.

    Returns:
        dict: Dictionary with JWT token and token type.

    Raises:
        HTTPException: If the credentials are incorrect.
    """
    user_auth = db.query(AuthMethod).filter(
        AuthMethod.provider == "email",
        AuthMethod.provider_user_id == form_data.username
    ).first()
    
    if not user_auth:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect credentials"
        )

    if user_auth.hashed_password != hash_password(form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect credentials"
        )

    token_data = {
        "sub": str(user_auth.user_id),
        "auth_type": "email",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    token = jwt.encode(token_data, SECRET_KEY_EMAIL, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}
