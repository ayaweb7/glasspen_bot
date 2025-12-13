"""
Конкретная реализация Helper Bot.
"""

import logging
from typing import List

from telegram.ext import CallbackQueryHandler

from src.core.base_bot import BaseBot
from src.bots.glasspen_bot.handlers.commands import (
    get_handlers,
    button_callback_handler
)
from src.bots.glasspen_bot.keyboards.main_menu import get_main_keyboard

logger = logging.getLogger(__name__)

class HelperBot(BaseBot):
    """Helper Bot - бот для ведения записей"""
    
    def __init__(self, token: str, config: dict):
        super().__init__(name="helper", token=token, config=config)
        
    def get_handlers(self):
        """Получить обработчики команд для этого бота"""
        handlers = get_handlers()
        
        # Добавляем обработчик inline-кнопок
        handlers.append(CallbackQueryHandler(button_callback_handler))
        
        return handlers
    
    async def setup(self):
        """Дополнительная настройка бота"""
        await super().setup()
        logger.info(f"Helper Bot настроен. Админы: {self.config.get('admin_ids', [])}")
    
    async def send_welcome_message(self, chat_id: int):
        """Отправить приветственное сообщение"""
        welcome_text = """
🎉 Добро пожаловать в Helper Bot!

Я помогу вам организовать ваши записи и мысли.

Начните с команды /new для создания первой записи!
"""
        
        await self.send_message(
            chat_id=chat_id,
            text=welcome_text,
            reply_markup=get_main_keyboard()
        )
