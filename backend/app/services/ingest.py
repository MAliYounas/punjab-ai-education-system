from sqlalchemy.orm import Session
from ..models import Book, Chapter, Chunk, Concept, CurriculumVersion, SLO, Subtopic, Term, Topic, User
from .parser import extract_structure, parse_upload, split_paragraphs
from .rag import index_book
from . import ai_client


def ingest_document(db: Session, user: User, filepath: str, filename: str, grade: int, subject: str, title: str | None):
    text = parse_upload(filepath)
    if len(text.strip()) < 40:
        raise ValueError("Could not extract enough text. Try a text, DOCX or text-based PDF.")

    structure = extract_structure(text, fallback_title=title or filename)
    if ai_client.llm_available():
        enhanced = _llm_structure(text[:12000], grade, subject)
        if enhanced:
            structure = enhanced

    version = (
        db.query(CurriculumVersion)
        .filter(CurriculumVersion.status == "approved")
        .order_by(CurriculumVersion.id.desc())
        .first()
    )
    if not version:
        version = CurriculumVersion(name="Uploaded corpus", board="PCTB", year="2024", status="approved")
        db.add(version)
        db.flush()

    book = Book(
        version_id=version.id,
        grade=grade,
        subject=subject,
        title=title or filename,
        language="en",
        source_file=filename,
        publisher="Uploaded by school / teacher",
    )
    db.add(book)
    db.flush()

    for ch in structure:
        chapter = Chapter(
            book_id=book.id,
            number=int(ch.get("number") or 1),
            title=ch.get("title") or f"Chapter {ch.get('number')}",
            summary=(ch.get("summary") or "")[:2000] or _summarise_topics(ch.get("topics") or []),
            difficulty=ch.get("difficulty") or "medium",
            page_start=ch.get("page_start") or 1,
            page_end=ch.get("page_end") or 1,
            expected_level=f"Grade {grade} / Middle",
        )
        db.add(chapter)
        db.flush()
        for i, t in enumerate(ch.get("topics") or [], start=1):
            body = t.get("content") or t.get("summary") or ""
            topic = Topic(chapter_id=chapter.id, title=t.get("title") or f"Topic {i}", order=i, summary=body[:400])
            db.add(topic)
            db.flush()
            if body:
                db.add(Subtopic(topic_id=topic.id, title=t.get("title") or "Content", content=body[:8000]))
            for s in t.get("slos") or _infer_slos(body, grade, i):
                db.add(
                    SLO(
                        topic_id=topic.id,
                        code=s.get("code") or f"SLO-{grade}-U-{chapter.number}.{i}",
                        statement=s.get("statement") or s.get("text") or "",
                        bloom_level=s.get("bloom") or "Understand",
                    )
                )
            for c in t.get("concepts") or _infer_concepts(body, chapter.number):
                db.add(
                    Concept(
                        topic_id=topic.id,
                        name=c.get("name") or "Concept",
                        explanation=c.get("explanation") or body[:500],
                        simple_explanation=c.get("simple") or c.get("explanation") or body[:240],
                        example=c.get("example") or "",
                        difficulty=c.get("difficulty") or "medium",
                        source_ref=c.get("source_ref") or f"Ch.{chapter.number} · {topic.title}",
                        source_excerpt=(c.get("excerpt") or body[:280]),
                    )
                )
        for term in ch.get("terms") or []:
            db.add(
                Term(
                    chapter_id=chapter.id,
                    term=term.get("term") or term.get("name"),
                    definition=term.get("definition") or "",
                    source_ref=f"Ch.{chapter.number}",
                )
            )
        for para in split_paragraphs(" ".join(t.get("content") or "" for t in ch.get("topics") or [])):
            db.add(
                Chunk(
                    book_id=book.id,
                    chapter_id=chapter.id,
                    text=para,
                    source_ref=f"Ch.{chapter.number} · uploaded",
                    page=chapter.page_start,
                )
            )
    db.flush()
    index_book(db, book)
    return book


def _summarise_topics(topics):
    titles = [t.get("title") for t in topics if t.get("title")]
    return "Topics: " + ", ".join(titles[:8]) if titles else "Extracted from uploaded curriculum document."


def _infer_slos(body: str, grade: int, i: int):
    first = (body or "Understand the uploaded topic.").split(".")[0][:200]
    return [
        {"code": f"SLO-{grade}-U-{i}.1", "statement": f"Describe: {first}.", "bloom": "Understand"},
        {"code": f"SLO-{grade}-U-{i}.2", "statement": f"Apply ideas from this section to a simple example.", "bloom": "Apply"},
    ]


def _infer_concepts(body: str, chapter_n: int):
    sentences = [s.strip() for s in (body or "").split(".") if len(s.strip()) > 40][:3]
    out = []
    for i, s in enumerate(sentences, start=1):
        words = s.split()
        name = " ".join(words[:6])
        out.append(
            {
                "name": name[:80],
                "explanation": s[:500],
                "simple": s[:180],
                "example": "",
                "source_ref": f"Ch.{chapter_n}",
                "excerpt": s[:240],
            }
        )
    if not out:
        out.append(
            {
                "name": "Uploaded concept",
                "explanation": (body or "See source document.")[:500],
                "simple": (body or "")[:180],
                "source_ref": f"Ch.{chapter_n}",
                "excerpt": (body or "")[:240],
            }
        )
    return out


def _llm_structure(text, grade, subject):
    prompt = (
        f"Structure this {subject} Grade {grade} curriculum into JSON: "
        '{"chapters":[{"number":1,"title":"","summary":"","difficulty":"medium","topics":'
        '[{"title":"","content":"","slos":[{"code":"","statement":"","bloom":"Understand"}],'
        '"concepts":[{"name":"","explanation":"","simple":"","example":"","difficulty":"medium","source_ref":"","excerpt":""}]}]}]}'
        " Bloom levels must be one of Remember, Understand, Apply, Analyze, Evaluate, Create. "
        "Use only information present in the document."
    )
    raw = ai_client.complete(prompt, text[:10000], json_mode=True)
    data = ai_client.parse_json(raw)
    if data and data.get("chapters"):
        return data["chapters"]
    return None
