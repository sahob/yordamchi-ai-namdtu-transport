# GitHub’ga joylash bo‘yicha yo‘riqnoma

## 1. GitHub repository yaratish

GitHub profiliga kiring va yangi repository yarating:

- Repository name: `yordamchi-ai-namdtu-transport`
- Visibility: `Public` yoki `Private`
- README qo‘shmang, chunki loyiha ichida tayyor README bor.

## 2. Lokal papkani GitHub bilan ulash

Terminalda loyiha papkasiga kiring:

```bash
cd yordamchi-ai-namdtu-transport
```

Gitni ishga tushiring:

```bash
git init
git add .
git commit -m "Initial MVP for Yordamchi AI NamDTU Transport"
git branch -M main
```

Remote ulash:

```bash
git remote add origin https://github.com/USERNAME/yordamchi-ai-namdtu-transport.git
```

GitHub’ga yuborish:

```bash
git push -u origin main
```

## 3. Keyingi o‘zgarishlarni yuborish

```bash
git add .
git commit -m "Update knowledge base"
git push
```

## 4. Tavsiya etiladigan branchlar

- `main` — barqaror versiya
- `dev` — ishlab chiqish versiyasi
- `feature/telegram-bot` — Telegram bot qo‘shish
- `feature/admin-panel` — admin panel qo‘shish
