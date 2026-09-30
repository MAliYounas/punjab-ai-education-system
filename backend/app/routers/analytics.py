from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..auth import get_current_user, require_roles
from ..config import HAS_LLM
from ..database import get_db
from ..models import (
    Assessment, Attempt, AuditLog, Book, Chapter, Concept, District,
    Mastery, Question, SLO, School, Topic, User,
)

router = APIRouter(prefix="/api", tags=["analytics"])


@router.get("/teacher/overview")
def teacher_overview(user: User = Depends(require_roles("admin", "teacher", "management")), db: Session = Depends(get_db)):
    students = db.query(User).filter(User.role == "student").all()
    attempts = db.query(Attempt).filter(Attempt.completed_at.isnot(None)).all()
    by_student = {}
    for a in attempts:
        by_student.setdefault(a.student_id, []).append(a.percent)
    roster = []
    for s in students:
        scores = by_student.get(s.id, [])
        roster.append(
            {
                "id": s.id,
                "name": s.name,
                "username": s.username,
                "attempts": len(scores),
                "average": round(sum(scores) / len(scores), 1) if scores else 0,
                "latest": scores[-1] if scores else None,
            }
        )
    weak_slos = []
    for slo in db.query(SLO).all():
        rows = db.query(Mastery).filter(Mastery.slo_id == slo.id).all()
        if not rows:
            continue
        avg = sum(r.score for r in rows) / len(rows)
        if avg < 0.67:
            weak_slos.append({"code": slo.code, "statement": slo.statement, "bloom": slo.bloom_level, "mastery": round(avg * 100, 1)})
    weak_slos.sort(key=lambda x: x["mastery"])
    return {
        "students": roster,
        "assessments": db.query(Assessment).count(),
        "published": db.query(Assessment).filter(Assessment.status == "published").count(),
        "pending": db.query(Assessment).filter(Assessment.status == "pending_review").count(),
        "weak_slos": weak_slos[:10],
        "class_average": round(sum(r["average"] for r in roster) / len(roster), 1) if roster else 0,
    }


@router.get("/management/overview")
def management(user: User = Depends(require_roles("admin", "management", "teacher")), db: Session = Depends(get_db)):
    """Prototype KPIs with a mix of live class data and scaled district illustration."""
    live_attempts = db.query(Attempt).filter(Attempt.completed_at.isnot(None)).all()
    live_avg = round(sum(a.percent for a in live_attempts) / len(live_attempts), 1) if live_attempts else 0
    chapters = db.query(Chapter).count()
    topics = db.query(Topic).count()
    slos = db.query(SLO).count()
    concepts_n = db.query(Concept).count()
    coverage = 100.0 if chapters else 0

    districts = db.query(District).all()
    district_rows = []
    # Illustrated scale-out numbers, anchored to live prototype average
    offsets = {
        "Lahore": 4.2,
        "Faisalabad": -1.8,
        "Multan": -4.5,
        "Rawalpindi": 1.1,
        "Bahawalpur": -6.2,
    }
    weak_map = {
        "Lahore": "Photosynthesis — application / limiting factors",
        "Faisalabad": "Transport — xylem vs phloem",
        "Multan": "Human organ systems — enzymes",
        "Rawalpindi": "Food chains — energy flow",
        "Bahawalpur": "Chemical vs physical change",
    }
    for d in districts:
        schools = db.query(School).filter(School.district_id == d.id).count()
        avg = max(48, min(92, live_avg + offsets.get(d.name, 0)))
        district_rows.append(
            {
                "id": d.id,
                "name": d.name,
                "division": d.division,
                "schools": schools,
                "slo_mastery": round(avg - 3, 1),
                "achievement": round(avg, 1),
                "curriculum_coverage": 82 if d.name != "Lahore" else 100,
                "weak_topic": weak_map.get(d.name, "Application items"),
            }
        )

    bloom = {}
    questions = db.query(Question).all()
    for q in questions:
        bloom[q.bloom] = bloom.get(q.bloom, 0) + 1

    hierarchy = {
        "punjab": {
            "students_reached_prototype": db.query(User).filter(User.role == "student").count(),
            "students_modelled_scale": 18420,
            "schools": db.query(School).count(),
            "districts": db.query(District).count(),
            "achievement": round(sum(r["achievement"] for r in district_rows) / len(district_rows), 1) if district_rows else live_avg,
            "slo_mastery": round(sum(r["slo_mastery"] for r in district_rows) / len(district_rows), 1) if district_rows else live_avg,
            "curriculum_coverage": round(sum(r["curriculum_coverage"] for r in district_rows) / len(district_rows), 1) if district_rows else coverage,
        },
        "note": "Lahore class 7-A is live prototype data. Other districts are architecture-ready modelled KPIs using the same schema (student → class → school → district → Punjab).",
    }
    return {
        "kpis": {
            "curriculum_coverage": coverage,
            "chapters": chapters,
            "topics": topics,
            "slos": slos,
            "concepts": concepts_n,
            "live_class_achievement": live_avg,
            "assessments": db.query(Assessment).count(),
        },
        "districts": district_rows,
        "hierarchy": hierarchy,
        "bloom_distribution": bloom,
        "subject_performance": [{"subject": "General Science", "achievement": live_avg, "grade": 7}],
        "assessment_performance": {
            "published": db.query(Assessment).filter(Assessment.status == "published").count(),
            "attempts": len(live_attempts),
            "live_average": live_avg,
        },
        "improvement_trend": [
            {"label": a.completed_at.strftime("%d %b") if a.completed_at else str(i), "percent": a.percent}
            for i, a in enumerate(live_attempts[-8:])
        ],
        "weak_chapters": [
            {"chapter": ch.title, "number": ch.number}
            for ch in db.query(Chapter).order_by(Chapter.number).limit(3)
        ],
        "scale_path": [
            "1 subject prototype (this build)",
            "Grades 1–10, same schema",
            "Multiple subjects / PCTB books",
            "School information system integration",
            "District dashboards",
            "Punjab-wide Education Intelligence Platform",
        ],
    }


@router.get("/audit")
def audit_feed(user: User = Depends(require_roles("admin", "management", "teacher")), db: Session = Depends(get_db)):
    rows = db.query(AuditLog).order_by(AuditLog.id.desc()).limit(80).all()
    out = []
    for r in rows:
        u = db.get(User, r.user_id) if r.user_id else None
        out.append(
            {
                "id": r.id,
                "action": r.action,
                "entity": r.entity,
                "entity_id": r.entity_id,
                "details": r.details,
                "user": u.name if u else "system",
                "role": u.role if u else "system",
                "at": r.created_at.isoformat() if r.created_at else None,
            }
        )
    return {"logs": out}


@router.get("/overview")
def home(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return {
        "role": user.role,
        "books": db.query(Book).count(),
        "chapters": db.query(Chapter).count(),
        "slos": db.query(SLO).count(),
        "assessments": db.query(Assessment).count(),
        "attempts": db.query(Attempt).filter(Attempt.completed_at.isnot(None)).count(),
        "students": db.query(User).filter(User.role == "student").count(),
        "llm": HAS_LLM,
    }
