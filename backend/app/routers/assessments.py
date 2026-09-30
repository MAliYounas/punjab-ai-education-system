import json
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..auth import get_current_user, require_roles
from ..database import get_db
from ..models import Approval, Assessment, Attempt, Chapter, Question, SLO, Topic, User
from ..seed import audit
from ..services.generator import generate_assessment, learning_material
from ..services.evaluator import evaluate_attempt
from ..services.recommender import analyse_attempt

router = APIRouter(prefix="/api", tags=["assessments"])


class GenerateIn(BaseModel):
    chapter_id: int
    topic_id: int | None = None
    difficulty: str = "medium"
    assessment_type: str = "quiz"
    qtypes: list[str] = ["mcq"]
    n: int = 8
    title: str | None = None
    language: str = "en"


class AttemptIn(BaseModel):
    answers: dict


@router.post("/assessments/generate")
def generate(body: GenerateIn, user: User = Depends(require_roles("admin", "teacher")), db: Session = Depends(get_db)):
    try:
        a = generate_assessment(
            db,
            user_id=user.id,
            chapter_id=body.chapter_id,
            topic_id=body.topic_id,
            difficulty=body.difficulty,
            assessment_type=body.assessment_type,
            qtypes=body.qtypes or ["mcq"],
            n=max(3, min(body.n, 30)),
            title=body.title,
            language=body.language,
        )
    except ValueError as e:
        raise HTTPException(400, str(e))
    db.add(Approval(content_type="assessment", content_id=a.id, status="pending"))
    audit(db, user.id, "assessment.generate", "assessment", a.id, a.title)
    db.commit()
    return serialize_assessment(db, a, include_answers=True)


