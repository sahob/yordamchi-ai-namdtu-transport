from __future__ import annotations

import hashlib
import json
import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import yaml

from .config import get_settings, project_root
from .transliteration import normalize_for_search


@dataclass(slots=True)
class SourceMeta:
    title: str
    document_number: str = ""
    date: str = ""
    url: str = ""
    section: str = ""
    status: str = "amalda"


@dataclass(slots=True)
class Chunk:
    id: str
    text: str
    search_text: str
    meta: SourceMeta


@dataclass(slots=True)
class SearchResult:
    chunk: Chunk
    score: float
    method: str = "keyword"


FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)
HEADER_RE = re.compile(r"^(#{1,3})\s+(.+)$", re.MULTILINE)
TOKEN_RE = re.compile(r"[a-zа-яёғқўҳʼʻ0-9]{2,}", re.IGNORECASE)
STOPWORDS = {
    "uchun", "bilan", "boyicha", "bo'yicha", "bo‘yicha", "qanday", "nima", "qachon",
    "kerak", "mumkin", "haqida", "talaba", "talabalar", "men", "menga", "shu", "bu",
    "the", "and", "или", "это", "для", "олиш", "учун", "билан", "қандай", "нима",
    "қачон", "керак", "мумкин", "ҳақида", "талаба", "талабалар",
}


def tokenize(text: str) -> list[str]:
    normalized = normalize_for_search(text)
    tokens = [t.strip("ʼʻ'").lower() for t in TOKEN_RE.findall(normalized)]
    return [t for t in tokens if t and t not in STOPWORDS]


def parse_markdown_file(path: Path) -> tuple[SourceMeta, str]:
    raw = path.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(raw)
    metadata: dict = {}
    body = raw
    if match:
        metadata = yaml.safe_load(match.group(1)) or {}
        body = match.group(2)
    meta = SourceMeta(
        title=str(metadata.get("title") or path.stem),
        document_number=str(metadata.get("document_number") or ""),
        date=str(metadata.get("date") or ""),
        url=str(metadata.get("url") or ""),
        status=str(metadata.get("status") or "amalda"),
    )
    return meta, body.strip()


def _split_long_text(text: str, max_chars: int = 2200, overlap: int = 250) -> list[str]:
    """Uzoq bo'limlarni RAG uchun kichik bo'laklarga ajratadi."""
    text = text.strip()
    if len(text) <= max_chars:
        return [text]

    parts: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + max_chars, len(text))
        if end < len(text):
            # Gap yoki xatboshi chegarasiga yaqin joyda kesish.
            candidates = [text.rfind("\n\n", start, end), text.rfind(". ", start, end), text.rfind("; ", start, end)]
            cut = max(candidates)
            if cut > start + max_chars // 2:
                end = cut + 1
        parts.append(text[start:end].strip())
        if end >= len(text):
            break
        start = max(end - overlap, 0)
    return [p for p in parts if p]


def split_markdown_into_chunks(meta: SourceMeta, body: str, file_stem: str) -> list[Chunk]:
    sections: list[tuple[str, str]] = []
    matches = list(HEADER_RE.finditer(body))
    if not matches:
        sections.append(("Umumiy", body))
    else:
        for idx, match in enumerate(matches):
            title = match.group(2).strip()
            start = match.end()
            end = matches[idx + 1].start() if idx + 1 < len(matches) else len(body)
            content = body[start:end].strip()
            if content:
                sections.append((title, content))

    chunks: list[Chunk] = []
    chunk_no = 1
    for section, content in sections:
        for part_no, part in enumerate(_split_long_text(content), start=1):
            section_name = section if part_no == 1 else f"{section} — davom {part_no}"
            enriched_meta = SourceMeta(
                title=meta.title,
                document_number=meta.document_number,
                date=meta.date,
                url=meta.url,
                section=section_name,
                status=meta.status,
            )
            chunk_text = f"{section_name}\n{part}".strip()
            chunks.append(Chunk(
                id=f"{file_stem}-{chunk_no}",
                text=chunk_text,
                search_text=normalize_for_search(f"{meta.title}\n{section_name}\n{part}"),
                meta=enriched_meta,
            ))
            chunk_no += 1
    return chunks


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def _chunk_signature(chunks: list[Chunk], embedding_model: str) -> str:
    payload = "\n".join(f"{c.id}:{hashlib.sha256(c.search_text.encode('utf-8')).hexdigest()}" for c in chunks)
    return hashlib.sha256(f"{embedding_model}\n{payload}".encode("utf-8")).hexdigest()


