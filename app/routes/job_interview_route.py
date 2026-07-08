from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from app.core.html_helper import serve_html_with_base
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.crud.job_interview_crud import (
    cancel_interview,
    complete_interview,
    reschedule_interview,
    schedule_interview,
    submit_interview_remarks,
    update_interview,
)
from app.models import (
    ApplicantStatus,
    InterviewMode,
    InterviewRemark,
    JobInterviewSchedule,
    JobApplicant,
    ApplicantJobStatus,
    InterviewStatus,
    ApplicantStage
)
from app.routes.interview_auth_route import get_current_admin_id

router = APIRouter(prefix="/job-interviews", tags=["Job Interviews"])


class InterviewScheduleRequest(BaseModel):
    job_id: int
    job_applicant_id: int
    interview_round: str
    scheduled_at: str           # Accept both naive and tz-aware ISO strings
    end_time_at: str
    interview_mode: InterviewMode = InterviewMode.ONLINE
    meeting_link: Optional[str] = None
    location: Optional[str] = None
    interviewer_name: Optional[str] = None
    created_by: Optional[int] = None


class InterviewUpdateRequest(BaseModel):
    interview_round: Optional[str] = None
    interview_mode: Optional[InterviewMode] = None
    scheduled_at: Optional[datetime] = None
    end_time_at: Optional[datetime] = None
    meeting_link: Optional[str] = None
    location: Optional[str] = None
    interviewer_name: Optional[str] = None


class InterviewRescheduleRequest(BaseModel):
    scheduled_at: str           # Accept both naive and tz-aware ISO strings
    end_time_at: str
    reschedule_reason: Optional[str] = None
    rescheduled_by: Optional[int] = None
    interviewer_name: Optional[str] = None


class InterviewCancelRequest(BaseModel):
    cancelled_reason: Optional[str] = None


class InterviewRemarksRequest(BaseModel):
    applicant_status: ApplicantStatus
    created_by: Optional[int] = None
    round: Optional[str] = None
    remarks: Optional[str] = None


def _serialize_job_interview(job_interview: JobInterviewSchedule) -> dict:
    scheduled_at = None
    if job_interview.scheduled_date and getattr(job_interview, 'start_time', None):
        scheduled_at = datetime.combine(job_interview.scheduled_date, job_interview.start_time)

    end_time_at = None
    if job_interview.scheduled_date and getattr(job_interview, 'end_time', None):
        end_time_at = datetime.combine(job_interview.scheduled_date, job_interview.end_time)

    rescheduled_at = None
    if job_interview.rescheduled_date and getattr(job_interview, 'rescheduled_start_time', None):
        rescheduled_at = datetime.combine(job_interview.rescheduled_date, job_interview.rescheduled_start_time)
        
    rescheduled_end_time_at = None
    if job_interview.rescheduled_date and getattr(job_interview, 'rescheduled_end_time', None):
        rescheduled_end_time_at = datetime.combine(job_interview.rescheduled_date, job_interview.rescheduled_end_time)

    return {
        "job_interview_id": job_interview.job_interview_id,
        "job_id": job_interview.job_id,
        "job_applicant_id": job_interview.job_applicant_id,
        "interview_round": job_interview.interview_round,
        "interview_mode": job_interview.interview_mode,
        "scheduled_at": scheduled_at,
        "end_time_at": end_time_at,
        "rescheduled_at": rescheduled_at,
        "rescheduled_end_time_at": rescheduled_end_time_at,
        "meeting_link": job_interview.meeting_link,
        "location": job_interview.location,
        "interviewer_name": job_interview.interviewer_name,
        "status": job_interview.status,
        "reschedule_reason": job_interview.reschedule_reason,
        "cancelled_reason": job_interview.cancelled_reason,
        "created_by": job_interview.created_by,
        "rescheduled_by": job_interview.rescheduled_by,
    }


