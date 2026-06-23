from urllib.parse import urlencode
from typing import List, Optional
from decimal import Decimal
import jwt
from fastapi import APIRouter, Depends, Request, Header, HTTPException, status, UploadFile, File
from fastapi.responses import RedirectResponse
from app.core.html_helper import serve_html_with_base
from sqlalchemy.orm import Session
from app.crud.auth_crud import (
    authenticate_user_roles,
    googlelogin,
    linkedin_login,
    logout_user_logs,
    register_candidate,
    get_candidate_profile_db,
    update_candidate_profile_db,
    get_interviewers_db,
    update_candidate_resume_db,
    update_candidate_profile_image_db,
)
from app.core.config import settings
from app.core.database import get_db
from app.core.oauth import get_google_user_info, get_linkedin_user_info
from pydantic import BaseModel


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


class EducationItem(BaseModel):
    education_level: Optional[str] = None
    degree_name: Optional[str] = None
    specialization: Optional[str] = None
    institution_name: Optional[str] = None
    university_name: Optional[str] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    percentage: Optional[Decimal] = None
    cgpa: Optional[Decimal] = None


class ExperienceItem(BaseModel):
    company_name: str
    job_title: str
    employment_type: Optional[str] = "Full-time"
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    total_experience: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None


class CandidateMetadataUpdate(BaseModel):
    date_of_birth: Optional[str] = None
    personal_address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    pincode: Optional[str] = None
    candidate_category: Optional[str] = None
    skills: Optional[List[str]] = None
    resume_doc: Optional[str] = None
    profile_status: Optional[str] = None
    about: Optional[str] = None
    languages: Optional[str] = None
    designation: Optional[str] = None
    company: Optional[str] = None
    blood_group: Optional[str] = None
    marital_status: Optional[str] = None
    experience: Optional[str] = None
    salary: Optional[str] = None
    notice_period: Optional[str] = None
    employment_type: Optional[str] = None


class CandidateProfileUpdateRequest(BaseModel):
    first_name: str
    last_name: str
    gender: str
    mobile: str
    image_path: Optional[str] = None
    metadata: Optional[CandidateMetadataUpdate] = None
    education: Optional[List[EducationItem]] = None
    experience: Optional[List[ExperienceItem]] = None


class UserLoginRequest(BaseModel):
    email: str
    password: str


class CandidateRegisterRequest(BaseModel):
    email: str
    first_name: str
    last_name: str
    mobile: str
    password: str


router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.get("/units")
def get_units(
    db: Session = Depends(get_db)
):
    """Fetch all units to display in dropdowns/filters"""
    from app.models.unit_model import Units
    units_list = db.query(Units).all()
    return [{"id": u.id, "unit_name": u.unit_name} for u in units_list]

@router.post("/user/login")
def user_login(
    request: Request,
    form_data: UserLoginRequest,
    db: Session = Depends(get_db)
):
    """Login for hr_head, hr_admin, school_admin and candidate roles."""
    client_ip = request.client.host if request.client else None
    return authenticate_user_roles(
        db=db,
        email=form_data.email,
        password=form_data.password,
        ip_address=client_ip
    )


@router.post("/user/logout")
def user_logout(
    request: Request,
    admin_id: int,
    session_id: str,
    db: Session = Depends(get_db)
):
    client_ip = request.client.host if request.client else None
    logout_user_logs(
        db=db,
        admin_id=admin_id,
        session_id=session_id,
        ip_address=client_ip
    )
    return {"message": "Admin logged out successfully."}

@router.post("/candidate/register")
def candidate_register(
    request: Request,
    form_data: CandidateRegisterRequest,
    db: Session = Depends(get_db)
):
    client_ip = request.client.host if request.client else None
    return register_candidate(
        db=db,
        email=form_data.email,
        first_name=form_data.first_name,
        last_name=form_data.last_name,
        mobile=form_data.mobile,
        password=form_data.password,
        ip_address=client_ip
    )


@router.get("/google/login")
def google_login():
    """Redirects the user to Google's OAuth consent screen."""
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent",
    }
    return RedirectResponse(f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}")


@router.get("/google/callback")
def google_callback(
    request: Request,
    code: str,
    db: Session = Depends(get_db)
):
    """Handles the Google OAuth callback and redirects the candidate to the frontend."""
    client_ip = request.client.host if request.client else None
    user_info = get_google_user_info(code)
    result = googlelogin(db=db, email=user_info["email"], name=user_info["name"], ip_address=client_ip)
    params = urlencode({
        "token": result["access_token"],
        "user_type": result["user_type"],
        "name": result["name"],
        "user_id": result["user_id"],
        "email": result["email"],
    })
    return RedirectResponse(f"/mss-career-portal/pages/candidate/oauth-callback.html?{params}")


