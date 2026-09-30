import re
from sqlalchemy.orm import Session
from ..models import Chapter, User, Approval
from .generator import generate_assessment, learning_material
from .recommender import student_dashboard


def interpret(prompt: str) -> dict:
    p = (prompt or "").lower()
    intent = "explain"
    atype = "quiz"
    qtypes = ["mcq"]
    n = 10
    difficulty = "medium"
    grade = 7
    chapter_n = None

    m = re.search(r"grade\s*(\d+)", p)
    if m:
        grade = int(m.group(1))
    m = re.search(r"chapter\s*(\d+)", p)
    if m:
        chapter_n = int(m.group(1))
    m = re.search(r"(\d+)\s*(mcq|question|item)", p)
    if m:
        n = int(m.group(1))
    if "easy" in p:
        difficulty = "easy"
    if "hard" in p or "difficult" in p:
        difficulty = "hard"
    if "medium" in p:
        difficulty = "medium"

    if "homework" in p:
        intent, atype, qtypes = "generate", "homework", ["short", "mcq", "fib"]
    elif "assignment" in p:
        intent, atype, qtypes = "generate", "assignment", ["short", "long", "conceptual"]
    elif "exam" in p or "examination" in p or "30-mark" in p or "30 mark" in p:
        intent, atype, qtypes = "generate", "exam", ["mcq", "tf", "short", "long"]
        if "30" in p:
            n = 12
    elif "worksheet" in p:
        intent, atype, qtypes = "generate", "worksheet", ["mcq", "fib", "tf"]
    elif "quiz" in p or "mcq" in p:
        intent, atype, qtypes = "generate", "quiz", ["mcq"] if "mcq" in p else ["mcq", "tf"]
    elif "remedial" in p or "practice" in p or "targeted" in p:
        intent, atype, qtypes = "generate", "practice", ["mcq", "short"]
        difficulty = "easy"
    elif "slo" in p or "struggling" in p or "gap" in p or "weak" in p:
        intent = "gaps"
    elif "explain" in p or "weak student" in p or "simpler" in p:
        intent = "explain"
    elif "summary" in p or "learning material" in p:
        intent = "material"

    return {
        "intent": intent,
        "type": atype,
        "qtypes": qtypes,
        "n": n,
        "difficulty": difficulty,
        "grade": grade,
        "chapter_n": chapter_n,
        "raw": prompt,
    }


def run_copilot(db: Session, user: User, prompt: str, chapter_id: int | None = None, student_id: int | None = None):
    spec = interpret(prompt)
    chapter = None
    if chapter_id:
        chapter = db.get(Chapter, chapter_id)
    elif spec["chapter_n"]:
        chapter = db.query(Chapter).filter(Chapter.number == spec["chapter_n"]).first()
    if chapter is None:
        chapter = db.query(Chapter).filter(Chapter.number == 2).first() or db.query(Chapter).first()

    if spec["intent"] == "generate":
        assessment = generate_assessment(
            db,
            user_id=user.id,
            chapter_id=chapter.id,
            topic_id=None,
            difficulty=spec["difficulty"],
            assessment_type=spec["type"],
            qtypes=spec["qtypes"],
            n=spec["n"],
            language=user.language or "en",
        )
        db.add(Approval(content_type="assessment", content_id=assessment.id, status="pending"))
        msg = (
            f"Draft {assessment.type} created from approved Chapter {chapter.number} ({chapter.title}). "
            "Status: pending teacher review before students can see it."
        )
        if any(w in prompt.lower() for w in ("math", "mathematics", "riazi", "ریاضی")):
            msg += (
                " Mathematics is not in this prototype corpus, so the engine used the approved "
                "General Science knowledge base — the same pipeline that will serve maths once that textbook is ingested."
            )
        return {
            "intent": spec["intent"],
            "message": msg,
            "assessment_id": assessment.id,
            "chapter": {"id": chapter.id, "title": chapter.title, "number": chapter.number},
            "grounded": True,
        }

    if spec["intent"] == "explain":
        material = learning_material(db, chapter.id, simple=True)
        return {
            "intent": spec["intent"],
            "message": f"Simpler explanations for a weaker student, grounded in Chapter {chapter.number}.",
            "material": material,
            "chapter": {"id": chapter.id, "title": chapter.title, "number": chapter.number},
        }

    if spec["intent"] == "material":
        return {
            "intent": spec["intent"],
            "message": "Learning material generated from the knowledge base.",
            "material": learning_material(db, chapter.id, simple=False),
            "chapter": {"id": chapter.id, "title": chapter.title, "number": chapter.number},
        }

    sid = student_id
    if not sid:
        stu = db.query(User).filter(User.role == "student", User.username == "student").first()
        sid = stu.id if stu else None
    dash = student_dashboard(db, sid) if sid else {}
    weak_slos = [s for s in dash.get("slos", []) if s["score"] < 67]
    return {
        "intent": "gaps",
        "message": "SLO struggle report from live mastery data (prototype class 7-A).",
        "weak_slos": weak_slos[:8],
        "weak_concepts": dash.get("weak", []),
        "recommendation": dash.get("recommendation"),
        "chapter": {"id": chapter.id, "title": chapter.title, "number": chapter.number},
    }
