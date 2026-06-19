from sqlalchemy import String, func
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import TYPE_CHECKING, List
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.candidate_education_model import CandidateEducationDetail
    from app.models.candidate_experience_model import CandidateExperience
    from app.models.candidate_metadata_model import CandidateMetadata
    from app.models.candidate_screening_answer_model import CandidateScreeningAnswer
    from app.models.job_applicant_model import JobApplicant
    from app.models.user_roles_model import UserRoles

class Users(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    role_id: Mapped[int] = mapped_column(ForeignKey("user_roles.role_id", ondelete="CASCADE"))
    
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    
    gender: Mapped[str] = mapped_column(String(10), nullable=False)
    
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    
    mobile: Mapped[str] = mapped_column(String(15), nullable=False)
    
    image_path: Mapped[str] = mapped_column(String(255), nullable=True)
    
    user_status: Mapped[int] = mapped_column(nullable=False, default=1)
    
    oauth_provider: Mapped[str] = mapped_column(String(50), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())
    
    user_roles: Mapped["UserRoles"] = relationship(back_populates="users")
    candidate_education_details : Mapped[List["CandidateEducationDetail"]] = relationship(back_populates="users")
    candidate_experience_details : Mapped[List["CandidateExperience"]] = relationship(back_populates="users")
    candidate_metadata : Mapped["CandidateMetadata"] = relationship(back_populates="users", uselist=False)
    candidate_screening_answers : Mapped[List["CandidateScreeningAnswer"]] = relationship(back_populates="users")
    job_applicants : Mapped[List["JobApplicant"]] = relationship(back_populates="users")
    
    def __repr__(self) -> str:
        return f"<Users(user_id={self.user_id}, first_name='{self.first_name}', last_name='{self.last_name}', email='{self.email}')>"
