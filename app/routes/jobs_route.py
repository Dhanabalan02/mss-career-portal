from datetime import date
from typing import Any, List, Optional

import jwt
from fastapi import APIRouter, Depends, Header, HTTPException, status
from fastapi.responses import RedirectResponse
from app.core.html_helper import serve_html_with_base
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.crud.jobs_crud import (
    create_job_post,
    update_job_post,
    update_job_status,
    get_admin_job_posts,
    get_job_post_or_404,
    get_published_job_posts,
    get_published_job_post_or_404,
    get_job_prescreening_questions,
    clone_job_post,
)
from app.models import (
    JobPost,
    JobStatus,
    JobPreScreeningQuestion,
    JobApplicant,
    Users,
    JobInterviewSchedule,
    CandidateExperience,
    CandidateEducationDetail,
    CandidateMetadata,
    CandidateScreeningAnswer,
    ApplicantJobStatus,
    ApplicantStage,
    InterviewStatus,
    InterviewRemark,
)
from app.models.job_applicant_model import OfferAcceptanceStatus
from sqlalchemy import or_

router = APIRouter(prefix="/jobs", tags=["Job Posts"])


def _get_admin_id_from_token(
    authorization: Optional[str] = Header(default=None),
) -> int:
    """Extracts and validates the admin_id from the JWT Bearer token."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header.",
        )
    token = authorization.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        admin_id = int(payload.get("sub", 0))
        if not admin_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload.",
            )
        return admin_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired."
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token."
        )

class PreScreeningQuestionRequest(BaseModel):
    question_text: str
    question_type: Optional[str] = None
    options: Optional[Any] = None
    expected_answer: Optional[str] = None


class JobPostCreateRequest(BaseModel):
    job_posted_by: Optional[int] = (
        None  # Ignored — admin_id is derived from the JWT token
    )
    job_title: Optional[str] = None
    department: Optional[str] = None
    job_type: Optional[str] = None
    vacancy_count: Optional[int] = None
    school_name: Optional[str] = None
    location: Optional[str] = None
    programme: Optional[str] = None
    min_exp: Optional[str] = None
    max_exp: Optional[str] = None
    closing_date: Optional[date] = None
    job_description: Optional[str] = None
    skills_required: Optional[str] = None
    education_qualification: Optional[str] = None
    additional_requirements: Optional[str] = None
    job_status: JobStatus = JobStatus.PUBLISH
    pre_screening_questions: Optional[List[PreScreeningQuestionRequest]] = None


class JobPostUpdateRequest(BaseModel):
    job_title: Optional[str] = None
    department: Optional[str] = None
    job_type: Optional[str] = None
    vacancy_count: Optional[int] = None
    school_name: Optional[str] = None
    location: Optional[str] = None
    programme: Optional[str] = None
    min_exp: Optional[str] = None
    max_exp: Optional[str] = None
    closing_date: Optional[date] = None
    job_description: Optional[str] = None
    skills_required: Optional[str] = None
    education_qualification: Optional[str] = None
    additional_requirements: Optional[str] = None
    job_status: Optional[JobStatus] = None
    pre_screening_questions: Optional[List[PreScreeningQuestionRequest]] = None


def _serialize_job_post(job_post: JobPost, db: Optional[Session] = None) -> dict:
    is_clone = False
    if db:
        is_clone = (
            db.query(JobPost)
            .filter(
                JobPost.job_posted_by == job_post.job_posted_by,
                JobPost.job_title == job_post.job_title,
                JobPost.job_id < job_post.job_id,
            )
            .first()
            is not None
        )

    published_date = None
    if (
        job_post.job_status == JobStatus.PUBLISH
        or getattr(job_post.job_status, "value", None) == "publish"
    ):
        published_date = (
            job_post.updated_at.isoformat() if job_post.updated_at else None
        )

    applicant_count = 0
    if db:
        applicant_count = (
            db.query(JobApplicant)
            .filter(JobApplicant.job_id == job_post.job_id)
            .count()
        )

    return {
        "job_id": job_post.job_id,
        "job_posted_by": job_post.job_posted_by,
        "job_title": job_post.job_title,
        "department": job_post.department,
        "job_type": job_post.job_type,
        "vacancy_count": job_post.vacancy_count,
        "school_name": job_post.school_name,
        "location": job_post.location,
        "programme": job_post.programme,
        "min_exp": job_post.min_exp,
        "max_exp": job_post.max_exp,
        "closing_date": job_post.closing_date,
        "job_description": job_post.job_description,
        "skills_required": job_post.skills_required,
        "education_qualification": job_post.education_qualification,
        "additional_requirements": job_post.additional_requirements,
        "job_status": job_post.job_status,
        "is_clone": is_clone,
        "published_date": published_date,
        "applicant_count": applicant_count,
        "views": job_post.views or 0,
        "pre_screening_questions": (
            [
                {
                    "question_id": q.question_id,
                    "question_text": q.question_text,
                    "question_type": q.question_type,
                    "options": q.options,
                    "expected_answer": q.expected_answer,
                }
                for q in job_post.job_pre_screening_questions
            ]
            if job_post.job_pre_screening_questions
            else []
        ),
    }


@router.get("/")
def get_job_post_route(
    db: Session = Depends(get_db), admin_id: int = Depends(_get_admin_id_from_token)
):
    """Retrieves all job posts created by the current admin."""
    job_posts = get_admin_job_posts(db, admin_id=admin_id)

    return [_serialize_job_post(job_post, db=db) for job_post in job_posts]


@router.get("/public")
def get_public_job_posts_route(school_name: Optional[str] = None, db: Session = Depends(get_db)):
    """Retrieves all published job posts. No authentication required — used by the public candidate-facing site."""
    job_posts = get_published_job_posts(db, school_name=school_name)
    return [_serialize_job_post(job_post, db=db) for job_post in job_posts]


@router.get("/public/{job_id}")
def get_public_job_post_by_id_route(job_id: int, db: Session = Depends(get_db)):
    """Retrieves a single published job post by its ID. No authentication required."""
    job_post = get_published_job_post_or_404(db, job_id=job_id)
    return _serialize_job_post(job_post, db=db)


def _get_candidate_id_from_token_opt(authorization: Optional[str] = Header(default=None)) -> Optional[int]:
    """Extracts and validates candidate user_id from JWT token. Returns None if invalid or missing."""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = int(payload.get("sub", 0))
        role = payload.get("role")
        if not user_id or role != "candidate":
            return None
        return user_id
    except:
        return None


@router.post("/public/{job_id}/view")
def increment_job_view_route(
    job_id: int, 
    db: Session = Depends(get_db), 
    user_id: Optional[int] = Depends(_get_candidate_id_from_token_opt)
):
    """Increments the view count for a published job. Only counts once per logged-in user."""
    job_post = get_published_job_post_or_404(db, job_id=job_id)
    
    # If not logged in, we do not increment to keep it strict to "logged in user once view".
    # (Or we could increment once per IP, but per requirement we only track for logged-in users)
    if not user_id:
        return {"view_counted": False, "reason": "Not logged in"}
        
    from app.models.job_view_log_model import JobViewLog
    
    # Check if they already viewed it
    existing_log = db.query(JobViewLog).filter(
        JobViewLog.job_id == job_id,
        JobViewLog.user_id == user_id
    ).first()
    
    if existing_log:
        return {"view_counted": False, "reason": "Already viewed"}
        
    # Add new view log
    new_log = JobViewLog(job_id=job_id, user_id=user_id)
    db.add(new_log)
    
    if not job_post.views:
        job_post.views = 0
    job_post.views += 1
    
    db.commit()
    return {"view_counted": True, "views": job_post.views}


class ApplicantStatusUpdateRequest(BaseModel):
    status: str
    remarks: Optional[str] = None


@router.get("/applicants")
def get_applicants_route(
    job_id: Optional[int] = None,
    stage: Optional[str] = None,
    search: Optional[str] = None,
    exp: Optional[str] = None,
    db: Session = Depends(get_db),
    admin_id: int = Depends(_get_admin_id_from_token),
):
    from app.models import (
        Admins,
        JobApplicant,
        JobPost,
        JobInterviewSchedule,
        InterviewRemark,
        CandidateExperience,
    )
    from sqlalchemy.orm import joinedload

    admin = (
        db.query(Admins)
        .options(joinedload(Admins.user_roles))
        .filter(Admins.admin_id == admin_id)
        .first()
    )
    is_hr = admin is not None and admin.user_roles.role_name in {
        "hr_head",
        "hr_team",
        "hr_admin",
    }

    query = db.query(JobApplicant).join(JobPost, JobApplicant.job_id == JobPost.job_id)
    if not is_hr:
        query = query.filter(JobPost.job_posted_by == admin_id)

    if job_id:
        query = query.filter(JobApplicant.job_id == job_id)

    all_applicants = query.all()

    serialized_applicants = []
    colors = [
        "#378ADD",
        "#534AB7",
        "#1D9E75",
        "#EF9F27",
        "#D85A30",
        "#0891b2",
        "#993C1D",
        "#0F6E56",
    ]

    total_count = 0
    interviewing_count = 0
    offers_count = 0
    onboarding_count = 0

    chip_counts = {
        "Applied": 0,
        "Screened": 0,
        "Interview": 0,
        "Offer": 0,
        "Offer Accepted": 0,
        "Onboarding": 0,
        "Rejected": 0,
    }

    from datetime import datetime, date

    for idx, app in enumerate(all_applicants):
        user = app.users
        job_post = db.query(JobPost).filter(JobPost.job_id == app.job_id).first()
        job_title = job_post.job_title if job_post else "Unknown Job"

        name = f"{user.first_name} {user.last_name}".strip()
        avatar = "".join([part[0] for part in name.split() if part]).upper()
        color = colors[idx % len(colors)]

        # Get all interview schedules for this applicant
        interviews = (
            db.query(JobInterviewSchedule)
            .filter(JobInterviewSchedule.job_applicant_id == app.job_applicant_id)
            .order_by(JobInterviewSchedule.job_interview_id.desc())
            .all()
        )

        # Calculate stage and status text
        from app.crud.common import compute_stage

        stage_val = compute_stage(app, len(interviews) > 0)
        interview_status = "Pending"


        if len(interviews) > 0:
            latest_int = interviews[0]

            # --- FETCHING DIRECTLY FROM INTERVIEW_REMARKS RELATIONSHIP ---
            remark = (
                db.query(InterviewRemark)
                .filter(InterviewRemark.job_interview_id == latest_int.job_interview_id)
                .first()
            )

            if remark and remark.applicant_status:
                if remark.applicant_status == "next_round":
                    interview_status = "Next Round"
                else:
                    interview_status = remark.applicant_status.capitalize()
            elif latest_int.status == "completed":
                interview_status = "Completed"
            else:
                interview_status = (
                    latest_int.status.value.capitalize()
                    if hasattr(latest_int.status, "value")
                    else str(latest_int.status).capitalize()
                )

        # Calculate experience from CandidateExperience
        exp_records = (
            db.query(CandidateExperience)
            .filter(CandidateExperience.user_id == user.user_id)
            .all()
        )

        total_experience = 0.0
        for exp_rec in exp_records:
            if exp_rec.total_experience:
                try:
                    num_part = str(exp_rec.total_experience).strip().split()[0]
                    total_experience += float(num_part)
                except (ValueError, IndexError):
                    continue

        if total_experience > 0:
            exp_str = f"{round(total_experience, 1)} yrs"
        else:
            exp_str = "—"

        # Increment chip counts
        if stage_val in chip_counts:
            chip_counts[stage_val] += 1

        # Stats counts
        total_count += 1
        if stage_val == "Interview":
            interviewing_count += 1
        elif stage_val in ["Offer", "Offer Accepted"]:
            offers_count += 1
        elif stage_val == "Onboarding":
            onboarding_count += 1

        # Filter matching
        if search:
            search_lower = search.lower()
            if (
                search_lower not in name.lower()
                and search_lower not in job_title.lower()
            ):
                continue
        if stage and stage != stage_val:
            continue

        # FIX: Changed exp_years to total_experience to resolve NameError crashes
        if exp:
            if exp == "0-3 yrs" and not (0 <= total_experience <= 3):
                continue
            elif exp == "3-6 yrs" and not (3 < total_experience <= 6):
                continue
            elif exp == "6-10 yrs" and not (6 < total_experience <= 10):
                continue
            elif exp == "10+ yrs" and not (total_experience > 10):
                continue

        serialized_applicants.append(
            {
                "id": app.job_applicant_id,
                "job_id": app.job_id,
                "name": name,
                "job": job_title,
                "appliedDate": (
                    app.created_at.strftime("%Y-%m-%d") if app.created_at else ""
                ),
                "exp": exp_str,
                "stage": stage_val,
                "interviewStatus": interview_status,
                "interview_round": (
                    interviews[0].interview_round if len(interviews) > 0 else ""
                ),
                "avatar": avatar,
                "color": color,
            }
        )

    unique_jobs_count = (
        len(set(app.job_id for app in all_applicants)) if all_applicants else 0
    )
    interview_pct = (
        round((interviewing_count / total_count * 100), 1) if total_count > 0 else 0
    )
    accepted_count = chip_counts.get("Offer Accepted", 0)

    current_month = datetime.now().month
    current_year = datetime.now().year
    onboarding_this_month = 0
    for app in all_applicants:
        if app.applicant_stage and app.applicant_stage.value == "Onboarding":
            if (
                app.updated_at
                and app.updated_at.month == current_month
                and app.updated_at.year == current_year
            ):
                onboarding_this_month += 1

    return {
        "applicants": serialized_applicants,
        "stats": {
            "total": total_count,
            "interview": interviewing_count,
            "offers": offers_count,
            "onboarding": onboarding_count,
            "deltas": {
                "total": f"Across {unique_jobs_count} position{'s' if unique_jobs_count != 1 else ''}",
                "interview": f"{interview_pct}% of pipeline",
                "offers": f"{accepted_count} accepted so far",
                "onboarding": f"{onboarding_this_month} active this month",
            },
        },
        "chips": chip_counts,
    }


@router.get("/applicants/{job_applicant_id}")
def get_applicant_detail_route(
    job_applicant_id: int,
    db: Session = Depends(get_db),
    admin_id: int = Depends(_get_admin_id_from_token),
):
    """Retrieves full candidate profile details by job applicant ID."""
    from app.models import Admins
    from sqlalchemy.orm import joinedload

    admin = (
        db.query(Admins)
        .options(joinedload(Admins.user_roles))
        .filter(Admins.admin_id == admin_id)
        .first()
    )
    is_hr = admin is not None and admin.user_roles.role_name in {
        "hr_head",
        "hr_team",
        "hr_admin",
    }

    query = (
        db.query(JobApplicant)
        .join(JobPost, JobApplicant.job_id == JobPost.job_id)
        .filter(JobApplicant.job_applicant_id == job_applicant_id)
    )
    if is_hr:
        pass
    elif admin is not None and admin.user_roles.role_name == "school_admin":
        from app.crud.school_admin_crud import _get_admin_job_filter

        job_filter = _get_admin_job_filter(db, admin_id)
        query = query.filter(job_filter)
    else:
        query = query.filter(JobPost.job_posted_by == admin_id)
    app = query.first()
    if not app:
        raise HTTPException(status_code=404, detail="Job applicant not found.")

    user = app.users
    job_post = db.query(JobPost).filter(JobPost.job_id == app.job_id).first()
    job_title = job_post.job_title if job_post else "Unknown Job"

    # Calculate experience
    from datetime import datetime, date

    exp_records = (
        db.query(CandidateExperience)
        .filter(CandidateExperience.user_id == user.user_id)
        .all()
    )
    total_days = 0
    for exp_rec in exp_records:
        start_dt = exp_rec.start_date
        if isinstance(start_dt, str):
            if start_dt.strip().lower() == "unknown":
                start_dt = None
            else:
                try:
                    start_dt = datetime.strptime(start_dt.split()[0], "%Y-%m-%d").date()
                except ValueError:
                    start_dt = None

        end_dt = exp_rec.end_date
        if not end_dt or (isinstance(end_dt, str) and end_dt.strip().lower() == "unknown"):
            end_dt = date.today()
        elif isinstance(end_dt, str):
            try:
                end_dt = datetime.strptime(end_dt.split()[0], "%Y-%m-%d").date()
            except ValueError:
                end_dt = date.today()

        if start_dt and end_dt:
            total_days += (end_dt - start_dt).days

    if total_days > 0:
        exp_years = round(total_days / 365.25, 1)
        exp_str = f"{exp_years} yrs"
    else:
        exp_str = "—"

    # Get latest stage info
    interviews = (
        db.query(JobInterviewSchedule)
        .filter(JobInterviewSchedule.job_applicant_id == app.job_applicant_id)
        .order_by(JobInterviewSchedule.job_interview_id.desc())
        .all()
    )

    stage_val = "Applied"
    interview_status = "Pending"
    if app.applicant_job_status == "rejected":
        stage_val = "Rejected"
        interview_status = "Rejected"
    elif app.sync_masset == 1:
        stage_val = "Onboarding"
        interview_status = "Synced to MASSET"
    elif app.offer_acceptance_status == "accepted":
        stage_val = "Offer Accepted"
        interview_status = "Offer Accepted"
    elif app.offer_acceptance_status == "expired":
        stage_val = "Offer"
        interview_status = "Offer Expired"
    elif app.issue_offer == 1 or app.offer_letter_doc:
        stage_val = "Offer"
        interview_status = "Offer Sent"
    elif len(interviews) > 0:
        stage_val = "Interview"
        latest_int = interviews[0]
        remark = (
            db.query(InterviewRemark)
            .filter(InterviewRemark.job_interview_id == latest_int.job_interview_id)
            .first()
        )
        if remark and remark.applicant_status:
            if remark.applicant_status == "next_round":
                interview_status = "Next Round"
            else:
                interview_status = (
                    remark.applicant_status.value.capitalize()
                    if hasattr(remark.applicant_status, "value")
                    else remark.applicant_status.capitalize()
                )
        elif latest_int.status == "completed":
            interview_status = "Completed"
        else:
            interview_status = (
                latest_int.status.value.capitalize()
                if hasattr(latest_int.status, "value")
                else str(latest_int.status).capitalize()
            )
    elif app.applicant_job_status == "hold":
        stage_val = "Screened"
        interview_status = "On Hold"
    elif app.applicant_job_status == "selected":
        stage_val = "Screened"
        interview_status = "Selected"

    # Serialize metadata
    meta = (
        db.query(CandidateMetadata)
        .filter(CandidateMetadata.user_id == user.user_id)
        .first()
    )
    metadata_dict = {
        "date_of_birth": (
            meta.date_of_birth.strftime("%Y-%m-%d")
            if (meta and meta.date_of_birth)
            else ""
        ),
        "personal_address": (
            meta.personal_address if (meta and meta.personal_address) else ""
        ),
        "city": meta.city if (meta and meta.city) else "",
        "state": meta.state if (meta and meta.state) else "",
        "country": meta.country if (meta and meta.country) else "",
        "pincode": meta.pincode if (meta and meta.pincode) else "",
        "skills": (
            (
                (
                    lambda s: (
                        __import__("json").loads(s)
                        if s.startswith("[")
                        else [x.strip() for x in s.split(",") if x.strip()]
                    )
                )(meta.skills)
            )
            if (meta and meta.skills)
            else []
        ),
        "profile_status": meta.profile_status if (meta and meta.profile_status) else "",
        "resume_doc": app.resume_doc
        or (getattr(meta, "resume_doc", None) if meta else None)
        or "",
        "cover_letter": app.cover_letter or "",
        "about": meta.about if (meta and meta.about) else "",
        "bio": "Dynamic educator committed to student growth.",
    }

    # Serialize education
    edu_records = (
        db.query(CandidateEducationDetail)
        .filter(CandidateEducationDetail.user_id == user.user_id)
        .all()
    )
    education_list = []
    for edu in edu_records:
        education_list.append(
            {
                "level": edu.education_level,
                "degree": edu.degree_name or "",
                "specialization": edu.specialization or "",
                "institution": edu.institution_name or "",
                "university": edu.university_name or "",
                "start_year": edu.start_year,
                "end_year": edu.end_year,
                "percentage": float(edu.percentage) if edu.percentage else None,
                "cgpa": float(edu.cgpa) if edu.cgpa else None,
            }
        )

    # Serialize experience
    experience_list = []
    for exp_rec in exp_records:
        start_date_str = ""
        if exp_rec.start_date:
            start_date_str = (
                exp_rec.start_date
                if isinstance(exp_rec.start_date, str)
                else exp_rec.start_date.strftime("%Y-%m-%d")
            )

        end_date_str = "Present"
        if exp_rec.end_date:
            end_date_str = (
                exp_rec.end_date
                if isinstance(exp_rec.end_date, str)
                else exp_rec.end_date.strftime("%Y-%m-%d")
            )

        experience_list.append(
            {
                "company": exp_rec.company_name,
                "title": exp_rec.designation,
                "type": exp_rec.employment_type or "Full-time",
                "start_date": start_date_str,
                "end_date": end_date_str,
                "location": exp_rec.location or "",
                "description": exp_rec.description or "",
                "notice_period": exp_rec.notice_period or "",
            }
        )

    # Serialize screening answers
    screening_answers = (
        db.query(CandidateScreeningAnswer)
        .filter(
            CandidateScreeningAnswer.candidate_id == user.user_id,
            CandidateScreeningAnswer.job_id == app.job_id,
        )
        .all()
    )

    # Deduplicate by question_id, keeping the latest one
    unique_answers = {}
    for ans in screening_answers:
        unique_answers[ans.question_id] = ans

    answers_list = []
    for q_id, ans in unique_answers.items():
        q = (
            db.query(JobPreScreeningQuestion)
            .filter(JobPreScreeningQuestion.question_id == q_id)
            .first()
        )
        answers_list.append(
            {
                "question": q.question_text if q else "Pre-Screening Question",
                "answer": ans.answer,
                "expected_answer": q.expected_answer if q else "",
            }
        )

    # Serialize interview history
    interviews_history = []
    for item in interviews:
        sch_at = None
        end_at = None
        if item.scheduled_date and item.start_time:
            sch_at = datetime.combine(item.scheduled_date, item.start_time)
        if item.scheduled_date and item.end_time:
            end_at = datetime.combine(item.scheduled_date, item.end_time)

        resch_at = None
        if item.rescheduled_date and item.rescheduled_start_time:
            resch_at = datetime.combine(
                item.rescheduled_date, item.rescheduled_start_time
            )

        remark = (
            db.query(InterviewRemark)
            .filter(InterviewRemark.job_interview_id == item.job_interview_id)
            .first()
        )
        interviews_history.append(
            {
                "job_interview_id": item.job_interview_id,
                "round": item.interview_round,
                "mode": item.interview_mode,
                "scheduled_at": sch_at,
                "end_time_at": end_at,
                "rescheduled_at": resch_at,
                "meeting_link": item.meeting_link or "",
                "location": item.location or "",
                "interviewer": item.interviewer_name or "",
                "status": item.status,
                "reschedule_reason": item.reschedule_reason or "",
                "cancelled_reason": item.cancelled_reason or "",
                "remarks": (
                    {
                        "remarks": remark.remarks or "",
                        "applicant_status": remark.applicant_status or "",
                        "round": remark.round or "",
                    }
                    if remark
                    else None
                ),
            }
        )

    return {
        "id": app.job_applicant_id,
        "name": f"{user.first_name} {user.last_name}".strip(),
        "email": user.email,
        "mobile": user.mobile,
        "job": job_title,
        "job_id": app.job_id,
        "user_id": user.user_id,
        "appliedDate": app.created_at.strftime("%Y-%m-%d") if app.created_at else "",
        "exp": exp_str,
        "stage": stage_val,
        "interviewStatus": interview_status,
        "sync_masset": app.sync_masset,
        "offer_letter_doc": app.offer_letter_doc or "",
        "offer_acceptance_status": app.offer_acceptance_status or "",
        "metadata": metadata_dict,
        "education": education_list,
        "experience": experience_list,
        "screening": answers_list,
        "interviews": interviews_history,
    }


@router.patch("/applicants/{job_applicant_id}/status")
def update_applicant_status_route(
    job_applicant_id: int,
    form_data: ApplicantStatusUpdateRequest,
    db: Session = Depends(get_db),
    admin_id: int = Depends(_get_admin_id_from_token),
):
    from app.models import Admins
    from sqlalchemy.orm import joinedload

    admin = (
        db.query(Admins)
        .options(joinedload(Admins.user_roles))
        .filter(Admins.admin_id == admin_id)
        .first()
    )
    is_hr = admin is not None and admin.user_roles.role_name in {
        "hr_head",
        "hr_team",
        "hr_admin",
    }

    query = (
        db.query(JobApplicant)
        .join(JobPost, JobApplicant.job_id == JobPost.job_id)
        .filter(JobApplicant.job_applicant_id == job_applicant_id)
    )
    if not is_hr:
        query = query.filter(JobPost.job_posted_by == admin_id)
    app = query.first()
    if not app:
        raise HTTPException(status_code=404, detail="Job applicant not found.")

    status_lower = form_data.status.lower()
    if status_lower == "selected":
        app.applicant_job_status = ApplicantJobStatus.SELECTED
    elif status_lower == "rejected":
        app.applicant_job_status = ApplicantJobStatus.REJECTED
    elif status_lower == "hold":
        app.applicant_job_status = ApplicantJobStatus.HOLD
    else:
        raise HTTPException(
            status_code=400, detail=f"Invalid status value: {form_data.status}"
        )

    db.commit()
    db.refresh(app)

    # Send Notifications
    try:
        from app.models import Users
        from app.crud.notification_crud import (
            notify_candidate
        )

        job = db.query(JobPost).filter(JobPost.job_id == app.job_id).first()
        candidate = db.query(Users).filter(Users.user_id == app.user_id).first()

        if job and candidate:
            candidate_name = f"{candidate.first_name} {candidate.last_name}".strip()

            # 1. Notify Candidate
            notify_candidate(
                db=db,
                candidate_id=candidate.user_id,
                title="Application Status Update",
                message=f"Your application status for '{job.job_title}' has been updated to {status_lower}.",
                notification_type="status_update",
                sender_user_id=admin_id,
                sender_type="hr" if is_hr else "schoolAdmin",
            )

    except Exception as e:
        from app.core.logger import logger

        logger.error(f"Error creating status update notifications: {e}")

    return {"message": f"Candidate status updated to {status_lower} successfully."}


@router.get("/{job_id}")
def get_job_post_by_id_route(
    job_id: int,
    db: Session = Depends(get_db),
    admin_id: int = Depends(_get_admin_id_from_token),
):
    """Retrieves a single job post by its ID."""
    job_post = get_job_post_or_404(db, job_id=job_id)
    from app.models import Admins
    from sqlalchemy.orm import joinedload

    admin = (
        db.query(Admins)
        .options(joinedload(Admins.user_roles))
        .filter(Admins.admin_id == admin_id)
        .first()
    )
    is_hr = admin is not None and admin.user_roles.role_name in {
        "hr_head",
        "hr_team",
        "hr_admin",
    }

    if job_post.job_posted_by != admin_id and not is_hr:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this job post.",
        )
    job_details = _serialize_job_post(job_post, db=db)

    # Calculate stats for this job
    applications_count = (
        db.query(JobApplicant).filter(JobApplicant.job_id == job_id).count()
    )

    shortlisted_count = (
        db.query(JobApplicant)
        .filter(
            JobApplicant.job_id == job_id,
            (JobApplicant.applicant_job_status.in_(["selected", "hold"]))
            | (
                db.query(JobInterviewSchedule)
                .filter(
                    JobInterviewSchedule.job_applicant_id
                    == JobApplicant.job_applicant_id
                )
                .exists()
            ),
        )
        .count()
    )

    interview_count = (
        db.query(JobInterviewSchedule)
        .filter(
            JobInterviewSchedule.job_id == job_id,
            JobInterviewSchedule.status == "scheduled",
        )
        .count()
    )

    offers_count = (
        db.query(JobApplicant)
        .filter(
            JobApplicant.job_id == job_id,
            (JobApplicant.issue_offer == 1)
            | (JobApplicant.offer_letter_doc.isnot(None)),
        )
        .count()
    )

    job_details["stats"] = {
        "applications": applications_count,
        "shortlisted": shortlisted_count,
        "interviews": interview_count,
        "offers": offers_count,
    }

    return job_details


@router.post("/")
def create_job_post_route(
    form_data: JobPostCreateRequest,
    db: Session = Depends(get_db),
    admin_id: int = Depends(_get_admin_id_from_token),
):
    """Creates a new job post along with optional pre-screening questions."""
    job_post = create_job_post(
        db=db,
        job_posted_by=admin_id,
        job_title=form_data.job_title,
        department=form_data.department,
        job_type=form_data.job_type,
        vacancy_count=form_data.vacancy_count,
        school_name=form_data.school_name,
        location=form_data.location,
        programme=form_data.programme,
        min_exp=form_data.min_exp,
        max_exp=form_data.max_exp,
        closing_date=form_data.closing_date,
        job_description=form_data.job_description,
        skills_required=form_data.skills_required,
        education_qualification=form_data.education_qualification,
        additional_requirements=form_data.additional_requirements,
        job_status=form_data.job_status,
        pre_screening_questions=(
            [question.model_dump() for question in form_data.pre_screening_questions]
            if form_data.pre_screening_questions
            else None
        ),
    )
    return _serialize_job_post(job_post)


@router.put("/{job_id}")
def update_job_post_route(
    job_id: int, form_data: JobPostUpdateRequest, db: Session = Depends(get_db)
):
    """Edits/updates an existing job post's fields and pre-screening questions."""
    job_post = update_job_post(
        db=db,
        job_id=job_id,
        job_title=form_data.job_title,
        department=form_data.department,
        job_type=form_data.job_type,
        vacancy_count=form_data.vacancy_count,
        school_name=form_data.school_name,
        location=form_data.location,
        programme=form_data.programme,
        min_exp=form_data.min_exp,
        max_exp=form_data.max_exp,
        closing_date=form_data.closing_date,
        job_description=form_data.job_description,
        skills_required=form_data.skills_required,
        education_qualification=form_data.education_qualification,
        additional_requirements=form_data.additional_requirements,
        job_status=form_data.job_status,
        pre_screening_questions=(
            [question.model_dump() for question in form_data.pre_screening_questions]
            if form_data.pre_screening_questions is not None
            else None
        ),
    )
    return _serialize_job_post(job_post, db=db)


