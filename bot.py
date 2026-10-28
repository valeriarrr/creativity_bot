import logging
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
from telegram.request import HTTPXRequest
from creativity_bot.config import BOT_TOKEN

# логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logging.getLogger("httpx").setLevel(logging.WARNING)

# список идей для контента
CONTENT_IDEAS = [
    "Скрести «Вязание» и «Космос»: свяжи шарф с вышитыми созвездиями.",
    "Сними видео «Что было бы, если бы коты правили миром» — 5 сценариев.",
    "Напиши пост «5 ошибок, которые я совершал в начале пути».",
    "Сделай челлендж: 7 дней без сахара — дневник с фото.",
    "Разбери миф «Чтобы начать, нужно много денег» на 3 аргумента.",
    "Создай рубрику «Один день — один лайфхак» на 30 дней.",
    "Сними «До/После» своего рабочего стола.",
    "Придумай игру «Угадай профессию по описанию» для сторис.",
    "Сделай обзор «3 приложения, которые экономят мне час в день».",
    "Запиши подкаст «Что я делал бы иначе, если бы начинал с нуля».",
]

# шаблоны мемов
MEME_TEMPLATES = {
    "drake": {
        "name": "Drake (отказ / одобрение)",
        "top": "Работать 8 часов в офисе",
        "bottom": "Смотреть мемы о работе из дома",
    },
    "distracted": {
        "name": "Отвлечённый парень",
        "top": "Дедлайн через час",
        "bottom": "Новая вкладка с YouTube",
    },
    "this_is_fine": {
        "name": "This is fine",
        "top": "Проект горит",
        "bottom": "Я пью кофе",
    },
}

# промпты для нейросетей
PROMPT_TEMPLATES = [
    "Киберпанк-город ночью, неоновые вывески, дождь, отражения в лужах, кинематографичный свет, 8k, hyperrealistic",
    "Портрет пожилого рыбака, морщины, солёный ветер, золотой час, детализация кожи, 85mm, photorealistic",
    "Фэнтези-лес, светящиеся грибы, туман, магический свет, стиль Studio Ghibli, пастельные тона",
    "Астронавт на заброшенной станции, ржавчина, драматичный свет, sci-fi, cinematic, unreal engine 5",
]

# вопросы для брейнсторма
BRAINSTORM_QUESTIONS = [
    "Какую конкретную проблему решает твоя идея? Опиши одним предложением.",
    "Кто твоя целевая аудитория? Опиши одного человека: возраст, интересы, боль.",
    "Что уже существует на рынке и чем твоя идея отличается? Назови 1–2 конкурента.",
    "Какой самый маленький шаг ты можешь сделать сегодня, чтобы проверить идею?",
    "Что может пойти не так? Назови 3 риска и по одному способу их снизить.",
    "Как ты поймёшь, что идея работает? Назови 1 измеримый критерий.",
]

# шаблоны для творчества
CREATIVE_TEMPLATES = [
    ("Пост в соцсети", "Хук -> Проблема -> Решение -> Призыв к действию -> Хештеги."),
    ("Сценарий Reels/Shorts", "Вопрос-крючок (0-3 сек) -> Шок-факт -> Объяснение -> Финал с CTA."),
    ("История (сторителлинг)", "Герой -> Проблема -> Препятствия -> Поворот -> Развязка -> Мораль."),
    ("Описание картинки для нейросети", "Стиль + Объект + Детали + Освещение + Качество (8k, photorealistic)."),
    ("Письмо клиенту", "Приветствие -> Суть -> Что делаем -> Сроки -> Благодарность."),
    ("Питч идеи (30 сек)", "Проблема -> Решение -> Ценность -> Призыв попробовать."),
]


# главное меню
def main_menu() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("Идея для контента", callback_data="idea")],
        [InlineKeyboardButton("Создать мем", callback_data="meme")],
        [InlineKeyboardButton("Промпт для нейросети", callback_data="prompt")],
        [InlineKeyboardButton("Брейнсторминг", callback_data="brainstorm")],
        [InlineKeyboardButton("Шаблоны для творчества", callback_data="templates")],
    ]
    return InlineKeyboardMarkup(keyboard)


# команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_text(
        f"Привет, {user.first_name}!\n\n"
        "Я креативный генератор. Помогу придумать идею, собрать мем, "
        "написать промпт для нейросети, провести брейнсторм или найти шаблон.\n\n"
        "Выбери раздел:",
        reply_markup=main_menu(),
    )


