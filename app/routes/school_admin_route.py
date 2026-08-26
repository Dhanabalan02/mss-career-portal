from datetime import date, datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Header
from app.core.html_helper import serve_html_with_base
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.logger import logger

from app.core.database import get_db
from app.routes.interview_auth_route import get_current_admin_id
from app.crud.school_admin_crud import (
    get_school_dashboard,
    get_school_jobs,
    get_school_job_detail,
    get_school_applicants,
    get_school_offers,
    update_offer_status,
)

router = APIRouter(prefix="/school", tags=["School Admin"])


class WebhookOfferUpdatePayload(BaseModel):
    phone: str
    status: str


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


@router.get("/jobs/{job_identifier}")
def school_job_detail(
    job_identifier: str,
    db: Session = Depends(get_db),
    admin_id: int = Depends(get_current_admin_id),
):
    if "-" in job_identifier:
        from app.models import JobPost

        job = db.query(JobPost).filter(JobPost.uuid == job_identifier).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        job_id = job.job_id
    else:
        try:
            job_id = int(job_identifier)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid job identifier")

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
    offer_issued_date: Optional[datetime] = None
    offer_expiry_date: Optional[date] = None
    offer_remarks: Optional[str] = None
    offer_template: Optional[str] = "standard"
    offer_letter_doc: Optional[str] = None
    is_draft: Optional[bool] = False


@router.post("/offers/{applicant_id}/issue")
def issue_offer_route(
    applicant_id: int,
    payload: IssueOfferPayload,
    db: Session = Depends(get_db),
    admin_id: int = Depends(get_current_admin_id),
):
    from app.crud.school_admin_crud import issue_offer

    result = issue_offer(db, admin_id, applicant_id, payload.dict(exclude_unset=True))
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    if not payload.is_draft:
        try:
            from app.models import JobApplicant, JobPost, Users
            from app.crud.notification_crud import notify_candidate

            app_record = (
                db.query(JobApplicant)
                .filter(JobApplicant.job_applicant_id == applicant_id)
                .first()
            )
            if app_record:
                job = (
                    db.query(JobPost)
                    .filter(JobPost.job_id == app_record.job_id)
                    .first()
                )
                candidate = (
                    db.query(Users).filter(Users.user_id == app_record.user_id).first()
                )

                if job and candidate:
                    from urllib.parse import quote

                    job_description_url = (
                        "/mss-career-portal/job-description?uuid="
                        f"{quote(str(job.uuid or ''), safe='')}"
                        f"&title={quote((job.job_title or '').replace(' ', '-'))}"
                        f"&unit={quote((job.school_name or '').replace(' ', '-'))}"
                    )
                    notify_candidate(
                        db=db,
                        candidate_id=candidate.user_id,
                        title="Offer Letter Issued",
                        message=f"Congratulations! You have received an offer for the position of '{job.job_title}'. Please log in to view the details.",
                        notification_type="offer_issued",
                        sender_user_id=admin_id,
                        sender_type="school_admin",
                        redirect_url=job_description_url,
                    )

                    # Call WhatsApp service
                    from app.core.logger import offer_logger

                    try:
                        offer_logger.info(
                            f"Initiating WhatsApp OfferService for candidate_id={candidate.user_id}"
                        )
                        from app.services.offer_service import OfferService

                        phone = candidate.mobile

                        candidate_name = getattr(
                            candidate,
                            "name",
                            getattr(candidate, "first_name", "Candidate"),
                        )

                        offer_logger.info(f"Candidate phone resolved to: {phone}")
                        if phone:
                            doc_url = result.get("offer_letter_doc_path")
                            if not doc_url:
                                offer_logger.warning(
                                    f"No offer document path for candidate {candidate.user_id}, skipping WhatsApp offer."
                                )
                            else:
                                doc_url = doc_url.replace("\\", "/")
                                if not doc_url.startswith(("http://", "https://")):
                                    base_url = (
                                        "https://stagecareer.themadrassevasadan.org"
                                    )
                                    doc_url = base_url + (
                                        doc_url
                                        if doc_url.startswith("/")
                                        else f"/{doc_url}"
                                    )

                                from urllib.parse import urlparse, quote

                                parsed = urlparse(doc_url)
                                doc_url = f"{parsed.scheme}://{parsed.netloc}{quote(parsed.path, safe='/')}"
                                if parsed.query:
                                    doc_url += f"?{parsed.query}"

                                offer_logger.info(
                                    f"Offer document URL: {doc_url}, Job Title: {job.job_title}"
                                )

                                response = OfferService().issue_offer(
                                    to=phone,
                                    candidate_name=candidate_name,
                                    job_title=job.job_title,
                                    document_url=doc_url,
                                )
                                offer_logger.info(
                                    f"OfferService response for candidate_id={candidate.user_id}: {response}"
                                )
                                if response.get("success"):
                                    offer_logger.info(
                                        "OfferService().issue_offer executed successfully"
                                    )
                                else:
                                    offer_logger.error(
                                        f"OfferService failed for candidate_id={candidate.user_id}. Details: {response}"
                                    )
                        else:
                            offer_logger.warning(
                                f"Candidate {candidate.user_id} has no phone number, WhatsApp offer skipped."
                            )
                    except Exception as e:
                        offer_logger.error(
                            f"Error calling WhatsApp service for candidate_id={candidate.user_id}: {e}",
                            exc_info=True,
                        )
        except Exception as e:
            logger.error(
                f"Error creating notification for issued offer: {e}", exc_info=True
            )

    return result


