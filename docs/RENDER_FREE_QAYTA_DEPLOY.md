# Render Free hostingga qayta deploy qilish

Agar Render deploy oynasi uzoq vaqt aylanib tursa, odatda server ishga tushish paytida og'ir ish bajarayotgan bo'ladi. Bu loyiha RAG qidiruv uchun vector indeks ishlatadi, shuning uchun to'liq hujjatlar bazasida indeksni Render start paytida qurish tavsiya etilmaydi.

## Tavsiya etilgan Environment Variables

```env
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
USE_VECTOR_SEARCH=true
BUILD_VECTOR_INDEX_ON_STARTUP=false
```

Bu rejimda server tez ishga tushadi. Agar `.cache/vector_index.json` GitHub'da bo'lsa, vector qidiruv ishlaydi. Agar cache bo'lmasa, tizim keyword qidiruv orqali manbalarni topib, AI javob yaratadi.

## Eng yaxshi usul: indeksni lokalda qurib GitHub'ga yuklash

```cmd
cd /d C:\Users\admin\Desktop\yordamchi-ai-namdtu-transport
.venv\Scripts\activate.bat
python scripts\build_vector_index.py
git add .cache\vector_index.json
git commit -m "Add prebuilt vector index"
git push
```

Keyin Render avtomatik qayta deploy qiladi.

## Render start command

```bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

## Deploy qotib qolsa

1. Render -> Service -> Manual Deploy -> Clear build cache & deploy.
2. Environment Variables ni tekshiring.
3. Build log va deploy logdagi oxirgi xatolik qatorini tekshiring.
