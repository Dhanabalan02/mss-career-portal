from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_
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
    get_initials, get_color, parse_skills, compute_exp_str, get_latest_offers_map,
    get_applicant_stage_label,
)
from app.core.timezone import to_ist, now_ist

def _is_hr_role(db: Session, admin_id: int) -> bool:
    from sqlalchemy.orm import joinedload
    admin = db.query(Admins).options(joinedload(Admins.user_roles)).filter(Admins.admin_id == admin_id).first()
    return admin is not None and admin.user_roles.role_name in {"hr_head", "hr_team", "hr_admin", "hr_processor", "hr_executive"}

def _days_ago(dt) -> int:
    if not dt:
        return 0
    try:
        d = to_ist(dt)
        ref_date = d.date() if isinstance(d, datetime) else d
        return (now_ist().date() - ref_date).days
    except Exception:
        return 0


def _format_time(t) -> str:
    if not t:
        return ""
    try:
        return datetime.strptime(str(t), "%H:%M:%S").strftime("%I:%M %p").lstrip("0")
    except Exception:
        return str(t)


def _coerce_datetime(value):
    """Some columns (e.g. masset_synced_at) are stored as TEXT, so SQLAlchemy
    hands back a raw string instead of a datetime object; parse it so
    downstream to_ist()/strftime() calls work."""
    if isinstance(value, str):
        for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
        return None
    return value


def _format_date(d) -> str:
    d = _coerce_datetime(d)
    if not d:
        return ""
    try:
        d = to_ist(d)
        return d.strftime("%d-%b-%Y")
    except Exception:
        return str(d)


def _format_exact(dt) -> Optional[str]:
    """Formats a date/datetime as an exact, human-readable stamp (with time if available)."""
    dt = _coerce_datetime(dt)
    if not dt:
        return None
    try:
        dt = to_ist(dt)
        if isinstance(dt, datetime):
            return dt.strftime("%d %b %Y, %I:%M %p")
        return dt.strftime("%d %b %Y")
    except Exception:
        return str(dt)


