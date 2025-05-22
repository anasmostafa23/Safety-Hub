# safetyhub_bot/handlers/audit.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.template_loader import load_template
from utils.pdf_generator import generate_pdf

# In-memory user state
user_states = {}

async def start_audit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # Mark that we're waiting for the user's full name
    user_states[user_id] = {
        "awaiting_name": True
    }

    await update.message.reply_text("👷 Please enter your full name :")

def build_question_keyboard(question, answered, current_index):
    option_buttons = [
        InlineKeyboardButton(opt, callback_data=f"answer:{opt}") for opt in question["options"]
    ]

    nav_buttons = []
    if current_index > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Previous", callback_data="nav:prev"))
    if answered:
        nav_buttons.append(InlineKeyboardButton("➡️ Next", callback_data="nav:next"))

    keyboard = InlineKeyboardMarkup([option_buttons, nav_buttons])
    return keyboard

async def send_next_question(update, context, user_id):
    state = user_states[user_id]
    questions = state["template"]["categories"]
    flat_questions = [q for category in questions for q in category["questions"]]
    index = state["current_index"]

    if index >= len(flat_questions):
        username = (
            update.effective_user.username
            if hasattr(update, "effective_user") else update.from_user.username
        ) or str(user_id)

        await context.bot.send_message(chat_id=user_id, text="✅ Audit complete! Generating PDF...")

        pdf_path = generate_pdf(
            username=state.get("full_name", str(user_id)),
            template=state["template"],
            responses=state["responses"],
            site_id=state.get("site_id", "Unknown")
        )

        await context.bot.send_document(chat_id=user_id, document=open(pdf_path, "rb"))
        await context.bot.send_message(chat_id=user_id, text="Use /start to start a new audit.")
        user_states.pop(user_id, None)
        return

    q = flat_questions[index]
    answer = state["responses"][index] if index < len(state["responses"]) else None
    keyboard = build_question_keyboard(q, answered=bool(answer), current_index=index)

    answer_text = f"\n📝 Current answer: {answer}" if answer else ""
    await context.bot.send_message(
        chat_id=user_id,
        text=f"Q{index + 1}: {q['question_en']}\n\n🇷🇺 {q['question_ru']}{answer_text}",
        reply_markup=keyboard
    )

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    state = user_states.get(user_id)
    if not state:
        await query.edit_message_text("Session expired. Please /start again.")
        return

    data = query.data
    index = state["current_index"]

    if data.startswith("answer:"):
        answer = data.split("answer:")[1]

        # Ensure responses list is long enough
        if len(state["responses"]) <= index:
            state["responses"] += [None] * (index - len(state["responses"]) + 1)

        state["responses"][index] = answer

        # Rebuild keyboard with nav buttons
        flat_questions = [q for cat in state["template"]["categories"] for q in cat["questions"]]
        q = flat_questions[index]
        keyboard = build_question_keyboard(q, answered=True, current_index=index)

        # Edit message instead of sending new one
        await query.edit_message_text(
            text=f"Q{index + 1}: {q['question_en']}\n\n🇷🇺 {q['question_ru']}\n\n📝 Selected: {answer}",
            reply_markup=keyboard
        )

    elif data == "nav:next":
        state["current_index"] += 1
        await send_next_question(query, context, user_id)

    elif data == "nav:prev":
        state["current_index"] -= 1
        await send_next_question(query, context, user_id)


async def handle_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    message = update.message.text.strip()
    state = user_states.get(user_id)

    if not state:
        await update.message.reply_text("Session expired. Please /start again.")
        return

    if state.get("awaiting_name"):
        state["full_name"] = message
        state["awaiting_name"] = False
        state["awaiting_site_id"] = True
        await update.message.reply_text("📍 Now enter the Site ID:")
        return

    if state.get("awaiting_site_id"):
        state["site_id"] = message
        state["awaiting_site_id"] = False

        template = load_template()
        state.update({
            "template": template,
            "current_index": 0,
            "responses": []
        })

        await update.message.reply_text(
            f"✅ Thanks, {state['full_name']}!\n📄 Starting audit for Site ID: {state['site_id']}"
        )
        await send_next_question(update, context, user_id)
        return

    await update.message.reply_text("Please use the buttons to respond.")
