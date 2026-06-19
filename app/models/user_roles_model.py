from typing import TYPE_CHECKING, List
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.admin_model import Admins
    from app.models.user_model import Users

class UserRoles(Base):
    __tablename__ = "user_roles"

    role_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    role_name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)

    admins: Mapped[List["Admins"]] = relationship(back_populates="user_roles")
    users: Mapped[List["Users"]] = relationship(back_populates="user_roles")

    def __repr__(self) -> str:
        return f"<UserRoles(role_id={self.role_id}, role_name='{self.role_name}')>"
