from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent

if __package__ is None or __package__ == "":
    sys.path.append(str(BASE_DIR))

from app.core.html_helper import serve_html_with_base
from app.core.logger import logger
from app.routes.auth_route import router as auth_router
from app.routes.jobs_route import router as jobs_router
from app.routes.job_interview_route import router as job_interview_router
from app.routes.job_apply_route import router as apply_jobs_router
from app.routes.hr_route import router as hr_router
from app.routes.school_admin_route import router as school_admin_router
from app.routes.notification_route import router as notification_router
from app.routes.interview_auth_route import router as interview_auth_router

app = FastAPI()

origins = ["*"]

class CatchExceptionsMiddleware(BaseHTTPMiddleware):
    """Converts unhandled errors into a JSON response from inside CORSMiddleware,
    so the CORS headers still get attached. A bare @app.exception_handler(Exception)
    does NOT work for this: Starlette routes handlers for Exception/500 to
    ServerErrorMiddleware, which sits outside CORSMiddleware and skips its headers."""

    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except Exception as exc:
            logger.exception(f"Unhandled error on {request.method} {request.url.path}: {exc}")
            return JSONResponse(status_code=500, content={"detail": "Internal server error."})

# Must be added before CORSMiddleware so it ends up nested inside it
app.add_middleware(CatchExceptionsMiddleware)

# 2. Add CORSMiddleware to your FastAPI application
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    logger.info("FastAPI application has started successfully.")

# API root endpoint returning a welcome JSON response
# Redirect root URL to candidate home page
@app.get("/")
def redirect_to_home():
    return RedirectResponse(url="/mss-career-portal/home")

# Short URL redirects for easier access
@app.get("/mss-career-portal")
@app.get("/mss-career-portal/")
def redirect_to_portal_root():
    return serve_html_with_base("mss-career-portal/pages/candidate/home.html", "/mss-career-portal/pages/candidate/")

# Candidate Clean Routes
@app.get("/mss-career-portal/home")
def redirect_short_home():
    return serve_html_with_base("mss-career-portal/pages/candidate/home.html", "/mss-career-portal/pages/candidate/")

@app.get("/mss-career-portal/register")
def redirect_short_register():
    return serve_html_with_base("mss-career-portal/pages/candidate/register.html", "/mss-career-portal/pages/candidate/")

@app.get("/mss-career-portal/dashboard")
def redirect_short_dashboard():
    return serve_html_with_base("mss-career-portal/pages/candidate/dashboard.html", "/mss-career-portal/pages/candidate/")

@app.get("/mss-career-portal/jobs")
def redirect_short_jobs():
    return serve_html_with_base("mss-career-portal/pages/candidate/jobs.html", "/mss-career-portal/pages/candidate/")

@app.get("/mss-career-portal/job-detail")
def redirect_short_job_detail():
    return serve_html_with_base("mss-career-portal/pages/candidate/job-detail.html", "/mss-career-portal/pages/candidate/")

@app.get("/mss-career-portal/job-grid")
def redirect_short_job_grid():
    return serve_html_with_base("mss-career-portal/pages/candidate/job-grid.html", "/mss-career-portal/pages/candidate/")

@app.get("/mss-career-portal/apply")
def redirect_short_apply():
    return serve_html_with_base("mss-career-portal/pages/candidate/apply.html", "/mss-career-portal/pages/candidate/")

@app.get("/mss-career-portal/profile")
def redirect_short_profile():
    return serve_html_with_base("mss-career-portal/pages/candidate/profile.html", "/mss-career-portal/pages/candidate/")

@app.get("/mss-career-portal/units")
def redirect_short_units():
    return serve_html_with_base("mss-career-portal/pages/candidate/units.html", "/mss-career-portal/pages/candidate/")

@app.get("/mss-career-portal/oauth-callback")
def redirect_short_oauth_callback():
    return serve_html_with_base("mss-career-portal/pages/candidate/oauth-callback.html", "/mss-career-portal/pages/candidate/")

# HR Clean Routes
@app.get("/mss-career-portal/hr/dashboard")
def redirect_short_hr_dashboard():
    return serve_html_with_base("mss-career-portal/pages/hr/hr-dashboard.html", "/mss-career-portal/pages/hr/")

