from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from app.core.html_helper import serve_html_with_base
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.routes.interview_auth_route import get_current_admin_id
from app.crud.school_admin_crud import (
    get_school_dashboard,
    get_school_jobs,
    get_school_job_detail,
    get_school_applicants,
    get_school_offers,
    issue_offer,
    update_offer_status,
)

router = APIRouter(prefix="/school", tags=["School Admin"])


@router.get("/dashboard")
def school_dashboard(
    db: Session = Depends(get_db),
    admin_id: int = Depends(get_current_admin_id),
):
    return get_school_dashboard(db, admin_id)


@router.get("/jobs")
def school_jobs(
    db: Session = Depends(get_db),
    admin_id: int = Depends(get_current_admin_id),
):
    jobs = get_school_jobs(db, admin_id)
    return {"jobs": jobs}


@router.get("/jobs/{job_id}")
def school_job_detail(
    job_id: int,
    db: Session = Depends(get_db),
    admin_id: int = Depends(get_current_admin_id),
):
    job = get_school_job_detail(db, admin_id, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.get("/applicants")
def school_applicants(
    db: Session = Depends(get_db),
    admin_id: int = Depends(get_current_admin_id),
):
    applicants = get_school_applicants(db, admin_id)
    return {"applicants": applicants}


@router.get("/offers")
def school_offers(
    db: Session = Depends(get_db),
    admin_id: int = Depends(get_current_admin_id),
):
    offers = get_school_offers(db, admin_id)
    return {"candidates": offers}


class IssueOfferPayload(BaseModel):
    offered_salary: Optional[str] = None
    joining_date: Optional[date] = None
    probation_period: Optional[str] = None
    offer_issued_date: Optional[date] = None
    offer_expiry_date: Optional[date] = None
    offer_remarks: Optional[str] = None
    offer_template: Optional[str] = "standard"
    offer_letter_doc: Optional[str] = None


@router.post("/offers/{applicant_id}/issue")
def issue_offer_route(
    applicant_id: int,
    payload: IssueOfferPayload,
    db: Session = Depends(get_db),
    admin_id: int = Depends(get_current_admin_id),
):
    result = issue_offer(db, admin_id, applicant_id, payload.dict())
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


class UpdateOfferStatusPayload(BaseModel):
    status: str


@router.patch("/offers/{applicant_id}/update-status")
def update_offer_status_route(
    applicant_id: int,
    payload: UpdateOfferStatusPayload,
    db: Session = Depends(get_db),
    admin_id: int = Depends(get_current_admin_id),
):
    result = update_offer_status(db, admin_id, applicant_id, payload.status)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.get("/sidebar-counts")
def sidebar_counts(
    db: Session = Depends(get_db),
    admin_id: int = Depends(get_current_admin_id),
):
    from app.crud.school_admin_crud import get_school_sidebar_counts
    return get_school_sidebar_counts(db, admin_id)


@router.get("/dashboard-page")
def dashboard_page():
    return serve_html_with_base("mss-career-portal/pages/school/schooladmin-dashboard.html", "/mss-career-portal/pages/school/")


@router.get("/jobs-page")
def jobs_page():
    return serve_html_with_base("mss-career-portal/pages/school/schooladmin-jobposts.html", "/mss-career-portal/pages/school/")


@router.get("/job-detail-page")
def job_detail_page():
    return serve_html_with_base("mss-career-portal/pages/school/schooladmin-jobpostdetails.html", "/mss-career-portal/pages/school/")


@router.get("/applicants-page")
def applicants_page():
    return serve_html_with_base("mss-career-portal/pages/school/schooladmin-jobapplicants-list.html", "/mss-career-portal/pages/school/")


@router.get("/offers-page")
def offers_page():
    return serve_html_with_base("mss-career-portal/pages/school/schooladmin-offermanagement.html", "/mss-career-portal/pages/school/")
