"""
Основной модуль Telegram бота.
"""

import logging
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)

from config import config
from src.bot.handlers.command_handlers import (
    start_command,
    help_command,
    new_entry_command,
    list_entries_command,
    settings_command,
    handle_text_message,
    button_callback_handler
)

logger = logging.getLogger(__name__)

class TelegramBot:
    """Класс для управления Telegram ботом"""
    
    def __init__(self):
        self.token = config.bot.token
        self.application = None
        self.is_running = False
        
    async def start(self):
        """Запуск бота"""
        if self.is_running:
            logger.warning("Бот уже запущен")
            return
        
        logger.info("Создание приложения бота...")
        
        # Создаём приложение
        self.application = ApplicationBuilder().token(self.token).build()
        
        # Регистрируем обработчики команд
        self._register_handlers()
        
        # Запускаем бота
        logger.info("Запуск бота...")
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        
        self.is_running = True
        logger.info("✅ Бот успешно запущен и готов к работе!")
        
        # Бесконечно ждём (прерывается по Ctrl+C)
        await self._run_forever()
        
    async def stop(self):
        """Остановка бота"""
        if not self.is_running:
            logger.warning("Бот уже остановлен")
            return
        
        logger.info("Остановка бота...")
        
        if self.application:
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()
        
        self.is_running = False
        logger.info("✅ Бот остановлен")
        
    def _register_handlers(self):
        """Регистрация всех обработчиков команд"""
        
        # Команды
        self.application.add_handler(CommandHandler("start", start_command))
        self.application.add_handler(CommandHandler("help", help_command))
        self.application.add_handler(CommandHandler("new", new_entry_command))
        self.application.add_handler(CommandHandler("list", list_entries_command))
        self.application.add_handler(CommandHandler("settings", settings_command))
        
        # Обработчик inline-кнопок
        self.application.add_handler(CallbackQueryHandler(button_callback_handler))
        
        # Обработчик текстовых сообщений
        self.application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_text_message
        ))
        
        # Обработчик ошибок
        self.application.add_error_handler(self._error_handler)
        
        logger.info("Обработчики команд зарегистрированы")
        
    async def _error_handler(self, update: object, context):
        """Обработчик ошибок"""
        logger.error(f"Ошибка при обработке обновления: {context.error}", exc_info=True)
        
        # Можно отправить сообщение об ошибке администратору
        if config.bot.admin_ids:
            for admin_id in config.bot.admin_ids:
                try:
                    await context.bot.send_message(
                        chat_id=admin_id,
                        text=f"❌ Ошибка бота: {context.error}"
                    )
                except:
                    pass
    
    async def _run_forever(self):
        """Бесконечный цикл работы бота"""
        import asyncio
        try:
            while self.is_running:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            pass
        except KeyboardInterrupt:
            logger.info("Получен сигнал KeyboardInterrupt")
        finally:
            if self.is_running:
                await self.stop()
    
    async def send_message_to_admin(self, text: str):
        """Отправить сообщение администратору"""
        if not config.bot.admin_ids:
            return
        
        for admin_id in config.bot.admin_ids:
            try:
                await self.application.bot.send_message(
                    chat_id=admin_id,
                    text=text
                )
            except Exception as e:
                logger.error(f"Не удалось отправить сообщение админу {admin_id}: {e}")

# Глобальный экземпляр бота
_bot_instance = None

def get_bot() -> TelegramBot:
    """Получить экземпляр бота (синглтон)"""
    global _bot_instance
    if _bot_instance is None:
        _bot_instance = TelegramBot()
    return _bot_instance
