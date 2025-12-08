#!/usr/bin/env python3
"""
Точка входа в приложение glasspen_bot.
"""

import sys
import os
import logging
import time

# Определяем корень проекта
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    from config import config
    from bot.core import get_bot
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print(f"📁 PROJECT_ROOT: {PROJECT_ROOT}")
    print(f"📁 sys.path: {sys.path}")
    sys.exit(1)

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, config.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('data/bot.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

def setup_directories():
    """Создание необходимых директорий"""
    directories = ['data', 'logs']
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.debug(f"Директория создана/проверена: {directory}")

def main():
    """Основная функция запуска приложения"""
    try:
        # Показываем конфигурацию
        config.show()
        
        # Создаём необходимые директории
        setup_directories()
        
        # Инициализируем бота
        bot = get_bot()
        
        # Запускаем бота
        bot.start()
        
        logger.info("Приложение успешно запущено")
        print("\n✨ Приложение работает! Нажмите Ctrl+C для остановки.")
        
        # Имитируем работу
        try:
            while bot.is_running:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Получен сигнал остановки (Ctrl+C)")
        
        # Останавливаем бота
        bot.stop()
        
        logger.info("Приложение завершено")
        return 0
        
    except Exception as e:
        logger.error(f"Ошибка при запуске приложения: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
