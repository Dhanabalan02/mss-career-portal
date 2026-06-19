from datetime import date, datetime
from typing import TYPE_CHECKING, Optional
from sqlalchemy import Integer, String, Date, Text, TIMESTAMP, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user_model import Users

class CandidateExperience(Base):
    __tablename__ = "candidate_experience"

    candidate_experience_id: Mapped[int] = mapped_column(
        Integer, primary_key=True,
        autoincrement=True
    )
    
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), index=True)

    company_name: Mapped[str] = mapped_column(String(255))
    
    job_title: Mapped[str] = mapped_column(String(255))
    
    employment_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    start_date: Mapped[date] = mapped_column(Date)
    
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    
    total_experience: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.current_timestamp()
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp()
    )
    
    users : Mapped["Users"] = relationship(back_populates="candidate_experience_details")

    def __repr__(self) -> str:
        return f"<CandidateExperience(id={self.candidate_experience_id}, user_id={self.user_id}, company='{self.company_name}')>"
