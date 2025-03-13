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
    # Остальные ссылки...
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
        entry_points=[CommandHandler('start', start)],
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
        webhook_url=f"{render_url}/{TOKEN}"
    )

    # Запуск Flask-сервера
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))  # Используем порт из переменной окружения
