from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .db import SessionLocal
from .auth import decode_token
from .models import User

oauth2 = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def current_user(token: str = Depends(oauth2), db: Session = Depends(get_db)) -> User:
    subject = decode_token(token)
    if not subject:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.email == subject).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user