@app.get("/mss-career-portal/hr/ats-pipeline")
def redirect_short_hr_ats_pipeline():
    return serve_html_with_base("mss-career-portal/pages/hr/hr-atspipeline.html", "/mss-career-portal/pages/hr/")

@app.get("/mss-career-portal/hr/interviews")
def redirect_short_hr_interviews():
    return serve_html_with_base("mss-career-portal/pages/hr/hr-interviewlist.html", "/mss-career-portal/pages/hr/")

@app.get("/mss-career-portal/hr/reports")
def redirect_short_hr_reports():
    return serve_html_with_base("mss-career-portal/pages/hr/hr-reports.html", "/mss-career-portal/pages/hr/")

@app.get("/mss-career-portal/hr/masset-candidates")
def redirect_short_hr_masset_candidates():
    return serve_html_with_base("mss-career-portal/pages/hr/masset-sync-dashboard.html", "/mss-career-portal/pages/hr/")

@app.get("/mss-career-portal/hr/candidate-profile")
def redirect_short_hr_candidate_profile():
    return serve_html_with_base("mss-career-portal/pages/hr/hr-candidate-profile.html", "/mss-career-portal/pages/hr/")

@app.get("/mss-career-portal/hr/interview-feedback")
def redirect_short_hr_interview_feedback():
    return serve_html_with_base("mss-career-portal/pages/hr/hr-interview-feedback.html", "/mss-career-portal/pages/hr/")

@app.get("/mss-career-portal/hr/jobapplicants-list")
def redirect_short_hr_jobapplicants_list():
    return serve_html_with_base("mss-career-portal/pages/hr/hr-jobapplicants-list.html", "/mss-career-portal/pages/hr/")

@app.get("/mss-career-portal/hr/jobpost-create")
def redirect_short_hr_jobpost_create():
    return serve_html_with_base("mss-career-portal/pages/hr/hr-jobpost-create.html", "/mss-career-portal/pages/hr/")

@app.get("/mss-career-portal/hr/jobpost-details")
def redirect_short_hr_jobpost_details():
    return serve_html_with_base("mss-career-portal/pages/hr/hr-jobpost-details.html", "/mss-career-portal/pages/hr/")

@app.get("/mss-career-portal/hr/jobpost-list")
def redirect_short_hr_jobpost_list():
    return serve_html_with_base("mss-career-portal/pages/hr/hr-jobpost-list.html", "/mss-career-portal/pages/hr/")

# School Clean Routes
@app.get("/mss-career-portal/school/dashboard")
def redirect_short_school_dashboard():
    return serve_html_with_base("mss-career-portal/pages/school/schooladmin-dashboard.html", "/mss-career-portal/pages/school/")

@app.get("/mss-career-portal/school/jobs")
def redirect_short_school_jobs():
    return serve_html_with_base("mss-career-portal/pages/school/schooladmin-jobposts.html", "/mss-career-portal/pages/school/")

@app.get("/mss-career-portal/school/job-detail")
def redirect_short_school_job_detail():
    return serve_html_with_base("mss-career-portal/pages/school/schooladmin-jobpostdetails.html", "/mss-career-portal/pages/school/")

@app.get("/mss-career-portal/school/applicants")
def redirect_short_school_applicants():
    return serve_html_with_base("mss-career-portal/pages/school/schooladmin-jobapplicants-list.html", "/mss-career-portal/pages/school/")

@app.get("/mss-career-portal/school/offers")
def redirect_short_school_offers():
    return serve_html_with_base("mss-career-portal/pages/school/schooladmin-offermanagement.html", "/mss-career-portal/pages/school/")

@app.get("/mss-career-portal/school/candidate-profile")
def redirect_short_school_candidate_profile():
    return serve_html_with_base("mss-career-portal/pages/school/schooladmin-candidate-profile.html", "/mss-career-portal/pages/school/")


app.include_router(auth_router)
app.include_router(jobs_router)
app.include_router(job_interview_router)
app.include_router(apply_jobs_router)
app.include_router(hr_router)
app.include_router(school_admin_router)
app.include_router(notification_router)
app.include_router(interview_auth_router)

# Mount uploads folder
app.mount("/uploads", StaticFiles(directory=str(BASE_DIR / "uploads")), name="uploads")

# Mount frontend static files as a fallback for asset requests
app.mount("/mss-career-portal", StaticFiles(directory=str(BASE_DIR / "mss-career-portal"), html=True), name="mss-career-portal")

if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, reload=True)
