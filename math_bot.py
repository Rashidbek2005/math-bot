import logging
import json
import os
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
    WAIT_STUDENT_CODE, WAIT_STUDENT_NAME,
    ADD_HOMEWORK_TITLE, ADD_HOMEWORK_DESC, ADD_HOMEWORK_DEADLINE,
    ADD_VIDEO_TITLE, ADD_VIDEO_LINK, ADD_VIDEO_TOPIC,
    ADD_TEST_QUESTION, ADD_TEST_OPTIONS, ADD_TEST_ANSWER,
    WAIT_CONFIRM_DELETE
) = range(12)

# ============================================================
#  MA'LUMOTLAR BAZASI (JSON fayl)
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
        "class_code": "MATH2024"
    }

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def is_teacher(user_id):
    return user_id == TEACHER_ID

def is_student(user_id, data):
    return str(user_id) in data["students"]

# ============================================================
#  BOSH MENYULAR
# ============================================================
def teacher_menu():
    keyboard = [
        [InlineKeyboardButton("📚 Vazifa qo'shish", callback_data="add_homework"),
         InlineKeyboardButton("🎥 Video qo'shish", callback_data="add_video")],
        [InlineKeyboardButton("📝 Test yaratish", callback_data="add_test"),
         InlineKeyboardButton("👥 O'quvchilar", callback_data="view_students")],
        [InlineKeyboardButton("📋 Barcha vazifalar", callback_data="view_homeworks"),
         InlineKeyboardButton("🎬 Barcha videolar", callback_data="view_videos")],
        [InlineKeyboardButton("📊 Test natijalari", callback_data="test_results"),
         InlineKeyboardButton("🔑 Sinf kodi", callback_data="class_code")],
    ]
    return InlineKeyboardMarkup(keyboard)

def student_menu():
    keyboard = [
        [InlineKeyboardButton("📚 Uy vazifalari", callback_data="s_homeworks"),
         InlineKeyboardButton("🎥 Video darslar", callback_data="s_videos")],
        [InlineKeyboardButton("📝 Testlar", callback_data="s_tests"),
         InlineKeyboardButton("🤖 AI yordam", callback_data="s_ai")],
        [InlineKeyboardButton("📊 Mening natijalarim", callback_data="s_results")],
    ]
    return InlineKeyboardMarkup(keyboard)

# ============================================================
#  /start
# ============================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    data = load_data()

    if is_teacher(user_id):
        await update.message.reply_text(
            "👨‍🏫 *O'qituvchi paneli*\n\nAssalomu alaykum! Nima qilmoqchisiz?",
            parse_mode="Markdown",
            reply_markup=teacher_menu()
        )
        return ConversationHandler.END

    if is_student(user_id, data):
        name = data["students"][str(user_id)]["name"]
        await update.message.reply_text(
            f"👋 Xush kelibsiz, *{name}*!\n\nNima qilmoqchisiz?",
            parse_mode="Markdown",
            reply_markup=student_menu()
        )
        return ConversationHandler.END

    await update.message.reply_text(
        "🏫 *Matematika 10-11 sinf boti*\n\n"
        "Kirish uchun sinf kodini yuboring:",
        parse_mode="Markdown"
    )
    return WAIT_STUDENT_CODE

# ============================================================
#  O'QUVCHI KIRISHI
# ============================================================
async def student_enter_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    code = update.message.text.strip().upper()

    if code == data["class_code"].upper():
        context.user_data["code_ok"] = True
        await update.message.reply_text("✅ Kod to'g'ri! Ismingizni kiriting:")
        return WAIT_STUDENT_NAME
    else:
        await update.message.reply_text("❌ Noto'g'ri kod. Qayta urinib ko'ring:")
        return WAIT_STUDENT_CODE

async def student_enter_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text.strip()
    user_id = str(update.effective_user.id)
    data = load_data()

    data["students"][user_id] = {
        "name": name,
        "username": update.effective_user.username or "",
        "test_results": {}
    }
    save_data(data)

    await update.message.reply_text(
        f"🎉 Xush kelibsiz, *{name}*!\nSiz muvaffaqiyatli ro'yxatdan o'tdingiz.",
        parse_mode="Markdown",
        reply_markup=student_menu()
    )
    return ConversationHandler.END

