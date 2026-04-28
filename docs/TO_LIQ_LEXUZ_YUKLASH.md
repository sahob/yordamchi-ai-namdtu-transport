# Lex.uz hujjatlarini to'liq yuklash

Bu qo'llanma `knowledge_base` ichiga Lex.uz'dagi normativ-huquqiy hujjatlarning to'liq matnini `.md` formatida yuklaydi. Platforma keyin RAG qidiruv + AI modeli orqali aynan shu hujjatlar asosida javob beradi.

## 1. Kerakli paketlarni o'rnatish

```cmd
cd /d C:\Users\admin\Desktop\yordamchi-ai-namdtu-transport
.venv\Scripts\activate.bat
pip install -r requirements.txt
```

## 2. Hujjatlarni to'liq yuklash

Mavjud qisqa `.md` fayllarni zaxiralab, ularning o'rniga to'liq Lex.uz bazasini yuklash uchun:

```cmd
python scripts\download_lexuz_full.py --replace
```

Natijada fayllar quyidagi papkaga tushadi:

```text
knowledge_base\lexuz_full\
```

## 3. Eski vector indeksni tozalash

To'liq matn yuklangandan keyin eski embedding cache mos kelmasligi mumkin. Tozalash:

```cmd
rmdir /s /q .cache
```

## 4. Serverni qayta ishga tushirish

```cmd
python -m uvicorn backend.main:app --reload
```

Yoki server ishlab turgan bo'lsa:

```cmd
curl -X POST http://127.0.0.1:8000/api/reload
```

## 5. Tekshirish

Brauzerda:

```text
http://127.0.0.1:8000/api/health
```

`chunks` soni ko'paygan bo'lishi kerak. Keyin platformada test savollar bering:

- Talaba qanday hollarda o'qishdan chetlashtiriladi?
- Akademik ta'til olish tartibi qanday?
- Stipendiya qanday tayinlanadi?
- Talabalar turar joyiga kimlar birinchi navbatda joylashadi?
- Kontraktni kechiktirsam nima bo'ladi?

## 6. GitHub'ga yuklash

```cmd
git add backend scripts docs requirements.txt knowledge_base
git commit -m "Add full Lex.uz importer and full legal knowledge base"
git push
```

## Eslatma

To'liq hujjatlar embedding qilishda OpenAI API chaqiruvlari ishlatiladi. Birinchi yuklashda biroz vaqt va API krediti sarflanishi mumkin. Keyingi ishga tushirishlarda `.cache/vector_index.json` ishlatiladi.
