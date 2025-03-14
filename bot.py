# -*- coding: utf-8 -*-
import os
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
        [InlineKeyboardButton("Начать тест 🚀", callback_data="start_quiz")]
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

    # Отправляем клавиатуру
    if next_question_id == 1:
        text = "Как вы представляете свой идеальный отдых? 🌆"
        options = {
            "1_a": "В самом сердце исторического центра (Китай-город)",
            "1_b": "В деловом районе с удобным транспортным сообщением (Курская/Сретенская)",
            "1_c": "В спокойном месте с парковыми зонами поблизости (Бауманская/Менделеевская)",
            "1_d": "На природе с полным погружением в экологичную среду (Глэмпинг)",
        }
    elif next_question_id == 2:
        text = "Какой тип отдыха вы предпочитаете? 🏖️"
        options = {
            "2_a": "Активный отдых (экскурсии, прогулки)",
            "2_b": "Спокойный отдых (чтение книг, медитация)",
            "2_c": "Семейный отдых (с детьми, активности для всей семьи)",
            "2_d": "Романтический отдых (для двоих)",
        }
    elif next_question_id == 3:
        text = "Какие условия проживания вы предпочитаете? 🏨"
        options = {
            "3_a": "Люксовые апартаменты",
            "3_b": "Стандартные номера",
            "3_c": "Хостел или общежитие",
            "3_d": "Кемпинг или палатка",
        }
    elif next_question_id == 4:
        text = "Какую еду вы предпочитаете во время отдыха? 🍽️"
        options = {
            "4_a": "Рестораны высокой кухни",
            "4_b": "Уютные кафе и закусочные",
            "4_c": "Фастфуд и уличная еда",
            "4_d": "Самостоятельное приготовление еды",
        }
    elif next_question_id == 5:
        text = "Как вы предпочитаете передвигаться по городу? 🚶‍♂️"
        options = {
            "5_a": "Пешком",
            "5_b": "Общественный транспорт",
            "5_c": "Такси или каршеринг",
            "5_d": "Аренда автомобиля",
        }
    elif next_question_id == 6:
        text = "Готовы ли вы платить за дополнительные услуги (спа, экскурсии)? 💰"
        options = {
            "6_a": "Да, обязательно!",
            "6_b": "Нет, только если это бесплатно",
            "6_c": "Зависит от условий",
        }
    elif next_question_id == 7:
        text = "Любите ли вы шумные места с большим количеством людей? 🎉"
        options = {
            "7_a": "Да, я люблю шумные места",
            "7_b": "Нет, я предпочитаю тишину",
            "7_c": "Зависит от настроения",
        }
    elif next_question_id == 8:
        text = "Готовы ли вы забронировать отель прямо сейчас? ✅"
        options = {
            "8_a": "Да, я готов забронировать прямо сейчас",
            "8_b": "Нет, я хочу подумать",
            "8_c": "Я хочу посмотреть другие варианты",
        }

    # Создаем клавиатуру
    keyboard = [
        [InlineKeyboardButton(text, callback_data=key)]
        for key, text in options.items()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text(
        text=text,
        reply_markup=reply_markup
    )
    return next_question_id

# Функция анализа результатов
async def result(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()

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
    return ConversationHandler.END

# Команда отмены
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
        per_chat=True,
        per_user=True
    )
    application.add_handler(conv_handler)

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