# ============================================================
#  O'QITUVCHI — VAZIFA QO'SHISH
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
    await update.message.reply_text("📅 Muddat kiriting (masalan: 15-iyun yoki 3 kun):")
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
        f"✅ Vazifa qo'shildi!\n\n"
        f"📚 *{hw['title']}*\n{hw['desc']}\n📅 Muddat: {hw['deadline']}",
        parse_mode="Markdown",
        reply_markup=teacher_menu()
    )

    # O'quvchilarga xabar yuborish
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
#  O'QITUVCHI — VIDEO QO'SHISH
# ============================================================
async def add_video_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("🎥 Video sarlavhasini kiriting:")
    return ADD_VIDEO_TITLE

async def add_video_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["v_title"] = update.message.text.strip()
    await update.message.reply_text("🔗 Video havolasini kiriting (YouTube yoki boshqa):")
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
        f"✅ Video qo'shildi!\n\n🎥 *{video['title']}*\n📖 Mavzu: {video['topic']}\n🔗 {video['link']}",
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
#  O'QITUVCHI — TEST YARATISH
# ============================================================
async def add_test_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["test_questions"] = []
    await query.message.reply_text(
        "📝 Test savolini kiriting:\n(Tugatish uchun /done yuboring)"
    )
    return ADD_TEST_QUESTION

async def add_test_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text.strip() == "/done":
        if not context.user_data.get("test_questions"):
            await update.message.reply_text("❌ Kamida 1 ta savol kiriting!")
            return ADD_TEST_QUESTION

        data = load_data()
        test = {
            "id": len(data["tests"]) + 1,
            "title": f"Test #{len(data['tests']) + 1}",
            "questions": context.user_data["test_questions"]
        }
        data["tests"].append(test)
        save_data(data)

        await update.message.reply_text(
            f"✅ Test yaratildi! {len(test['questions'])} ta savol.",
            reply_markup=teacher_menu()
        )

        for uid in data["students"]:
            try:
                await context.bot.send_message(
                    chat_id=int(uid),
                    text=f"📝 *Yangi test qo'shildi!*\n{test['title']} — {len(test['questions'])} ta savol\n\nBotdan kirib ishlang!",
                    parse_mode="Markdown"
                )
            except:
                pass

        return ConversationHandler.END

    context.user_data["current_question"] = update.message.text.strip()
    await update.message.reply_text(
        "Variantlarni kiriting (har birini yangi qatorga):\n"
        "Misol:\nA) 1\nB) 2\nC) 3\nD) 4"
    )
    return ADD_TEST_OPTIONS

async def add_test_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["current_options"] = update.message.text.strip()
    await update.message.reply_text("To'g'ri javobni kiriting (A, B, C yoki D):")
    return ADD_TEST_ANSWER

async def add_test_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    answer = update.message.text.strip().upper()
    if answer not in ["A", "B", "C", "D"]:
        await update.message.reply_text("❌ Faqat A, B, C yoki D kiriting:")
        return ADD_TEST_ANSWER

    question = {
        "q": context.user_data["current_question"],
        "options": context.user_data["current_options"],
        "answer": answer
    }
    context.user_data["test_questions"].append(question)

    count = len(context.user_data["test_questions"])
    await update.message.reply_text(
        f"✅ {count}-savol qo'shildi!\n\n"
        "Keyingi savolni kiriting yoki /done yuboring:"
    )
    return ADD_TEST_QUESTION

# ============================================================
#  CALLBACK — O'QITUVCHI
# ============================================================
async def teacher_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = load_data()

    if query.data == "view_students":
        if not data["students"]:
            text = "👥 Hali o'quvchi yo'q."
        else:
            lines = ["👥 *O'quvchilar ro'yxati:*\n"]
            for i, (uid, s) in enumerate(data["students"].items(), 1):
                uname = f"@{s['username']}" if s.get("username") else "username yo'q"
                lines.append(f"{i}. *{s['name']}* — {uname}")
            text = "\n".join(lines)
        await query.message.reply_text(text, parse_mode="Markdown", reply_markup=teacher_menu())

    elif query.data == "view_homeworks":
        if not data["homeworks"]:
            text = "📚 Hali vazifa yo'q."
        else:
            lines = ["📚 *Barcha vazifalar:*\n"]
            for hw in data["homeworks"]:
                lines.append(f"*{hw['id']}.* {hw['title']} — 📅 {hw['deadline']}")
            text = "\n".join(lines)
        await query.message.reply_text(text, parse_mode="Markdown", reply_markup=teacher_menu())

    elif query.data == "view_videos":
        if not data["videos"]:
            text = "🎥 Hali video yo'q."
        else:
            lines = ["🎥 *Barcha videolar:*\n"]
            for v in data["videos"]:
                lines.append(f"*{v['id']}.* {v['title']} — {v['link']}")
            text = "\n".join(lines)
        await query.message.reply_text(text, parse_mode="Markdown", reply_markup=teacher_menu())

    elif query.data == "test_results":
        lines = ["📊 *Test natijalari:*\n"]
        for uid, s in data["students"].items():
            if s.get("test_results"):
                for test_id, result in s["test_results"].items():
                    lines.append(f"👤 {s['name']} — Test {test_id}: {result['score']}/{result['total']}")
        if len(lines) == 1:
            lines.append("Hali natija yo'q.")
        await query.message.reply_text("\n".join(lines), parse_mode="Markdown", reply_markup=teacher_menu())

    elif query.data == "class_code":
        await query.message.reply_text(
            f"🔑 *Sinf kodi:* `{data['class_code']}`\n\nO'quvchilarga bu kodni bering.",
            parse_mode="Markdown",
            reply_markup=teacher_menu()
        )

