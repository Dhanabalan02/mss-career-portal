from datetime import datetime
from typing import TYPE_CHECKING, Optional, Any, List
from sqlalchemy import Integer, ForeignKey, Text, String, TIMESTAMP, func, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.candidate_screening_answer_model import CandidateScreeningAnswer
    from app.models.job_post_model import JobPost

class JobPreScreeningQuestion(Base):
    __tablename__ = "job_pre_screening_questions"

    question_id: Mapped[int] = mapped_column("question_id", Integer, primary_key=True, autoincrement=True)
    
    job_id: Mapped[int] = mapped_column(ForeignKey("job_posts.job_id"), index=True)
    
    question_text: Mapped[str] = mapped_column(Text)
    
    question_type: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    options: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)

    expected_answer: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.current_timestamp()
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp()
    )
    
    candidate_screening_answers : Mapped[List["CandidateScreeningAnswer"]] = relationship(back_populates="job_pre_screening_questions")
    job_posts : Mapped["JobPost"] = relationship(back_populates="job_pre_screening_questions")

    def __repr__(self) -> str:
        return f"<JobPreScreeningQuestion(id={self.id}, job_id={self.job_id})>"
