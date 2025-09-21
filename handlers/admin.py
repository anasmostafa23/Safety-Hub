# handlers/admin.py
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.audit_parser import parse_audit_pdf_openai
from database.models import Audit
from database.db import Session as SessionLocal

ADMIN_IDS = [6015506522]  # <-- replace with real admin Telegram IDs

def is_admin(user_id):
    return user_id in ADMIN_IDS

async def upload_audit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("⛔ You are not authorized to upload audits.")
        return
    await update.message.reply_text("📄 Please send the PDF/DOCX file for the new audit.")

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        return

    document = update.message.document
    file = await document.get_file()
    os.makedirs("uploads", exist_ok=True)
    file_path = os.path.join("uploads", document.file_name)
    await file.download_to_drive(file_path)

    await update.message.reply_text("🔄 Processing file with OpenAI... this may take a moment.")
    checklist = parse_audit_pdf_openai(file_path)

    if not checklist:
        await update.message.reply_text("❌ Failed to process audit. Try again.")
        return

    # Save to DB
    session = SessionLocal()
    audit = Audit(
        title=checklist.get("template_name", "Untitled Audit"),
        file_path=file_path,
        parsed_json=checklist,
        created_by=str(user_id),
        is_active=False
    )
    session.add(audit)
    session.commit()
    session.close()

    keyboard = [[
        InlineKeyboardButton("✅ Activate", callback_data=f"activate_audit_{audit.id}"),
        InlineKeyboardButton("❌ Keep Inactive", callback_data="noop")
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(f"✅ Audit saved: {audit.title}\nActivate now?", reply_markup=reply_markup)
