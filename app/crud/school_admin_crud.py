from datetime import date, datetime
from typing import Optional
from sqlalchemy.orm import Session

from app.models import(
    JobApplicant, 
    ApplicantJobStatus, 
    OfferAcceptanceStatus,
    JobPost, 
    JobStatus,
    JobInterviewSchedule, 
    InterviewStatus,
    Users,
    InterviewRemark,
    CandidateMetadata,
    CandidateExperience,
    Admins
)

from app.crud.common import (
    get_initials, get_color, get_av_class, parse_skills,
    compute_exp_str, compute_stage, compute_offer_status,
)


def _format_date(d) -> str:
    if not d:
        return ""
    try:
        return d.strftime("%d-%b-%Y")
    except Exception:
        return str(d)


def _format_time(t) -> str:
    if not t:
        return ""
    try:
        return datetime.strptime(str(t), "%H:%M:%S").strftime("%I:%M %p").lstrip("0")
    except Exception:
        return str(t)


def _days_ago(dt) -> int:
    if not dt:
        return 0
    try:
        return (date.today() - dt.date()).days
    except Exception:
        return 0


def _get_admin_job_filter(db: Session, admin_id: int):
    from sqlalchemy import text, or_, func
    admin = db.query(Admins).filter(Admins.admin_id == admin_id).first()
    if not admin:
        return JobPost.job_id == -1

    admin_email = (admin.email or "").strip().lower()
    
    # Check if there is any interview schedule where this admin is the interviewer
    has_interviews = db.query(JobInterviewSchedule).filter(
        func.lower(func.trim(JobInterviewSchedule.interviewer_name)) == admin_email
    ).first() is not None

    if not has_interviews:
        # If this logic is false, then loads no data and display in the dashboard
        return JobPost.job_id == -1

    school_name = ""
    if admin.unit_id:
        result = db.execute(text("SELECT unit_name FROM units WHERE id = :unit_id"), {"unit_id": admin.unit_id}).fetchone()
        if result and result[0]:
            school_name = result[0]

    iv_job_ids = [
        r[0] for r in db.query(JobInterviewSchedule.job_id)
        .filter(func.lower(func.trim(JobInterviewSchedule.interviewer_name)) == admin_email)
        .distinct()
        .all()
    ]
    
    if school_name and iv_job_ids:
        return or_(JobPost.school_name == school_name, JobPost.job_id.in_(iv_job_ids))
    elif school_name:
        return JobPost.school_name == school_name
    elif iv_job_ids:
        return JobPost.job_id.in_(iv_job_ids)
    else:
        return JobPost.job_id == -1

