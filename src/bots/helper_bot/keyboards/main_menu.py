"""
Клавиатуры для Helper Bot.
"""

from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime

def get_main_keyboard():
    """Основная клавиатура для HelperBot"""
    keyboard = [
        ['📝 Новая запись', '📖 Мои записи'],
        ['⚙️ Настройки', 'ℹ️ Помощь']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_inline_keyboard():
    """Inline-клавиатура для действий с записями"""
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