@router.patch("/{job_id}/close")
def close_job_post_route(
    job_id: int,
    db: Session = Depends(get_db),
    admin_id: int = Depends(_get_admin_id_from_token),
):
    """Marks a job post as closed."""
    job_post = get_job_post_or_404(db, job_id=job_id)
    from app.models import Admins
    from sqlalchemy.orm import joinedload

    admin = (
        db.query(Admins)
        .options(joinedload(Admins.user_roles))
        .filter(Admins.admin_id == admin_id)
        .first()
    )
    is_hr = admin is not None and admin.user_roles.role_name in {
        "hr_head",
        "hr_team",
        "hr_admin",
    }

    if job_post.job_posted_by != admin_id and not is_hr:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to close this job post.",
        )
    job_post = update_job_status(db=db, job_id=job_id, job_status=JobStatus.CLOSED)
    return _serialize_job_post(job_post, db=db)


@router.post("/{job_id}/clone")
def clone_job_post_route(
    job_id: int,
    publish: bool = False,
    db: Session = Depends(get_db),
    admin_id: int = Depends(_get_admin_id_from_token),
):
    """Clones an existing job post."""
    original_job = get_job_post_or_404(db, job_id=job_id)
    from app.models import Admins
    from sqlalchemy.orm import joinedload

    admin = (
        db.query(Admins)
        .options(joinedload(Admins.user_roles))
        .filter(Admins.admin_id == admin_id)
        .first()
    )
    is_hr = admin is not None and admin.user_roles.role_name in {
        "hr_head",
        "hr_team",
        "hr_admin",
    }

    if original_job.job_posted_by != admin_id and not is_hr:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to clone this job post.",
        )
    cloned_job = clone_job_post(
        db=db, job_id=job_id, admin_id=admin_id, publish=publish
    )
    return _serialize_job_post(cloned_job, db=db)


