from datetime import datetime
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.logger import logger
from app.models import (
    ApplicantStatus,
    InterviewMode,
    InterviewRemark,
    InterviewStatus,
    JobInterviewSchedule,
)

def get_job_interview_or_404(db: Session, job_interview_id: int) -> JobInterviewSchedule:
    """Fetches a job interview schedule by its primary key or raises a 404."""
    job_interview = (
        db.query(JobInterviewSchedule)
        .filter(JobInterviewSchedule.job_interview_id == job_interview_id)
        .first()
    )
    if not job_interview:
        logger.warning(f"Job interview schedule not found: {job_interview_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job interview schedule not found.")
    return job_interview


def schedule_interview(
    db: Session,
    job_id: int,
    job_applicant_id: int,
    interview_round: str,
    scheduled_at: datetime,
    end_time_at: datetime,
    interview_mode: InterviewMode = InterviewMode.ONLINE,
    meeting_link: Optional[str] = None,
    location: Optional[str] = None,
    interviewer_name: Optional[str] = None,
    created_by: Optional[int] = None,
) -> JobInterviewSchedule:
    """Schedules a new interview round for a job applicant."""
    # Convert scheduled_at datetime to split date and time
    sch_date = scheduled_at.date()
    sch_time = scheduled_at.time()
    end_time_time = end_time_at.time()
    
    # address is NOT NULL in the database
    address_val = location if location else ""

    job_interview = JobInterviewSchedule(
        job_id=job_id,
        job_applicant_id=job_applicant_id,
        interview_round=interview_round,
        interview_mode=interview_mode,
        scheduled_date=sch_date,
        start_time=sch_time,
        end_time=end_time_time,
        meeting_link=meeting_link,
        location=location,
        address=address_val,
        interviewer_name=interviewer_name,
        status=InterviewStatus.SCHEDULED,
        created_by=created_by,
    )
    db.add(job_interview)
    db.commit()
    db.refresh(job_interview)

    from app.models.job_applicant_model import JobApplicant, ApplicantStage
    applicant = db.query(JobApplicant).filter(JobApplicant.job_applicant_id == job_applicant_id).first()
    if applicant:
        applicant.applicant_stage = ApplicantStage.INTERVIEW
        db.commit()

    logger.info(f"Interview scheduled: id={job_interview.job_interview_id} for applicant={job_applicant_id}")
    return job_interview


def update_interview(
    db: Session,
    job_interview_id: int,
    interview_round: Optional[str] = None,
    interview_mode: Optional[InterviewMode] = None,
    scheduled_at: Optional[datetime] = None,
    end_time_at: Optional[datetime] = None,
    meeting_link: Optional[str] = None,
    location: Optional[str] = None,
    interviewer_name: Optional[str] = None,
) -> JobInterviewSchedule:
    """Edits the details of an existing interview schedule."""
    job_interview = get_job_interview_or_404(db, job_interview_id)

    field_updates = {
        "interview_round": interview_round,
        "interview_mode": interview_mode,
        "meeting_link": meeting_link,
        "location": location,
        "interviewer_name": interviewer_name,
    }
    for field, value in field_updates.items():
        if value is not None:
            setattr(job_interview, field, value)

    if scheduled_at is not None:
        job_interview.scheduled_date = scheduled_at.date()
        job_interview.start_time = scheduled_at.time()
        
    if end_time_at is not None:
        job_interview.end_time = end_time_at.time()

    if location is not None:
        job_interview.address = location if location else ""

    db.commit()
    db.refresh(job_interview)
    logger.info(f"Interview updated: id={job_interview_id}")
    return job_interview


def reschedule_interview(
    db: Session,
    job_interview_id: int,
    scheduled_at: datetime,
    end_time_at: datetime,
    reschedule_reason: Optional[str] = None,
    rescheduled_by: Optional[int] = None,
    interviewer_name: Optional[str] = None,
) -> JobInterviewSchedule:
    """Reschedules an interview to a new date/time, keeping the previous slot for reference."""
    job_interview = get_job_interview_or_404(db, job_interview_id)
    # Store old scheduled date/time into rescheduled date/time
    job_interview.rescheduled_date = job_interview.scheduled_date
    job_interview.rescheduled_start_time = job_interview.start_time
    job_interview.rescheduled_end_time = job_interview.end_time
    
    # Store new scheduled date/time
    job_interview.scheduled_date = scheduled_at.date()
    job_interview.start_time = scheduled_at.time()
    job_interview.end_time = end_time_at.time()
    
    job_interview.reschedule_reason = reschedule_reason
    job_interview.rescheduled_by = rescheduled_by
    if interviewer_name is not None:
        job_interview.interviewer_name = interviewer_name
    job_interview.status = InterviewStatus.RESCHEDULED
    db.commit()
    db.refresh(job_interview)
    logger.info(f"Interview rescheduled: id={job_interview_id} to {scheduled_at}")
    return job_interview


def cancel_interview(
    db: Session,
    job_interview_id: int,
    cancelled_reason: Optional[str] = None,
) -> JobInterviewSchedule:
    """Cancels a scheduled interview."""
    job_interview = get_job_interview_or_404(db, job_interview_id)
    job_interview.status = InterviewStatus.CANCELLED
    job_interview.cancelled_reason = cancelled_reason
    db.commit()
    db.refresh(job_interview)
    logger.info(f"Interview cancelled: id={job_interview_id}")
    return job_interview


def complete_interview(db: Session, job_interview_id: int) -> JobInterviewSchedule:
    """Marks an interview as completed."""
    job_interview = get_job_interview_or_404(db, job_interview_id)
    job_interview.status = InterviewStatus.COMPLETED
    db.commit()
    db.refresh(job_interview)
    logger.info(f"Interview marked completed: id={job_interview_id}")
    return job_interview


def submit_interview_remarks(
    db: Session,
    job_interview_id: int,
    applicant_status: ApplicantStatus,
    created_by: int,
    round: Optional[str] = None,
    remarks: Optional[str] = None,
) -> InterviewRemark:
    """Creates or updates the remarks/result for an interview (one remark record per interview)."""
    interview = get_job_interview_or_404(db, job_interview_id)

    interview_remark = (
        db.query(InterviewRemark)
        .filter(InterviewRemark.job_interview_id == job_interview_id)
        .first()
    )

    if interview_remark:
        interview_remark.round = round
        interview_remark.remarks = remarks
        interview_remark.applicant_status = applicant_status
        interview_remark.updated_by = created_by
        logger.info(f"Interview remarks updated: job_interview_id={job_interview_id}")
    else:
        interview_remark = InterviewRemark(
            job_interview_id=job_interview_id,
            round=round,
            remarks=remarks,
            applicant_status=applicant_status,
            created_by=created_by,
        )
        db.add(interview_remark)
        logger.info(f"Interview remarks created: job_interview_id={job_interview_id}")

    db.commit()
    db.refresh(interview_remark)

    from app.models.job_applicant_model import JobApplicant, ApplicantJobStatus, ApplicantStage
    applicant = db.query(JobApplicant).filter(JobApplicant.job_applicant_id == interview.job_applicant_id).first()
    if applicant:
        applicant.applicant_job_status = ApplicantJobStatus(applicant_status.value)
        if applicant_status == ApplicantStatus.SELECTED:
            applicant.applicant_stage = ApplicantStage.OFFER
        db.commit()

    return interview_remark
