"""
Клавиатуры для основного меню бота.
"""

from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

def get_main_keyboard():
    """Основная клавиатура"""
    keyboard = [
        ['📝 Новая запись', '📖 Мои записи'],
        ['⚙️ Настройки', 'ℹ️ Помощь']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_inline_keyboard():
    """Inline-клавиатура для действий"""
    keyboard = [
        [
            InlineKeyboardButton("👍 Нравится", callback_data='like'),
            InlineKeyboardButton("👎 Не нравится", callback_data='dislike')
        ],
        [
            InlineKeyboardButton("✏️ Редактировать", callback_data='edit'),
            InlineKeyboardButton("🗑️ Удалить", callback_data='delete')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_settings_keyboard():
    """Клавиатура настроек"""
    keyboard = [
        ['🔔 Уведомления', '🎨 Тема'],
        ['🌐 Язык', '⬅️ Назад']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