def get_school_dashboard(db: Session, admin_id: int) -> dict:
    job_filter = _get_admin_job_filter(db, admin_id)
    admin = db.query(Admins).filter(Admins.admin_id == admin_id).first()
    admin_email = (admin.email or "").strip().lower() if admin else ""

    from sqlalchemy import func

    jobs_q = db.query(JobPost).filter(
        job_filter,
        JobPost.job_status == JobStatus.PUBLISH,
    )
    active_jobs = jobs_q.count()

    all_job_ids = [j.job_id for j in db.query(JobPost.job_id).filter(job_filter).all()]
    apps_q = db.query(JobApplicant).filter(JobApplicant.job_id.in_(all_job_ids)) if all_job_ids else None
    total_applicants = apps_q.count() if apps_q else 0
    offers_sent = apps_q.filter(JobApplicant.issue_offer == 1).count() if apps_q else 0

    upcoming_interviews_q = (
        db.query(JobInterviewSchedule, Users, JobPost)
        .join(JobPost, JobInterviewSchedule.job_id == JobPost.job_id)
        .join(JobApplicant, JobInterviewSchedule.job_applicant_id == JobApplicant.job_applicant_id)
        .join(Users, JobApplicant.user_id == Users.user_id)
        .filter(job_filter)
        .filter(func.lower(func.trim(JobInterviewSchedule.interviewer_name)) == admin_email)
        .filter(JobInterviewSchedule.scheduled_date >= date.today())
        .order_by(JobInterviewSchedule.scheduled_date, JobInterviewSchedule.start_time)
    )
    upcoming_rows = upcoming_interviews_q.limit(10).all()
    upcoming_count = upcoming_interviews_q.count()

    # Build calendar data {YYYY-M-D: [{name, role, round, time, color}]}
    INTERVIEW_COLORS = ['#2563eb', '#16a34a', '#7c3aed', '#ea580c', '#0891b2', '#d97706', '#dc2626']
    calendar_data: dict = {}
    all_iv_rows = (
        db.query(JobInterviewSchedule, Users, JobPost)
        .join(JobPost, JobInterviewSchedule.job_id == JobPost.job_id)
        .join(JobApplicant, JobInterviewSchedule.job_applicant_id == JobApplicant.job_applicant_id)
        .join(Users, JobApplicant.user_id == Users.user_id)
        .filter(job_filter)
        .filter(func.lower(func.trim(JobInterviewSchedule.interviewer_name)) == admin_email)
        .all()
    )
    for ci, (iv, user, job) in enumerate(all_iv_rows):
        if iv.scheduled_date:
            key = f"{iv.scheduled_date.year}-{iv.scheduled_date.month}-{iv.scheduled_date.day}"
            calendar_data.setdefault(key, []).append({
                "name": f"{user.first_name} {user.last_name}".strip(),
                "role": job.job_title or "",
                "round": iv.interview_round or "Round 1",
                "time": _format_time(iv.start_time),
                "color": INTERVIEW_COLORS[ci % len(INTERVIEW_COLORS)],
            })

    # Upcoming list (max 5)
    upcoming_list = []
    for ci, (iv, user, job) in enumerate(upcoming_rows[:5]):
        name = f"{user.first_name} {user.last_name}".strip()
        iv_date = iv.scheduled_date
        today = date.today()
        if iv_date == today:
            label = f"Today {_format_time(iv.start_time)}"
        elif iv_date == today.replace(day=today.day + 1) if today.day < 28 else today:
            label = f"Tomorrow {_format_time(iv.start_time)}"
        else:
            label = f"{_format_date(iv_date)} {_format_time(iv.start_time)}"
        upcoming_list.append({
            "applicant_id": iv.job_applicant_id,
            "name": name,
            "initials": get_initials(user.first_name, user.last_name),
            "role": f"{job.job_title or ''} · {iv.interview_round or 'Round 1'}",
            "label": label,
            "color": INTERVIEW_COLORS[ci % len(INTERVIEW_COLORS)],
            "is_today": iv_date == today,
        })

    # Recent job posts (max 5)
    recent_jobs_rows = (
        db.query(JobPost)
        .filter(job_filter)
        .order_by(JobPost.created_at.desc())
        .limit(5)
        .all()
    )
    recent_jobs = []
    for j in recent_jobs_rows:
        applicant_count = db.query(JobApplicant).filter(JobApplicant.job_id == j.job_id).count()
        recent_jobs.append({
            "job_id": j.job_id,
            "title": j.job_title or "",
            "dept": j.department or "",
            "type": j.job_type or "Full-time",
            "vacancies": j.vacancy_count or 1,
            "applicants": applicant_count,
            "closing_date": _format_date(j.closing_date),
            "status": j.job_status.value.capitalize() if j.job_status else "Draft",
        })

    # Recent applicants (max 5)
    recent_app_rows = (
        db.query(JobApplicant, Users, JobPost)
        .join(Users, JobApplicant.user_id == Users.user_id)
        .join(JobPost, JobApplicant.job_id == JobPost.job_id)
        .filter(job_filter)
        .order_by(JobApplicant.created_at.desc())
        .limit(5)
        .all()
    )
    interviewed_recent = set()
    user_ids = []
    if recent_app_rows:
        rids = [a.job_applicant_id for a, _, _ in recent_app_rows]
        user_ids = [u.user_id for _, u, _ in recent_app_rows]
        iv_result = db.query(JobInterviewSchedule.job_applicant_id).filter(
            JobInterviewSchedule.job_applicant_id.in_(rids)
        ).distinct().all()
        interviewed_recent = {r[0] for r in iv_result}

    exps_map = {}
    if user_ids:
        exps = db.query(CandidateExperience).filter(CandidateExperience.user_id.in_(user_ids)).all()
        for e in exps:
            exps_map.setdefault(e.user_id, []).append(e)

    recent_applicants = []
    for ci, (app, user, job) in enumerate(recent_app_rows):
        stage = compute_stage(app, app.job_applicant_id in interviewed_recent)
        exp_str = compute_exp_str(exps_map.get(user.user_id, []))
        recent_applicants.append({
            "id": app.job_applicant_id,
            "name": f"{user.first_name} {user.last_name}".strip(),
            "initials": get_initials(user.first_name, user.last_name),
            "email": user.email,
            "position": job.job_title or "",
            "applied_date": _format_date(app.created_at.date() if app.created_at else None),
            "experience": exp_str,
            "stage": stage,
            "status": (app.applicant_job_status.value if app.applicant_job_status else ""),
            "color": INTERVIEW_COLORS[ci % len(INTERVIEW_COLORS)],
        })

    # Candidate status summary
    status_summary = {"selected": 0, "on_hold": 0, "rejected": 0}
    if apps_q:
        status_summary["selected"] = db.query(JobApplicant).filter(
            JobApplicant.job_id.in_(all_job_ids),
            JobApplicant.applicant_job_status == ApplicantJobStatus.SELECTED,
        ).count()
        status_summary["on_hold"] = db.query(JobApplicant).filter(
            JobApplicant.job_id.in_(all_job_ids),
            JobApplicant.applicant_job_status == ApplicantJobStatus.HOLD,
        ).count()
        status_summary["rejected"] = db.query(JobApplicant).filter(
            JobApplicant.job_id.in_(all_job_ids),
            JobApplicant.applicant_job_status == ApplicantJobStatus.REJECTED,
        ).count()

    return {
        "stats": {
            "active_jobs": active_jobs,
            "total_applicants": total_applicants,
            "offers_sent": offers_sent,
            "upcoming_interviews": upcoming_count,
        },
        "calendar": calendar_data,
        "upcoming_interviews": upcoming_list,
        "recent_jobs": recent_jobs,
        "recent_applicants": recent_applicants,
        "status_summary": status_summary,
    }


