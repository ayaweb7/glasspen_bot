"""
Конфигурационный файл проекта glasspen_bot.
Загружает настройки из .env файла и предоставляет доступ к ним.
"""

import os
import sys
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv

# Загружаем переменные из .env файла
# load_dotenv() ищет .env в текущей директории и родительских
load_dotenv()

@dataclass
class DatabaseConfig:
    """Конфигурация базы данных"""
    url: str = "sqlite:///data/bot.db"
    
    def __post_init__(self):
        """Проверка после инициализации"""
        if not self.url:
            raise ValueError("DATABASE_URL не указан в .env файле")

@dataclass
class TelegramConfig:
    """Конфигурация Telegram бота"""
    token: Optional[str] = None
    admin_ids: list = None
    
    def __post_init__(self):
        if self.admin_ids is None:
            self.admin_ids = []
        
        # Преобразуем строку ADMIN_ID в список чисел
        admin_id_str = os.getenv("ADMIN_ID", "")
        if admin_id_str:
            try:
                self.admin_ids.append(int(admin_id_str))
            except ValueError:
                print(f"⚠️  Неверный формат ADMIN_ID: {admin_id_str}")

@dataclass
class AppConfig:
    """Основная конфигурация приложения"""
    name: str = "Glasspen Bot"
    version: str = "0.1.0"
    log_level: str = "INFO"
    
    # Подконфигурации
    db: DatabaseConfig = None
    telegram: TelegramConfig = None
    
    def __init__(self):
        self.db = DatabaseConfig(
            url=os.getenv("DATABASE_URL", "sqlite:///data/bot.db")
        )
        
        self.telegram = TelegramConfig(
            token=os.getenv("TELEGRAM_BOT_TOKEN")
        )
        
        self.log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        
        # Валидация обязательных полей
        self._validate()
    
    def _validate(self):
        """Проверка обязательных настроек"""
        errors = []
        
        if not self.telegram.token:
            errors.append("TELEGRAM_BOT_TOKEN не установлен в .env файле")
        
        if errors:
            error_msg = "\n".join([f"❌ {error}" for error in errors])
            print("\n" + "="*50)
            print("ОШИБКИ КОНФИГУРАЦИИ:")
            print(error_msg)
            print("="*50)
            print("\nСоздайте файл .env на основе .env.example")
            print("Или установите переменные окружения напрямую")
            sys.exit(1)
    
    def show(self):
        """Показать текущую конфигурацию (без секретов)"""
        print("\n" + "="*50)
        print(f"🎯 {self.name} v{self.version}")
        print("="*50)
        print(f"📁 База данных: {self.db.url}")
        print(f"📊 Уровень логов: {self.log_level}")
        print(f"👑 Админы: {self.telegram.admin_ids}")
        
        # Токен показываем частично для безопасности
        if self.telegram.token:
            token_preview = self.telegram.token[:5] + "..." + self.telegram.token[-5:]
            print(f"🤖 Токен бота: {token_preview}")
        else:
            print("🤖 Токен бота: НЕ УСТАНОВЛЕН")
        
        print("="*50)

# Создаём глобальный объект конфигурации
config = AppConfig()

# Для обратной совместимости можно оставить старые переменные
TELEGRAM_BOT_TOKEN = config.telegram.token
DATABASE_URL = config.db.url
LOG_LEVEL = config.log_level

if __name__ == "__main__":
    # Если запустить этот файл напрямую, покажем конфигурацию
    config.show()
