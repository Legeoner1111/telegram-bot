# -*- coding: utf-8 -*-
import os  # Импортируем модуль os
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
    keyboard = [
        [InlineKeyboardButton("Начать тест", callback_data="start_quiz")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Добро пожаловать! Этот тест поможет найти идеальный отель для вашего отдыха.\n"
        "Нажмите кнопку ниже, чтобы начать.",
        reply_markup=reply_markup
    )
    return QUESTION_1

async def question_1(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    user_answers[1] = query.data  # Сохраняем ответ пользователя
    keyboard = [
        [InlineKeyboardButton("В самом сердце исторического центра (Китай-город)", callback_data="1_a")],
        [InlineKeyboardButton("В деловом районе с удобным транспортным сообщением (Курская/Сретенская)", callback_data="1_b")],
        [InlineKeyboardButton("В спокойном месте с парковыми зонами поблизости (Бауманская/Менделеевская)", callback_data="1_c")],
        [InlineKeyboardButton("На природе с полным погружением в экологичную среду (Глэмпинг)", callback_data="1_d")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text="Как вы представляете свой идеальный отдых?",
        reply_markup=reply_markup
    )
    return QUESTION_2

async def question_2(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    user_answers[2] = query.data  # Сохраняем ответ пользователя
    keyboard = [
        [InlineKeyboardButton("Активный отдых (экскурсии, прогулки)", callback_data="2_a")],
        [InlineKeyboardButton("Спокойный отдых (чтение книг, медитация)", callback_data="2_b")],
        [InlineKeyboardButton("Семейный отдых (с детьми, активности для всей семьи)", callback_data="2_c")],
        [InlineKeyboardButton("Романтический отдых (для двоих)", callback_data="2_d")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text="Какой тип отдыха вы предпочитаете?",
        reply_markup=reply_markup
    )
    return QUESTION_3

# Остальные функции остаются без изменений...

async def result(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    user_answers[8] = query.data
    # Анализ ответов
    answers = list(user_answers.values())
    if answers.count("1_a") + answers.count("2_a") + answers.count("3_a") > 4:
        hotel = "Китай-город"
        url = "https://norke.ru/hotel1"
    elif answers.count("1_b") + answers.count("2_b") + answers.count("7_a") > 4:
        hotel = "Сретенская/Курская"
        url = "https://norke.ru/hotel2"
    elif answers.count("1_c") + answers.count("2_c") + answers.count("3_c") > 4:
        hotel = "Бауманская/Первомайская"
        url = "https://norke.ru/hotel3"
    else:
        hotel = "Глэмпинг"
        url = "https://norke.ru/glamping"
    keyboard = [
        [InlineKeyboardButton("Забронировать этот вариант", url=url)],
        [InlineKeyboardButton("Посмотреть другие варианты", url="https://norke.ru")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=f"Поздравляем! Ваш идеальный вариант - {hotel}.\n"
             f"Мы подготовили специальное предложение специально для вас!",
        reply_markup=reply_markup
    )
    return ConversationHandler.END

async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("Тест завершен. Если хотите повторить, нажмите /start.")
    return ConversationHandler.END

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
        entry_points=[CommandHandler('start', start)],
        states={
            QUESTION_1: [CallbackQueryHandler(question_1)],
            QUESTION_2: [CallbackQueryHandler(question_2)],  # Исправлено название функции
            QUESTION_3: [CallbackQueryHandler(question_3)],
            QUESTION_4: [CallbackQueryHandler(question_4)],
            QUESTION_5: [CallbackQueryHandler(question_5)],
            QUESTION_6: [CallbackQueryHandler(question_6)],
            QUESTION_7: [CallbackQueryHandler(question_7)],
            QUESTION_8: [CallbackQueryHandler(question_8)],
            RESULT: [CallbackQueryHandler(result)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        per_message=False,  # Явно указываем параметр
        per_chat=True,      # Отслеживаем состояние для каждого чата
        per_user=True       # Отслеживаем состояние для каждого пользователя
    )
    application.add_handler(conv_handler)

    # Публичный URL от Render
    render_url = "https://telegram-bot-d8rq.onrender.com"  # Замени на свой реальный Render URL

    # Установка вебхука
    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8080)),  # Используем порт из переменной окружения
        url_path=TOKEN,
        webhook_url=f"{render_url}/{TOKEN}"  # Полный URL для вебхука
    )

    # Запуск Flask-сервера
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))  # Используем порт из переменной окружения