def _serialize_interview_remark(interview_remark: InterviewRemark) -> dict:
    return {
        "interview_remarks_id": interview_remark.interview_remarks_id,
        "job_interview_id": interview_remark.job_interview_id,
        "round": interview_remark.round,
        "remarks": interview_remark.remarks,
        "applicant_status": interview_remark.applicant_status,
        "created_by": interview_remark.created_by,
        "updated_by": interview_remark.updated_by,
    }


@router.get("/school-admins")
def get_school_admins_route(
    db: Session = Depends(get_db),
    admin_id: int = Depends(get_current_admin_id)
):
    from sqlalchemy import text
    query = text("""
        SELECT a.admin_id, a.email, a.unit_id, u.unit_name
        FROM admins a
        LEFT JOIN units u ON a.unit_id = u.id
        WHERE a.role_id = 7 AND a.is_active = 1
    """)
    result = db.execute(query).fetchall()
    return [
        {
            "admin_id": r.admin_id, 
            "email": r.email, 
            "unit_id": r.unit_id,
            "unit_name": r.unit_name
        } 
        for r in result
    ]

@router.post("/")
def schedule_interview_route(
    form_data: InterviewScheduleRequest,
    db: Session = Depends(get_db),
    admin_id: int = Depends(get_current_admin_id)
):
    scheduled_at_str = form_data.scheduled_at.replace("Z", "+00:00")
    end_time_at_str = form_data.end_time_at.replace("Z", "+00:00")
    try:
        scheduled_dt = datetime.fromisoformat(scheduled_at_str)
        if scheduled_dt.tzinfo is not None:
            scheduled_dt = scheduled_dt.astimezone(timezone.utc).replace(tzinfo=None)
            
        end_time_dt = datetime.fromisoformat(end_time_at_str)
        if end_time_dt.tzinfo is not None:
            end_time_dt = end_time_dt.astimezone(timezone.utc).replace(tzinfo=None)
    except ValueError:
        from fastapi import HTTPException as _HTTPException
        raise _HTTPException(status_code=422, detail="Invalid date format. Use ISO 8601, e.g. 2026-06-17T10:00:00")

    job_interview = schedule_interview(
        db=db,
        job_id=form_data.job_id,
        job_applicant_id=form_data.job_applicant_id,
        interview_round=form_data.interview_round,
        scheduled_at=scheduled_dt,
        end_time_at=end_time_dt,
        interview_mode=form_data.interview_mode,
        meeting_link=form_data.meeting_link,
        location=form_data.location,
        interviewer_name=form_data.interviewer_name,
        created_by=admin_id,
    )
    
    # Send Notifications
    try:
        from app.models import JobApplicant, JobPost, Users, Admins
        from app.crud.notification_crud import notify_candidate, notify_school_admin
        
        applicant = db.query(JobApplicant).filter(JobApplicant.job_applicant_id == form_data.job_applicant_id).first()
        job = db.query(JobPost).filter(JobPost.job_id == form_data.job_id).first()
        
        if applicant and job:
            candidate = db.query(Users).filter(Users.user_id == applicant.user_id).first()
            if candidate:
                candidate_name = f"{candidate.first_name} {candidate.last_name}".strip()
                date_str = scheduled_dt.strftime("%d %B, %Y at %I:%M %p")
                
                # 1. Notify Candidate
                notify_candidate(
                    db=db,
                    candidate_id=candidate.user_id,
                    title="Interview Scheduled",
                    message=f"An interview for '{job.job_title}' has been scheduled on {date_str} (Mode: {form_data.interview_mode.value if hasattr(form_data.interview_mode, 'value') else form_data.interview_mode}).",
                    notification_type="interview_scheduled",
                    sender_user_id=admin_id,
                    sender_type="hr"
                )
                
                from app.services.interview_service import InterviewService
                interview_service = InterviewService()
                
                if getattr(candidate, "mobile", None):
                    interview_service.send_interview_scheduled(
                        to=candidate.mobile,
                        candidate_name=candidate_name,
                        job_title=job.job_title,
                        interview_mode=str(form_data.interview_mode.value if hasattr(form_data.interview_mode, 'value') else form_data.interview_mode),
                        interview_date_time=date_str,
                        interview_type=form_data.interview_round,
                        interview_link_location=form_data.location or form_data.meeting_link or "N/A"
                    )
                
                # 2. Notify School Admin (interviewer)
                interviewer_admin_id = None
                if form_data.interviewer_name:
                    interviewer = db.query(Admins).filter(Admins.email == form_data.interviewer_name).first()
                    if interviewer:
                        interviewer_admin_id = interviewer.admin_id
                
                if interviewer_admin_id:
                    notify_school_admin(
                        db=db,
                        admin_id=interviewer_admin_id,
                        title="Interview Scheduled",
                        message=f"Interview round '{form_data.interview_round}' has been scheduled for candidate {candidate_name} on {date_str}.",
                        notification_type="interview_scheduled",
                        sender_user_id=admin_id,
                        sender_type="hr"
                    )
                    
                    interviewer_mobile = getattr(interviewer, "mobile", None)
                    if interviewer_mobile:
                        interview_service.send_admin_interview_schedule(
                            to=interviewer_mobile,
                            job_title=job.job_title,
                            candidate_name=candidate_name,
                            interview_round=form_data.interview_round,
                            interview_mode=str(form_data.interview_mode.value if hasattr(form_data.interview_mode, 'value') else form_data.interview_mode),
                            interview_date_time=date_str,
                            interview_link_location=form_data.location or form_data.meeting_link or "N/A"
                        )
                
    except Exception as e:
        from app.core.logger import logger
        logger.error(f"Error creating interview scheduled notifications: {e}")

    return _serialize_job_interview(job_interview)


