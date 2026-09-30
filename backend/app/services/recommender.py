import json
from sqlalchemy.orm import Session
from ..models import Attempt, AttemptAnswer, Assessment, Book, Chapter, Concept, Mastery, Question, Recommendation, SLO, Topic


def analyse_attempt(db: Session, attempt: Attempt) -> dict:
    rows = (
        db.query(AttemptAnswer, Question)
        .join(Question, Question.id == AttemptAnswer.question_id)
        .filter(AttemptAnswer.attempt_id == attempt.id)
        .all()
    )
    weak, strong = [], []
    bloom_stats = {}
    difficulty_stats = {}
    concept_stats = {}
    slo_stats = {}
    for ans, q in rows:
        bloom_stats.setdefault(q.bloom, {"ok": 0, "n": 0})
        bloom_stats[q.bloom]["n"] += 1
        bloom_stats[q.bloom]["ok"] += 1 if ans.is_correct else 0
        difficulty_stats.setdefault(q.difficulty, {"ok": 0, "n": 0})
        difficulty_stats[q.difficulty]["n"] += 1
        difficulty_stats[q.difficulty]["ok"] += 1 if ans.is_correct else 0
        if q.concept_id:
            concept_stats.setdefault(q.concept_id, {"ok": 0, "n": 0})
            concept_stats[q.concept_id]["n"] += 1
            concept_stats[q.concept_id]["ok"] += 1 if ans.is_correct else 0
        if q.slo_id:
            slo_stats.setdefault(q.slo_id, {"ok": 0, "n": 0})
            slo_stats[q.slo_id]["n"] += 1
            slo_stats[q.slo_id]["ok"] += 1 if ans.is_correct else 0

    for cid, st in concept_stats.items():
        c = db.get(Concept, cid)
        rate = st["ok"] / st["n"]
        rec = {"id": cid, "name": c.name if c else "Concept", "rate": round(rate, 2), "source_ref": c.source_ref if c else ""}
        (strong if rate >= 0.67 else weak).append(rec)

    weak_slos = []
    for sid, st in slo_stats.items():
        s = db.get(SLO, sid)
        rate = st["ok"] / st["n"]
        if s:
            item = {"id": sid, "code": s.code, "statement": s.statement, "bloom": s.bloom_level, "rate": round(rate, 2)}
            if rate < 0.67:
                weak_slos.append(item)

    text, activities = _narrative(attempt, strong, weak, weak_slos, bloom_stats)
    rec = Recommendation(
        student_id=attempt.student_id,
        attempt_id=attempt.id,
        text=text,
        activities_json=json.dumps(activities),
    )
    db.add(rec)
    db.flush()
    return {
        "percent": attempt.percent,
        "score": attempt.score,
        "max_score": attempt.max_score,
        "strong": strong,
        "weak": weak,
        "weak_slos": weak_slos,
        "bloom": {k: round(100 * v["ok"] / v["n"], 1) for k, v in bloom_stats.items() if v["n"]},
        "difficulty": {k: round(100 * v["ok"] / v["n"], 1) for k, v in difficulty_stats.items() if v["n"]},
        "recommendation": text,
        "activities": activities,
        "recommendation_id": rec.id,
    }


def _narrative(attempt, strong, weak, weak_slos, bloom_stats):
    strong_names = ", ".join(s["name"] for s in strong[:3]) or "core recall items"
    weak_names = ", ".join(w["name"] for w in weak[:3]) or "application items"
    apply_rate = None
    if "Apply" in bloom_stats and bloom_stats["Apply"]["n"]:
        apply_rate = bloom_stats["Apply"]["ok"] / bloom_stats["Apply"]["n"]
    remember_rate = None
    if "Remember" in bloom_stats and bloom_stats["Remember"]["n"]:
        remember_rate = bloom_stats["Remember"]["ok"] / bloom_stats["Remember"]["n"]

    if remember_rate is not None and apply_rate is not None and remember_rate >= 0.7 and apply_rate < 0.5:
        text = (
            f"The student understands the definition-level ideas ({strong_names}) but is weak in applying "
            f"them ({weak_names}). Recommend concept revision followed by five application-level questions."
        )
    elif attempt.percent >= 80:
        text = (
            f"Strong performance ({attempt.percent}%). Maintain {strong_names}. "
            f"A short stretch quiz on {weak_names or 'higher Bloom levels'} will deepen mastery."
        )
    elif attempt.percent >= 50:
        text = (
            f"Partial mastery ({attempt.percent}%). {strong_names} are relatively secure. "
            f"Priority gaps: {weak_names}. Revise those concepts with simpler explanations, then targeted practice."
        )
    else:
        text = (
            f"Foundational gaps ({attempt.percent}%). Return to the Learn stage for {weak_names}. "
            f"Use the simpler explanations and worked examples before reassessment."
        )
    if weak_slos:
        text += " Struggling SLOs: " + "; ".join(f"{s['code']} ({s['bloom']})" for s in weak_slos[:3]) + "."

    activities = []
    for w in weak[:3]:
        activities.append(f"Revise concept: {w['name']} (simple explanation + example)")
    if weak:
        activities.append("Complete 5 application-level questions on weak concepts")
        activities.append("Reassess with a short targeted quiz")
    else:
        activities.append("Advance to the next topic in the chapter sequence")
    return text, activities


