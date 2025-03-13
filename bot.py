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

# Веса ответов
WEIGHTS = {
    # Вопрос 1: Как вы представляете свой идеальный отдых?
    "1_a": {"city_center": 3},
    "1_b": {"business_area": 2},
    "1_c": {"business_area": 1, "nature": 1},
    "1_d": {"nature": 3},

    # Вопрос 2: Какой тип отдыха вы предпочитаете?
    "2_a": {"city_center": 2, "business_area": 1},
    "2_b": {"nature": 2},
    "2_c": {"city_center": 1, "business_area": 1},
    "2_d": {"nature": 2},

    # Вопрос 3: Какие условия проживания вы предпочитаете?
    "3_a": {"city_center": 3},
    "3_b": {"business_area": 2},
    "3_c": {"nature": 1},
    "3_d": {"nature": 3},

    # Остальные вопросы...
}

# Словарь для хранения ответов пользователя
user_answers = {}

# Начало теста
async def start(update: Update, context: CallbackContext) -> int:
    keyboard = [
        [InlineKeyboardButton("Начать тест", callback_data="start_quiz")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🌍 Добро пожаловать! Этот тест поможет найти идеальный отель для вашего отдыха.\n"
        "Нажмите кнопку ниже, чтобы начать.",
        reply_markup=reply_markup
    )
    return QUESTION_1

# Универсальная функция для обработки вопросов
async def handle_question(update: Update, context: CallbackContext, question_id: int) -> int:
    query = update.callback_query
    await query.answer()

    # Сохраняем ответ пользователя
    user_answers[question_id] = query.data

    # Переходим к следующему вопросу
    next_question_id = question_id + 1
    if next_question_id > 8:
        return await result(update, context)

    # Отправляем следующий вопрос
    text = f"Вопрос {next_question_id}: ..."
    keyboard = [
        [InlineKeyboardButton("Вариант 1", callback_data=f"{next_question_id}_a")],
        [InlineKeyboardButton("Вариант 2", callback_data=f"{next_question_id}_b")],
        [InlineKeyboardButton("Вариант 3", callback_data=f"{next_question_id}_c")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=text, reply_markup=reply_markup)
    return next_question_id

# Функция анализа результатов
async def result(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()

    # Подсчет баллов
    scores = {"city_center": 0, "business_area": 0, "nature": 0}
    for answer in user_answers.values():
        if answer in WEIGHTS:
            for category, weight in WEIGHTS[answer].items():
                scores[category] += weight

    # Выбор победителя
    max_category = max(scores, key=scores.get)
    if max_category == "city_center":
        hotel = "Китай-город"
        url = "https://norke.ru/hotel1"
    elif max_category == "business_area":
        hotel = "Сретенская/Курская"
        url = "https://norke.ru/hotel2"
    else:
        hotel = "Глэмпинг"
        url = "https://norke.ru/glamping"

    # Отправляем результат
    keyboard = [
        [InlineKeyboardButton("Забронировать этот вариант", url=url)],
        [InlineKeyboardButton("Посмотреть другие варианты", url="https://norke.ru")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=f"🎉 Поздравляем! Ваш идеальный вариант - {hotel}.\n"
             f"Мы подготовили специальное предложение специально для вас!",
        reply_markup=reply_markup
    )
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
            QUESTION_1: [CallbackQueryHandler(lambda u, c: handle_question(u, c, 1))],
            QUESTION_2: [CallbackQueryHandler(lambda u, c: handle_question(u, c, 2))],
            QUESTION_3: [CallbackQueryHandler(lambda u, c: handle_question(u, c, 3))],
            QUESTION_4: [CallbackQueryHandler(lambda u, c: handle_question(u, c, 4))],
            QUESTION_5: [CallbackQueryHandler(lambda u, c: handle_question(u, c, 5))],
            QUESTION_6: [CallbackQueryHandler(lambda u, c: handle_question(u, c, 6))],
            QUESTION_7: [CallbackQueryHandler(lambda u, c: handle_question(u, c, 7))],
            QUESTION_8: [CallbackQueryHandler(lambda u, c: handle_question(u, c, 8))],
            RESULT: [CallbackQueryHandler(result)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        per_message=False,
        per_chat=True,
        per_user=True
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
