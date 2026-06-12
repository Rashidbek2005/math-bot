import logging
import json
import os
import asyncio
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters, ConversationHandler
)

# ============================================================
#  SOZLAMALAR
# ============================================================
TOKEN = "8935480466:AAHUZKJDt7iuFXPjNbFrReTym9ReTtu4OIY"
TEACHER_ID = 5048048280
DATA_FILE = "data.json"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Conversation states
(
    WAIT_FIRST_NAME, WAIT_LAST_NAME,
    ADD_HOMEWORK_TITLE, ADD_HOMEWORK_DESC, ADD_HOMEWORK_DEADLINE,
    ADD_VIDEO_TITLE, ADD_VIDEO_LINK, ADD_VIDEO_TOPIC,
    ADD_TEST_NAME, ADD_TEST_TIME, ADD_TEST_BULK,
) = range(11)

# ============================================================
#  MA'LUMOTLAR BAZASI
# ============================================================
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "students": {},
        "homeworks": [],
        "videos": [],
        "tests": [],
    }

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def is_teacher(user_id):
    return user_id == TEACHER_ID

def is_registered(user_id, data):
    return str(user_id) in data["students"]

# ============================================================
#  MENYULAR
# ============================================================
def teacher_menu():
    keyboard = [
        [InlineKeyboardButton("📚 Vazifa qo'shish", callback_data="add_homework"),
         InlineKeyboardButton("🎥 Video qo'shish", callback_data="add_video")],
        [InlineKeyboardButton("📝 Test yaratish", callback_data="add_test"),
         InlineKeyboardButton("👥 O'quvchilar", callback_data="view_students")],
        [InlineKeyboardButton("📋 Vazifalar", callback_data="view_homeworks"),
         InlineKeyboardButton("🎬 Videolar", callback_data="view_videos")],
        [InlineKeyboardButton("📊 Test natijalari", callback_data="test_results"),
         InlineKeyboardButton("🗑 Testlarni tozala", callback_data="clear_tests")],
    ]
    return InlineKeyboardMarkup(keyboard)

def student_menu():
    keyboard = [
        [InlineKeyboardButton("📚 Uy vazifalari", callback_data="s_homeworks"),
         InlineKeyboardButton("🎥 Video darslar", callback_data="s_videos")],
        [InlineKeyboardButton("📝 Testlar", callback_data="s_tests"),
         InlineKeyboardButton("🤖 AI yordam", callback_data="s_ai")],
        [InlineKeyboardButton("📊 Natijalarim", callback_data="s_results")],
    ]
    return InlineKeyboardMarkup(keyboard)

def back_to_menu_btn(role="student"):
    cb = "go_student_menu" if role == "student" else "go_teacher_menu"
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Bosh menyu", callback_data=cb)]])

# ============================================================
#  /start
# ============================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    data = load_data()

    if is_teacher(user_id):
        await update.message.reply_text(
            "👨‍🏫 *O'qituvchi paneli*\n\nAssalomu alaykum, Rashidbek domla!",
            parse_mode="Markdown",
            reply_markup=teacher_menu()
        )
        return ConversationHandler.END

    if is_registered(user_id, data):
        s = data["students"][str(user_id)]
        name = f"{s['first_name']} {s['last_name']}"
        await update.message.reply_text(
            f"👋 Xush kelibsiz, *{name}*!",
            parse_mode="Markdown",
            reply_markup=student_menu()
        )
        return ConversationHandler.END

    await update.message.reply_text(
        "🏫 *Matematika 10-11 sinf*\n\n"
        "Ro'yxatdan o'tish uchun ismingizni kiriting:",
        parse_mode="Markdown"
    )
    return WAIT_FIRST_NAME

# ============================================================
#  RO'YXATDAN O'TISH
# ============================================================
async def wait_first_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    first = update.message.text.strip()
    if len(first) < 2:
        await update.message.reply_text("❌ Ism juda qisqa. Qayta kiriting:")
        return WAIT_FIRST_NAME
    context.user_data["first_name"] = first
    await update.message.reply_text(f"✅ Ism: *{first}*\n\nFamilyangizni kiriting:", parse_mode="Markdown")
    return WAIT_LAST_NAME

