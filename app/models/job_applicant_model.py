from datetime import date, datetime
from decimal import Decimal
from enum import Enum as PyEnum
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import Integer, String, Text, Numeric, Enum, Date, TIMESTAMP, func, ForeignKey
from sqlalchemy.dialects.mysql import TINYINT as TinyInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.interview_schedule_model import JobInterviewSchedule
    from app.models.job_post_model import JobPost
    from app.models.user_model import Users


class ApplicantJobStatus(str, PyEnum):
    NEXT_ROUND = "next_round"
    SELECTED = "selected"
    REJECTED = "rejected"
    HOLD = "hold"


class OfferAcceptanceStatus(str, PyEnum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    EXPIRED = "expired"
    REJECTED = "rejected"


class ApplicantStage(str, PyEnum):
    APPLIED = "applied"
    SCREENED = "screened"
    INTERVIEW = "interview"
    OFFER = "offer"
    OFFER_ACCEPTED = "offer_accepted"
    ONBOARDING = "onboarding"


class JobApplicant(Base):
    __tablename__ = "job_applicants"

    job_applicant_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    mss_app_no: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    job_id: Mapped[int] = mapped_column(Integer, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), index=True)

    resume_doc: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    cover_letter: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    skills_match: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)

    applicant_job_status: Mapped[Optional[ApplicantJobStatus]] = mapped_column(
        Enum(ApplicantJobStatus, name="applicant_job_status_enum",
             values_callable=lambda x: [e.value for e in x]),
        nullable=True,
    )

    applicant_stage: Mapped[Optional[ApplicantStage]] = mapped_column(
        Enum(ApplicantStage, name="applicant_stage_enum",
             values_callable=lambda x: [e.value for e in x]),
        nullable=True,
    )

    # Offer fields
    offered_salary: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    joining_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    probation_period: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    issue_offer: Mapped[Optional[int]] = mapped_column(TinyInteger, server_default="0", nullable=True)
    offer_letter_doc: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    issued_by: Mapped[Optional[int]] = mapped_column(ForeignKey("admins.admin_id"), nullable=True)
    offer_acceptance_status: Mapped[Optional[OfferAcceptanceStatus]] = mapped_column(
        Enum(OfferAcceptanceStatus, name="offer_acceptance_status_enum",
             values_callable=lambda x: [e.value for e in x]),
        server_default="pending",
        nullable=True,
    )
    offer_issued_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    offer_expiry_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    offer_remarks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    offer_template: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # MASSET sync fields
    sync_masset: Mapped[Optional[int]] = mapped_column(TinyInteger, server_default="0", nullable=True)
    masset_synced_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP, nullable=True)
    masset_synced_by: Mapped[Optional[int]] = mapped_column(ForeignKey("admins.admin_id"), nullable=True)
    masset_employee_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    masset_status: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    issue_appointment_order: Mapped[Optional[int]] = mapped_column(TinyInteger, server_default="0", nullable=True)

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp()
    )

    users: Mapped["Users"] = relationship(back_populates="job_applicants")
    job_interview_schedules: Mapped[List["JobInterviewSchedule"]] = relationship(
        back_populates="job_applicants"
    )

    def __repr__(self) -> str:
        return f"<JobApplicant(id={self.job_applicant_id}, job_id={self.job_id}, user_id={self.user_id})>"
