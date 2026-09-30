from datetime import datetime, timedelta
import json
from sqlalchemy.orm import Session
from .auth import hash_password
from .models import (
    Approval, Assessment, Attempt, AttemptAnswer, AuditLog, Book, Chapter,
    Classroom, Concept, CurriculumVersion, District, Mastery, Question,
    Recommendation, SLO, School, Subtopic, Term, Topic, User,
)
from .seed_curriculum import CURRICULUM
from .services.rag import index_book


DEMO_USERS = [
    {
        "name": "Director Curriculum Wing",
        "username": "admin",
        "password": "admin123",
        "role": "admin",
        "grade": None,
    },
    {
        "name": "Ayesha Khan",
        "username": "teacher",
        "password": "teacher123",
        "role": "teacher",
        "grade": 7,
    },
    {
        "name": "Ahmed Ali",
        "username": "student",
        "password": "student123",
        "role": "student",
        "grade": 7,
    },
    {
        "name": "Sara Malik",
        "username": "student2",
        "password": "student123",
        "role": "student",
        "grade": 7,
    },
    {
        "name": "Director Monitoring & Evaluation",
        "username": "director",
        "password": "director123",
        "role": "management",
        "grade": None,
    },
]

DISTRICTS = [
    ("Lahore", "Lahore"),
    ("Faisalabad", "Faisalabad"),
    ("Multan", "Multan"),
    ("Rawalpindi", "Rawalpindi"),
    ("Bahawalpur", "Bahawalpur"),
]

SCHOOLS = [
    ("GGHS Model Town", "EMIS-LHR-101", "Lahore", "High"),
    ("GHS Shalimar", "EMIS-LHR-214", "Lahore", "High"),
    ("GGHS Peoples Colony", "EMIS-FSD-088", "Faisalabad", "High"),
    ("GHS Jhang Road", "EMIS-FSD-112", "Faisalabad", "High"),
    ("GGHS Shah Rukn-e-Alam", "EMIS-MUL-055", "Multan", "High"),
    ("GHS Bosan Road", "EMIS-MUL-073", "Multan", "High"),
    ("GGHS Satellite Town", "EMIS-RWP-041", "Rawalpindi", "High"),
    ("GHS Saddar", "EMIS-BWP-019", "Bahawalpur", "High"),
]


def audit(db: Session, user_id, action, entity="", entity_id="", details=""):
    db.add(
        AuditLog(
            user_id=user_id,
            action=action,
            entity=entity,
            entity_id=str(entity_id) if entity_id is not None else "",
            details=details,
        )
    )


def seed_all(db: Session):
    if db.query(User).first():
        return False
    _seed_geography(db)
    users = _seed_users(db)
    book = _seed_curriculum(db)
    index_book(db, book)
    _seed_published_quiz(db, users["teacher"], book, users["student"], users["student2"])
    audit(db, users["admin"].id, "system.seed", "curriculum", book.id, "Prototype database initialised")
    db.commit()
    return True


def _seed_geography(db: Session):
    by_name = {}
    for name, division in DISTRICTS:
        d = District(name=name, division=division)
        db.add(d)
        db.flush()
        by_name[name] = d
    for name, emis, dist, level in SCHOOLS:
        db.add(
            School(
                name=name,
                emis_code=emis,
                district_id=by_name[dist].id,
                level=level,
            )
        )
    db.flush()
    school = db.query(School).filter(School.emis_code == "EMIS-LHR-101").first()
    db.add(Classroom(name="Grade 7-A", grade=7, section="A", school_id=school.id))
    db.add(Classroom(name="Grade 7-B", grade=7, section="B", school_id=school.id))
    db.flush()


def _seed_users(db: Session):
    school = db.query(School).filter(School.emis_code == "EMIS-LHR-101").first()
    room = db.query(Classroom).filter(Classroom.name == "Grade 7-A").first()
    out = {}
    for row in DEMO_USERS:
        u = User(
            name=row["name"],
            username=row["username"],
            password_hash=hash_password(row["password"]),
            role=row["role"],
            grade=row["grade"],
            language="en",
            school_id=school.id if row["role"] in ("teacher", "student") else None,
            classroom_id=room.id if row["role"] == "student" else None,
        )
        db.add(u)
        db.flush()
        out[row["username"]] = u
        out[row["role"] if row["username"] in ("admin", "teacher", "director") else row["username"]] = u
    return out


