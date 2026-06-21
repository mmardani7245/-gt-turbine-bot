

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

def main():
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
