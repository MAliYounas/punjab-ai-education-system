import json
import random
import re
from sqlalchemy.orm import Session
from ..models import Assessment, Chapter, Concept, Question, SLO, Term, Topic
from . import ai_client
from .rag import retrieve

BLOOM = ["Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create"]

DISTRACTOR_BANK = {
    "photosynthesis": ["respiration", "transpiration", "fermentation", "diffusion"],
    "chlorophyll": ["haemoglobin", "melanin", "keratin", "insulin"],
    "stomata": ["xylem vessels", "root hairs", "alveoli", "nephrons"],
    "xylem": ["phloem", "alveoli", "arteries", "stomata"],
    "phloem": ["xylem", "veins", "bronchi", "capillaries"],
    "glucose": ["nitrogen gas", "cellulose only in animals", "haemoglobin", "urea"],
    "oxygen": ["nitrogen as the food product", "methane", "ammonia", "ozone as food"],
    "enzyme": ["hormone only", "vitamin C", "mineral salt", "antibody"],
    "alveoli": ["stomata", "nephrons", "villi", "chloroplasts"],
}


def generate_assessment(
    db: Session,
    *,
    user_id: int,
    chapter_id: int,
    topic_id: int | None,
    difficulty: str,
    assessment_type: str,
    qtypes: list[str],
    n: int,
    title: str | None = None,
    language: str = "en",
    auto_publish: bool = False,
) -> Assessment:
    chapter = db.get(Chapter, chapter_id)
    if not chapter:
        raise ValueError("Chapter not found")
    topic = db.get(Topic, topic_id) if topic_id else None
    concepts = _concepts(db, chapter_id, topic_id)
    slos = _slos(db, chapter_id, topic_id)
    terms = db.query(Term).filter(Term.chapter_id == chapter_id).all()
    if not concepts:
        raise ValueError("No curriculum concepts found for this selection")

    query = f"{chapter.title} {topic.title if topic else ''} {' '.join(c.name for c in concepts[:8])}"
    sources = retrieve(db, query, chapter_id=chapter_id, topic_id=topic_id, k=8)
    context = "\n\n".join(f"[{h['source_ref']}] {h['text']}" for h in sources)

    items = []
    llm_items = _try_llm(context, chapter, topic, difficulty, qtypes, n, language)
    if llm_items:
        items = llm_items
    if len(items) < n:
        items.extend(_engine_items(concepts, slos, terms, difficulty, qtypes, n - len(items), chapter))
    items = items[:n]

    status = "published" if auto_publish else "pending_review"
    assessment = Assessment(
        title=title or _default_title(assessment_type, chapter, topic, n),
        type=assessment_type,
        chapter_id=chapter.id,
        topic_id=topic.id if topic else None,
        difficulty=difficulty,
        created_by=user_id,
        status=status,
        language=language,
        grounded=True,
        total_marks=0,
    )
    db.add(assessment)
    db.flush()
    total = 0
    for item in items:
        concept = _match_concept(concepts, item.get("concept") or item.get("stem", ""))
        slo = _match_slo(slos, item.get("bloom") or "Understand")
        marks = int(item.get("marks") or _marks(item.get("qtype", "mcq"), assessment_type))
        total += marks
        source = concept.source_ref if concept else (sources[0]["source_ref"] if sources else f"Ch.{chapter.number}")
        excerpt = item.get("source_excerpt") or (concept.source_excerpt if concept else (sources[0]["text"][:240] if sources else ""))
        db.add(
            Question(
                assessment_id=assessment.id,
                qtype=item.get("qtype", "mcq"),
                stem=sanitize_age(item["stem"]),
                options_json=json.dumps([sanitize_age(o) for o in (item.get("options") or [])]),
                correct_answer=sanitize_age(item.get("correct_answer") or item.get("correct") or ""),
                explanation=sanitize_age(item.get("explanation") or ""),
                difficulty=item.get("difficulty") or difficulty,
                bloom=item.get("bloom") or "Understand",
                marks=marks,
                slo_id=slo.id if slo else None,
                topic_id=(topic.id if topic else (concept.topic_id if concept else None)),
                concept_id=concept.id if concept else None,
                source_ref=item.get("source_ref") or source,
                source_excerpt=excerpt[:500],
            )
        )
    assessment.total_marks = total
    db.flush()
    return assessment


