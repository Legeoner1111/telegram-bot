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

# URL-адреса изображений для вопросов
IMAGE_URLS = {
    "question_1": "https://i.pinimg.com/736x/54/02/71/540271abaa48cf42b485ef8d29074ea9.jpg",
    "question_2": "https://i.pinimg.com/736x/94/5f/b9/945fb9e523630f45170f4140cd82351b.jpg",
    "question_3": "https://i.pinimg.com/736x/1a/b2/c7/1ab2c74722fc1a74d874af4071bede51.jpg",
    "question_4": "https://i.pinimg.com/736x/af/ec/47/afec47f80d249b03627f8b7567a25340.jpg",
    "question_5": "https://i.pinimg.com/736x/28/93/4b/28934bcf71cbf3264cb041effa5dbd9d.jpg",
    "question_6": "https://i.pinimg.com/736x/f6/80/46/f68046553973f747006ed5946c84ede7.jpg",
    "question_7": "https://i.pinimg.com/736x/d5/d3/a2/d5d3a2debe36dec850063d5150485295.jpg",
}

# URL-адреса изображений для ответов
ANSWER_IMAGE_URLS = {
    "1_a": "https://avatars.mds.yandex.net/get-altay/14451083/2a000001931f4e723019fd685dbd1baf4758/XXXL",  # Китай-город
    "1_b": "https://avatars.mds.yandex.net/get-altay/11419181/2a00000191c9cd851b04d0e019bfda1120cf/XXXL",  # Курская/Сретенская
    "1_c": "https://avatars.mds.yandex.net/get-altay/14010724/2a00000191c7b57383ddee958f1b2c2fa0ee/XXXL",  # Бауманская/Менделеевская
    "1_d": "https://yandex-images.clstorage.net/IW5F0x186/3884c5pILe/FzM4EjuhkXxnmYwyCSXV298roOykPQFtrTEoXiKCPMUnn3a-5pQNZV6VRjggMKsK3bgB7JCIv2yDCGoO4_yTnQUlNVtx-IYpJMjOdUR91M3BNvStmAAhD5wLHTAHuAe6D7RLkebaUjUL21x_ZFvbGMTfd5XX3sEH_iQ8cpmEmMAsOlJacaGqfH-1tSRVP_3DsiOz0rELGAG3GhAyHYwtnymmU73r-kYeHMo2Rlxy00jt60ONzO_kP_I5JlC_uJHcNy1WSWGrjVhntLAAayX44YYLjcqoDRA6jgITJRaxOro1iVel9MpOAwLSBF9iceVp7tF3hePtzADAACtxurmUyRAyQXZmkrJtXqubBHA9-8mkBqnJmCs0ApMxETUPqSKAHIpRmtjjSyYm9St1elLCVfrmQ4_w7dg0_DslS5aFgeUILnN_ZbiNVF6tvyJUB-jyshSM0po0Ngy2HQ8-DaQ4mS2CSK_F6HoUHc4LSV9x92nT6n2M1_biPvQyHFGxqLj-FSNGXGO0gGtbnaYUYhrn5ZgXgs6zGSkUlzMuFgCREKY8qUSL8Mx9NRnTGl53R95v5f5bttnA-DHZOQJ7kYSA-SQaQXxAgqFJdLSnB1IY1NC0Aa_Mgg8AKbYsNAM1qj69NYNqpfLJWRgh7gBUY03HSt3xQrPywdwE5AQxUaWohu4yBXF8RKyFVFi7iTFxDejAoDuP15ILKDOtBw0wLaAJiQq7bo3uwmUgDOgadHt9y3zs8lqW6snLF-sQMFGxvYDDCSh4XFW0k0pRlIkuTQrL2L0_o_CWKjsTiw44EzS_PpoRg3CU2P5mHSLMHWZ8XNxe6PtLu-3V9jPzGSB6gJSO7yQnd3ZQuJNYeZOHJUQN3eyjKKbkhAsSJ4cdPwYNlDmSI5VTsfXfWyUF9wRbQGHDbtvncJPx_Mka5Tk4driKk_ggBEVkeaOKXkCBrAZICvvLgz2p6LY7FzOmGjEHB5E",  # Глэмпинг
    "2_a": "https://example.com/answer2_a.jpg",  # Активный отдых
    "2_b": "https://example.com/answer2_b.jpg",  # Спокойный отдых
    "2_c": "https://example.com/answer2_c.jpg",  # Семейный отдых
    "2_d": "https://example.com/answer2_d.jpg",  # Романтический отдых
    "3_a": "https://example.com/answer3_a.jpg",  # Люксовые апартаменты
    "3_b": "https://example.com/answer3_b.jpg",  # Стандартные номера
    "3_c": "https://example.com/answer3_c.jpg",  # Хостел или общежитие
    "3_d": "https://example.com/answer3_d.jpg",  # Кемпинг или палатка
    "4_a": "https://example.com/answer4_a.jpg",  # Рестораны высокой кухни
    "4_b": "https://example.com/answer4_b.jpg",  # Уютные кафе
    "4_c": "https://example.com/answer4_c.jpg",  # Фастфуд
    "4_d": "https://example.com/answer4_d.jpg",  # Самостоятельное приготовление
    "5_a": "https://example.com/answer5_a.jpg",  # Пешком
    "5_b": "https://example.com/answer5_b.jpg",  # Общественный транспорт
    "5_c": "https://example.com/answer5_c.jpg",  # Такси или каршеринг
    "5_d": "https://example.com/answer5_d.jpg",  # Аренда автомобиля
    "6_a": "https://example.com/answer6_a.jpg",  # Да, обязательно!
    "6_b": "https://example.com/answer6_b.jpg",  # Нет, только если бесплатно
    "6_c": "https://example.com/answer6_c.jpg",  # Зависит от условий
    "7_a": "https://example.com/answer7_a.jpg",  # Да, люблю шумные места
    "7_b": "https://example.com/answer7_b.jpg",  # Нет, предпочитаю тишину
    "7_c": "https://example.com/answer7_c.jpg",  # Зависит от настроения
    "8_a": "https://example.com/answer8_a.jpg",  # Да, готов забронировать
    "8_b": "https://example.com/answer8_b.jpg",  # Нет, хочу подумать
    "8_c": "https://example.com/answer8_c.jpg",  # Хочу посмотреть другие варианты
}

