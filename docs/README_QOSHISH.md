# Yordamchi AI — Lex.uz bilim bazasi (.md)

Bu papkadagi `.md` fayllar “Yordamchi AI — NamDTU Transport fakulteti” platformasining `knowledge_base` papkasiga qo‘yish uchun tayyorlangan.

## Qo‘shish tartibi — Windows CMD

1. ZIP faylni oching.
2. Loyiha papkasiga kiring:

```cmd
cd /d C:\Users\admin\Desktop\yordamchi-ai-namdtu-transport
```

3. Eski `knowledge_base` papkasini zaxiralab qo‘ying:

```cmd
ren knowledge_base knowledge_base_old
```

4. Ushbu paketdagi `knowledge_base` papkasini loyiha ichiga nusxalang.

5. Serverni qayta ishga tushiring:

```cmd
.venv\Scripts\activate.bat
python -m uvicorn backend.main:app --reload
```

Yoki server ishlab turgan bo‘lsa:

```cmd
curl -X POST http://127.0.0.1:8000/api/reload
```

6. GitHub’ga saqlang:

```cmd
git add knowledge_base
git commit -m "Add Lex.uz based knowledge base"
git push
```

## Test uchun savollar

- Darsni 18 soat qoldirsam nima bo‘ladi?
- 74 soatdan ortiq dars qoldirsam o‘qishdan chetlatilamanmi?
- Akademik taʼtil qanday olinadi?
- GPA nima?
- Oraliq nazorat nechta bo‘ladi?
- Yotoqxonaga qanday ariza beriladi?
- Ijtimoiy reestrda bo‘lsam TTJ to‘lovi qoplanadimi?
- Kontraktni to‘lamasam nima bo‘ladi?
- Magistrlik dissertatsiyasi necha bet bo‘lishi kerak?
