from datetime import date, datetime
from typing import TYPE_CHECKING, Optional
from sqlalchemy import Integer, String, Date, Text, TIMESTAMP, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user_model import Users

class CandidateMetadata(Base):
    __tablename__ = "candidate_metadata"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), index=True)
    
    date_of_birth: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    
    marital_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    personal_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    state: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    pincode: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    candidate_category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    skills: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    resume_doc: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    profile_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    about: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    designation: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    company: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    experience: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    salary: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    expected_salary: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    notice_period: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    work_mode: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    employment_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    preferred_role: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    languages: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.current_timestamp()
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp()
    )
    
    users : Mapped["Users"] = relationship(back_populates="candidate_metadata")

    def __repr__(self) -> str:
        return f"<CandidateMetadata(id={self.id}, user_id={self.user_id})>"
