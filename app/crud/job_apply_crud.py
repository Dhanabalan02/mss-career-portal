from typing import List, Optional
from sqlalchemy.orm import Session
from app.models import JobApplicant, CandidateScreeningAnswer, JobPreScreeningQuestion
from app.models.candidate_screening_answer_model import CandidateStatus
from app.models.job_applicant_model import ApplicantJobStatus, ApplicantStage, OfferAcceptanceStatus
from app.core.logger import logger

from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.user_model import Users

def create_job_application(
    db: Session,
    user_id: int,
    job_id: int,
    mobile: Optional[str] = None,  # Added mobile parameter
    resume_doc: Optional[str] = None,
    cover_letter: Optional[str] = None,
    screening_answers: Optional[List[dict]] = None
) -> JobApplicant:
    """Creates a new job application record and backfills the user's mobile number if missing."""
    
    # --- 1. Check and Update User Mobile Number ---
    if mobile:
        user = db.query(Users).filter(Users.user_id == user_id).first()
        # Update only if the user exists and doesn't already have a mobile number
        if user and not user.mobile:
            user.mobile = mobile
            db.add(user) # Schedules the user record for update

    # --- 2. Create Job Application ---
    db_applicant = JobApplicant(
        job_id=job_id,
        user_id=user_id,
        resume_doc=resume_doc,
        cover_letter=cover_letter,
        applicant_job_status=None,
        offer_acceptance_status=OfferAcceptanceStatus.PENDING,
        applicant_stage=None,
        mss_app_no="TEMP"
    )
    db.add(db_applicant)
    db.flush() # Forces the DB to generate the job_applicant_id before committing

    # Generate and assign the unique application number
    db_applicant.mss_app_no = f"MSS-APP-{db_applicant.job_applicant_id}"

    # --- 3. Process Screening Answers ---
    if screening_answers:
        questions = db.query(JobPreScreeningQuestion).filter(JobPreScreeningQuestion.job_id == job_id).all()
        expected_map = {q.question_id: (q.expected_answer or "").strip().lower() for q in questions if q.expected_answer}
        
        total_qs = len(questions)
        correct_count = 0
        
        if total_qs > 0:
            for ans in screening_answers:
                q_id = ans.get("question_id")
                answer_text = (ans.get("answer") or "").strip().lower()
                expected = expected_map.get(q_id)
                if expected and answer_text == expected:
                    correct_count += 1
                    
            score = (correct_count / total_qs) * 100
            if score == 100:
                final_status = CandidateStatus.SCREENED
                db_applicant.applicant_stage = ApplicantStage.SCREENED
            else:
                final_status = CandidateStatus.INELIGIBLE
                db_applicant.applicant_stage = ApplicantStage.PRESCREEN_REJECT
                db_applicant.applicant_job_status = ApplicantJobStatus.REJECTED
        else:
            final_status = CandidateStatus.SCREENED
            db_applicant.applicant_stage = ApplicantStage.SCREENED

        for ans in screening_answers:
            q_id = ans.get("question_id")
            answer_text = ans.get("answer")
            db_answer = CandidateScreeningAnswer(
                candidate_id=user_id,
                job_id=job_id,
                question_id=q_id,
                answer=answer_text,
                candidate_status=final_status
            )
            db.add(db_answer)

    # Commits both the job application and the updated user mobile record atomically
    db.commit()
    db.refresh(db_applicant)
    
    logger.info(f"Job application created: applicant_id={db_applicant.job_applicant_id}, mss_app_no={db_applicant.mss_app_no}, job_id={job_id}, user_id={user_id}")
    return db_applicant

def get_candidate_applications(db: Session, user_id: int) -> List[JobApplicant]:
    """Retrieves all job applications submitted by a specific candidate."""
    return db.query(JobApplicant).filter(JobApplicant.user_id == user_id).all()

def get_job_application(db: Session, job_applicant_id: int) -> Optional[JobApplicant]:
    """Retrieves a single job application by its ID."""
    return db.query(JobApplicant).filter(JobApplicant.job_applicant_id == job_applicant_id).first()

def check_already_applied(db: Session, user_id: int, job_id: int) -> Optional[JobApplicant]:
    """Returns the JobApplicant if the candidate has already applied to this specific job."""
    return db.query(JobApplicant).filter(
        JobApplicant.user_id == user_id,
        JobApplicant.job_id == job_id
    ).first()

def respond_to_offer(db: Session, user_id: int, job_id: int, status_str: str) -> bool:
    app = db.query(JobApplicant).filter(
        JobApplicant.user_id == user_id,
        JobApplicant.job_id == job_id
    ).first()
    if not app:
        return False
    
    if status_str.lower() == 'accepted':
        app.offer_acceptance_status = OfferAcceptanceStatus.ACCEPTED
    elif status_str.lower() == 'rejected':
        app.offer_acceptance_status = OfferAcceptanceStatus.REJECTED
    else:
        return False
    
    db.commit()
    
    if status_str.lower() == 'accepted':
        from app.crud.common import check_and_close_job_if_filled
        check_and_close_job_if_filled(db, job_id)
        
    return True