class VectorIndex:
    def __init__(self, chunks: list[Chunk], allow_build: bool = False) -> None:
        self.settings = get_settings()
        self.chunks = chunks
        self.embeddings: list[list[float]] = []
        self.available = False
        self.error: str | None = None
        self._load_or_build(allow_build=allow_build)

    def _index_path(self) -> Path:
        path = Path(self.settings.vector_index_path)
        if not path.is_absolute():
            path = project_root() / path
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    def _load_or_build(self, allow_build: bool = False) -> None:
        if not self.settings.openai_api_key:
            self.error = "OPENAI_API_KEY topilmadi"
            return
        signature = _chunk_signature(self.chunks, self.settings.openai_embedding_model)
        path = self._index_path()
        if path.exists():
            try:
                cached = json.loads(path.read_text(encoding="utf-8"))
                if cached.get("signature") == signature and len(cached.get("embeddings", [])) == len(self.chunks):
                    self.embeddings = cached["embeddings"]
                    self.available = True
                    return
            except Exception:
                pass
        if allow_build:
            self._build(signature, path)
        else:
            self.available = False
            self.error = (
                "Vector indeks cache topilmadi yoki eskirgan. Server tez ishga tushishi uchun "
                "indeks avtomatik qurilmadi. scripts/build_vector_index.py ni lokalda ishga tushirib "
                ".cache/vector_index.json faylini GitHub'ga yuklang yoki USE_VECTOR_SEARCH=false qiling."
            )

    def _build(self, signature: str, path: Path) -> None:
        try:
            from openai import OpenAI

            client = OpenAI(api_key=self.settings.openai_api_key)
            texts = [c.search_text[:8000] for c in self.chunks]
            embeddings: list[list[float]] = []
            batch_size = 64
            for start in range(0, len(texts), batch_size):
                batch = texts[start:start + batch_size]
                response = client.embeddings.create(
                    model=self.settings.openai_embedding_model,
                    input=batch,
                )
                embeddings.extend([item.embedding for item in response.data])
            if len(embeddings) != len(self.chunks):
                raise RuntimeError("Embedding soni chunk soniga mos kelmadi")
            self.embeddings = embeddings
            self.available = True
            path.write_text(json.dumps({
                "signature": signature,
                "model": self.settings.openai_embedding_model,
                "embeddings": embeddings,
            }, ensure_ascii=False), encoding="utf-8")
        except Exception as exc:
            self.available = False
            self.error = str(exc)

    def search(self, query: str, limit: int) -> list[SearchResult]:
        if not self.available or not self.embeddings:
            return []
        try:
            from openai import OpenAI

            client = OpenAI(api_key=self.settings.openai_api_key)
            response = client.embeddings.create(
                model=self.settings.openai_embedding_model,
                input=normalize_for_search(query),
            )
            q_embedding = response.data[0].embedding
            scored = [
                SearchResult(chunk=chunk, score=_dot(q_embedding, embedding), method="vector")
                for chunk, embedding in zip(self.chunks, self.embeddings)
            ]
            scored.sort(key=lambda item: item.score, reverse=True)
            return [r for r in scored[:limit] if r.score >= self.settings.min_vector_score]
        except Exception as exc:
            self.error = str(exc)
            return []


