"""
Обработчики команд для бота GlassPen
Стиль python-telegram-bot (как helper_bot)
"""
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler

logger = logging.getLogger(__name__)

# Состояния для ConversationHandler (должны совпадать с bot.py)
ASKING_QUESTION = 1

# Данные FAQ (временно, позже вынесем в отдельный файл/БД)
FAQ_DATA = {
    "1": {
        "question": "Можно ли на вашем канале разместить свои стихи?",
        "answer": (
            "Можно. Пришлите свои стихи администратору канала на модерацию, "
            "и стихи будут размещены в ближайшее время."
        )
    },
    "2": {
        "question": "Какие требования для присылаемых в адрес вашего канала стихов?",
        "answer": (
            "Требования к стихам:\n\n"
            "• Корректная лексика\n"
            "• Объём около 1500 символов или 300-400 слов\n"
            "• Указание на авторство обязательно\n"
            "• Ссылка на размещённое произведение (если имеется)"
        )
    },
    "3": {
        "question": "Как часто выходят новые публикации?",
        "answer": (
            "Специального расписания нет. Периодичность публикации полностью "
            "зависит от вдохновения автора канала или подписчиков канала."
        )
    },
    "4": {
        "question": "Задайте свой вопрос автору канала",
        "answer": (
            "Чтобы задать свой вопрос, воспользуйтесь кнопкой "
            "'Задать вопрос автору канала' в главном меню. "
            "Автор постарается ответить вам в ближайшее время."
        )
    },
    "5": {
        "question": "Вакантный вопрос",
        "answer": "—"
    }
}


# ========== КОМАНДЫ ==========

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик команды /start
    """
    welcome_text = (
        "👋 Добро пожаловать в бот канала 'Стеклянное Перо'!\n\n"
        "📚 *Что я умею:*\n"
        "• 📋 Показать ссылку на канал\n"
        "• ❓ Ответить на частые вопросы\n"
        "• ✏️ Принять ваш вопрос для автора канала\n\n"
        "Выберите действие в меню ниже:"
    )
    
    keyboard = get_main_menu_keyboard()
    
    await update.message.reply_text(
        welcome_text,
        parse_mode="Markdown",
        reply_markup=keyboard
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик команды /help
    """
    help_text = (
        "🆘 *Помощь по использованию бота:*\n\n"
        "*Доступные команды:*\n"
        "/start - Главное меню\n"
        "/help - Эта справка\n"
        "/channel - Получить ссылку на канал\n\n"
        "*Основные функции:*\n"
        "• Получить ссылку на канал 'Стеклянное Перо'\n"
        "• Посмотреть ответы на частые вопросы (FAQ)\n"
        "• Задать свой вопрос автору канала\n\n"
        "Для навигации используйте кнопки меню."
    )
    
    keyboard = get_main_menu_keyboard()
    
    await update.message.reply_text(
        help_text,
        parse_mode="Markdown",
        reply_markup=keyboard
    )


async def cmd_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик команды /channel
    """
    channel_link = "https://t.me/glass_pen/"
    channel_text = (
        "📢 *Канал 'Стеклянное Перо':*\n\n"
        f"{channel_link}\n\n"
        "Нажмите на ссылку выше или скопируйте её.\n"
        "Подписывайтесь, чтобы быть в курсе новых публикаций!"
    )
    
    keyboard = get_main_menu_keyboard()
    
    await update.message.reply_text(
        channel_text,
        parse_mode="Markdown",
        reply_markup=keyboard
    )


# ========== CALLBACK ОБРАБОТЧИКИ ==========

async def handle_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Показ главного меню (обработка callback)
    """
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "🏠 *Главное меню:*\n\n"
        "Выберите действие:",
        parse_mode="Markdown",
        reply_markup=get_main_menu_keyboard()
    )


async def handle_faq_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Показ меню с частыми вопросами
    """
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "❓ *Частые вопросы:*\n\n"
        "Выберите вопрос, чтобы увидеть ответ:",
        parse_mode="Markdown",
        reply_markup=get_faq_menu_keyboard()
    )


async def handle_faq_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Показ ответа на выбранный вопрос FAQ
    """
    query = update.callback_query
    await query.answer()
    
    # Извлекаем номер вопроса из callback_data (формат: faq:1)
    faq_id = query.data.split(":")[1]
    
    if faq_id in FAQ_DATA:
        faq = FAQ_DATA[faq_id]
        
        response_text = (
            f"*Вопрос:* {faq['question']}\n\n"
            f"*Ответ:* {faq['answer']}"
        )
        
        await query.edit_message_text(
            response_text,
            parse_mode="Markdown",
            reply_markup=get_back_to_faq_keyboard()
        )
    else:
        await query.answer("Вопрос не найден", show_alert=True)