@router.put("/{job_interview_id}")
def update_interview_route(
    job_interview_id: int,
    form_data: InterviewUpdateRequest,
    db: Session = Depends(get_db),
    admin_id: int = Depends(get_current_admin_id)
):
    """Edits the details of an existing interview schedule."""
    job_interview = update_interview(
        db=db,
        job_interview_id=job_interview_id,
        interview_round=form_data.interview_round,
        interview_mode=form_data.interview_mode,
        scheduled_at=form_data.scheduled_at,
        end_time_at=form_data.end_time_at,
        meeting_link=form_data.meeting_link,
        location=form_data.location,
        interviewer_name=form_data.interviewer_name,
    )
    return _serialize_job_interview(job_interview)


@router.patch("/{job_interview_id}/reschedule")
def reschedule_interview_route(
    job_interview_id: int,
    form_data: InterviewRescheduleRequest,
    db: Session = Depends(get_db),
    admin_id: int = Depends(get_current_admin_id)
):
    """Reschedules an interview to a new date/time."""
    scheduled_at_str = form_data.scheduled_at.replace("Z", "+00:00")
    end_time_at_str = form_data.end_time_at.replace("Z", "+00:00")
    try:
        scheduled_dt = datetime.fromisoformat(scheduled_at_str)
        if scheduled_dt.tzinfo is not None:
            scheduled_dt = scheduled_dt.astimezone(timezone.utc).replace(tzinfo=None)
            
        end_time_dt = datetime.fromisoformat(end_time_at_str)
        if end_time_dt.tzinfo is not None:
            end_time_dt = end_time_dt.astimezone(timezone.utc).replace(tzinfo=None)
    except ValueError:
        from fastapi import HTTPException as _HTTPException
        raise _HTTPException(status_code=422, detail="Invalid date format.")

    job_interview = reschedule_interview(
        db=db,
        job_interview_id=job_interview_id,
        scheduled_at=scheduled_dt,
        end_time_at=end_time_dt,
        reschedule_reason=form_data.reschedule_reason,
        rescheduled_by=admin_id,
        interviewer_name=form_data.interviewer_name,
    )
    
    # Send Notifications
    try:
        from app.models import JobApplicant, JobPost, Users, Admins
        from app.crud.notification_crud import notify_candidate, notify_school_admin
        
        applicant = db.query(JobApplicant).filter(JobApplicant.job_applicant_id == job_interview.job_applicant_id).first()
        job = db.query(JobPost).filter(JobPost.job_id == job_interview.job_id).first()
        
        if applicant and job:
            candidate = db.query(Users).filter(Users.user_id == applicant.user_id).first()
            if candidate:
                candidate_name = f"{candidate.first_name} {candidate.last_name}".strip()
                date_str = scheduled_dt.strftime("%d %B, %Y at %I:%M %p")
                reason_part = f" Reason: {form_data.reschedule_reason}." if form_data.reschedule_reason else ""
                
                # 1. Notify Candidate
                notify_candidate(
                    db=db,
                    candidate_id=candidate.user_id,
                    title="Interview Rescheduled",
                    message=f"Your interview for '{job.job_title}' has been rescheduled to {date_str}.{reason_part}",
                    notification_type="interview_rescheduled",
                    sender_user_id=admin_id,
                    sender_type="hr"
                )
                
                from app.services.interview_service import InterviewService
                interview_service = InterviewService()
                if getattr(candidate, "mobile", None):
                    interview_service.send_interview_rescheduled(
                        to=candidate.mobile,
                        candidate_name=candidate_name,
                        job_title=job.job_title,
                        interview_mode=str(job_interview.interview_mode.value if hasattr(job_interview.interview_mode, 'value') else job_interview.interview_mode),
                        interview_new_date_time=date_str,
                        interview_type=job_interview.interview_round,
                        interview_link_location=job_interview.location or job_interview.meeting_link or "N/A",
                        rescheduled_reason=form_data.reschedule_reason or "N/A"
                    )
                
                # 2. Notify School Admin (interviewer)
                interviewer_admin_id = None
                if job_interview.interviewer_name:
                    interviewer = db.query(Admins).filter(Admins.email == job_interview.interviewer_name).first()
                    if interviewer:
                        interviewer_admin_id = interviewer.admin_id
                
                if interviewer_admin_id:
                    notify_school_admin(
                        db=db,
                        admin_id=interviewer_admin_id,
                        title="Interview Rescheduled",
                        message=f"Interview round '{job_interview.interview_round}' has been rescheduled to {date_str} for candidate {candidate_name}.{reason_part}",
                        notification_type="interview_rescheduled",
                        sender_user_id=admin_id,
                        sender_type="hr"
                    )
                    
                    interviewer_mobile = getattr(interviewer, "mobile", None)
                    if interviewer_mobile:
                        interview_service.send_admin_interview_reschedule(
                            to=interviewer_mobile,
                            job_title=job.job_title,
                            candidate_name=candidate_name,
                            interview_round=job_interview.interview_round,
                            interview_mode=str(job_interview.interview_mode.value if hasattr(job_interview.interview_mode, 'value') else job_interview.interview_mode),
                            interview_new_date_time=date_str,
                            interview_link_location=job_interview.location or job_interview.meeting_link or "N/A"
                        )
                
    except Exception as e:
        from app.core.logger import logger
        logger.error(f"Error creating interview rescheduled notifications: {e}")

    return _serialize_job_interview(job_interview)


