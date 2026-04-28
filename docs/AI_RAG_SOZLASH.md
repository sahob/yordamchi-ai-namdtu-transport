# Yordamchi AI RAG sozlash

Bu versiya oldindan tayyorlangan savol-javoblarga tayanmaydi. Tizim quyidagicha ishlaydi:

1. Talaba ixtiyoriy savol beradi.
2. Tizim `knowledge_base/*.md` ichidan savolga mos normativ-huquqiy manbalarni semantik qidiruv orqali topadi.
3. AI modeli faqat topilgan manbalar asosida javob yaratadi.
4. Javobda manba raqamlari `[1]`, `[2]` tarzida ko'rsatiladi.

## Majburiy sozlama

`.env` fayliga OpenAI API kalitini yozing:

```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

Kalit kiritilmasa, platforma AI javob yaratmaydi.

## Bilim bazasini yangilash

`knowledge_base` ichiga `.md` hujjatlar joylang. Keyin serverni qayta ishga tushiring yoki:

```cmd
curl -X POST http://127.0.0.1:8000/api/reload
```

Server qayta ishga tushganda `.cache/vector_index.json` fayli yaratiladi. Bu hujjatlar embedding indeksidir.

## Test savollar

```text
Talaba qanday hollarda o'qishdan chetlashtiriladi?
Akademik ta'til kimlarga beriladi?
Yotoqxonaga joylashish tartibi qanday?
Kontrakt to'lovini kechiktirsam nima bo'ladi?
Baholashda yakuniy nazoratdan o'tolmasam nima bo'ladi?
```
