"""
Админ-команды для glasspen_bot
question_text
"""
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CommandHandler

from src.core.question_manager import question_manager

logger = logging.getLogger(__name__)

def escape_markdown(text: str) -> str:
    """
    Экранирует спецсимволы Markdown
    """
    if not text:
        return ""
    
    # Список символов для экранирования
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    
    # Экранируем каждый символ
    result = ""
    for char in text:
        if char in escape_chars:
            result += '\\' + char
        else:
            result += char
    
    return result

async def admin_questions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает неотвеченные вопросы (только для админа)"""
    user = update.effective_user
    
    # Проверяем, админ ли
    admin_ids = context.bot_data.get('admin_ids', [])
    
    # Если admin_ids пуст, пробуем получить из application.bot_data
    if not admin_ids and hasattr(context, 'application') and hasattr(context.application, 'bot_data'):
        admin_ids = context.application.bot_data.get('admin_ids', [])
    
    logger.info(f"=== DEBUG admin_questions ===")
    logger.info(f"Пользователь: {user.id}, Имя: {user.first_name}")
    logger.info(f"admin_ids из bot_data: {admin_ids}")
    logger.info(f"Пользователь в списке админов: {user.id in admin_ids}")
    
    if user.id not in admin_ids:
        await update.message.reply_text("⛔ У вас нет доступа к этой команде.")
        return
    
    questions = question_manager.get_pending_questions()
    
    logger.info(f"Найдено неотвеченных вопросов: {len(questions)}")
    
    if not questions:
        await update.message.reply_text("📭 Нет новых вопросов.")
        return
    
    response = f"📨 Неотвеченные вопросы: {len(questions)}\n\n"
    
    for i, q in enumerate(questions[:-10], 1):  # Ограничиваем 10
        # Форматируем дату
        created_at = q['created_at']
        if 'T' in created_at:
            date_str = created_at.split('T')[0].replace('-', '.')
            time_str = created_at.split('T')[1][:5]
            datetime_str = f"{date_str} {time_str}"
        else:
            datetime_str = created_at[:16]
        
        # ИСПРАВЛЕНИЕ: Экранируем спецсимволы в тексте вопроса
        question_text = escape_markdown(q['question_text'])
        # Убираем Markdown символы для безопасности
        question_text = question_text.replace('*', '').replace('_', '').replace('`', '')
        
        response += f"{i}. ID: `{q['id']}`\n"
        response += f"   👤 {q['first_name']} (@{q['username'] or 'нет'})\n"
        response += f"   🕒 {datetime_str}\n"
        response += f"   📝 {q['question_text'][:100]}...\n\n"
    
    response += "Используйте:\n"
    response += "`/answer ID_вопроса ваш_комментарий`\n"
    response += "Пример:\n"
    response += "`/answer q20260101223528_7156086085 Ответил пользователю`"
    
    # Создаем клавиатуру для быстрых действий
    keyboard = []
    for q in questions[:5]:  # Только первые 3 вопроса
        keyboard.append([
            InlineKeyboardButton(
                f"Ответить: {q['question_text'][:10]}...",
                callback_data=f"admin_answer_{q['id']}"
            )
        ])
    
    keyboard.append([
        InlineKeyboardButton("Обновить", callback_data="admin_refresh"),
        InlineKeyboardButton("Главное меню", callback_data="main_menu")
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        response,
        # parse_mode="Markdown",
        reply_markup=reply_markup
    )


async def admin_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отметить вопрос как отвеченный"""
    user = update.effective_user
    
    # Проверяем, админ ли
    admin_ids = context.bot_data.get('admin_ids', [])
    if not admin_ids and hasattr(context, 'application') and hasattr(context.application, 'bot_data'):
        admin_ids = context.application.bot_data.get('admin_ids', [])
    
    logger.info(f"=== DEBUG admin_answer ===")
    logger.info(f"Пользователь: {user.id} в админах: {user.id in admin_ids}")
    
    if user.id not in admin_ids:
        await update.message.reply_text("⛔ Нет доступа.")
        return
    
    if len(context.args) < 2:
        await update.message.reply_text(
            "*Использование:*\n"
            "`/answer ID_вопроса ваш_комментарий`\n\n"
            "*Пример:*\n"
            "`/answer q20260101223528_7156086085 Ответил пользователю`\n\n"
            "ID вопроса можно получить из `/questions`",
            parse_mode="Markdown"
        )
        return
    
    question_id = context.args[0]
    comment = " ".join(context.args[1:])
    
    logger.info(f"Пытаемся отметить вопрос {question_id} как отвеченный")
    
    success = question_manager.mark_as_answered(question_id, comment)
    
    if success:
        # Получаем обновлённый вопрос для подтверждения
        all_questions = []
        try:
            import json
            from pathlib import Path
            
            questions_file = Path("data") / "glasspen_questions.json"
            if questions_file.exists():
                with open(questions_file, 'r', encoding='utf-8') as f:
                    all_questions = json.load(f)
        except Exception as e:
            logger.error(f"Ошибка загрузки вопросов для подтверждения: {e}")
        
        # Находим наш вопрос
        question_info = ""
        for q in all_questions:
            if q['id'] == question_id:
                question_text_preview = q['question_text'][:80] + "..." if len(q['question_text']) > 80 else q['question_text']
                question_info = f"\n*Вопрос:* {question_text_preview}"
                break
        
        await update.message.reply_text(
            f"✅ *Вопрос отмечен как отвеченный!*\n\n"
            f"*ID:* `{question_id}`\n"
            f"*Комментарий:* {comment}\n"
            f"{question_info}\n\n"
            f"Используйте `/questions` для просмотра оставшихся вопросов.",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            "❌ Не удалось обновить вопрос. Возможно, ID неверный или вопрос уже обработан.",
            parse_mode="Markdown"
        )


async def handle_admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка callback от админ-кнопок"""
    query = update.callback_query
    data = query.data
    
    logger.info(f"=== DEBUG handle_admin_callback ===")
    logger.info(f"Callback data: {data}")
    
    try:
        await query.answer()
    except Exception as e:
        logger.warning(f"Не удалось ответить на callback: {e}")
        # Продолжаем выполнение даже если callback устарел
    
    if data == "admin_refresh":
        # Обновляем список вопросов
        await admin_questions(update, context)
    elif data.startswith("admin_answer_"):
        # Показываем форму для ответа на конкретный вопрос
        question_id = data[13:]  # Убираем "admin_answer_"
        
        await query.edit_message_text(
            f"✏️ *Ответ на вопрос* `{question_id}`\n\n"
            f"Введите ответ в формате:\n"
            f"`/answer {question_id} ваш_комментарий`\n\n"
            f"*Пример:*\n"
            f"`/answer {question_id} Ответил пользователю в личке`",
            parse_mode="Markdown"
        )
    elif data == "main_menu":
        # Возврат в главное меню
        from .commands import handle_main_menu
        await handle_main_menu(update, context)


def get_admin_handlers():
    """Возвращает админ-обработчики"""
    return [
        CommandHandler("questions", admin_questions),
        CommandHandler("answer", admin_answer)
    ]