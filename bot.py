# safetyhub_bot/bot.py
import os
from dotenv import load_dotenv
from database.models import Session, init_db

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

import logging
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, CallbackQueryHandler
)

from handlers.audit import start_audit, handle_response, button_click
from handlers.admin import upload_audit, handle_document, handle_template_name
from utils.utils import my_id

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start_audit))
    app.add_handler(CommandHandler("myid", my_id))
    app.add_handler(CommandHandler("upload_audit", upload_audit))

    # Callbacks
    app.add_handler(CallbackQueryHandler(button_click))

    # Document upload (admin)
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))

    # ✅ NEW: Admin template name input (must be above handle_response)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_template_name))

    # Fallback for other user text (audit answers)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_response))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
