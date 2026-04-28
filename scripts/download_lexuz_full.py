from __future__ import annotations

import argparse
import datetime as dt
import re
import shutil
import sys
import time
from pathlib import Path
from typing import Iterable

import requests
import yaml
from bs4 import BeautifulSoup

PROJECT_ROOT = Path(__file__).resolve().parents[1]
KB_DIR = PROJECT_ROOT / "knowledge_base"
OUTPUT_DIR = KB_DIR / "lexuz_full"

SOURCES = [
    {
        "filename": "00-konstitutsiya.md",
        "title": "O'zbekiston Respublikasi Konstitutsiyasi",
        "document_number": "Konstitutsiya",
        "date": "30.04.2023",
        "url": "https://lex.uz/docs/6445145",
    },
    {
        "filename": "01-talim-togrisida-qonun.md",
        "title": "Ta'lim to'g'risida",
        "document_number": "O'RQ-637",
        "date": "23.09.2020",
        "url": "https://lex.uz/docs/5013007",
    },
    {
        "filename": "02-oliy-talim-nizomi-3807.md",
        "title": "Oliy ta'lim to'g'risidagi nizomni tasdiqlash haqida",
        "document_number": "3807-son",
        "date": "03.04.2026",
        "url": "https://lex.uz/uz/docs/8117474",
    },
    {
        "filename": "03-qabul-kochirish-tiklash-chetlashtirish-578.md",
        "title": "Oliy ta'lim tashkilotlariga o'qishga qabul qilish jarayonlarini tartibga soluvchi normativ-huquqiy hujjatlarni tasdiqlash to'g'risida",
        "document_number": "VMQ 578-son",
        "date": "13.09.2025",
        "url": "https://lex.uz/uz/docs/7726569",
    },
    {
        "filename": "04-baholash-tizimi-3069.md",
        "title": "Oliy ta'lim tashkilotlarida talabalar bilimini nazorat qilish va baholash tizimi to'g'risidagi nizomni tasdiqlash haqida",
        "document_number": "Ro'yxat raqami 3069",
        "date": "26.09.2018",
        "url": "https://lex.uz/uz/docs/3916793",
    },
    {
        "filename": "05-kredit-modul-tizimi-824.md",
        "title": "Oliy ta'lim muassasalarida ta'lim jarayonini tashkil etish bilan bog'liq tizimni takomillashtirish chora-tadbirlari to'g'risida",
        "document_number": "VMQ 824-son",
        "date": "31.12.2020",
        "url": "https://lex.uz/uz/docs/5193564",
    },
    {
        "filename": "06-stipendiya-59.md",
        "title": "Oliy ta'lim muassasalari talabalariga to'lanadigan stipendiyalar miqdorlarini belgilash hamda stipendiyalar tayinlash va to'lash tartibini takomillashtirish chora-tadbirlari to'g'risida",
        "document_number": "VMQ 59-son",
        "date": "31.01.2020",
        "url": "https://lex.uz/uz/docs/4725554",
    },
    {
        "filename": "07-akademik-tatil-344.md",
        "title": "O'zbekiston Respublikasi oliy ta'lim muassasalari talabalariga akademik ta'til berish to'g'risidagi nizomni tasdiqlash haqida",
        "document_number": "VMQ 344-son",
        "date": "03.06.2021",
        "url": "https://lex.uz/docs/5443081",
    },
    {
        "filename": "08-masofaviy-talim-559.md",
        "title": "Oliy ta'lim tashkilotlarida masofaviy ta'lim shaklini joriy etish chora-tadbirlari to'g'risida",
        "document_number": "VMQ 559-son",
        "date": "03.10.2022",
        "url": "https://lex.uz/uz/docs/6221502",
    },
    {
        "filename": "09-talabalar-turar-joyi-376.md",
        "title": "Oliy ta'lim muassasalari talabalarini turar joy bilan ta'minlash tizimini takomillashtirish chora-tadbirlari to'g'risida",
        "document_number": "VMQ 376-son",
        "date": "14.08.2023",
        "url": "https://lex.uz/uz/docs/6568679",
    },
    {
        "filename": "10-tolov-kontrakt-2431.md",
        "title": "Oliy va o'rta maxsus, professional ta'lim tashkilotlarida o'qitishning to'lov-kontrakt shakli va undan tushgan mablag'larni taqsimlash tartibi to'g'risidagi nizomni tasdiqlash haqida",
        "document_number": "Ro'yxat raqami 2431",
        "date": "26.02.2013",
        "url": "https://lex.uz/docs/2137212",
    },
    {
        "filename": "11-ttj-yashash-xarajatlarini-qoplash-32.md",
        "title": "Ayrim toifadagi talabalar TTJ yashash xarajatlarini qoplab berish tartibi to'g'risidagi nizomni tasdiqlash haqida",
        "document_number": "VMQ 32-son",
        "date": "28.01.2026",
        "url": "https://lex.uz/uz/docs/8022224",
    },
    {
        "filename": "12-magistratura-nizomi-36.md",
        "title": "Magistratura to'g'risidagi Nizomni tasdiqlash haqida",
        "document_number": "VMQ 36-son",
        "date": "02.03.2015",
        "url": "https://lex.uz/docs/2579469",
    },
    {
        "filename": "13-namdtu-tashkil-etish-pq-23.md",
        "title": "Namangan davlat texnika universitetini tashkil etish to'g'risida",
        "document_number": "PQ-23-son",
        "date": "24.01.2025",
        "url": "https://lex.uz/uz/docs/-7339049",
    },
]

