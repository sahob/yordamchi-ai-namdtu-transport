from __future__ import annotations

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

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)
HEADER_RE = re.compile(r"^(#{1,3})\s+(.+)$", re.MULTILINE)
TOKEN_RE = re.compile(r"[a-zа-яёғқўҳʼʻ0-9]{2,}", re.IGNORECASE)
STOPWORDS = {"uchun","bilan","boyicha","bo‘yicha","qanday","nima","qachon","kerak","mumkin","haqida","talaba","talabalar","men","menga","shu","bu","олиш","учун","билан","қандай","нима","қачон","керак","мумкин","ҳақида"}

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
    for i, (section, content) in enumerate(sections, start=1):
        enriched_meta = SourceMeta(
            title=meta.title,
            document_number=meta.document_number,
            date=meta.date,
            url=meta.url,
            section=section,
            status=meta.status,
        )
        chunk_text = f"{section}\n{content}".strip()
        chunks.append(Chunk(
            id=f"{file_stem}-{i}",
            text=chunk_text,
            search_text=normalize_for_search(f"{meta.title}\n{section}\n{content}"),
            meta=enriched_meta,
        ))
    return chunks

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
        self.reload()

    def reload(self) -> None:
        self.chunks = list(self._load_chunks())
        self.chunk_tokens = []
        self.doc_freq = Counter()
        for chunk in self.chunks:
            counts = Counter(tokenize(chunk.search_text))
            self.chunk_tokens.append(counts)
            self.doc_freq.update(counts.keys())

    def _load_chunks(self) -> Iterable[Chunk]:
        self.kb_path.mkdir(parents=True, exist_ok=True)
        for path in sorted(self.kb_path.glob("*.md")):
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

    def _score(self, query_terms: Counter[str], chunk_terms: Counter[str]) -> float:
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

    def search(self, query: str, limit: int | None = None) -> list[SearchResult]:
        limit = limit or self.settings.max_context_chunks
        query_terms = Counter(tokenize(query))
        scored = [
            SearchResult(chunk=chunk, score=self._score(query_terms, terms))
            for chunk, terms in zip(self.chunks, self.chunk_tokens)
        ]
        scored.sort(key=lambda item: item.score, reverse=True)
        return [result for result in scored[:limit] if result.score > 0]
