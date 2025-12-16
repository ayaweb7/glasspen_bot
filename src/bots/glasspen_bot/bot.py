"""
Конкретная реализация Glasspen Bot (бота обратной связи для канала).
"""

import logging
from typing import List

from telegram.ext import CommandHandler, CallbackQueryHandler

from src.core.base_bot import BaseBot
from src.bots.glasspen_bot.handlers.commands import (
    link_command,
    contents_command,
    question_command,
    handle_inline_buttons,
    get_handlers
)
from src.bots.glasspen_bot.keyboards.main_menu import get_main_keyboard

logger = logging.getLogger(__name__)

class GlasspenBot(BaseBot):
    """Glasspen Bot - бот для обратной связи в Telegram-канале."""

    def __init__(self, token: str, config: dict):
        super().__init__(name="glasspen", token=token, config=config)
        # Можно сохранить специфичные данные из конфига, например, ID админского чата
        self.admin_chat_id = config.get('admin_chat_id')  # Будет браться из extra_config в .env

    async def start_command(self, update, context):
        """Обработчик команды /start. Определён здесь, т.к. использует get_main_keyboard()."""
        welcome_text = """
        Приветствую в литературном уголке! 📚

        Я помогу вам:
        • Найти ссылку на наш канал
        • Показать оглавление произведений
        • Направить ваш вопрос авторам

        Выберите действие ниже 👇
        """
        await update.message.reply_text(welcome_text, reply_markup=get_main_keyboard())

    def get_handlers(self):
        """Получить все обработчики команд для этого бота."""
        handlers = get_handlers()  # Базовые обработчики сообщений

        # Явно добавляем обработчики команд
        handlers.extend([
            CommandHandler("start", self.start_command),
            CommandHandler("link", link_command),
            CommandHandler("contents", contents_command),
            CommandHandler("question", question_command),
        ])

        # Добавляем обработчик инлайн-кнопок (для оглавления)
        handlers.append(CallbackQueryHandler(handle_inline_buttons))

        return handlers

    async def setup(self):
        """Дополнительная настройка бота."""
        await super().setup()
        logger.info(f"Glasspen Bot настроен. Админы: {self.config.get('admin_ids', [])}. Админ-чат: {self.admin_chat_id}")
