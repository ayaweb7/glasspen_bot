"""
Менеджер для работы с записями (Note).
Отвечает за загрузку, сохранение, поиск и манипуляции с записями в хранилище.
"""

import json
import logging
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from src.core.models import Note

logger = logging.getLogger(__name__)

class NoteManager:
    """Управляет хранением и обработкой записей."""
    
    def __init__(self, storage_path: str = "data/notes.json"):
        """
        Инициализация менеджера.
        
        Args:
            storage_path: Путь к файлу JSON для хранения данных.
        """
        self.storage_path = Path(storage_path)
        self._ensure_storage_exists()
        self._notes_cache = {}  # Кэш: {user_id: [Note, Note, ...]}
        self._load_all_notes()
    
    def _ensure_storage_exists(self):
        """Убеждается, что директория и файл для хранения данных существуют."""
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.storage_path.exists():
            self.storage_path.write_text("{}", encoding="utf-8")
            logger.info(f"Создан новый файл хранилища: {self.storage_path}")
    
    def _load_all_notes(self):
        """Загружает все записи из JSON файла в кэш."""
        try:
            data = json.loads(self.storage_path.read_text(encoding="utf-8"))
            self._notes_cache = {}
            
            for user_id_str, notes_list in data.items():
                user_id = int(user_id_str)
                self._notes_cache[user_id] = [
                    Note.from_dict(note_data) for note_data in notes_list
                ]
            
            total_notes = sum(len(notes) for notes in self._notes_cache.values())
            logger.info(f"Загружено {total_notes} записей для {len(self._notes_cache)} пользователей")
        
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.warning(f"Ошибка при загрузке записей, создаём новое хранилище: {e}")
            self._notes_cache = {}
    
    def _save_all_notes(self):
        """Сохраняет все записи из кэша в JSON файл."""
        data = {}
        for user_id, notes in self._notes_cache.items():
            data[str(user_id)] = [note.to_dict() for note in notes]
        
        self.storage_path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        logger.debug(f"Сохранено {sum(len(notes) for notes in self._notes_cache.values())} записей")
    
    # --- Основные CRUD операции ---
    
    def add_note(self, note: Note) -> Note:
        """
        Добавляет новую запись.
        
        Args:
            note: Объект Note для добавления.
            
        Returns:
            Добавленная запись (с заполненными полями id, created_at и т.д.).
        """
        if note.user_id not in self._notes_cache:
            self._notes_cache[note.user_id] = []
        
        self._notes_cache[note.user_id].append(note)
        self._save_all_notes()
        
        logger.info(f"Добавлена запись {note.id} для пользователя {note.user_id}")
        return note
    
    def get_note(self, user_id: int, note_id: str) -> Optional[Note]:
        """Находит запись по ID пользователя и ID записи."""
        user_notes = self._notes_cache.get(user_id, [])
        for note in user_notes:
            if note.id == note_id:
                return note
        return None
    
    def get_all_notes(self, user_id: int) -> List[Note]:
        """Возвращает ВСЕ записи пользователя."""
        return self._notes_cache.get(user_id, [])
    
    def get_recent_notes(self, user_id: int, limit: int = 10) -> List[Note]:
        """Возвращает последние записи пользователя (по дате создания)."""
        notes = self.get_all_notes(user_id)
        # Сортируем по дате создания (новые сверху)
        notes.sort(key=lambda x: x.created_at, reverse=True)
        return notes[:limit]
    
    def get_notes_by_category(self, user_id: int, category: str) -> List[Note]:
        """Возвращает записи пользователя по категории."""
        return [
            note for note in self.get_all_notes(user_id)
            if note.category.lower() == category.lower()
        ]
    
    def update_note(self, user_id: int, note_id: str, updates: dict) -> Optional[Note]:
        """
        Обновляет запись.
        
        Args:
            user_id: ID пользователя.
            note_id: ID записи.
            updates: Словарь с полями для обновления.
                     Например: {"text": "новый текст", "category": "Работа"}
        
        Returns:
            Обновлённый объект Note или None, если запись не найдена.
        """
        note = self.get_note(user_id, note_id)
        if not note:
            logger.warning(f"Запись {note_id} не найдена для пользователя {user_id}")
            return None
        
        # Обновляем поля
        for field, value in updates.items():
            if hasattr(note, field):
                setattr(note, field, value)
        
        # Обновляем время изменения
        note.updated_at = datetime.now()
        
        self._save_all_notes()
        logger.info(f"Обновлена запись {note_id} для пользователя {user_id}")
        return note
    
    def delete_note(self, user_id: int, note_id: str) -> bool:
        """Удаляет запись по ID. Возвращает True, если удаление прошло успешно."""
        user_notes = self._notes_cache.get(user_id, [])
        
        for i, note in enumerate(user_notes):
            if note.id == note_id:
                del user_notes[i]
                self._save_all_notes()
                logger.info(f"Удалена запись {note_id} для пользователя {user_id}")
                return True
        
        logger.warning(f"Не удалось удалить запись {note_id} для пользователя {user_id}")
        return False
    
    # --- Вспомогательные методы ---
    
    def get_categories(self, user_id: int) -> List[str]:
        """Возвращает список уникальных категорий пользователя."""
        categories = set()
        for note in self.get_all_notes(user_id):
            categories.add(note.category)
        return sorted(list(categories))
    
    def get_notes_with_reminders(self) -> List[Note]:
        """Возвращает ВСЕ записи с установленными напоминаниями (для планировщика)."""
        all_notes = []
        for user_notes in self._notes_cache.values():
            for note in user_notes:
                if note.reminder_at:
                    all_notes.append(note)
        return all_notes

# Глобальный экземпляр менеджера для использования во всём приложении
note_manager = NoteManager()
