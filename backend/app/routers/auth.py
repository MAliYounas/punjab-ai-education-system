from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..auth import get_current_user, issue_token, verify_password
from ..database import get_db
from ..models import Classroom, School, User
from ..seed import audit

router = APIRouter(prefix="/api/auth", tags=["auth"])


class LoginIn(BaseModel):
    username: str
    password: str


@router.post("/login")
def login(body: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == body.username).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = issue_token(db, user)
    audit(db, user.id, "auth.login", "user", user.id, user.username)
    db.commit()
    return {"token": token, "user": serialize_user(db, user)}


@router.get("/me")
def me(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return serialize_user(db, user)


@router.post("/language")
def language(payload: dict, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    lang = payload.get("language", "en")
    if lang not in ("en", "ur"):
        raise HTTPException(400, "language must be en or ur")
    user.language = lang
    db.commit()
    return {"language": lang}


def serialize_user(db: Session, user: User):
    school = db.get(School, user.school_id) if user.school_id else None
    room = db.get(Classroom, user.classroom_id) if user.classroom_id else None
    return {
        "id": user.id,
        "name": user.name,
        "username": user.username,
        "role": user.role,
        "language": user.language,
        "grade": user.grade,
        "school": school.name if school else None,
        "classroom": room.name if room else None,
    }
