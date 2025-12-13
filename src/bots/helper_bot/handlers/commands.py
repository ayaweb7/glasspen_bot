"""
Обработчики команд для Glasspen Bot.
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
from datetime import datetime

from src.bots.glasspen_bot.keyboards.main_menu import get_main_keyboard, get_inline_keyboard

logger = logging.getLogger(__name__)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user
    logger.info(f"[Glasspen] Пользователь {user.id} начал диалог")
    
    welcome_text = f"""
👋 Привет, {user.first_name}!

Я — Glasspen Bot, твой личный помощник для ведения записей.

✨ Что я умею:
• 📝 Создавать новые записи
• 📖 Хранить и просматривать старые записи
• 🔔 Напоминать о важном
• 🏷️ Организовывать по тегам

Используй меню ниже или команды:
/start - начать диалог
/help - помощь
/new - новая запись
/list - список записей
"""
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=get_main_keyboard()
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    help_text = """
📚 **Помощь по командам Glasspen Bot:**

**Основные команды:**
/start - Начать диалог с ботом
/help - Эта справка
/new - Создать новую запись
/list - Показать последние записи
/settings - Настройки бота

**Используйте кнопки для управления записями:**
• 📝 "Новая запись" для создания
• 📖 "Мои записи" для просмотра
• В inline-клавиатуре записи можно редактировать и удалять
"""
    
    await update.message.reply_text(
        help_text,
        parse_mode='Markdown'
    )

async def new_entry_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /new"""
    context.user_data['waiting_for_entry'] = True
    
    await update.message.reply_text(
        "📝 *Создание новой записи*\n\n"
        "Напишите текст вашей записи. Можно добавить теги через #тег.",
        parse_mode='Markdown',
        reply_markup=get_inline_keyboard()
    )

async def list_entries_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /list"""
    example_entries = [
        f"1. Запись от {datetime.now().strftime('%d.%m %H:%M')}: План на день",
        f"2. Запись от {(datetime.now()).strftime('%d.%m %H:%M')}: Идея для проекта",
    ]
    
    entries_text = "📖 *Ваши последние записи:*\n\n" + "\n\n".join(example_entries)
    
    await update.message.reply_text(
        entries_text,
        parse_mode='Markdown',
        reply_markup=get_inline_keyboard()
    )

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    text = update.message.text
    
    if context.user_data.get('waiting_for_entry'):
        context.user_data['waiting_for_entry'] = False
        
        await update.message.reply_text(
            f"✅ Запись сохранена!\n\n"
            f"*Текст:* {text}\n\n",
            parse_mode='Markdown'
        )
        return
    
    # Обработка кнопок
    if text == '📝 Новая запись':
        await new_entry_command(update, context)
    elif text == '📖 Мои записи':
        await list_entries_command(update, context)
    elif text == 'ℹ️ Помощь':
        await help_command(update, context)
    else:
        await update.message.reply_text(
            f"Вы написали: {text}\n\n"
            f"Используйте меню или команды.",
            reply_markup=get_main_keyboard()
        )

async def button_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик inline-кнопок"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == 'like':
        await query.edit_message_text(text="👍 Спасибо!")
    elif data == 'dislike':
        await query.edit_message_text(text="👎 Жаль...")
    elif data == 'edit':
        await query.edit_message_text(text="✏️ Редактирование...")
    elif data == 'delete':
        await query.edit_message_text(text="🗑️ Удаление...")

def get_handlers():
    """Получить все обработчики команд для этого бота"""
    return [
        CommandHandler("start", start_command),
        CommandHandler("help", help_command),
        CommandHandler("new", new_entry_command),
        CommandHandler("list", list_entries_command),
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message),
        # CallbackQueryHandler добавляется в классе бота
    ]