def _try_llm(context, chapter, topic, difficulty, qtypes, n, language):
    prompt = (
        f"Generate {n} assessment items for Grade 7 General Science, "
        f"Chapter {chapter.number}: {chapter.title}. "
        f"Topic: {topic.title if topic else 'whole chapter'}. Difficulty: {difficulty}. "
        f"Allowed types: {', '.join(qtypes)}. Language: {language}. "
        "Each item: qtype, stem, options (4 for mcq, True/False for tf, empty for others), "
        "correct_answer, explanation, difficulty, bloom, marks, source_ref (from excerpts), "
        "source_excerpt, concept. MCQ distractors must be plausible misconceptions. "
        'Return JSON {"items":[...]} only using the excerpts.'
    )
    raw = ai_client.complete(prompt, context, json_mode=True)
    data = ai_client.parse_json(raw) or {}
    items = data.get("items") or data.get("questions") or []
    clean = []
    for it in items:
        if it.get("stem") and it.get("correct_answer") or it.get("correct"):
            if "correct" in it and "correct_answer" not in it:
                it["correct_answer"] = it["correct"]
            clean.append(it)
    return clean


def _engine_items(concepts, slos, terms, difficulty, qtypes, n, chapter):
    random.seed()
    items = []
    pool = list(concepts)
    random.shuffle(pool)
    i = 0
    while len(items) < n and pool:
        concept = pool[i % len(pool)]
        qtype = qtypes[len(items) % len(qtypes)]
        slo = slos[len(items) % len(slos)] if slos else None
        bloom = slo.bloom_level if slo else _bloom_for(qtype, difficulty)
        fn = {
            "mcq": _mcq,
            "tf": _tf,
            "fib": _fib,
            "short": _short,
            "long": _long,
            "conceptual": _conceptual,
        }.get(qtype, _mcq)
        item = fn(concept, terms, chapter, difficulty, bloom)
        if slo:
            item["slo"] = slo.code
        items.append(item)
        i += 1
        if i > n * 4:
            break
    return items


def _mcq(concept, terms, chapter, difficulty, bloom):
    correct = _short_fact(concept)
    options = [correct]
    for d in _distractors(concept, terms):
        if d not in options:
            options.append(d)
        if len(options) == 4:
            break
    while len(options) < 4:
        options.append(f"This is not stated in Chapter {chapter.number} of the approved textbook.")
    random.shuffle(options)
    stem = _mcq_stem(concept, difficulty)
    return {
        "qtype": "mcq",
        "stem": stem,
        "options": options,
        "correct_answer": correct,
        "explanation": concept.explanation,
        "difficulty": concept.difficulty or difficulty,
        "bloom": bloom,
        "marks": 1,
        "concept": concept.name,
        "source_ref": concept.source_ref,
        "source_excerpt": concept.source_excerpt,
    }


def _tf(concept, terms, chapter, difficulty, bloom):
    true_stmt = f"{concept.name}: {concept.explanation.split('.')[0]}."
    false_stmt = f"{concept.name} is unrelated to {chapter.title} and is not required in Grade 7 Science."
    use_true = random.random() > 0.4
    stem = true_stmt if use_true else false_stmt
    return {
        "qtype": "tf",
        "stem": stem,
        "options": ["True", "False"],
        "correct_answer": "True" if use_true else "False",
        "explanation": concept.explanation,
        "difficulty": difficulty,
        "bloom": "Understand",
        "marks": 1,
        "concept": concept.name,
        "source_ref": concept.source_ref,
        "source_excerpt": concept.source_excerpt,
    }


