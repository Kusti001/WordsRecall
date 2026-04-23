from pydantic import BaseModel

class WordAdd(BaseModel):
    word: str
    level: str
    meaning: str | None
    example: str | None
    translation: str