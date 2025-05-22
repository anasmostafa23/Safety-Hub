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

    # Prompt the user to enter their full name
    await update.message.reply_text(
        "👷 Please enter your full name :"
    )


async def send_next_question(update, context, user_id):
    state = user_states[user_id]
    questions = state["template"]["categories"]

    # Flatten questions
    flat_questions = [
        q for category in questions for q in category["questions"]
    ]

    index = state["current_index"]

    if index >= len(flat_questions):
        # Detect whether update is from a message or callback
        if hasattr(update, "effective_user"):
            username = update.effective_user.username or str(user_id)
        elif hasattr(update, "from_user"):
            username = update.from_user.username or str(user_id)
        else:
            username = str(user_id)

        await context.bot.send_message(chat_id=user_id, text="✅ Audit complete! Generating PDF...")
        full_name = state.get("full_name", str(user_id))
        pdf_path = generate_pdf(
            username=full_name,
            template=state["template"],
            responses=state["responses"],
            site_id= state.get("site_id", "Unknown")

        )

        await context.bot.send_document(chat_id=user_id, document=open(pdf_path, "rb")) 
        
        await context.bot.send_message(chat_id=user_id, text="use /start to start a new audit")

        user_states.pop(user_id, None)
        return

    q = flat_questions[index]
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(opt, callback_data=opt)] for opt in q["options"]
    ])

    await context.bot.send_message(
        chat_id=user_id,
        text=f"Q{index + 1}: {q['question_en']}\n\n🇷🇺 {q['question_ru']}",
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

    selected_option = query.data
    state["responses"].append(selected_option)
    state["current_index"] += 1

    await send_next_question(query, context, user_id)

# handlers/audit.py

async def handle_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    message = update.message.text.strip()
    state = user_states.get(user_id)

    if not state:
        await update.message.reply_text("Session expired. Please /start again.")
        return

    # Step 1: Get full name
    if state.get("awaiting_name"):
        state["full_name"] = message
        state["awaiting_name"] = False
        state["awaiting_site_id"] = True
        await update.message.reply_text("📍 Now enter the Site ID:")
        return

    # Step 2: Get Site ID
    if state.get("awaiting_site_id"):
        state["site_id"] = message
        state["awaiting_site_id"] = False

        # Load the audit template
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

    # Otherwise, fallback
    await update.message.reply_text("Please use the buttons to respond.")
