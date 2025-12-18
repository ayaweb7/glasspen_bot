"""
Конкретная реализация Helper Bot (простая версия).
"""

import logging
from telegram.ext import CallbackQueryHandler

from src.core.base_bot import BaseBot
from src.bots.helper_bot.handlers.commands import (
    get_handlers,
    handle_inline_buttons  # <-- ДОБАВЬТЕ ЭТУ СТРОКУ!
)
from src.bots.helper_bot.keyboards.main_menu import get_main_keyboard

logger = logging.getLogger(__name__)

class HelperBot(BaseBot):
    """Helper Bot - простой бот для ведения записей"""
    
    def __init__(self, token: str, config: dict):
        super().__init__(name="helper", token=token, config=config)
        
    def get_handlers(self):
        """Получить обработчики команд для этого бota"""
        handlers = get_handlers()
        
        # Добавляем обработчик inline-кнопок
        handlers.append(CallbackQueryHandler(handle_inline_buttons))
        
        return handlers
    
    async def setup(self):
        """Дополнительная настройка бота"""
        await super().setup()
        logger.info(f"Helper Bot (простая версия) настроен. Админы: {self.config.get('admin_ids', [])}")
    
    async def send_welcome_message(self, chat_id: int):
        """Отправить приветственное сообщение (опционально)"""
        welcome_text = """
🎉 Добро пожаловать в упрощённый Helper Bot!

Теперь всё просто:
1. Отправьте /new
2. Напишите текст
3. Запись сохранена!

Дополнительные настройки — отдельными командами.
"""
        
        await self.send_message(
            chat_id=chat_id,
            text=welcome_text,
            reply_markup=get_main_keyboard()
        )