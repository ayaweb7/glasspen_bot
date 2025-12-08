#!/usr/bin/env python3
"""
Основной скрипт запуска приложения.
Используйте: python run.py
"""

import sys
import os

# Убедимся, что мы находимся в правильной директории
if __name__ == "__main__":
    # Добавляем возможность запуска из любой директории
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Запускаем основной модуль
    from src.main import main
    sys.exit(main())
