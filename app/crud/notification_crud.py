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

def create_notification(
    db: Session,
    recipient_user_id: int,
    recipient_type: str,
    title: str,
    message: str,
    sender_user_id: int = None,
    sender_type: str = None,
    channel: str = "in_app",
    notification_type: str = None,
    recipient_email: str = None,
    recipient_mobile: str = None
) -> NotificationLog:
    """
    Create a new notification log in the database.
    """
    db_notification = NotificationLog(
        sender_user_id=sender_user_id,
        recipient_user_id=recipient_user_id,
        sender_type=sender_type,
        recipient_type=recipient_type,
        channel=channel,
        title=title,
        message=message,
        status="sent",
        is_read=0,
        notification_type=notification_type,
        recipient_email=recipient_email,
        recipient_mobile=recipient_mobile
    )
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification

def notify_candidate(
    db: Session,
    candidate_id: int,
    title: str,
    message: str,
    notification_type: str = "general",
    sender_user_id: int = None,
    sender_type: str = None
) -> NotificationLog:
    """
    Send an in-app notification to a candidate.
    """
    return create_notification(
        db=db,
        recipient_user_id=candidate_id,
        recipient_type="candidate",
        title=title,
        message=message,
        notification_type=notification_type,
        sender_user_id=sender_user_id,
        sender_type=sender_type
    )

def notify_school_admin(
    db: Session,
    admin_id: int,
    title: str,
    message: str,
    notification_type: str = "general",
    sender_user_id: int = None,
    sender_type: str = None
) -> NotificationLog:
    """
    Send an in-app notification to a school admin.
    """
    return create_notification(
        db=db,
        recipient_user_id=admin_id,
        recipient_type="schoolAdmin",
        title=title,
        message=message,
        notification_type=notification_type,
        sender_user_id=sender_user_id,
        sender_type=sender_type
    )

def notify_hr_users(
    db: Session,
    title: str,
    message: str,
    notification_type: str = "general",
    sender_user_id: int = None,
    sender_type: str = None
) -> int:
    """
    Send an in-app notification to all active HR admins/heads/team members.
    """
    from app.models.admin_model import Admins
    from app.models.user_roles_model import UserRoles
    
    hr_admins = db.query(Admins).join(UserRoles).filter(
        UserRoles.role_name.in_(["hr_head", "hr_admin", "hr_team"]),
        Admins.is_active == 1
    ).all()
    
    sent_count = 0
    for hr in hr_admins:
        create_notification(
            db=db,
            recipient_user_id=hr.admin_id,
            recipient_type="hr",
            title=title,
            message=message,
            notification_type=notification_type,
            sender_user_id=sender_user_id,
            sender_type=sender_type
        )
        sent_count += 1
        
    return sent_count

