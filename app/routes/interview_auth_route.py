import jwt
from typing import Optional
from fastapi import APIRouter, Header, HTTPException, status
from fastapi.responses import RedirectResponse
from app.core.html_helper import serve_html_with_base
from app.core.config import settings

router = APIRouter(prefix="/interview-auth", tags=["Interview Auth"])


@router.get("/feedback-page")
def feedback_page():
    return serve_html_with_base("mss-career-portal/pages/hr/hr-interview-feedback.html", "/mss-career-portal/pages/hr/")


def get_current_admin_id(authorization: Optional[str] = Header(default=None)) -> int:
    """Extracts and validates the admin_id from the JWT Bearer token for HR/Interview tasks."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header."
        )
    token = authorization.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        admin_id = int(payload.get("sub", 0))
        role = payload.get("role")
        if not admin_id or role not in ["hr_head", "hr_admin", "school_admin", "hr_team"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authorized to perform this interview/HR task."
            )
        return admin_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token.")
