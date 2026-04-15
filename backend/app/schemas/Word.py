from pydantic import BaseModel

class WordAdd(BaseModel): # определяем модель данных для добавления слова, которая наследуется от BaseModel
    word: str
    level: str
    meaning: str | None
    example: str | None
    translation: str