@router.get("/linkedin/login")
def linkedin_oauth_login():
    """Redirects the user to LinkedIn's OAuth consent screen."""
    params = {
        "client_id": settings.LINKEDIN_CLIENT_ID,
        "redirect_uri": settings.LINKEDIN_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid profile email",
    }
    return RedirectResponse(f"https://www.linkedin.com/oauth/v2/authorization?{urlencode(params)}")


@router.get("/linkedin/callback")
def linkedin_oauth_callback(
    request: Request,
    code: str,
    db: Session = Depends(get_db)
):
    """Handles the LinkedIn OAuth callback and redirects the candidate to the frontend."""
    client_ip = request.client.host if request.client else None
    user_info = get_linkedin_user_info(code)
    result = linkedin_login(db=db, email=user_info["email"], name=user_info["name"], ip_address=client_ip)
    params = urlencode({
        "token": result["access_token"],
        "user_type": result["user_type"],
        "name": result["name"],
        "user_id": result["user_id"],
        "email": result["email"],
    })
    return RedirectResponse(f"/mss-career-portal/pages/candidate/oauth-callback.html?{params}")


@router.get("/candidate/profile")
def get_candidate_profile(
    db: Session = Depends(get_db),
    candidate_id: int = Depends(_get_candidate_id_from_token)
):
    """Retrieves full candidate profile details."""
    return get_candidate_profile_db(db, user_id=candidate_id)


@router.put("/candidate/profile")
def update_candidate_profile(
    form_data: CandidateProfileUpdateRequest,
    db: Session = Depends(get_db),
    candidate_id: int = Depends(_get_candidate_id_from_token)
):
    """Updates candidate profile details."""
    return update_candidate_profile_db(db, user_id=candidate_id, data=form_data.model_dump(exclude_unset=True))


from pathlib import Path
import os
import time

ROUTE_BASE_DIR = Path(__file__).resolve().parent.parent.parent

@router.post("/candidate/upload-resume")
async def upload_candidate_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    candidate_id: int = Depends(_get_candidate_id_from_token)
):
    """Uploads and updates the candidate's resume document."""
    upload_dir = ROUTE_BASE_DIR / "uploads" / "resumes"
    os.makedirs(upload_dir, exist_ok=True)
    
    filename = file.filename
    file_path = upload_dir / filename
    
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
        
    db_path = f"uploads/resumes/{filename}"
    return update_candidate_resume_db(db, user_id=candidate_id, resume_path=db_path)


@router.post("/candidate/upload-profile-image")
async def upload_candidate_profile_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    candidate_id: int = Depends(_get_candidate_id_from_token)
):
    """Uploads and updates the candidate's profile image."""
    upload_dir = ROUTE_BASE_DIR / "uploads" / "profile_images"
    os.makedirs(upload_dir, exist_ok=True)
    
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"profile_{candidate_id}_{int(time.time())}{file_extension}"
    file_path = upload_dir / unique_filename
    
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
        
    # Store relative path for DB so that frontend URL construction works
    db_path = f"uploads/profile_images/{unique_filename}"
    return update_candidate_profile_image_db(db, user_id=candidate_id, image_path=db_path)



def _get_hr_id_from_token(authorization: Optional[str] = Header(default=None)) -> int:
    """Extracts and validates HR admin_id from JWT token (any HR role)."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header."
        )
    token = authorization.split(" ", 1)[1]
    hr_roles = {"hr_head", "hr_admin", "school_admin", "hr_team"}
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        admin_id = int(payload.get("sub", 0))
        role = payload.get("role")
        if not admin_id or role not in hr_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")
        return admin_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token.")


@router.get("/interviewers")
def get_interviewers(
    db: Session = Depends(get_db),
    _: int = Depends(_get_hr_id_from_token)
):
    """Returns all active admins with role_id=3 (interviewers) for use in dropdowns."""
    return get_interviewers_db(db)


@router.get("/register-page")
def register_page():
    return serve_html_with_base("mss-career-portal/pages/candidate/register.html", "/mss-career-portal/pages/candidate/")


@router.get("/login-page")
def login_page():
    return serve_html_with_base("mss-career-portal/pages/candidate/home.html", "/mss-career-portal/pages/candidate/")


@router.get("/oauth-callback-page")
def oauth_callback_page():
    return serve_html_with_base("mss-career-portal/pages/candidate/oauth-callback.html", "/mss-career-portal/pages/candidate/")