# команда /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Доступные команды:\n"
        "/start - главное меню\n"
        "/idea - случайная идея для контента\n"
        "/prompt - случайный промпт для нейросети\n"
        "/meme - шаблоны мемов\n"
        "/brainstorm - вопросы для брейнсторма\n"
        "/templates - шаблоны для творчества\n"
        "/help - эта справка"
    )


# команда /idea
async def idea_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    idea = random.choice(CONTENT_IDEAS)
    await update.message.reply_text(
        f"Идея для контента:\n\n{idea}",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Ещё идею", callback_data="idea")],
             [InlineKeyboardButton("В меню", callback_data="menu")]]
        ),
    )


# команда /prompt
async def prompt_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    prompt = random.choice(PROMPT_TEMPLATES)
    await update.message.reply_text(
        f"Промпт для нейросети:\n\n{prompt}",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Ещё промпт", callback_data="prompt")],
             [InlineKeyboardButton("В меню", callback_data="menu")]]
        ),
    )


# команда /meme
async def meme_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = "Шаблоны мемов:\n\n"
    for val in MEME_TEMPLATES.values():
        text += f"{val['name']}\nВерх: {val['top']}\nНиз: {val['bottom']}\n\n"
    text += "Скопируй текст в любой мем-генератор."
    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("В меню", callback_data="menu")]]
        ),
    )


# команда /brainstorm
async def brainstorm_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = random.choice(BRAINSTORM_QUESTIONS)
    await update.message.reply_text(
        f"Вопрос для брейнсторма:\n\n{q}",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Ещё вопрос", callback_data="brainstorm")],
             [InlineKeyboardButton("В меню", callback_data="menu")]]
        ),
    )


# команда /templates
async def templates_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = "Шаблоны для творчества:\n\n"
    for name, desc in CREATIVE_TEMPLATES:
        text += f"{name}\n{desc}\n\n"
    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("В меню", callback_data="menu")]]
        ),
    )


# обработка нажатий на кнопки
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == "idea":
        idea = random.choice(CONTENT_IDEAS)
        await query.edit_message_text(
            f"Идея для контента:\n\n{idea}",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Ещё идею", callback_data="idea")],
                 [InlineKeyboardButton("В меню", callback_data="menu")]]
            ),
        )
    elif query.data == "prompt":
        prompt = random.choice(PROMPT_TEMPLATES)
        await query.edit_message_text(
            f"Промпт для нейросети:\n\n{prompt}",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Ещё промпт", callback_data="prompt")],
                 [InlineKeyboardButton("В меню", callback_data="menu")]]
            ),
        )
    elif query.data == "meme":
        text = "Шаблоны мемов:\n\n"
        for val in MEME_TEMPLATES.values():
            text += f"{val['name']}\nВерх: {val['top']}\nНиз: {val['bottom']}\n\n"
        text += "Скопируй текст в любой мем-генератор."
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("В меню", callback_data="menu")]]
            ),
        )
    elif query.data == "brainstorm":
        q = random.choice(BRAINSTORM_QUESTIONS)
        await query.edit_message_text(
            f"Вопрос для брейнсторма:\n\n{q}",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Ещё вопрос", callback_data="brainstorm")],
                 [InlineKeyboardButton("В меню", callback_data="menu")]]
            ),
        )
    elif query.data == "templates":
        text = "Шаблоны для творчества:\n\n"
        for name, desc in CREATIVE_TEMPLATES:
            text += f"{name}\n{desc}\n\n"
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("В меню", callback_data="menu")]]
            ),
        )
    elif query.data == "menu":
        await query.edit_message_text("Выбери раздел:", reply_markup=main_menu())
    else:
        await query.edit_message_text("Неизвестная команда.")


# ответ на свободный текст
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Я не понимаю свободный текст. Используй /help, чтобы увидеть команды."
    )


# запуск бота
def main() -> None:
    # увеличенные таймауты, чтобы не падало на медленной сети
    request = HTTPXRequest(connect_timeout=20.0, read_timeout=30.0)

    # если нужен прокси - раскомментируй строку ниже и укажи свой порт
    # request = HTTPXRequest(proxy="http://127.0.0.1:7890", connect_timeout=20.0, read_timeout=30.0)

    application = Application.builder().token(BOT_TOKEN).request(request).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("idea", idea_command))
    application.add_handler(CommandHandler("prompt", prompt_command))
    application.add_handler(CommandHandler("meme", meme_command))
    application.add_handler(CommandHandler("brainstorm", brainstorm_command))
    application.add_handler(CommandHandler("templates", templates_command))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    print("Бот запущен. Нажмите Ctrl+C для остановки.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
