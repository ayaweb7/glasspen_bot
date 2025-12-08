"""
Обработчики команд бота.
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime

from src.bot.keyboards.main_menu import get_main_keyboard, get_inline_keyboard

logger = logging.getLogger(__name__)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user
    logger.info(f"Пользователь {user.id} ({user.username}) начал диалог")
    
    welcome_text = f"""
👋 Привет, {user.first_name}!

Я — Glasspen Bot, твой личный помощник для ведения записей и заметок.

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
/settings - настройки
"""
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=get_main_keyboard()
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    help_text = """
📚 **Помощь по командам:**

**Основные команды:**
/start - Начать диалог с ботом
/help - Показать это сообщение
/new - Создать новую запись
/list - Показать последние записи
/settings - Настройки бота

**Управление записями:**
• Используйте кнопку "📝 Новая запись" для создания
• "📖 Мои записи" для просмотра
• В inline-клавиатуре можно редактировать и удалять

**Техническая поддержка:**
Если возникли проблемы, свяжитесь с администратором.
"""
    
    await update.message.reply_text(
        help_text,
        parse_mode='Markdown'
    )

async def new_entry_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /new или кнопки 'Новая запись'"""
    user = update.effective_user
    
    # Сохраняем состояние - ждём текст записи
    context.user_data['waiting_for_entry'] = True
    
    await update.message.reply_text(
        "📝 *Создание новой записи*\n\n"
        "Пожалуйста, напишите текст вашей записи. "
        "Вы можете добавить теги, используя #тег.",
        parse_mode='Markdown',
        reply_markup=get_inline_keyboard()
    )

async def list_entries_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /list"""
    # В будущем здесь будет работа с БД
    # Пока имитация
    
    example_entries = [
        f"1. Запись от {datetime.now().strftime('%d.%m %H:%M')}: План на день",
        f"2. Запись от {(datetime.now()).strftime('%d.%m %H:%M')}: Идея для проекта",
        f"3. Запись от {(datetime.now()).strftime('%d.%m %H:%M')}: Список покупок"
    ]
    
    entries_text = "📖 *Ваши последние записи:*\n\n" + "\n\n".join(example_entries)
    
    await update.message.reply_text(
        entries_text,
        parse_mode='Markdown',
        reply_markup=get_inline_keyboard()
    )

async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /settings"""
    from src.bot.keyboards.main_menu import get_settings_keyboard
    
    settings_text = """
⚙️ **Настройки бота:**

• 🔔 Уведомления: Вкл
• 🎨 Тема: Светлая
• 🌐 Язык: Русский

Используйте кнопки ниже для изменения настроек.
"""
    
    await update.message.reply_text(
        settings_text,
        parse_mode='Markdown',
        reply_markup=get_settings_keyboard()
    )

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    user = update.effective_user
    text = update.message.text
    
    # Проверяем, ждём ли мы запись от пользователя
    if context.user_data.get('waiting_for_entry'):
        # Сохраняем запись
        context.user_data['waiting_for_entry'] = False
        
        # Имитируем сохранение
        logger.info(f"Пользователь {user.id} создал запись: {text[:50]}...")
        
        await update.message.reply_text(
            f"✅ Запись сохранена!\n\n"
            f"*Текст:* {text}\n\n"
            f"Запись можно найти в разделе \"📖 Мои записи\"",
            parse_mode='Markdown'
        )
        return
    
    # Обработка кнопок основного меню
    if text == '📝 Новая запись':
        await new_entry_command(update, context)
    elif text == '📖 Мои записи':
        await list_entries_command(update, context)
    elif text == '⚙️ Настройки':
        await settings_command(update, context)
    elif text == 'ℹ️ Помощь':
        await help_command(update, context)
    elif text == '⬅️ Назад':
        await update.message.reply_text(
            "Возвращаемся в главное меню",
            reply_markup=get_main_keyboard()
        )
    else:
        # Если не команда и не кнопка - просто эхо
        await update.message.reply_text(
            f"Вы написали: {text}\n\n"
            f"Используйте меню или команды для взаимодействия.",
            reply_markup=get_main_keyboard()
        )

async def button_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий inline-кнопок"""
    query = update.callback_query
    await query.answer()  # Ответить на callback, чтобы убрать "часики"
    
    user = query.from_user
    data = query.data
    
    logger.info(f"Пользователь {user.id} нажал кнопку: {data}")
    
    # Обработка разных кнопок
    if data == 'like':
        await query.edit_message_text(text="👍 Спасибо за оценку!")
    elif data == 'dislike':
        await query.edit_message_text(text="👎 Жаль, что не понравилось...")
    elif data == 'edit':
        await query.edit_message_text(text="✏️ Редактирование... (в разработке)")
    elif data == 'delete':
        await query.edit_message_text(text="🗑️ Удаление... (в разработке)")
