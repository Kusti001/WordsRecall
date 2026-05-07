from pydantic import BaseModel
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

class BaseResponse(BaseModel):
    """Базовый формат ответа API"""
    message: str
    data: Optional[Any] = None

class ListResponse(BaseModel):
    """Формат ответа для списков"""
    message: str
    total: int
    items: List[Any]

class ErrorResponse(BaseModel):
    """Формат ответа для ошибок"""
    message: str
    error: Optional[str] = None

class UserResponse(BaseModel):
    """Ответ с данными пользователя"""
    user_id: int
    telegram_id: str
    created_at: str

class WordResponse(BaseModel):
    """Ответ с данными слова"""
    id: int
    word: str
    level: str
    example: str
    meaning: str
    translation: str

class UserWordResponse(BaseModel):
    """Ответ с данными пользовательского слова для ревью"""
    user_word_id: int
    word: str
    translation: str
    meaning: str
    example: str
    level: str

class DictionaryWordResponse(BaseModel):
    """Ответ для словаря пользователя"""
    word: str
    translation: str
    next_review: str

class ReviewResponse(BaseModel):
    """Ответ после ревью слова"""
    message: str
    next_review: str
    interval_days: int

