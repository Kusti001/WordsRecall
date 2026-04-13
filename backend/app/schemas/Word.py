from pydantic import BaseModel

class WordAdd(BaseModel): # определяем модель данных для добавления слова, которая наследуется от BaseModel
    english: str # поле для слова, которое будет добавлено
    russian: str # поле для перевода слова на русский язык
    example: str | None = None # необязательное поле для примера использования слова в