async def wait_last_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    last = update.message.text.strip()
    if len(last) < 2:
        await update.message.reply_text("❌ Familya juda qisqa. Qayta kiriting:")
        return WAIT_LAST_NAME

    first = context.user_data["first_name"]
    user_id = str(update.effective_user.id)
    data = load_data()

    data["students"][user_id] = {
        "first_name": first,
        "last_name": last,
        "username": update.effective_user.username or "",
        "registered_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "test_results": {}
    }
    save_data(data)

    await update.message.reply_text(
        f"🎉 *{first} {last}*, muvaffaqiyatli ro'yxatdan o'tdingiz!\n\nXush kelibsiz!",
        parse_mode="Markdown",
        reply_markup=student_menu()
    )
    return ConversationHandler.END

# ============================================================
#  O'QITUVCHI — VAZIFA
# ============================================================
async def add_homework_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("📚 Vazifa sarlavhasini kiriting:")
    return ADD_HOMEWORK_TITLE

async def add_homework_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["hw_title"] = update.message.text.strip()
    await update.message.reply_text("📝 Vazifa mazmunini kiriting:")
    return ADD_HOMEWORK_DESC

async def add_homework_desc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["hw_desc"] = update.message.text.strip()
    await update.message.reply_text("📅 Muddatni kiriting (masalan: 15-iyun):")
    return ADD_HOMEWORK_DEADLINE

async def add_homework_deadline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    hw = {
        "id": len(data["homeworks"]) + 1,
        "title": context.user_data["hw_title"],
        "desc": context.user_data["hw_desc"],
        "deadline": update.message.text.strip()
    }
    data["homeworks"].append(hw)
    save_data(data)

    await update.message.reply_text(
        f"✅ Vazifa qo'shildi!\n\n📚 *{hw['title']}*\n{hw['desc']}\n📅 {hw['deadline']}",
        parse_mode="Markdown",
        reply_markup=teacher_menu()
    )
    for uid in data["students"]:
        try:
            await context.bot.send_message(
                chat_id=int(uid),
                text=f"📚 *Yangi vazifa!*\n\n*{hw['title']}*\n{hw['desc']}\n📅 Muddat: {hw['deadline']}",
                parse_mode="Markdown"
            )
        except:
            pass
    return ConversationHandler.END

# ============================================================
#  O'QITUVCHI — VIDEO
# ============================================================
async def add_video_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("🎥 Video sarlavhasini kiriting:")
    return ADD_VIDEO_TITLE

async def add_video_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["v_title"] = update.message.text.strip()
    await update.message.reply_text("🔗 Video havolasini kiriting (YouTube):")
    return ADD_VIDEO_LINK

async def add_video_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["v_link"] = update.message.text.strip()
    await update.message.reply_text("📖 Mavzuni kiriting (masalan: Trigonometriya):")
    return ADD_VIDEO_TOPIC

async def add_video_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    video = {
        "id": len(data["videos"]) + 1,
        "title": context.user_data["v_title"],
        "link": context.user_data["v_link"],
        "topic": update.message.text.strip()
    }
    data["videos"].append(video)
    save_data(data)

    await update.message.reply_text(
        f"✅ Video qo'shildi!\n\n🎥 *{video['title']}*\n📖 {video['topic']}\n🔗 {video['link']}",
        parse_mode="Markdown",
        reply_markup=teacher_menu()
    )
    for uid in data["students"]:
        try:
            await context.bot.send_message(
                chat_id=int(uid),
                text=f"🎥 *Yangi video dars!*\n\n*{video['title']}*\n📖 {video['topic']}\n🔗 {video['link']}",
                parse_mode="Markdown"
            )
        except:
            pass
    return ConversationHandler.END

