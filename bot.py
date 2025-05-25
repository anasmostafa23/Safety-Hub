# safetyhub_bot/bot.py
import os
from dotenv import load_dotenv
from database.models import Session , init_db # ✅ same session everywhere
#init_db()

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")


import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ContextTypes, CallbackQueryHandler
)

from handlers.audit import start_audit, handle_response, button_click

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Command handlers
    app.add_handler(CommandHandler("start", start_audit))

    # Callback for inline buttons
    app.add_handler(CallbackQueryHandler(button_click))

    # Fallback for text inputs (if you later support open-ended responses)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_response))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
