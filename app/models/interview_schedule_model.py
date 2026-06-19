from datetime import datetime
from enum import Enum as PyEnum
from typing import TYPE_CHECKING, Optional
from sqlalchemy import Integer, String, Text, Enum, Date, Time, TIMESTAMP, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.interview_remarks_model import InterviewRemark
    from app.models.job_applicant_model import JobApplicant
    from app.models.job_post_model import JobPost

class InterviewMode(str, PyEnum):
    OFFLINE = "offline"
    ONLINE = "online"

class InterviewStatus(str, PyEnum):
    SCHEDULED = "scheduled"
    RESCHEDULED = "rescheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class JobInterviewSchedule(Base):
    __tablename__ = "job_interview_schedule"

    job_interview_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    
    job_id: Mapped[int] = mapped_column(ForeignKey("job_posts.job_id"), index=True)
    
    job_applicant_id: Mapped[int] = mapped_column(ForeignKey("job_applicants.job_applicant_id"), index=True)
    
    interview_round: Mapped[str] = mapped_column(String(100))
    
    interview_mode: Mapped[Optional[InterviewMode]] = mapped_column(
        Enum(InterviewMode, name="interview_mode_enum", values_callable=lambda x: [e.value for e in x]),
        server_default="online",
        nullable=True
    )
    
    scheduled_date: Mapped[datetime] = mapped_column(Date, index=True)
    
    start_time: Mapped[datetime] = mapped_column(Time, index=True)
    
    end_time: Mapped[datetime] = mapped_column(Time, index=True)    
    
    rescheduled_date: Mapped[Optional[datetime]] = mapped_column(Date, nullable=True)
    
    rescheduled_start_time: Mapped[Optional[datetime]] = mapped_column(Time, nullable=True)
    
    rescheduled_end_time: Mapped[Optional[datetime]] = mapped_column(Time, nullable=True)

    meeting_link: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    location: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    interviewer_name: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    
    status: Mapped[Optional[InterviewStatus]] = mapped_column(
        Enum(InterviewStatus, name="interview_status_enum", values_callable=lambda x: [e.value for e in x]),
        server_default="scheduled",
        nullable=True
    )
    
    reschedule_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    cancelled_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_by: Mapped[Optional[int]] = mapped_column(ForeignKey("admins.admin_id"), index=True, nullable=True)
    
    rescheduled_by: Mapped[Optional[int]] = mapped_column(ForeignKey("admins.admin_id"), index=True, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.current_timestamp()
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp()
    )
    
    interview_remarks : Mapped["InterviewRemark"] = relationship(back_populates="job_interview_schedule", uselist=False)
    job_posts : Mapped["JobPost"] = relationship(back_populates="job_interview_schedules")
    job_applicants : Mapped["JobApplicant"] = relationship(back_populates="job_interview_schedules")

    def __repr__(self) -> str:
        return f"<JobInterviewSchedule(id={self.job_interview_id}, job_id={self.job_id}, applicant_id={self.job_applicant_id})>"
