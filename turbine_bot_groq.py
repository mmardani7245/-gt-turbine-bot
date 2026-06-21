#!/usr/bin/env python3
"""
🔧 TURBINE REPAIR ASSISTANT BOT - OpenAI Version
ربات دستیار تعمیرات توربین گازی و سیکل ترکیبی
"""

import os
import logging
import asyncio
from typing import Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
    CallbackQueryHandler,
)
import aiohttp
from openai import OpenAI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not TELEGRAM_TOKEN or not OPENAI_API_KEY:
    raise ValueError("❌ مفقود: TELEGRAM_BOT_TOKEN یا OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT_FA = """تو یک متخصص صنعتی در زمینه تعمیرات توربین‌های گازی و سیکل‌های ترکیبی نیروگاه هستی.

تخصص‌های تو:
🔧 GE Frame 9, Frame 7, MS5001
⚙️ گیربکس کمکی و تجهیزات جانبی
🔍 تشخیص و رفع عیوب
📋 برنامه تعمیرات و نگهداری
💰 برآورد هزینه‌ها

روش کار:
1. سوال کاربر را به دقت بخوان
2. راه‌حل فنی و عملی ارائه بده
3. از تجربه واقعی استفاده کن
4. همیشه ایمنی را اولویت بده"""

SYSTEM_PROMPT_EN = """You are an expert in Gas Turbine repair and maintenance.
Expertise: GE Frame 9, 7, MS5001, Auxiliary equipment, troubleshooting, maintenance planning, cost estimation."""

async def search_web(query: str) -> str:
    """جستجوی اینترنت"""
    try:
        search_url = f"https://api.duckduckgo.com/?q={query}&format=json"
        async with aiohttp.ClientSession() as session:
            async with session.get(search_url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    results = data.get("Results", [])[:3]
                    if results:
                        return "🔍 نتایج جستجو:\n" + "\n".join([f"{i}. {r.get('Title', '')}" for i, r in enumerate(results, 1)])
    except:
        pass
    return ""

def get_openai_response(user_message: str, language: str = "fa") -> str:
    """دریافت پاسخ از OpenAI"""
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
        return f"❌ خطا: {str(e)}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """دستور شروع"""
    await update.message.reply_text("""
سلام! 👋

🔧 ربات دستیار تعمیرات توربین

/help - راهنما
/settings - تنظیمات

سوال خود را بنویسید!
""")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """راهنما"""
    await update.message.reply_text("""
📖 راهنما

سوالات تفصیلی بپرسید!
مثال: "GE Frame 9 رو چطور تعمیر کنم؟"

/start - شروع
/help - کمک
/settings - تنظیمات
""")

async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """تنظیمات"""
    keyboard = [
        [InlineKeyboardButton("🇮🇷 فارسی", callback_data="lang_fa"),
         InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")]
    ]
    await update.message.reply_text("زبان انتخاب کن:", reply_markup=InlineKeyboardMarkup(keyboard))

async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """تنظیم زبان"""
    query = update.callback_query
    lang = query.data.split("_")[1]
    context.user_data["language"] = lang
    await query.answer("✅ تنظیم شد")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """پردازش پیام‌ها"""
    user_message = update.message.text
    language = context.user_data.get("language", "fa")
    
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    try:
        response = get_openai_response(user_message, language)
        
        if len(response) > 4096:
            for chunk in [response[i:i+4096] for i in range(0, len(response), 4096)]:
                await update.message.reply_text(chunk, parse_mode="Markdown")
        else:
            await update.message.reply_text(response, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ خطا: {str(e)}")

async def main():
    """راه‌اندازی ربات"""
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("settings", settings_command))
    app.add_handler(CallbackQueryHandler(language_callback, pattern="^lang_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("🚀 ربات شروع می‌شود...") app.run_polling(allowed_updates=Update.ALL_TYPES)
app.run_polling(allowed_updates=Update.ALL_TYPES)
main()