def get_school_jobs(db: Session, admin_id: int) -> list:
    job_filter = _get_admin_job_filter(db, admin_id)
    rows = (
        db.query(JobPost)
        .filter(job_filter)
        .order_by(JobPost.created_at.desc())
        .all()
    )
    out = []
    for j in rows:
        applicant_count = db.query(JobApplicant).filter(JobApplicant.job_id == j.job_id).count()
        out.append({
            "job_id": j.job_id,
            "title": j.job_title or "",
            "dept": j.department or "",
            "type": j.job_type or "Full-time",
            "vacancies": j.vacancy_count or 1,
            "closing_date": _format_date(j.closing_date),
            "applicants": applicant_count,
            "status": j.job_status.value.capitalize() if j.job_status else "Draft",
        })
    return out


def get_school_job_detail(db: Session, admin_id: int, job_id: int)-> Optional[dict]:
    job_filter = _get_admin_job_filter(db, admin_id)
    job = db.query(JobPost).filter(
        JobPost.job_id == job_id,
        job_filter,
    ).first()
    if not job:
        return None
    
    applicant_count = db.query(JobApplicant).filter(JobApplicant.job_id == job_id).count()
    
    shortlisted_count = db.query(JobApplicant).filter(
        JobApplicant.job_id == job_id,
        (JobApplicant.applicant_job_status.in_([ApplicantJobStatus.SELECTED, ApplicantJobStatus.HOLD])) | 
        (db.query(JobInterviewSchedule).filter(JobInterviewSchedule.job_applicant_id == JobApplicant.job_applicant_id).exists())
    ).count()
    
    interview_count = db.query(JobInterviewSchedule).filter(
        JobInterviewSchedule.job_id == job_id,
        JobInterviewSchedule.status == InterviewStatus.SCHEDULED
    ).count()
    
    offers_count = db.query(JobApplicant).filter(
        JobApplicant.job_id == job_id,
        (JobApplicant.issue_offer == 1) | (JobApplicant.offer_letter_doc.isnot(None))
    ).count()

    questions_list = []
    for q in job.job_pre_screening_questions:
        questions_list.append({
            "question": q.question_text or "",
            "type": q.question_type or "Text",
            "is_required": True
        })

    return {
        "job_id": job.job_id,
        "job_unique_id": f"JOB-{job.job_id}",
        "title": job.job_title or "",
        "dept": job.department or "",
        "type": job.job_type or "",
        "school": job.school_name or "",
        "vacancies": job.vacancy_count or 1,
        "min_exp": job.min_exp or "",
        "max_exp": job.max_exp or "",
        "description": job.job_description or "",
        "skills_required": job.skills_required or "",
        "education": job.education_qualification or "",
        "closing_date": _format_date(job.closing_date),
        "status": job.job_status.value if job.job_status else "draft",
        "applicants": applicant_count,
        "shortlisted": shortlisted_count,
        "interviews": interview_count,
        "offers": offers_count,
        "questions": questions_list,
    }


