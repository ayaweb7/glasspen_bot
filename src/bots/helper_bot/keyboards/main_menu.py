"""
ПРОСТЫЕ клавиатуры для Helper Bot.
"""

from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

def get_main_keyboard():
    """Основная клавиатура меню"""
    keyboard = [
        ['📝 Новая запись', '📖 Мои записи'],
        ['📅 Сегодня', '⚙️ Настройки']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, input_field_placeholder="Выберите действие...")

def get_notes_keyboard(notes):
    """Inline-клавиатура для действий с записями (простая)"""
    buttons = []
    
    # Кнопки для первых 5 записей
    for i, note in enumerate(notes[:5], 1):
        preview = note.text[:20] + "..." if len(note.text) > 20 else note.text
        buttons.append([
            InlineKeyboardButton(f"{i}. {preview}", callback_data=f"view_{note.id}")
        ])
    
    # Кнопки навигации
    if len(notes) > 5:
        buttons.append([
            InlineKeyboardButton("⬅️ Назад", callback_data="page_prev"),
            InlineKeyboardButton("Вперёд ➡️", callback_data="page_next")
        ])
    
    buttons.append([
        InlineKeyboardButton("✏️ Редактировать", callback_data="edit_last"),
        InlineKeyboardButton("🗑️ Удалить", callback_data="delete_last")
    ])
    
    buttons.append([
        InlineKeyboardButton("🏠 В главное меню", callback_data="main_menu")
    ])
    
    return InlineKeyboardMarkup(buttons)

def get_yes_no_keyboard():
    """Простая клавиатура Да/Нет"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Да", callback_data="yes"),
            InlineKeyboardButton("❌ Нет", callback_data="no")
        ]
    ])

# Обработчик для inline-кнопок можно добавить позже
# async def handle_inline_buttons(update, context): ...