from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.notification_logs_model import NotificationLog
import datetime

def get_user_notifications(db: Session, user_id: int, role: str):
    """
    Fetch all notifications for a specific user and role, ordered by created_at descending.
    """
    return db.query(NotificationLog).filter(
        NotificationLog.recipient_user_id == user_id,
        NotificationLog.recipient_type == role
    ).order_by(desc(NotificationLog.created_at)).all()

def get_unread_count(db: Session, user_id: int, role: str) -> int:
    """
    Get the count of unread notifications for a specific user and role.
    """
    return db.query(NotificationLog).filter(
        NotificationLog.recipient_user_id == user_id,
        NotificationLog.recipient_type == role,
        NotificationLog.is_read == 0
    ).count()

def mark_notification_as_read(db: Session, notification_id: int, user_id: int):
    """
    Mark a single notification as read, ensuring it belongs to the user.
    """
    notification = db.query(NotificationLog).filter(
        NotificationLog.notification_id == notification_id,
        NotificationLog.recipient_user_id == user_id
    ).first()
    
    if notification and not notification.is_read:
        notification.is_read = 1
        notification.read_at = datetime.datetime.utcnow()
        db.commit()
        db.refresh(notification)
        
    return notification

def mark_all_notifications_as_read(db: Session, user_id: int, role: str):
    """
    Mark all unread notifications for a user as read.
    """
    unread_notifications = db.query(NotificationLog).filter(
        NotificationLog.recipient_user_id == user_id,
        NotificationLog.recipient_type == role,
        NotificationLog.is_read == 0
    ).all()
    
    for notification in unread_notifications:
        notification.is_read = 1
        notification.read_at = datetime.datetime.utcnow()
        
    db.commit()
    return len(unread_notifications)
