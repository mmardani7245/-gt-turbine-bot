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

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

if not TELEGRAM_TOKEN or not OPENAI_API_KEY:
    raise ValueError("TELEGRAM_BOT_TOKEN یا OPENAI_API_KEY موجود نیست")

client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT_FA = """تو یک دستیار تخصصی در زمینه تعمیرات توربین های گازی و سیکل ترکیبی نیروگاه هستی.
تخصص های تو:
- قاب GE 9، قاب 7، MS5001
- گیربکس کمکی و تجهیزات جانبی
- تشخیص و رفع عیب
- برنامه تعمیرات و نگهداری
- برآورد هزینه ها
روش کار:
1. سوال کاربر را به دقت بخوان
2. راه حل فنی و عملی ارائه بده
3. از تجربه واقعی استفاده کن
4. همیشه ایمنی را اولویت بده"""

async def get_ai_response(user_message: str, lang: str = "fa") -> str:
    system = SYSTEM_PROMPT_FA
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_message}
            ],
            max_tokens=1024,
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"خطا: {e}"

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "سلام!\nربات دستیار تعمیرات توربین\nکمک - /help\nراهنما - /settings\n"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "مثال: GE Frame 9 چگونه تعمیر کنم؟\n\n/start - راهنما\n/help - سوالات تخصصی بپرسید"
    )

async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("فارسی", callback_data="lang_fa"),
         InlineKeyboardButton("English", callback_data="lang_en")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("زبانت را عوض کن:", reply_markup=reply_markup)

async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    lang = query.data.split("_")[1]
    context.user_data["lang"] = lang
    await query.message.reply_text("تنظیم شد")

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    lang = context.user_data.get("lang", "fa")
    await update.message.chat.send_action(action="typing")
    try:
        response = await get_ai_response(text, lang)
        if len(response) > 4096:
            for i in range(0, len(response), 4096):
                await update.message.reply_text(response[i:i+4096])
        else:
            await update.message.reply_text(response)
    except Exception as e:
        await update.message.reply_text(f"خطا: {e}")

def main() -> None:
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("settings", settings_command))
    app.add_handler(CallbackQueryHandler(language_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    logger.info("ربات شروع به کار میکند...")
  import time
    while True:
        try:
            app.run_polling(
                allowed_updates=Update.ALL_TYPES,
                drop_pending_updates=True
            )
            break
        except Exception as e:
            logger.error(f"خطا: {e}")
            time.sleep(5)
    main()