def build_dynamic_timeline(app, stage: str, latest_interview=None, latest_offer=None) -> list:
    applied_at = _format_exact(app.created_at) or "Recently"

    # Rejected candidates (either at pre-screen, or later at Screened/Interview/Offer)
    # get a short, terminal timeline instead of the full pipeline — the stages
    # after rejection never happened, so they shouldn't be shown.
    if stage in ('Prescreen Rejected', 'Rejected'):
        tl = [{'t': 'Application Received', 'd': applied_at, 's': 'done', 'icon': 'ti-file-text'}]

        if stage == 'Rejected':
            # applicant_job_status overrides compute_stage() to 'Rejected' without
            # clearing applicant_stage, so that column still tells us how far the
            # candidate actually got before being rejected.
            progressed = get_applicant_stage_label(app)
            reached = {'Screened': 1, 'Interview': 2, 'Offer': 3}.get(progressed, 0)

            if reached >= 1:
                screened_at = _format_exact(app.updated_at)
                tl.append({'t': 'Resume Screened', 'd': screened_at or 'Completed', 's': 'done', 'icon': 'ti-shield-check'})
            if reached >= 2:
                interview_at = None
                if latest_interview:
                    iv_date = latest_interview.rescheduled_date or latest_interview.scheduled_date
                    iv_time = latest_interview.rescheduled_start_time or latest_interview.start_time
                    if iv_date and iv_time:
                        interview_at = datetime.combine(iv_date, iv_time).strftime("%d %b %Y, %I:%M %p")
                    elif iv_date:
                        interview_at = _format_exact(iv_date)
                tl.append({'t': 'Interview Process', 'd': interview_at or 'Completed', 's': 'done', 'icon': 'ti-microphone-2'})
            if reached >= 3:
                offer_at = _format_exact(latest_offer.offer_issued_date) if latest_offer else None
                tl.append({'t': 'Offer Extended', 'd': offer_at or 'Sent to Candidate', 's': 'done', 'icon': 'ti-file-invoice'})

        rejected_at = _format_exact(app.updated_at) or 'Recently'
        rejected_title = 'Application Rejected' if stage == 'Prescreen Rejected' else 'Candidate Rejected'
        tl.append({'t': rejected_title, 'd': rejected_at, 's': 'rejected', 'icon': 'ti-circle-x'})
        return tl

    stages = ['Screened', 'Interview', 'Offer', 'Offer Accepted', 'Onboarding', 'Onboarded']
    try:
        current_idx = stages.index(stage) + 1
    except ValueError:
        current_idx = 0

    is_onboarding = app.sync_masset == 1
    is_onboarded = app.masset_status and app.masset_status.lower() == 'onboarded'

    interview_at = None
    if latest_interview:
        iv_date = latest_interview.rescheduled_date or latest_interview.scheduled_date
        iv_time = latest_interview.rescheduled_start_time or latest_interview.start_time
        if iv_date and iv_time:
            interview_at = datetime.combine(iv_date, iv_time).strftime("%d %b %Y, %I:%M %p")
        elif iv_date:
            interview_at = _format_exact(iv_date)

    offer_at = _format_exact(latest_offer.offer_issued_date) if latest_offer else None
    accepted_at = _format_exact(app.offer_accepted_on)
    onboarding_at = _format_exact(app.masset_synced_at)
    onboarded_at = _format_exact(app.masset_sync_success_on)

    tl = []

    # 1. Applied (Application Received)
    s1 = 'done' if current_idx > 0 else 'current'
    tl.append({'t': 'Application Received', 'd': applied_at, 's': s1, 'icon': 'ti-file-text'})

    # 2. Screened (Resume Screened) - no dedicated timestamp column; best-effort via updated_at
    # while Screened is (or was most recently) the active stage.
    screened_at = _format_exact(app.updated_at) if stage == 'Screened' else None
    if current_idx > 1:
        s2 = 'done'
        d2 = screened_at or 'Completed'
    elif current_idx == 1:
        s2 = 'current'
        d2 = screened_at or 'In Progress'
    else:
        s2 = 'pending'
        d2 = 'Pending'
    tl.append({'t': 'Resume Screened', 'd': d2, 's': s2, 'icon': 'ti-shield-check'})

    # 3. Interview (Interview Process)
    if current_idx > 2:
        s3 = 'done'
        d3 = interview_at or 'Cleared'
    elif current_idx == 2:
        s3 = 'current'
        d3 = interview_at or 'In Progress'
    else:
        s3 = 'pending'
        d3 = 'Pending'
    tl.append({'t': 'Interview Process', 'd': d3, 's': s3, 'icon': 'ti-microphone-2'})

    # 4. Offer (Offer Extended)
    if current_idx > 3:
        s4 = 'done'
        d4 = offer_at or 'Sent to Candidate'
    elif current_idx == 3:
        s4 = 'current'
        d4 = offer_at or 'Sent to Candidate'
    else:
        s4 = 'pending'
        d4 = 'Pending'
    tl.append({'t': 'Offer Extended', 'd': d4, 's': s4, 'icon': 'ti-file-invoice'})

    # 5. Offer Accepted
    if current_idx > 4 or is_onboarding or is_onboarded:
        s5 = 'done'
        d5 = accepted_at or 'Candidate Agreed'
    elif current_idx == 4:
        s5 = 'current'
        d5 = accepted_at or 'Candidate Agreed'
    else:
        s5 = 'pending'
        d5 = 'Pending'
    tl.append({'t': 'Offer Accepted', 'd': d5, 's': s5, 'icon': 'ti-circle-check'})

    # 6. Onboarding Initiated
    if is_onboarded or is_onboarding:
        s6 = 'done'
        d6 = onboarding_at or 'Completed'
    else:
        s6 = 'pending'
        d6 = 'Pending'
    tl.append({'t': 'Onboarding Initiated', 'd': d6, 's': s6, 'icon': 'ti-briefcase'})

    # 7. Onboarding Completed
    if is_onboarded:
        s7 = 'done'
        d7 = onboarded_at or 'Joined Company'
    elif is_onboarding:
        s7 = 'current'
        d7 = 'In Progress'
    else:
        s7 = 'pending'
        d7 = 'Pending'
    tl.append({'t': 'Onboarding Completed', 'd': d7, 's': s7, 'icon': 'ti-briefcase'})

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
        query.filter(
            or_(
                JobApplicant.applicant_job_status != ApplicantJobStatus.REJECTED,
                JobApplicant.applicant_job_status.is_(None),
                JobApplicant.applicant_stage == ApplicantStage.PRESCREEN_REJECT
            )
        )
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

    # Batch-check which applicants have at least one interview, and which have active interviews
    applicant_ids = [app.job_applicant_id for app, _, _, _ in rows]
    interviewed_ids: set[int] = set()
    active_interview_ids: set[int] = set()
    if applicant_ids:
        result = (
            db.query(JobInterviewSchedule.job_applicant_id)
            .filter(JobInterviewSchedule.job_applicant_id.in_(applicant_ids))
            .distinct()
            .all()
        )
        interviewed_ids = {r[0] for r in result}

        from app.models.interview_schedule_model import InterviewStatus
        active_result = (
            db.query(JobInterviewSchedule.job_applicant_id)
            .filter(JobInterviewSchedule.job_applicant_id.in_(applicant_ids))
            .filter(JobInterviewSchedule.status.in_([InterviewStatus.SCHEDULED, InterviewStatus.RESCHEDULED]))
            .distinct()
            .all()
        )
        active_interview_ids = {r[0] for r in active_result}

    # Latest interview schedule per applicant (for exact interview date/time on the timeline)
    latest_interview_map: dict[int, JobInterviewSchedule] = {}
    if applicant_ids:
        interview_rows = (
            db.query(JobInterviewSchedule)
            .filter(JobInterviewSchedule.job_applicant_id.in_(applicant_ids))
            .order_by(JobInterviewSchedule.job_applicant_id, JobInterviewSchedule.job_interview_id.desc())
            .all()
        )
        for iv in interview_rows:
            if iv.job_applicant_id not in latest_interview_map:
                latest_interview_map[iv.job_applicant_id] = iv

    latest_offer_map = get_latest_offers_map(db, applicant_ids)

    out = []
    for idx, (app, user, meta, job) in enumerate(rows):
        name = f"{user.first_name} {user.last_name}".strip()
        has_interview = app.job_applicant_id in interviewed_ids
        
        from app.crud.common import compute_stage
        stage = compute_stage(app, has_interview)
        
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
            "appliedDate": _format_date(app.created_at),
            "updated_at": app.updated_at,
            "notes": notes,
            "skills": skills,
            "color": color,
            "timeline": build_dynamic_timeline(app, stage, latest_interview_map.get(app.job_applicant_id), latest_offer_map.get(app.job_applicant_id)),
            "sync_masset": app.sync_masset,
            "applicant_job_status": app.applicant_job_status,
            "has_active_interview": app.job_applicant_id in active_interview_ids,
        })
    return out