class KnowledgeBase:
    def __init__(self) -> None:
        self.settings = get_settings()
        kb_path = Path(self.settings.knowledge_base_dir)
        if not kb_path.is_absolute():
            kb_path = project_root() / kb_path
        self.kb_path = kb_path
        self.chunks: list[Chunk] = []
        self.chunk_tokens: list[Counter[str]] = []
        self.doc_freq: Counter[str] = Counter()
        self.vector_index: VectorIndex | None = None
        self.reload()

    def reload(self) -> None:
        self.chunks = list(self._load_chunks())
        self.chunk_tokens = []
        self.doc_freq = Counter()
        for chunk in self.chunks:
            counts = Counter(tokenize(chunk.search_text))
            self.chunk_tokens.append(counts)
            self.doc_freq.update(counts.keys())
        self.vector_index = (
            VectorIndex(self.chunks, allow_build=self.settings.build_vector_index_on_startup)
            if self.settings.use_vector_search else None
        )

    def _load_chunks(self) -> Iterable[Chunk]:
        self.kb_path.mkdir(parents=True, exist_ok=True)
        # .md fayllarni rekursiv o'qiydi: knowledge_base/lexuz_full/*.md ham yuklanadi.
        # _backup_* papkalari indeksga kirmaydi.
        for path in sorted(self.kb_path.rglob("*.md")):
            if any(part.startswith("_backup") or part in {"old", "archive"} for part in path.parts):
                continue
            meta, body = parse_markdown_file(path)
            yield from split_markdown_into_chunks(meta, body, path.stem)

    def list_sources(self) -> list[SourceMeta]:
        seen: dict[str, SourceMeta] = {}
        for chunk in self.chunks:
            key = f"{chunk.meta.title}|{chunk.meta.document_number}|{chunk.meta.date}"
            if key not in seen:
                seen[key] = SourceMeta(
                    title=chunk.meta.title,
                    document_number=chunk.meta.document_number,
                    date=chunk.meta.date,
                    url=chunk.meta.url,
                    status=chunk.meta.status,
                )
        return list(seen.values())

    def _keyword_score(self, query_terms: Counter[str], chunk_terms: Counter[str]) -> float:
        if not query_terms or not chunk_terms:
            return 0.0
        total_docs = max(len(self.chunks), 1)
        score = 0.0
        for term, q_count in query_terms.items():
            tf = chunk_terms.get(term, 0)
            if tf <= 0:
                continue
            idf = math.log((1 + total_docs) / (1 + self.doc_freq.get(term, 0))) + 1
            score += (1 + math.log(tf)) * idf * min(q_count, 2)
        norm = math.sqrt(sum(v * v for v in chunk_terms.values())) or 1.0
        return score / norm

    def keyword_search(self, query: str, limit: int | None = None) -> list[SearchResult]:
        limit = limit or self.settings.max_context_chunks
        query_terms = Counter(tokenize(query))
        scored = [
            SearchResult(chunk=chunk, score=self._keyword_score(query_terms, terms), method="keyword")
            for chunk, terms in zip(self.chunks, self.chunk_tokens)
        ]
        scored.sort(key=lambda item: item.score, reverse=True)
        return [r for r in scored[:limit] if r.score >= self.settings.min_keyword_score]

    def search(self, query: str, limit: int | None = None) -> list[SearchResult]:
        """Ixtiyoriy savol uchun semantik + keyword RAG qidiruv."""
        limit = limit or self.settings.max_context_chunks
        combined: dict[str, SearchResult] = {}

        if self.vector_index and self.vector_index.available:
            for result in self.vector_index.search(query, limit=limit):
                combined[result.chunk.id] = result

        for result in self.keyword_search(query, limit=limit):
            existing = combined.get(result.chunk.id)
            if existing:
                # Hybrid qidiruv: vector natija ustiga keyword signalini ham qo'shamiz.
                existing.score = max(existing.score, result.score)
                existing.method = "hybrid"
            else:
                combined[result.chunk.id] = result

        results = list(combined.values())
        results.sort(key=lambda item: item.score, reverse=True)
        return results[:limit]

    def vector_status(self) -> dict:
        if not self.vector_index:
            return {"enabled": False, "available": False, "error": "Vector qidiruv o'chirilgan"}
        return {
            "enabled": True,
            "available": self.vector_index.available,
            "error": self.vector_index.error,
            "model": self.settings.openai_embedding_model,
        }
