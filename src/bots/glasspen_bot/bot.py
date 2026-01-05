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
        
        # Получаем ID администратора из конфига
        # admin_chat_id находится в extra_config, который передаётся как часть config
        self.admin_id = config.get('admin_chat_id')
        self.admin_ids = config.get('admin_ids', [])
        
        # Если admin_id не найден, пробуем взять первый из admin_ids
        if not self.admin_id and self.admin_ids:
            self.admin_id = self.admin_ids[0]
        
        self.channel_link = config.get("channel_link", "https://t.me/glass_pen/")
    
    async def setup(self):
        """Настройка бота"""
        await super().setup()
        
        # Сохраняем данные админа для использования в обработчиках
        if hasattr(self.application, 'bot_data'):
            self.application.bot_data['admin_id'] = self.admin_id
            self.application.bot_data['admin_ids'] = self.admin_ids
        
        logger.info(f"GlasspenBot настроен. Админ ID: {self.admin_id}")
        logger.info(f"Админ IDs список: {self.admin_ids}")
    
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
            channel_command,
            handle_main_menu,
            handle_faq_menu,
            handle_faq_answer,
            handle_ask_question,
            handle_question_input,
            handle_cancel,
            handle_start,
            handle_show_channel
        )
        
        from .handlers.admin_commands import (
            admin_questions,
            admin_answer,
            handle_admin_callback  # ← ДОБАВИТЬ ЭТОТ ИМПОРТ
        )
        
        # Определяем состояния для ConversationHandler
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
            per_message=False
        )
        
        # Собираем все обработчики
        handlers = [
            CommandHandler("start", cmd_start),
            CommandHandler("help", cmd_help),
            CommandHandler("channel", channel_command),
            CommandHandler("questions", admin_questions),
            CommandHandler("answer", admin_answer),
            CallbackQueryHandler(handle_main_menu, pattern="^main_menu$"),
            CallbackQueryHandler(handle_show_channel, pattern="^show_channel$"),
            CallbackQueryHandler(handle_faq_menu, pattern="^show_faq$"),
            CallbackQueryHandler(handle_faq_answer, pattern="^faq:"),
            CallbackQueryHandler(handle_admin_callback, pattern="^admin_"),  # ← ДОБАВИТЬ ЭТОТ ОБРАБОТЧИК
            CallbackQueryHandler(handle_cancel, pattern="^cancel$"),
            question_conv_handler
        ]
        
        return handlers


# Функция для создания экземпляра бота
def create_bot(token: str, config: dict) -> GlasspenBot:
    """Фабрика для создания экземпляра GlasspenBot"""
    return GlasspenBot(token, config)