from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import func
from app.db.base import Base

class Word(Base):
    __tablename__ = "words"

    id: Mapped[int] = mapped_column(primary_key=True)
    word: Mapped[str] = mapped_column(unique=True)
    level: Mapped[str | None]
    meaning: Mapped[str | None]
    example: Mapped[str | None]
    translation: Mapped[str]

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    user_words: Mapped[list["UserWord"]] = relationship(back_populates="word")