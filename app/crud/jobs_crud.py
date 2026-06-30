import secrets

import string

from datetime import date

from typing import Any, Dict, List, Optional


from fastapi import HTTPException, status

from sqlalchemy.orm import Session


from app.core.logger import logger

from app.models import JobPost, JobPreScreeningQuestion, JobStatus


def get_job_post_or_404(db: Session, job_id: int) -> JobPost:
    """Fetches a job post by its primary key or raises a 404."""

    job_post = db.query(JobPost).filter(JobPost.job_id == job_id).first()

    if not job_post:

        logger.warning(f"Job post not found: {job_id}")

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job post not found."
        )

    return job_post


def get_admin_job_posts(db: Session, admin_id: int) -> List[JobPost]:
    """Retrieves all job posts created by a specific admin (or all if HR)."""

    from app.models import Admins

    from sqlalchemy.orm import joinedload

    admin = (
        db.query(Admins)
        .options(joinedload(Admins.user_roles))
        .filter(Admins.admin_id == admin_id)
        .first()
    )

    if admin and admin.user_roles.role_name in {"hr_head", "hr_team", "hr_admin"}:

        return db.query(JobPost).all()

    return db.query(JobPost).filter(JobPost.job_posted_by == admin_id).all()


def get_published_job_posts(
    db: Session, school_name: Optional[str] = None
) -> List[JobPost]:
    """Retrieves all published job posts, for the public candidate-facing site."""

    query = db.query(JobPost).filter(JobPost.job_status == JobStatus.PUBLISH)

    if school_name:

        query = query.filter(JobPost.school_name == school_name)

    return query.order_by(JobPost.updated_at.desc()).all()


def get_published_job_post_or_404(db: Session, job_id: int) -> JobPost:
    """Fetches a single published job post by its primary key or raises a 404."""

    job_post = (
        db.query(JobPost)
        .filter(JobPost.job_id == job_id, JobPost.job_status == JobStatus.PUBLISH)
        .first()
    )

    if not job_post:

        logger.warning(f"Published job post not found: {job_id}")

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job post not found."
        )

    if not job_post.views:
        job_post.views = 0
    else:
        try:
            job_post.views = int(job_post.views)
        except ValueError:
            job_post.views = 0

    db.refresh(job_post)

    return job_post


def create_job_post(
    db: Session,
    job_posted_by: int,
    closing_date: Optional[date] = None,
    job_title: Optional[str] = None,
    department: Optional[str] = None,
    job_type: Optional[str] = None,
    vacancy_count: Optional[int] = None,
    school_name: Optional[str] = None,
    location: Optional[str] = None,
    programme: Optional[str] = None,
    min_exp: Optional[str] = None,
    max_exp: Optional[str] = None,
    job_description: Optional[str] = None,
    skills_required: Optional[str] = None,
    education_qualification: Optional[str] = None,
    additional_requirements: Optional[str] = None,
    job_status: JobStatus = JobStatus.PUBLISH,
    pre_screening_questions: Optional[List[Dict[str, Any]]] = None,
) -> JobPost:
    """Creates a new job post with a generated unique job ID and optional pre-screening questions."""

    job_post = JobPost(
        job_posted_by=job_posted_by,
        job_title=job_title,
        department=department,
        job_type=job_type,
        vacancy_count=vacancy_count,
        school_name=school_name,
        location=location,
        programme=programme,
        min_exp=min_exp,
        max_exp=max_exp,
        closing_date=closing_date,
        job_description=job_description,
        skills_required=skills_required,
        education_qualification=education_qualification,
        additional_requirements=additional_requirements,
        job_status=job_status,
    )

    if pre_screening_questions:

        job_post.job_pre_screening_questions = [
            JobPreScreeningQuestion(**question) for question in pre_screening_questions
        ]

    db.add(job_post)

    db.commit()

    db.refresh(job_post)

    logger.info(f"Job post created by admin {job_posted_by}")

    return job_post


