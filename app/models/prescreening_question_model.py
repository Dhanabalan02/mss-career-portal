from sqlalchemy import Integer, Boolean, Text, ForeignKey
from datetime import datetime
from app.models.base import Base
from sqlalchemy.orm import Mapped, mapped_column

class PrescreeningQuestion(Base):
    __tablename__ = "pre_screening_questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    questions: Mapped[str] = mapped_column(Text, nullable=False)
    created_by: Mapped[int] = mapped_column(ForeignKey("admins.admin_id"), nullable=False)
    updated_by: Mapped[int] = mapped_column(ForeignKey("admins.admin_id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<PrescreeningQuestion(id={self.id}, questions='{self.questions}', created_by={self.created_by}, updated_by={self.updated_by})>"