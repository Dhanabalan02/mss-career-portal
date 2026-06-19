from typing import List, Optional
from sqlalchemy.orm import Session
from app.models import JobApplicant, CandidateScreeningAnswer, JobPreScreeningQuestion
from app.models.candidate_screening_answer_model import CandidateStatus
from app.models.job_applicant_model import ApplicantJobStatus, OfferAcceptanceStatus
from app.core.logger import logger

def create_job_application(
    db: Session,
    user_id: int,
    job_id: int,
    resume_doc: Optional[str] = None,
    cover_letter: Optional[str] = None,
    expected_salary: Optional[str] = None,
    screening_answers: Optional[List[dict]] = None
) -> JobApplicant:
    """Creates a new job application record for a candidate and saves their pre-screening answers."""
    db_applicant = JobApplicant(
        job_id=job_id,
        user_id=user_id,
        resume_doc=resume_doc,
        cover_letter=cover_letter,
        expected_salary=expected_salary,
        applicant_job_status=None,  # defaults to pending/None
        offer_acceptance_status=OfferAcceptanceStatus.PENDING
    )
    db.add(db_applicant)
    db.flush() # Forces the DB to generate the job_applicant_id before committing

    # Generate and assign the unique application number
    db_applicant.mss_app_no = f"MSS-APP-{db_applicant.job_applicant_id}"

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
            if score >= 60:
                final_status = CandidateStatus.SCREENED
            elif score >= 10:
                final_status = CandidateStatus.APPLIED
            else:
                final_status = CandidateStatus.INELIGIBLE
        else:
            final_status = CandidateStatus.APPLIED

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
    return True