# ============================================================
#  O'QITUVCHI — TEST (BULK)
# ============================================================
async def add_test_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text(
        "📝 Test nomini kiriting:\nMasalan: _Planimetriya — Burchaklar_",
        parse_mode="Markdown"
    )
    return ADD_TEST_NAME

async def add_test_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["test_title"] = update.message.text.strip()
    await update.message.reply_text(
        "⏱ Test vaqtini kiriting (daqiqada):\nMasalan: *20*",
        parse_mode="Markdown"
    )
    return ADD_TEST_TIME

async def add_test_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        minutes = int(update.message.text.strip())
        if minutes < 1 or minutes > 180:
            raise ValueError
        context.user_data["test_time"] = minutes
    except:
        await update.message.reply_text("❌ Noto'g'ri. Faqat raqam kiriting (1-180):")
        return ADD_TEST_TIME

    await update.message.reply_text(
        f"✅ Vaqt: *{context.user_data['test_time']} daqiqa*\n\n"
        "Endi barcha savollarni *bir xabarda* yuboring:\n\n"
        "📋 *Format:*\n"
        "```\n"
        "1. Savol matni\n"
        "A) variant\n"
        "B) variant\n"
        "C) variant\n"
        "D) variant\n"
        "To'g'ri: A\n\n"
        "2. Savol matni\n"
        "...\n"
        "```",
        parse_mode="Markdown"
    )
    return ADD_TEST_BULK

async def add_test_bulk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    questions = []
    blocks = []
    current = []

    for line in text.split("\n"):
        line = line.strip()
        if not line:
            if current:
                blocks.append(current)
                current = []
        else:
            current.append(line)
    if current:
        blocks.append(current)

    for block in blocks:
        q_text = ""
        options_lines = []
        answer = ""
        for line in block:
            if line and line[0].isdigit() and ("." in line[:3] or ")" in line[:3]):
                q_text = line.split(".", 1)[-1].split(")", 1)[-1].strip()
            elif line.upper().startswith(("A)", "B)", "C)", "D)")):
                options_lines.append(line)
            elif "to'g'ri" in line.lower() or "togri" in line.lower():
                parts = line.split(":")
                if len(parts) > 1:
                    answer = parts[1].strip().upper()[0] if parts[1].strip() else ""

        if q_text and options_lines and answer in ["A", "B", "C", "D"]:
            questions.append({
                "q": q_text,
                "options": "\n".join(options_lines),
                "answer": answer
            })

    if not questions:
        await update.message.reply_text(
            "❌ Savollar topilmadi. Format to'g'ri emasmi?\n\n"
            "Namuna:\n1. Savol\nA) ...\nB) ...\nC) ...\nD) ...\nTo'g'ri: A"
        )
        return ADD_TEST_BULK

    data = load_data()
    test = {
        "id": len(data["tests"]) + 1,
        "title": context.user_data.get("test_title", f"Test #{len(data['tests'])+1}"),
        "time_limit": context.user_data.get("test_time", 20),
        "questions": questions
    }
    data["tests"].append(test)
    save_data(data)
    context.user_data.pop("test_title", None)
    context.user_data.pop("test_time", None)

    await update.message.reply_text(
        f"✅ *{test['title']}* yaratildi!\n"
        f"📊 {len(questions)} ta savol | ⏱ {test['time_limit']} daqiqa",
        parse_mode="Markdown",
        reply_markup=teacher_menu()
    )
    for uid in data["students"]:
        try:
            await context.bot.send_message(
                chat_id=int(uid),
                text=f"📝 *Yangi test!*\n\n*{test['title']}*\n"
                     f"📊 {len(questions)} ta savol\n⏱ {test['time_limit']} daqiqa\n\nBotdan kirib ishlang!",
                parse_mode="Markdown"
            )
        except:
            pass
    return ConversationHandler.END

