
from telegram import Update
from telegram.ext import ContextTypes 

async def my_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(f"👤 Your Telegram ID: `{user.id}`", parse_mode="Markdown")