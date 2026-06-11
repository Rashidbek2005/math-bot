# 📚 Matematika Bot — O'rnatish Yo'riqnomasi

## Kerakli fayllar
- `math_bot.py` — asosiy bot kodi
- `requirements.txt` — kutubxonalar
- `railway.toml` — server sozlamasi

---

## 1-QADAM: GitHub hisob oching

1. https://github.com ga boring
2. "Sign up" bosing
3. Bepul hisob yarating (Google bilan ham bo'ladi)

---

## 2-QADAM: Yangi repository yarating

1. GitHub ga kirgan holda "+" tugmasini bosing → "New repository"
2. Repository nomi: `math-bot`
3. "Public" tanlang
4. "Create repository" bosing

---

## 3-QADAM: Fayllarni yuklang

Repository ichida "uploading an existing file" havolasini bosing.
3 ta faylni yuklang:
- math_bot.py
- requirements.txt
- railway.toml

"Commit changes" bosing.

---

## 4-QADAM: Railway da joylashtiring

1. https://railway.app ga boring
2. "Start a New Project" bosing
3. "Deploy from GitHub repo" tanlang
4. GitHub bilan ulang va `math-bot` repositoryni tanlang
5. Railway avtomatik o'rnatadi

---

## 5-QADAM: Muhit o'zgaruvchilari (Environment Variables)

Railway dashboard da "Variables" bo'limiga boring va qo'shing:

```
ANTHROPIC_API_KEY = (ixtiyoriy — AI yordam uchun)
```

> AI yordam kerak bo'lmasa bu qadamni o'tkazib yuboring.

---

## 6-QADAM: Bot ishlayaptimi?

Railway "Deployments" bo'limida yashil "Success" ko'rsangiz — bot ishga tushdi!

Telegramga boring va botingizni oching, /start yuboring.

---

## Bot imkoniyatlari

### O'qituvchi (siz):
- 📚 Vazifa qo'shish → o'quvchilarga avtomatik xabar
- 🎥 Video qo'shish → o'quvchilarga avtomatik xabar
- 📝 Test yaratish → o'quvchilarga avtomatik xabar
- 👥 O'quvchilar ro'yxatini ko'rish
- 📊 Test natijalarini ko'rish
- 🔑 Sinf kodini ko'rish (standart: MATH2024)

### O'quvchilar:
- Sinf kodi bilan ro'yxatdan o'tish
- Vazifalarni ko'rish
- Video darslarni ko'rish
- Testlarni ishlash
- AI dan yordam so'rash

---

## Sinf kodi

Standart sinf kodi: **MATH2024**

O'zgartirish uchun `math_bot.py` faylida:
```python
"class_code": "MATH2024"
```
bu qatorni o'zgartiring.

---

## Muammo bo'lsa

Telegram: @userinfobot ga /start yuboring — ID ni tekshiring.
