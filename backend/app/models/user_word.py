from datetime import datetime, timezone
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, func
from app.db.base import Base

class UserWord(Base):
    __tablename__ = "user_words"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    word_id: Mapped[int] = mapped_column(ForeignKey("words.id"))
    
    interval: Mapped[int] = mapped_column(default=1)
    repetitions: Mapped[int] = mapped_column(default=0)
    next_review: Mapped[datetime] = mapped_column(server_default=func.now())

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="user_words")
    word: Mapped["Word"] = relationship(back_populates="user_words")
    reviews: Mapped[list["Review"]] = relationship(back_populates="user_word")