from pydantic import BaseModel
from datetime import datetime

class UserBase(BaseModel):
    telegram_id: str
    username: str | None = None

class UserCreate(UserBase):
    pass

class UserRead(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True  # для SQLAlchemy моделей