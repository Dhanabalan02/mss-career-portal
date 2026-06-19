import jwt
from fastapi import APIRouter, Depends, Header, HTTPException, status
from fastapi.responses import RedirectResponse
from app.core.html_helper import serve_html_with_base
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.core.config import settings
from app.crud.notification_crud import (
    get_user_notifications,
    mark_all_notifications_as_read,
    mark_notification_as_read
)

router = APIRouter(prefix="/notifications", tags=["Notifications"])

def get_current_user_and_role(authorization: Optional[str] = Header(default=None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header."
        )
    token = authorization.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = int(payload.get("sub", 0))
        role = payload.get("role")
        
        # Mapping roles to the 'recipient_type' expected by the frontend / DB.
        # hr_head/hr_admin -> 'hr', school_admin -> 'schoolAdmin'
        # Fallback to the direct role string if it doesn't match these exactly
        recipient_type = role
        if role in ["hr_head", "hr_admin", "hr", "hr_team"]:
            recipient_type = "hr"
        elif role in ["school_admin", "schoolAdmin"]:
            recipient_type = "schoolAdmin"
            
        return {"user_id": user_id, "role": recipient_type}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token.")


@router.get("/")
def get_notifications(
    db: Session = Depends(get_db),
    user_info: dict = Depends(get_current_user_and_role)
):
    notifications = get_user_notifications(db, user_info["user_id"], user_info["role"])
    
    # Format for the frontend
    result = []
    for n in notifications:
        result.append({
            "id": n.notification_id,
            "title": n.title or "Notification",
            "message": n.message or "",
            "time": n.created_at.strftime("%b %d, %I:%M %p") if n.created_at else "Just now",
            "read": bool(n.is_read)
        })
    return result


@router.put("/mark-all-read")
def mark_all_read(
    db: Session = Depends(get_db),
    user_info: dict = Depends(get_current_user_and_role)
):
    updated_count = mark_all_notifications_as_read(db, user_info["user_id"], user_info["role"])
    return {"message": "All notifications marked as read", "updated_count": updated_count}


@router.put("/{notification_id}/read")
def mark_read(
    notification_id: int,
    db: Session = Depends(get_db),
    user_info: dict = Depends(get_current_user_and_role)
):
    notification = mark_notification_as_read(db, notification_id, user_info["user_id"])
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found or access denied")
    return {"message": "Notification marked as read"}


@router.get("/view-page")
def view_page():
    return serve_html_with_base("mss-career-portal/pages/candidate/dashboard.html", "/mss-career-portal/pages/candidate/")
