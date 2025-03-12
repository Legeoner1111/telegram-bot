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
STEPS = range(9)

# Конфигурация вопросов и вариантов ответов
QUESTIONS = {
    0: {
        "text": "Как вы представляете свой идеальный отдых?",
        "options": [
            ("В самом сердце исторического центра (Китай-город)", "1_a"),
            ("В деловом районе с удобным транспортным сообщением (Курская/Сретенская)", "1_b"),
            ("В спокойном месте с парковыми зонами поблизости (Бауманская/Менделеевская)", "1_c"),
            ("На природе с полным погружением в экологичную среду (Глэмпинг)", "1_d"),
        ],
    },
    1: {
        "text": "Какой тип отдыха вы предпочитаете?",
        "options": [
            ("Активный отдых (экскурсии, прогулки)", "2_a"),
            ("Спокойный отдых (чтение книг, медитация)", "2_b"),
            ("Семейный отдых (с детьми, активности для всей семьи)", "2_c"),
            ("Романтический отдых (для двоих)", "2_d"),
        ],
    },
    # Добавьте остальные вопросы аналогично...
}

# Веса для анализа ответов
SCORES = {
    "1_a": {"Китай-город": 3},
    "1_b": {"Сретенская/Курская": 3},
    "1_c": {"Бауманская/Первомайская": 3},
    "1_d": {"Глэмпинг": 3},
    "2_a": {"Китай-город": 2},
    "2_b": {"Сретенская/Курская": 2},
    "2_c": {"Бауманская/Первомайская": 2},
    "2_d": {"Глэмпинг": 2},
    # Добавьте веса для всех вариантов ответов
}

# Начало теста
async def start(update: Update, context: CallbackContext) -> int:
    keyboard = [[InlineKeyboardButton("Начать тест", callback_data="start_quiz")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Добро пожаловать! Этот тест поможет найти идеальный отель для вашего отдыха.\n"
        "Нажмите кнопку ниже, чтобы начать.",
        reply_markup=reply_markup,
    )
    return 0

# Универсальная функция для обработки вопросов
async def handle_question(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()

    step = context.user_data.get("step", 0)
    if step >= len(QUESTIONS):
        return await result(update, context)

    question = QUESTIONS[step]

    # Сохраняем ответ пользователя
    if step > 0:
        previous_answer = query.data
        context.user_data.setdefault("answers", []).append(previous_answer)

    # Формируем клавиатуру
    keyboard = [[InlineKeyboardButton(option[0], callback_data=option[1])] for option in question["options"]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Отправляем вопрос
    await query.edit_message_text(text=question["text"], reply_markup=reply_markup)

    # Обновляем шаг
    context.user_data["step"] = step + 1
    return step + 1

# Анализ результатов
async def result(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()

    answers = context.user_data.get("answers", [])
    scores = {"Китай-город": 0, "Сретенская/Курская": 0, "Бауманская/Первомайская": 0, "Глэмпинг": 0}

    for answer in answers:
        if answer in SCORES:
            for hotel, score in SCORES[answer].items():
                scores[hotel] += score

    best_option = max(scores, key=scores.get)
    url = {
        "Китай-город": "https://norke.ru/hotel1",
        "Сретенская/Курская": "https://norke.ru/hotel2",
        "Бауманская/Первомайская": "https://norke.ru/hotel3",
        "Глэмпинг": "https://norke.ru/glamping",
    }[best_option]

    keyboard = [
        [InlineKeyboardButton("Забронировать этот вариант", url=url)],
        [InlineKeyboardButton("Посмотреть другие варианты", url="https://norke.ru")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=f"Поздравляем! Ваш идеальный вариант - {best_option}.\n"
             f"Мы подготовили специальное предложение специально для вас!",
        reply_markup=reply_markup,
    )
    return ConversationHandler.END

# Отмена теста
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
        entry_points=[CommandHandler("start", start)],
        states={i: [CallbackQueryHandler(handle_question)] for i in STEPS},
        fallbacks=[CommandHandler("cancel", cancel)],
        per_message=True,  # Явно указываем параметр
        per_chat=True,
        per_user=True,
    )
    application.add_handler(conv_handler)

    # Публичный URL от Render
    render_url = "https://your-render-url.onrender.com"  # Замените на ваш реальный Render URL
    application.run_webhook(
        listen="0.0.0.0",
        port=8080,
        url_path=TOKEN,
        webhook_url=f"{render_url}/{TOKEN}",
    )
