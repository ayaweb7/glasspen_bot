"""
Конфигурация системы ботов.
Поддерживает несколько ботов с разными токенами.
"""

import os
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Any
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

@dataclass
class BotConfig:
    """Конфигурация одного бота"""
    name: str
    token: str
    enabled: bool = True
    admin_ids: List[int] = field(default_factory=list)
    extra_config: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Валидация конфигурации"""
        if not self.token:
            raise ValueError(f"Токен не указан для бота {self.name}")
        
        if ':' not in self.token:
            raise ValueError(f"Неверный формат токена для бота {self.name}")

@dataclass
class DatabaseConfig:
    """Конфигурация базы данных"""
    enabled: bool = False
    url: str = "sqlite:///data/bots.db"
    echo: bool = False

@dataclass
class AppConfig:
    """Основная конфигурация приложения"""
    name: str = "Glasspen Bot System"
    version: str = "2.0.0"
    log_level: str = "INFO"
    bots: Dict[str, BotConfig] = field(default_factory=dict)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    
    def __init__(self):
        # Инициализируем словарь ботов до загрузки конфигурации
        self.bots = {}
        self.log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        
        # Загружаем конфигурацию ботов из .env
        self._load_bots_config()
        
        # Конфигурация БД
        self.database = DatabaseConfig(
            enabled=os.getenv("DATABASE_ENABLED", "false").lower() == "true",
            url=os.getenv("DATABASE_URL", "sqlite:///data/bots.db"),
            echo=os.getenv("DATABASE_ECHO", "false").lower() == "true"
        )
    
    def _load_bots_config(self):
        """Загрузка конфигурации ботов из переменных окружения"""
        
        # Формат переменных:
        # BOT_GLASSPEN_TOKEN=токен1
        # BOT_GLASSPEN_ADMIN_IDS=123,456
        # BOT_HELPER_TOKEN=токен2
        # BOT_HELPER_ADMIN_IDS=789
        
        bot_prefixes = []
        
        # Ищем все переменные с префиксом BOT_
        for key in os.environ:
            if key.startswith("BOT_") and key.endswith("_TOKEN"):
                # Извлекаем имя бота: BOT_GLASSPEN_TOKEN → glasspen
                prefix = key[4:-6]  # Убираем "BOT_" и "_TOKEN"
                bot_prefixes.append(prefix.lower())
        
        # Создаём конфигурации для найденных ботов
        for prefix in bot_prefixes:
            token_key = f"BOT_{prefix.upper()}_TOKEN"
            token = os.getenv(token_key)
            
            if not token:
                continue
            
            # Администраторы
            admin_ids = []
            admin_key = f"BOT_{prefix.upper()}_ADMIN_IDS"
            admin_str = os.getenv(admin_key, "")
            if admin_str:
                for admin_id in admin_str.split(','):
                    try:
                        admin_ids.append(int(admin_id.strip()))
                    except ValueError:
                        logging.warning(f"Неверный формат admin_id для бота {prefix}: {admin_id}")
            
            # Extra конфигурация
            extra_config = {}
            for key in os.environ:
                if key.startswith(f"BOT_{prefix.upper()}_") and \
                   not key.endswith("_TOKEN") and \
                   not key.endswith("_ADMIN_IDS"):
                    config_key = key[len(f"BOT_{prefix.upper()}_"):].lower()
                    extra_config[config_key] = os.getenv(key)
            
            bot_config = BotConfig(
                name=prefix,
                token=token,
                admin_ids=admin_ids,
                extra_config=extra_config
            )
            
            self.bots[prefix] = bot_config
            logging.info(f"Загружена конфигурация бота: {prefix}")
    
    def validate(self):
        """Проверка конфигурации"""
        if not self.bots:
            print("\n❌ ОШИБКА: Не найдены конфигурации ботов")
            print("Добавьте в .env файл переменные:")
            print("BOT_GLASSPEN_TOKEN=ваш_токен_бота")
            print("BOT_HELPER_TOKEN=токен_второго_бота")
            exit(1)
    
    def show(self):
        """Показать текущую конфигурацию"""
        print("\n" + "="*60)
        print(f"🤖 {self.name} v{self.version}")
        print("="*60)
        print(f"📊 Уровень логов: {self.log_level}")
        print(f"🗄️  База данных: {'Включена' if self.database.enabled else 'Выключена'}")
        
        print(f"\n🔧 Зарегистрированные боты ({len(self.bots)}):")
        for bot_name, bot_config in self.bots.items():
            status = "✅" if bot_config.enabled else "⏸️"
            token_preview = bot_config.token[:5] + " ... " + bot_config.token[-5:]
            print(f"  {status} {bot_name}:")
            print(f"    Токен: {token_preview}")
            print(f"    Админы: {bot_config.admin_ids}")
            if bot_config.extra_config:
                print(f"    Доп. настройки: {bot_config.extra_config}")
        
        print("="*60)

# Глобальный объект конфигурации
config = AppConfig()
