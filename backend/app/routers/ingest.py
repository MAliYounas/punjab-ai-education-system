from pathlib import Path
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session
from ..auth import require_roles
from ..config import UPLOAD_DIR
from ..database import get_db
from ..models import Chapter, Topic, User
from ..seed import audit
from ..services.ingest import ingest_document

router = APIRouter(prefix="/api/ingest", tags=["ingest"])


@router.post("/upload")
async def upload(
    file: UploadFile = File(...),
    grade: int = Form(7),
    subject: str = Form("General Science"),
    title: str = Form(""),
    user: User = Depends(require_roles("admin", "teacher")),
    db: Session = Depends(get_db),
):
    allowed = {".pdf", ".docx", ".txt", ".md"}
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in allowed:
        raise HTTPException(400, "Upload PDF, DOCX or TXT")
    dest = UPLOAD_DIR / f"{user.id}_{file.filename}"
    data = await file.read()
    dest.write_bytes(data)
    try:
        book = ingest_document(db, user, str(dest), file.filename, grade, subject, title or None)
    except ValueError as e:
        raise HTTPException(400, str(e))
    audit(db, user.id, "curriculum.upload", "book", book.id, file.filename)
    db.commit()
    chapters = db.query(Chapter).filter(Chapter.book_id == book.id).count()
    topics = (
        db.query(Topic)
        .join(Chapter, Chapter.id == Topic.chapter_id)
        .filter(Chapter.book_id == book.id)
        .count()
    )
    return {
        "book_id": book.id,
        "title": book.title,
        "grade": book.grade,
        "subject": book.subject,
        "chapters": chapters,
        "topics": topics,
        "source_file": book.source_file,
        "message": "Document structured into the curriculum knowledge base with source traceability.",
    }
