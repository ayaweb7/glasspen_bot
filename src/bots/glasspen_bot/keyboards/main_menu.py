"""
Клавиатуры для Glasspen Bot.
"""

from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

# ---------- Reply-клавиатура (главное меню) ----------
def get_main_keyboard():
    """Возвращает основную Reply-клавиатуру меню."""
    keyboard = [
        ["📚 Ссылка на канал", "📖 Оглавление"],
        ["❓ Задать вопрос авторам"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, input_field_placeholder="Выберите действие...")

# ---------- Inline-клавиатуры ----------
def get_contents_keyboard():
    """Возвращает Inline-клавиатуру для выбора раздела оглавления."""
    keyboard = [
        [InlineKeyboardButton("💖 Стихи о любви", callback_data="love_poems")],
        [InlineKeyboardButton("📖 Проза", callback_data="prose")],
        [InlineKeyboardButton("🔍 Анализ произведений", callback_data="analysis")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main"), InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]  # Пример кнопок навигации
    ]
    return InlineKeyboardMarkup(keyboard)

# В будущем здесь можно добавить другие клавиатуры, например:
# def get_back_keyboard(): ...