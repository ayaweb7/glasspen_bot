"""
Конфигурация Telegram бота.
"""

import os
import logging
from dataclasses import dataclass
from typing import List, Optional
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

@dataclass
class BotConfig:
    """Конфигурация Telegram бота"""
    token: str
    admin_ids: List[int]
    
    def __post_init__(self):
        """Валидация конфигурации"""
        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN не установлен в .env файле")
        
        # Проверяем формат токена
        if ':' not in self.token:
            raise ValueError("Неверный формат токена. Должен быть: 1234567890:ABCdef...")

@dataclass
class AppConfig:
    """Основная конфигурация приложения"""
    name: str = "Glasspen Bot"
    version: str = "0.2.0"
    log_level: str = "INFO"
    
    def __init__(self):
        # Загружаем настройки из .env
        token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        
        # Преобразуем ADMIN_ID в список чисел
        admin_ids = []
        admin_id_str = os.getenv("ADMIN_ID", "")
        if admin_id_str:
            try:
                admin_ids.append(int(admin_id_str))
            except ValueError:
                logging.warning(f"Неверный формат ADMIN_ID: {admin_id_str}")
        
        self.bot = BotConfig(token=token, admin_ids=admin_ids)
        self.log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        
        # Валидация
        self._validate()
    
    def _validate(self):
        """Проверка обязательных настроек"""
        if not self.bot.token:
            print("\n❌ ОШИБКА: TELEGRAM_BOT_TOKEN не установлен")
            print("Создайте файл .env с вашим токеном или установите переменную окружения")
            print("Пример: TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNoPQRsTUVwxyz")
            exit(1)
    
    def show(self):
        """Показать текущую конфигурацию"""
        print("\n" + "="*50)
        print(f"🤖 {self.name} v{self.version}")
        print("="*50)
        print(f"📊 Уровень логов: {self.log_level}")
        print(f"👑 Админы: {self.bot.admin_ids}")
        
        # Токен показываем частично для безопасности
        if self.bot.token:
            token_preview = self.bot.token[:10] + "..." + self.bot.token[-5:]
            print(f"🔑 Токен бота: {token_preview}")
        print("="*50)

# Глобальный объект конфигурации
config = AppConfig()
