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

# Токен бота
TOKEN = "7575514249:AAEZd9zzOQKTJdRcwu9kgSG3SF0-7HQpa5k"

# Состояния диалога
QUESTION_1, QUESTION_2, QUESTION_3, QUESTION_4, QUESTION_5, QUESTION_6, QUESTION_7, QUESTION_8, RESULT = range(9)

# Веса ответов для анализа
WEIGHTS = {
    "1_a": {"city_center": 3},  # Китай-город -> центр города
    "1_b": {"business_area": 2},  # Курская/Сретенская -> деловой район
    "1_c": {"business_area": 1, "nature": 1},  # Бауманская/Менделеевская -> немного деловой район, немного природа
    "1_d": {"nature": 3},  # Глэмпинг -> природа
    "2_a": {"city_center": 2, "business_area": 1},  # Активный отдых -> центр города и деловой район
    "2_b": {"nature": 2},  # Спокойный отдых -> природа
    "2_c": {"city_center": 1, "business_area": 1},  # Семейный отдых -> центр города и деловой район
    "2_d": {"nature": 2},  # Романтический отдых -> природа
    "3_a": {"city_center": 3},  # Люксовые апартаменты -> центр города
    "3_b": {"business_area": 2},  # Стандартные номера -> деловой район
    "3_c": {"nature": 1},  # Хостел или общежитие -> немного природа
    "3_d": {"nature": 3},  # Кемпинг или палатка -> природа
}

# URL-адреса изображений для вопросов
IMAGE_URLS = {
    1: "https://i.pinimg.com/736x/54/02/71/540271abaa48cf42b485ef8d29074ea9.jpg",  # Изображение для вопроса 1
    2: "https://i.pinimg.com/736x/94/5f/b9/945fb9e523630f45170f4140cd82351b.jpg",  # Изображение для вопроса 2
    3: "https://i.pinimg.com/736x/1a/b2/c7/1ab2c74722fc1a74d874af4071bede51.jpg",  # Изображение для вопроса 3
    4: "https://i.pinimg.com/736x/af/ec/47/afec47f80d249b03627f8b7567a25340.jpg",  # Изображение для вопроса 4
    5: "https://i.pinimg.com/736x/28/93/4b/28934bcf71cbf3264cb041effa5dbd9d.jpg",  # Изображение для вопроса 5
    6: "https://i.pinimg.com/736x/f6/80/46/f68046553973f747006ed5946c84ede7.jpg",  # Изображение для вопроса 6
    7: "https://i.pinimg.com/736x/d5/d3/a2/d5d3a2debe36dec850063d5150485295.jpg",  # Изображение для вопроса 7
    8: "https://i.pinimg.com/736x/af/ec/47/afec47f80d249b03627f8b7567a25340.jpg",  # Изображение для вопроса 8
}

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

    # Отправляем изображение
    await context.bot.send_photo(
        chat_id=query.message.chat_id,
        photo=IMAGE_URLS[next_question_id],
        caption=f"🌍 Вопрос {next_question_id}: ..."
    )

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
            QUESTION_
