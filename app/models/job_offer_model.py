from datetime import date, datetime
from typing import Optional
from sqlalchemy import Integer, String, Text, Date, TIMESTAMP, func, ForeignKey
from sqlalchemy.dialects.mysql import TINYINT as TinyInteger
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base
from app.core.timezone import utcnow


class JobOffer(Base):
    __tablename__ = "job_offers"

    job_offer_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_applicant_id: Mapped[int] = mapped_column(ForeignKey("job_applicants.job_applicant_id"), index=True)

    offered_salary: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    joining_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    probation_period: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    offer_issued_date: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP, nullable=True)
    offer_expiry_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    offer_remarks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    offer_template: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    offer_letter_doc: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    offer_letter_doc_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    issued_by: Mapped[Optional[int]] = mapped_column(ForeignKey("admins.admin_id"), nullable=True)
    is_draft: Mapped[Optional[int]] = mapped_column(TinyInteger, server_default="0", nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, default=utcnow, server_default=func.current_timestamp()
    )

    def __repr__(self) -> str:
        return f"<JobOffer(id={self.job_offer_id}, applicant_id={self.job_applicant_id})>"
