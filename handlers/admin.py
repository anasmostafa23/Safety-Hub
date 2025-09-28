# handlers/admin.py
import os
import json
import uuid
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.audit_parser import parse_audit_pdf_openai
from database.models import Audit
from database.db import Session as SessionLocal

ADMIN_IDS = [6015506522]  # Replace with your real admin IDs

def is_admin(user_id):
    return user_id in ADMIN_IDS


async def upload_audit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("⛔ You are not authorized to upload audits.")
        return

    context.user_data.clear()
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

    await update.message.reply_text("🔄 Processing file with OpenAI... please wait.")
    checklist = parse_audit_pdf_openai(file_path)

    if not checklist:
        await update.message.reply_text("❌ Failed to parse audit file. Try again.")
        return

    # Store for next step
    context.user_data["parsed_checklist"] = checklist
    context.user_data["uploaded_file"] = file_path

    await update.message.reply_text("✏️ Please enter a title for this audit.")


async def handle_audit_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        return

    title = update.message.text
    checklist = context.user_data.get("parsed_checklist")

    if not checklist:
        await update.message.reply_text("❌ No checklist found. Please start over with /upload_audit.")
        return

    # Save checklist to templates folder
    os.makedirs("templates", exist_ok=True)
    template_filename = f"{uuid.uuid4().hex}.json"
    template_path = os.path.join("templates", template_filename)

    with open(template_path, "w", encoding="utf-8") as f:
        json.dump(checklist, f, ensure_ascii=False, indent=2)

    session = SessionLocal()
    audit = Audit(
        title=title,
        template_path=template_path,
        is_active=False  # admin will activate manually
    )
    session.add(audit)
    session.commit()
    session.refresh(audit)
    session.close()

    keyboard = [[
        InlineKeyboardButton("✅ Activate", callback_data=f"activate_audit_{audit.id}"),
        InlineKeyboardButton("❌ Keep Inactive", callback_data="noop")
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"✅ Audit saved: {audit.title}\nActivate now?",
        reply_markup=reply_markup
    )


async def handle_audit_activation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle audit activation callback"""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    if not is_admin(user_id):
        await query.edit_message_text("⛔ You are not authorized to activate audits.")
        return

    # Parse audit ID from callback data
    callback_data = query.data
    if not callback_data.startswith("activate_audit_"):
        return

    try:
        audit_id = int(callback_data.split("activate_audit_")[1])
    except (ValueError, IndexError):
        await query.edit_message_text("❌ Invalid audit ID.")
        return

    # Update audit status in database
    session = SessionLocal()
    audit = session.query(Audit).filter_by(id=audit_id).first()

    if not audit:
        session.close()
        await query.edit_message_text("❌ Audit not found.")
        return

    # Deactivate all other audits first
    session.query(Audit).update({"is_active": False})
    audit.is_active = True
    session.commit()
    session.close()

    await query.edit_message_text(
        f"✅ Audit '{audit.title}' has been activated!\n"
        "Users can now start this audit with /start"
    )
