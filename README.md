Мой первый хорошо структурированный Python проект - Glasspen_bot.

## 📁 Структура проекта

glasspen_bot/			# Корень проекта (корневая директория)
│
├── src/					# Основной код проекта (source)
│	├── bots/				# Менеджер ботов
│src/	├── glasspen_bot/	# Бот Стеклянного Пера
│bots/	│	├── handlers/
│	│	│	│	├── __init__.py
│	│	│	│	└── commands.py
│	│	│	│
│   │	│	├── keyboards/
│	│	│	│	├── __init__.py
│	│	│	│	└── xxxx.py
│	│	│	│
│	│	│	├── __init__.py
│	│	│	└── bot.py
│	│	│
│	│	│
│src/	├── helper_bot/		# Бот Помощника
│bots/│	│	├── handlers/
│	│	│	│	├── __init__.py
│	│	│	│	└── commands.py
│	│	│	│
│   │	│	├── keyboards/
│	│	│	│	├── __init__.py
│	│	│	│	└── xxxx.py
│	│	│	│
│	│	│	├── __init__.py
│	│	│	└── bot.py
│	│	│
│	│	│		
│	│	└── __init__.py
│	│	
│	├── bot/				# Рабочий вариант helper бота
│src/	├── handlers/
│bot/	│	├── __init__.py
│	│	│	└── command_handlers.py
│	│	│
│	│	├── keyboards/
│	│	│	├── __init__.py
│	│	│	└── main_menu.py
│	│	│
│	│	├── utils/
│	│	│	└── __init__.py
│	│	│
│   │	├── __init__.py
│   │	├── bot.py
│   │	└── core.py
│	│
│	├── config/
│src/	└── __init__.py
│	│
│	├── core/
│src/	├── __init__.py
│core/	├── base_bot.py
│	│	└── bot_manager.py
│	│
│	├── utils/
│src/	└── logging_config.py
│	│
│	├── glasspen_bot.py		# Исходный код (для bot/)
│	├── main.py				# Основной код (для bots/)
│	└── __init__.py
│
│
├── tests/						# Директория для тестов
│   ├── test_glasspen_bot.py 	# Файл с тестами для glasspen_bot.py
│   └── test_main.py 			# Файл с тестами для main.py
│
│
├── docs/			# Документация проекта
│   └── README.md	# Основной файл документации (можно создать позже)
│
│
├── data/			# Директория для входных/выходных данных, датасетов
│   ├── bot.log		# Логгирование процессов
│   ├── input/
│   └── output/
│
│
├── logs/			# Директория для логов
│   └── bot.log		# Логгирование процессов
│
│
├── notebooks/		# Эксперименты в Jupyter Notebooks (Опционально)
│   └── glasspen_bot.ipynb		# Тестирование
│
│
*****glasspen_bot/files*
│
│
├──  __init__.py
├── .gitignore		# Файл, для инструкций отслеживания файлов Git
├── .env.example	# Шаблон файла с секретными переменными
├── .env			# Для секретных переменных (Опционально, но рекомендуется)
├── requirements.txt # Список зависимостей (библиотек) проекта
├── config.py		# Файл конфигурации (настройки, константы)
├── run.py			# Специальный файл для запуска из корня проекта (Опционально)
├── setup.py		# Файл установки проекта в виртуальное окружение (Опционально)
└── README.md		# Главное описание проекта (видно на GitHub)


## 🚀 Быстрый старт

1. Клонируйте репозиторий:
```bash
git clone https://github.com/ВАШ_НИКНЕЙМ/glasspen_bot.git
cd glasspen_bot
```

2. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/Scripts/activate  # Windows (Git Bash)
# или: source venv/bin/activate  # macOS/Linux
```

3. Запустите проект:
```bash
python src/main.py
```

## 🔐 Настройка окружения

1. Скопируйте шаблон настроек:
   ```bash
   cp .env.example .env
   ```

2. Отредактируйте `.env` файл:  
   Откройте `.env` в текстовом редакторе и заполните реальными значениями:
   ```env
   TELEGRAM_BOT_TOKEN=ваш_токен_от_BotFather
   ADMIN_ID=ваш_telegram_id
   ```

3. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

4. Как получить токен бота:
   - Напишите [@BotFather](https://t.me/botfather) в Telegram
   - Команда `/newbot`
   - Следуйте инструкциям
   - Скопируйте полученный токен в `.env` файл

## 📦 Управление зависимостями

Проект использует `pip-tools` для управления зависимостями.

### Файлы зависимостей:
- `requirements.in` — основные зависимости (production)
- `requirements-dev.in` — зависимости для разработки
- `requirements.txt` — сгенерированный файл с точными версиями (не коммитить!)
- `requirements-dev.txt` — сгенерированный файл для разработки (не коммитить!)

### Основные команды:

```bash
# Установить зависимости для разработки
pip install -r requirements-dev.txt

# Обновить зависимости (после изменения .in файлов)
./update-deps.sh  # или update-deps.bat на Windows

# Установить только production зависимости
pip install -r requirements.txt

# Добавить новую зависимость
# 1. Добавьте пакет в requirements.in или requirements-dev.in
# 2. Выполните ./update-deps.sh
# 3. Установите: pip install -r requirements-dev.txt
```

### Добавление новых зависимостей:

1. Отредактируйте `requirements.in` (основные) или `requirements-dev.in` (для разработки)
2. Запустите скрипт обновления:
   ```bash
   ./update-deps.sh
   ```
3. Установите обновленные зависимости:
   ```bash
   pip install -r requirements-dev.txt
   ```

