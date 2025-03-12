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

# Конфигурация вопросов
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
    2: {
        "text": "Какие условия проживания вы предпочитаете?",
        "options": [
            ("Люксовые апартаменты", "3_a"),
            ("Стандартные номера", "3_b"),
            ("Хостел или общежитие", "3_c"),
            ("Кемпинг или палатка", "3_d"),
        ],
    },
    # Добавьте остальные вопросы аналогично...
}

# Состояния диалога
STEPS = range(len(QUESTIONS) + 1)

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
        per_message=False,
        per_chat=True,
        per_user=True,
    )
    application.add_handler(conv_handler)

    # Публичный URL от Render
    render_url = "https://telegram-bot-d8rq.onrender.com"  # Замени на свой реальный Render URL

    # Установка вебхука
    application.run_webhook(
        listen="0.0.0.0",
        port=8080,
        url_path=TOKEN,
        webhook_url=f"{render_url}/{TOKEN}",
    )