_STAGE_TO_FIELDS = {
    'Prescreen Rejected': {
        'applicant_stage': ApplicantStage.PRESCREEN_REJECT,
        'applicant_job_status': ApplicantJobStatus.REJECTED,
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
        'issue_offer': 0,
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
    'Hold': {
        'applicant_job_status': ApplicantJobStatus.HOLD,
    },
    'Reject': {
        'applicant_job_status': ApplicantJobStatus.REJECTED,
    },
}


def update_candidate_stage(db: Session, admin_id: int, applicant_id: int, stage: str, remarks: Optional[str] = None):
    from fastapi import HTTPException
    from app.models.interview_schedule_model import JobInterviewSchedule, InterviewStatus
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

    previous_stage = app_record.applicant_stage

    # If the action is Hold or Reject, handle latest interview schedule and remarks
    if stage in ("Hold", "Reject"):
        latest_interview = (
            db.query(JobInterviewSchedule)
            .filter(JobInterviewSchedule.job_applicant_id == applicant_id)
            .order_by(JobInterviewSchedule.job_interview_id.desc())
            .first()
        )
        if latest_interview:
            latest_interview.status = InterviewStatus.COMPLETED
            
            from app.models.interview_remarks_model import InterviewRemark, ApplicantStatus
            new_status = ApplicantStatus.HOLD if stage == "Hold" else ApplicantStatus.REJECTED
            new_remark = InterviewRemark(
                job_interview_id=latest_interview.job_interview_id,
                round=latest_interview.interview_round or "General",
                remarks=remarks or f"Candidate put on {stage.lower()}",
                applicant_status=new_status,
                created_by=admin_id
            )
            db.add(new_remark)

    if (app_record.applicant_stage in (ApplicantStage.OFFER, ApplicantStage.OFFER_ACCEPTED)) and stage == "Interview":
        # Find the latest interview schedule for this applicant
        latest_interview = (
            db.query(JobInterviewSchedule)
            .filter(JobInterviewSchedule.job_applicant_id == applicant_id)
            .order_by(JobInterviewSchedule.job_interview_id.desc())
            .first()
        )
        if latest_interview:
            latest_interview.status = InterviewStatus.SCHEDULED
            
            # Find the corresponding remark
            from app.models.interview_remarks_model import InterviewRemark, ApplicantStatus
            remark = (
                db.query(InterviewRemark)
                .filter(InterviewRemark.job_interview_id == latest_interview.job_interview_id)
                .first()
            )
            if remark and remark.applicant_status == ApplicantStatus.SELECTED:
                remark.applicant_status = ApplicantStatus.NEXT_ROUND

    # Check if candidate is moving from Interview to Offer
    if stage == "Offer" and app_record.applicant_stage == ApplicantStage.INTERVIEW:
        latest_interview = (
            db.query(JobInterviewSchedule)
            .filter(JobInterviewSchedule.job_applicant_id == applicant_id)
            .order_by(JobInterviewSchedule.job_interview_id.desc())
            .first()
        )
        if latest_interview:
            from app.models.interview_remarks_model import InterviewRemark, ApplicantStatus
            
            latest_interview.status = InterviewStatus.COMPLETED
            
            remark = (
                db.query(InterviewRemark)
                .filter(InterviewRemark.job_interview_id == latest_interview.job_interview_id)
                .first()
            )
            if remark:
                if remarks is not None:
                    remark.remarks = remarks
                remark.applicant_status = ApplicantStatus.SELECTED
                remark.updated_by = admin_id
            else:
                new_remark = InterviewRemark(
                    job_interview_id=latest_interview.job_interview_id,
                    remarks=remarks,
                    applicant_status=ApplicantStatus.SELECTED,
                    created_by=admin_id
                )
                db.add(new_remark)

    for attr, value in fields.items():
        setattr(app_record, attr, value)

    db.commit()

    if previous_stage == ApplicantStage.PRESCREEN_REJECT and stage == "Screened":
        try:
            from app.crud.notification_crud import notify_candidate

            notify_candidate(
                db=db,
                candidate_id=app_record.user_id,
                title="Application Status Updated",
                message=(
                    f"Your application status for '{job.job_title}' has been updated to Screened."
                ),
                notification_type="application_status_update",
                sender_user_id=admin_id,
                sender_type="hr",
                redirect_url="/mss-career-portal/applied-jobs",
            )
        except Exception as e:
            logger.error(
                f"Failed to notify candidate {app_record.user_id} about stage update: {e}"
            )
    
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
        date_val = iv.scheduled_date

        start_val = iv.start_time
        end_val = iv.end_time

        # scheduled_date/start_time/end_time were split from a UTC instant when the
        # interview was booked (see job_interview_route.py); recombine before
        # converting to IST so the date doesn't drift for interviews near midnight.
        start_ist = to_ist(datetime.combine(date_val, start_val)) if (date_val and start_val) else None
        end_ist = to_ist(datetime.combine(date_val, end_val)) if (date_val and end_val) else None

        time_str = _format_time(start_ist.time()) if start_ist else ""
        if end_ist:
            time_str += f" - {_format_time(end_ist.time())}"

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
            "date": _format_date(start_ist or date_val),
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
        if iv["date"] == _format_date(now_ist().date())
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

    latest_offer_map = get_latest_offers_map(db, [app.job_applicant_id for app, _, _ in rows])

    out = []
    for idx, (app, user, job) in enumerate(rows):
        name = f"{user.first_name} {user.last_name}".strip()
        offer = latest_offer_map.get(app.job_applicant_id)
        last_sync = _format_exact(app.masset_synced_at) if app.masset_synced_at else None
        if not last_sync:
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
            "offerDate": _format_date(offer.offer_issued_date) if offer else "",
            "status": status,
            "lastSync": last_sync,
            "email": user.email,
            "color": get_color(idx),
        })
    return out

