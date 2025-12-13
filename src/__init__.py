"""
Glasspen Bot - система управления Telegram ботами.
"""

__version__ = "0.2.0"
__author__ = "Kornely Prutkov"
__email__ = "your.email@ayaweb7.gmailcom"

# Экспорт основных компонентов
from .bot.bot import get_bot
from .bot.handlers.command_handlers import start_command

# Указываем, что импортировать при "from src import *"
__all__ = ['get_bot', 'start_command']
