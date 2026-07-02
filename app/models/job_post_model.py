from datetime import date, datetime
from enum import Enum as PyEnum
from typing import TYPE_CHECKING, Optional, List
from sqlalchemy import Integer, String, Text, Date, Enum, TIMESTAMP, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.candidate_screening_answer_model import CandidateScreeningAnswer
    from app.models.interview_schedule_model import JobInterviewSchedule
    from app.models.job_applicant_model import JobApplicant
    from app.models.job_prescreeningquestion_model import JobPreScreeningQuestion

class JobStatus(str, PyEnum):
    PUBLISH = "publish"
    DRAFT = "draft"
    CLOSED = "closed"

class JobPost(Base):
    __tablename__ = "job_posts"

    job_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    job_posted_by: Mapped[int] = mapped_column(ForeignKey("admins.admin_id"), index=True)
    
    job_title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    job_type: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    job_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    school_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    department: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    programme: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    vacancy_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    min_exp: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    max_exp: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    skills_required: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    education_qualification: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    closing_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    
    additional_requirements: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    job_status: Mapped[Optional[JobStatus]] = mapped_column(
        Enum(JobStatus, name="job_status_enum", values_callable=lambda x: [e.value for e in x]), 
        nullable=True
    )
    
    views: Mapped[Optional[int]] = mapped_column(Integer, default=0, nullable=True)
    
    uuid: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.current_timestamp()
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp()
    )
    
    candidate_screening_answers : Mapped[List["CandidateScreeningAnswer"]] = relationship(back_populates="job_posts")
    job_interview_schedules : Mapped[List["JobInterviewSchedule"]] = relationship(back_populates="job_posts")
    job_pre_screening_questions : Mapped[List["JobPreScreeningQuestion"]] = relationship(
        back_populates="job_posts", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<JobPost(id={self.job_id}, title='{self.job_title}', status='{self.job_status}')>"