def _seed_curriculum(db: Session) -> Book:
    meta = CURRICULUM["version"]
    version = CurriculumVersion(
        name=meta["name"],
        board=meta["board"],
        year=meta["year"],
        status=meta["status"],
        notes=meta["notes"],
    )
    db.add(version)
    db.flush()
    bmeta = CURRICULUM["book"]
    book = Book(
        version_id=version.id,
        grade=bmeta["grade"],
        subject=bmeta["subject"],
        title=bmeta["title"],
        language=bmeta["language"],
        source_file=bmeta["source_file"],
        publisher=bmeta["publisher"],
    )
    db.add(book)
    db.flush()
    for ch in CURRICULUM["chapters"]:
        chapter = Chapter(
            book_id=book.id,
            number=ch["number"],
            title=ch["title"],
            summary=ch["summary"],
            difficulty=ch["difficulty"],
            page_start=ch["page_start"],
            page_end=ch["page_end"],
            expected_level=ch["expected_level"],
        )
        db.add(chapter)
        db.flush()
        for t in ch["topics"]:
            topic = Topic(
                chapter_id=chapter.id,
                title=t["title"],
                order=t["order"],
                summary=t["summary"],
            )
            db.add(topic)
            db.flush()
            for st in t.get("subtopics", []):
                db.add(Subtopic(topic_id=topic.id, title=st["title"], content=st["content"]))
            for s in t.get("slos", []):
                db.add(SLO(topic_id=topic.id, code=s["code"], statement=s["statement"], bloom_level=s["bloom"]))
            for c in t.get("concepts", []):
                db.add(
                    Concept(
                        topic_id=topic.id,
                        name=c["name"],
                        explanation=c["explanation"],
                        simple_explanation=c["simple_explanation"],
                        example=c["example"],
                        difficulty=c["difficulty"],
                        source_ref=c["source_ref"],
                        source_excerpt=c["source_excerpt"],
                    )
                )
        for term in ch.get("terms", []):
            db.add(
                Term(
                    chapter_id=chapter.id,
                    term=term["term"],
                    definition=term["definition"],
                    source_ref=term["source_ref"],
                )
            )
    db.flush()
    return book


