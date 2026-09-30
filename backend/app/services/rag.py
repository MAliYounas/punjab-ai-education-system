import math
import re
from collections import Counter
from sqlalchemy.orm import Session
from ..models import Book, Chapter, Chunk, Concept, SLO, Subtopic, Term, Topic


STOP = {
    "the", "a", "an", "and", "or", "of", "to", "in", "on", "for", "is", "are", "was",
    "were", "be", "by", "with", "that", "this", "from", "as", "it", "at", "which",
    "into", "their", "they", "can", "may", "also", "than", "then", "its",
}


def tokenize(text: str) -> list[str]:
    return [t for t in re.findall(r"[a-zA-Z0-9]+", (text or "").lower()) if t not in STOP and len(t) > 2]


def index_book(db: Session, book: Book):
    db.query(Chunk).filter(Chunk.book_id == book.id).delete()
    chapters = db.query(Chapter).filter(Chapter.book_id == book.id).all()
    for ch in chapters:
        pieces = [ch.summary]
        for term in db.query(Term).filter(Term.chapter_id == ch.id).all():
            pieces.append(f"{term.term}: {term.definition}")
        topics = db.query(Topic).filter(Topic.chapter_id == ch.id).all()
        for topic in topics:
            pieces.append(topic.summary)
            for st in db.query(Subtopic).filter(Subtopic.topic_id == topic.id).all():
                pieces.append(f"{st.title}. {st.content}")
            for c in db.query(Concept).filter(Concept.topic_id == topic.id).all():
                pieces.append(f"{c.name}. {c.explanation} {c.example} {c.source_excerpt}")
            for s in db.query(SLO).filter(SLO.topic_id == topic.id).all():
                pieces.append(f"{s.code}: {s.statement}")
            body = " ".join(p for p in pieces if p)
            for i, part in enumerate(_window(body, 500)):
                db.add(
                    Chunk(
                        book_id=book.id,
                        chapter_id=ch.id,
                        topic_id=topic.id,
                        text=part,
                        source_ref=f"Ch.{ch.number} · {topic.title}",
                        page=ch.page_start + i,
                    )
                )
            pieces = []
    db.flush()


def _window(text: str, size: int) -> list[str]:
    words = text.split()
    if not words:
        return []
    out = []
    for i in range(0, len(words), size):
        out.append(" ".join(words[i : i + size]))
    return out


def retrieve(db: Session, query: str, chapter_id: int | None = None, topic_id: int | None = None, k: int = 6):
    q = db.query(Chunk)
    if chapter_id:
        q = q.filter(Chunk.chapter_id == chapter_id)
    if topic_id:
        q = q.filter(Chunk.topic_id == topic_id)
    chunks = q.all()
    if not chunks:
        return []
    qtok = tokenize(query)
    qcount = Counter(qtok)
    scored = []
    for ch in chunks:
        dtok = tokenize(ch.text)
        if not dtok:
            continue
        dcount = Counter(dtok)
        score = _cosine(qcount, dcount) + 0.15 * _overlap(qtok, dtok)
        scored.append((score, ch))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [{"score": round(s, 4), "text": c.text, "source_ref": c.source_ref, "page": c.page, "chapter_id": c.chapter_id, "topic_id": c.topic_id, "id": c.id} for s, c in scored[:k] if s > 0]


def _overlap(qtok, dtok):
    qs, ds = set(qtok), set(dtok)
    if not qs:
        return 0
    return len(qs & ds) / len(qs)


def _cosine(a: Counter, b: Counter) -> float:
    keys = set(a) | set(b)
    if not keys:
        return 0.0
    dot = sum(a[k] * b[k] for k in keys)
    na = math.sqrt(sum(v * v for v in a.values())) or 1
    nb = math.sqrt(sum(v * v for v in b.values())) or 1
    return dot / (na * nb)


def search_curriculum(db: Session, query: str, limit: int = 12):
    hits = retrieve(db, query, k=limit)
    concepts = db.query(Concept).all()
    qtok = set(tokenize(query))
    extra = []
    for c in concepts:
        blob = f"{c.name} {c.explanation} {c.example}"
        sc = _overlap(list(qtok), tokenize(blob))
        if sc > 0.15:
            extra.append(
                {
                    "kind": "concept",
                    "score": round(sc, 4),
                    "name": c.name,
                    "text": c.explanation,
                    "source_ref": c.source_ref,
                    "id": c.id,
                }
            )
    extra.sort(key=lambda x: x["score"], reverse=True)
    return {"chunks": hits, "concepts": extra[:8], "query": query}
