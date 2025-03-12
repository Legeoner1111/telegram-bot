# -*- coding: utf-8 -*-
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    CallbackContext,
)

# Создаем Flask-приложение
app = Flask(__name__)

# Токен твоего бота
TOKEN = "7575514249:AAEZd9zzOQKTJdRcwu9kgSG3SF0-7HQpa5k"

# Состояния диалога
QUESTION_1, QUESTION_2, QUESTION_3, QUESTION_4, QUESTION_5, QUESTION_6, QUESTION_7, QUESTION_8, RESULT = range(9)

# Словарь для хранения ответов пользователя
user_answers = {}

# Начало теста
async def start(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("Начать тест", callback_data="start_quiz")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        "Добро пожаловать! Этот тест поможет найти идеальный отель для вашего отдыха.\n"
        "Нажмите кнопку ниже, чтобы начать.",
        reply_markup=reply_markup
    )
    return QUESTION_1

# Остальные функции остаются без изменений...

# Маршрут для вебхука
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.process_update(update)
    return "OK"

# Запуск сервера
if __name__ == "__main__":
    # Инициализация Application
    application = Application.builder().token(TOKEN).build()

    # Добавление обработчиков
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(start, pattern="^start_quiz$")],  # Заменяем CommandHandler
        states={
            QUESTION_1: [CallbackQueryHandler(question_1)],
            QUESTION_2: [CallbackQueryHandler(question_2)],
            QUESTION_3: [CallbackQueryHandler(question_3)],
            QUESTION_4: [CallbackQueryHandler(question_4)],
            QUESTION_5: [CallbackQueryHandler(question_5)],
            QUESTION_6: [CallbackQueryHandler(question_6)],
            QUESTION_7: [CallbackQueryHandler(question_7)],
            QUESTION_8: [CallbackQueryHandler(question_8)],
            RESULT: [CallbackQueryHandler(result)],
        },
        fallbacks=[CallbackQueryHandler(cancel, pattern="^cancel$")],  # Заменяем CommandHandler
        per_message=True,  # Устанавливаем True
        per_chat=True,
        per_user=True
    )
    application.add_handler(conv_handler)

    # Публичный URL от Render
    render_url = "https://telegram-bot-d8rq.onrender.com"  # Замени на свой реальный Render URL

    # Установка вебхука
    application.run_webhook(
        listen="0.0.0.0",
        port=8080,
        url_path=TOKEN,
        webhook_url=f"{render_url}/{TOKEN}"
    )
