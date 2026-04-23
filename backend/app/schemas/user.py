from pydantic import BaseModel

class UserCreate(BaseModel):
    telegram_id: str

class AddWordRequest(BaseModel):
    text: str