from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from ..auth import get_current_user
from ..database import get_db
from ..models import Book, Chapter, Concept, CurriculumVersion, SLO, Subtopic, Term, Topic, User
from ..services.rag import search_curriculum

router = APIRouter(prefix="/api/curriculum", tags=["curriculum"])


@router.get("/tree")
def tree(_: User = Depends(get_current_user), db: Session = Depends(get_db)):
    versions = db.query(CurriculumVersion).order_by(CurriculumVersion.id.desc()).all()
    out = []
    for v in versions:
        books = db.query(Book).filter(Book.version_id == v.id).all()
        bout = []
        for b in books:
            chapters = db.query(Chapter).filter(Chapter.book_id == b.id).order_by(Chapter.number).all()
            chout = []
            for ch in chapters:
                topics = db.query(Topic).filter(Topic.chapter_id == ch.id).order_by(Topic.order).all()
                tout = []
                for t in topics:
                    slos = db.query(SLO).filter(SLO.topic_id == t.id).all()
                    concepts = db.query(Concept).filter(Concept.topic_id == t.id).all()
                    subs = db.query(Subtopic).filter(Subtopic.topic_id == t.id).all()
                    tout.append(
                        {
                            "id": t.id,
                            "title": t.title,
                            "order": t.order,
                            "summary": t.summary,
                            "subtopics": [{"id": s.id, "title": s.title, "content": s.content} for s in subs],
                            "slos": [{"id": s.id, "code": s.code, "statement": s.statement, "bloom": s.bloom_level} for s in slos],
                            "concepts": [
                                {
                                    "id": c.id,
                                    "name": c.name,
                                    "explanation": c.explanation,
                                    "simple_explanation": c.simple_explanation,
                                    "example": c.example,
                                    "difficulty": c.difficulty,
                                    "source_ref": c.source_ref,
                                    "source_excerpt": c.source_excerpt,
                                }
                                for c in concepts
                            ],
                        }
                    )
                terms = db.query(Term).filter(Term.chapter_id == ch.id).all()
                chout.append(
                    {
                        "id": ch.id,
                        "number": ch.number,
                        "title": ch.title,
                        "summary": ch.summary,
                        "difficulty": ch.difficulty,
                        "expected_level": ch.expected_level,
                        "pages": f"{ch.page_start}–{ch.page_end}",
                        "topics": tout,
                        "terms": [{"term": x.term, "definition": x.definition, "source_ref": x.source_ref} for x in terms],
                    }
                )
            bout.append(
                {
                    "id": b.id,
                    "grade": b.grade,
                    "subject": b.subject,
                    "title": b.title,
                    "language": b.language,
                    "source_file": b.source_file,
                    "publisher": b.publisher,
                    "chapters": chout,
                }
            )
        out.append(
            {
                "id": v.id,
                "name": v.name,
                "board": v.board,
                "year": v.year,
                "status": v.status,
                "notes": v.notes,
                "books": bout,
            }
        )
    return {"versions": out}


@router.get("/search")
def search(q: str = Query(...), _: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return search_curriculum(db, q)


@router.get("/stats")
def stats(_: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return {
        "versions": db.query(CurriculumVersion).count(),
        "books": db.query(Book).count(),
        "chapters": db.query(Chapter).count(),
        "topics": db.query(Topic).count(),
        "slos": db.query(SLO).count(),
        "concepts": db.query(Concept).count(),
        "terms": db.query(Term).count(),
    }
