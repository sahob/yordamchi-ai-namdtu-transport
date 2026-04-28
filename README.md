# Yordamchi AI — NamDTU Transport fakulteti

**Yordamchi AI — NamDTU Transport fakulteti** — talabalar uchun normativ-huquqiy hujjatlar, ichki tartib-qoidalar va o‘quv jarayoniga oid savollarga tezkor, manbali va tushunarli javob beruvchi MVP platforma.

Platforma RAG yondashuvida ishlaydi: talaba savoli bo‘yicha avval bilim bazasidan mos hujjat bo‘laklari topiladi, keyin javob aynan shu manbalarga tayangan holda shakllantiriladi.

## Imkoniyatlar

- Uzbek Latin va Uzbek Cyrillic savollarini qidirish uchun minimal transliteratsiya.
- Lex.uz va universitet ichki hujjatlari uchun `knowledge_base/*.md` bilim bazasi.
- Javob bilan birga manba, hujjat raqami, sana, bo‘lim va havola.
- OpenAI API kaliti bo‘lmasa ham ishlaydigan retrieval fallback.
- OpenAI API kaliti bo‘lsa, manbalarga tayangan tabiiy til javobi.
- Oddiy web-chat interfeys.
- FastAPI backend.

## Loyiha tuzilmasi

```text
yordamchi-ai-namdtu-transport/
├── backend/              # FastAPI backend, RAG qidiruv va AI javob
├── frontend/             # Oddiy HTML/CSS/JS web interfeys
├── knowledge_base/       # Markdown formatidagi normativ-huquqiy manbalar
├── docs/                 # GitHub va loyiha hujjatlari
├── scripts/              # Ishga tushirish va GitHub yordamchi skriptlari
├── tests/                # Minimal testlar
├── requirements.txt
├── .env.example
└── README.md
```

## Mahalliy ishga tushirish

### 1. Repozitoriyani ochish

```bash
cd yordamchi-ai-namdtu-transport
```

### 2. Virtual muhit yaratish

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
```

### 3. Kutubxonalarni o‘rnatish

```bash
pip install -r requirements.txt
```

### 4. Muhit sozlamasini yaratish

```bash
cp .env.example .env
```

OpenAI API ishlatmoqchi bo‘lsangiz `.env` faylida `OPENAI_API_KEY` qiymatini kiriting. Kiritilmasa ham platforma manba asosidagi fallback rejimida ishlaydi.

### 5. Serverni ishga tushirish

```bash
uvicorn backend.main:app --reload
```

Brauzerda oching:

```text
http://127.0.0.1:8000
```

## Bilim bazasiga hujjat qo‘shish

`knowledge_base/` papkasiga yangi `.md` fayl qo‘shing. Har bir faylda frontmatter bo‘lishi tavsiya etiladi:

```md
---
title: "Hujjat nomi"
document_number: "VMQ-000"
date: "01.01.2026"
url: "https://lex.uz/..."
status: "amalda"
---

# Mavzu nomi
Hujjatdan qisqa, tekshirilgan va manbali matn.
```

Server ishlayotgan bo‘lsa, bilim bazasini yangilash:

```bash
curl -X POST http://127.0.0.1:8000/api/reload
```

Production holatda `/api/reload` endpointini albatta admin login bilan himoyalash kerak.

## API endpointlar

| Method | Endpoint | Vazifa |
|---|---|---|
| GET | `/` | Web interfeys |
| GET | `/api/health` | Server va bilim bazasi holati |
| GET | `/api/sources` | Hujjatlar ro‘yxati |
| POST | `/api/ask` | Talaba savoliga javob |
| POST | `/api/reload` | Bilim bazasini qayta yuklash |

### `/api/ask` namunasi

```bash
curl -X POST http://127.0.0.1:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"Akademik ta’til olish tartibi qanday?","mode":"short"}'
```

## GitHub’ga joylash

1. GitHub’da yangi repository yarating: `yordamchi-ai-namdtu-transport`.
2. Quyidagi buyruqlarni ishlating:

```bash
git init
git add .
git commit -m "Initial MVP for Yordamchi AI NamDTU Transport"
git branch -M main
git remote add origin https://github.com/USERNAME/yordamchi-ai-namdtu-transport.git
git push -u origin main
```

`USERNAME` o‘rniga GitHub profilingiz nomini yozing.

## Muhim xavfsizlik talablari

- AI yakuniy yuridik qaror chiqarmaydi.
- Har bir javobda manba ko‘rsatiladi.
- Manba topilmasa, taxminiy javob berilmaydi.
- Universitet ichki hujjatlari faqat mas’ul shaxs ruxsati bilan qo‘shiladi.
- Talabalarning shaxsiy ma’lumotlari backend loglarida saqlanmasligi kerak.
- Production muhitda admin endpointlar autentifikatsiya bilan himoyalanishi shart.

## Keyingi rivojlantirish

- Admin panel: hujjat yuklash, tahrirlash, eskirgan hujjatni belgilash.
- Telegram bot integratsiyasi.
- OneID yoki universitet login tizimi bilan autentifikatsiya.
- PDF/DOCX parser.
- Qdrant yoki pgvector bilan professional vektor qidiruv.
- Foydalanuvchi bahosi: “foydali / foydasiz”.
- Savollar statistikasi va FAQ avtomatik generatsiyasi.
