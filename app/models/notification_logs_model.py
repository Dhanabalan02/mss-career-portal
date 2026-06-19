from datetime import datetime
from typing import Optional
from sqlalchemy import Integer, String, Text, DateTime, TIMESTAMP, func
from sqlalchemy.dialects.mysql import TINYINT as TinyInteger
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class NotificationLog(Base):
    __tablename__ = "notification_logs"

    notification_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    sender_user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    recipient_user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    sender_type: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
          
    recipient_type: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)   

    recipient_mobile: Mapped[Optional[str]] = mapped_column(String(15), nullable=True)
    
    recipient_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    notification_type: Mapped[Optional[str]] = mapped_column(String(100), index=True, nullable=True)
    
    channel: Mapped[Optional[str]] = mapped_column(String(50), index=True, nullable=True)
    
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    status: Mapped[Optional[str]] = mapped_column(String(50), index=True, nullable=True)
    
    is_read: Mapped[Optional[int]] = mapped_column(TinyInteger, server_default="0", nullable=True)
    
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.current_timestamp())
     
    updated_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP, onupdate=func.current_timestamp(), nullable=True)

    def __repr__(self) -> str:
        return f"<NotificationLog(id={self.notification_id}, type={self.notification_type}, status={self.status})>"
