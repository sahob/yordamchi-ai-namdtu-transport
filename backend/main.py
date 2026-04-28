from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .ai_provider import generate_answer
from .config import get_settings, project_root
from .knowledge import KnowledgeBase

settings = get_settings()
kb = KnowledgeBase()

app = FastAPI(title=settings.app_name, version=settings.app_version)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

frontend_path = project_root() / "frontend"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")


class AskRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=2000)
    mode: str = Field(default="short", description="short | detailed | steps")


class Citation(BaseModel):
    title: str
    document_number: str = ""
    date: str = ""
    section: str = ""
    url: str = ""
    score: float


class AskResponse(BaseModel):
    answer: str
    citations: list[Citation]
    found_sources: int


@app.get("/")
def index() -> FileResponse:
    index_file = frontend_path / "index.html"
    if not index_file.exists():
        raise HTTPException(status_code=404, detail="Frontend topilmadi")
    return FileResponse(index_file)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "app": settings.app_name, "chunks": len(kb.chunks)}


@app.get("/api/sources")
def sources() -> dict:
    return {"sources": [source.__dict__ for source in kb.list_sources()]}


@app.post("/api/reload")
def reload_knowledge_base() -> dict:
    # MVP uchun oddiy endpoint. Production holatda buni admin auth bilan himoyalang.
    kb.reload()
    return {"status": "reloaded", "chunks": len(kb.chunks)}


@app.post("/api/ask", response_model=AskResponse)
def ask(payload: AskRequest) -> AskResponse:
    results = kb.search(payload.question)
    relevant = [r for r in results if r.score >= settings.min_relevance_score]
    answer = generate_answer(payload.question, relevant)
    citations = [
        Citation(
            title=r.chunk.meta.title,
            document_number=r.chunk.meta.document_number,
            date=r.chunk.meta.date,
            section=r.chunk.meta.section,
            url=r.chunk.meta.url,
            score=round(r.score, 4),
        )
        for r in relevant
    ]
    return AskResponse(answer=answer, citations=citations, found_sources=len(citations))
