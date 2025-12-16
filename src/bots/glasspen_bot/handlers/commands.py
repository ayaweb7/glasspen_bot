"""
Обработчики команд и сообщений для Glasspen Bot (бота обратной связи).
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters

logger = logging.getLogger(__name__)

# ---------- Обработчики команд (для /command) ----------

async def link_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /link"""
    link_text = """
📚 **Ссылка на наш канал:**
[Литературный уголок](https://t.me/glass_pen)

**Как поделиться конкретным постом?**
1. Откройте нужный пост в канале
2. Нажмите на кнопку "↗️" (Поделиться)
3. Выберите "Скопировать ссылку"
"""
    await update.message.reply_text(link_text, parse_mode='Markdown')

async def contents_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /contents - показывает инлайн-клавиатуру для выбора раздела"""
    from src.bots.glasspen_bot.keyboards.main_menu import get_contents_keyboard
    reply_markup = get_contents_keyboard()
    await update.message.reply_text(
        "📚 **Выберите раздел:**",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def question_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /question - начинает диалог вопроса"""
    instruction = """
✍️ **Задать вопрос авторам**

Опишите, пожалуйста, ваш вопрос или пожелание. Мы прочитаем его и постараемся ответить в ближайшее время.

*Просто напишите ваш вопрос в чат...*
"""
    # Сохраняем состояние, что ждем вопрос
    context.user_data['awaiting_question'] = True
    await update.message.reply_text(instruction, parse_mode='Markdown')

# ---------- Обработчики кнопок и сообщений ----------

async def handle_inline_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик нажатий на инлайн-кнопки (для разделов оглавления)"""
    query = update.callback_query
    await query.answer()
    data = query.data

    # Генерация ответа в зависимости от раздела
    if data == "love_poems":
        response = "**Стихи о любви:**\n\n• 'Первая встреча'\n• 'Вечерний звон'\n• 'Без ответа'"
    elif data == "prose":
        response = "**Проза:**\n\n• 'Утренний туман'\n• 'Старый дом'"
    elif data == "analysis":
        response = "**Анализ произведений:**\n\n• 'Символика в поэзии'\n• 'Особенности стиля'"
    else:
        response = "Раздел не найден."

    await query.edit_message_text(response, parse_mode='Markdown')

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Главный обработчик ВСЕХ текстовых сообщений"""
    user_data = context.user_data
    text = update.message.text

    # 1. Проверяем, не нажата ли кнопка главного меню
    if text in ["📚 Ссылка на канал", "📖 Оглавление", "❓ Задать вопрос авторам"]:
        await handle_main_menu_buttons(update, context)
        return

    # 2. Проверяем, не ждём ли мы вопрос от пользователя
    if user_data.get('awaiting_question'):
        await process_user_question(update, context)
        return

    # 3. Если это любое другое текстовое сообщение
    await update.message.reply_text(
        "Используйте кнопки меню для навигации 🗺️",
        parse_mode='Markdown'
    )

async def handle_main_menu_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик нажатий на кнопки Reply-клавиатуры (главное меню)"""
    text = update.message.text
    if text == "📚 Ссылка на канал":
        await link_command(update, context)
    elif text == "📖 Оглавление":
        await contents_command(update, context)
    elif text == "❓ Задать вопрос авторам":
        await question_command(update, context)

async def process_user_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Логика обработки и пересылки вопроса от пользователя"""
    from src.bots.glasspen_bot.bot import GlasspenBot
    # Получаем экземпляр нашего бота, чтобы иметь доступ к его конфигурации
    # В конфигурации должны быть указаны admin_ids для пересылки
    user = update.message.from_user
    question_text = update.message.text

    # Формируем сообщение для админа
    admin_message = f"""
❓ **Новый вопрос от** @{user.username or 'без username'} ({user.first_name}):

{question_text}
"""
    # Логируем вопрос
    logger.info(f"Вопрос от user_id={user.id}: {question_text[:100]}...")

    # !!! ВАЖНО: Здесь нужна логика пересылки.
    # 1-й вариант (рекомендуется): Сохраняем админские ID в config бота при его создании.
    #    Тогда здесь мы можем получить бота из context и отправить сообщение.
    #    Пока оставляем заглушку:
    #    for admin_id in context.bot_data.get('admin_ids', []):
    #        await context.bot.send_message(chat_id=admin_id, text=admin_message, parse_mode='Markdown')
    #
    # 2-й вариант: Отправлять во внешний канал/чат по ID (ADMIN_CHAT_ID).
    #    Этот ID нужно будет добавить в extra_config бота в .env файле.
    #    Пример: BOT_GLASSPEN_ADMIN_CHAT_ID=-1001234567890

    # Временная заглушка - просто логируем
    logger.info(f"Вопрос для админа: {admin_message}")

    # Подтверждаем пользователю
    await update.message.reply_text(
        "✅ Спасибо! Ваш вопрос отправлен авторам. Мы ответим вам в ближайшее время.",
        parse_mode='Markdown'
    )
    # Сбрасываем состояние
    context.user_data['awaiting_question'] = False

def get_handlers():
    """Функция возвращает список обработчиков для регистрации в боте."""
    # CommandHandler будут добавлены в классе бота на основе списка команд
    return [
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message),
        # CallbackQueryHandler будет добавлен отдельно в классе бота
    ]
