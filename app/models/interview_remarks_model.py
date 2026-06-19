from datetime import datetime
from enum import Enum as PyEnum
from typing import TYPE_CHECKING, Optional
from sqlalchemy import Integer, String, Text, Enum, TIMESTAMP, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.interview_schedule_model import JobInterviewSchedule

class ApplicantStatus(str, PyEnum):
    SELECTED = "selected"
    REJECTED = "rejected"
    HOLD = "hold"
    NEXT_ROUND = "next_round"

class InterviewRemark(Base):
    __tablename__ = "interview_remarks"

    interview_remarks_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    
    job_interview_id: Mapped[int] = mapped_column(ForeignKey("job_interview_schedule.job_interview_id"), index=True)
    
    round: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    remarks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    applicant_status: Mapped[ApplicantStatus] = mapped_column(
        Enum(ApplicantStatus, name="applicant_status_enum")
    )
    
    created_by: Mapped[int] = mapped_column(Integer)
    
    updated_by: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.current_timestamp()
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp()
    )
    
    job_interview_schedule : Mapped["JobInterviewSchedule"] = relationship(back_populates="interview_remarks")
    
    def __repr__(self) -> str:
        return f"<InterviewRemark(id={self.interview_remarks_id}, job_interview_id={self.job_interview_id}, status='{self.applicant_status}')>"
