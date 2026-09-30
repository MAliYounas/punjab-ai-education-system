import re
from datetime import datetime
from sqlalchemy.orm import Session
from ..models import Attempt, AttemptAnswer, Mastery, Question


def normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (text or "").lower()).strip()


def score_answer(question: Question, given: str) -> tuple[bool, float]:
    given_n = normalize(given)
    correct_n = normalize(question.correct_answer)
    if question.qtype in ("mcq", "tf"):
        ok = given_n == correct_n or given.strip() == question.correct_answer.strip()
        return ok, question.marks if ok else 0
    if not given_n:
        return False, 0
    if correct_n and (correct_n in given_n or given_n in correct_n):
        return True, question.marks
    keys = [w for w in correct_n.split() if len(w) > 3]
    if not keys:
        return False, 0
    hit = sum(1 for w in keys if w in given_n)
    ratio = hit / len(keys)
    if ratio >= 0.55:
        return True, question.marks
    if ratio >= 0.3:
        return False, round(question.marks * 0.5, 1)
    return False, 0


def evaluate_attempt(db: Session, attempt: Attempt, answers: dict) -> Attempt:
    questions = db.query(Question).filter(Question.assessment_id == attempt.assessment_id).all()
    db.query(AttemptAnswer).filter(AttemptAnswer.attempt_id == attempt.id).delete()
    score = 0.0
    max_score = 0.0
    for q in questions:
        max_score += q.marks
        raw = answers.get(str(q.id), answers.get(q.id, ""))
        ok, awarded = score_answer(q, str(raw))
        score += awarded
        db.add(
            AttemptAnswer(
                attempt_id=attempt.id,
                question_id=q.id,
                answer=str(raw),
                is_correct=ok,
                marks_awarded=awarded,
            )
        )
        _bump(db, attempt.student_id, q, 1.0 if ok else (0.5 if awarded else 0.0))
    attempt.score = score
    attempt.max_score = max_score
    attempt.percent = round(100.0 * score / max_score, 1) if max_score else 0
    attempt.completed_at = datetime.utcnow()
    db.flush()
    return attempt


def _bump(db, student_id, question, value):
    for field, fid in (("slo_id", question.slo_id), ("topic_id", question.topic_id), ("concept_id", question.concept_id)):
        if not fid:
            continue
        row = db.query(Mastery).filter(Mastery.student_id == student_id, getattr(Mastery, field) == fid).first()
        if not row:
            db.add(Mastery(student_id=student_id, **{field: fid}, score=value, attempts_count=1))
        else:
            n = row.attempts_count + 1
            row.score = (row.score * row.attempts_count + value) / n
            row.attempts_count = n
            row.last_updated = datetime.utcnow()