@router.patch("/{job_id}/draft")
def draft_job_post_route(job_id: int, db: Session = Depends(get_db)):
    """Marks a job post as a draft."""
    job_post = update_job_status(db=db, job_id=job_id, job_status=JobStatus.DRAFT)
    return _serialize_job_post(job_post, db=db)


@router.get("/public/{job_id}/questions")
def get_job_prescreening_questions_route(job_id: int, db: Session = Depends(get_db)):
    """Retrieves pre-screening questions for a specific published job post."""
    # Ensure the job exists and is published
    get_published_job_post_or_404(db, job_id=job_id)
    questions = get_job_prescreening_questions(db, job_id=job_id)
    return [
        {
            "question_id": q.question_id,
            "job_id": q.job_id,
            "question_text": q.question_text,
            "question_type": q.question_type,
            "options": q.options,
            "expected_answer": q.expected_answer,
        }
        for q in questions
    ]


@router.get("/dashboard/stats")
def get_dashboard_stats(
    db: Session = Depends(get_db), admin_id: int = Depends(_get_admin_id_from_token)
):
    """Retrieves high-level statistics for the admin dashboard."""
    from app.models import Admins
    from sqlalchemy.orm import joinedload

    admin = (
        db.query(Admins)
        .options(joinedload(Admins.user_roles))
        .filter(Admins.admin_id == admin_id)
        .first()
    )
    is_hr = admin is not None and admin.user_roles.role_name in {
        "hr_head",
        "hr_team",
        "hr_admin",
    }

    base_q = db.query(JobApplicant).join(JobPost, JobApplicant.job_id == JobPost.job_id)
    if not is_hr:
        base_q = base_q.filter(JobPost.job_posted_by == admin_id)

    # Active jobs count
    active_jobs_q = db.query(JobPost).filter(JobPost.job_status == JobStatus.PUBLISH)
    if not is_hr:
        active_jobs_q = active_jobs_q.filter(JobPost.job_posted_by == admin_id)
    active_jobs = active_jobs_q.count()

    # Total applicants
    total_applicants = base_q.count()

    # Scheduled interviews (use enum value)
    scheduled_interviews_q = (
        db.query(JobInterviewSchedule)
        .join(JobPost, JobInterviewSchedule.job_id == JobPost.job_id)
        .filter(
            JobInterviewSchedule.status.in_(
                [InterviewStatus.SCHEDULED, InterviewStatus.RESCHEDULED]
            )
        )
    )
    if not is_hr:
        scheduled_interviews_q = scheduled_interviews_q.filter(
            JobPost.job_posted_by == admin_id
        )
    scheduled_interviews = scheduled_interviews_q.count()

    # MASSET sync pending: accepted but not yet synced (NULL or 0)
    masset_sync_pending = base_q.filter(
        JobApplicant.offer_acceptance_status == OfferAcceptanceStatus.ACCEPTED,
        or_(JobApplicant.sync_masset.is_(None), JobApplicant.sync_masset == 0),
    ).count()

    # Onboarded candidates: sync_masset == 1
    onboarded_candidates = base_q.filter(
        JobApplicant.issue_appointment_order == 1
    ).count()

    # Pre-compute the set of applicant_ids that have interviews (for funnel)
    interviewed_subq_q = db.query(JobInterviewSchedule.job_applicant_id).join(
        JobPost, JobInterviewSchedule.job_id == JobPost.job_id
    )
    if not is_hr:
        interviewed_subq_q = interviewed_subq_q.filter(
            JobPost.job_posted_by == admin_id
        )
    interviewed_subq = interviewed_subq_q.distinct().subquery()

    prescreen_reject_count = base_q.filter(
        JobApplicant.applicant_stage == ApplicantStage.PRESCREEN_REJECT
    ).count()
    interview_count = base_q.filter(
        JobApplicant.job_applicant_id.in_(interviewed_subq)
    ).count()
    screened_count = base_q.filter(
        or_(
            JobApplicant.applicant_job_status.in_(
                [ApplicantJobStatus.SELECTED, ApplicantJobStatus.HOLD]
            ),
            JobApplicant.job_applicant_id.in_(interviewed_subq),
            JobApplicant.applicant_stage == ApplicantStage.SCREENED
        )
    ).count()
    offer_count = base_q.filter(JobApplicant.issue_offer == 1).count()
    offer_accepted_count = base_q.filter(
        JobApplicant.offer_acceptance_status == OfferAcceptanceStatus.ACCEPTED
    ).count()
    onboarding_count = onboarded_candidates
    rejected_count = base_q.filter(
        JobApplicant.applicant_job_status == ApplicantJobStatus.REJECTED
    ).count()

    return {
        "active_jobs": active_jobs,
        "total_applicants": total_applicants,
        "scheduled_interviews": scheduled_interviews,
        "masset_sync_pending": masset_sync_pending,
        "onboarded_candidates": onboarded_candidates,
        "funnel": [
            {"stage": "Prescreen Reject", "count": prescreen_reject_count, "color": "#E24B4A"},
            {"stage": "Screened", "count": screened_count, "color": "#534AB7"},
            {"stage": "Interview", "count": interview_count, "color": "#EF9F27"},
            {"stage": "Offer", "count": offer_count, "color": "#D85A30"},
            {
                "stage": "Offer Accepted",
                "count": offer_accepted_count,
                "color": "#1D9E75",
            },
            {"stage": "Onboarding", "count": onboarding_count, "color": "#0891b2"},
            {"stage": "Rejected", "count": rejected_count, "color": "#A32D2D"},
        ],
    }


