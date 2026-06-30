from datetime import datetime
from sqlalchemy import Integer, ForeignKey, TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base

class JobViewLog(Base):
    __tablename__ = "job_view_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("job_posts.job_id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), index=True)
    viewed_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.current_timestamp())

    def __repr__(self) -> str:
        return f"<JobViewLog(id={self.id}, job_id={self.job_id}, user_id={self.user_id})>"