NOISE_PATTERNS = [
    r"^Hammasi$", r"^Ҳаммаси$", r"^Кейинги таҳрирга ҳавола$", r"^Keyingi tahrirga havola$",
    r"^Oldingi tahrirga havola$", r"^Олдинги таҳрирга ҳавола$", r"^QTUK bo.yicha indekslash$",
    r"^ҚТУК бўйича индекслаш$", r"^QMQ bo.yicha indekslash$", r"^ҚМҚ бўйича индекслаш$",
    r"^O.zgartirishlar manbasi$", r"^Ўзгартиришлар манбаси$", r"^Rasmiy nashr manbasi$",
    r"^Расмий нашр манбаси$", r"^Ko.rinish$", r"^Кўриниш$", r"^A$", r"^Рус$", r"^Eng$",
    r"^Ўзб$", r"^O.?zb$", r"^ONLINE TRANSLATE$", r"^Telegram$", r"^Facebook$", r"^Twitter$",
    r"^Instagram$", r"^Ulashish$", r"^Улашиш$", r"^Image$", r"Hujjatga taklif yuborish",
    r"Audioni tinglash", r"Hujjat elementidan havola olish", r"^Asosiy rekvizitlar", r"^Асосий реквизитлар",
]
NOISE_RE = re.compile("|".join(f"(?:{p})" for p in NOISE_PATTERNS), re.IGNORECASE)
MULTISPACE_RE = re.compile(r"[ \t]+")


def slug_to_heading(line: str) -> str:
    line = line.strip()
    # Lex.uz matnidagi bob/modda/bandlarni Markdown sarlavhaga aylantiramiz.
    if re.search(r"(боб|bob)\.?$", line, flags=re.IGNORECASE) or re.match(r"^(I|V|X|L|C|[0-9]+)[\-\s]*(боб|bob)\b", line, flags=re.IGNORECASE):
        return f"\n## {line}\n"
    if re.match(r"^\d+\s*[-–.]?\s*(модда|modda)\b", line, flags=re.IGNORECASE):
        return f"\n### {line}\n"
    if re.match(r"^\d+\s*[-–.]", line):
        return f"\n### {line}\n"
    return line


def clean_lines(lines: Iterable[str]) -> list[str]:
    cleaned: list[str] = []
    seen_short_noise = 0
    for raw in lines:
        line = MULTISPACE_RE.sub(" ", raw.replace("\xa0", " ")).strip()
        if not line:
            continue
        if NOISE_RE.search(line):
            continue
        if len(line) <= 1:
            continue
        # Lex sahifalaridagi juda ko'p takrorlanuvchi UI satrlarini kamaytirish.
        if line in {"0", "1", "2", "3"}:
            continue
        if line.startswith("[") and len(line) < 180 and ("ОКОЗ" in line or "ТСЗ" in line):
            continue
        if line == "Joriy versiya" or line == "Kuchga kirish sanasi" or line == "Qo'shimcha axborot" or line == "Қўшимча ахборот":
            continue
        cleaned.append(slug_to_heading(line))
    return cleaned


