from __future__ import annotations

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
    method: str = ""


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
    return {
        "status": "ok",
        "app": settings.app_name,
        "chunks": len(kb.chunks),
        "vector": kb.vector_status(),
        "ai_model_configured": bool(settings.openai_api_key),
    }


@app.get("/api/sources")
def sources() -> dict:
    return {"sources": [source.__dict__ for source in kb.list_sources()]}


@app.post("/api/reload")
def reload_knowledge_base() -> dict:
    # Production holatda buni admin login bilan himoyalash kerak.
    kb.reload()
    return {"status": "reloaded", "chunks": len(kb.chunks), "vector": kb.vector_status()}


@app.post("/api/ask", response_model=AskResponse)
def ask(payload: AskRequest) -> AskResponse:
    # Tayyor FAQ emas: har safar savol uchun bilim bazasidan mos hujjat bo'laklari olinadi,
    # keyin AI modeli aynan shu kontekst asosida javob yaratadi.
    relevant = kb.search(payload.question)
    answer = generate_answer(payload.question, relevant, payload.mode)
    citations = [
        Citation(
            title=r.chunk.meta.title,
            document_number=r.chunk.meta.document_number,
            date=r.chunk.meta.date,
            section=r.chunk.meta.section,
            url=r.chunk.meta.url,
            score=round(r.score, 4),
            method=r.method,
        )
        for r in relevant
    ]
    return AskResponse(answer=answer, citations=citations, found_sources=len(citations))
