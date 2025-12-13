"""
Базовый класс для всех Telegram ботов.
Определяет общий интерфейс и функционал.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

from telegram.ext import Application, ApplicationBuilder

logger = logging.getLogger(__name__)

class BaseBot(ABC):
    """Абстрактный базовый класс для Telegram ботов"""
    
    def __init__(self, name: str, token: str, config: Dict[str, Any]):
        """
        Инициализация бота.
        
        Args:
            name: Имя бота (для логирования)
            token: Токен Telegram бота
            config: Конфигурация бота
        """
        self.name = name
        self.token = token
        self.config = config
        self.application: Optional[Application] = None
        self.is_running = False
        
        # Статистика
        self.metrics = {
            'messages_processed': 0,
            'commands_processed': 0,
            'errors': 0,
            'start_time': None
        }
    
    async def start(self):
        """Запуск бота"""
        if self.is_running:
            logger.warning(f"Бот {self.name} уже запущен")
            return
        
        try:
            logger.info(f"Запуск бота: {self.name}")
            
            # Создаём приложение
            self.application = ApplicationBuilder().token(self.token).build()
            
            # Настраиваем бота
            await self.setup()
            
            # Регистрируем обработчики
            self._register_handlers()
            
            # Запускаем
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling()
            
            self.is_running = True
            self.metrics['start_time'] = asyncio.get_event_loop().time()
            
            logger.info(f"✅ Бот {self.name} успешно запущен")
            
        except Exception as e:
            logger.error(f"❌ Ошибка при запуске бота {self.name}: {e}", exc_info=True)
            raise
    
    async def stop(self):
        """Остановка бота"""
        if not self.is_running:
            logger.warning(f"Бот {self.name} уже остановлен")
            return
        
        try:
            logger.info(f"Остановка бота: {self.name}")
            
            if self.application:
                await self.application.updater.stop()
                await self.application.stop()
                await self.application.shutdown()
            
            self.is_running = False
            logger.info(f"✅ Бот {self.name} остановлен")
            
        except Exception as e:
            logger.error(f"Ошибка при остановке бота {self.name}: {e}", exc_info=True)
            raise
    
    async def setup(self):
        """
        Настройка бота.
        Переопределите в дочерних классах для дополнительной настройки.
        """
        logger.debug(f"Настройка бота: {self.name}")
        # Базовый setup - можно добавить общую логику
    
    def _register_handlers(self):
        """Регистрация обработчиков команд и сообщений"""
        if not self.application:
            raise RuntimeError("Приложение не инициализировано")
        
        # Регистрируем обработчики из дочернего класса
        handlers = self.get_handlers()
        for handler in handlers:
            self.application.add_handler(handler)
        
        # Обработчик ошибок
        self.application.add_error_handler(self._error_handler)
        
        logger.debug(f"Зарегистрировано обработчиков для {self.name}: {len(handlers)}")
    
    @abstractmethod
    def get_handlers(self):
        """
        Получить список обработчиков команд.
        Должен быть реализован в дочерних классах.
        
        Returns:
            List: Список обработчиков (CommandHandler, MessageHandler и т.д.)
        """
        pass
    
    async def _error_handler(self, update: object, context):
        """Обработчик ошибок"""
        error_msg = str(context.error)
        self.metrics['errors'] += 1
        
        logger.error(f"Ошибка в боте {self.name}: {error_msg}", exc_info=True)
        
        # Можно отправить ошибку администраторам
        await self._notify_admins(f"❌ Ошибка в {self.name}: {error_msg[:100]}")
    
    async def _notify_admins(self, message: str):
        """Уведомить администраторов"""
        admins = self.config.get('admin_ids', [])
        if not admins or not self.application:
            return
        
        for admin_id in admins:
            try:
                await self.application.bot.send_message(
                    chat_id=admin_id,
                    text=message
                )
            except Exception as e:
                logger.error(f"Не удалось отправить уведомление админу {admin_id}: {e}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Получить метрики работы бота"""
        return {
            **self.metrics,
            'name': self.name,
            'is_running': self.is_running,
            'uptime': (asyncio.get_event_loop().time() - self.metrics['start_time']) 
                     if self.metrics['start_time'] else 0
        }
    
    async def send_message(self, chat_id: int, text: str, **kwargs):
        """Отправить сообщение (обёртка)"""
        if not self.application or not self.is_running:
            raise RuntimeError("Бот не запущен")
        
        try:
            await self.application.bot.send_message(
                chat_id=chat_id,
                text=text,
                **kwargs
            )
            self.metrics['messages_processed'] += 1
            return True
        except Exception as e:
            logger.error(f"Не удалось отправить сообщение: {e}")
            return False