@router.patch("/{job_interview_id}/cancel")
def cancel_interview_route(
    job_interview_id: int,
    form_data: InterviewCancelRequest,
    db: Session = Depends(get_db),
    admin_id: int = Depends(get_current_admin_id)
):
    """Cancels a scheduled interview."""
    job_interview = cancel_interview(
        db=db,
        job_interview_id=job_interview_id,
        cancelled_reason=form_data.cancelled_reason,
    )
    
    # Send Notifications
    try:
        from app.models import JobApplicant, JobPost, Users, Admins
        from app.crud.notification_crud import notify_candidate, notify_school_admin
        
        applicant = db.query(JobApplicant).filter(JobApplicant.job_applicant_id == job_interview.job_applicant_id).first()
        job = db.query(JobPost).filter(JobPost.job_id == job_interview.job_id).first()
        
        if applicant and job:
            candidate = db.query(Users).filter(Users.user_id == applicant.user_id).first()
            if candidate:
                candidate_name = f"{candidate.first_name} {candidate.last_name}".strip()
                reason_part = f" Reason: {form_data.cancelled_reason}." if form_data.cancelled_reason else ""
                
                # 1. Notify Candidate
                notify_candidate(
                    db=db,
                    candidate_id=candidate.user_id,
                    title="Interview Cancelled",
                    message=f"Your interview for '{job.job_title}' has been cancelled.{reason_part}",
                    notification_type="interview_cancelled",
                    sender_user_id=admin_id,
                    sender_type="hr"
                )
                
                sch_dt = None
                if job_interview.scheduled_date and job_interview.start_time:
                    sch_dt = datetime.combine(job_interview.scheduled_date, job_interview.start_time)
                date_str = sch_dt.strftime("%d %B, %Y at %I:%M %p") if sch_dt else "N/A"
                
                from app.services.interview_service import InterviewService
                interview_service = InterviewService()
                
                if getattr(candidate, "mobile", None):
                    interview_service.send_interview_cancel(
                        to=candidate.mobile,
                        candidate_name=candidate_name,
                        job_title=job.job_title,
                        interview_round=job_interview.interview_round,
                        interview_date_time=date_str,
                        cancel_reason=form_data.cancelled_reason or "N/A"
                    )
                
                # 2. Notify School Admin (interviewer)
                interviewer_admin_id = None
                if job_interview.interviewer_name:
                    interviewer = db.query(Admins).filter(Admins.email == job_interview.interviewer_name).first()
                    if interviewer:
                        interviewer_admin_id = interviewer.admin_id
                
                if interviewer_admin_id:
                    notify_school_admin(
                        db=db,
                        admin_id=interviewer_admin_id,
                        title="Interview Cancelled",
                        message=f"Interview round '{job_interview.interview_round}' for candidate {candidate_name} has been cancelled.{reason_part}",
                        notification_type="interview_cancelled",
                        sender_user_id=admin_id,
                        sender_type="hr"
                    )
                    
                    interviewer_mobile = getattr(interviewer, "mobile", None)
                    if interviewer_mobile:
                        interview_service.send_admin_interview_cancel(
                            to=interviewer_mobile,
                            job_title=job.job_title,
                            candidate_name=candidate_name,
                            interview_round=job_interview.interview_round,
                            interview_date_time=date_str,
                            cancel_reason=form_data.cancelled_reason or "N/A"
                        )
                
    except Exception as e:
        from app.core.logger import logger
        logger.error(f"Error creating interview cancelled notifications: {e}")

    return _serialize_job_interview(job_interview)


