from __future__ import annotations

from textwrap import dedent

from .config import get_settings
from .knowledge import SearchResult


def format_citation(result: SearchResult, index: int) -> str:
    meta = result.chunk.meta
    parts = [meta.title]
    if meta.document_number:
        parts.append(meta.document_number)
    if meta.date:
        parts.append(meta.date)
    if meta.section:
        parts.append(f"bo‘lim: {meta.section}")
    return f"[{index}] " + ", ".join(parts)


def build_context(results: list[SearchResult]) -> str:
    blocks: list[str] = []
    for i, result in enumerate(results, start=1):
        blocks.append(
            f"MANBA {i}: {format_citation(result, i)}\n"
            f"URL: {result.chunk.meta.url}\n"
            f"MATN:\n{result.chunk.text}"
        )
    return "\n\n---\n\n".join(blocks)


def fallback_answer(question: str, results: list[SearchResult]) -> str:
    if not results:
        return (
            "Bu savol bo‘yicha bilim bazasida yetarli normativ-huquqiy manba topilmadi. "
            "Iltimos, savolni aniqroq yozing yoki platforma administratori orqali tegishli hujjatni bazaga qo‘shing."
        )

    top = results[0]
    lines = [
        "Quyidagi javob bilim bazasida topilgan manbalarga tayangan holda tayyorlandi.",
        "",
        "Qisqa javob:",
        top.chunk.text.split("\n", 1)[-1].strip()[:900],
        "",
        "Manbalar:",
    ]
    for i, result in enumerate(results, start=1):
        meta = result.chunk.meta
        lines.append(f"{i}. {format_citation(result, i)}")
        if meta.url:
            lines.append(f"   Havola: {meta.url}")
    lines.append("")
    lines.append("Eslatma: yakuniy huquqiy qaror mas’ul bo‘lim yoki vakolatli xodim tomonidan qabul qilinadi.")
    return "\n".join(lines)


def generate_answer(question: str, results: list[SearchResult]) -> str:
    settings = get_settings()
    if not settings.openai_api_key:
        return fallback_answer(question, results)

    try:
        from openai import OpenAI

        client = OpenAI(api_key=settings.openai_api_key)
        context = build_context(results)
        system_prompt = dedent(
            """
            Siz “Yordamchi AI — NamDTU Transport fakulteti” platformasisiz.
            Faqat berilgan MANBA matnlariga tayanib javob bering.
            Talabaga tushunarli, qisqa va amaliy o‘zbek tilida javob yozing.
            Agar manbalarda yetarli asos bo‘lmasa, buni ochiq ayting.
            Har bir muhim xulosadan keyin [1], [2] kabi manba raqamini ko‘rsating.
            Yuridik qaror chiqarmang; yakuniy qaror mas’ul bo‘lim tomonidan qabul qilinishini eslating.
            """
        ).strip()
        user_prompt = f"Savol: {question}\n\n{context}"
        response = client.chat.completions.create(
            model=settings.openai_model,
            temperature=0.2,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response.choices[0].message.content or fallback_answer(question, results)
    except Exception as exc:  # pragma: no cover - provider failures should not break MVP
        return fallback_answer(question, results) + f"\n\nTexnik eslatma: AI provayderi vaqtincha ishlamadi ({exc})."