def _fib(concept, terms, chapter, difficulty, bloom):
    name = concept.name
    stem = f"According to the approved Grade 7 textbook, ________ is described as follows: {concept.simple_explanation}"
    return {
        "qtype": "fib",
        "stem": stem,
        "options": [],
        "correct_answer": name,
        "explanation": concept.explanation,
        "difficulty": "easy",
        "bloom": "Remember",
        "marks": 1,
        "concept": concept.name,
        "source_ref": concept.source_ref,
        "source_excerpt": concept.source_excerpt,
    }


def _short(concept, terms, chapter, difficulty, bloom):
    return {
        "qtype": "short",
        "stem": f"In your own words, explain {concept.name.lower()} as given in the textbook. Give one example.",
        "options": [],
        "correct_answer": f"{concept.explanation} Example: {concept.example}",
        "explanation": concept.simple_explanation,
        "difficulty": difficulty,
        "bloom": "Understand",
        "marks": 3,
        "concept": concept.name,
        "source_ref": concept.source_ref,
        "source_excerpt": concept.source_excerpt,
    }


def _long(concept, terms, chapter, difficulty, bloom):
    return {
        "qtype": "long",
        "stem": (
            f"Write a structured answer on {concept.name} with reference to Chapter {chapter.number} "
            f"({chapter.title}). Include definition, process or structure, and importance. "
            f"Use this example as a starting point: {concept.example}"
        ),
        "options": [],
        "correct_answer": f"{concept.explanation} {concept.example}",
        "explanation": "Mark for definition, mechanism, and a curriculum-aligned example.",
        "difficulty": "hard" if difficulty == "hard" else "medium",
        "bloom": "Evaluate" if bloom in ("Evaluate", "Create") else "Analyze",
        "marks": 5,
        "concept": concept.name,
        "source_ref": concept.source_ref,
        "source_excerpt": concept.source_excerpt,
    }


def _conceptual(concept, terms, chapter, difficulty, bloom):
    return {
        "qtype": "conceptual",
        "stem": (
            f"A Grade 7 student in Punjab is confused about {concept.name}. "
            f"Using only the textbook idea, help the student apply it: {concept.example} "
            f"What would happen if the key condition in this concept were missing?"
        ),
        "options": [],
        "correct_answer": (
            f"If the key condition is missing, {concept.name} cannot occur as described. "
            f"{concept.explanation}"
        ),
        "explanation": concept.simple_explanation,
        "difficulty": "hard",
        "bloom": "Apply",
        "marks": 4,
        "concept": concept.name,
        "source_ref": concept.source_ref,
        "source_excerpt": concept.source_excerpt,
    }


def _mcq_stem(concept, difficulty):
    if difficulty == "easy":
        return f"Which of the following best describes {concept.name} in the Grade 7 Science textbook?"
    if difficulty == "hard":
        return (
            f"A student applies the idea of {concept.name} to this situation: {concept.example} "
            f"Which statement is correct?"
        )
    return f"According to the approved curriculum, {concept.name} is best defined as:"


def _short_fact(concept) -> str:
    sent = concept.explanation.split(".")[0].strip()
    if len(sent) > 140:
        sent = concept.simple_explanation.split(".")[0].strip()
    return sent[:180]


def _distractors(concept, terms):
    out = []
    key = concept.name.lower()
    for k, vals in DISTRACTOR_BANK.items():
        if k in key or k in (concept.explanation or "").lower():
            out.extend(vals)
    for t in terms:
        if t.term.lower() not in key:
            out.append(t.definition.split(".")[0][:160])
    others = [
        "A process that occurs only in animal cells",
        "A mineral absorbed only through the human lung",
        "A physical change of ice into water",
        "A vitamin produced in the human liver",
    ]
    out.extend(others)
    random.shuffle(out)
    return out