def _seed_published_quiz(db: Session, teacher: User, book: Book, student: User, student2: User):
    chapter = (
        db.query(Chapter)
        .filter(Chapter.book_id == book.id, Chapter.number == 2)
        .first()
    )
    topic = db.query(Topic).filter(Topic.chapter_id == chapter.id, Topic.order == 2).first()
    slos = db.query(SLO).filter(SLO.topic_id == topic.id).all()
    concepts = db.query(Concept).filter(Concept.topic_id == topic.id).all()
    by_name = {c.name: c for c in concepts}

    assessment = Assessment(
        title="Chapter 2 Diagnostic — Photosynthesis",
        type="quiz",
        chapter_id=chapter.id,
        topic_id=topic.id,
        difficulty="medium",
        created_by=teacher.id,
        status="published",
        grounded=True,
        total_marks=10,
    )
    db.add(assessment)
    db.flush()
    db.add(Approval(content_type="assessment", content_id=assessment.id, status="approved", reviewer_id=teacher.id, notes="Approved for class 7-A diagnostic."))

    bank = [
        {
            "qtype": "mcq",
            "stem": "Photosynthesis is the process by which green plants produce:",
            "options": ["Glucose and oxygen", "Protein and nitrogen", "Carbon dioxide and water", "Minerals and starch only"],
            "correct": "Glucose and oxygen",
            "explanation": "Green plants convert carbon dioxide and water into glucose and oxygen using sunlight and chlorophyll.",
            "bloom": "Remember",
            "concept": "Photosynthesis",
            "slo": 0,
            "excerpt": "Photosynthesis is the process by which green plants prepare glucose from carbon dioxide and water",
        },
        {
            "qtype": "mcq",
            "stem": "Which pigment captures light energy for photosynthesis?",
            "options": ["Haemoglobin", "Chlorophyll", "Melanin", "Carotene only in roots"],
            "correct": "Chlorophyll",
            "explanation": "Chlorophyll in chloroplasts absorbs light energy. Haemoglobin is in blood, not leaves.",
            "bloom": "Remember",
            "concept": "Chlorophyll and chloroplast",
            "slo": 1,
            "excerpt": "Chlorophyll is the green pigment that absorbs light energy.",
        },
        {
            "qtype": "mcq",
            "stem": "Carbon dioxide enters the leaf mainly through:",
            "options": ["Xylem vessels", "Root hairs only", "Stomata", "Phloem sieve tubes"],
            "correct": "Stomata",
            "explanation": "Stomata are pores for gas exchange. Xylem carries water; phloem carries food.",
            "bloom": "Understand",
            "concept": "Stomata",
            "slo": 1,
            "excerpt": "Carbon dioxide enters leaves through stomata.",
        },
        {
            "qtype": "mcq",
            "stem": "The chemical equation of photosynthesis is:",
            "options": [
                "6CO2 + 6H2O → C6H12O6 + 6O2",
                "C6H12O6 + 6O2 → 6CO2 + 6H2O",
                "NaCl + H2O → NaOH + HCl",
                "N2 + 3H2 → 2NH3",
            ],
            "correct": "6CO2 + 6H2O → C6H12O6 + 6O2",
            "explanation": "Photosynthesis builds glucose and oxygen. The reverse-looking equation is respiration.",
            "bloom": "Remember",
            "concept": "Photosynthesis equation",
            "slo": 0,
            "excerpt": "Chemical equation: 6CO2 + 6H2O → C6H12O6 + 6O2.",
        },
        {
            "qtype": "tf",
            "stem": "A plant kept in continuous darkness can still produce starch in its leaves.",
            "options": ["True", "False"],
            "correct": "False",
            "explanation": "Light is required. In darkness light is a limiting factor, so starch is not formed.",
            "bloom": "Apply",
            "concept": "Photosynthesis",
            "slo": 2,
            "excerpt": "in the presence of sunlight and chlorophyll",
        },
        {
            "qtype": "tf",
            "stem": "Heterotrophs ultimately depend on autotrophs for food.",
            "options": ["True", "False"],
            "correct": "True",
            "explanation": "Animals cannot make food; energy enters ecosystems through autotrophs.",
            "bloom": "Understand",
            "concept": "Photosynthesis",
            "slo": 0,
            "excerpt": "Heterotrophs cannot make food and depend on autotrophs.",
        },
        {
            "qtype": "fib",
            "stem": "The organelle in which photosynthesis takes place is the ________.",
            "options": [],
            "correct": "chloroplast",
            "explanation": "Chloroplasts contain chlorophyll and are the site of photosynthesis.",
            "bloom": "Remember",
            "concept": "Chlorophyll and chloroplast",
            "slo": 1,
            "excerpt": "The main site is the chloroplast in mesophyll cells of leaves.",
        },
        {
            "qtype": "short",
            "stem": "State two raw materials of photosynthesis and how each enters the leaf or plant.",
            "options": [],
            "correct": "Carbon dioxide enters through stomata; water is absorbed by roots and travels in xylem to the leaf.",
            "explanation": "Both raw materials plus light and chlorophyll are required.",
            "bloom": "Understand",
            "concept": "Photosynthesis",
            "slo": 1,
            "excerpt": "Carbon dioxide enters leaves through stomata. Water is absorbed by roots",
        },
        {
            "qtype": "mcq",
            "stem": "Which of the following is the best explanation of why a yellow patch on a variegated leaf does not test positive for starch?",
            "options": [
                "Yellow patches lack chlorophyll so they cannot photosynthesise",
                "Yellow patches have too many stomata",
                "Yellow patches store extra protein instead of starch",
                "Yellow patches absorb only water, not carbon dioxide",
            ],
            "correct": "Yellow patches lack chlorophyll so they cannot photosynthesise",
            "explanation": "Without chlorophyll, light energy cannot be captured, so glucose/starch is not made.",
            "bloom": "Analyze",
            "concept": "Chlorophyll and chloroplast",
            "slo": 2,
            "excerpt": "Without chlorophyll, light energy cannot be captured for photosynthesis.",
        },
        {
            "qtype": "conceptual",
            "stem": "A farmer in Faisalabad notices slower crop growth during a week of heavy cloud cover. Using the idea of limiting factors, explain why photosynthesis may have slowed.",
            "options": [],
            "correct": "Light intensity is a limiting factor. On cloudy days less light reaches chlorophyll, so the rate of photosynthesis falls and less glucose is produced for growth.",
            "explanation": "The assignment wants application, not recall of the definition alone.",
            "bloom": "Apply",
            "concept": "Photosynthesis",
            "slo": 2,
            "excerpt": "The rate of photosynthesis increases with light intensity up to a point",
        },
    ]

    for i, q in enumerate(bank, start=1):
        concept = by_name.get(q["concept"]) or concepts[0]
        slo = slos[min(q["slo"], len(slos) - 1)]
        db.add(
            Question(
                assessment_id=assessment.id,
                qtype=q["qtype"],
                stem=q["stem"],
                options_json=json.dumps(q["options"]),
                correct_answer=q["correct"],
                explanation=q["explanation"],
                difficulty="medium" if i < 9 else "hard",
                bloom=q["bloom"],
                marks=1,
                slo_id=slo.id,
                topic_id=topic.id,
                concept_id=concept.id,
                source_ref=concept.source_ref,
                source_excerpt=q["excerpt"],
            )
        )
    db.flush()

    questions = db.query(Question).filter(Question.assessment_id == assessment.id).order_by(Question.id).all()

    # Ahmed: weaker on application / stomata / limiting factors — supports the demo narrative
    ahmed_answers = {
        0: ("Glucose and oxygen", True),
        1: ("Chlorophyll", True),
        2: ("Xylem vessels", False),
        3: ("6CO2 + 6H2O → C6H12O6 + 6O2", True),
        4: ("True", False),
        5: ("True", True),
        6: ("chloroplast", True),
        7: ("CO2 and water", False),
        8: ("Yellow patches have too many stomata", False),
        9: ("The soil was dry", False),
    }
    _store_attempt(db, student, assessment, questions, ahmed_answers, days_ago=3)

    sara_answers = {i: (questions[i].correct_answer, True) for i in range(10)}
    _store_attempt(db, student2, assessment, questions, sara_answers, days_ago=3)

    db.add(
        Recommendation(
            student_id=student.id,
            text="Ahmed understands the definition of photosynthesis and can recall the equation, but is weak in applying the idea of limiting factors and in explaining how raw materials enter the leaf. Recommend a simpler explanation of stomata and xylem, followed by five application-level questions on darkness, cloud cover and variegated leaves.",
            activities_json=json.dumps(
                [
                    "Revise concept: Stomata (simple explanation + example)",
                    "Revise concept: Limiting factors of photosynthesis",
                    "Complete 5 application MCQs from Chapter 2",
                    "Reassess with a 6-item targeted quiz",
                ]
            ),
        )
    )


