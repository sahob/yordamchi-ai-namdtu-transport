# Texnik topshiriq: Yordamchi AI — NamDTU Transport fakulteti

## Maqsad

Transport fakulteti talabalarining normativ-huquqiy va o‘quv jarayoniga oid savollariga tezkor, manbali va ishonchli javob beruvchi online AI platforma yaratish.

## Asosiy rollar

1. Talaba — savol beradi va javob oladi.
2. Moderator — noto‘g‘ri javoblar bo‘yicha fikr bildiradi.
3. Administrator — bilim bazasiga hujjat qo‘shadi va yangilaydi.
4. Mas’ul bo‘lim — yakuniy huquqiy va tashkiliy qarorlarni tasdiqlaydi.

## Funksional talablar

- Savol-javob chat interfeysi.
- Manba bilan javob berish.
- Uzbek Latin, Uzbek Cyrillic va rus tilidagi savollarni qabul qilish.
- Hujjatlar ro‘yxatini ko‘rsatish.
- Bilim bazasini qayta yuklash.
- Past ishonch holatida taxmin qilmaslik.

## Nofunksional talablar

- Backend javob vaqti MVP bosqichida 3 soniyadan oshmasligi maqsad qilinadi.
- Talaba shaxsiy ma’lumotlari javob loglarida saqlanmaydi.
- Admin endpointlar production bosqichida autentifikatsiya bilan himoyalanadi.
- Har bir hujjatda sana, raqam va havola saqlanadi.

## Arxitektura

- Frontend: HTML/CSS/JS MVP.
- Backend: FastAPI.
- Qidiruv: TF-IDF asosidagi semantik/kalit so‘z qidiruv MVP.
- AI: ixtiyoriy OpenAI API; API kaliti bo‘lmasa fallback javob.
- Bilim bazasi: Markdown fayllar.

## Production uchun tavsiya

MVP sinovdan o‘tgach quyidagilar qo‘shiladi:

- Next.js frontend.
- PostgreSQL + pgvector yoki Qdrant.
- Admin panel.
- Login va rollar.
- PDF/DOCX parser.
- Telegram bot.
- Audit log.