def student_dashboard(db: Session, student_id: int) -> dict:
    attempts = (
        db.query(Attempt)
        .filter(Attempt.student_id == student_id, Attempt.completed_at.isnot(None))
        .order_by(Attempt.completed_at.asc())
        .all()
    )
    percents = [a.percent for a in attempts]
    overall = round(sum(percents) / len(percents), 1) if percents else 0
    latest = attempts[-1] if attempts else None
    rec = (
        db.query(Recommendation)
        .filter(Recommendation.student_id == student_id)
        .order_by(Recommendation.id.desc())
        .first()
    )
    mastery_rows = db.query(Mastery).filter(Mastery.student_id == student_id).all()
    topics, slos, concepts = [], [], []
    for m in mastery_rows:
        if m.topic_id:
            t = db.get(Topic, m.topic_id)
            if t:
                topics.append({"id": t.id, "name": t.title, "score": round(m.score * 100, 1), "attempts": m.attempts_count})
        if m.slo_id:
            s = db.get(SLO, m.slo_id)
            if s:
                slos.append({"id": s.id, "code": s.code, "statement": s.statement, "bloom": s.bloom_level, "score": round(m.score * 100, 1)})
        if m.concept_id:
            c = db.get(Concept, m.concept_id)
            if c:
                concepts.append({"id": c.id, "name": c.name, "score": round(m.score * 100, 1), "source_ref": c.source_ref})
    topics.sort(key=lambda x: x["score"])
    slos.sort(key=lambda x: x["score"])
    concepts = _unique(concepts, "id")
    concepts.sort(key=lambda x: x["score"])
    improvement = None
    if len(percents) >= 2:
        improvement = round(percents[-1] - percents[0], 1)

    chapter_map, subject_map, diff_map = {}, {}, {}
    for a in attempts:
        paper = db.get(Assessment, a.assessment_id)
        ch = db.get(Chapter, paper.chapter_id) if paper and paper.chapter_id else None
        if ch:
            chapter_map.setdefault(ch.id, {"name": f"Ch.{ch.number} {ch.title}", "scores": []})
            chapter_map[ch.id]["scores"].append(a.percent)
            book = db.get(Book, ch.book_id)
            if book:
                subject_map.setdefault(book.subject, [])
                subject_map[book.subject].append(a.percent)
        for ans in a.answers:
            q = db.get(Question, ans.question_id)
            if not q:
                continue
            dkey = q.difficulty or "medium"
            diff_map.setdefault(dkey, {"ok": 0, "n": 0})
            diff_map[dkey]["n"] += 1
            if ans.is_correct:
                diff_map[dkey]["ok"] += 1

    chapters = [
        {"name": v["name"], "score": round(sum(v["scores"]) / len(v["scores"]), 1)}
        for v in chapter_map.values()
    ]
    chapters.sort(key=lambda x: x["score"])
    subjects = [
        {"name": k, "score": round(sum(v) / len(v), 1)}
        for k, v in subject_map.items()
    ]
    difficulty = {
        k: round(100 * v["ok"] / v["n"], 1) for k, v in diff_map.items() if v["n"]
    }

    return {
        "overall": overall,
        "subject": "General Science",
        "subjects": subjects,
        "chapters": chapters,
        "difficulty": difficulty,
        "attempts": [
            {"id": a.id, "assessment_id": a.assessment_id, "percent": a.percent, "score": a.score, "max_score": a.max_score, "completed_at": a.completed_at.isoformat() if a.completed_at else None}
            for a in attempts
        ],
        "trend": percents,
        "improvement": improvement,
        "topics": _unique(topics, "id"),
        "slos": _unique(slos, "id"),
        "concepts": concepts,
        "strong": [c for c in concepts if c["score"] >= 67][:6],
        "weak": [c for c in concepts if c["score"] < 67][:6],
        "recommendation": rec.text if rec else None,
        "activities": json.loads(rec.activities_json) if rec and rec.activities_json else [],
        "latest_percent": latest.percent if latest else None,
    }


def _unique(rows, key):
    seen, out = set(), []
    for row in rows:
        if row.get(key) in seen:
            continue
        seen.add(row.get(key))
        out.append(row)
    return out
