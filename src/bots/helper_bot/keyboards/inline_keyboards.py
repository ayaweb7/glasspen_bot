"""
Inline-клавиатуры для Helper Bot.
Каждая функция возвращает InlineKeyboardMarkup для конкретного сценария.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List, Optional

def get_main_menu_keyboard():
    """Главное меню с inline-кнопками (альтернатива reply-клавиатуре)"""
    keyboard = [
        [
            InlineKeyboardButton("📝 Новая запись", callback_data='new_note'),
            InlineKeyboardButton("📖 Мои записи", callback_data='list_notes')
        ],
        [
            InlineKeyboardButton("📅 Сегодня", callback_data='today_notes'),
            InlineKeyboardButton("📊 Статистика", callback_data='stats')
        ],
        [
            InlineKeyboardButton("🏷️ Категории", callback_data='categories'),
            InlineKeyboardButton("🆘 Помощь", callback_data='help')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_notes_list_keyboard(notes: List, page: int = 0, total_pages: int = 1):
    """
    Клавиатура для списка записей (/list).
    Каждая запись получает кнопки действий.
    
    Args:
        notes: Список объектов Note для текущей страницы
        page: Текущая страница (0-based)
        total_pages: Всего страниц
    """
    keyboard = []
    
    # Кнопки для каждой записи
    for note in notes:
        # Иконка важности
        icon = "⭐ " if note.is_important else ""
        
        # Основная кнопка с текстом записи (короткая версия)
        text_preview = note.text[:25] + "..." if len(note.text) > 25 else note.text
        main_button = InlineKeyboardButton(
            f"{icon}{text_preview}",
            callback_data=f"view_{note.id[:8]}"
        )
        
        # Кнопки действий в строке под записью
        action_buttons = [
            InlineKeyboardButton("👁️", callback_data=f"view_{note.id[:8]}"),
            InlineKeyboardButton("✏️", callback_data=f"edit_{note.id[:8]}"),
            InlineKeyboardButton("🏷️", callback_data=f"category_{note.id[:8]}"),
            InlineKeyboardButton("⭐" if not note.is_important else "➖", 
                               callback_data=f"important_{note.id[:8]}_toggle"),
            InlineKeyboardButton("🗑️", callback_data=f"delete_{note.id[:8]}")
        ]
        
        keyboard.append([main_button])
        keyboard.append(action_buttons)
    
    # Пагинация (если есть несколько страниц)
    if total_pages > 1:
        nav_buttons = []
        if page > 0:
            nav_buttons.append(InlineKeyboardButton("◀️ Назад", callback_data=f"page_{page-1}"))
        
        nav_buttons.append(InlineKeyboardButton(f"{page+1}/{total_pages}", callback_data='current_page'))
        
        if page < total_pages - 1:
            nav_buttons.append(InlineKeyboardButton("Вперёд ▶️", callback_data=f"page_{page+1}"))
        
        if nav_buttons:
            keyboard.append(nav_buttons)
    
    # Кнопки общего назначения
    keyboard.append([
        InlineKeyboardButton("📝 Новая запись", callback_data='new_note'),
        InlineKeyboardButton("🏠 Главное меню", callback_data='main_menu')
    ])
    
    return InlineKeyboardMarkup(keyboard)

def get_note_actions_keyboard(note_id_short: str, current_category: str = "Общее"):
    """
    Клавиатура действий для конкретной записи (после просмотра).
    
    Args:
        note_id_short: Короткий ID записи (первые 8 символов)
        current_category: Текущая категория записи
    """
    keyboard = [
        [
            InlineKeyboardButton("✏️ Изменить текст", callback_data=f"edit_{note_id_short}"),
            InlineKeyboardButton("🏷️ Сменить категорию", callback_data=f"category_{note_id_short}")
        ],
        [
            InlineKeyboardButton("⭐ Важная/Обычная", callback_data=f"important_{note_id_short}_toggle"),
            InlineKeyboardButton("🗑️ Удалить", callback_data=f"delete_{note_id_short}")
        ],
        [
            InlineKeyboardButton("📋 К списку записей", callback_data='list_notes'),
            InlineKeyboardButton("🏠 Главное меню", callback_data='main_menu')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_confirmation_keyboard(action: str, note_id: str, 
                             yes_text: str = "✅ Да", 
                             no_text: str = "❌ Нет"):
    """
    Клавиатура подтверждения действий.
    
    Args:
        action: Тип действия ('delete', 'category_change', etc.)
        note_id: ID записи
        yes_text: Текст для кнопки подтверждения
        no_text: Текст для кнопки отмены
    """
    keyboard = [
        [
            InlineKeyboardButton(yes_text, callback_data=f"{action}_confirm_{note_id}"),
            InlineKeyboardButton(no_text, callback_data='cancel')
        ]
    ]
    
    if action == 'delete':
        keyboard.append([
            InlineKeyboardButton("👁️ Просмотреть запись", callback_data=f"view_{note_id}")
        ])
    
    keyboard.append([
        InlineKeyboardButton("🏠 Главное меню", callback_data='main_menu')
    ])
    
    return InlineKeyboardMarkup(keyboard)

def get_categories_keyboard_for_note(note_id_short: str, user_categories: List[str]):
    """
    Клавиатура выбора категории для конкретной записи.
    
    Args:
        note_id_short: ID записи
        user_categories: Список категорий пользователя
    """
    keyboard = []
    
    # Показываем популярные категории (первые 6)
    for category in user_categories[:6]:
        keyboard.append([
            InlineKeyboardButton(f"📁 {category}", callback_data=f"category_{note_id_short}_{category}")
        ])
    
    # Кнопка для ввода новой категории
    keyboard.append([
        InlineKeyboardButton("➕ Новая категория", callback_data=f"category_new_{note_id_short}")
    ])
    
    # Кнопки отмены
    keyboard.append([
        InlineKeyboardButton("👁️ Просмотреть запись", callback_data=f"view_{note_id_short}"),
        InlineKeyboardButton("❌ Отмена", callback_data='cancel')
    ])
    
    return InlineKeyboardMarkup(keyboard)

def get_pagination_keyboard(current_page: int, total_pages: int, 
                           base_callback: str = 'page'):
    """
    Универсальная клавиатура пагинации.
    
    Args:
        current_page: Текущая страница (0-based)
        total_pages: Всего страниц
        base_callback: Базовое имя для callback_data
    """
    keyboard = []
    
    if total_pages > 1:
        buttons = []
        
        if current_page > 0:
            buttons.append(InlineKeyboardButton("◀️", callback_data=f"{base_callback}_{current_page-1}"))
        
        # Показываем номера страниц вокруг текущей
        start_page = max(0, current_page - 2)
        end_page = min(total_pages, current_page + 3)
        
        for p in range(start_page, end_page):
            if p == current_page:
                buttons.append(InlineKeyboardButton(f"·{p+1}·", callback_data='current'))
            else:
                buttons.append(InlineKeyboardButton(str(p+1), callback_data=f"{base_callback}_{p}"))
        
        if current_page < total_pages - 1:
            buttons.append(InlineKeyboardButton("▶️", callback_data=f"{base_callback}_{current_page+1}"))
        
        keyboard.append(buttons)
    
    keyboard.append([
        InlineKeyboardButton("🏠 Главное меню", callback_data='main_menu')
    ])
    
    return InlineKeyboardMarkup(keyboard)