def sync_masset(db: Session, admin_id: int, applicant_id: int) -> dict:
    # 1. Fetch the applicant using applicant_id
    app = db.query(JobApplicant).filter(
        JobApplicant.job_applicant_id == applicant_id
    ).first()
    
    if not app:
        return {"error": "Applicant not found"}

    user = db.query(Users).filter(Users.user_id == app.user_id).first()
    user_metadata = db.query(CandidateMetadata).filter(CandidateMetadata.user_id == app.user_id).first()
    job = db.query(JobPost).filter(JobPost.job_id == app.job_id).first()

    # Resolve the unit id from the units table using school_name
    unit = None
    if job and job.school_name:
        unit = db.query(Units).filter(Units.unit_name == job.school_name).first()

    # 2. Construct JSON Payload (tracking via applicant_id and masset_employee_id)
    payload = {
        "candidate_id": applicant_id,
        "application_id": app.mss_app_no,
        "first_name": user.first_name if user else "",
        "last_name": user.last_name if user else "",
        "email": user.email if user else "",
        "phone": user.mobile if user else "",
        "date_of_birth": user_metadata.date_of_birth.strftime('%Y-%m-%d') if (user_metadata and user_metadata.date_of_birth and hasattr(user_metadata.date_of_birth, 'strftime')) else (user_metadata.date_of_birth if user_metadata and user_metadata.date_of_birth else ""),
        'gender': user.gender if user else "",
        "marital_status": user_metadata.marital_status if user_metadata else "", 
        "blood_group": user_metadata.blood_group if user_metadata else "",
        "designation": job.job_title if job else "",
        "unit_name": job.school_name if job else "",
        "unit_id": unit.id if unit else None,
        "action": "appointment_order"
    }

    # 3. HTTP POST Request to MASSET local server or Webhook URL
    webhook_url = "https://test.masset.themadrassevasadan.org/api/career_sync.php"
    logger.info(f"Attempting to sync candidate {applicant_id} to {webhook_url}")
    logger.info(f"Payload: {payload}")
    
    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        logger.info(f"Response Status Code: {response.status_code}")
        logger.info(f"Response Text: {response.text}")
        response.raise_for_status()
    except Exception as e:
        logger.error(f"MASSET Sync Failed. Exact issue: {str(e)}", exc_info=True)
        return {"error": f"Failed to sync with MASSET platform: {str(e)}"}
    
    app.sync_masset = 1
    app.applicant_stage = ApplicantStage.ONBOARDING
    app.masset_synced_at = datetime.utcnow()
    app.masset_synced_by = admin_id
    
    db.commit()
    db.refresh(app)
    
    try:
        from app.models.admin_model import Admins
        from app.services.email_service import EmailService
        
        school_admin = db.query(Admins).filter(Admins.admin_id == job.job_posted_by).first()
        if school_admin and school_admin.email:
            candidate_name = f"{user.first_name} {user.last_name}".strip() if user else "Candidate"
            position = job.job_title if job else "Unknown Position"
            email_service = EmailService()
            email_service.send_masset_sync_email(
                to_email=school_admin.email,
                candidate_name=candidate_name,
                position=position
            )
    except Exception as e:
        logger.error(f"Failed to send MASSET sync email: {e}")
    
    return {
        "success": True, 
        "message": "Data synced successfully. Tracking managed via application ID.",
        "payload_sent": payload
    }


