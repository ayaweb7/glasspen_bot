"""
Менеджер для управления несколькими ботами.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from src.core.base_bot import BaseBot

logger = logging.getLogger(__name__)

class BotManager:
    """Менеджер для запуска и управления несколькими ботами"""
    
    def __init__(self):
        self.bots: Dict[str, BaseBot] = {}
        self.is_running = False
        self.start_time = None
    
    def register_bot(self, bot: BaseBot):
        """Регистрация бота в менеджере"""
        if bot.name in self.bots:
            raise ValueError(f"Бот с именем '{bot.name}' уже зарегистрирован")
        
        self.bots[bot.name] = bot
        logger.info(f"Зарегистрирован бот: {bot.name}")
    
    async def start_all(self):
        """Запуск всех зарегистрированных ботов"""
        if self.is_running:
            logger.warning("Менеджер ботов уже запущен")
            return
        
        logger.info(f"Запуск менеджера ботов. Всего ботов: {len(self.bots)}")
        self.start_time = datetime.now()
        self.is_running = True
        
        # Запускаем все боты параллельно
        tasks = [bot.start() for bot in self.bots.values()]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Проверяем результаты
        i = 1
        for bot_name, result in zip(self.bots.keys(), results):
            if isinstance(result, Exception):
                logger.error(f"{i}. Ошибка при запуске бота {bot_name}: {result}")
            else:
                logger.info(f"{i}. Бот {bot_name} запущен успешно!")
            i+=1
        
        logger.info(f"✅ Все боты запущены! Всего ботов: {len(self.bots)}")
    
    async def stop_all(self):
        """Остановка всех ботов"""
        if not self.is_running:
            logger.warning("Менеджер ботов уже остановлен")
            return
        
        logger.info("Остановка всех ботов...")
        
        # Останавливаем все боты
        stop_tasks = [bot.stop() for bot in self.bots.values()]
        await asyncio.gather(*stop_tasks, return_exceptions=True)
        
        self.is_running = False
        logger.info("✅ Все боты остановлены")
    
    async def restart_bot(self, bot_name: str):
        """Перезапуск конкретного бота"""
        if bot_name not in self.bots:
            raise ValueError(f"Бот '{bot_name}' не найден")
        
        bot = self.bots[bot_name]
        
        if bot.is_running:
            await bot.stop()
        
        await bot.start()
        logger.info(f"✅ Бот {bot_name} перезапущен")
    
    def get_bot(self, bot_name: str) -> Optional[BaseBot]:
        """Получить бота по имени"""
        return self.bots.get(bot_name)
    
    def get_all_metrics(self) -> Dict[str, Dict]:
        """Получить метрики всех ботов"""
        return {
            bot_name: bot.get_metrics()
            for bot_name, bot in self.bots.items()
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Получить статус менеджера и всех ботов"""
        running_bots = sum(1 for bot in self.bots.values() if bot.is_running)
        
        return {
            'manager_running': self.is_running,
            'total_bots': len(self.bots),
            'running_bots': running_bots,
            'uptime': (datetime.now() - self.start_time).total_seconds() 
                     if self.start_time else 0,
            'bots': self.get_all_metrics()
        }
    
    async def health_check(self):
        """Проверка здоровья всех ботов"""
        status = self.get_status()
        
        # Проверяем каждый бот
        for bot_name, bot in self.bots.items():
            if not bot.is_running:
                logger.warning(f"Бот {bot_name} не запущен. Попытка перезапуска...")
                try:
                    await self.restart_bot(bot_name)
                except Exception as e:
                    logger.error(f"Не удалось перезапустить бот {bot_name}: {e}")
        
        return status

# Глобальный экземпляр менеджера
_bot_manager = None

def get_bot_manager() -> BotManager:
    """Получить глобальный экземпляр менеджера ботов (синглтон)"""
    global _bot_manager
    if _bot_manager is None:
        _bot_manager = BotManager()
    return _bot_manager
