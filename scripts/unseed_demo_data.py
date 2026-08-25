"""
Removes the demo data created by `scripts/seed_demo_data.py`, and nothing else.

Safety: reads the exact job_id/user_id list from `scripts/demo_data_manifest.json`
(written by the seed script) and, as a second independent check, only deletes a
Users row if its email still ends with `@demo.careerportal.local` and only
deletes a JobPost row if its job_id is in the manifest. Nothing outside those
two checks is touched — nothing is inferred or guessed.

Usage:
    python -m scripts.unseed_demo_data
"""

import json
import sys

sys.path.insert(0, ".")

from app.core.database import SessionLocal
from app.models import (
    Users,
    JobPost,
    JobApplicant,
    JobInterviewSchedule,
    InterviewRemark,
    JobOffer,
    JobPreScreeningQuestion,
    CandidateMetadata,
    CandidateExperience,
    CandidateEducationDetail,
)

DEMO_EMAIL_DOMAIN = "demo.careerportal.local"
MANIFEST_PATH = "scripts/demo_data_manifest.json"


def main():
    with open(MANIFEST_PATH) as f:
        manifest = json.load(f)
    job_ids = manifest["job_ids"]
    user_ids = manifest["user_ids"]

    db = SessionLocal()
    try:
        # Re-verify against the manifest independently before deleting anything.
        safe_user_ids = [
            u.user_id
            for u in db.query(Users.user_id, Users.email)
            .filter(Users.user_id.in_(user_ids))
            .filter(Users.email.like(f"%@{DEMO_EMAIL_DOMAIN}"))
            .all()
        ]
        safe_job_ids = [
            j.job_id
            for j in db.query(JobPost.job_id).filter(JobPost.job_id.in_(job_ids)).all()
        ]

        applicant_ids = [
            a.job_applicant_id
            for a in db.query(JobApplicant.job_applicant_id)
            .filter(JobApplicant.user_id.in_(safe_user_ids))
            .all()
        ]
        interview_ids = [
            i.job_interview_id
            for i in db.query(JobInterviewSchedule.job_interview_id)
            .filter(JobInterviewSchedule.job_applicant_id.in_(applicant_ids))
            .all()
        ]

        n_offers = db.query(JobOffer).filter(JobOffer.job_applicant_id.in_(applicant_ids)).delete(synchronize_session=False)
        n_remarks = db.query(InterviewRemark).filter(InterviewRemark.job_interview_id.in_(interview_ids)).delete(synchronize_session=False)
        n_interviews = db.query(JobInterviewSchedule).filter(JobInterviewSchedule.job_applicant_id.in_(applicant_ids)).delete(synchronize_session=False)
        n_applicants = db.query(JobApplicant).filter(JobApplicant.job_applicant_id.in_(applicant_ids)).delete(synchronize_session=False)

        n_edu = db.query(CandidateEducationDetail).filter(CandidateEducationDetail.user_id.in_(safe_user_ids)).delete(synchronize_session=False)
        n_exp = db.query(CandidateExperience).filter(CandidateExperience.user_id.in_(safe_user_ids)).delete(synchronize_session=False)
        n_meta = db.query(CandidateMetadata).filter(CandidateMetadata.user_id.in_(safe_user_ids)).delete(synchronize_session=False)
        n_users = db.query(Users).filter(Users.user_id.in_(safe_user_ids)).delete(synchronize_session=False)

        n_questions = db.query(JobPreScreeningQuestion).filter(JobPreScreeningQuestion.job_id.in_(safe_job_ids)).delete(synchronize_session=False)
        n_jobs = db.query(JobPost).filter(JobPost.job_id.in_(safe_job_ids)).delete(synchronize_session=False)

        db.commit()

        print(f"Deleted: {n_jobs} job posts, {n_questions} pre-screening questions")
        print(f"Deleted: {n_applicants} applications, {n_interviews} interviews, "
              f"{n_remarks} interview remarks, {n_offers} offers")
        print(f"Deleted: {n_users} users, {n_meta} metadata rows, {n_exp} experience rows, {n_edu} education rows")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
