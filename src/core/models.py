"""
Модели данных для проекта.
Основная модель - Note (Запись).
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
import uuid

# Если используете pydantic, раскомментируйте строки ниже и закомментируйте @dataclass
from pydantic import BaseModel, Field

# @dataclass
class Note(BaseModel):
    """
    Модель одной записи (заметки) пользователя.
    """
    # Обязательные поля
    id: str = field(default_factory=lambda: str(uuid.uuid4()))  # Уникальный идентификатор
    user_id: int  # ID пользователя Telegram, владельца записи
    text: str  # Текст записи
    
    # Автоматически заполняемые временные метки
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # Опциональные поля
    category: str = "Без категории"  # Категория для организации
    reminder_at: Optional[datetime] = None  # Время напоминания (если установлено)
    tags: List[str] = field(default_factory=list)  # Список тегов (#работа, #хобби)
    is_important: bool = False  # Флаг важности
    comment: Optional[str] = None  # Дополнительный комментарий
    
    def to_dict(self) -> dict:
        """Конвертирует объект Note в словарь для сохранения в JSON."""
        result = {
            "id": self.id,
            "user_id": self.user_id,
            "text": self.text,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "category": self.category,
            "tags": self.tags,
            "is_important": self.is_important,
        }
        # Обрабатываем опциональные поля с None
        if self.reminder_at:
            result["reminder_at"] = self.reminder_at.isoformat()
        if self.comment:
            result["comment"] = self.comment
        return result
    
    @classmethod
    def from_dict(cls, data: dict) -> "Note":
        """Создаёт объект Note из словаря (при загрузке из JSON)."""
        # Парсим строки дат обратно в объекты datetime
        created_at = datetime.fromisoformat(data["created_at"])
        updated_at = datetime.fromisoformat(data["updated_at"])
        reminder_at = (
            datetime.fromisoformat(data["reminder_at"])
            if data.get("reminder_at")
            else None
        )
        
        return cls(
            id=data["id"],
            user_id=data["user_id"],
            text=data["text"],
            created_at=created_at,
            updated_at=updated_at,
            category=data.get("category", "Без категории"),
            reminder_at=reminder_at,
            tags=data.get("tags", []),
            is_important=data.get("is_important", False),
            comment=data.get("comment"),
        )
