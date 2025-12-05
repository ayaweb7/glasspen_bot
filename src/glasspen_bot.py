# GLASSPEN_BOT.PY
# Запуск из командной строки: python glasspen_bot.py
# Основные импорты:
import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from telegram.ext import CallbackContext

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токен бота (получите у @BotFather)
BOT_TOKEN = "7918395635:AAEoAYwkrtorZqvwkksTB73QutUa0whCsBo"

# ID чата для пересылки вопросов (можно узнать через @userinfobot)
ADMIN_CHAT_ID = "7156086085"

# Обработчик команды /start
async def start_command(update: Update, context: CallbackContext) -> None:
    # Создаем кастомную клавиатуру
    keyboard = [
        ["📚 Ссылка на канал", "📖 Оглавление"],
        ["❓ Задать вопрос авторам"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    welcome_text = """
Приветствую в литературном уголке! 📚

Я помогу вам:
• Найти ссылку на наш канал
• Показать оглавление произведений  
• Направить ваш вопрос авторам

Выберите действие ниже 👇
"""
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

# Обработчик команды /link
async def link_command(update: Update, context: CallbackContext) -> None:
    link_text = """
📚 **Ссылка на наш канал:** 
[Литературный уголок](https://t.me/glass_pen)

**Как поделиться конкретным постом?**
1. Откройте нужный пост в канале
2. Нажмите на кнопку "↗️" (Поделиться)  
3. Выберите "Скопировать ссылку"
"""
    await update.message.reply_text(link_text, parse_mode='Markdown')

# Обработчик для инлайн-кнопок оглавления
async def handle_inline_buttons(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    
    # Обрабатываем нажатие на разные кнопки
    data = query.data
    
    if data == "love_poems":
        response = "**Стихи о любви:**\n\n• 'Первая встреча' - /post_1\n• 'Вечерний звон' - /post_2\n• 'Без ответа' - /post_3"
    elif data == "prose":
        response = "**Проза:**\n\n• 'Утренний туман' - /post_4\n• 'Старый дом' - /post_5"
    elif data == "analysis":
        response = "**Анализ произведений:**\n\n• 'Символика в поэзии' - /post_6\n• 'Особенности стиля' - /post_7"
    
    await query.edit_message_text(response, parse_mode='Markdown')

# Обработчик команды /contents
async def contents_command(update: Update, context: CallbackContext) -> None:
    # Создаем инлайн-клавиатуру
    keyboard = [
        [InlineKeyboardButton("💖 Стихи о любви", callback_data="love_poems")],
        [InlineKeyboardButton("📖 Проза", callback_data="prose")],
        [InlineKeyboardButton("🔍 Анализ произведений", callback_data="analysis")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "📚 **Выберите раздел:**",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# Обработчик для вопросов авторам
async def question_command(update: Update, context: CallbackContext) -> None:
    instruction = """
✍️ **Задать вопрос авторам**

Опишите, пожалуйста, ваш вопрос или пожелание. Мы прочитаем его и постараемся ответить в ближайшее время.

*Просто напишите ваш вопрос в чат...*
"""
    # Сохраняем состояние, что ждем вопрос
    context.user_data['awaiting_question'] = True
    await update.message.reply_text(instruction, parse_mode='Markdown')

# Обработчик текстовых сообщений (для вопросов)
async def handle_message(update: Update, context: CallbackContext) -> None:
    user_data = context.user_data
    
    # Проверяем, ждем ли мы вопрос от пользователя
    if user_data.get('awaiting_question'):
        user = update.message.from_user
        question_text = update.message.text
        
        # Формируем сообщение для админа
        admin_message = f"""
❓ **Новый вопрос от** @{user.username} ({user.first_name}):

{question_text}
"""
        # Пересылаем вопрос админу
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=admin_message,
            parse_mode='Markdown'
        )
        
        # Подтверждаем пользователю
        await update.message.reply_text(
            "✅ Спасибо! Ваш вопрос отправлен авторам. Мы ответим вам в ближайшее время.",
            parse_mode='Markdown'
        )
        
        # Сбрасываем состояние
        user_data['awaiting_question'] = False
    else:
        # Если это обычное сообщение, не связанное с вопросом
        await update.message.reply_text(
            "Используйте кнопки меню для навигации 🗺️",
            parse_mode='Markdown'
        )

# Обработчик кнопок главного меню
async def handle_main_menu_buttons(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    
    if text == "📚 Ссылка на канал":
        await link_command(update, context)
    elif text == "📖 Оглавление":
        await contents_command(update, context)
    elif text == "❓ Задать вопрос авторам":
        await question_command(update, context)

# Основная функция
def main():
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("link", link_command))
    application.add_handler(CommandHandler("contents", contents_command))
    application.add_handler(CommandHandler("question", question_command))
    
    # Обработчик инлайн-кнопок (для оглавления)
    application.add_handler(CallbackQueryHandler(handle_inline_buttons))
    
    # Обработчик текстовых сообщений (для вопросов)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Обработчик кнопок главного меню (используем Regex)
    application.add_handler(MessageHandler(
        filters.Regex(r'^(📚 Ссылка на канал|📖 Оглавление|❓ Задать вопрос авторам)$'),
        handle_main_menu_buttons
    ))
    
    # Запускаем бота
    print("Бот запущен...")
    application.run_polling()

if __name__ == '__main__':
    main()