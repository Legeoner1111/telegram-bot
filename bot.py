# -*- coding: utf-8 -*-
import os
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    CallbackContext,
)

# Создаем Flask-приложение
app = Flask(__name__)

# Токен бота
TOKEN = "7575514249:AAEZd9zzOQKTJdRcwu9kgSG3SF0-7HQpa5k"

# Словарь для хранения вопросов
QUESTIONS = {
    1: {
        "text": "Как вы представляете свой идеальный отдых?",
        "options": {
            "1_a": "В самом сердце исторического центра (Китай-город)",
            "1_b": "В деловом районе с удобным транспортным сообщением (Курская/Сретенская)",
            "1_c": "В спокойном месте с парковыми зонами поблизости (Бауманская/Менделеевская)",
            "1_d": "На природе с полным погружением в экологичную среду (Глэмпинг)",
        },
    },
    2: {
        "text": "Какой тип отдыха вы предпочитаете?",
        "options": {
            "2_a": "Активный отдых (экскурсии, прогулки)",
            "2_b": "Спокойный отдых (чтение книг, медитация)",
            "2_c": "Семейный отдых (с детьми, активности для всей семьи)",
            "2_d": "Романтический отдых (для двоих)",
        },
    },
    3: {
        "text": "Какие условия проживания вы предпочитаете?",
        "options": {
            "3_a": "Люксовые апартаменты",
            "3_b": "Стандартные номера",
            "3_c": "Хостел или общежитие",
            "3_d": "Кемпинг или палатка",
        },
    },
    4: {
        "text": "Какую еду вы предпочитаете во время отдыха?",
        "options": {
            "4_a": "Рестораны высокой кухни",
            "4_b": "Уютные кафе и закусочные",
            "4_c": "Фастфуд и уличная еда",
            "4_d": "Самостоятельное приготовление еды",
        },
    },
    5: {
        "text": "Как вы предпочитаете передвигаться по городу?",
        "options": {
            "5_a": "Пешком",
            "5_b": "Общественный транспорт",
            "5_c": "Такси или каршеринг",
            "5_d": "Аренда автомобиля",
        },
    },
    6: {
        "text": "Готовы ли вы платить за дополнительные услуги (спа, экскурсии)?",
        "options": {
            "6_a": "Да, обязательно!",
            "6_b": "Нет, только если это бесплатно",
            "6_c": "Зависит от условий",
        },
    },
    7: {
        "text": "Любите ли вы шумные места с большим количеством людей?",
        "options": {
            "7_a": "Да, я люблю шумные места",
            "7_b": "Нет, я предпочитаю тишину",
            "7_c": "Зависит от настроения",
        },
    },
    8: {
        "text": "Готовы ли вы забронировать отель прямо сейчас?",
        "options": {
            "8_a": "Да, я готов забронировать прямо сейчас",
            "8_b": "Нет, я хочу подумать",
            "8_c": "Я хочу посмотреть другие варианты",
        },
    },
}

# Начало теста
async def start(update: Update, context: CallbackContext) -> None:
    # Инициализируем ответы пользователя
    context.user_data["answers"] = {}
    context.user_data["current_question"] = 1

    # Отправляем первый вопрос
    await send_question(update, context)

# Функция отправки вопроса
async def send_question(update: Update, context: CallbackContext) -> None:
    question_id = context.user_data["current_question"]
    question = QUESTIONS[question_id]

    # Создаем клавиатуру
    keyboard = [
        [InlineKeyboardButton(text, callback_data=key)]
        for key, text in question["options"].items()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        await update.callback_query.message.reply_text(
            text=question["text"],
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            text=question["text"],
            reply_markup=reply_markup
        )

# Обработка ответов пользователя
async def handle_answer(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    # Сохраняем ответ пользователя
    question_id = context.user_data["current_question"]
    context.user_data["answers"][question_id] = query.data

    # Переходим к следующему вопросу
    context.user_data["current_question"] += 1
    next_question_id = context.user_data["current_question"]

    if next_question_id > len(QUESTIONS):
        await result(update, context)
    else:
        await send_question(update, context)

# Функция анализа результатов
async def result(update: Update, context: CallbackContext) -> None:
    answers = context.user_data["answers"]

    # Анализ ответов
    if answers.get("1") == "1_a" and answers.get("2") == "2_a":
        hotel = "Китай-город"
        url = "https://norke.ru/hotel1"
    elif answers.get("1") == "1_b" and answers.get("2") == "2_b":
        hotel = "Сретенская/Курская"
        url = "https://norke.ru/hotel2"
    elif answers.get("1") == "1_c" and answers.get("2") == "2_c":
        hotel = "Бауманская/Первомайская"
        url = "https://norke.ru/hotel3"
    else:
        hotel = "Глэмпинг"
        url = "https://norke.ru/glamping"

    # Отправляем результат
    keyboard = [
        [InlineKeyboardButton("Забронировать этот вариант 🏨", url=url)],
        [InlineKeyboardButton("Посмотреть другие варианты 🔍", url="https://norke.ru")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=f"🎉 Поздравляем! Ваш идеальный вариант - {hotel}.\n"
             f"Мы подготовили специальное предложение специально для вас!",
        reply_markup=reply_markup
    )

# Команда отмены
async def cancel(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Тест завершен. Если хотите повторить, нажмите /start.")
    context.user_data.clear()

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
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_answer))
    application.add_handler(CommandHandler("cancel", cancel))

    # Публичный URL от Render
    render_url = "https://telegram-bot-d8rq.onrender.com"  # Замени на свой реальный Render URL

    # Установка вебхука
    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8080)),  # Render использует переменную окружения PORT
        url_path=TOKEN,
        webhook_url=f"{render_url}/{TOKEN}"  # Полный URL для вебхука
    )

    # Запуск Flask-сервера
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))  # Render использует переменную окружения PORT
