from pathlib import Path
import re

from pypdf import PdfReader


def parse_upload(path: str) -> str:
    p = Path(path)
    suffix = p.suffix.lower()
    if suffix == ".pdf":
        return _pdf(p)
    if suffix in {".docx"}:
        return _docx(p)
    return p.read_text(encoding="utf-8", errors="ignore")


def _pdf(path: Path) -> str:
    reader = PdfReader(str(path))
    parts = []
    for i, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        parts.append(f"\n[Page {i}]\n{text}")
    return "\n".join(parts).strip()


def _docx(path: Path) -> str:
    from docx import Document

    doc = Document(str(path))
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())


def split_paragraphs(text: str) -> list[str]:
    chunks = [re.sub(r"\s+", " ", c).strip() for c in re.split(r"\n\s*\n", text) if c.strip()]
    out = []
    buf = ""
    for c in chunks:
        if len(buf) + len(c) < 700:
            buf = (buf + " " + c).strip()
        else:
            if buf:
                out.append(buf)
            buf = c
    if buf:
        out.append(buf)
    return out


CHAPTER_RE = re.compile(r"(?:chapter|باب)\s*(\d+)[:.\-–]?\s*(.+)", re.I)
TOPIC_RE = re.compile(r"^(?:topic|heading|unit)\s*\d*[:.\-–]?\s*(.+)", re.I)


def extract_structure(text: str, fallback_title="Uploaded curriculum"):
    """Heuristic structure from headings. Works without an external LLM."""
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    chapters = []
    current = None
    current_topic = None
    buffer = []

    def flush_topic():
        nonlocal current_topic, buffer
        if current is not None and (current_topic or buffer):
            title = current_topic or f"Section {len(current['topics']) + 1}"
            body = " ".join(buffer).strip()
            current["topics"].append({"title": title, "content": body})
        current_topic = None
        buffer = []

    def flush_chapter():
        nonlocal current
        flush_topic()
        if current and (current["topics"] or current["title"]):
            chapters.append(current)
        current = None

    for ln in lines:
        m = CHAPTER_RE.match(ln)
        if m:
            flush_chapter()
            current = {"number": int(m.group(1)), "title": m.group(2).strip()[:240], "topics": []}
            continue
        if re.match(r"^\d+\.\d+\s+\S+", ln) or TOPIC_RE.match(ln) or (ln.endswith(":") and len(ln) < 80):
            if current is None:
                current = {"number": len(chapters) + 1, "title": fallback_title, "topics": []}
            flush_topic()
            current_topic = ln.rstrip(":").strip()[:240]
            continue
        if current is None:
            current = {"number": 1, "title": fallback_title, "topics": []}
        buffer.append(ln)

    flush_chapter()
    if not chapters:
        chapters = [
            {
                "number": 1,
                "title": fallback_title,
                "topics": [{"title": "Full document", "content": text[:8000]}],
            }
        ]
    return chapters
