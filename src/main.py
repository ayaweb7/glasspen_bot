#!/usr/bin/env python3
"""
Точка входа в приложение Glasspen Bot.
"""

import sys
import os
import asyncio
import logging

# Добавляем корень проекта в путь Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import config
from src.bot.bot import get_bot

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, config.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/bot.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

def setup_directories():
    """Создание необходимых директорий"""
    directories = ['data', 'logs']
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.debug(f"Директория создана/проверена: {directory}")

async def main_async():
    """Асинхронная основная функция"""
    try:
        # Показываем конфигурацию
        config.show()
        
        # Создаём необходимые директории
        setup_directories()
        
        # Инициализируем бота
        bot = get_bot()
        
        # Запускаем бота
        logger.info("Запуск Telegram бота...")
        await bot.start()
        
        return 0
        
    except Exception as e:
        logger.error(f"Ошибка при запуске приложения: {e}", exc_info=True)
        return 1

def main():
    """Синхронная обёртка для асинхронной функции"""
    try:
        return asyncio.run(main_async())
    except KeyboardInterrupt:
        logger.info("Приложение завершено по запросу пользователя")
        return 0
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