def get_school_applicants(db: Session, admin_id: int) -> list:
    job_filter = _get_admin_job_filter(db, admin_id)
    rows = (
        db.query(JobApplicant, Users, CandidateMetadata, JobPost)
        .join(Users, JobApplicant.user_id == Users.user_id)
        .outerjoin(CandidateMetadata, Users.user_id == CandidateMetadata.user_id)
        .join(JobPost, JobApplicant.job_id == JobPost.job_id)
        .filter(job_filter)
        .order_by(JobApplicant.created_at.desc())
        .all()
    )

    user_ids = [u.user_id for _, u, _, _ in rows]
    exps_map: dict[int, list] = {}
    if user_ids:
        exps = db.query(CandidateExperience).filter(CandidateExperience.user_id.in_(user_ids)).all()
        for e in exps:
            exps_map.setdefault(e.user_id, []).append(e)

    applicant_ids = [app.job_applicant_id for app, _, _, _ in rows]
    interviewed_ids: set[int] = set()
    if applicant_ids:
        result = db.query(JobInterviewSchedule.job_applicant_id).filter(
            JobInterviewSchedule.job_applicant_id.in_(applicant_ids)
        ).distinct().all()
        interviewed_ids = {r[0] for r in result}

    out = []
    for idx, (app, user, meta, job) in enumerate(rows):
        name = f"{user.first_name} {user.last_name}".strip()
        has_interview = app.job_applicant_id in interviewed_ids
        stage = compute_stage(app, has_interview)
        exp_str = compute_exp_str(exps_map.get(user.user_id, []))
        color = get_color(idx)
        
        # --- NEW INTERVIEW STATUS LOGIC ---
        interview_status = "Pending"
        if has_interview:
            last_iv = (
                db.query(JobInterviewSchedule)
                .filter(JobInterviewSchedule.job_applicant_id == app.job_applicant_id)
                .order_by(JobInterviewSchedule.scheduled_date.desc()) # Grabbing latest interview
                .first()
            )
            if last_iv:
                # Query the InterviewRemark table using the interview ID
                remark = db.query(InterviewRemark).filter(InterviewRemark.job_interview_id == last_iv.job_interview_id).first()
                
                if remark and remark.applicant_status:
                    if remark.applicant_status == "next_round":
                        interview_status = "Next Round"
                    else:
                        interview_status = remark.applicant_status.capitalize()
                elif last_iv.status == "completed":
                    interview_status = "Completed"
                elif last_iv.status:
                    interview_status = last_iv.status.value.capitalize() if hasattr(last_iv.status, 'value') else str(last_iv.status).capitalize()
        # ----------------------------------

        out.append({
            "id": app.job_applicant_id,
            "job_id": app.job_id,
            "name": name,
            "initials": get_initials(user.first_name, user.last_name),
            "job": job.job_title or "",
            "appliedDate": app.created_at.strftime("%Y-%m-%d") if app.created_at else "",
            "exp": exp_str,
            "stage": stage,
            "interviewStatus": interview_status,
            "avatar": get_initials(user.first_name, user.last_name),
            "color": color,
        })
    return out


