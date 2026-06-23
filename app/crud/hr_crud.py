from typing import Optional
from datetime import date, datetime
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
import requests
from app.core.logger import logger

from app.models.job_applicant_model import JobApplicant, ApplicantJobStatus, OfferAcceptanceStatus, ApplicantStage
from app.models.job_post_model import JobPost
from app.models.interview_schedule_model import JobInterviewSchedule, InterviewStatus
from app.models.user_model import Users
from app.models.candidate_metadata_model import CandidateMetadata
from app.models.candidate_experience_model import CandidateExperience
from app.models.admin_model import Admins
from app.models.unit_model import Units
from app.crud.common import (
    get_initials, get_color, parse_skills, compute_exp_str, compute_stage, compute_offer_status
)

def _is_hr_role(db: Session, admin_id: int) -> bool:
    from sqlalchemy.orm import joinedload
    admin = db.query(Admins).options(joinedload(Admins.user_roles)).filter(Admins.admin_id == admin_id).first()
    return admin is not None and admin.user_roles.role_name in {"hr_head", "hr_team", "hr_admin"}

def _days_ago(dt) -> int:
    if not dt:
        return 0
    try:
        return (date.today() - dt.date()).days
    except Exception:
        return 0


def _format_time(t) -> str:
    if not t:
        return ""
    try:
        return datetime.strptime(str(t), "%H:%M:%S").strftime("%I:%M %p").lstrip("0")
    except Exception:
        return str(t)


def _format_date(d) -> str:
    if not d:
        return ""
    try:
        return d.strftime("%d-%b-%Y")
    except Exception:
        return str(d)

def build_dynamic_timeline(app, stage: str) -> list:
    applied_days = f"{_days_ago(app.created_at)} days ago" if app.created_at else "Recently"
    
    stages = ['Applied', 'Screened', 'Interview', 'Offer', 'Offer Accepted', 'Onboarding']
    try:
        current_idx = stages.index(stage)
    except ValueError:
        current_idx = 0
        
    tl = []
    # 1. Applied
    if current_idx >= 0:
        s_status = 'done' if current_idx > 0 else 'current'
        tl.append({'t': 'Application Received', 'd': applied_days, 's': s_status})
    
    # 2. Screened
    if current_idx >= 1:
        s_status = 'done' if current_idx > 1 else 'current'
        tl.append({'t': 'Resume Screened', 'd': 'System Evaluated', 's': s_status})
    elif current_idx == 0:
        tl.append({'t': 'Resume Screening', 'd': 'Pending', 's': 'pending'})
        
    # 3. Interview
    if current_idx >= 2:
        s_status = 'done' if current_idx > 2 else 'current'
        tl.append({'t': 'Interview Process', 'd': 'In Progress' if s_status == 'current' else 'Cleared', 's': s_status})
    elif current_idx == 1:
        tl.append({'t': 'Interview', 'd': 'Pending', 's': 'pending'})

    # 4. Offer
    if current_idx >= 3:
        s_status = 'done' if current_idx > 3 else 'current'
        tl.append({'t': 'Offer Extended', 'd': 'Sent to Candidate', 's': s_status})
    elif current_idx == 2:
        tl.append({'t': 'Offer Generation', 'd': 'Awaiting Decision', 's': 'pending'})
        
    # 5. Offer Accepted
    if current_idx >= 4:
        s_status = 'done' if current_idx > 4 else 'current'
        tl.append({'t': 'Offer Accepted', 'd': 'Candidate Agreed', 's': s_status})
    elif current_idx == 3:
        tl.append({'t': 'Offer Acceptance', 'd': 'Awaiting Reply', 's': 'pending'})
        
    # 6. Onboarding
    if current_idx >= 5:
        tl.append({'t': 'Onboarding Initiated', 'd': 'In Progress', 's': 'current'})
    elif current_idx == 4:
        tl.append({'t': 'Onboarding', 'd': 'Upcoming', 's': 'pending'})

    return tl