# ========== ОБРАБОТКА ВОПРОСОВ ==========

async def handle_ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Начало процесса задавания вопроса
    """
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "✏️ *Задайте вопрос автору канала:*\n\n"
        "Напишите ваш вопрос в одном сообщении.\n"
        "Автор получит его и ответит в ближайшее время.\n\n"
        "Или нажмите 'Отмена'.",
        parse_mode="Markdown",
        reply_markup=get_cancel_keyboard()
    )
    
    return ASKING_QUESTION


async def handle_question_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработка введенного вопроса
    """
    user_question = update.message.text
    
    # Здесь будет логика сохранения вопроса в JSON
    # Пока просто выводим подтверждение
    # Сохраняем вопрос в user_data для примера
    context.user_data['last_question'] = {
        'text': user_question,
        'timestamp': update.message.date.isoformat()
    }
    
    await update.message.reply_text(
        "✅ *Ваш вопрос получен!*\n\n"
        f"Вопрос: {user_question[:100]}...\n\n"
        "Автор канала получит ваш вопрос и ответит "
        "в ближайшее время. Спасибо за обращение!\n\n"
        "Вернуться в главное меню: /start",
        parse_mode="Markdown"
    )
    
    return ConversationHandler.END


async def handle_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Отмена задания вопроса
    """
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "❌ Ввод вопроса отменен.",
        reply_markup=get_main_menu_keyboard()
    )
    
    return ConversationHandler.END


# ========== КЛАВИАТУРЫ ==========

def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """
    Главное меню с тремя кнопками
    """
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "Скопировать ссылку на канал",
                callback_data="show_channel"
            )
        ],
        [
            InlineKeyboardButton(
                "Ответы на частые вопросы",
                callback_data="show_faq"
            )
        ],
        [
            InlineKeyboardButton(
                "Задать вопрос автору канала",
                callback_data="ask_question"
            )
        ]
    ])
    return keyboard


def get_faq_menu_keyboard() -> InlineKeyboardMarkup:
    """
    Меню с вопросами FAQ
    """
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "Можно ли на вашем канале разместить свои стихи?",
                callback_data="faq:1"
            )
        ],
        [
            InlineKeyboardButton(
                "Какие требования для присылаемых стихов?",
                callback_data="faq:2"
            )
        ],
        [
            InlineKeyboardButton(
                "Как часто выходят новые публикации?",
                callback_data="faq:3"
            )
        ],
        [
            InlineKeyboardButton(
                "Задайте свой вопрос автору канала",
                callback_data="faq:4"
            )
        ],
        [
            InlineKeyboardButton("Вакантный вопрос", callback_data="faq:5")
        ],
        [
            InlineKeyboardButton("Назад", callback_data="main_menu"),
            InlineKeyboardButton("Главное меню", callback_data="main_menu")
        ]
    ])
    return keyboard


def get_back_to_faq_keyboard() -> InlineKeyboardMarkup:
    """
    Кнопки для возврата из ответа FAQ
    """
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Назад", callback_data="show_faq"),
            InlineKeyboardButton("Главное меню", callback_data="main_menu")
        ]
    ])
    return keyboard


def get_cancel_keyboard() -> InlineKeyboardMarkup:
    """
    Кнопка отмены для диалога
    """
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Отмена", callback_data="cancel")]
    ])
    return keyboard


# ========== РЕГИСТРАЦИЯ ОБРАБОТЧИКОВ (для совместимости) ==========

def get_handlers():
    """
    Возвращает обработчики для регистрации (как в helper_bot)
    """
    from telegram.ext import (
        CommandHandler,
        CallbackQueryHandler,
        MessageHandler,
        filters,
        ConversationHandler
    )
    
    ASKING_QUESTION = 1
    
    question_conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(handle_ask_question, pattern="^ask_question$")
        ],
        states={
            ASKING_QUESTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_question_input)
            ]
        },
        fallbacks=[
            CallbackQueryHandler(handle_cancel, pattern="^cancel$"),
            CommandHandler("start", cmd_start)
        ],
        allow_reentry=True
    )
    
    return [
        CommandHandler("start", cmd_start),
        CommandHandler("help", cmd_help),
        CommandHandler("channel", cmd_channel),
        CallbackQueryHandler(handle_main_menu, pattern="^main_menu$"),
        CallbackQueryHandler(handle_faq_menu, pattern="^show_faq$"),
        CallbackQueryHandler(handle_faq_answer, pattern="^faq:"),
        question_conv_handler,
        CallbackQueryHandler(handle_cancel, pattern="^cancel$")
    ]