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
        parts.append(f"bo'lim: {meta.section}")
    return f"[{index}] " + ", ".join(parts)


def build_context(results: list[SearchResult]) -> str:
    blocks: list[str] = []
    for i, result in enumerate(results, start=1):
        blocks.append(
            f"MANBA {i}: {format_citation(result, i)}\n"
            f"URL: {result.chunk.meta.url}\n"
            f"QIDIRUV USULI: {result.method}, SCORE: {result.score:.4f}\n"
            f"MATN:\n{result.chunk.text}"
        )
    return "\n\n---\n\n".join(blocks)


def no_ai_answer(results: list[SearchResult]) -> str:
    if not results:
        return (
            "Bu savol bo'yicha bilim bazasida mos normativ-huquqiy manba topilmadi. "
            "Hujjat bazaga qo'shilganini va .md fayl matnida shu mavzuga oid bandlar borligini tekshiring."
        )
    return (
        "AI modeli ulanmagan. Ixtiyoriy savolga hujjatlar asosida javob yaratish uchun .env fayliga "
        "OPENAI_API_KEY ni qo'shing va serverni qayta ishga tushiring.\n\n"
        "Hozir tizim mos manbalarni topdi, lekin AI javob yaratmayapti."
    )


def generate_answer(question: str, results: list[SearchResult], mode: str = "short") -> str:
    settings = get_settings()
    if not results:
        return (
            "Bu savol bo'yicha bilim bazasida yetarli normativ-huquqiy manba topilmadi. "
            "Savolni aniqroq yozing yoki tegishli Lex.uz/NamDTU hujjatini knowledge_base papkasiga qo'shing."
        )
    if not settings.openai_api_key:
        return no_ai_answer(results)

    try:
        from openai import OpenAI

        client = OpenAI(api_key=settings.openai_api_key)
        context = build_context(results)
        style = {
            "short": "Javob qisqa, aniq va 5-8 jumladan oshmasin.",
            "detailed": "Javob batafsil bo'lsin: asos, tartib, istisno va eslatmalarni ajrating.",
            "steps": "Javob qadam-baqadam yo'riqnoma shaklida bo'lsin.",
        }.get(mode, "Javob qisqa va aniq bo'lsin.")

        instructions = dedent(
            f"""
            Siz “Yordamchi AI — NamDTU Transport fakulteti” platformasisiz.
            Sizning vazifangiz — talabaning ixtiyoriy savoliga FAQ yoki tayyor javobdan emas,
            faqat quyida berilgan MANBA matnlaridan foydalanib javob yaratish.

            QOIDALAR:
            1) Faqat MANBA matnlaridagi ma'lumotlarga tayaning.
            2) Manbada yo'q ma'lumotni o'ylab topmang.
            3) Har bir muhim xulosadan keyin [1], [2] kabi manba raqamini qo'ying.
            4) Agar manba yetarli bo'lmasa: "Bu savol bo'yicha berilgan manbalarda yetarli asos topilmadi" deb yozing.
            5) Talaba tushunadigan sodda o'zbek tilida javob bering.
            6) Yuridik qaror chiqarmang; yakuniy qaror mas'ul bo'lim tomonidan qabul qilinishini eslating.
            7) {style}
            """
        ).strip()

        input_text = f"Savol: {question}\n\nMANBALAR:\n{context}"
        response = client.responses.create(
            model=settings.openai_model,
            instructions=instructions,
            input=input_text,
            temperature=0.1,
        )
        return response.output_text.strip()
    except Exception as exc:  # pragma: no cover
        return (
            "AI javob yaratishda texnik xatolik yuz berdi. .env faylidagi OPENAI_API_KEY, OPENAI_MODEL "
            f"va internet aloqasini tekshiring. Xatolik: {exc}"
        )
