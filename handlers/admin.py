# handlers/admin.py
import os
import json
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from utils.audit_parser import parse_audit_pdf_openai

ADMIN_IDS = [6015506522]  # replace with real admin Telegram IDs

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

    # ✅ Store checklist temporarily and ask for a name
    context.user_data["pending_checklist"] = checklist
    await update.message.reply_text("✏️ Please enter a name for this audit template:")

async def handle_template_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the admin's reply with the template name."""
    if "pending_checklist" not in context.user_data:
        await update.message.reply_text("⚠️ No checklist waiting to be named. Please upload a file first.")
        return

    checklist = context.user_data.pop("pending_checklist")
    user_input_name = update.message.text.strip()
    safe_title = user_input_name.replace(" ", "_")

    # ✅ Save to templates folder
    os.makedirs("templates", exist_ok=True)
    json_path = os.path.join("templates", f"{safe_title}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(checklist, f, ensure_ascii=False, indent=2)

    await update.message.reply_text(f"✅ Template saved as *{safe_title}*.\nYou can activate it later.", parse_mode="Markdown")
