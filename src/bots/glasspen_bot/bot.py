"""
Основной файл бота GlassPen
Используем python-telegram-bot (как helper_bot)
"""
import logging

from src.core.base_bot import BaseBot

logger = logging.getLogger(__name__)


class GlasspenBot(BaseBot):
    """Бот для канала 'Стеклянное Перо'"""
    
    def __init__(self, token: str, config: dict):
        super().__init__(name="glasspen", token=token, config=config)
        self.config = config
        self.channel_link = config.get("channel_link", "https://t.me/glass_pen/")
    
    def get_handlers(self):
        """
        Возвращает список обработчиков для python-telegram-bot
        """
        from telegram.ext import (
            CommandHandler,
            CallbackQueryHandler,
            MessageHandler,
            filters,
            ConversationHandler
        )
        
        # Импортируем обработчики
        from .handlers.commands import (
            cmd_start,
            cmd_help,
            cmd_channel,
            handle_main_menu,
            handle_faq_menu,
            handle_faq_answer,
            handle_ask_question,
            handle_question_input,
            handle_cancel
        )
        
        # Определяем состояния для ConversationHandler (как в helper_bot)
        ASKING_QUESTION = 1
        
        # Создаём ConversationHandler для обработки вопросов
        question_conv_handler = ConversationHandler(
            entry_points=[
                CallbackQueryHandler(handle_ask_question, pattern="^ask_question$")
            ],
            states={
                ASKING_QUESTION: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, handle_question_input)
                ]
            },
            fallbacks=[
                CallbackQueryHandler(handle_cancel, pattern="^cancel$"),
                CommandHandler("start", cmd_start)
            ],
            allow_reentry=True
        )
        
        # Собираем все обработчики
        handlers = [
            CommandHandler("start", cmd_start),
            CommandHandler("help", cmd_help),
            CommandHandler("channel", cmd_channel),
            CallbackQueryHandler(handle_main_menu, pattern="^main_menu$"),
            CallbackQueryHandler(handle_faq_menu, pattern="^show_faq$"),
            CallbackQueryHandler(handle_faq_answer, pattern="^faq:"),
            question_conv_handler,  # Используем ConversationHandler вместо простого MessageHandler
            CallbackQueryHandler(handle_cancel, pattern="^cancel$")
        ]
        
        return handlers


# Функция для создания экземпляра бота
def create_bot(token: str, config: dict) -> GlasspenBot:
    """Фабрика для создания экземпляра GlasspenBot"""
    return GlasspenBot(token, config)