"""
Конфигурация логирования с ротацией.
"""

import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import os

def setup_logging(log_level="INFO", log_dir="logs"):
    """Настройка логирования с ротацией файлов"""
    
    # Преобразуем строку уровня в константу
    level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Создаём директорию для логов
    os.makedirs(log_dir, exist_ok=True)
    
    # Форматтер
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Файловый обработчик с ротацией по размеру
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, 'bot_system.log'),
        maxBytes=10*1024*1024,  # 10 MB
        backupCount=10,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)
    
    # Файловый обработчик с ротацией по времени (отдельно для ошибок)
    error_handler = TimedRotatingFileHandler(
        os.path.join(log_dir, 'errors.log'),
        when='midnight',
        interval=1,
        backupCount=30,
        encoding='utf-8'
    )
    error_handler.setFormatter(formatter)
    error_handler.setLevel(logging.ERROR)
    
    # Консольный обработчик
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)
    
    # Корневой логгер
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Удаляем существующие обработчики
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Добавляем новые обработчики
    root_logger.addHandler(file_handler)
    root_logger.addHandler(error_handler)
    root_logger.addHandler(console_handler)
    
    # Настройка логгеров библиотек
    logging.getLogger('telegram').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('asyncio').setLevel(logging.WARNING)
    
    return root_logger
