# handlers/admin.py
import os
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, MessageHandler, filters, CommandHandler
from utils.audit_parser import parse_audit_pdf_openai
from utils.template_manager import get_available_templates, set_active_template, get_active_template, get_template_info

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
    user_id = update.effective_user.id

    # Only process if admin AND pending_checklist is present
    if not (is_admin(user_id) and "pending_checklist" in context.user_data):
        # Do nothing, let the message fall through to the next handler
        return

    checklist = context.user_data.pop("pending_checklist")
    user_input_name = update.message.text.strip()
    safe_title = user_input_name.replace(" ", "_")

    os.makedirs("templates", exist_ok=True)
    json_path = os.path.join("templates", f"{safe_title}.json")

    if os.path.exists(json_path):
        await update.message.reply_text(f"⚠️ A template named *{safe_title}* already exists. Choose another name.")
        return

    checklist["template_name"] = safe_title  # ✅ ensure name stored in JSON
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(checklist, f, ensure_ascii=False, indent=2)

    await update.message.reply_text(
        f"✅ Template saved as *{safe_title}*.\nYou can activate it later.",
        parse_mode="Markdown"
    )


async def list_templates(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all available templates for admin selection."""
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("⛔ You are not authorized to manage templates.")
        return

    templates = get_available_templates()

    if not templates:
        await update.message.reply_text("📋 No templates found.\n\nPlease upload an audit file first using /upload_audit")
        return

    # Get current active template
    active_template = get_active_template()
    active_filename = None
    if active_template:
        # Find the filename of the active template
        for template in templates:
            try:
                with open(template['filepath'], 'r', encoding='utf-8') as f:
                    template_data = json.load(f)
                    if template_data.get('template_name') == active_template.get('template_name'):
                        active_filename = template['filename']
                        break
            except:
                continue

    message = "📋 **Available Templates:**\n\n"
    for template in templates:
        status = "✅ ACTIVE" if template['filename'] == active_filename else ""
        message += f"📄 *{template['name']}*\n"
        message += f"   📊 Categories: {template['categories_count']} | Questions: {template['questions_count']}\n"
        message += f"   📁 File: `{template['filename']}`"
        if status:
            message += f" {status}"
        message += "\n\n"

    message += "Use `/select_template <filename>` to activate a template"

    await update.message.reply_text(message, parse_mode="Markdown")

async def select_template(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Select and activate a template by filename."""
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("⛔ You are not authorized to manage templates.")
        return

    if not context.args:
        await update.message.reply_text("❌ Please provide a template filename.\n\nUse `/list_templates` to see available templates.")
        return

    template_filename = context.args[0]
    success = set_active_template(template_filename)

    if success:
        # Get template info for confirmation
        template_info = get_template_info(template_filename)
        if template_info:
            await update.message.reply_text(
                f"✅ Template activated successfully!\n\n"
                f"📄 *{template_info['name']}*\n"
                f"📊 Categories: {template_info['categories_count']} | Questions: {template_info['questions_count']}\n\n"
                f"All new audits will now use this template.",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text("✅ Template activated successfully!")
    else:
        await update.message.reply_text(
            f"❌ Failed to activate template '{template_filename}'.\n\n"
            f"Use `/list_templates` to see available templates."
        )

async def current_template(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show the currently active template."""
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("⛔ You are not authorized to view template information.")
        return

    active_template = get_active_template()

    if not active_template:
        await update.message.reply_text(
            "⚠️ No active template set.\n\n"
            "Use `/list_templates` to see available templates, then use `/select_template <filename>` to activate one."
        )
        return

    template_name = active_template.get('template_name', 'Unknown')
    categories_count = len(active_template.get('categories', []))
    questions_count = sum(len(cat.get('questions', [])) for cat in active_template.get('categories', []))

    await update.message.reply_text(
        "📋 **Currently Active Template:**\n\n"
        f"📄 *{template_name}*\n"
        f"📊 Categories: {categories_count} | Questions: {questions_count}\n\n"
        "Use `/list_templates` to see all available templates.",
        parse_mode="Markdown"
    )
