
#!/usr/bin/env python3
"""
TURBINE REPAIR ASSISTANT BOT - OpenAI Version
ربات دستیار تعمیرات توربین گازی و سیکل ترکیبی
"""

import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
    CallbackQueryHandler,
)
from openai import OpenAI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not TELEGRAM_TOKEN or not OPENAI_API_KEY:
    raise ValueError("Missing TELEGRAM_BOT_TOKEN or OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT_FA = """تو یک متخصص صنعتی در زمینه تعمیرات توربین های گازی و سیکل های ترکیبی نیروگاه هستی.

تخصص های تو:
GE Frame 9, Frame 7, MS5001
گیربکس کمکی و تجهیزات جانبی
تشخیص و رفع عیوب
برنامه تعمیرات و نگهداری
براورد هزینه ها

روش کار:
1. سوال کاربر را به دقت بخوان
2. راه حل فنی و عملی ارائه بده
3. از تجربه واقعی استفاده کن
4. همیشه ایمنی را اولویت بده"""

SYSTEM_PROMPT_EN = """You are an expert in Gas Turbine repair and maintenance.
Expertise: GE Frame 9, 7, MS5001, Auxiliary equipment, troubleshooting, maintenance planning, cost estimation."""

def get_openai_response(user_message: str, language: str = "fa") -> str:
    system = SYSTEM_PROMPT_FA if language == "fa" else SYSTEM_PROMPT_EN
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_message}
            ],
            max_tokens=1024,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "سلام!\n\nربات دستیار تعمیرات توربین\n\n/help - راهنما\n/settings - تنظیمات\n\nسوال خود را بنویسید!"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "راهنما\n\nسوالات تفصیلی بپرسید!\nمثال: GE Frame 9 رو چطور تعمیر کنم؟\n\n/start - شروع\n/help - کمک\n/settings - تنظیمات"
    )

async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("فارسی", callback_data="lang_fa"),
         InlineKeyboardButton("English", callback_data="lang_en")]
    ]
    await update.message.reply_text("زبان انتخاب کن:", reply_markup=InlineKeyboardMarkup(keyboard))

async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    lang = query.data.split("_")[1]
    context.user_data["language"] = lang
    await query.answer("تنظیم شد")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text
    language = context.user_data.get("language", "fa")
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    try:
        response = get_openai_response(user_message, language)
        if len(response) > 4096:
            for i in range(0, len(response), 4096):
                await update.message.reply_text(response[i:i+4096])
        else:
            await update.message.reply_text(response)
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("settings", settings_command))
    app.add_handler(CallbackQueryHandler(language_callback, pattern="^lang_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("Bot is starting...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
