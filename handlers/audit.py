from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.template_loader import load_template
from utils.pdf_generator import generate_pdf
from database.db import upsert_user, create_audit, save_responses
from database.models import Session , init_db


# In-memory user state
user_states = {}

def get_flat_questions(template):
    return [q for cat in template["categories"] for q in cat["questions"]]

async def start_audit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_states[user_id] = {"awaiting_name": True}
    await update.message.reply_text("👷 Please enter your full name:")

def build_question_keyboard(question, selected_answer, current_index, total_questions):
    option_buttons = [
        InlineKeyboardButton(
            f"{'✅ ' if opt == selected_answer else ''}{opt}",
            callback_data=f"answer:{opt}"
        ) for opt in question["options"]
    ]

    nav_buttons = []
    if current_index > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Previous", callback_data="nav:prev"))

    if current_index < total_questions - 1:
        if selected_answer:
            nav_buttons.append(InlineKeyboardButton("➡️ Next", callback_data="nav:next"))
    else:
        # Always show the generate button on the last question
        if selected_answer:
            nav_buttons.append(InlineKeyboardButton("Generate Report", callback_data="generate"))


    return InlineKeyboardMarkup([
        option_buttons,
        nav_buttons
    ])

async def send_next_question(update, context, user_id):
    state = user_states[user_id]
    flat_questions = get_flat_questions(state["template"])
    index = state["current_index"]

    if index >= len(flat_questions):
        # Save responses to DB
        full_name = state.get("full_name", str(user_id))
        site_id = state.get("site_id", "Unknown")
        template_name = state.get("template_name", "Unknown Template")  # ✅ Get template name
        
        upsert_user(user_id, full_name, site_id)
        
        # ✅ Pass template title when creating audit
        audit_id = create_audit(
            telegram_id=user_id, 
            site_id=site_id,
            title=template_name  # ✅ KEY FIX: Store template name
        )
        save_responses(audit_id, state["template"], state["responses"])

        await context.bot.send_message(chat_id=user_id, text="✅ Audit complete! Generating PDF...")
        pdf_path = generate_pdf(
            username=full_name,
            template=state["template"],
            responses=state["responses"],
            site_id=site_id
        )
        with open(pdf_path, "rb") as pdf_file:
            await context.bot.send_document(chat_id=user_id, document=pdf_file)
        await context.bot.send_message(chat_id=user_id, text="Use /start to start a new audit.")
        user_states.pop(user_id, None)
        return

    q = flat_questions[index]
    selected_answer = state["responses"][index] if index < len(state["responses"]) else None
    total_questions = len(flat_questions)

    keyboard = build_question_keyboard(
        question=q,
        selected_answer=selected_answer,
        current_index=index,
        total_questions=total_questions
    )

    question_text = f"Q{index + 1} of {total_questions}: {q['question_en']}\n\n {q['question_ru']}"

    try:
        if "last_message_id" in state:
            await context.bot.edit_message_text(
                chat_id=user_id,
                message_id=state["last_message_id"],
                text=question_text,
                reply_markup=keyboard
            )
            return
    except Exception:
        try:
            await context.bot.delete_message(chat_id=user_id, message_id=state["last_message_id"])
        except:
            pass

    msg = await context.bot.send_message(chat_id=user_id, text=question_text, reply_markup=keyboard)
    state["last_message_id"] = msg.message_id

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
    flat_questions = get_flat_questions(state["template"])

    if data.startswith("answer:"):
        answer = data.split("answer:")[1]

        if len(state["responses"]) <= index:
            state["responses"] += [None] * (index - len(state["responses"]) + 1)

        state["responses"][index] = answer
        state["current_index"] += 1
        await send_next_question(query, context, user_id)

    elif data == "nav:next":
        state["current_index"] += 1
        await send_next_question(query, context, user_id)

    elif data == "nav:prev":
        if index > 0:
            state["current_index"] -= 1
            await send_next_question(query, context, user_id)
        else:
            await query.answer("This is the first question.", show_alert=True)

    elif data == "generate":
        state["current_index"] += 1
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

        # ✅ Load template and extract template name
        template = load_template()
        template_name = template.get("template_name", "Unknown Template")  # ✅ KEY FIX
        
        state.update({
            "template": template,
            "template_name": template_name,  # ✅ Store template name in state
            "current_index": 0,
            "responses": []
        })

        await update.message.reply_text(
            f"✅ Thanks, {state['full_name']}!\n📄 Starting audit for Site ID: {state['site_id']}\n📋 Template: {template_name}"
        )
        await send_next_question(update, context, user_id)
        return

    await update.message.reply_text("Please use the buttons to respond.")