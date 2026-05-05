from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, func
from app.db.base import Base

class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_word_id: Mapped[int] = mapped_column(ForeignKey("user_words.id"))
    result: Mapped[str]
    reviewed_at: Mapped[datetime] = mapped_column(server_default=func.now())

    user_word: Mapped["UserWord"] = relationship(back_populates="reviews")