def update_job_post(
    db: Session,
    job_id: int,
    job_title: Optional[str] = None,
    department: Optional[str] = None,
    job_type: Optional[str] = None,
    vacancy_count: Optional[int] = None,
    school_name: Optional[str] = None,
    location: Optional[str] = None,
    programme: Optional[str] = None,
    min_exp: Optional[str] = None,
    max_exp: Optional[str] = None,
    closing_date: Optional[date] = None,
    job_description: Optional[str] = None,
    skills_required: Optional[str] = None,
    education_qualification: Optional[str] = None,
    additional_requirements: Optional[str] = None,
    job_status: Optional[JobStatus] = None,
    pre_screening_questions: Optional[List[Dict[str, Any]]] = None,
) -> JobPost:
    """Edits an existing job post's fields, replacing its pre-screening questions if provided."""

    job_post = get_job_post_or_404(db, job_id)

    field_updates = {
        "job_title": job_title,
        "department": department,
        "job_type": job_type,
        "vacancy_count": vacancy_count,
        "school_name": school_name,
        "location": location,
        "programme": programme,
        "min_exp": min_exp,
        "max_exp": max_exp,
        "closing_date": closing_date,
        "job_description": job_description,
        "skills_required": skills_required,
        "education_qualification": education_qualification,
        "additional_requirements": additional_requirements,
        "job_status": job_status,
    }

    for field, value in field_updates.items():

        if value is not None:

            setattr(job_post, field, value)

    if pre_screening_questions is not None:

        db.query(JobPreScreeningQuestion).filter(
            JobPreScreeningQuestion.job_id == job_id
        ).delete()

        for question in pre_screening_questions:

            db.add(JobPreScreeningQuestion(job_id=job_id, **question))

    db.commit()

    db.refresh(job_post)

    return job_post


def update_job_status(db: Session, job_id: int, job_status: JobStatus) -> JobPost:
    """Sets a job post's status, used to mark a job post as closed or as a draft."""

    job_post = get_job_post_or_404(db, job_id)

    job_post.job_status = job_status

    if job_status == JobStatus.CLOSED:

        job_post.closing_date = date.today()

    db.commit()

    db.refresh(job_post)

    return job_post


def clone_job_post(
    db: Session, job_id: int, admin_id: int, publish: bool = False
) -> JobPost:
    """Clones an existing job post, copying its details and pre-screening questions."""

    original_job = get_job_post_or_404(db, job_id)

    cloned_job = JobPost(
        job_posted_by=admin_id,
        job_title=original_job.job_title,
        job_type=original_job.job_type,
        job_description=original_job.job_description,
        school_name=original_job.school_name,
        location=original_job.location,
        programme=original_job.programme,
        department=original_job.department,
        vacancy_count=original_job.vacancy_count,
        min_exp=original_job.min_exp,
        max_exp=original_job.max_exp,
        skills_required=original_job.skills_required,
        education_qualification=original_job.education_qualification,
        closing_date=original_job.closing_date,
        additional_requirements=original_job.additional_requirements,
        job_status=JobStatus.PUBLISH if publish else JobStatus.DRAFT,
    )

    db.add(cloned_job)

    db.flush()

    # Clone pre-screening questions

    original_questions = (
        db.query(JobPreScreeningQuestion)
        .filter(JobPreScreeningQuestion.job_id == job_id)
        .all()
    )

    for q in original_questions:

        cloned_q = JobPreScreeningQuestion(
            job_id=cloned_job.job_id,
            question_text=q.question_text,
            question_type=q.question_type,
            options=q.options,
            expected_answer=q.expected_answer,
        )

        db.add(cloned_q)

    db.commit()

    db.refresh(cloned_job)

    return cloned_job


def get_job_prescreening_questions(
    db: Session, job_id: int
) -> List[JobPreScreeningQuestion]:
    """Retrieves all pre-screening questions for a specific job post."""

    return (
        db.query(JobPreScreeningQuestion)
        .filter(JobPreScreeningQuestion.job_id == job_id)
        .all()
    )
