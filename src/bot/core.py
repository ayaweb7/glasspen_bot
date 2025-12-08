"""
Ядро телеграм-бота.
"""

import sys
import os
import logging
from typing import Optional

# Определяем корень проекта
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config import config

logger = logging.getLogger(__name__)

class BotCore:
    """Основной класс бота"""
    
    def __init__(self):
        self.token = config.telegram.token
        self.is_running = False
        logger.info(f"Бот инициализирован с токеном: {self.token[:5]}...{self.token[-5:]}")
    
    def start(self):
        """Запуск бота"""
        if self.is_running:
            logger.warning("Бот уже запущен")
            return
        
        logger.info("🚀 Запуск бота...")
        self.is_running = True
        logger.info("✅ Бот успешно запущен")
    
    def stop(self):
        """Остановка бота"""
        if not self.is_running:
            logger.warning("Бот уже остановлен")
            return
        
        logger.info("🛑 Остановка бота...")
        self.is_running = False
        logger.info("✅ Бот остановлен")
    
    def send_message(self, chat_id: int, text: str) -> bool:
        """Отправка сообщения (заглушка)"""
        if not self.is_running:
            logger.error("Бот не запущен")
            return False
        
        logger.info(f"📨 Отправка сообщения в chat_id={chat_id}: {text[:50]}...")
        return True

bot_instance: Optional[BotCore] = None

def get_bot() -> BotCore:
    """Получить экземпляр бота (синглтон)"""
    global bot_instance
    if bot_instance is None:
        bot_instance = BotCore()
    return bot_instance
