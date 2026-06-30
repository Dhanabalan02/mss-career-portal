import jwt
from typing import Optional, List
from fastapi import APIRouter, Depends, Header, HTTPException, status
from fastapi.responses import RedirectResponse
from app.core.html_helper import serve_html_with_base
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models import UserLoginLog, LoginStatus, Users, CandidateMetadata
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
    screening_answers: Optional[List[ScreeningAnswerRequest]] = None


def _serialize_application(app):
    return {
        "job_applicant_id": app.job_applicant_id,
        "job_id": app.job_id,
        "user_id": app.user_id,
        "resume_doc": app.resume_doc,
        "cover_letter": app.cover_letter,
        "applicant_job_status": app.applicant_job_status,
        "offer_acceptance_status": getattr(app.offer_acceptance_status, 'value', app.offer_acceptance_status) if app.offer_acceptance_status else None,
        "created_at": app.created_at,
        "job_title": app.job.job_title if hasattr(app, 'job') and app.job else None,
        "school_name": app.job.school_name if hasattr(app, 'job') and app.job else None,
        "department": app.job.department if hasattr(app, 'job') and app.job else None,
        "location": app.job.location if hasattr(app, 'job') and app.job else None,
        "job_type": app.job.job_type if hasattr(app, 'job') and app.job else None,
        "stage": getattr(app.applicant_stage, 'value', app.applicant_stage) if getattr(app, 'applicant_stage', None) else "Applied",
        "issue_offer": app.issue_offer if hasattr(app, 'issue_offer') else 0
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

        meta = db.query(CandidateMetadata).filter(CandidateMetadata.user_id == user_id).first()
        resume_doc = meta.resume_doc if meta else ""

        return {
            "logged_in": True,
            "user_id": user_id,
            "name": f"{user.first_name} {user.last_name}".strip(),
            "email": user.email,
            "mobile": user.mobile,
            "resume_doc": resume_doc
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
        screening_answers=[ans.model_dump() for ans in form_data.screening_answers] if form_data.screening_answers else None
    )
    
    # Send Notifications
    try:
        from app.models.job_post_model import JobPost
        from app.models.user_model import Users
        from app.crud.notification_crud import notify_candidate, notify_hr_users, create_notification
        from app.models.admin_model import Admins
        
        job = db.query(JobPost).filter(JobPost.job_id == form_data.job_id).first()
        candidate = db.query(Users).filter(Users.user_id == user_id).first()
        
        if job and candidate:
            candidate_name = f"{candidate.first_name} {candidate.last_name}".strip()
            #Notify HR Users
            notify_hr_users(
                db=db,
                title="New Job Application",
                message=f"New application received from {candidate_name} for '{job.job_title}' at {job.school_name}.",
                notification_type="new_application",
                sender_user_id=user_id,
                sender_type="candidate"
            )
    except Exception as e:
        from app.core.logger import logger
        logger.error(f"Error creating job application notifications: {e}")

    return _serialize_application(application)

@router.get("/my-applications")
def get_my_applications_route(
    db: Session = Depends(get_db),
    user_id: int = Depends(_get_candidate_id_from_token)
):
    """Retrieves all applications for the logged-in candidate."""
    applications = get_candidate_applications(db, user_id=user_id)
    
    from app.models.job_post_model import JobPost
    job_ids = [app.job_id for app in applications]
    jobs = db.query(JobPost).filter(JobPost.job_id.in_(job_ids)).all() if job_ids else []
    job_map = {job.job_id: job for job in jobs}
    
    for app in applications:
        setattr(app, 'job', job_map.get(app.job_id))
        
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
        
    # Send Notifications
    try:
        from app.models.job_post_model import JobPost
        from app.models.user_model import Users
        from app.crud.notification_crud import notify_candidate, notify_hr_users, create_notification
        from app.models.admin_model import Admins
        
        job = db.query(JobPost).filter(JobPost.job_id == job_id).first()
        candidate = db.query(Users).filter(Users.user_id == user_id).first()
        
        if job and candidate:
            candidate_name = f"{candidate.first_name} {candidate.last_name}".strip()
            status_cap = payload.status.capitalize()
            
            # 1. Notify Job Poster (School Admin or HR)
            poster = db.query(Admins).filter(Admins.admin_id == job.job_posted_by).first()
            if poster:
                poster_role = poster.user_roles.role_name if poster.user_roles else ""
                recipient_type = "hr" if poster_role in ["hr_head", "hr_admin", "hr_team"] else "schoolAdmin"
                if recipient_type == "schoolAdmin":
                    create_notification(
                        db=db,
                        recipient_user_id=poster.admin_id,
                        recipient_type=recipient_type,
                        title=f"Offer {status_cap}",
                        message=f"Candidate {candidate_name} has {payload.status} the offer for '{job.job_title}'.",
                        notification_type=f"offer_{payload.status.lower()}",
                        sender_user_id=user_id,
                        sender_type="candidate"
                    )
                
            # 2. Notify HR Users
            notify_hr_users(
                db=db,
                title=f"Offer {status_cap}",
                message=f"Candidate {candidate_name} has {payload.status} the offer for '{job.job_title}' at {job.school_name}.",
                notification_type=f"offer_{payload.status.lower()}",
                sender_user_id=user_id,
                sender_type="candidate"
            )
    except Exception as e:
        from app.core.logger import logger
        logger.error(f"Error creating offer response notifications: {e}")
        
    return {"success": True}


@router.get("/apply-page")
def apply_page():
    return serve_html_with_base("mss-career-portal/pages/candidate/apply.html", "/mss-career-portal/pages/candidate/")


@router.get("/my-applications-page")
def my_applications_page():
    return serve_html_with_base("mss-career-portal/pages/candidate/dashboard.html", "/mss-career-portal/pages/candidate/")

@router.get("/download/{filename:path}")
def download_resume_route(filename: str, inline: bool = False):
    import os
    from fastapi import HTTPException
    from fastapi.responses import FileResponse
    import mimetypes
    
    print(f"DEBUG download: original filename = {repr(filename)}")
    
    from pathlib import Path

    # Base directory of the project (parent of 'app')
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    
    # Normalize path separators
    normalized_path = filename.replace("\\", "/")
    print(f"DEBUG download: normalized_path = {repr(normalized_path)}")
    download_name = os.path.basename(normalized_path)
    
    # Check absolute path from BASE_DIR
    target_path = BASE_DIR / normalized_path
    
    if not target_path.exists():
        # Fallback to app/uploads/resumes
        fallback_path = BASE_DIR / "app" / "uploads" / "resumes" / download_name
        if fallback_path.exists():
            target_path = fallback_path
        else:
            # Fallback to root uploads/resumes
            fallback_path2 = BASE_DIR / "uploads" / "resumes" / download_name
            if fallback_path2.exists():
                target_path = fallback_path2
            else:
                target_path = None
            
    print(f"DEBUG download: target_path = {repr(target_path)}")
    if not target_path:
        raise HTTPException(status_code=404, detail="File not found")
        
    media_type, _ = mimetypes.guess_type(str(target_path))
    if not media_type:
        media_type = "application/octet-stream"

    content_disposition_type = "inline" if inline else "attachment"

    return FileResponse(
        target_path, 
        media_type=media_type, 
        filename=download_name,
        content_disposition_type=content_disposition_type
    )