@router.patch("/{job_interview_id}/complete")
def complete_interview_route(
    job_interview_id: int,
    db: Session = Depends(get_db),
):
    """Marks an interview as completed."""
    job_interview = complete_interview(db=db, job_interview_id=job_interview_id)
    return _serialize_job_interview(job_interview)


@router.post("/{job_interview_id}/remarks")
def submit_interview_remarks_route(
    job_interview_id: int,
    form_data: InterviewRemarksRequest,
    db: Session = Depends(get_db),
    admin_id: int = Depends(get_current_admin_id)
):
    # Fetch the interview schedule to get the round name if not provided
    interview_schedule = db.query(JobInterviewSchedule).filter(
        JobInterviewSchedule.job_interview_id == job_interview_id
    ).first()
    
    round_val = form_data.round
    if not round_val and interview_schedule:
        round_val = interview_schedule.interview_round

    interview_remark = submit_interview_remarks(
        db=db,
        job_interview_id=job_interview_id,
        applicant_status=form_data.applicant_status,
        created_by=admin_id,
        round=round_val,
        remarks=form_data.remarks,
    )

    # Sync status outcome back to job_applicants table
    interview_schedule = db.query(JobInterviewSchedule).filter(
        JobInterviewSchedule.job_interview_id == job_interview_id
    ).first()
    if interview_schedule:
        interview_schedule.status = InterviewStatus.COMPLETED
        applicant = db.query(JobApplicant).filter(
            JobApplicant.job_applicant_id == interview_schedule.job_applicant_id
        ).first()
        if applicant:
            if form_data.applicant_status == ApplicantStatus.SELECTED:
                applicant.applicant_job_status = ApplicantJobStatus.SELECTED
                applicant.applicant_stage = ApplicantStage.OFFER
            elif form_data.applicant_status == ApplicantStatus.REJECTED:
                applicant.applicant_job_status = ApplicantJobStatus.REJECTED
            elif form_data.applicant_status == ApplicantStatus.HOLD:
                applicant.applicant_job_status = ApplicantJobStatus.HOLD
        
        # Extract fields to avoid detached instance issues after commit
        job_id_val = interview_schedule.job_id
        applicant_user_id_val = applicant.user_id if applicant else None
        
        db.commit()
        
        # Send Notifications
        try:
            from app.models import JobPost, Users, Admins
            from app.crud.notification_crud import notify_candidate, notify_school_admin
            
            job = db.query(JobPost).filter(JobPost.job_id == job_id_val).first()
            if applicant_user_id_val and job:
                candidate = db.query(Users).filter(Users.user_id == applicant_user_id_val).first()
                if candidate:
                    candidate_name = f"{candidate.first_name} {candidate.last_name}".strip()
                    status_str = form_data.applicant_status.value.lower() if hasattr(form_data.applicant_status, 'value') else str(form_data.applicant_status).lower()
                    
                    # 1. Notify Candidate
                    notify_candidate(
                        db=db,
                        candidate_id=candidate.user_id,
                        title="Application Status Update",
                        message=f"Your application status for '{job.job_title}' has been updated to {status_str}.",
                        notification_type="status_update",
                        sender_user_id=admin_id,
                        sender_type="hr"
                    )
                    
                    from app.services.interview_service import InterviewService
                    interview_service = InterviewService()
                    if getattr(candidate, "mobile", None):
                        interview_service.send_interview_feedback(
                            to=candidate.mobile,
                            candidate_name=candidate_name,
                            job_title=job.job_title,
                            status=status_str.capitalize(),
                            description=form_data.remarks or "N/A"
                        )
                    
                    # 2. Notify School Admin (interviewer)
                    interviewer_admin_id = None
                    if interview_schedule and interview_schedule.interviewer_name:
                        interviewer = db.query(Admins).filter(Admins.email == interview_schedule.interviewer_name).first()
                        if interviewer:
                            interviewer_admin_id = interviewer.admin_id
                    
                    if interviewer_admin_id:
                        if status_str == "selected":
                            admin_title = "Offer Letter Request"
                            admin_message = f"Candidate {candidate_name} has been selected for '{job.job_title}'. Please generate and issue an offer letter."
                            admin_type = "offer_request"
                        else:
                            admin_title = "Application Status Update"
                            admin_message = f"Application status for candidate {candidate_name} has been updated to {status_str}."
                            admin_type = "status_update"
                            
                        notify_school_admin(
                            db=db,
                            admin_id=interviewer_admin_id,
                            title=admin_title,
                            message=admin_message,
                            notification_type=admin_type,
                            sender_user_id=admin_id,
                            sender_type="hr"
                        )
                    
        except Exception as e:
            from app.core.logger import logger
            logger.error(f"Error creating status update notifications: {e}")

    return _serialize_interview_remark(interview_remark)


@router.get("/schedule-page")
def schedule_page():
    return serve_html_with_base("mss-career-portal/pages/hr/hr-interviewlist.html", "/mss-career-portal/pages/hr/")


@router.get("/feedback-page")
def feedback_page():
    return serve_html_with_base("mss-career-portal/pages/hr/hr-interview-feedback.html", "/mss-career-portal/pages/hr/")
