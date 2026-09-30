import hashlib
import secrets
from datetime import datetime
from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session
from .database import get_db
from .models import SessionToken, User


def hash_password(password: str) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode(), b"peip-salt", 120000).hex()


def verify_password(password: str, stored: str) -> bool:
    return hash_password(password) == stored


def issue_token(db: Session, user: User) -> str:
    token = secrets.token_hex(24)
    db.add(SessionToken(token=token, user_id=user.id, created_at=datetime.utcnow()))
    db.commit()
    return token


def get_current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Sign in required")
    token = authorization.split(" ", 1)[1].strip()
    row = db.query(SessionToken).filter(SessionToken.token == token).first()
    if not row:
        raise HTTPException(status_code=401, detail="Session expired")
    user = db.get(User, row.user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def require_roles(*roles):
    def _inner(user: User = Depends(get_current_user)):
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="Not permitted for this role")
        return user

    return _inner