def _store_attempt(db, student, assessment, questions, answers, days_ago=0):
    score = sum(1 for _, ok in answers.values() if ok)
    max_score = len(questions)
    percent = 100.0 * score / max_score if max_score else 0
    started = datetime.utcnow() - timedelta(days=days_ago, minutes=20)
    attempt = Attempt(
        student_id=student.id,
        assessment_id=assessment.id,
        started_at=started,
        completed_at=started + timedelta(minutes=18),
        score=score,
        max_score=max_score,
        percent=percent,
    )
    db.add(attempt)
    db.flush()
    for idx, q in enumerate(questions):
        ans, ok = answers[idx]
        db.add(
            AttemptAnswer(
                attempt_id=attempt.id,
                question_id=q.id,
                answer=ans,
                is_correct=ok,
                marks_awarded=1 if ok else 0,
            )
        )
        _bump_mastery(db, student.id, q, 1.0 if ok else 0.0)
    return attempt


def _bump_mastery(db, student_id, question, value):
    for field, fid in (("slo_id", question.slo_id), ("topic_id", question.topic_id), ("concept_id", question.concept_id)):
        if not fid:
            continue
        row = (
            db.query(Mastery)
            .filter(Mastery.student_id == student_id, getattr(Mastery, field) == fid)
            .first()
        )
        if not row:
            row = Mastery(student_id=student_id, **{field: fid}, score=value, attempts_count=1)
            db.add(row)
        else:
            n = row.attempts_count + 1
            row.score = (row.score * row.attempts_count + value) / n
            row.attempts_count = n
            row.last_updated = datetime.utcnow()
