from datetime import datetime
from enum import Enum as PyEnum
from typing import TYPE_CHECKING, Optional
from sqlalchemy import Integer, String, Text, Enum, TIMESTAMP, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.job_post_model import JobPost
    from app.models.job_prescreeningquestion_model import JobPreScreeningQuestion
    from app.models.user_model import Users

class CandidateStatus(str, PyEnum):
    REJECTED = "rejected"
    INTERVIEW_PROGRESS = "interview_progress"
    INELIGIBLE = "ineligible"
    SCREENED = "screened"

class CandidateScreeningAnswer(Base):
    __tablename__ = "candidate_screening_answers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    candidate_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), index=True)
    
    job_id: Mapped[int] = mapped_column(ForeignKey("job_posts.job_id"), index=True)
    
    question_id: Mapped[Optional[int]] = mapped_column(ForeignKey("job_pre_screening_questions.question_id"), nullable=True)
    
    answer: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    remarks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    candidate_status: Mapped[Optional[CandidateStatus]] = mapped_column(
        Enum(CandidateStatus, name="candidate_status_enum", values_callable=lambda x: [e.value for e in x]), 
        nullable=True
    )
    
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.current_timestamp()
    )
    
    users : Mapped["Users"] = relationship(back_populates="candidate_screening_answers")
    job_posts : Mapped["JobPost"] = relationship(back_populates="candidate_screening_answers")
    job_pre_screening_questions : Mapped["JobPreScreeningQuestion"] = relationship(back_populates="candidate_screening_answers")

    def __repr__(self) -> str:
        return f"<CandidateScreeningAnswer(id={self.id}, candidate_id={self.candidate_id}, job_id={self.job_id})>"
