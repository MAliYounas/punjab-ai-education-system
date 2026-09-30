import json
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..auth import get_current_user, require_roles
from ..database import get_db
from ..models import CopilotLog, User
from ..seed import audit
from ..services.copilot import run_copilot
from ..services.recommender import student_dashboard

router = APIRouter(prefix="/api", tags=["copilot"])


class CopilotIn(BaseModel):
    prompt: str
    chapter_id: int | None = None
    student_id: int | None = None


@router.post("/copilot")
def copilot(body: CopilotIn, user: User = Depends(require_roles("admin", "teacher", "management")), db: Session = Depends(get_db)):
    result = run_copilot(db, user, body.prompt, body.chapter_id, body.student_id)
    db.add(
        CopilotLog(
            user_id=user.id,
            prompt=body.prompt,
            intent=result.get("intent", ""),
            response_json=json.dumps({k: v for k, v in result.items() if k != "material"}, default=str)[:8000],
        )
    )
    audit(db, user.id, "copilot.ask", "copilot", user.id, body.prompt[:180])
    db.commit()
    return result


@router.get("/students/{sid}/dashboard")
def dash(sid: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role == "student" and user.id != sid:
        sid = user.id
    return student_dashboard(db, sid)


@router.get("/me/dashboard")
def mine(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    target = user.id
    if user.role != "student":
        stu = db.query(User).filter(User.username == "student").first()
        target = stu.id if stu else user.id
    return student_dashboard(db, target)
