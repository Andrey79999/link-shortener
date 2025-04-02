import hashlib
from fastapi import Depends, HTTPException, status, Header, Request
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from models.user import User
from db.session import get_db

from core.config import SECRET_KEY_EMAIL, SECRET_KEY_TELEGRAM, ALGORITHM


def hash_password(password: str) -> str:
   """
   Hash a password using the MD5 algorithm.

   Args:
       password (str): The password to hash.

   Returns:
       str: The hashed password.
   """
   hash_object = hashlib.md5(password.encode())
   return hash_object.hexdigest()

def get_current_user(request: Request, db: Session = Depends(get_db)):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header not passed"
        )
    scheme, _, token = auth_header.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format"
        )

    try:
        unverified_payload = jwt.get_unverified_claims(token)
        auth_type = unverified_payload.get("auth_type")
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    if auth_type == "email":
        secret_key = SECRET_KEY_EMAIL
    elif auth_type == "telegram":
        secret_key = SECRET_KEY_TELEGRAM
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unknown authorization type"
        )

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"Failed to verify credentials. Auth_type: {auth_type}",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user