@router.get("/dashboard/recent-applicants")
def get_dashboard_recent_applicants(
    db: Session = Depends(get_db), admin_id: int = Depends(_get_admin_id_from_token)
):
    """Retrieves recent applicants details for the admin dashboard."""
    from app.models import Admins
    from sqlalchemy.orm import joinedload

    admin = (
        db.query(Admins)
        .options(joinedload(Admins.user_roles))
        .filter(Admins.admin_id == admin_id)
        .first()
    )
    is_hr = admin is not None and admin.user_roles.role_name in {
        "hr_head",
        "hr_team",
        "hr_admin",
    }

    query = (
        db.query(JobApplicant, Users, JobPost)
        .join(Users, JobApplicant.user_id == Users.user_id)
        .join(JobPost, JobApplicant.job_id == JobPost.job_id)
    )
    if not is_hr:
        query = query.filter(JobPost.job_posted_by == admin_id)

    rows = query.order_by(JobApplicant.job_applicant_id.desc()).limit(10).all()

    # Batch-load interview ids so we avoid N+1
    app_ids = [app.job_applicant_id for app, _, _ in rows]
    interviewed: set[int] = set()
    latest_iv: dict[int, JobInterviewSchedule] = {}
    if app_ids:
        iv_rows = (
            db.query(JobInterviewSchedule)
            .filter(JobInterviewSchedule.job_applicant_id.in_(app_ids))
            .order_by(JobInterviewSchedule.job_interview_id.desc())
            .all()
        )
        for iv in iv_rows:
            interviewed.add(iv.job_applicant_id)
            if iv.job_applicant_id not in latest_iv:
                latest_iv[iv.job_applicant_id] = iv

    colors = [
        "#378ADD",
        "#534AB7",
        "#1D9E75",
        "#EF9F27",
        "#D85A30",
        "#0891b2",
        "#993C1D",
        "#0F6E56",
    ]

    result = []
    for idx, (app, user, job_post) in enumerate(rows):
        name = f"{user.first_name or ''} {user.last_name or ''}".strip() or user.email
        initials = (
            (user.first_name[0] if user.first_name else "")
            + (user.last_name[0] if user.last_name else "")
        ).upper() or "?"
        color = colors[idx % len(colors)]

        # --- MOVED AND FIXED: Calculate experience per specific applicant ---
        exp_records = (
            db.query(CandidateExperience)
            .filter(CandidateExperience.user_id == user.user_id)
            .all()
        )
        total_experience = 0.0
        for exp_rec in exp_records:
            if exp_rec.total_experience:
                try:
                    num_part = str(exp_rec.total_experience).strip().split()[0]
                    total_experience += float(num_part)
                except (ValueError, IndexError):
                    continue

        if total_experience > 0:
            exp_str = f"{round(total_experience, 1)} yrs"
        else:
            exp_str = "—"
        # ---------------------------------------------------------------------

        # Stage + interview status
        has_interview = app.job_applicant_id in interviewed
        if app.sync_masset == 1:
            stage = "Onboarding"
            interview_status = "Synced to MASSET"
        elif app.offer_acceptance_status == OfferAcceptanceStatus.ACCEPTED:
            stage = "Offer Accepted"
            interview_status = "Offer Accepted"
        elif app.offer_acceptance_status in (
            OfferAcceptanceStatus.EXPIRED,
            OfferAcceptanceStatus.REJECTED,
        ):
            stage = "Offer"
            interview_status = "Offer " + (
                app.offer_acceptance_status.value.capitalize()
            )
        elif app.issue_offer == 1:
            stage = "Offer"
            interview_status = "Offer Sent"
        elif has_interview:
            stage = "Interview"
            iv = latest_iv[app.job_applicant_id]
            remark = (
                db.query(InterviewRemark)
                .filter(InterviewRemark.job_interview_id == iv.job_interview_id)
                .first()
            )
            if remark and remark.applicant_status:
                if remark.applicant_status == "next_round":
                    interview_status = "Next Round"
                else:
                    interview_status = remark.applicant_status.capitalize()
            else:
                date_str = (
                    iv.scheduled_date.strftime("%b %d, %Y") if iv.scheduled_date else ""
                )
                time_str = str(iv.start_time)[:5] if iv.start_time else ""
                interview_status = (
                    f"{iv.interview_round or 'Round 1'} · {time_str}".strip(" ·")
                )
        elif app.applicant_job_status in (
            ApplicantJobStatus.SELECTED,
            ApplicantJobStatus.HOLD,
        ):
            stage = "Screened"
            interview_status = app.applicant_job_status.value.capitalize()
        elif app.applicant_job_status == ApplicantJobStatus.REJECTED:
            stage = "Rejected"
            interview_status = "Rejected"
        else:
            stage = "Applied"
            interview_status = "Pending"

        result.append(
            {
                "name": name,
                "initials": initials,
                "color": color,
                "job": job_post.job_title or "",
                "exp": exp_str,  # Now correctly references the current iteration's experience string
                "stage": stage,
                "interviewStatus": interview_status,
                "job_applicant_id": app.job_applicant_id,
            }
        )

    return result


@router.get("/public-jobs-page")
def public_jobs_page():
    return serve_html_with_base(
        "mss-career-portal/pages/candidate/jobs.html",
        "/mss-career-portal/pages/candidate/",
    )


@router.get("/job-detail-page")
def job_detail_page():
    return serve_html_with_base(
        "mss-career-portal/pages/candidate/job-detail.html",
        "/mss-career-portal/pages/candidate/",
    )


@router.get("/job-grid-page")
def job_grid_page():
    return serve_html_with_base(
        "mss-career-portal/pages/candidate/job-grid.html",
        "/mss-career-portal/pages/candidate/",
    )


@router.get("/admin-jobs-page")
def admin_jobs_page():
    return serve_html_with_base(
        "mss-career-portal/pages/hr/hr-jobpost-list.html",
        "/mss-career-portal/pages/hr/",
    )


@router.get("/job-create-page")
def job_create_page():
    return serve_html_with_base(
        "mss-career-portal/pages/hr/hr-jobpost-create.html",
        "/mss-career-portal/pages/hr/",
    )