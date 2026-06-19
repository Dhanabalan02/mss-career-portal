from datetime import datetime
from enum import Enum as PyEnum
from typing import TYPE_CHECKING, Optional
from sqlalchemy import Integer, String, DateTime, Text, Enum, TIMESTAMP, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.admin_model import Admins
    from app.models.user_model import Users

class LoginStatus(str, PyEnum):
    success = "success"
    failed = "failed"

class UserLoginLog(Base):
    __tablename__ = "user_login_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.user_id"), index=True, nullable=True)
    
    user_type: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    login_time: Mapped[datetime] = mapped_column(DateTime, index=True)
    
    login_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    logout_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    status: Mapped[Optional[LoginStatus]] = mapped_column(
        Enum(LoginStatus, name="login_status_enum"), 
        nullable=True
    )
    
    session_id: Mapped[Optional[str]] = mapped_column(Text, index=True, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, 
        server_default=func.current_timestamp()
    )

    def __repr__(self) -> str:
        return f"<UserLoginLog(id={self.id}, user_id={self.user_id}, status='{self.status}')>"