@router.patch("/offers/update-by-webhook")
def update_offer_status_via_webhook(
    payload: WebhookOfferUpdatePayload,  # Use a small payload container (phone + status)
    x_webhook_token: str = Header(None),
    db: Session = Depends(get_db),
):
    # Verify the incoming webhook request is authentic
    if not x_webhook_token or x_webhook_token != "admin@123":
        raise HTTPException(status_code=401, detail="Unauthorized webhook client")

    # 1. Look up the latest active job applicant using their phone number
    from app.models import Users, JobApplicant

    phone_clean = payload.phone.lstrip("+")

    if phone_clean.startswith("91") and len(phone_clean) > 10:
        phone_clean = phone_clean[-10:]  # keep last 10 digits

    candidate = (
        db.query(Users)
        .filter(Users.mobile.contains(phone_clean))
        .first()
    )

    if not candidate:
       raise HTTPException(status_code=404, detail="Candidate not found by phone reference")

    app = (
        db.query(JobApplicant)
        .filter(JobApplicant.user_id == candidate.user_id)
        .order_by(JobApplicant.job_applicant_id.desc())
        .first()
    )  # Gets latest open application

    if not app:
       raise HTTPException(status_code=404, detail="No active application found for candidate")

    # 2. Update the candidate response in career db directly, without using the internal application logic
    from app.models.job_applicant_model import OfferAcceptanceStatus

    status_map = {
        "accepted": OfferAcceptanceStatus.ACCEPTED,
        "rejected": OfferAcceptanceStatus.REJECTED,
    }
    new_status = status_map.get(payload.status.lower())
    if not new_status:
        raise HTTPException(status_code=400, detail=f"Unknown status: {payload.status}")

    app.offer_acceptance_status = new_status
    if new_status == OfferAcceptanceStatus.ACCEPTED:
        from app.models.job_applicant_model import ApplicantStage
        from app.core.timezone import utcnow

        app.applicant_stage = ApplicantStage.OFFER_ACCEPTED
        app.offer_accepted_on = utcnow()
    db.commit()
    # --- Your Notification Dispatch Logic Stays Exactly The Same ---
    try:
        from app.models import JobPost
        from app.crud.notification_crud import (
            notify_hr_users,
            notify_school_admins_for_unit,
            build_candidate_profile_redirect_url,
        )

        job = db.query(JobPost).filter(JobPost.job_id == app.job_id).first()
        if job:
            candidate_name = f"{candidate.first_name} {candidate.last_name}".strip()
            status_cap = payload.status.capitalize()

            notify_hr_users(
                db=db,
                title=f"Offer {status_cap}",
                message=f"Offer status for candidate {candidate_name} ('{job.job_title}') has been updated to '{payload.status}' via WhatsApp.",
                notification_type=f"offer_status_{payload.status.lower()}",
                sender_user_id=candidate.user_id,
                sender_type="candidate",
                redirect_url="/mss-career-portal/hr/masset-candidates"
            )
            notify_school_admins_for_unit(
                db=db,
                unit_name=job.school_name,
                title=f"Offer {status_cap}",
                message=f"Offer status for candidate {candidate_name} ('{job.job_title}') has been updated to '{payload.status}' via WhatsApp.",
                notification_type=f"offer_status_{payload.status.lower()}",
                sender_user_id=candidate.user_id,
                sender_type="candidate",
                redirect_url=build_candidate_profile_redirect_url(
                    "schoolAdmin", app.job_applicant_id, candidate_name, job.job_title
                ),
            )
    except Exception as e:
        logger.error(f"Error creating notification events: {e}")

    return {"success": True, "updated_status": payload.status}


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

    # Send Notifications
    try:
        from app.models import JobApplicant, JobPost, Users
        from app.crud.notification_crud import notify_hr_users, notify_school_admins, build_candidate_profile_redirect_url

        app = (
            db.query(JobApplicant)
            .filter(JobApplicant.job_applicant_id == applicant_id)
            .first()
        )
        if app:
            job = db.query(JobPost).filter(JobPost.job_id == app.job_id).first()
            candidate = db.query(Users).filter(Users.user_id == app.user_id).first()
            if job and candidate:
                candidate_name = f"{candidate.first_name} {candidate.last_name}".strip()
                status_cap = payload.status.capitalize()

                # 1. Notify HR Users
                notify_hr_users(
                    db=db,
                    title=f"Offer {status_cap}",
                    message=f"Offer status for candidate {candidate_name} ('{job.job_title}') has been updated to '{payload.status}'.",
                    notification_type=f"offer_status_{payload.status.lower()}",
                    sender_user_id=candidate.user_id,
                    sender_type="candidate",
                    redirect_url="/mss-career-portal/hr/masset-candidates"
                )

                # 2. Notify School Admins
                notify_school_admins(
                    db=db,
                    title=f"Offer {status_cap}",
                    message=f"Offer status for candidate {candidate_name} ('{job.job_title}') has been updated to '{payload.status}'.",
                    notification_type=f"offer_status_{payload.status.lower()}",
                    sender_user_id=candidate.user_id,
                    sender_type="candidate",
                    redirect_url=build_candidate_profile_redirect_url("schoolAdmin", app.job_applicant_id, candidate_name, job.job_title)
                )
    except Exception as e:
        logger.error(f"Error creating offer status update notifications: {e}")

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
    return serve_html_with_base(
        "mss-career-portal/pages/school/schooladmin-dashboard.html",
        "/mss-career-portal/pages/school/",
    )


@router.get("/jobs-page")
def jobs_page():
    return serve_html_with_base(
        "mss-career-portal/pages/school/schooladmin-jobposts.html",
        "/mss-career-portal/pages/school/",
    )


@router.get("/job-detail-page")
def job_detail_page():
    return serve_html_with_base(
        "mss-career-portal/pages/school/schooladmin-jobpostdetails.html",
        "/mss-career-portal/pages/school/",
    )


@router.get("/applicants-page")
def applicants_page():
    return serve_html_with_base(
        "mss-career-portal/pages/school/schooladmin-jobapplicants-list.html",
        "/mss-career-portal/pages/school/",
    )


@router.get("/offers-page")
def offers_page():
    return serve_html_with_base(
        "mss-career-portal/pages/school/schooladmin-offermanagement.html",
        "/mss-career-portal/pages/school/",
    )