# ============================================================
#  TEST ISHLASH
# ============================================================
async def send_test_question(message, context, test, idx):
    q = test["questions"][idx]
    total = len(test["questions"])
    keyboard = [
        [InlineKeyboardButton("A", callback_data="ta_A"),
         InlineKeyboardButton("B", callback_data="ta_B")],
        [InlineKeyboardButton("C", callback_data="ta_C"),
         InlineKeyboardButton("D", callback_data="ta_D")],
        [InlineKeyboardButton("🏳 Testni tugatish", callback_data="ta_finish")],
    ]
    await message.reply_text(
        f"📝 *{test['title']}*\n"
        f"Savol {idx+1}/{total} | ⏱ {test.get('time_limit', 20)} daqiqa\n\n"
        f"*{q['q']}*\n\n{q['options']}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def finish_test(message, context, data, user_id):
    test = context.user_data.get("active_test")
    score = context.user_data.get("test_score", 0)
    total = len(test["questions"])
    pct = round(score / total * 100) if total else 0

    if user_id not in data["students"]:
        data["students"][user_id] = {"first_name": "?", "last_name": "?", "test_results": {}}
    if "test_results" not in data["students"][user_id]:
        data["students"][user_id]["test_results"] = {}
    data["students"][user_id]["test_results"][str(test["id"])] = {
        "score": score, "total": total, "percent": pct,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    save_data(data)

    emoji = "🏆" if pct >= 80 else "👍" if pct >= 50 else "📚"
    comment = "Zo'r natija!" if pct >= 80 else "Yaxshi!" if pct >= 50 else "Ko'proq o'qing!"

    context.user_data.pop("active_test", None)
    context.user_data.pop("test_q_index", None)
    context.user_data.pop("test_score", None)

    await message.reply_text(
        f"{emoji} *Test yakunlandi!*\n\n"
        f"📊 Natija: *{score}/{total}* ({pct}%)\n"
        f"💬 {comment}",
        parse_mode="Markdown",
        reply_markup=student_menu()
    )

# ============================================================
#  CALLBACK HANDLERLAR
# ============================================================
async def all_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = load_data()
    user_id = str(query.from_user.id)
    cb = query.data

    # --- Menyu navigatsiya ---
    if cb == "go_student_menu":
        await query.message.reply_text("📱 Bosh menyu:", reply_markup=student_menu())
        return
    if cb == "go_teacher_menu":
        await query.message.reply_text("👨‍🏫 O'qituvchi paneli:", reply_markup=teacher_menu())
        return

    # ============ O'QITUVCHI CALLBACKLAR ============
    if cb == "view_students":
        if not data["students"]:
            text = "👥 Hali o'quvchi yo'q."
        else:
            lines = [f"👥 *O'quvchilar ({len(data['students'])} ta):*\n"]
            for i, (uid, s) in enumerate(data["students"].items(), 1):
                name = f"{s.get('first_name','')} {s.get('last_name','')}"
                uname = f"@{s['username']}" if s.get("username") else ""
                lines.append(f"{i}. *{name}* {uname}")
            text = "\n".join(lines)
        await query.message.reply_text(text, parse_mode="Markdown", reply_markup=back_to_menu_btn("teacher"))

    elif cb == "view_homeworks":
        if not data["homeworks"]:
            text = "📚 Hali vazifa yo'q."
        else:
            lines = ["📚 *Barcha vazifalar:*\n"]
            for hw in data["homeworks"]:
                lines.append(f"*{hw['id']}.* {hw['title']} — 📅 {hw['deadline']}")
            text = "\n".join(lines)
        await query.message.reply_text(text, parse_mode="Markdown", reply_markup=back_to_menu_btn("teacher"))

    elif cb == "view_videos":
        if not data["videos"]:
            text = "🎥 Hali video yo'q."
        else:
            lines = ["🎥 *Barcha videolar:*\n"]
            for v in data["videos"]:
                lines.append(f"*{v['id']}.* {v['title']} — {v['link']}")
            text = "\n".join(lines)
        await query.message.reply_text(text, parse_mode="Markdown", reply_markup=back_to_menu_btn("teacher"))

    elif cb == "test_results":
        lines = ["📊 *Test natijalari:*\n"]
        found = False
        for uid, s in data["students"].items():
            name = f"{s.get('first_name','')} {s.get('last_name','')}"
            for tid, r in s.get("test_results", {}).items():
                test_name = next((t["title"] for t in data["tests"] if str(t["id"]) == tid), f"Test {tid}")
                lines.append(f"👤 {name} | {test_name}: {r['score']}/{r['total']} ({r.get('percent',0)}%)")
                found = True
        if not found:
            lines.append("Hali natija yo'q.")
        await query.message.reply_text("\n".join(lines), parse_mode="Markdown", reply_markup=back_to_menu_btn("teacher"))

    elif cb == "clear_tests":
        keyboard = [[
            InlineKeyboardButton("✅ Ha, tozala", callback_data="confirm_clear_tests"),
            InlineKeyboardButton("❌ Yo'q", callback_data="go_teacher_menu")
        ]]
        await query.message.reply_text(
            "⚠️ Barcha testlar o'chirilsinmi?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif cb == "confirm_clear_tests":
        data["tests"] = []
        save_data(data)
        await query.message.reply_text("✅ Testlar tozalandi!", reply_markup=teacher_menu())

    # ============ O'QUVCHI CALLBACKLAR ============
    elif cb == "s_homeworks":
        if not data["homeworks"]:
            text = "📚 Hali vazifa yo'q."
        else:
            lines = ["📚 *Uy vazifalari:*\n"]
            for hw in data["homeworks"]:
                lines.append(f"*{hw['id']}.* {hw['title']}\n   📝 {hw['desc']}\n   📅 Muddat: {hw['deadline']}\n")
            text = "\n".join(lines)
        await query.message.reply_text(text, parse_mode="Markdown", reply_markup=back_to_menu_btn())

    elif cb == "s_videos":
        if not data["videos"]:
            text = "🎥 Hali video yo'q."
        else:
            lines = ["🎥 *Video darslar:*\n"]
            for v in data["videos"]:
                lines.append(f"*{v['id']}.* {v['title']}\n   📖 {v['topic']}\n   🔗 {v['link']}\n")
            text = "\n".join(lines)
        await query.message.reply_text(text, parse_mode="Markdown", reply_markup=back_to_menu_btn())

    elif cb == "s_tests":
        if not data["tests"]:
            await query.message.reply_text("📝 Hali test yo'q.", reply_markup=back_to_menu_btn())
            return
        keyboard = []
        for t in data["tests"]:
            keyboard.append([InlineKeyboardButton(
                f"📝 {t['title']} ({len(t['questions'])} savol | ⏱{t.get('time_limit',20)} daq)",
                callback_data=f"take_test_{t['id']}"
            )])
        keyboard.append([InlineKeyboardButton("🔙 Bosh menyu", callback_data="go_student_menu")])
        await query.message.reply_text(
            "📝 *Testlar:*\nQaysi testni ishlaysiz?",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif cb.startswith("take_test_"):
        test_id = int(cb.split("_")[-1])
        test = next((t for t in data["tests"] if t["id"] == test_id), None)
        if not test:
            await query.message.reply_text("Test topilmadi.", reply_markup=back_to_menu_btn())
            return
        context.user_data["active_test"] = test
        context.user_data["test_q_index"] = 0
        context.user_data["test_score"] = 0
        context.user_data["test_start"] = datetime.now().isoformat()
        await send_test_question(query.message, context, test, 0)

    elif cb.startswith("ta_"):
        test = context.user_data.get("active_test")
        if not test:
            await query.message.reply_text("Test topilmadi.", reply_markup=student_menu())
            return

        if cb == "ta_finish":
            await finish_test(query.message, context, data, user_id)
            return

        answer = cb.split("_")[1]
        idx = context.user_data.get("test_q_index", 0)
        correct = test["questions"][idx]["answer"]

        if answer == correct:
            context.user_data["test_score"] = context.user_data.get("test_score", 0) + 1
            await query.message.reply_text("✅ To'g'ri!")
        else:
            await query.message.reply_text(f"❌ Noto'g'ri! To'g'ri javob: *{correct}*", parse_mode="Markdown")

        next_idx = idx + 1
        context.user_data["test_q_index"] = next_idx

        if next_idx < len(test["questions"]):
            await send_test_question(query.message, context, test, next_idx)
        else:
            await finish_test(query.message, context, data, user_id)

    elif cb == "s_ai":
        context.user_data["ai_mode"] = True
        await query.message.reply_text(
            "🤖 *AI matematik yordamchi*\n\n"
            "Savolingizni yozing, men tushuntiraman!\n\n"
            "Masalan:\n• sin(60°) nima?\n• x²-5x+6=0 ni yeching\n• Integral nima?",
            parse_mode="Markdown",
            reply_markup=back_to_menu_btn()
        )

    elif cb == "s_results":
        student = data["students"].get(user_id, {})
        results = student.get("test_results", {})
        if not results:
            text = "📊 Hali test ishlamadingiz."
        else:
            lines = ["📊 *Mening natijalarim:*\n"]
            for tid, r in results.items():
                test_name = next((t["title"] for t in data["tests"] if str(t["id"]) == tid), f"Test {tid}")
                lines.append(f"📝 {test_name}\n   ✅ {r['score']}/{r['total']} ({r.get('percent',0)}%) | 📅 {r.get('date','')}\n")
            text = "\n".join(lines)
        await query.message.reply_text(text, parse_mode="Markdown", reply_markup=back_to_menu_btn())

# ============================================================
#  MATN XABARLAR — AI
# ============================================================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    data = load_data()

    if is_teacher(user_id):
        await update.message.reply_text("O'qituvchi paneli:", reply_markup=teacher_menu())
        return

    if context.user_data.get("ai_mode"):
        context.user_data["ai_mode"] = False
        thinking = await update.message.reply_text("🤖 Javob tayyorlanmoqda...")

        try:
            import anthropic
            client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))
            response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=1000,
                messages=[{
                    "role": "user",
                    "content": f"Sen matematika o'qituvchisissan. O'zbek tilida, sodda va tushunarli tushuntir, misollar kel: {text}"
                }]
            )
            answer = response.content[0].text
        except Exception as e:
            answer = (
                "🤖 AI hozir ishlamayapti.\n\n"
                "Sabab: ANTHROPIC_API_KEY sozlanmagan.\n"
                "Railway → Variables bo'limiga ANTHROPIC_API_KEY qo'shing."
            )

        await thinking.delete()
        await update.message.reply_text(answer, reply_markup=student_menu())
        return

    if is_registered(user_id, data):
        await update.message.reply_text("Menyu:", reply_markup=student_menu())
    else:
        await update.message.reply_text(
            "Ro'yxatdan o'tish uchun /start yuboring."
        )

# ============================================================
#  ASOSIY
# ============================================================
def main():
    app = Application.builder().token(TOKEN).build()

    conv = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CallbackQueryHandler(add_homework_start, pattern="^add_homework$"),
            CallbackQueryHandler(add_video_start, pattern="^add_video$"),
            CallbackQueryHandler(add_test_start, pattern="^add_test$"),
        ],
        states={
            WAIT_FIRST_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, wait_first_name)],
            WAIT_LAST_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, wait_last_name)],
            ADD_HOMEWORK_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_homework_title)],
            ADD_HOMEWORK_DESC: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_homework_desc)],
            ADD_HOMEWORK_DEADLINE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_homework_deadline)],
            ADD_VIDEO_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_video_title)],
            ADD_VIDEO_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_video_link)],
            ADD_VIDEO_TOPIC: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_video_topic)],
            ADD_TEST_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_test_name)],
            ADD_TEST_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_test_time)],
            ADD_TEST_BULK: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_test_bulk)],
        },
        fallbacks=[CommandHandler("start", start)],
        per_message=False,
    )

    app.add_handler(conv)
    app.add_handler(CallbackQueryHandler(all_callbacks))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ Bot ishga tushdi!")
    app.run_polling()

if __name__ == "__main__":
    main()