def _concepts(db, chapter_id, topic_id):
    if topic_id:
        rows = db.query(Concept).filter(Concept.topic_id == topic_id).all()
        if rows:
            return rows
    topic_ids = [t.id for t in db.query(Topic).filter(Topic.chapter_id == chapter_id).all()]
    return db.query(Concept).filter(Concept.topic_id.in_(topic_ids)).all() if topic_ids else []


def _slos(db, chapter_id, topic_id):
    if topic_id:
        rows = db.query(SLO).filter(SLO.topic_id == topic_id).all()
        if rows:
            return rows
    topic_ids = [t.id for t in db.query(Topic).filter(Topic.chapter_id == chapter_id).all()]
    return db.query(SLO).filter(SLO.topic_id.in_(topic_ids)).all() if topic_ids else []


def _match_concept(concepts, text):
    t = (text or "").lower()
    for c in concepts:
        if c.name.lower() in t:
            return c
    return concepts[0] if concepts else None


def _match_slo(slos, bloom):
    for s in slos:
        if s.bloom_level.lower() == (bloom or "").lower():
            return s
    return slos[0] if slos else None


def _marks(qtype, assessment_type):
    if assessment_type == "exam":
        return {"mcq": 1, "tf": 1, "fib": 1, "short": 3, "long": 8, "conceptual": 5}.get(qtype, 1)
    return {"mcq": 1, "tf": 1, "fib": 1, "short": 2, "long": 5, "conceptual": 3}.get(qtype, 1)


def _bloom_for(qtype, difficulty):
    if qtype in ("mcq", "tf", "fib") and difficulty == "easy":
        return "Remember"
    if qtype == "short":
        return "Understand"
    if qtype in ("conceptual",) or difficulty == "hard":
        return "Apply"
    if qtype == "long":
        return "Analyze"
    return "Understand"


def _default_title(assessment_type, chapter, topic, n):
    label = {
        "quiz": "Quiz",
        "homework": "Homework",
        "assignment": "Assignment",
        "exam": "Examination paper",
        "worksheet": "Practice worksheet",
        "chapter_test": "Chapter test",
        "practice": "Targeted practice",
    }.get(assessment_type, "Assessment")
    scope = f"Ch.{chapter.number} {chapter.title}"
    if topic:
        scope += f" — {topic.title}"
    return f"{label}: {scope} ({n} items)"


def learning_material(db: Session, chapter_id: int, topic_id: int | None = None, simple: bool = False):
    chapter = db.get(Chapter, chapter_id)
    topic = db.get(Topic, topic_id) if topic_id else None
    concepts = _concepts(db, chapter_id, topic_id)
    slos = _slos(db, chapter_id, topic_id)
    terms = db.query(Term).filter(Term.chapter_id == chapter_id).all()
    sources = retrieve(db, chapter.title + (f" {topic.title}" if topic else ""), chapter_id, topic_id, k=5)
    return {
        "chapter": {"id": chapter.id, "number": chapter.number, "title": chapter.title, "summary": chapter.summary, "difficulty": chapter.difficulty, "expected_level": chapter.expected_level, "pages": f"{chapter.page_start}–{chapter.page_end}"},
        "topic": {"id": topic.id, "title": topic.title, "summary": topic.summary} if topic else None,
        "slos": [{"id": s.id, "code": s.code, "statement": s.statement, "bloom": s.bloom_level} for s in slos],
        "concepts": [
            {
                "id": c.id,
                "name": c.name,
                "explanation": c.simple_explanation if simple else c.explanation,
                "simple_explanation": c.simple_explanation,
                "example": c.example,
                "difficulty": c.difficulty,
                "source_ref": c.source_ref,
                "source_excerpt": c.source_excerpt,
            }
            for c in concepts
        ],
        "terms": [{"term": t.term, "definition": t.definition, "source_ref": t.source_ref} for t in terms],
        "sources": sources,
        "grounded": True,
    }


def sanitize_age(text: str) -> str:
    banned = [r"\b(kill|suicide|weapon|hate)\b"]
    out = text or ""
    for p in banned:
        out = re.sub(p, "[removed]", out, flags=re.I)
    return out
