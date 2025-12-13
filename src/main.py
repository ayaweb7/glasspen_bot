#!/usr/bin/env python3
"""
Основной файл запуска системы ботов.
"""

import sys
import os
import asyncio
import logging
import signal

# Добавляем корень проекта в путь Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import config
from src.core.bot_manager import get_bot_manager
from src.bots.glasspen_bot.bot import GlasspenBot
from src.bots.helper_bot.bot import HelperBot
from src.utils.logging_config import setup_logging

logger = logging.getLogger(__name__)

def setup_directories():
    """Создание необходимых директорий"""
    directories = ['data', 'logs']
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.debug(f"Директория создана/проверена: {directory}")

def create_bots():
    """Создание и регистрация всех ботов"""
    manager = get_bot_manager()
    
    # Создаём и регистрируем всех ботов из конфигурации
    for bot_name, bot_config in config.bots.items():
        if not bot_config.enabled:
            logger.info(f"Бот {bot_name} отключен в конфигурации")
            continue
        
        # Выбираем класс бота в зависимости от имени
        if bot_name == "glasspen":
            bot_class = GlasspenBot
        elif bot_name == "helper":
            bot_class = helperBot
        else:
            logger.warning(f"Неизвестный тип бота: {bot_name}. Используем BaseBot.")
            from src.core.base_bot import BaseBot
            bot_class = BaseBot
        
        # Создаём экземпляр бота
        bot = bot_class(
            name=bot_name,
            token=bot_config.token,
            config={
                'admin_ids': bot_config.admin_ids,
                **bot_config.extra_config
            }
        )
        
        # Регистрируем в менеджере
        manager.register_bot(bot)
        logger.info(f"Создан бот: {bot_name}")

async def shutdown(signal, loop):
    """Корректное завершение работы"""
    logger.info(f"Получен сигнал {signal.name}. Завершение работы...")
    
    manager = get_bot_manager()
    await manager.stop_all()
    
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    for task in tasks:
        task.cancel()
    
    await asyncio.gather(*tasks, return_exceptions=True)
    loop.stop()
    
    logger.info("Работа завершена")

async def main_async():
    """Асинхронная основная функция"""
    try:
        # Настройка логирования
        setup_logging(config.log_level)
        
        # Показываем конфигурацию
        config.show()
        
        # Создаём необходимые директории
        setup_directories()
        
        # Создаём ботов
        create_bots()
        
        # Настройка обработки сигналов
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(
                sig,
                lambda s=sig: asyncio.create_task(shutdown(s, loop))
            )
        
        # Запускаем менеджер ботов
        manager = get_bot_manager()
        
        logger.info("="*60)
        logger.info("🚀 Запуск системы ботов...")
        logger.info("="*60)
        
        await manager.start_all()
        
        # Периодическая проверка здоровья
        async def health_check_task():
            while True:
                await asyncio.sleep(60)  # Каждую минуту
                status = await manager.health_check()
                logger.debug(f"Health check: {status['running_bots']}/{status['total_bots']} ботов работают")
        
        asyncio.create_task(health_check_task())
        
        # Бесконечный цикл
        await asyncio.Event().wait()
        
        return 0
        
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}", exc_info=True)
        return 1

def main():
    """Синхронная обёртка для асинхронной функции"""
    try:
        return asyncio.run(main_async())
    except KeyboardInterrupt:
        logger.info("Работа завершена пользователем")
        return 0
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
