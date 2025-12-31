"""
Менеджер для работы с вопросами пользователей
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class UserQuestion:
    """Модель вопроса пользователя"""
    id: str
    user_id: int
    username: str
    first_name: str
    question_text: str
    created_at: str
    status: str  # 'new', 'answered', 'archived'
    admin_comment: str = ""
    answered_at: str = ""


class QuestionManager:
    """Управление вопросами пользователей"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.questions_file = self.data_dir / "glasspen_questions.json"
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Создаёт файл если его нет"""
        if not self.questions_file.exists():
            with open(self.questions_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    def save_question(self, user_id: int, username: str, first_name: str, question_text: str) -> str:
        """Сохраняет новый вопрос"""
        try:
            # Загружаем существующие вопросы
            with open(self.questions_file, 'r', encoding='utf-8') as f:
                questions = json.load(f)
            
            # Создаём новый вопрос
            question_id = f"q{datetime.now().strftime('%Y%m%d%H%M%S')}_{user_id}"
            new_question = UserQuestion(
                id=question_id,
                user_id=user_id,
                username=username or "",
                first_name=first_name or "",
                question_text=question_text,
                created_at=datetime.now().isoformat(),
                status="new"
            )
            
            # Добавляем и сохраняем
            questions.append(asdict(new_question))
            
            with open(self.questions_file, 'w', encoding='utf-8') as f:
                json.dump(questions, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Сохранён вопрос {question_id} от пользователя {user_id}")
            return question_id
            
        except Exception as e:
            logger.error(f"Ошибка сохранения вопроса: {e}")
            return ""
    
    def get_pending_questions(self) -> List[Dict]:
        """Получает все неотвеченные вопросы"""
        try:
            with open(self.questions_file, 'r', encoding='utf-8') as f:
                questions = json.load(f)
            
            return [q for q in questions if q['status'] == 'new']
        except Exception as e:
            logger.error(f"Ошибка загрузки вопросов: {e}")
            return []
    
    def mark_as_answered(self, question_id: str, admin_comment: str = "") -> bool:
        """Отмечает вопрос как отвеченный"""
        try:
            with open(self.questions_file, 'r', encoding='utf-8') as f:
                questions = json.load(f)
            
            # Находим и обновляем вопрос
            for q in questions:
                if q['id'] == question_id:
                    q['status'] = 'answered'
                    q['admin_comment'] = admin_comment
                    q['answered_at'] = datetime.now().isoformat()
                    break
            
            with open(self.questions_file, 'w', encoding='utf-8') as f:
                json.dump(questions, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            logger.error(f"Ошибка обновления вопроса: {e}")
            return False


# Синглтон экземпляр
question_manager = QuestionManager()