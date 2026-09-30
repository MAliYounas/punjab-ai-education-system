from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from .config import FRONTEND_DIR, HAS_LLM
from .database import Base, SessionLocal, engine
from . import models  # noqa: F401
from .routers import analytics, assessments, auth, copilot, curriculum, ingest
from .seed import seed_all

app = FastAPI(
    title="Punjab Education Intelligence Platform",
    description="Curriculum → Knowledge → Learning → Assessment → Diagnosis → Improvement",
    version="0.9.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(curriculum.router)
app.include_router(ingest.router)
app.include_router(assessments.router)
app.include_router(copilot.router)
app.include_router(analytics.router)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_all(db)
    finally:
        db.close()


@app.get("/api/health")
def health():
    return {"ok": True, "llm": HAS_LLM, "name": "Punjab Education Intelligence Platform"}


@app.get("/")
def index():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/assets/{path:path}")
def assets(path: str):
    root = FRONTEND_DIR.resolve()
    target = (FRONTEND_DIR / path).resolve()
    if root not in target.parents and target != root:
        raise HTTPException(404)
    if not target.is_file():
        raise HTTPException(404)
    return FileResponse(target)
