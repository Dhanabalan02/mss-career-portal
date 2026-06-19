import jwt
from typing import Optional, List
from fastapi import APIRouter, Depends, Header, HTTPException, status
from fastapi.responses import RedirectResponse
from app.core.html_helper import serve_html_with_base
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models import UserLoginLog, LoginStatus, Users
from app.crud.job_apply_crud import (
    create_job_application,
    get_candidate_applications,
    check_already_applied
)

router = APIRouter(prefix="/apply", tags=["Apply Jobs"])


def _get_candidate_id_from_token(authorization: Optional[str] = Header(default=None)) -> int:
    """Extracts and validates candidate user_id from JWT token."""
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
        if not user_id or role != "candidate":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token role or subject.")
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token.")


class ScreeningAnswerRequest(BaseModel):
    question_id: int
    answer: str


class JobApplicationRequest(BaseModel):
    job_id: int
    resume_doc: Optional[str] = None
    cover_letter: Optional[str] = None
    expected_salary: Optional[str] = None
    screening_answers: Optional[List[ScreeningAnswerRequest]] = None


def _serialize_application(app):
    return {
        "job_applicant_id": app.job_applicant_id,
        "job_id": app.job_id,
        "user_id": app.user_id,
        "resume_doc": app.resume_doc,
        "cover_letter": app.cover_letter,
        "expected_salary": app.expected_salary,
        "applicant_job_status": app.applicant_job_status,
        "offer_acceptance_status": app.offer_acceptance_status,
        "created_at": app.created_at
    }


@router.get("/check-login")
def check_login_route(
    authorization: Optional[str] = Header(default=None),
    db: Session = Depends(get_db)
):
    """
    Checks if the candidate is logged in and has an active login session record in user_login_logs.
    """
    if not authorization or not authorization.startswith("Bearer "):
        return {"logged_in": False, "detail": "Missing or invalid authorization header."}
    
    token = authorization.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = int(payload.get("sub", 0))
        role = payload.get("role")
        if not user_id or role != "candidate":
            return {"logged_in": False, "detail": "Token is not for a candidate."}

        # Check user_login_logs for active session
        log_entry = (
            db.query(UserLoginLog)
            .filter(
                UserLoginLog.user_id == user_id,
                UserLoginLog.session_id == token,
                UserLoginLog.status == LoginStatus.success,
                UserLoginLog.logout_time.is_(None)
            )
            .first()
        )
        if not log_entry:
            return {"logged_in": False, "detail": "No active session log entry found."}

        user = db.query(Users).filter(Users.user_id == user_id).first()
        if not user:
            return {"logged_in": False, "detail": "User not found."}

        return {
            "logged_in": True,
            "user_id": user_id,
            "name": f"{user.first_name} {user.last_name}".strip(),
            "email": user.email,
            "mobile": user.mobile
        }
    except jwt.ExpiredSignatureError:
        return {"logged_in": False, "detail": "Token expired."}
    except jwt.InvalidTokenError:
        return {"logged_in": False, "detail": "Invalid token."}
    except Exception as e:
        return {"logged_in": False, "detail": str(e)}


@router.post("/")
def apply_for_job_route(
    form_data: JobApplicationRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(_get_candidate_id_from_token)
):
    """Submits a new job application."""
    # Check if already applied
    if check_already_applied(db, user_id=user_id, job_id=form_data.job_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already applied for this job."
        )

    # Note: mss_app_no argument removed from here; handled internally below
    application = create_job_application(
        db=db,
        user_id=user_id,
        job_id=form_data.job_id,
        resume_doc=form_data.resume_doc,
        cover_letter=form_data.cover_letter,
        expected_salary=form_data.expected_salary,
        screening_answers=[ans.model_dump() for ans in form_data.screening_answers] if form_data.screening_answers else None
    )
    return _serialize_application(application)

@router.get("/my-applications")
def get_my_applications_route(
    db: Session = Depends(get_db),
    user_id: int = Depends(_get_candidate_id_from_token)
):
    """Retrieves all applications for the logged-in candidate."""
    applications = get_candidate_applications(db, user_id=user_id)
    return [_serialize_application(app) for app in applications]


@router.get("/check-applied/{job_id}")
def check_applied_route(
    job_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(_get_candidate_id_from_token)
):
    """Checks if the candidate has already applied to a job and returns offer info."""
    applied_app = check_already_applied(db, user_id=user_id, job_id=job_id)
    if not applied_app:
        return {"applied": False}
        
    offer_data = None
    if applied_app.issue_offer == 1:
        offer_data = {
            "offered_salary": applied_app.offered_salary,
            "joining_date": str(applied_app.joining_date) if hasattr(applied_app, 'joining_date') and applied_app.joining_date else None,
            "probation_period": applied_app.probation_period if hasattr(applied_app, 'probation_period') else None,
            "offer_remarks": applied_app.offer_remarks,
            "offer_expiry_date": str(applied_app.offer_expiry_date) if applied_app.offer_expiry_date else None,
            "offer_letter_doc": applied_app.offer_letter_doc,
            "offer_acceptance_status": getattr(applied_app.offer_acceptance_status, 'value', applied_app.offer_acceptance_status) if applied_app.offer_acceptance_status else "pending"
        }
        
    return {
        "applied": True,
        "offer": offer_data
    }

class OfferResponseRequest(BaseModel):
    status: str

@router.patch("/offer/{job_id}/respond")
def respond_to_offer_route(
    job_id: int,
    payload: OfferResponseRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(_get_candidate_id_from_token)
):
    """Candidate accepts or rejects an offer."""
    from app.crud.job_apply_crud import respond_to_offer
    success = respond_to_offer(db, user_id, job_id, payload.status)
    if not success:
        raise HTTPException(status_code=404, detail="Offer not found or update failed")
    return {"success": True}


@router.get("/apply-page")
def apply_page():
    return serve_html_with_base("mss-career-portal/pages/candidate/apply.html", "/mss-career-portal/pages/candidate/")


@router.get("/my-applications-page")
def my_applications_page():
    return serve_html_with_base("mss-career-portal/pages/candidate/dashboard.html", "/mss-career-portal/pages/candidate/")
