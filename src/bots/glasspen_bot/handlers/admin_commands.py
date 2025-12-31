"""
Админ-команды для glasspen_bot
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

from src.core.question_manager import question_manager

logger = logging.getLogger(__name__)


async def admin_questions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает неотвеченные вопросы (только для админа)"""
    user = update.effective_user
    
    # Проверяем, админ ли (можно вынести в декоратор)
    admin_ids = context.bot_data.get('admin_ids', [])
    if user.id not in admin_ids:
        await update.message.reply_text("⛔ У вас нет доступа к этой команде.")
        return
    
    questions = question_manager.get_pending_questions()
    
    if not questions:
        await update.message.reply_text("📭 Нет новых вопросов.")
        return
    
    response = f"📨 *Неотвеченные вопросы: {len(questions)}*\n\n"
    
    for i, q in enumerate(questions[:10], 1):  # Ограничиваем 10
        response += f"{i}. *ID:* `{q['id']}`\n"
        response += f"   👤 {q['first_name']} (@{q['username'] or 'нет'})\n"
        response += f"   🕒 {q['created_at'][:16].replace('T', ' ')}\n"
        response += f"   📝 {q['question_text'][:100]}...\n\n"
    
    response += "Используйте `/answer ID_вопроса комментарий` для ответа."
    
    await update.message.reply_text(response, parse_mode="Markdown")


async def admin_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отметить вопрос как отвеченный"""
    user = update.effective_user
    admin_ids = context.bot_data.get('admin_ids', [])
    
    if user.id not in admin_ids:
        await update.message.reply_text("⛔ Нет доступа.")
        return
    
    if len(context.args) < 2:
        await update.message.reply_text(
            "Использование: `/answer ID_вопроса ваш_комментарий`"
        )
        return
    
    question_id = context.args[0]
    comment = " ".join(context.args[1:])
    
    success = question_manager.mark_as_answered(question_id, comment)
    
    if success:
        await update.message.reply_text(
            f"✅ Вопрос `{question_id}` отмечен как отвеченный.\n"
            f"Комментарий: {comment[:100]}"
        )
    else:
        await update.message.reply_text("❌ Не удалось обновить вопрос.")


def get_admin_handlers():
    """Возвращает админ-обработчики"""
    return [
        CommandHandler("questions", admin_questions),
        CommandHandler("answer", admin_answer)
    ]