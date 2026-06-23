import json
from datetime import date
from typing import List, Optional

COLORS = [
    ['#dbeafe', '#1d4ed8'],
    ['#dcfce7', '#15803d'],
    ['#fef3c7', '#b45309'],
    ['#ede9fe', '#6d28d9'],
    ['#ffedd5', '#c2410c'],
    ['#ccfbf1', '#0f766e'],
]

AV_CLASSES = ['av-blue', 'av-green', 'av-amber', 'av-purple', 'av-red']


def get_initials(first: Optional[str], last: Optional[str]) -> str:
    parts = []
    if first:
        parts.append(first[0].upper())
    if last:
        parts.append(last[0].upper())
    return ''.join(parts[:2]) or '?'


def get_color(idx: int) -> List[str]:
    return COLORS[idx % len(COLORS)]


def get_av_class(idx: int) -> str:
    return AV_CLASSES[idx % len(AV_CLASSES)]


def parse_skills(skills_str: Optional[str]) -> List[str]:
    if not skills_str:
        return []
    try:
        parsed = json.loads(skills_str)
        if isinstance(parsed, list):
            return [str(s).strip() for s in parsed if s]
    except (json.JSONDecodeError, ValueError):
        pass
    return [s.strip() for s in skills_str.split(',') if s.strip()]


def compute_exp_str(experiences, meta_exp: Optional[str] = None) -> str:
    if meta_exp:
        return meta_exp
    total_years = 0.0
    for exp in experiences:
        if getattr(exp, "total_experience", None):
            import re
            match = re.search(r"[\d\.]+", exp.total_experience)
            if match:
                try:
                    total_years += float(match.group())
                except ValueError:
                    pass
                    
    if total_years > 0:
        return f"{round(total_years, 1)} yrs"
    return "—"


_STAGE_ENUM_TO_LABEL = {
    "applied": "Applied",
    "screened": "Screened",
    "interview": "Interview",
    "offer": "Offer",
    "offer_accepted": "Offer Accepted",
    "onboarding": "Onboarding",
}


def compute_stage(app, has_interview: bool) -> str:
    from app.models.job_applicant_model import ApplicantJobStatus, OfferAcceptanceStatus

    # Prefer the explicit ATS stage column when present
    if app.applicant_stage is not None:
        stage_val = app.applicant_stage.value if hasattr(app.applicant_stage, 'value') else str(app.applicant_stage)
        return _STAGE_ENUM_TO_LABEL.get(stage_val, 'Applied')

    # Fallback: derive stage from legacy fields (for existing rows without applicant_stage)
    status = app.applicant_job_status
    if status == ApplicantJobStatus.REJECTED:
        return 'Rejected'
    if app.sync_masset:
        return 'Onboarding'
    if app.offer_acceptance_status == OfferAcceptanceStatus.ACCEPTED:
        return 'Offer Accepted'
    if app.offer_acceptance_status in (OfferAcceptanceStatus.EXPIRED, OfferAcceptanceStatus.REJECTED):
        return 'Offer'
    if app.issue_offer:
        return 'Offer'
    if has_interview or status == ApplicantJobStatus.NEXT_ROUND:
        return 'Interview'
    if status in (ApplicantJobStatus.SELECTED, ApplicantJobStatus.HOLD):
        return 'Screened'
    return 'Applied'


def compute_offer_status(app) -> str:
    from app.models.job_applicant_model import ApplicantJobStatus, OfferAcceptanceStatus
    if app.offer_acceptance_status == OfferAcceptanceStatus.ACCEPTED:
        return 'accepted'
    if app.offer_acceptance_status == OfferAcceptanceStatus.EXPIRED:
        return 'expired'
    if app.issue_offer:
        return 'sent'
    if app.applicant_job_status == ApplicantJobStatus.SELECTED:
        return 'awaiting'
    return 'awaiting'

def check_and_close_job_if_filled(db, job_id: int):
    from app.models.job_post_model import JobPost
    from app.models.job_applicant_model import JobApplicant, OfferAcceptanceStatus
    
    job = db.query(JobPost).filter(JobPost.job_id == job_id).first()
    if not job or job.job_status != "publish":
        return
        
    hired_count = db.query(JobApplicant).filter(
        JobApplicant.job_id == job_id,
        JobApplicant.offer_acceptance_status == OfferAcceptanceStatus.ACCEPTED
    ).count()
    
    if hired_count >= job.vacancy_count:
        job.job_status = "closed"
        db.commit()

