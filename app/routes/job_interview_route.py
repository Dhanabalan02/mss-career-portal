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
    InterviewStatus
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


@router.post("/")
def schedule_interview_route(
    form_data: InterviewScheduleRequest,
    db: Session = Depends(get_db),
    admin_id: int = Depends(get_current_admin_id)
):
    """Schedules a new interview round for a job applicant."""
    # Parse scheduled_at — strip trailing Z / offset for naive datetime
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
    )
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
    return _serialize_job_interview(job_interview)


@router.patch("/{job_interview_id}/complete")
def complete_interview_route(
    job_interview_id: int,
    db: Session = Depends(get_db),
    admin_id: int = Depends(get_current_admin_id)
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
    """Submits or updates the remarks/result for an interview."""
    interview_remark = submit_interview_remarks(
        db=db,
        job_interview_id=job_interview_id,
        applicant_status=form_data.applicant_status,
        created_by=admin_id,
        round=form_data.round,
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
            elif form_data.applicant_status == ApplicantStatus.REJECTED:
                applicant.applicant_job_status = ApplicantJobStatus.REJECTED
            elif form_data.applicant_status == ApplicantStatus.HOLD:
                applicant.applicant_job_status = ApplicantJobStatus.HOLD
        db.commit()

    return _serialize_interview_remark(interview_remark)


@router.get("/schedule-page")
def schedule_page():
    return serve_html_with_base("mss-career-portal/pages/hr/hr-interviewlist.html", "/mss-career-portal/pages/hr/")


@router.get("/feedback-page")
def feedback_page():
    return serve_html_with_base("mss-career-portal/pages/hr/hr-interview-feedback.html", "/mss-career-portal/pages/hr/")
