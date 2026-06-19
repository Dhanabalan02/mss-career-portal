from sqlalchemy import Integer, String, func
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.userlogin_model import UserLoginLog
    from app.models.user_roles_model import UserRoles

class Admins(Base):
    __tablename__ = "admins"

    admin_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("user_roles.role_id", ondelete="CASCADE"))
    unit_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    user_roles: Mapped["UserRoles"] = relationship(back_populates="admins")

    def __repr__(self) -> str:
        return f"<Admins(admin_id={self.admin_id}, email='{self.email}')>"
