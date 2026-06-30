from typing import Optional
from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from app.core.html_helper import serve_html_with_base
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.routes.interview_auth_route import get_current_admin_id
from app.crud.hr_crud import (
    get_ats_candidates,
    update_candidate_stage,
    get_interviews,
    get_masset_candidates,
    sync_masset,
    get_hr_reports,
    get_pending_actions,
)

router = APIRouter(prefix="/hr", tags=["HR"])


@router.get("/ats-pipeline")
def ats_pipeline(
    db: Session = Depends(get_db),
    admin_id: int = Depends(get_current_admin_id),
):
    from datetime import datetime

    candidates = get_ats_candidates(db, admin_id)

    total_count = len(candidates)
    unique_jobs_count = len(set(c.get("job_id") for c in candidates if c.get("job_id")))

    interviewing_count = sum(1 for c in candidates if c.get("stage") == "Interview")
    interview_pct = (
        round((interviewing_count / total_count * 100), 1) if total_count > 0 else 0
    )

    offers_count = sum(
        1 for c in candidates if c.get("stage") in ["Offer", "Offer Accepted"]
    )
    accepted_count = sum(1 for c in candidates if c.get("stage") == "Offer Accepted")

    current_month = datetime.now().month
    current_year = datetime.now().year
    onboarding_this_month = 0
    for c in candidates:
        if c.get("stage") == "Onboarding":
            updated = c.get("updated_at")
            if (
                updated
                and updated.month == current_month
                and updated.year == current_year
            ):
                onboarding_this_month += 1

    # Remove updated_at from serialization just to keep response clean (optional, but good practice)
    for c in candidates:
        c.pop("updated_at", None)

    stats = {
        "total": total_count,
        "interview": interviewing_count,
        "offers": offers_count,
        "onboarding": sum(1 for c in candidates if c.get("stage") == "Onboarding"),
        "deltas": {
            "total": f"Across {unique_jobs_count} position{'s' if unique_jobs_count != 1 else ''}",
            "interview": f"{interview_pct}% of pipeline",
            "offers": f"{accepted_count} accepted so far",
            "onboarding": f"{onboarding_this_month} active this month",
        },
    }

    return {"candidates": candidates, "stats": stats}


class StageUpdateRequest(BaseModel):
    stage: str
    remarks: Optional[str] = None


@router.patch("/ats-pipeline/{applicant_id}/stage")
def update_ats_stage(
    applicant_id: int,
    payload: StageUpdateRequest,
    db: Session = Depends(get_db),
    admin_id: int = Depends(get_current_admin_id),
):
    return update_candidate_stage(db, admin_id, applicant_id, payload.stage, payload.remarks)


@router.get("/interviews")
def interview_list(
    db: Session = Depends(get_db),
    admin_id: int = Depends(get_current_admin_id),
):
    return get_interviews(db, admin_id)


@router.get("/reports")
def hr_reports(
    db: Session = Depends(get_db),
    admin_id: int = Depends(get_current_admin_id),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    school_name: Optional[str] = None,
    department: Optional[str] = None,
    job_type: Optional[str] = None,
):
    return get_hr_reports(
        db,
        admin_id,
        start_date=start_date,
        end_date=end_date,
        school_name=school_name,
        department=department,
        job_type=job_type,
    )


@router.get("/masset/candidates")
def masset_candidates(
    db: Session = Depends(get_db),
    admin_id: int = Depends(get_current_admin_id),
):
    candidates = get_masset_candidates(db, admin_id)
    return {"candidates": candidates}


@router.get("/masset/stats")
def masset_stats(
    db: Session = Depends(get_db),
    admin_id: int = Depends(get_current_admin_id),
):
    from app.crud.hr_crud import get_masset_stats

    stats = get_masset_stats(db, admin_id)
    return stats


class MassetSyncRequest(BaseModel):
    employee_id: Optional[str] = None


@router.patch("/masset/{applicant_id}/sync")
def masset_sync(
    applicant_id: int,
    payload: MassetSyncRequest = MassetSyncRequest(),
    db: Session = Depends(get_db),
    admin_id: int = Depends(get_current_admin_id),
):
    result = sync_masset(db, admin_id, applicant_id, payload.employee_id or "")
    return result


@router.get("/pending-actions")
def pending_actions(
    db: Session = Depends(get_db),
    admin_id: int = Depends(get_current_admin_id),
):
    return get_pending_actions(db, admin_id)


class MassetWebhookRequest(BaseModel):
    masset_employee_id: str
    status: str
    message: Optional[str] = None


@router.post("/masset/webhook")
def masset_webhook(payload: MassetWebhookRequest, db: Session = Depends(get_db)):
    """
    Webhook endpoint for MASSET external HRMS to update candidate status
    based on masset_employee_id.
    """
    from app.crud.hr_crud import update_masset_status_from_webhook

    return update_masset_status_from_webhook(
        db, payload.masset_employee_id, payload.status
    )


@router.get("/sidebar-counts")
def sidebar_counts(
    db: Session = Depends(get_db),
    admin_id: int = Depends(get_current_admin_id),
):
    from app.crud.hr_crud import get_sidebar_counts

    return get_sidebar_counts(db, admin_id)


@router.get("/dashboard-page")
def dashboard_page():
    return serve_html_with_base(
        "mss-career-portal/pages/hr/hr-dashboard.html", "/mss-career-portal/pages/hr/"
    )


@router.get("/ats-pipeline-page")
def ats_pipeline_page():
    return serve_html_with_base(
        "mss-career-portal/pages/hr/hr-atspipeline.html", "/mss-career-portal/pages/hr/"
    )


@router.get("/interviews-page")
def interviews_page():
    return serve_html_with_base(
        "mss-career-portal/pages/hr/hr-interviewlist.html",
        "/mss-career-portal/pages/hr/",
    )


@router.get("/reports-page")
def reports_page():
    return serve_html_with_base(
        "mss-career-portal/pages/hr/hr-reports.html", "/mss-career-portal/pages/hr/"
    )


@router.get("/masset-candidates-page")
def masset_candidates_page():
    return serve_html_with_base(
        "mss-career-portal/pages/hr/masset-sync-dashboard.html",
        "/mss-career-portal/pages/hr/",
    )