# Начало теста
async def start(update: Update, context: CallbackContext) -> int:
    keyboard = [
        [InlineKeyboardButton("🚀 Начать тест", callback_data="start_quiz")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🎉 Добро пожаловать! Этот тест поможет найти идеальный отель для вашего отдыха.\n"
        "Нажмите кнопку ниже, чтобы начать.",
        reply_markup=reply_markup
    )
    return QUESTION_1

async def question_1(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    user_answers[1] = query.data  # Сохраняем ответ пользователя

    # Отправка картинки
    await query.message.reply_photo(
        photo=IMAGE_URLS["question_1"],  # Замените на реальный URL
        caption="🌆 Как вы представляете свой идеальный отдых?",
    )

    keyboard = [
        [InlineKeyboardButton("🏛️ Исторический центр (Китай-город)", callback_data="1_a")],
        [InlineKeyboardButton("💼 Деловой район (Курская/Сретенская)", callback_data="1_b")],
        [InlineKeyboardButton("🌳 Спокойное место (Бауманская)", callback_data="1_c")],
        [InlineKeyboardButton("🏕️ На природе (Глэмпинг)", callback_data="1_d")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text(
        text="Выберите вариант:",
        reply_markup=reply_markup
    )
    return QUESTION_2

async def question_2(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    user_answers[2] = query.data  # Сохраняем ответ пользователя

    # Отправка картинки
    await query.message.reply_photo(
        photo=IMAGE_URLS["question_2"],  # Замените на реальный URL
        caption="🌴 Какой тип отдыха вы предпочитаете?",
    )

    keyboard = [
        [InlineKeyboardButton("🏃‍♂️ Активный отдых", callback_data="2_a")],
        [InlineKeyboardButton("🧘‍♀️ Спокойный отдых", callback_data="2_b")],
        [InlineKeyboardButton("👨‍👩‍👧‍👦 Семейный отдых", callback_data="2_c")],
        [InlineKeyboardButton("💑 Романтический отдых", callback_data="2_d")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text(
        text="Выберите вариант:",
        reply_markup=reply_markup
    )
    return QUESTION_3

async def question_3(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    user_answers[3] = query.data  # Сохраняем ответ пользователя

    # Отправка картинки
    await query.message.reply_photo(
        photo=IMAGE_URLS["question_3"],  # Замените на реальный URL
        caption="🏡 Какие условия проживания вы предпочитаете?",
    )

    keyboard = [
        [InlineKeyboardButton("🌟 Люксовые апартаменты", callback_data="3_a")],
        [InlineKeyboardButton("🏠 Стандартные номера", callback_data="3_b")],
        [InlineKeyboardButton("🛏️ Хостел или общежитие", callback_data="3_c")],
        [InlineKeyboardButton("⛺ Кемпинг или палатка", callback_data="3_d")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text(
        text="Выберите вариант:",
        reply_markup=reply_markup
    )
    return QUESTION_4

async def question_4(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    user_answers[4] = query.data  # Сохраняем ответ пользователя

    # Отправка картинки
    await query.message.reply_photo(
        photo=IMAGE_URLS["question_4"],  # Замените на реальный URL
        caption="🍔 Какую еду вы предпочитаете во время отдыха?",
    )

    keyboard = [
        [InlineKeyboardButton("🍴 Рестораны высокой кухни", callback_data="4_a")],
        [InlineKeyboardButton("☕ Уютные кафе", callback_data="4_b")],
        [InlineKeyboardButton("🍟 Фастфуд", callback_data="4_c")],
        [InlineKeyboardButton("🍳 Самостоятельное приготовление", callback_data="4_d")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text(
        text="Выберите вариант:",
        reply_markup=reply_markup
    )
    return QUESTION_5

async def question_5(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    user_answers[5] = query.data  # Сохраняем ответ пользователя

    # Отправка картинки
    await query.message.reply_photo(
        photo=IMAGE_URLS["question_5"],  # Замените на реальный URL
        caption="🚗 Как вы предпочитаете передвигаться по городу?",
    )

    keyboard = [
        [InlineKeyboardButton("🚶‍♂️ Пешком", callback_data="5_a")],
        [InlineKeyboardButton("🚇 Общественный транспорт", callback_data="5_b")],
        [InlineKeyboardButton("🚕 Такси или каршеринг", callback_data="5_c")],
        [InlineKeyboardButton("🚙 Аренда автомобиля", callback_data="5_d")],  # Исправленная строка
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text(
        text="Выберите вариант:",
        reply_markup=reply_markup
    )
    return QUESTION_6

async def question_6(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    user_answers[6] = query.data  # Сохраняем ответ пользователя

    # Отправка картинки
    await query.message.reply_photo(
        photo=IMAGE_URLS["question_6"],  # Замените на реальный URL
        caption="💆 Готовы ли вы платить за дополнительные услуги (спа, экскурсии)?",
    )

    keyboard = [
        [InlineKeyboardButton("✅ Да, обязательно!", callback_data="6_a")],
        [InlineKeyboardButton("❌ Нет, только если это бесплатно", callback_data="6_b")],
        [InlineKeyboardButton("🤔 Зависит от условий", callback_data="6_c")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text(
        text="Выберите вариант:",
        reply_markup=reply_markup
    )
    return QUESTION_7

async def question_7(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    user_answers[7] = query.data  # Сохраняем ответ пользователя

    # Отправка картинки
    await query.message.reply_photo(
        photo=IMAGE_URLS["question_7"],  # Замените на реальный URL
        caption="🎶 Любите ли вы шумные места с большим количеством людей?",
    )

    keyboard = [
        [InlineKeyboardButton("🎉 Да, я люблю шумные места", callback_data="7_a")],
        [InlineKeyboardButton("🔇 Нет, я предпочитаю тишину", callback_data="7_b")],
        [InlineKeyboardButton("🤷‍♂️ Зависит от настроения", callback_data="7_c")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text(
        text="Выберите вариант:",
        reply_markup=reply_markup
    )
    return QUESTION_8

async def question_8(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    user_answers[8] = query.data  # Сохраняем ответ пользователя

    # Отправка картинки
    await query.message.reply_photo(
        photo=IMAGE_URLS["question_8"],  # Замените на реальный URL
        caption="📝 Готовы ли вы забронировать отель прямо сейчас?",
    )

    keyboard = [
        [InlineKeyboardButton("✅ Да, я готов забронировать", callback_data="8_a")],
        [InlineKeyboardButton("⏳ Нет, я хочу подумать", callback_data="8_b")],
        [InlineKeyboardButton("🔍 Я хочу посмотреть другие варианты", callback_data="8_c")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text(
        text="Выберите вариант:",
        reply_markup=reply_markup
    )
    return RESULT
