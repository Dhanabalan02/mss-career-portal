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
    "rejected": "Rejected",
}


def compute_stage(app, has_interview: bool) -> str:
    from app.models.job_applicant_model import ApplicantJobStatus, OfferAcceptanceStatus

    # 1. Deterministic definitive statuses take highest precedence
    # If a candidate is synced to Masset, they are onboarding.
    if app.sync_masset:
        return 'Onboarding'
        
    # If the candidate accepted the offer, they are in Offer Accepted stage.
    offer_status_val = app.offer_acceptance_status.value if hasattr(app.offer_acceptance_status, 'value') else str(app.offer_acceptance_status)
    if offer_status_val == "accepted":
        return 'Offer Accepted'
        
    # If the candidate is rejected, they are Rejected.
    job_status_val = app.applicant_job_status.value if hasattr(app.applicant_job_status, 'value') else str(app.applicant_job_status)
    if job_status_val == "rejected":
        return 'Rejected'

    # 2. Prefer the explicit ATS stage column when present and not overridden by definitive statuses
    if app.applicant_stage is not None:
        stage_val = app.applicant_stage.value if hasattr(app.applicant_stage, 'value') else str(app.applicant_stage)
        stage_val_norm = stage_val.lower().strip().replace(" ", "_").replace("-", "_")
        return _STAGE_ENUM_TO_LABEL.get(stage_val_norm, 'Applied')

    # 3. Fallback: derive stage from legacy fields
    if offer_status_val in ("expired", "rejected"):
        return 'Offer'
    if app.issue_offer:
        return 'Offer'
    if has_interview or job_status_val == "next_round":
        return 'Interview'
    if job_status_val in ("selected", "hold"):
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

