"""
ПРОСТЫЕ обработчики команд для Helper Bot.
Без сложного FSM. Только базовый CRUD.
"""

import logging
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler, filters

from src.core.models import Note
from src.core.note_manager import note_manager
from src.bots.helper_bot.keyboards.main_menu import get_main_keyboard, get_notes_keyboard
from typing import Optional  # Для аннотации _find_note_by_short_id

# Добавьте эти импорты в начало commands.py, если их там нет:
from src.bots.helper_bot.keyboards.inline_keyboards import (
    get_main_menu_keyboard,
    get_notes_list_keyboard,
    get_note_actions_keyboard,
    get_confirmation_keyboard,
    get_categories_keyboard_for_note,
    get_pagination_keyboard
)

logger = logging.getLogger(__name__)

# ---- БАЗОВЫЕ КОМАНДЫ ----

# 1. ========== Приветствие и Главное меню ==========
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Приветствие и главное меню"""
    user = update.effective_user
    
    welcome_text = f"""👋 Привет, {user.first_name}!

Я — твой простой помощник для записей.

*📝 Быстрые команды:*
• /new - Новая запись
• /list - Последние 10 записей  
• /today - Записи за сегодня
• /categories - Все категории

*⚙️ Управление последней записью:*
• /set_category - Изменить категорию
• /set_reminder - Добавить напоминание
• /mark_important - Отметить важным

Используйте кнопки внизу для быстрого доступа."""
    
    # Очищаем контекст
    context.user_data.clear()
    
    await update.message.reply_text(
        welcome_text,
        parse_mode='Markdown',
        reply_markup=get_main_keyboard()
    )
    logger.info(f"[Helper] Старт для {user.id}")

# 2. ========== Полная справка по командам ==========
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Полная справка по всем командам"""
    help_text = """
*🆘 ПОЛНАЯ СПРАВКА ПО КОМАНДАМ*

*📝 СОЗДАНИЕ И ПРОСМОТР:*
`/new` - Новая запись (просто напишите текст после команды)
`/list [страница]` - Последние записи (по 5 на странице)
`/view ID` - Полный текст записи (ID из /list)
`/today` - Записи за сегодня
`/yesterday` - Записи за вчера
`/search текст` - Поиск по всем записям

*✏️ РЕДАКТИРОВАНИЕ:*
`/edit ID новый_текст` - Изменить текст записи
`/set_category [ID] категория` - Изменить категорию
`/mark_important [ID] [off]` - Отметить важным/снять отметку
`/delete ID [confirm]` - Удалить запись (требует подтверждения)

*📊 АНАЛИТИКА:*
`/categories` - Все категории с статистикой
`/stats` - Общая статистика записей

*⚙️ СИСТЕМА:*
`/start` - Главное меню
`/help` - Эта справка

*💡 СОВЕТЫ:*
• Короткий ID записи (первые 8 символов) можно получить из /list
• Если не указать ID в некоторых командах, они применятся к последней записи
• Команды в сообщениях кликабельны - можно копировать
• Используйте теги # в тексте для организации

*Примеры:*
`/new Купить молоко #покупки #дом`
`/view a1b2c3d4`
`/edit a1b2c3d4 Купить молоко и хлеб`
`/set_category a1b2c3d4 Покупки`
`/search молоко`
"""
    
    await update.message.reply_text(
        help_text,
        parse_mode='Markdown',
        reply_markup=get_main_keyboard()
    )

# ---- ПРОСТОЕ СОЗДАНИЕ ЗАПИСИ ----

# 3. ========== Создание Новой записи ==========
async def new_entry_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начинает создание новой записи - просто запрашивает текст"""
    await update.message.reply_text(
        "📝 *Создание новой записи*\n\n"
        "Просто напишите текст записи. Можно добавить теги через #.\n\n"
        "Пример: \"Купить молоко #покупки #дом\"\n\n"
        "Или отправьте /cancel для отмены.",
        parse_mode='Markdown'
    )
    # Устанавливаем флаг, что ждём текст
    context.user_data['waiting_for_note'] = True

# 4. ========== Обработка Новой записи - редактирование существующих ==========
async def handle_note_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает все текстовые сообщения (создание, редактирование, категории)"""
    text = update.message.text.strip()
    user = update.effective_user
    
    # 1. КОМАНДА /CANCEL в любом состоянии
    if text == '/cancel':
        await cancel_command(update, context)
        return
    
    # 2. РЕДАКТИРОВАНИЕ существующей записи
    if 'editing_note_id' in context.user_data:
        await _handle_edit_text_input(update, context, text, user.id)
        return
    
    # 3. ВВОД НОВОЙ КАТЕГОРИИ
    if 'awaiting_category_for' in context.user_data:
        await _handle_new_category_input(update, context, text)
        return
    
    # 4. СОЗДАНИЕ НОВОЙ ЗАПИСИ
    if context.user_data.get('waiting_for_note'):
        await _handle_new_note_input(update, context, text, user.id)
        return
    
    # 5. ОБЫЧНОЕ СООБЩЕНИЕ - обработка кнопок главного меню
    await handle_regular_message(update, context)

# 4.1. ========== Обработка ввода нового текста ==========
async def _handle_edit_text_input(update, context, text, user_id):
    """Обрабатывает ввод нового текста для редактируемой записи"""
    note_id = context.user_data['editing_note_id']
    note_id_short = context.user_data.get('editing_note_short_id', note_id[:8])
    
    # Валидация
    if len(text) < 3:
        await update.message.reply_text("❌ Текст слишком короткий. Нужно минимум 3 символа.")
        return
    
    # Обновляем запись
    success = note_manager.update_note(
        user_id=user_id,
        note_id=note_id,
        updates={"text": text}
    )
    
    if success:
        # Очищаем контекст
        context.user_data.pop('editing_note_id', None)
        context.user_data.pop('editing_note_short_id', None)
        
        await update.message.reply_text(
            f"✅ Запись `{note_id_short}` обновлена!\n\n"
            f"Новый текст: {text[:80]}...",
            parse_mode='Markdown',
            reply_markup=get_main_keyboard()
        )
    else:
        await update.message.reply_text(
            "❌ Не удалось обновить запись.",
            reply_markup=get_main_keyboard()
        )

