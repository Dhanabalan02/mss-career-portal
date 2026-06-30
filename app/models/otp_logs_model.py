from datetime import datetime
from typing import Optional
from sqlalchemy import Integer, ForeignKey, String, TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base

class OTPLog(Base):
    __tablename__ = "otp_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), index=True)    
    otp: Mapped[int] = mapped_column(Integer)
    is_verified: Mapped[int] = mapped_column(Integer)
    purpose: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, 
        server_default=func.current_timestamp()
    )

    def __repr__(self) -> str:
        return (
            f"<OTPLog(id={self.id}, user_id={self.user_id}, "
            f"otp={self.otp}, is_verified={self.is_verified}, purpose='{self.purpose}')>"
        )