def get_ats_candidates(db: Session, admin_id: int) -> list:
    query = (
        db.query(JobApplicant, Users, CandidateMetadata, JobPost)
        .join(Users, JobApplicant.user_id == Users.user_id)
        .outerjoin(CandidateMetadata, Users.user_id == CandidateMetadata.user_id)
        .join(JobPost, JobApplicant.job_id == JobPost.job_id)
    )
    if not _is_hr_role(db, admin_id):
        query = query.filter(JobPost.job_posted_by == admin_id)
    rows = (
        query.filter(or_(JobApplicant.applicant_job_status != ApplicantJobStatus.REJECTED, JobApplicant.applicant_job_status.is_(None)))
        .order_by(JobApplicant.created_at.desc())
        .all()
    )

    # Collect all user_ids to batch-load experiences
    user_ids = [u.user_id for _, u, _, _ in rows]
    exps_map: dict[int, list] = {}
    if user_ids:
        exps = db.query(CandidateExperience).filter(CandidateExperience.user_id.in_(user_ids)).all()
        for e in exps:
            exps_map.setdefault(e.user_id, []).append(e)

    # Batch-check which applicants have at least one interview
    applicant_ids = [app.job_applicant_id for app, _, _, _ in rows]
    interviewed_ids: set[int] = set()
    if applicant_ids:
        result = (
            db.query(JobInterviewSchedule.job_applicant_id)
            .filter(JobInterviewSchedule.job_applicant_id.in_(applicant_ids))
            .distinct()
            .all()
        )
        interviewed_ids = {r[0] for r in result}

    out = []
    for idx, (app, user, meta, job) in enumerate(rows):
        name = f"{user.first_name} {user.last_name}".strip()
        has_interview = app.job_applicant_id in interviewed_ids
        
        stage_val = app.applicant_stage.value if hasattr(app.applicant_stage, 'value') else str(app.applicant_stage) if app.applicant_stage else "applied"
        from app.crud.common import _STAGE_ENUM_TO_LABEL
        stage = _STAGE_ENUM_TO_LABEL.get(stage_val, "Applied")
        exp_str = compute_exp_str(
            exps_map.get(user.user_id, [])
        )
        skills = parse_skills(meta.skills if meta else None)
        notes = (meta.about or "") if meta else ""
        color = get_color(idx)
        out.append({
            "id": app.job_applicant_id,
            "job_id": app.job_id,
            "name": name,
            "initials": get_initials(user.first_name, user.last_name),
            "position": job.job_title or "",
            "school": job.school_name or "",
            "stage": stage,
            "exp": exp_str,
            "email": user.email,
            "phone": user.mobile or "",
            "daysAgo": _days_ago(app.created_at),
            "notes": notes,
            "skills": skills,
            "color": color,
            "timeline": build_dynamic_timeline(app, stage),
        })
    return out


_STAGE_TO_FIELDS = {
    'Applied': {
        'applicant_stage': ApplicantStage.APPLIED,
        'applicant_job_status': None,
        'issue_offer': 0,
        'offer_acceptance_status': OfferAcceptanceStatus.PENDING,
        'sync_masset': 0,
    },
    'Screened': {
        'applicant_stage': ApplicantStage.SCREENED,
        'applicant_job_status': None,
        'issue_offer': 0,
        'offer_acceptance_status': OfferAcceptanceStatus.PENDING,
        'sync_masset': 0,
    },
    'Interview': {
        'applicant_stage': ApplicantStage.INTERVIEW,
        'applicant_job_status': ApplicantJobStatus.NEXT_ROUND,
        'issue_offer': 0,
        'offer_acceptance_status': OfferAcceptanceStatus.PENDING,
        'sync_masset': 0,
    },
    'Offer': {
        'applicant_stage': ApplicantStage.OFFER,
        'applicant_job_status': ApplicantJobStatus.SELECTED,
        'issue_offer': 1,
        'offer_acceptance_status': OfferAcceptanceStatus.PENDING,
        'sync_masset': 0,
    },
    'Offer Accepted': {
        'applicant_stage': ApplicantStage.OFFER_ACCEPTED,
        'applicant_job_status': ApplicantJobStatus.SELECTED,
        'issue_offer': 1,
        'offer_acceptance_status': OfferAcceptanceStatus.ACCEPTED,
        'sync_masset': 0,
    },
    'Onboarding': {
        'applicant_stage': ApplicantStage.ONBOARDING,
        'applicant_job_status': ApplicantJobStatus.SELECTED,
        'issue_offer': 1,
        'offer_acceptance_status': OfferAcceptanceStatus.ACCEPTED,
        'sync_masset': 1,
    },
}


