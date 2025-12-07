# cat > config.py << 'EOF' # Команда для редактирования через терминал
"""
Конфигурация проекта glasspen_bot
"""

# Пути
DATA_DIR = "data"
LOG_DIR = "logs"

# Настройки приложения
APP_NAME = "Glasspen Bot"
VERSION = "0.1.0"
DEBUG = True

# Пример настройки API (заменить на реальные при необходимости)
API_BASE_URL = "https://api.example.com"
REQUEST_TIMEOUT = 30

def show_config():
    """Показать текущую конфигурацию"""
    print(f"{APP_NAME} v{VERSION}")
    print(f"Debug mode: {DEBUG}")
    print(f"Data directory: {DATA_DIR}")

# EOF # Завершение команды для редактирования через терминал