# ============================================================
#  CALLBACK — O'QUVCHI
# ============================================================
async def student_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = load_data()
    user_id = str(query.from_user.id)

    if query.data == "s_homeworks":
        if not data["homeworks"]:
            text = "📚 Hali vazifa yo'q."
        else:
            lines = ["📚 *Uy vazifalari:*\n"]
            for hw in data["homeworks"]:
                lines.append(f"*{hw['id']}.* {hw['title']}\n   📝 {hw['desc']}\n   📅 Muddat: {hw['deadline']}\n")
            text = "\n".join(lines)
        await query.message.reply_text(text, parse_mode="Markdown", reply_markup=student_menu())

    elif query.data == "s_videos":
        if not data["videos"]:
            text = "🎥 Hali video yo'q."
        else:
            lines = ["🎥 *Video darslar:*\n"]
            for v in data["videos"]:
                lines.append(f"*{v['id']}.* {v['title']}\n   📖 {v['topic']}\n   🔗 {v['link']}\n")
            text = "\n".join(lines)
        await query.message.reply_text(text, parse_mode="Markdown", reply_markup=student_menu())

    elif query.data == "s_tests":
        if not data["tests"]:
            await query.message.reply_text("📝 Hali test yo'q.", reply_markup=student_menu())
            return
        keyboard = []
        for t in data["tests"]:
            keyboard.append([InlineKeyboardButton(
                f"📝 {t['title']} ({len(t['questions'])} savol)",
                callback_data=f"take_test_{t['id']}"
            )])
        keyboard.append([InlineKeyboardButton("🔙 Orqaga", callback_data="s_back")])
        await query.message.reply_text(
            "📝 *Testlar:*\nQaysi testni ishlaysiz?",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data.startswith("take_test_"):
        test_id = int(query.data.split("_")[-1])
        test = next((t for t in data["tests"] if t["id"] == test_id), None)
        if not test:
            await query.message.reply_text("Test topilmadi.")
            return

        context.user_data["active_test"] = test
        context.user_data["test_q_index"] = 0
        context.user_data["test_score"] = 0

        await send_test_question(query.message, context, test, 0)

    elif query.data.startswith("test_ans_"):
        parts = query.data.split("_")
        answer = parts[2]
        test = context.user_data.get("active_test")
        idx = context.user_data.get("test_q_index", 0)

        if not test:
            return

        correct = test["questions"][idx]["answer"]
        if answer == correct:
            context.user_data["test_score"] = context.user_data.get("test_score", 0) + 1
            await query.message.reply_text(f"✅ To'g'ri!")
        else:
            await query.message.reply_text(f"❌ Noto'g'ri! To'g'ri javob: {correct}")

        next_idx = idx + 1
        context.user_data["test_q_index"] = next_idx

        if next_idx < len(test["questions"]):
            await send_test_question(query.message, context, test, next_idx)
        else:
            score = context.user_data["test_score"]
            total = len(test["questions"])
            pct = round(score / total * 100)

            data = load_data()
            if user_id not in data["students"]:
                data["students"][user_id] = {"name": "Noma'lum", "test_results": {}}
            if "test_results" not in data["students"][user_id]:
                data["students"][user_id]["test_results"] = {}
            data["students"][user_id]["test_results"][str(test["id"])] = {
                "score": score, "total": total
            }
            save_data(data)

            emoji = "🏆" if pct >= 80 else "👍" if pct >= 50 else "📚"
            await query.message.reply_text(
                f"{emoji} *Test yakunlandi!*\n\n"
                f"Natija: *{score}/{total}* ({pct}%)\n\n"
                f"{'Zo\'r natija!' if pct >= 80 else 'Ko\'proq o\'qing!' if pct < 50 else 'Yaxshi!'}",
                parse_mode="Markdown",
                reply_markup=student_menu()
            )

    elif query.data == "s_ai":
        await query.message.reply_text(
            "🤖 *AI matematik yordamchi*\n\n"
            "Matematik savolingizni yozing, men tushuntiraman!\n\n"
            "Masalan:\n• sin(60°) nima?\n• x² - 5x + 6 = 0 ni yeching\n• Integral nima?",
            parse_mode="Markdown"
        )
        context.user_data["ai_mode"] = True

    elif query.data == "s_results":
        data = load_data()
        student = data["students"].get(user_id, {})
        results = student.get("test_results", {})
        if not results:
            text = "📊 Hali test ishlamadingiz."
        else:
            lines = ["📊 *Mening natijalarim:*\n"]
            for tid, r in results.items():
                pct = round(r['score'] / r['total'] * 100)
                lines.append(f"Test {tid}: {r['score']}/{r['total']} ({pct}%)")
            text = "\n".join(lines)
        await query.message.reply_text(text, parse_mode="Markdown", reply_markup=student_menu())

    elif query.data == "s_back":
        await query.message.reply_text("Bosh menyu:", reply_markup=student_menu())

async def send_test_question(message, context, test, idx):
    q = test["questions"][idx]
    total = len(test["questions"])
    keyboard = [
        [InlineKeyboardButton("A", callback_data="test_ans_A"),
         InlineKeyboardButton("B", callback_data="test_ans_B")],
        [InlineKeyboardButton("C", callback_data="test_ans_C"),
         InlineKeyboardButton("D", callback_data="test_ans_D")],
    ]
    await message.reply_text(
        f"📝 *Savol {idx+1}/{total}*\n\n{q['q']}\n\n{q['options']}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ============================================================
#  MATN XABARLAR — AI YORDAM
# ============================================================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    data = load_data()

    if is_teacher(user_id):
        await update.message.reply_text(
            "O'qituvchi paneli:",
            reply_markup=teacher_menu()
        )
        return

    if context.user_data.get("ai_mode"):
        context.user_data["ai_mode"] = False
        await update.message.reply_text("🤖 Savolingiz qabul qilindi, javob tayyorlanmoqda...")

        try:
            import anthropic
            client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1000,
                messages=[{
                    "role": "user",
                    "content": f"Sen matematika o'qituvchisissan. O'quvchi savol berdi. O'zbek tilida, sodda va tushunarli tushuntir, misollar kel: {text}"
                }]
            )
            answer = response.content[0].text
        except Exception as e:
            answer = f"AI hozir ishlamayapti. Keyinroq urinib ko'ring."

        await update.message.reply_text(answer, reply_markup=student_menu())
        return

    if is_student(user_id, data):
        await update.message.reply_text("Menyu:", reply_markup=student_menu())
    else:
        await update.message.reply_text(
            "Kirish uchun sinf kodini yuboring:"
        )

# ============================================================
#  ASOSIY
# ============================================================
def main():
    app = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CallbackQueryHandler(add_homework_start, pattern="^add_homework$"),
            CallbackQueryHandler(add_video_start, pattern="^add_video$"),
            CallbackQueryHandler(add_test_start, pattern="^add_test$"),
        ],
        states={
            WAIT_STUDENT_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, student_enter_code)],
            WAIT_STUDENT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, student_enter_name)],
            ADD_HOMEWORK_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_homework_title)],
            ADD_HOMEWORK_DESC: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_homework_desc)],
            ADD_HOMEWORK_DEADLINE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_homework_deadline)],
            ADD_VIDEO_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_video_title)],
            ADD_VIDEO_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_video_link)],
            ADD_VIDEO_TOPIC: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_video_topic)],
            ADD_TEST_QUESTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_test_question),
                CommandHandler("done", add_test_question),
            ],
            ADD_TEST_OPTIONS: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_test_options)],
            ADD_TEST_ANSWER: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_test_answer)],
        },
        fallbacks=[CommandHandler("start", start)],
        per_message=False,
    )

    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(teacher_callbacks, pattern="^(view_students|view_homeworks|view_videos|test_results|class_code)$"))
    app.add_handler(CallbackQueryHandler(student_callbacks, pattern="^(s_homeworks|s_videos|s_tests|s_results|s_ai|s_back|take_test_.*|test_ans_.*)$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ Bot ishga tushdi!")
    app.run_polling()

if __name__ == "__main__":
    main()
