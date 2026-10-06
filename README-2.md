# 🌱 EcoXabar

Chiqindilar haqida xabar berish sayti (Flask + SQLite).

## Lokal ishga tushirish
```bash
pip install -r requirements.txt
python app.py
```
Sayt: http://localhost:5000

## Muhit o'zgaruvchilari
| Nomi | Vazifasi |
|------|----------|
| `SECRET_KEY` | Sessiya uchun uzun tasodifiy matn (majburiy, serverda) |
| `ADMIN_PHONE` | Shu telefon raqami bilan ro'yxatdan o'tgan foydalanuvchi admin bo'ladi |
| `DATA_DIR` | Baza va suratlar saqlanadigan papka (ixtiyoriy) |

## Render.com'ga joylash
1. Render → New → Web Service → GitHub repozitoriyni tanlang
2. Build Command: `pip install -r requirements.txt`
3. Start Command: `gunicorn app:app`
4. Environment bo'limiga `SECRET_KEY` va `ADMIN_PHONE` qo'shing
5. Deploy bosing