# 4.2. ========== Обработка ввода новой записи ==========
async def _handle_new_note_input(update, context, text, user_id):
    """Обрабатывает ввод текста для новой записи"""
    # Валидация
    if len(text) < 3:
        await update.message.reply_text("❌ Текст слишком короткий. Нужно минимум 3 символа.")
        return
    
    # Извлекаем теги
    import re
    tags = re.findall(r'#(\w+)', text)
    
    # Создаём и сохраняем запись
    try:
        note = Note(
            user_id=user_id,
            text=text,
            category="Общее",
            tags=tags[:5] if tags else []
        )
        
        saved_note = note_manager.add_note(note)
        
        # Очищаем флаг ожидания
        context.user_data.pop('waiting_for_note', None)
        
        # Подтверждение
        success_msg = f"""
✅ *Запись сохранена!*

📅 {saved_note.created_at.strftime('%d.%m.%Y %H:%M')}
🏷️ Категория: {saved_note.category}
{"🏷️ Теги: " + ", ".join([f"#{t}" for t in saved_note.tags]) if saved_note.tags else ""}

ID: `{saved_note.id[:8]}`
"""
        await update.message.reply_text(
            success_msg,
            parse_mode='Markdown',
            reply_markup=get_main_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Ошибка сохранения: {e}")
        await update.message.reply_text(
            f"❌ Ошибка при сохранении: {str(e)[:100]}",
            reply_markup=get_main_keyboard()
        )

# ---- ПРОСМОТР ЗАПИСЕЙ (улучшенная версия) ----

# 5. ========== Показ последних записей ==========
async def list_entries_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает записи пользователя с inline-кнопками для управления"""
    user = update.effective_user
    all_notes = note_manager.get_all_notes(user.id)
    
    if not all_notes:
        await update.message.reply_text(
            "📭 У вас ещё нет записей.\n\nНачните с команды /new",
            reply_markup=get_main_keyboard()
        )
        return
    
    # Сортируем по дате (новые сверху)
    all_notes.sort(key=lambda x: x.created_at, reverse=True)
    
    # Определяем запрошенную страницу
    page = 0
    if context.args and context.args[0].isdigit():
        page = int(context.args[0]) - 1
        page = max(0, page)  # Не меньше 0
    
    # Сохраняем все записи в контексте для быстрого доступа по короткому ID
    context.user_data['notes_cache'] = {note.id[:8]: note for note in all_notes}
    
    # Разбиваем на страницы (по 5 записей на страницу)
    notes_per_page = 5
    total_pages = (len(all_notes) + notes_per_page - 1) // notes_per_page  # Округление вверх
    
    # Проверяем, что запрошенная страница существует
    if page >= total_pages:
        page = total_pages - 1
    
    start_idx = page * notes_per_page
    end_idx = start_idx + notes_per_page
    page_notes = all_notes[start_idx:end_idx]
    
    # Формируем текст сообщения
    message_text = f"📋 *Ваши записи* (страница {page+1}/{total_pages})\n\n"
    message_text += f"Всего записей: *{len(all_notes)}*\n"
    
    if total_pages > 1:
        message_text += "Используйте кнопки ниже для навигации.\n"
    
    message_text += "\n┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈\n"
    
    # Получаем inline-клавиатуру для этой страницы
    reply_markup = get_notes_list_keyboard(
        notes=page_notes,
        page=page,
        total_pages=total_pages
    )
    
    # Отправляем или редактируем сообщение
    if update.message:  # Если команда вызвана из чата
        await update.message.reply_text(
            message_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    else:  # Если это callback от кнопки пагинации
        query = update.callback_query
        await query.edit_message_text(
            message_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

# 6. ========== Полный текст записи с inline-кнопками ==========
async def view_note_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает полный текст записи с inline-кнопками"""
    user = update.effective_user
    
    # Если команда вызвана из чата с аргументом
    if context.args:
        note_id_short = context.args[0].strip()
        note = _find_note_by_short_id(user.id, note_id_short, context)
        
        if not note:
            await update.message.reply_text(
                f"❌ Запись с ID `{note_id_short}` не найдена.",
                parse_mode='Markdown'
            )
            return
        
        await _show_note_with_buttons(update, context, note, user.id)
    
    # Если вызвана без аргументов, показываем последнюю запись
    else:
        notes = note_manager.get_recent_notes(user.id, limit=1)
        if not notes:
            await update.message.reply_text(
                "У вас ещё нет записей. Создайте первую с помощью /new",
                reply_markup=get_main_keyboard()
            )
            return
        
        await _show_note_with_buttons(update, context, notes[0], user.id)

# 6.1. ========== Показывает запись с inline-кнопками действий ==========
async def _show_note_with_buttons(update, context, note, user_id):
    """Показывает запись с inline-кнопками действий"""
    # Форматируем полный текст записи
    full_text = f"""
📄 *Запись `{note.id[:8]}`*

*Создана:* {note.created_at.strftime('%d.%m.%Y в %H:%M')}
*Изменена:* {note.updated_at.strftime('%d.%m.%Y в %H:%M')}
*Категория:* {note.category}
*Важность:* {'⭐ ВАЖНАЯ' if note.is_important else 'Обычная'}
"""
    
    if note.tags:
        tags_str = " ".join([f"#{t}" for t in note.tags])
        full_text += f"*Теги:* {tags_str}\n"
    
    if note.reminder_at:
        reminder_str = note.reminder_at.strftime('%d.%m.%Y в %H:%M')
        full_text += f"*⏰ Напоминание:* {reminder_str}\n"
    
    if note.comment:
        full_text += f"*💬 Комментарий:* {note.comment}\n"
    
    full_text += f"\n*Текст записи:*\n{note.text}"
    
    # Получаем клавиатуру действий
    reply_markup = get_note_actions_keyboard(note.id[:8], note.category)
    
    # Отправляем или редактируем сообщение
    if update.message:  # Команда из чата
        await update.message.reply_text(
            full_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    else:  # Callback от inline-кнопки
        query = update.callback_query
        await query.edit_message_text(
            full_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

# 7. ========== Поиск записи по тексту ==========
async def search_notes_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ищет записи по тексту"""
    user = update.effective_user
    
    if not context.args:
        await update.message.reply_text(
            "Укажите текст для поиска. Пример: `/search встреча`",
            parse_mode='Markdown'
        )
        return
    
    search_query = " ".join(context.args).lower()
    all_notes = note_manager.get_all_notes(user.id)
    
    # Простой поиск по тексту
    found_notes = [
        note for note in all_notes
        if search_query in note.text.lower()
    ]
    
    if not found_notes:
        await update.message.reply_text(
            f"🔍 По запросу \"{search_query}\" ничего не найдено.",
            reply_markup=get_main_keyboard()
        )
        return
    
    # Показываем найденные записи
    search_text = f"🔍 *Найдено записей: {len(found_notes)}*\n\n"
    
    for i, note in enumerate(found_notes[:10], 1):  # Ограничиваем 10 результатами
        date_str = note.created_at.strftime('%d.%m %H:%M')
        preview = note.text[:60] + "..." if len(note.text) > 60 else note.text
        
        # Подсветка найденного текста в preview (простая версия)
        if search_query in preview.lower():
            # Находим позицию поискового запроса
            idx = preview.lower().find(search_query)
            if idx >= 0:
                # Вырезаем фрагмент с контекстом
                start = max(0, idx - 20)
                end = min(len(preview), idx + len(search_query) + 20)
                if start > 0:
                    preview = "..." + preview[start:end] + "..."
                else:
                    preview = preview[start:end] + "..."
        
        search_text += f"{i}. `{note.id[:8]}` *{date_str}* - {preview}\n"
    
    if len(found_notes) > 10:
        search_text += f"\n... и ещё {len(found_notes) - 10} записей.\n"
    
    search_text += f"\nИспользуйте `/view ID` для просмотра полного текста."
    
    # Сохраняем найденные записи в кэш для быстрого доступа
    context.user_data['notes_cache'] = {note.id[:8]: note for note in found_notes}
    
    await update.message.reply_text(
        search_text,
        parse_mode='Markdown',
        reply_markup=get_main_keyboard()
    )

# 8. ========== Записи за Сегодня ==========
async def today_entries_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает записи за сегодня"""
    user = update.effective_user
    today = datetime.now().date()
    
    all_notes = note_manager.get_all_notes(user.id)
    today_notes = [
        note for note in all_notes
        if note.created_at.date() == today
    ]
    
    if not today_notes:
        await update.message.reply_text(
            "📅 Сегодня ещё нет записей.\n\nСоздайте первую с помощью /new",
            reply_markup=get_main_keyboard()
        )
        return
    
    today_text = f"📅 *Записи за сегодня ({today.strftime('%d.%m.%Y')}):*\n\n"
    for i, note in enumerate(today_notes, 1):
        time_str = note.created_at.strftime('%H:%M')
        preview = note.text[:60] + "..." if len(note.text) > 60 else note.text
        today_text += f"{i}. *{time_str}* - {preview}\n"
    
    await update.message.reply_text(today_text, parse_mode='Markdown')

# ---- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ----

# 9. ========== Поиск записи по ID ==========
def _find_note_by_short_id(user_id: int, short_id: str, context) -> Optional[Note]:
    """
    Находит запись по короткому ID.
    Сначала ищет в кэше context.user_data['notes_cache'],
    потом среди всех записей пользователя.
    """
    # Пытаемся найти в кэше (из /list или /search)
    if 'notes_cache' in context.user_data:
        note = context.user_data['notes_cache'].get(short_id)
        if note:
            return note
    
    # Ищем среди всех записей пользователя
    all_notes = note_manager.get_all_notes(user_id)
    for note in all_notes:
        if note.id.startswith(short_id):
            # Обновляем кэш для будущих обращений
            if 'notes_cache' not in context.user_data:
                context.user_data['notes_cache'] = {}
            context.user_data['notes_cache'][short_id] = note
            return note
    
    return None

# ---- УПРАВЛЕНИЕ ЗАПИСЯМИ (отдельные команды) ----

# 10. ========== Категория последней записи ==========
async def set_category_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Устанавливает категорию для последней записи"""
    user = update.effective_user
    
    # Получаем последнюю запись пользователя
    notes = note_manager.get_recent_notes(user.id, limit=1)
    if not notes:
        await update.message.reply_text(
            "У вас ещё нет записей. Сначала создайте запись с помощью /new",
            reply_markup=get_main_keyboard()
        )
        return
    
    last_note = notes[0]
    
    # Если в аргументах команды указана категория
    if context.args:
        new_category = " ".join(context.args)
        note_manager.update_note(user.id, last_note.id, {"category": new_category})
        await update.message.reply_text(
            f"✅ Категория изменена на: {new_category}",
            reply_markup=get_main_keyboard()
        )
    else:
        # Запрашиваем категорию
        await update.message.reply_text(
            f"Текущая категория: *{last_note.category}*\n\n"
            "Введите новую категорию:",
            parse_mode='Markdown'
        )
        context.user_data['setting_category_for'] = last_note.id

# 11. ========== Заглушка напоминания последней записи ==========
async def set_reminder_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Устанавливает напоминание для последней записи (заглушка)"""
    await update.message.reply_text(
        "⏰ Функция напоминаний будет добавлена позже.\n\n"
        "Пока что вы можете:\n"
        "1. Использовать /list для просмотра записей\n"
        "2. Установить категорию через /set_category\n"
        "3. Отметить важное через /mark_important",
        reply_markup=get_main_keyboard()
    )

# 12. ========== Отметка последней записи как важной ==========
async def mark_important_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмечает последнюю запись как важную"""
    user = update.effective_user
    notes = note_manager.get_recent_notes(user.id, limit=1)
    
    if not notes:
        await update.message.reply_text("Нет записей для отметки.", reply_markup=get_main_keyboard())
        return
    
    last_note = notes[0]
    note_manager.update_note(user.id, last_note.id, {"is_important": True})
    
    await update.message.reply_text(
        f"✅ Запись отмечена как важная:\n\n{last_note.text[:100]}...",
        reply_markup=get_main_keyboard()
    )

# 13. ========== Редактирование записи ==========
async def edit_note_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Изменяет текст записи по её ID"""
    user = update.effective_user
    
    if len(context.args) < 2:
        await update.message.reply_text(
            "❌ *Использование:* `/edit ID новый_текст`\n\n"
            "Пример: `/edit a1b2c3d4 Нужно купить хлеб и молоко`\n"
            "ID можно посмотреть в списке записей (/list).",
            parse_mode='Markdown'
        )
        return
    
    note_id_short = context.args[0].strip()
    new_text = " ".join(context.args[1:])  # Весь остальной текст после ID
    
    # Находим запись
    note = _find_note_by_short_id(user.id, note_id_short, context)
    if not note:
        await update.message.reply_text(
            f"❌ Запись с ID `{note_id_short}` не найдена.",
            parse_mode='Markdown'
        )
        return
    
    # Обновляем запись
    success = note_manager.update_note(
        user_id=user.id,
        note_id=note.id,
        updates={"text": new_text}
    )
    
    if success:
        # Формируем ответ с сравнением
        old_preview = note.text[:50] + "..." if len(note.text) > 50 else note.text
        new_preview = new_text[:50] + "..." if len(new_text) > 50 else new_text
        
        response = f"""
*✅ Запись обновлена!*

*Было:* {old_preview}
*Стало:* {new_preview}

ID: `{note.id[:8]}`
Время изменения: {datetime.now().strftime('%H:%M')}
"""
        await update.message.reply_text(
            response,
            parse_mode='Markdown',
            reply_markup=get_main_keyboard()
        )
    else:
        await update.message.reply_text(
            "❌ Не удалось обновить запись.",
            reply_markup=get_main_keyboard()
        )

# 14. ========== Изменение категории ==========
async def set_category_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Изменяет категорию записи по ID"""
    user = update.effective_user
    
    if len(context.args) < 2:
        # Если ID не указан, работаем с последней записью
        notes = note_manager.get_recent_notes(user.id, limit=1)
        if not notes:
            await update.message.reply_text(
                "У вас ещё нет записей. Сначала создайте запись с помощью /new",
                reply_markup=get_main_keyboard()
            )
            return
        
        last_note = notes[0]
        if len(context.args) == 1:
            # Только новая категория указана
            new_category = context.args[0]
            note_id_short = last_note.id[:8]
        else:
            # Ничего не указано - показываем текущую категорию
            await update.message.reply_text(
                f"*Текущая категория:* {last_note.category}\n\n"
                "Используйте: `/set_category ID новая_категория`\n"
                f"Пример: `/set_category {last_note.id[:8]} Работа`",
                parse_mode='Markdown'
            )
            return
    else:
        # Указаны и ID, и категория
        note_id_short = context.args[0]
        new_category = " ".join(context.args[1:])
    
    # Находим запись
    note = _find_note_by_short_id(user.id, note_id_short, context)
    if not note:
        await update.message.reply_text(
            f"❌ Запись с ID `{note_id_short}` не найдена.",
            parse_mode='Markdown'
        )
        return
    
    # Обновляем категорию
    success = note_manager.update_note(
        user_id=user.id,
        note_id=note.id,
        updates={"category": new_category}
    )
    
    if success:
        # ПОЛУЧАЕМ ОБНОВЛЁННУЮ ЗАПИСЬ
        updated_note = note_manager.get_note(user.id, note.id)
        
        response = f"""
*✅ Категория изменена!*

Запись: `{note.id[:8]}`
Старая категория: {note.category}
Новая категория: *{updated_note.category if updated_note else new_category}*

Текст записи: {note.text[:60]}...
"""
        await update.message.reply_text(
            response,
            parse_mode='Markdown',
            reply_markup=get_main_keyboard()
        )
    else:
        await update.message.reply_text(
            "❌ Не удалось изменить категорию.",
            reply_markup=get_main_keyboard()
        )

# 15. ========== Отметка о важности ==========
async def mark_important_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмечает запись как важную или снимает отметку"""
    user = update.effective_user
    
    if not context.args:
        # Если ID не указан, работаем с последней записью
        notes = note_manager.get_recent_notes(user.id, limit=1)
        if not notes:
            await update.message.reply_text(
                "У вас ещё нет записей.",
                reply_markup=get_main_keyboard()
            )
            return
        
        last_note = notes[0]
        note_id_short = last_note.id[:8]
        toggle = True  # По умолчанию отмечаем как важную
    else:
        note_id_short = context.args[0]
        # Если указан второй аргумент "off", снимаем отметку
        toggle = len(context.args) < 2 or context.args[1].lower() != 'off'
    
    # Находим запись
    note = _find_note_by_short_id(user.id, note_id_short, context)
    if not note:
        await update.message.reply_text(
            f"❌ Запись с ID `{note_id_short}` не найдена.",
            parse_mode='Markdown'
        )
        return
    
    # Определяем новое состояние
    new_importance = toggle
    
    # Обновляем запись
    success = note_manager.update_note(
        user_id=user.id,
        note_id=note.id,
        updates={"is_important": new_importance}
    )
    
    if success:
        status = "⭐ ОТМЕЧЕНА КАК ВАЖНАЯ" if new_importance else "Снята отметка важности"
        icon = "⭐" if new_importance else "➖"
        
        response = f"""
{icon} *{status}*

Запись: `{note.id[:8]}`
Текст: {note.text[:80]}...

Используйте снова эту команду, чтобы { 'снять отметку' if new_importance else 'вернуть отметку' }.
"""
        await update.message.reply_text(
            response,
            parse_mode='Markdown',
            reply_markup=get_main_keyboard()
        )
    else:
        await update.message.reply_text(
            "❌ Не удалось изменить статус важности.",
            reply_markup=get_main_keyboard()
        )

# 16. ========== Удаление записи с подтверждением ==========
async def delete_note_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Удаляет запись по ID (требует подтверждения)"""
    user = update.effective_user
    
    if not context.args:
        await update.message.reply_text(
            "❌ *Использование:* `/delete ID [confirm]`\n\n"
            "Пример: `/delete a1b2c3d4` - покажет запись для подтверждения\n"
            "Пример: `/delete a1b2c3d4 confirm` - сразу удалит\n\n"
            "ID можно посмотреть в списке записей (/list).",
            parse_mode='Markdown'
        )
        return
    
    note_id_short = context.args[0]
    immediate_confirm = len(context.args) > 1 and context.args[1].lower() == 'confirm'
    
    # Находим запись
    note = _find_note_by_short_id(user.id, note_id_short, context)
    if not note:
        await update.message.reply_text(
            f"❌ Запись с ID `{note_id_short}` не найдена.",
            parse_mode='Markdown'
        )
        return
    
    # Если не требуется немедленное подтверждение, показываем запись и запрашиваем
    if not immediate_confirm:
        preview = note.text[:100] + "..." if len(note.text) > 100 else note.text
        
        warning = f"""
*⚠️ Вы действительно хотите удалить эту запись?*

`{note.id[:8]}` - *{note.created_at.strftime('%d.%m.%Y %H:%M')}*
Категория: {note.category}
{"⭐ ВАЖНАЯ" if note.is_important else ""}

*Текст:* {preview}

Если ДА, используйте команду:
`/delete {note.id[:8]} confirm`

Если НЕТ, просто проигнорируйте это сообщение.
"""
        await update.message.reply_text(
            warning,
            parse_mode='Markdown'
        )
        return
    
    # Подтверждение получено - удаляем
    success = note_manager.delete_note(user.id, note.id)
    
    if success:
        response = f"""
*🗑️ Запись удалена!*

ID: `{note.id[:8]}`
Дата создания: {note.created_at.strftime('%d.%m.%Y')}
Текст: {note.text[:60]}...

Запись удалена безвозвратно.
"""
        await update.message.reply_text(
            response,
            parse_mode='Markdown',
            reply_markup=get_main_keyboard()
        )
    else:
        await update.message.reply_text(
            "❌ Не удалось удалить запись. Возможно, она уже была удалена.",
            reply_markup=get_main_keyboard()
        )

# 17. ========== Статистика по категориям ==========
async def categories_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает все категории пользователя с количеством записей"""
    user = update.effective_user
    all_notes = note_manager.get_all_notes(user.id)
    
    if not all_notes:
        await update.message.reply_text(
            "📭 У вас ещё нет записей с категориями.\n\n"
            "Создайте первую запись с помощью /new",
            reply_markup=get_main_keyboard()
        )
        return
    
    # Собираем статистику по категориям
    from collections import defaultdict
    category_stats = defaultdict(int)
    
    for note in all_notes:
        category_stats[note.category] += 1
    
    # Сортируем по количеству записей (убывание)
    sorted_categories = sorted(
        category_stats.items(),
        key=lambda x: x[1],
        reverse=True
    )
    
    # Формируем ответ
    categories_text = "🏷️ *Ваши категории:*\n\n"
    
    total_notes = len(all_notes)
    for category, count in sorted_categories:
        percentage = (count / total_notes) * 100
        bar_length = int(percentage / 5)  # 5% на один символ
        bar = "█" * bar_length + "░" * (20 - bar_length)
        
        categories_text += f"*{category}*\n"
        categories_text += f"`{bar}` {count} зап. ({percentage:.1f}%)\n\n"
    
    categories_text += f"*Всего записей:* {total_notes}\n\n"
    categories_text += "*Использование:*\n"
    categories_text += "• `/list` - все записи\n"
    categories_text += f"• `/search категория` - искать в категории\n"
    categories_text += "• `/set_category ID новая_категория` - изменить"
    
    await update.message.reply_text(
        categories_text,
        parse_mode='Markdown',
        reply_markup=get_main_keyboard()
    )

# 18. ========== Статистика по записям ==========
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает статистику по записям"""
    user = update.effective_user
    all_notes = note_manager.get_all_notes(user.id)
    
    if not all_notes:
        await update.message.reply_text(
            "📊 У вас ещё нет записей для статистики.",
            reply_markup=get_main_keyboard()
        )
        return
    
    from collections import defaultdict, Counter
    from datetime import datetime, timedelta
    
    # Базовая статистика
    total_notes = len(all_notes)
    
    # По категориям
    categories = Counter(note.category for note in all_notes)
    top_category, top_count = categories.most_common(1)[0] if categories else ("-", 0)
    
    # По важности
    important_notes = sum(1 for note in all_notes if note.is_important)
    
    # По тегам
    all_tags = []
    for note in all_notes:
        all_tags.extend(note.tags)
    tag_counts = Counter(all_tags)
    top_tags = tag_counts.most_common(3)
    
    # По времени (последние 7 дней)
    week_ago = datetime.now() - timedelta(days=7)
    recent_notes = [n for n in all_notes if n.created_at > week_ago]
    
    # Формируем ответ
    stats_text = f"""
*📊 Статистика ваших записей*

*Общее:*
• Всего записей: *{total_notes}*
• Важных: *{important_notes}* ({important_notes/total_notes*100:.1f}%)
• За последние 7 дней: *{len(recent_notes)}*

*Категории:*
• Всего категорий: *{len(categories)}*
• Самая популярная: *{top_category}* ({top_count} зап.)

*Теги:*
• Всего тегов: *{len(tag_counts)}*
"""
    
    if top_tags:
        stats_text += "• Топ-3 тега:\n"
        for tag, count in top_tags:
            stats_text += f"  #{tag} - {count} раз\n"
    
    # Дополнительная информация
    if total_notes > 1:
        oldest = min(all_notes, key=lambda x: x.created_at)
        newest = max(all_notes, key=lambda x: x.created_at)
        
        days_diff = (newest.created_at - oldest.created_at).days
        avg_per_day = total_notes / max(days_diff, 1)
        
        stats_text += f"\n*Временные метки:*\n"
        stats_text += f"• Первая запись: {oldest.created_at.strftime('%d.%m.%Y')}\n"
        stats_text += f"• Последняя запись: {newest.created_at.strftime('%d.%m.%Y')}\n"
        stats_text += f"• Период: {days_diff} дней\n"
        stats_text += f"• В среднем: {avg_per_day:.1f} зап./день"
    
    await update.message.reply_text(
        stats_text,
        parse_mode='Markdown',
        reply_markup=get_main_keyboard()
    )

# 19. ========== Список вчерашних записей ==========
async def yesterday_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает записи за вчера"""
    user = update.effective_user
    from datetime import datetime, timedelta
    
    yesterday = (datetime.now() - timedelta(days=1)).date()
    all_notes = note_manager.get_all_notes(user.id)
    
    yesterday_notes = [
        note for note in all_notes
        if note.created_at.date() == yesterday
    ]
    
    if not yesterday_notes:
        await update.message.reply_text(
            f"📅 Вчера ({yesterday.strftime('%d.%m.%Y')}) записей не было.",
            reply_markup=get_main_keyboard()
        )
        return
    
    yesterday_text = f"📅 *Записи за вчера ({yesterday.strftime('%d.%m.%Y')}):*\n\n"
    
    for i, note in enumerate(yesterday_notes, 1):
        time_str = note.created_at.strftime('%H:%M')
        preview = note.text[:70] + "..." if len(note.text) > 70 else note.text
        
        yesterday_text += f"{i}. *{time_str}* - {preview}\n"
        
        if note.category != "Общее":
            yesterday_text += f"   🏷️ {note.category}\n"
        
        if note.is_important:
            yesterday_text += "   ⭐ Важная\n"
        
        yesterday_text += f"   ID: `{note.id[:8]}`\n\n"
    
    yesterday_text += f"*Всего записей:* {len(yesterday_notes)}"
    
    await update.message.reply_text(
        yesterday_text,
        parse_mode='Markdown',
        reply_markup=get_main_keyboard()
    )

# 20. ========== Заглушка для напоминаний ==========
async def set_reminder_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Устанавливает напоминание для записи (заглушка с пояснением)"""
    explanation = """
*⏰ Система напоминаний (в разработке)*

Сейчас вы можете:
1. Просматривать записи за определённый день (`/today`, `/yesterday`)
2. Искать записи по тексту (`/search`)
3. Отмечать важные записи (`/mark_important`)

*Планируемые функции напоминаний:*
• Установка времени напоминания для записи
• Ежедневные утренние/вечерние напоминания
• Напоминания о невыполненных важных задачах

*Альтернатива сейчас:*
Используйте `/mark_important` для важных записей и 
просматривайте их регулярно через `/list`.
"""
    
    await update.message.reply_text(
        explanation,
        parse_mode='Markdown',
        reply_markup=get_main_keyboard()
    )


# 21. ========== ОБРАБОТКА РЕГУЛЯРНЫХ СООБЩЕНИЙ ==========

async def handle_regular_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка обычных сообщений (не команд)"""
    text = update.message.text
    
    # Кнопки главного меню
    if text == '📝 Новая запись':
        await new_entry_command(update, context)
    elif text == '📖 Мои записи':
        await list_entries_command(update, context)
    elif text == '📅 Сегодня':
        await today_entries_command(update, context)
    elif text == '⚙️ Настройки':
        await help_command(update, context)
    else:
        await update.message.reply_text(
            "Я не понял команду. Используйте меню или /help",
            reply_markup=get_main_keyboard()
        )


# 22. ========== INLINE-КНОПКИ: ОБРАБОТЧИК ==========

async def handle_inline_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Главный обработчик ВСЕХ inline-кнопок"""
    query = update.callback_query
    await query.answer()  # Убираем "часики" у кнопки
    
    data = query.data
    user = query.from_user
    
    logger.info(f"[Helper] Нажата inline-кнопка: {data} пользователем {user.id}")
    
    # Разбираем callback_data. Формат: "действие_данные"
    # Примеры: "view_a1b2c3d4", "page_2", "delete_confirm_a1b2c3d4"
    
    # 1. ПРОСМОТР записи
    if data.startswith('view_'):
        note_id_short = data[5:]  # Убираем "view_"
        await _handle_view_button(query, context, note_id_short, user.id)
    
    # 2. УДАЛЕНИЕ записи (подтверждение)
    elif data.startswith('delete_'):
        # Формат: delete_a1b2c3d4 или delete_confirm_a1b2c3d4
        parts = data.split('_')
        note_id_short = parts[1] if len(parts) > 1 else None
        
        if len(parts) == 3 and parts[1] == 'confirm':
            note_id_short = parts[2]
            await _handle_delete_confirm(query, context, note_id_short, user.id)
        else:
            await _handle_delete_button(query, context, note_id_short, user.id)
    
    # 3. РЕДАКТИРОВАНИЕ записи
    elif data.startswith('edit_'):
        note_id_short = data[5:]
        await _handle_edit_button(query, context, note_id_short, user.id)
    
    # 4. СМЕНА КАТЕГОРИИ
    elif data.startswith('category_'):
        # Формат: category_a1b2c3d4 или category_a1b2c3d4_Работа
        parts = data.split('_')
        note_id_short = parts[1]
        
        if len(parts) == 3:
            new_category = parts[2]
            await _handle_category_change(query, context, note_id_short, user.id, new_category)
        else:
            await _handle_category_button(query, context, note_id_short, user.id)
    
    # 5. ВАЖНОСТЬ записи
    elif data.startswith('important_'):
        parts = data.split('_')
        note_id_short = parts[1]
        action = parts[2] if len(parts) > 2 else 'toggle'
        await _handle_important_button(query, context, note_id_short, user.id, action)
    
    # 6. ПАГИНАЦИЯ
    elif data.startswith('page_'):
        page_num = data[5:]
        if page_num.isdigit():
            await _handle_pagination(query, context, int(page_num), user.id)
    
    # 7. ВОЗВРАТ В МЕНЮ
    elif data == 'main_menu':
        await query.edit_message_text(
            "🏠 Возвращаюсь в главное меню.",
            reply_markup=get_main_keyboard()
        )
    
    # 8. ОТМЕНА действия
    elif data == 'cancel':
        await query.edit_message_text(
            "❌ Действие отменено.",
            reply_markup=get_main_keyboard()
        )
        
    # 9. СОЗДАНИЕ НОВОЙ ЗАПИСИ через кнопку
    elif data == 'new_note':
        await query.edit_message_text(
            "📝 *Создание новой записи*\n\n"
            "Просто напишите текст записи в чат. Можно добавить теги через #.\n\n"
            "Или нажмите '❌ Отмена'.",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("❌ Отмена", callback_data='main_menu')
            ]])
        )
        # Устанавливаем флаг ожидания текста
        context.user_data['waiting_for_note'] = True
    
    # 10. СПИСОК ЗАПИСЕЙ через кнопку
    elif data == 'list_notes':
        # Просто вызываем list_entries_command
        context.args = []  # Сбрасываем аргументы
        await list_entries_command(update, context)
        
    # 11. ЗАПИСИ ЗА СЕГОДНЯ через кнопку
    elif data == 'today_notes':
        await today_entries_command(update, context)
    
    # 12. СТАТИСТИКА через кнопку
    elif data == 'stats':
        await stats_command(update, context)
    
    # 13. КАТЕГОРИИ через кнопку
    elif data == 'categories':
        await categories_command(update, context)
    
    # 14. ПОМОЩЬ через кнопку
    elif data == 'help':
        await help_command(update, context)
    
    # 15. НОВАЯ КАТЕГОРИЯ (запрос на ввод)
    elif data.startswith('category_new_'):
        note_id_short = data[13:]  # Убираем 'category_new_'
        await query.edit_message_text(
            f"➕ *Новая категория для записи* `{note_id_short}`\n\n"
            "Введите название новой категории сообщением в этот чат.",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("❌ Отмена", callback_data=f"category_{note_id_short}")
            ]])
        )
        # Сохраняем, для какой записи ждём категорию
        context.user_data['awaiting_category_for'] = note_id_short

    else:
        # Неизвестная кнопка
        await query.edit_message_text(
            "Кнопка устарела. Используйте /list для обновления списка.",
            reply_markup=get_main_keyboard()
        )

# ========== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ДЛЯ КНОПОК ==========

# 23. ========== Обработка кнопки ==========
async def _handle_view_button(query, context, note_id_short, user_id):
    """Обработка кнопки 'Просмотреть'"""
    note = _find_note_by_short_id(user_id, note_id_short, context)
    if not note:
        await query.edit_message_text(
            f"❌ Запись `{note_id_short}` не найдена.",
            parse_mode='Markdown'
        )
        return
    
    # Используем существующую логику view_note_command, но адаптируем для inline-сообщения
    from src.bots.helper_bot.keyboards.inline_keyboards import get_note_actions_keyboard
    
    # Форматируем текст как в view_note_command
    full_text = f"""
📄 *Запись `{note.id[:8]}`*

*Создана:* {note.created_at.strftime('%d.%m.%Y в %H:%M')}
*Категория:* {note.category}
*Важность:* {'⭐ ВАЖНАЯ' if note.is_important else 'Обычная'}
"""
    
    if note.tags:
        tags_str = " ".join([f"#{t}" for t in note.tags])
        full_text += f"*Теги:* {tags_str}\n"
    
    full_text += f"\n*Текст записи:*\n{note.text}"
    
    await query.edit_message_text(
        full_text,
        parse_mode='Markdown',
        reply_markup=get_note_actions_keyboard(note.id[:8], note.category)
    )

# 24. ========== Подтверждение удаления ==========
async def _handle_delete_button(query, context, note_id_short, user_id):
    """Показать подтверждение удаления"""
    note = _find_note_by_short_id(user_id, note_id_short, context)
    if not note:
        await query.edit_message_text("Запись не найдена.")
        return
    
    from src.bots.helper_bot.keyboards.inline_keyboards import get_confirmation_keyboard
    
    preview = note.text[:80] + "..." if len(note.text) > 80 else note.text
    
    confirmation_text = f"""
*⚠️ Удалить эту запись?*

`{note.id[:8]}` - {note.created_at.strftime('%d.%m.%Y')}
Категория: {note.category}

*Текст:* {preview}

Запись будет удалена безвозвратно.
"""
    
    await query.edit_message_text(
        confirmation_text,
        parse_mode='Markdown',
        reply_markup=get_confirmation_keyboard(
            action='delete',
            note_id=note.id[:8],
            yes_text="🗑️ Да, удалить",
            no_text="❌ Нет, отменить"
        )
    )

# 25. ========== Подтверждённое удаление ==========
async def _handle_delete_confirm(query, context, note_id_short, user_id):
    """Подтверждённое удаление"""
    note = _find_note_by_short_id(user_id, note_id_short, context)
    if not note:
        await query.edit_message_text("Запись уже удалена.")
        return
    
    success = note_manager.delete_note(user_id, note.id)
    
    if success:
        await query.edit_message_text(
            f"✅ Запись `{note.id[:8]}` удалена.\n\n{note.text[:60]}...",
            parse_mode='Markdown',
            reply_markup=get_main_keyboard()
        )
    else:
        await query.edit_message_text(
            "❌ Не удалось удалить запись.",
            reply_markup=get_main_keyboard()
        )

# Остальные функции (_handle_edit_button, _handle_category_button и т.д.)
# мы добавим позже, после создания клавиатур

# 26. =$=$=$=$=$=$=$=$=$=$ КНОПКИ: Обработка кнопок пагинации  =$=$=$=$=$=$=$=$=$=$
async def _handle_pagination(query, context, page_num, user_id):
    """Обработка нажатий кнопок пагинации"""
    # Просто вызываем list_entries_command с нужной страницей
    # Создаём фиктивный update с callback_query
    class FakeUpdate:
        def __init__(self, query):
            self.callback_query = query
            self.effective_user = query.from_user
    
    fake_update = FakeUpdate(query)
    
    # Устанавливаем аргументы для страницы (page_num + 1, так как пользователь видит с 1)
    context.args = [str(page_num + 1)]
    
    await list_entries_command(fake_update, context)

# 27. =$=$=$=$=$=$=$=$=$=$ КНОПКИ: Редактировать  =$=$=$=$=$=$=$=$=$=$
async def _handle_edit_button(query, context, note_id_short, user_id):
    """Обработка кнопки 'Редактировать' - запрашивает новый текст"""
    note = _find_note_by_short_id(user_id, note_id_short, context)
    if not note:
        await query.edit_message_text("Запись не найдена.")
        return
    
    # Сохраняем ID записи для редактирования
    context.user_data['editing_note_id'] = note.id
    context.user_data['editing_note_short_id'] = note_id_short
    
    await query.edit_message_text(
        f"✏️ *Редактирование записи* `{note_id_short}`\n\n"
        f"*Текущий текст:*\n{note.text}\n\n"
        "Введите новый текст сообщением в этот чат.\n"
        "Или нажмите '❌ Отмена'.",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("❌ Отмена", callback_data=f"view_{note_id_short}")
        ]])
    )

# 28. =$=$=$=$=$=$=$=$=$=$ КНОПКИ: Меню категорий  =$=$=$=$=$=$=$=$=$=$
async def _handle_category_button(query, context, note_id_short, user_id):
    """Показывает меню выбора категории для записи"""
    note = _find_note_by_short_id(user_id, note_id_short, context)
    if not note:
        await query.edit_message_text("Запись не найдена.")
        return
    
    # Получаем категории пользователя
    user_categories = note_manager.get_categories(user_id)
    
    await query.edit_message_text(
        f"🏷️ *Выбор категории для записи* `{note_id_short}`\n\n"
        f"Текущая категория: *{note.category}*\n\n"
        "Выберите новую категорию:",
        parse_mode='Markdown',
        reply_markup=get_categories_keyboard_for_note(note_id_short, user_categories)
    )

# 29. =$=$=$=$=$=$=$=$=$=$ КНОПКИ: Меняет категорию записи  =$=$=$=$=$=$=$=$=$=$
async def _handle_category_change(query, context, note_id_short, user_id, new_category):
    """Меняет категорию записи"""
    note = _find_note_by_short_id(user_id, note_id_short, context)
    if not note:
        await query.edit_message_text("Запись не найдена.")
        return
    
    # Обновляем категорию
    success = note_manager.update_note(
        user_id=user_id,
        note_id=note.id,
        updates={"category": new_category}
    )
    
    if success:
        await query.edit_message_text(
            f"✅ Категория изменена на: *{new_category}*\n\n"
            f"Запись: `{note_id_short}`\n"
            f"Текст: {note.text[:60]}...",
            parse_mode='Markdown',
            reply_markup=get_note_actions_keyboard(note_id_short, new_category)
        )
    else:
        await query.edit_message_text(
            "❌ Не удалось изменить категорию.",
            reply_markup=get_note_actions_keyboard(note_id_short, note.category)
        )

# 30. =$=$=$=$=$=$=$=$=$=$ КНОПКИ: переключатель важности  =$=$=$=$=$=$=$=$=$=$
async def _handle_important_button(query, context, note_id_short, user_id, action="toggle"):
    """Переключает важность записи"""
    note = _find_note_by_short_id(user_id, note_id_short, context)
    if not note:
        await query.edit_message_text("Запись не найдена.")
        return
    
    # Определяем новое значение
    new_importance = not note.is_important if action == "toggle" else (action == "yes")
    
    # Обновляем запись
    success = note_manager.update_note(
        user_id=user_id,
        note_id=note.id,
        updates={"is_important": new_importance}
    )
    
    if success:
        status = "⭐ ОТМЕЧЕНА КАК ВАЖНАЯ" if new_importance else "➖ Снята отметка важности"
        
        await query.edit_message_text(
            f"{status}\n\n"
            f"Запись: `{note_id_short}`\n"
            f"Текст: {note.text[:60]}...",
            parse_mode='Markdown',
            reply_markup=get_note_actions_keyboard(note_id_short, note.category)
        )
    else:
        await query.edit_message_text(
            "❌ Не удалось изменить статус важности.",
            reply_markup=get_note_actions_keyboard(note_id_short, note.category)
        )

# 31. =$=$=$=$=$=$=$=$=$=$ КНОПКИ: Обработка ввода Новой категории  =$=$=$=$=$=$=$=$=$=$
async def _handle_new_category_input(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    """Обрабатывает ввод новой категории после нажатия кнопки '➕ Новая категория'"""
    user = update.effective_user
    
    if 'awaiting_category_for' not in context.user_data:
        await update.message.reply_text("Сессия устарела. Начните заново.")
        return
    
    note_id_short = context.user_data['awaiting_category_for']
    note = _find_note_by_short_id(user.id, note_id_short, context)
    
    if not note:
        await update.message.reply_text("Запись не найдена.")
        context.user_data.pop('awaiting_category_for', None)
        return
    
    # Обновляем категорию
    success = note_manager.update_note(
        user_id=user.id,
        note_id=note.id,
        updates={"category": text}
    )
    
    if success:
        context.user_data.pop('awaiting_category_for', None)
        
        await update.message.reply_text(
            f"✅ Новая категория: *{text}*\n\n"
            f"Запись: `{note_id_short}`",
            parse_mode='Markdown',
            reply_markup=get_note_actions_keyboard(note_id_short, text)
        )
    else:
        await update.message.reply_text(
            "❌ Не удалось изменить категорию.",
            reply_markup=get_main_keyboard()
        )

# 45. ========== РЕГИСТРАЦИЯ ОБРАБОТЧИКОВ ==========
def get_handlers():
    """Возвращает все обработчики для регистрации"""
    return [
        CommandHandler("start", start_command),
        CommandHandler("help", help_command),
        CommandHandler("new", new_entry_command),
        CommandHandler("list", list_entries_command),
        CommandHandler("today", today_entries_command),
        CommandHandler("yesterday", yesterday_command),     # <-- ДОБАВИТЬ
        CommandHandler("view", view_note_command),
        CommandHandler("search", search_notes_command),
        CommandHandler("edit", edit_note_command),
        CommandHandler("set_category", set_category_command),
        CommandHandler("mark_important", mark_important_command),
        CommandHandler("delete", delete_note_command),
        CommandHandler("categories", categories_command),   # <-- ДОБАВИТЬ
        CommandHandler("stats", stats_command),             # <-- ДОБАВИТЬ
        CommandHandler("set_reminder", set_reminder_command),
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_note_text),
    ]