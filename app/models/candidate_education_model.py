from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional
from sqlalchemy import Integer, String, Numeric, TIMESTAMP, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user_model import Users

class CandidateEducationDetail(Base):
    __tablename__ = "candidate_education_details"

    candidate_education_details_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), index=True)
    
    education_level: Mapped[str] = mapped_column(String(150), index=True)

    degree_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    specialization: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    institution_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    university_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    start_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    end_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    percentage: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)

    cgpa: Mapped[Optional[Decimal]] = mapped_column(Numeric(4, 2), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, 
        server_default=func.current_timestamp()
    )

    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp()
    )
    
    users : Mapped["Users"] = relationship(back_populates="candidate_education_details")

    def __repr__(self) -> str:
        return (
            f"<CandidateEducationDetail(id={self.candidate_education_details_id}, "
            f"user_id={self.user_id}, level='{self.education_level}')>"
        )