def update_candidate_stage(db: Session, admin_id: int, applicant_id: int, stage: str):
    from fastapi import HTTPException
    fields = _STAGE_TO_FIELDS.get(stage)
    if fields is None:
        raise HTTPException(status_code=400, detail=f"Invalid stage: {stage}")

    # Verify the applicant exists and the caller has access to the job
    row = (
        db.query(JobApplicant, JobPost)
        .join(JobPost, JobApplicant.job_id == JobPost.job_id)
        .filter(JobApplicant.job_applicant_id == applicant_id)
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Applicant not found")

    app_record, job = row
    if not _is_hr_role(db, admin_id) and job.job_posted_by != admin_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Check if candidate is moving from Offer/Offer Accepted to Interview
    if (app_record.applicant_stage in (ApplicantStage.OFFER, ApplicantStage.OFFER_ACCEPTED)) and stage == "Interview":
        # Find the latest interview schedule for this applicant
        latest_interview = (
            db.query(JobInterviewSchedule)
            .filter(JobInterviewSchedule.job_applicant_id == applicant_id)
            .order_by(JobInterviewSchedule.job_interview_id.desc())
            .first()
        )
        if latest_interview:
            # Find the corresponding remark
            from app.models.interview_remarks_model import InterviewRemark, ApplicantStatus
            remark = (
                db.query(InterviewRemark)
                .filter(InterviewRemark.job_interview_id == latest_interview.job_interview_id)
                .first()
            )
            if remark and remark.applicant_status == ApplicantStatus.SELECTED:
                remark.applicant_status = ApplicantStatus.NEXT_ROUND

    for attr, value in fields.items():
        setattr(app_record, attr, value)

    db.commit()
    
    from app.crud.common import check_and_close_job_if_filled
    check_and_close_job_if_filled(db, job.job_id)

    return {"ok": True, "applicant_id": applicant_id, "stage": stage}


def get_interviews(db: Session, admin_id: int) -> dict:
    query_rows = (
        db.query(JobInterviewSchedule, Users, JobPost)
        .join(JobPost, JobInterviewSchedule.job_id == JobPost.job_id)
        .join(JobApplicant, JobInterviewSchedule.job_applicant_id == JobApplicant.job_applicant_id)
        .join(Users, JobApplicant.user_id == Users.user_id)
    )
    if not _is_hr_role(db, admin_id):
        query_rows = query_rows.filter(JobPost.job_posted_by == admin_id)
    rows = (
        query_rows.order_by(JobInterviewSchedule.scheduled_date.desc(), JobInterviewSchedule.start_time.desc())
        .all()
    )

    interviews = []
    for idx, (iv, user, job) in enumerate(rows):
        name = f"{user.first_name} {user.last_name}".strip()
        is_rescheduled = iv.status.value.lower() == "rescheduled" if iv.status else False
        date_val = iv.rescheduled_date if is_rescheduled and iv.rescheduled_date else iv.scheduled_date
        
        start_val = iv.rescheduled_start_time if is_rescheduled and iv.rescheduled_start_time else iv.start_time
        end_val = iv.rescheduled_end_time if is_rescheduled and iv.rescheduled_end_time else iv.end_time
        
        time_str = _format_time(start_val) if start_val else ""
        if end_val:
            time_str += f" - {_format_time(end_val)}"

        from app.models.interview_remarks_model import InterviewRemark
        status_text = iv.status.value.capitalize() if iv.status else "Scheduled"
        candidate_status = ""
        if iv.status and iv.status.value.lower() == "completed":
            remark = db.query(InterviewRemark).filter(InterviewRemark.job_interview_id == iv.job_interview_id).first()
            if remark and remark.applicant_status:
                candidate_status = remark.applicant_status.value if hasattr(remark.applicant_status, 'value') else remark.applicant_status

        interviews.append({
            "job_interview_id": iv.job_interview_id,
            "candidate_id": user.user_id,
            "candidate": name,
            "initials": get_initials(user.first_name, user.last_name),
            "color": get_color(idx),
            "position": job.job_title or "",
            "round": iv.interview_round or "Round 1",
            "date": _format_date(date_val),
            "time": time_str,
            "interviewer": iv.interviewer_name or "",
            "status": status_text,
            "mode": (iv.interview_mode.value if iv.interview_mode else "online"),
            "candidate_status": candidate_status
        })

    # Also return candidates list for the schedule-interview dropdown
    query_app = (
        db.query(JobApplicant, Users, JobPost)
        .join(Users, JobApplicant.user_id == Users.user_id)
        .join(JobPost, JobApplicant.job_id == JobPost.job_id)
    )
    if not _is_hr_role(db, admin_id):
        query_app = query_app.filter(JobPost.job_posted_by == admin_id)
    app_rows = (
        query_app.filter(JobApplicant.applicant_job_status != ApplicantJobStatus.REJECTED)
        .order_by(Users.first_name)
        .all()
    )
    candidates = []
    for app, user, job in app_rows:
        candidates.append({
            "id": app.job_applicant_id,
            "name": f"{user.first_name} {user.last_name}".strip(),
            "position": job.job_title or "",
            "job_id": app.job_id,
        })

    # Summary stats
    total_today = sum(
        1 for iv in interviews
        if iv["date"] == _format_date(date.today())
    )
    completed = sum(1 for iv in interviews if iv["status"].lower() == "completed")
    pending_feedback = sum(1 for iv in interviews if iv["status"].lower() == "scheduled")

    return {
        "interviews": interviews,
        "candidates": candidates,
        "stats": {
            "today": total_today,
            "completed": completed,
            "pending_feedback": pending_feedback,
        },
    }
    

def get_masset_candidates(db: Session, admin_id: int) -> list:
    query = (
        db.query(JobApplicant, Users, JobPost)
        .join(Users, JobApplicant.user_id == Users.user_id)
        .join(JobPost, JobApplicant.job_id == JobPost.job_id)
    )
    if not _is_hr_role(db, admin_id):
        query = query.filter(JobPost.job_posted_by == admin_id)
    rows = (
        query.filter(JobApplicant.offer_acceptance_status == OfferAcceptanceStatus.ACCEPTED)
        .order_by(JobApplicant.updated_at.desc())
        .all()
    )

    out = []
    for idx, (app, user, job) in enumerate(rows):
        name = f"{user.first_name} {user.last_name}".strip()
        sync_val = app.masset_synced_at
        if sync_val:
            if isinstance(sync_val, str):
                try:
                    sync_val = datetime.strptime(sync_val.split(' ')[0].split('T')[0], "%Y-%m-%d")
                except Exception:
                    pass
            last_sync = _format_date(sync_val.date() if hasattr(sync_val, 'date') else sync_val)
        else:
            last_sync = "Not synced"

        if last_sync == "Not synced":
            status = "Sync Pending"
        elif app.masset_status:
            status = app.masset_status
        else:
            status = "AO Pending"

        out.append({
            "id": app.job_applicant_id,
            "name": name,
            "initials": get_initials(user.first_name, user.last_name),
            "position": job.job_title or "",
            "school": job.school_name or "",
            "offerDate": _format_date(app.offer_issued_date),
            "status": status,
            "lastSync": last_sync,
            "email": user.email,
            "color": get_color(idx),
            "masset_employee_id": app.masset_employee_id or "",
        })
    return out

def sync_masset(db: Session, admin_id: int, applicant_id: int, employee_id: str) -> dict:
    # 1. Fetch the applicant using applicant_id
    app = db.query(JobApplicant).filter(
        JobApplicant.job_applicant_id == applicant_id
    ).first()
    
    if not app:
        return {"error": "Applicant not found"}

    user = db.query(Users).filter(Users.user_id == app.user_id).first()
    user_metadata = db.query(CandidateMetadata).filter(CandidateMetadata.user_id == app.user_id).first()
    job = db.query(JobPost).filter(JobPost.job_id == app.job_id).first()

    # Generate local MASSET employee ID if not already present
    local_employee_id = app.masset_employee_id or f"EMP-{applicant_id:04d}"

    # 2. Construct JSON Payload (tracking via applicant_id and masset_employee_id)
    payload = {
        "candidate_id": applicant_id,
        "masset_employee_id": local_employee_id,
        "first_name": user.first_name if user else "",
        "last_name": user.last_name if user else "",
        "email": user.email if user else "",
        "phone": user.mobile if user else "",
        "date_of_birth": user_metadata.date_of_birth.strftime('%Y-%m-%d') if (user_metadata and user_metadata.date_of_birth and hasattr(user_metadata.date_of_birth, 'strftime')) else (user_metadata.date_of_birth if user_metadata and user_metadata.date_of_birth else ""),
        'gender': user.gender if user else "",
        "marital_status": user_metadata.marital_status if user_metadata else "", 
        "designation": job.job_title if job else "",
        "unit_name": job.school_name if job else "",
        "action": "appointment_order"
    }

    # 3. HTTP POST Request to MASSET local server or Webhook URL
    webhook_url = "http://192.168.0.8/synchrms/api/career_sync.php"
    logger.info(f"Attempting to sync candidate {applicant_id} to {webhook_url}")
    logger.info(f"Payload: {payload}")
    
    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        logger.info(f"Response Status Code: {response.status_code}")
        logger.info(f"Response Text: {response.text}")
        response.raise_for_status()  # Ensures we got a 200 OK / success HTTP status
    except Exception as e:
        logger.error(f"MASSET Sync Failed. Exact issue: {str(e)}", exc_info=True)
        return {"error": f"Failed to sync with MASSET platform: {str(e)}"}
    
    # 4. Update state to 'Onboarding'. Tracking continues via app.masset_employee_id
    app.sync_masset = 1
    app.masset_employee_id = local_employee_id
    app.masset_synced_at = datetime.utcnow()
    app.masset_synced_by = admin_id
    
    db.commit()
    db.refresh(app)
    
    return {
        "success": True, 
        "message": "Data synced successfully. Tracking managed via masset_employee_id.",
        "masset_employee_id": app.masset_employee_id, 
        "payload_sent": payload
    }


def update_masset_status_from_webhook(db: Session, employee_id: str, status: str) -> dict:
    """
    Called by the MASSET external HRMS webhook to update the applicant's status
    (e.g., to 'Onboarded' or 'AO Generated') using the generated masset_employee_id.
    """
    app = db.query(JobApplicant).filter(
        JobApplicant.masset_employee_id == employee_id
    ).first()

    if not app:
        return {"error": f"No candidate found with MASSET Employee ID: {employee_id}"}

    app.masset_status = status
    app.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(app)
    
    logger.info(f"Successfully updated candidate {app.job_applicant_id} (Employee ID: {employee_id}) to status: {status}")
    
    return {
        "success": True,
        "message": f"Candidate status updated to '{status}'"
    }

def get_masset_stats(db: Session, admin_id: int) -> dict:
    candidates = get_masset_candidates(db, admin_id)
    counts = {
        "Sync Pending": 0,
        "AO Pending": 0,
        "Onboarded": 0,
        "Sync Failed": 0
    }
    for c in candidates:
        if c["status"] in counts:
            counts[c["status"]] += 1
    return counts


def get_hr_reports(
    db: Session,
    admin_id: int,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    school_name: Optional[str] = None,
    department: Optional[str] = None,
    job_type: Optional[str] = None,
) -> dict:
    from datetime import datetime
    start_dt = None
    end_dt = None
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            pass
    if end_date:
        try:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            end_dt = end_dt.replace(hour=23, minute=59, second=59)
        except ValueError:
            pass

    is_hr = _is_hr_role(db, admin_id)
    jobs_q = db.query(JobPost)
    base_q = (
        db.query(JobApplicant)
        .join(JobPost, JobApplicant.job_id == JobPost.job_id)
    )
    if not is_hr:
        jobs_q = jobs_q.filter(JobPost.job_posted_by == admin_id)
        base_q = base_q.filter(JobPost.job_posted_by == admin_id)

    # Apply school_name (unit) filter
    if school_name:
        jobs_q = jobs_q.filter(JobPost.school_name == school_name)
        base_q = base_q.filter(JobPost.school_name == school_name)

    # Apply department (category) filter
    if department:
        jobs_q = jobs_q.filter(JobPost.department == department)
        base_q = base_q.filter(JobPost.department == department)

    # Apply job_type filter
    if job_type:
        jobs_q = jobs_q.filter(JobPost.job_type == job_type)
        base_q = base_q.filter(JobPost.job_type == job_type)

    # Apply date filters
    if start_dt:
        jobs_q = jobs_q.filter(JobPost.created_at >= start_dt)
        base_q = base_q.filter(JobApplicant.created_at >= start_dt)
    if end_dt:
        jobs_q = jobs_q.filter(JobPost.created_at <= end_dt)
        base_q = base_q.filter(JobApplicant.created_at <= end_dt)

    open_jobs = jobs_q.filter(JobPost.job_status == "publish").count()
    closed_jobs = jobs_q.filter(JobPost.job_status != "publish").count()

    total = base_q.count()
    selected = base_q.filter(JobApplicant.applicant_job_status == ApplicantJobStatus.SELECTED).count()
    on_hold = base_q.filter(JobApplicant.applicant_job_status == ApplicantJobStatus.HOLD).count()
    rejected = base_q.filter(JobApplicant.applicant_job_status == ApplicantJobStatus.REJECTED).count()
    offer_sent = base_q.filter(JobApplicant.issue_offer == 1).count()
    offer_accepted = base_q.filter(
        JobApplicant.offer_acceptance_status == OfferAcceptanceStatus.ACCEPTED
    ).count()
    onboarded = base_q.filter(JobApplicant.sync_masset == 1).count()
    interviewed = base_q.filter(
        JobApplicant.job_applicant_id.in_(
            db.query(JobInterviewSchedule.job_applicant_id).subquery()
        )
    ).count()

    total_jobs = jobs_q.count()
    fulfillment_rate = round((offer_accepted / total_jobs) * 100) if total_jobs else 0

    stages = {
        "Applied": max(total - selected - on_hold - rejected, 0),
        "Screened": selected + on_hold,
        "Interview": interviewed,
        "Offer": offer_sent,
        "Offer Accepted": offer_accepted,
        "Onboarding": onboarded,
        "Rejected": rejected,
    }

    # Monthly Hiring Trend
    accepted_apps = base_q.filter(JobApplicant.offer_acceptance_status == OfferAcceptanceStatus.ACCEPTED).all()
    monthly_trend = {}
    for app in accepted_apps:
        if app.offer_issued_date:
            month = app.offer_issued_date.strftime("%B")
            monthly_trend[month] = monthly_trend.get(month, 0) + 1
    
    if not monthly_trend:
        # Fallback empty data if no filters or no hires exist
        monthly_trend = {"January": 0, "February": 0, "March": 0, "April": 0}

    # School Comparison (School hires)
    from sqlalchemy import func
    school_hires_q = (
        db.query(JobPost.school_name, func.count(JobApplicant.job_applicant_id))
        .join(JobApplicant, JobPost.job_id == JobApplicant.job_id)
        .filter(JobApplicant.offer_acceptance_status == OfferAcceptanceStatus.ACCEPTED)
    )
    if not is_hr:
        school_hires_q = school_hires_q.filter(JobPost.job_posted_by == admin_id)
    if school_name:
        school_hires_q = school_hires_q.filter(JobPost.school_name == school_name)
    if department:
        school_hires_q = school_hires_q.filter(JobPost.department == department)
    if job_type:
        school_hires_q = school_hires_q.filter(JobPost.job_type == job_type)
    if start_dt:
        school_hires_q = school_hires_q.filter(JobApplicant.created_at >= start_dt)
    if end_dt:
        school_hires_q = school_hires_q.filter(JobApplicant.created_at <= end_dt)
        
    school_hires = school_hires_q.group_by(JobPost.school_name).all()
    # Initialize with all units from DB to 0 for a complete, structured response
    all_units = db.query(Units).all()
    school_comparison = {u.unit_name: 0 for u in all_units}
    for row in school_hires:
        if row[0]:
            school_comparison[row[0]] = row[1]

    # Vacancy Gap Analysis
    dept_vacancies_q = (
        db.query(JobPost.department, func.sum(JobPost.vacancy_count))
        .filter(JobPost.job_status == "publish")
    )
    if not is_hr:
        dept_vacancies_q = dept_vacancies_q.filter(JobPost.job_posted_by == admin_id)
    if school_name:
        dept_vacancies_q = dept_vacancies_q.filter(JobPost.school_name == school_name)
    if department:
        dept_vacancies_q = dept_vacancies_q.filter(JobPost.department == department)
    if job_type:
        dept_vacancies_q = dept_vacancies_q.filter(JobPost.job_type == job_type)
    if start_dt:
        dept_vacancies_q = dept_vacancies_q.filter(JobPost.created_at >= start_dt)
    if end_dt:
        dept_vacancies_q = dept_vacancies_q.filter(JobPost.created_at <= end_dt)
        
    dept_vacancies = dept_vacancies_q.group_by(JobPost.department).all()

    dept_hires_q = (
        db.query(JobPost.department, func.count(JobApplicant.job_applicant_id))
        .join(JobApplicant, JobPost.job_id == JobApplicant.job_id)
        .filter(JobApplicant.offer_acceptance_status == OfferAcceptanceStatus.ACCEPTED)
    )
    if not is_hr:
        dept_hires_q = dept_hires_q.filter(JobPost.job_posted_by == admin_id)
    if school_name:
        dept_hires_q = dept_hires_q.filter(JobPost.school_name == school_name)
    if department:
        dept_hires_q = dept_hires_q.filter(JobPost.department == department)
    if job_type:
        dept_hires_q = dept_hires_q.filter(JobPost.job_type == job_type)
    if start_dt:
        dept_hires_q = dept_hires_q.filter(JobApplicant.created_at >= start_dt)
    if end_dt:
        dept_hires_q = dept_hires_q.filter(JobApplicant.created_at <= end_dt)

    dept_hires = dept_hires_q.group_by(JobPost.department).all()

    vacancy_gap = {}
    default_depts = [
        "Teaching Staff", "Administration", "Physical Education", 
        "Arts & Music", "Sports Coaching", "Support Staff"
    ]
    for dept in default_depts:
        vacancy_gap[dept] = {"vacancies": 0, "hired": 0, "gap": 0}

    for row in dept_vacancies:
        if row[0]:
            if row[0] not in vacancy_gap:
                vacancy_gap[row[0]] = {"vacancies": 0, "hired": 0, "gap": 0}
            vacancy_gap[row[0]]["vacancies"] = row[1] or 0

    for row in dept_hires:
        if row[0]:
            if row[0] not in vacancy_gap:
                vacancy_gap[row[0]] = {"vacancies": 0, "hired": 0, "gap": 0}
            vacancy_gap[row[0]]["hired"] = row[1] or 0

    for dept in vacancy_gap:
        vacancy_gap[dept]["gap"] = max(0, vacancy_gap[dept]["vacancies"] - vacancy_gap[dept]["hired"])

    # Budget (Mock logic as requested by design but dynamic structure)
    budget = {
        "allocated": "₹48L",
        "utilized": "₹41L",
        "remaining": "₹7L",
        "percentage": 85
    }

    return {
        "total_applicants": total,
        "total_hires": offer_accepted,
        "open_jobs": open_jobs,
        "closed_jobs": closed_jobs,
        "fulfillment_rate": fulfillment_rate,
        "selected": selected,
        "on_hold": on_hold,
        "rejected": rejected,
        "offer_sent": offer_sent,
        "offer_accepted": offer_accepted,
        "onboarded": onboarded,
        "stages": stages,
        "by_stage": stages,
        "monthly_trend": monthly_trend,
        "school_comparison": school_comparison,
        "vacancy_gap": vacancy_gap,
        "budget": budget
    }

def get_pending_actions(db: Session, admin_id: int) -> dict:
    today = date.today()
    is_hr = _is_hr_role(db, admin_id)

    q_pre = (
        db.query(JobApplicant)
        .join(JobPost, JobApplicant.job_id == JobPost.job_id)
    )
    if not is_hr:
        q_pre = q_pre.filter(JobPost.job_posted_by == admin_id)
    pre_screen_count = q_pre.filter(JobApplicant.applicant_job_status.is_(None)).count()

    q_int = (
        db.query(JobInterviewSchedule)
        .join(JobApplicant, JobInterviewSchedule.job_applicant_id == JobApplicant.job_applicant_id)
        .join(JobPost, JobApplicant.job_id == JobPost.job_id)
    )
    if not is_hr:
        q_int = q_int.filter(JobPost.job_posted_by == admin_id)
    interviews_count = (
        q_int.filter(JobInterviewSchedule.scheduled_date >= today)
        .filter(JobInterviewSchedule.status.in_([InterviewStatus.SCHEDULED, InterviewStatus.RESCHEDULED]))
        .count()
    )

    q_off = (
        db.query(JobApplicant)
        .join(JobPost, JobApplicant.job_id == JobPost.job_id)
    )
    if not is_hr:
        q_off = q_off.filter(JobPost.job_posted_by == admin_id)
    offers_count = q_off.filter(JobApplicant.offer_acceptance_status == OfferAcceptanceStatus.ACCEPTED).count()

    q_sync = (
        db.query(JobApplicant)
        .join(JobPost, JobApplicant.job_id == JobPost.job_id)
    )
    if not is_hr:
        q_sync = q_sync.filter(JobPost.job_posted_by == admin_id)
    masset_sync_count = (
        q_sync.filter(JobApplicant.sync_masset == 0)
        .filter(JobApplicant.offer_acceptance_status == OfferAcceptanceStatus.ACCEPTED)
        .count()
    )

    return {
        "pre_screen_count": pre_screen_count,
        "interviews_count": interviews_count,
        "offers_count": offers_count,
        "masset_sync_count": masset_sync_count
    }

def get_sidebar_counts(db: Session, admin_id: int) -> dict:
    is_hr = _is_hr_role(db, admin_id)
    
    q_jobs = db.query(JobPost)
    if not is_hr:
        q_jobs = q_jobs.filter(JobPost.job_posted_by == admin_id)
    job_posts_count = q_jobs.count()
    
    q_apps = (
        db.query(JobApplicant)
        .join(JobPost, JobApplicant.job_id == JobPost.job_id)
    )
    if not is_hr:
        q_apps = q_apps.filter(JobPost.job_posted_by == admin_id)
    applicants_count = q_apps.count()

    return {
        "job_posts_count": job_posts_count,
        "job_applicants_count": applicants_count,
    }
