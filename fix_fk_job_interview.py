"""
One-time fix: the `fk_job_applicant_id` constraint on `job_interview_schedule`
incorrectly references `users(user_id)` instead of `job_applicants(job_applicant_id)`.
Run once: python fix_fk_job_interview.py
"""
from sqlalchemy import text
from app.core.database import engine

with engine.connect() as conn:
    conn.execute(text(
        "ALTER TABLE job_interview_schedule "
        "DROP FOREIGN KEY fk_job_applicant_id"
    ))
    conn.execute(text(
        "ALTER TABLE job_interview_schedule "
        "ADD CONSTRAINT fk_job_applicant_id "
        "FOREIGN KEY (job_applicant_id) "
        "REFERENCES job_applicants(job_applicant_id)"
    ))
    conn.commit()
    print("FK constraint fixed: job_interview_schedule.job_applicant_id -> job_applicants.job_applicant_id")