def get_school_offers(db: Session, admin_id: int) -> list:
    job_filter = _get_admin_job_filter(db, admin_id)
    rows = (
        db.query(JobApplicant, Users, CandidateMetadata, JobPost)
        .join(Users, JobApplicant.user_id == Users.user_id)
        .outerjoin(CandidateMetadata, Users.user_id == CandidateMetadata.user_id)
        .join(JobPost, JobApplicant.job_id == JobPost.job_id)
        .filter(job_filter)
        .filter(JobApplicant.applicant_job_status == ApplicantJobStatus.SELECTED)
        .order_by(JobApplicant.updated_at.desc())
        .all()
    )

    user_ids = [u.user_id for _, u, _, _ in rows]
    exps_map: dict[int, list] = {}
    if user_ids:
        exps = db.query(CandidateExperience).filter(CandidateExperience.user_id.in_(user_ids)).all()
        for e in exps:
            exps_map.setdefault(e.user_id, []).append(e)

    out = []
    for idx, (app, user, meta, job) in enumerate(rows):
        name = f"{user.first_name} {user.last_name}".strip()
        exp_str = compute_exp_str(
            exps_map.get(user.user_id, [])
        )
        status = compute_offer_status(app)
        av = get_av_class(idx)
        updated = _format_date(app.updated_at.date() if app.updated_at else None)
        out.append({
            "id": app.job_applicant_id,
            "name": name,
            "initials": get_initials(user.first_name, user.last_name),
            "av": av,
            "role": job.job_title or "",
            "dept": job.department or "",
            "school": job.school_name or "",
            "exp": exp_str,
            "status": status,
            "updated": updated,
            "offered_salary": app.offered_salary or "",
            "joining_date": str(app.joining_date) if app.joining_date else "",
            "probation_period": app.probation_period or "",
            "offer_issued_date": str(app.offer_issued_date) if app.offer_issued_date else "",
            "offer_expiry_date": str(app.offer_expiry_date) if app.offer_expiry_date else "",
            "offer_remarks": app.offer_remarks or "",
            "offer_template": app.offer_template or "",
            "offer_letter_doc": app.offer_letter_doc or "",
        })
    return out


def issue_offer(db: Session, admin_id: int, applicant_id: int, payload: dict) -> dict:
    app = db.query(JobApplicant).filter(
        JobApplicant.job_applicant_id == applicant_id
    ).first()
    if not app:
        return {"error": "Applicant not found"}
    is_draft = payload.get("is_draft", False)
    app.issue_offer = 0 if is_draft else 1
    app.offered_salary = payload.get("offered_salary", app.offered_salary)
    if "joining_date" in payload:
        app.joining_date = payload["joining_date"]
    if "probation_period" in payload:
        app.probation_period = payload["probation_period"]
    app.offer_issued_date = payload.get("offer_issued_date") or date.today()
    app.offer_expiry_date = payload.get("offer_expiry_date")
    app.offer_remarks = payload.get("offer_remarks", "")
    app.offer_template = payload.get("offer_template", "standard")
    
    if "offer_letter_doc" in payload and payload["offer_letter_doc"]:
        app.offer_letter_doc = payload["offer_letter_doc"]
        
    app.issued_by = admin_id
    app.offer_acceptance_status = OfferAcceptanceStatus.PENDING
    db.commit()
    return {"success": True}


def update_offer_status(db: Session, admin_id: int, applicant_id: int, status: str) -> dict:
    app = db.query(JobApplicant).filter(
        JobApplicant.job_applicant_id == applicant_id
    ).first()
    if not app:
        return {"error": "Applicant not found"}
    status_map = {
        "accepted": OfferAcceptanceStatus.ACCEPTED,
        "expired": OfferAcceptanceStatus.EXPIRED,
        "rejected": OfferAcceptanceStatus.REJECTED,
        "pending": OfferAcceptanceStatus.PENDING,
    }
    new_status = status_map.get(status.lower())
    if not new_status:
        return {"error": f"Unknown status: {status}"}
    app.offer_acceptance_status = new_status
    db.commit()
    return {"success": True}

def get_school_sidebar_counts(db: Session, admin_id: int) -> dict:
    job_filter = _get_admin_job_filter(db, admin_id)
    job_posts_count = db.query(JobPost).filter(job_filter).count()
    
    applicants_count = (
        db.query(JobApplicant)
        .join(JobPost, JobApplicant.job_id == JobPost.job_id)
        .filter(job_filter)
        .count()
    )

    return {
        "job_posts_count": job_posts_count,
        "job_applicants_count": applicants_count,
    }