@router.get("/assessments")
def list_assessments(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    q = db.query(Assessment).order_by(Assessment.id.desc())
    if user.role == "student":
        q = q.filter(Assessment.status == "published")
    rows = q.all()
    return [serialize_assessment(db, a, include_questions=False) for a in rows]


@router.get("/assessments/{aid}")
def get_assessment(aid: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    a = db.get(Assessment, aid)
    if not a:
        raise HTTPException(404, "Not found")
    if user.role == "student" and a.status != "published":
        raise HTTPException(403, "Not published")
    include_answers = user.role in ("teacher", "admin", "management")
    return serialize_assessment(db, a, include_answers=include_answers)


@router.post("/assessments/{aid}/review")
def review(aid: int, payload: dict, user: User = Depends(require_roles("admin", "teacher")), db: Session = Depends(get_db)):
    a = db.get(Assessment, aid)
    if not a:
        raise HTTPException(404, "Not found")
    decision = payload.get("status", "approved")
    notes = payload.get("notes", "")
    if decision not in ("approved", "published", "rejected"):
        raise HTTPException(400, "Invalid status")
    a.status = "published" if decision in ("approved", "published") else "rejected"
    ap = db.query(Approval).filter(Approval.content_id == aid, Approval.content_type == "assessment").order_by(Approval.id.desc()).first()
    if ap:
        ap.status = a.status
        ap.reviewer_id = user.id
        ap.notes = notes
    audit(db, user.id, "assessment.review", "assessment", a.id, a.status)
    db.commit()
    return serialize_assessment(db, a, include_answers=True)


@router.post("/assessments/{aid}/start")
def start(aid: int, user: User = Depends(require_roles("student", "teacher", "admin")), db: Session = Depends(get_db)):
    a = db.get(Assessment, aid)
    if not a:
        raise HTTPException(404, "Not found")
    if user.role == "student" and a.status != "published":
        raise HTTPException(403, "Waiting for teacher approval")
    attempt = Attempt(student_id=user.id, assessment_id=a.id, max_score=a.total_marks)
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    return {"attempt_id": attempt.id, "assessment": serialize_assessment(db, a, include_answers=False)}


@router.post("/attempts/{tid}/submit")
def submit(tid: int, body: AttemptIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    attempt = db.get(Attempt, tid)
    if not attempt or attempt.student_id != user.id:
        raise HTTPException(404, "Attempt not found")
    evaluate_attempt(db, attempt, body.answers)
    analysis = analyse_attempt(db, attempt)
    audit(db, user.id, "attempt.submit", "attempt", attempt.id, f"{attempt.percent}%")
    db.commit()
    return {
        "attempt_id": attempt.id,
        "percent": attempt.percent,
        "score": attempt.score,
        "max_score": attempt.max_score,
        "analysis": analysis,
        "review": _review_items(db, attempt),
    }


@router.get("/learning/{chapter_id}")
def learning(
    chapter_id: int,
    topic_id: int | None = None,
    simple: bool = False,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return learning_material(db, chapter_id, topic_id, simple=simple)


@router.post("/practice/targeted")
def targeted(payload: dict, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    chapter_id = int(payload.get("chapter_id"))
    n = int(payload.get("n") or 5)
    a = generate_assessment(
        db,
        user_id=user.id,
        chapter_id=chapter_id,
        topic_id=payload.get("topic_id"),
        difficulty=payload.get("difficulty") or "medium",
        assessment_type="practice",
        qtypes=["mcq", "short"],
        n=n,
        title="Targeted practice — learning gaps",
        auto_publish=True,
    )
    audit(db, user.id, "practice.targeted", "assessment", a.id, "gap practice")
    db.commit()
    include_answers = user.role != "student"
    return serialize_assessment(db, a, include_answers=include_answers)


def serialize_assessment(db: Session, a: Assessment, include_questions=True, include_answers=False):
    chapter = db.get(Chapter, a.chapter_id) if a.chapter_id else None
    topic = db.get(Topic, a.topic_id) if a.topic_id else None
    data = {
        "id": a.id,
        "title": a.title,
        "type": a.type,
        "difficulty": a.difficulty,
        "status": a.status,
        "total_marks": a.total_marks,
        "grounded": a.grounded,
        "created_at": a.created_at.isoformat() if a.created_at else None,
        "chapter": {"id": chapter.id, "number": chapter.number, "title": chapter.title} if chapter else None,
        "topic": {"id": topic.id, "title": topic.title} if topic else None,
    }
    if include_questions:
        qs = db.query(Question).filter(Question.assessment_id == a.id).all()
        items = []
        for q in qs:
            slo = db.get(SLO, q.slo_id) if q.slo_id else None
            item = {
                "id": q.id,
                "qtype": q.qtype,
                "stem": q.stem,
                "options": json.loads(q.options_json or "[]"),
                "difficulty": q.difficulty,
                "bloom": q.bloom,
                "marks": q.marks,
                "source_ref": q.source_ref,
                "source_excerpt": q.source_excerpt,
                "topic_id": q.topic_id,
                "slo_id": q.slo_id,
                "slo_code": slo.code if slo else None,
                "concept_id": q.concept_id,
            }
            if include_answers:
                item["correct_answer"] = q.correct_answer
                item["explanation"] = q.explanation
            items.append(item)
        data["questions"] = items
        data["count"] = len(items)
    else:
        data["count"] = db.query(Question).filter(Question.assessment_id == a.id).count()
    return data


def _review_items(db, attempt):
    from ..models import AttemptAnswer

    rows = (
        db.query(AttemptAnswer, Question)
        .join(Question, Question.id == AttemptAnswer.question_id)
        .filter(AttemptAnswer.attempt_id == attempt.id)
        .all()
    )
    out = []
    for ans, q in rows:
        out.append(
            {
                "question_id": q.id,
                "stem": q.stem,
                "qtype": q.qtype,
                "given": ans.answer,
                "correct": q.correct_answer,
                "is_correct": ans.is_correct,
                "marks_awarded": ans.marks_awarded,
                "marks": q.marks,
                "explanation": q.explanation,
                "source_ref": q.source_ref,
                "bloom": q.bloom,
            }
        )
    return out