def update_masset_status_from_webhook(db: Session, application_id: str, masset_employee_id: str, status: str, reporting_to: Optional[str]) -> dict:
    """
    Called by the MASSET external HRMS webhook to update the applicant's status
    and generated masset_employee_id using the application_id.
    """
    app = db.query(JobApplicant).filter(
        JobApplicant.mss_app_no == application_id
    ).first()

    if not app:
        return {"error": f"No candidate found with Application ID: {application_id}"}

    app.masset_employee_id = masset_employee_id
    app.masset_status = status
    
    if status and status.lower() == "onboarded":
        app.issue_appointment_order = 1
        app.masset_sync_success_on = datetime.utcnow()
        app.applicant_stage = ApplicantStage.ONBOARDING_COMPLETED
        app.reporting_to = reporting_to
        
    app.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(app)
    
    logger.info(f"Successfully updated candidate {app.job_applicant_id} (Application ID: {application_id}) to status: {status} with masset_employee_id: {masset_employee_id}")
    
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
    onboarding = base_q.filter(
        JobApplicant.sync_masset == 1,
        JobApplicant.issue_appointment_order != 1,
    ).count()
    onboarded = base_q.filter(JobApplicant.issue_appointment_order == 1).count()
    interviewed = base_q.filter(
        JobApplicant.job_applicant_id.in_(
            db.query(JobInterviewSchedule.job_applicant_id).subquery()
        )
    ).count()

    total_jobs = jobs_q.count()
    fulfillment_rate = round((offer_accepted / total_jobs) * 100) if total_jobs else 0

    stages = {
        "PreScreening Rejection": max(rejected, 0),
        "Screened": selected + on_hold,
        "Interview": interviewed,
        "Offer": offer_sent,
        "Offer Accepted": offer_accepted,
        "Onboarding": onboarding,
        "Onboarded": onboarded,
        "Rejected": rejected,
    }

    # Monthly Hiring Trend
    accepted_apps = base_q.filter(JobApplicant.offer_acceptance_status == OfferAcceptanceStatus.ACCEPTED).all()
    accepted_offer_map = get_latest_offers_map(db, [a.job_applicant_id for a in accepted_apps])
    monthly_trend = {}
    for app in accepted_apps:
        offer = accepted_offer_map.get(app.job_applicant_id)
        if offer and offer.offer_issued_date:
            month = offer.offer_issued_date.strftime("%B")
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
        "vacancy_gap": vacancy_gap
    }

def get_pending_actions(db: Session, admin_id: int) -> dict:
    today = now_ist().date()
    is_hr = _is_hr_role(db, admin_id)

    q_pre = (
        db.query(JobApplicant)
        .join(JobPost, JobApplicant.job_id == JobPost.job_id)
    )
    if not is_hr:
        q_pre = q_pre.filter(JobPost.job_posted_by == admin_id)
    # "Screened" also leaves applicant_job_status NULL, so also require the
    # applicant to still be at the fresh/unstaged step (not yet screened),
    # otherwise already-screened candidates keep re-appearing as pending.
    pre_screen_count = q_pre.filter(
        JobApplicant.applicant_job_status.is_(None),
        JobApplicant.applicant_stage.is_(None),
    ).count()

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
    