def extract_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript", "svg", "form", "button", "input", "select", "textarea"]):
        tag.decompose()
    # Lex.uz odatda asosiy matnni body ichida beradi; UI shovqinini keyingi qadamda filtrlaymiz.
    text = soup.get_text("\n")
    lines = clean_lines(text.splitlines())
    # Ketma-ket bo'sh qatorlarni me'yorlaymiz.
    content = "\n".join(lines)
    content = re.sub(r"\n{3,}", "\n\n", content).strip()
    return content


def write_markdown(source: dict, content: str, out_path: Path) -> None:
    metadata = {
        "title": source["title"],
        "document_number": source["document_number"],
        "date": source["date"],
        "url": source["url"],
        "status": "amalda",
        "source": "lex.uz",
        "full_text": True,
        "imported_at": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    frontmatter = yaml.safe_dump(metadata, allow_unicode=True, sort_keys=False).strip()
    body = f"---\n{frontmatter}\n---\n\n# {source['title']}\n\nManba: {source['url']}\n\n{content}\n"
    out_path.write_text(body, encoding="utf-8")


def backup_existing_markdown(kb_dir: Path) -> Path | None:
    existing = [p for p in kb_dir.rglob("*.md") if "_backup" not in p.parts]
    if not existing:
        return None
    backup_dir = kb_dir / f"_backup_{dt.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    backup_dir.mkdir(parents=True, exist_ok=True)
    for path in existing:
        rel = path.relative_to(kb_dir)
        target = backup_dir / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(path), str(target))
    return backup_dir


def download_one(session: requests.Session, source: dict, timeout: int) -> str:
    resp = session.get(source["url"], timeout=timeout)
    resp.raise_for_status()
    if not resp.encoding or resp.encoding.lower() == "iso-8859-1":
        resp.encoding = "utf-8"
    text = extract_text(resp.text)
    if len(text) < 1000:
        raise RuntimeError(f"Matn juda qisqa chiqdi ({len(text)} belgi). Lex.uz sahifasi to'g'ri o'qilmadi: {source['url']}")
    return text


def main() -> int:
    parser = argparse.ArgumentParser(description="Lex.uz hujjatlarini to'liq .md faylga yuklash")
    parser.add_argument("--replace", action="store_true", help="Mavjud .md fayllarni backup qilib, to'liq Lex.uz bazasi bilan almashtiradi")
    parser.add_argument("--delay", type=float, default=1.0, help="Har bir so'rov orasidagi pauza, soniya")
    parser.add_argument("--timeout", type=int, default=60, help="HTTP timeout, soniya")
    args = parser.parse_args()

    KB_DIR.mkdir(parents=True, exist_ok=True)
    if args.replace:
        backup = backup_existing_markdown(KB_DIR)
        if backup:
            print(f"Eski .md fayllar backup qilindi: {backup}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) YordamchiAI/1.0",
        "Accept-Language": "uz,en;q=0.8,ru;q=0.7",
    })

    ok = 0
    failed: list[tuple[str, str]] = []
    for idx, source in enumerate(SOURCES, start=1):
        out_path = OUTPUT_DIR / source["filename"]
        print(f"[{idx}/{len(SOURCES)}] Yuklanmoqda: {source['title']}")
        try:
            content = download_one(session, source, args.timeout)
            write_markdown(source, content, out_path)
            print(f"  OK: {out_path} ({len(content):,} belgi)")
            ok += 1
        except Exception as exc:
            print(f"  XATO: {exc}", file=sys.stderr)
            failed.append((source["title"], str(exc)))
        time.sleep(args.delay)

    print("\nNatija:")
    print(f"  Muvaffaqiyatli: {ok}")
    print(f"  Xato: {len(failed)}")
    if failed:
        print("\nXato bo'lgan hujjatlar:")
        for title, error in failed:
            print(f"- {title}: {error}")
        return 1
    print("\nTayyor. Endi serverni qayta ishga tushiring yoki /api/reload chaqiring.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
