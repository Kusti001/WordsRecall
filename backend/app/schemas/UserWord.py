from pydantic import BaseModel

class AddWordRequest(BaseModel):
    text: str  # слово на русском или английском