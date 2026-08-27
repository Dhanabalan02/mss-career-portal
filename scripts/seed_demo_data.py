"""
Seeds realistic demo data into the Career Portal database: job postings across
every unit, and candidates distributed across the full recruitment pipeline
(Applied, Screened, Interview, Selected, Offer, Offer Accepted, Onboarding,
Onboarded), with matching interviews and offers.

Safety:
  - Additive only. Never updates or deletes any existing row.
  - Reuses existing Units/Admins rows as foreign keys but never modifies them.
  - Demo candidates use a clearly-marked, non-deliverable email domain
    (`@demo.careerportal.local`) so this data is trivial to find and remove
    later (see `scripts/unseed_demo_data.py`).
  - Idempotent: re-running skips job posts / candidates that already exist
    (matched by title+unit and by email respectively) instead of duplicating.
  - Does not call any CRUD function that has side effects (no emails sent, no
    external MASSET webhook calls) — all fields are set directly on the ORM
    objects.

Usage:
    python -m scripts.seed_demo_data
"""

import json
import os
import random
import sys
import uuid as uuid_lib
from datetime import datetime, timedelta

sys.path.insert(0, ".")

from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models import (
    Units,
    Admins,
    UserRoles,
    Users,
    JobPost,
    JobStatus,
    JobApplicant,
    ApplicantJobStatus,
    ApplicantStage,
    OfferAcceptanceStatus,
    JobInterviewSchedule,
    InterviewMode,
    InterviewStatus,
    InterviewRemark,
    ApplicantStatus,
    JobOffer,
    CandidateMetadata,
    CandidateExperience,
    CandidateEducationDetail,
    JobPreScreeningQuestion,
    CandidateScreeningAnswer,
)
from app.models.candidate_screening_answer_model import CandidateStatus

DEMO_EMAIL_DOMAIN = "demo.careerportal.local"
random.seed(42)

# ─────────────────────────────────────────────────────────────────────────
# Reference data
# ─────────────────────────────────────────────────────────────────────────

SUBJECTS = [
    {
        "key": "english",
        "title": "English Teacher",
        "department": "Teaching",
        "skills": "Lesson Planning, Creative Writing, Classroom Management, Public Speaking",
        "education": "B.A. English Literature, B.Ed",
        "desc": (
            "We are looking for a passionate English teacher to inspire students in "
            "reading, writing, and communication skills, and to build engaging lesson "
            "plans aligned with the curriculum."
        ),
        "min_exp": "1",
        "max_exp": "5",
        "degree": "B.A. English Literature",
    },
    {
        "key": "mathematics",
        "title": "Mathematics Teacher",
        "department": "Teaching",
        "skills": "Curriculum Development, Problem Solving, Classroom Management, Assessment Design",
        "education": "B.Sc. Mathematics, B.Ed",
        "desc": (
            "Seeking an experienced Mathematics teacher to deliver engaging lessons, "
            "mentor students, and drive strong academic outcomes across grades."
        ),
        "min_exp": "2",
        "max_exp": "6",
        "degree": "B.Sc. Mathematics",
    },
    {
        "key": "science",
        "title": "Science Teacher",
        "department": "Teaching",
        "skills": "Laboratory Management, Curriculum Development, Experiment Design, Classroom Management",
        "education": "B.Sc. Science, B.Ed",
        "desc": (
            "Looking for a Science teacher who can bring physics, chemistry, and biology "
            "concepts to life through hands-on experiments and engaging classroom "
            "instruction."
        ),
        "min_exp": "1",
        "max_exp": "5",
        "degree": "B.Sc. Physics",
    },
    {
        "key": "computer_science",
        "title": "Computer Science Teacher",
        "department": "IT",
        "skills": "Programming Fundamentals, Curriculum Development, Python, Classroom Management",
        "education": "B.E./B.Tech Computer Science, B.Ed (preferred)",
        "desc": (
            "We need a Computer Science teacher to introduce students to programming, "
            "computational thinking, and digital literacy through a hands-on curriculum."
        ),
        "min_exp": "1",
        "max_exp": "4",
        "degree": "B.E. Computer Science",
    },
    {
        "key": "primary",
        "title": "Primary Teacher",
        "department": "Teaching",
        "skills": "Lesson Planning, Student Assessment, Classroom Management, Early Childhood Education",
        "education": "B.El.Ed / D.El.Ed, B.Ed",
        "desc": (
            "Seeking a nurturing Primary School teacher to build strong foundational "
            "skills in young learners through engaging, age-appropriate teaching "
            "methods."
        ),
        "min_exp": "0",
        "max_exp": "4",
        "degree": "B.El.Ed",
    },
    {
        "key": "social_studies",
        "title": "Social Studies Teacher",
        "department": "Teaching",
        "skills": "Curriculum Development, Classroom Management, Research Skills, Public Speaking",
        "education": "B.A. History, B.Ed",
        "desc": (
            "Looking for a Social Studies teacher to help students understand history, "
            "geography, and civics through interactive and thought-provoking lessons."
        ),
        "min_exp": "1",
        "max_exp": "5",
        "degree": "B.A. History",
    },
    {
        "key": "physical_education",
        "title": "Physical Education Teacher",
        "department": "Teaching",
        "skills": "Sports Coaching, Fitness Training, Event Management, Student Mentoring",
        "education": "B.P.Ed",
        "desc": (
            "We are seeking a Physical Education teacher to promote fitness, "
            "sportsmanship, and healthy habits among students through structured "
            "activities and competitions."
        ),
        "min_exp": "1",
        "max_exp": "6",
        "degree": "B.P.Ed",
    },
    {
        "key": "special_educator",
        "title": "Special Educator",
        "department": "Teaching",
        "skills": "Individualized Education Plans, Behavioral Support, Classroom Management, Patience & Empathy",
        "education": "B.Ed Special Education",
        "desc": (
            "Looking for a compassionate Special Educator to support students with "
            "diverse learning needs through individualized instruction and care."
        ),
        "min_exp": "1",
        "max_exp": "5",
        "degree": "B.Ed Special Education",
    },
    {
        "key": "music",
        "title": "Music Teacher",
        "department": "Music",
        "skills": "Vocal Training, Instrumental Training, Music Theory, Event Coordination",
        "education": "B.A./B.Mus Music, Diploma in Music",
        "desc": (
            "Seeking a talented Music teacher to nurture students' musical abilities "
            "through vocal and instrumental training, and to coordinate school music "
            "events."
        ),
        "min_exp": "1",
        "max_exp": "6",
        "degree": "B.A. Music",
    },
]
SUBJECTS_BY_KEY = {s["key"]: s for s in SUBJECTS}
ROTATION_SUBJECTS = [s for s in SUBJECTS if s["key"] != "music"]  # 8 core subjects

MALE_FIRST = [
    "Arun", "Karthik", "Vijay", "Suresh", "Ramesh", "Praveen", "Sathish", "Dinesh",
    "Manoj", "Ashok", "Bala", "Ganesh", "Hari", "Kiran", "Mohan", "Naveen",
    "Prakash", "Sanjay", "Vishnu", "Anand", "Deepak", "Gopal", "Mahesh", "Rajesh",
]
FEMALE_FIRST = [
    "Priya", "Lakshmi", "Divya", "Kavitha", "Meena", "Anitha", "Deepa", "Geetha",
    "Kalpana", "Latha", "Nisha", "Padma", "Radha", "Saranya", "Uma", "Vani",
    "Bhavani", "Chitra", "Indhu", "Jaya", "Malathi", "Nithya", "Pooja", "Revathi",
]
LAST_NAMES = [
    "Kumar", "Raj", "Iyer", "Nair", "Pillai", "Subramaniam", "Krishnan", "Menon",
    "Rao", "Varma", "Sundaram", "Narayanan", "Chandran", "Venkatesh",
    "Ramanathan", "Srinivasan", "Natarajan", "Muthu", "Balakrishnan", "Ravindran",
]
FICTIONAL_SCHOOLS = [
    "Green Valley Public School", "Sunrise Matriculation School", "Bright Minds Academy",
    "Horizon International School", "Lakeview Senior Secondary School", "Maple Leaf School",
    "Silver Oak Public School", "Riverdale Matriculation School", "Crescent Academy",
    "Northfield Senior Secondary School",
]

CAMPUS_BY_UNIT_SUBSTR = [
    ("tambaram", "Tambaram"),
    ("t. nagar", "T.Nagar"),
    ("chetpet", "Chetpet"),
]


def campus_for_unit(unit_name: str) -> str:
    lname = unit_name.lower()
    for substr, campus in CAMPUS_BY_UNIT_SUBSTR:
        if substr in lname:
            return campus
    return "Chetpet"


def programme_for(unit_name: str, subject_key: str) -> str:
    lname = unit_name.lower()
    if "lady andal school" in lname:
        return "PYP" if subject_key == "primary" else random.choice(["MYP", "DP"])
    if subject_key == "primary":
        return "Primary"
    if subject_key in ("physical_education", "computer_science"):
        return "Higher Secondary/Senior"
    return "Secondary"


EXPERIENCE_BUCKETS = ["Less than 1 year", "1-2 years", "3-5 years", "6+ years"]


def experience_bucket(min_exp) -> str:
    try:
        n = int(str(min_exp).strip())
    except (TypeError, ValueError):
        n = 2
    if n <= 0:
        return EXPERIENCE_BUCKETS[0]
    if n <= 2:
        return EXPERIENCE_BUCKETS[1]
    if n <= 5:
        return EXPERIENCE_BUCKETS[2]
    return EXPERIENCE_BUCKETS[3]


def ensure_prescreen_questions(db, job_id: int, subject: dict) -> list:
    """Every job should carry a few pre-screening questions so applicants
    have something real to answer. Idempotent: skips jobs that already have
    any questions attached. Mirrors how hr-jobpost-create.html itself builds
    questions: boolean questions carry options=["Yes","No"]; mcq questions
    carry the real choice list, with expected_answer one of those choices."""
    existing = (
        db.query(JobPreScreeningQuestion)
        .filter(JobPreScreeningQuestion.job_id == job_id)
        .order_by(JobPreScreeningQuestion.question_id)
        .all()
    )
    if existing:
        return existing

    specs = [
        {
            "question_text": f"How many years of experience do you have teaching {subject['title'].replace(' Teacher', '')}?",
            "question_type": "mcq",
            "options": list(EXPERIENCE_BUCKETS),
            "expected_answer": experience_bucket(subject["min_exp"]),
        },
        {
            "question_text": f"Do you hold a {subject['degree']} or equivalent qualification?",
            "question_type": "boolean",
            "options": ["Yes", "No"],
            "expected_answer": "Yes",
        },
        {
            "question_text": "Are you available to join within 30 days of receiving an offer?",
            "question_type": "boolean",
            "options": ["Yes", "No"],
            "expected_answer": "Yes",
        },
    ]
    for spec in specs:
        db.add(
            JobPreScreeningQuestion(
                job_id=job_id,
                question_text=spec["question_text"],
                question_type=spec["question_type"],
                options=spec["options"],
                expected_answer=spec["expected_answer"],
            )
        )
    db.flush()
    return (
        db.query(JobPreScreeningQuestion)
        .filter(JobPreScreeningQuestion.job_id == job_id)
        .order_by(JobPreScreeningQuestion.question_id)
        .all()
    )


def days_ago(n: int) -> datetime:
    return datetime.utcnow() - timedelta(days=n)


def offer_letter_html(name: str, job_title: str, school: str, dept: str, salary: str, joining_date, probation: str, expiry) -> str:
    fmt = lambda d: f"{d.day} {d.strftime('%b %Y')}"
    return (
        f'<div style="max-width: 600px; margin: 20px auto; text-align: left; '
        f'border: 1px solid #d4d1cb; padding: 40px; border-radius: 8px; '
        f'font-size: 16px; line-height: 1.8; background-color: #ffffff;">'
        f"Dear <span class=\"ph\">{name}</span>,<br><br>\n"
        f"We are pleased to offer you the position of <span class=\"ph\">{job_title}</span> "
        f"at <span class=\"ph\">{school}</span>, under the <span class=\"ph\">{dept}</span> department.<br><br>\n"
        f"This is a full-time position with a gross annual compensation of "
        f"<span class=\"ph\">{salary}</span>. Your expected date of joining is "
        f"<span class=\"ph\">{fmt(joining_date)}</span>. You will be subject to a "
        f"probationary period of <span class=\"ph\">{probation}</span>.<br><br>\n"
        f"Please confirm your acceptance by <span class=\"ph\">{fmt(expiry)}</span>. "
        f"If you have any questions, feel free to reach out to our HR team.<br><br>\n"
        f"We look forward to welcoming you to the team.<br><br>\n"
        f"Warm regards,<br><strong>School Admin — TMSS</strong></div>"
    )


def name_pool(idx: int):
    is_male = idx % 2 == 0
    first_pool = MALE_FIRST if is_male else FEMALE_FIRST
    first = first_pool[idx % len(first_pool)]
    last = LAST_NAMES[(idx * 7 + 3) % len(LAST_NAMES)]
    gender = "Male" if is_male else "Female"
    return first, last, gender


# ─────────────────────────────────────────────────────────────────────────
# Job posts
# ─────────────────────────────────────────────────────────────────────────

def seed_jobs(db, units, unit_admin_map, hr_admin_id):
    """Creates ~2 teaching job posts per unit. Returns {subject_key: [job dict]}."""
    jobs_by_subject: dict[str, list] = {s["key"]: [] for s in SUBJECTS}
    created = 0
    skipped = 0
    created_job_ids: list[int] = []

    for i, unit in enumerate(units):
        subject_keys = [
            ROTATION_SUBJECTS[i % len(ROTATION_SUBJECTS)]["key"],
            ROTATION_SUBJECTS[(i + 1) % len(ROTATION_SUBJECTS)]["key"],
        ]
        if "school of sound and music" in unit.unit_name.lower():
            subject_keys = ["music", subject_keys[0]]

        admin_id = unit_admin_map.get(unit.id, hr_admin_id)

        for j, subject_key in enumerate(subject_keys):
            subject = SUBJECTS_BY_KEY[subject_key]

            existing = (
                db.query(JobPost)
                .filter(
                    JobPost.job_title == subject["title"],
                    JobPost.school_name == unit.unit_name,
                )
                .first()
            )
            if existing:
                ensure_prescreen_questions(db, existing.job_id, subject)
                jobs_by_subject[subject_key].append(
                    {"id": existing.job_id, "unit": unit, "status": existing.job_status}
                )
                skipped += 1
                continue

            job_index = i * 2 + j
            created_at = days_ago(60 - (job_index % 55))
            # Most jobs are published; a handful are draft/closed for realism.
            if job_index % 11 == 0:
                status = JobStatus.CLOSED
            elif job_index % 9 == 0:
                status = JobStatus.DRAFT
            else:
                status = JobStatus.PUBLISH

            job = JobPost(
                job_posted_by=admin_id,
                job_title=subject["title"],
                job_type=random.choice(["Full-time", "Full-time", "Full-time", "Part-time"]),
                job_description=subject["desc"],
                school_name=unit.unit_name,
                department=subject["department"],
                location=campus_for_unit(unit.unit_name),
                programme=programme_for(unit.unit_name, subject_key),
                vacancy_count=random.choice([1, 1, 2, 3]),
                min_exp=subject["min_exp"],
                max_exp=subject["max_exp"],
                skills_required=subject["skills"],
                education_qualification=subject["education"],
                additional_requirements="Strong communication skills and a collaborative mindset.",
                job_status=status,
                views=random.randint(15, 240),
                created_at=created_at,
                updated_at=created_at,
                published_at=created_at if status == JobStatus.PUBLISH else None,
            )
            if status == JobStatus.PUBLISH:
                job.uuid = str(uuid_lib.uuid4())
            if status == JobStatus.CLOSED:
                job.closed_by = admin_id
                job.closed_at = created_at + timedelta(days=20)

            db.add(job)
            db.flush()
            ensure_prescreen_questions(db, job.job_id, subject)
            created += 1
            created_job_ids.append(job.job_id)
            jobs_by_subject[subject_key].append({"id": job.job_id, "unit": unit, "status": status})

    print(f"Job posts: {created} created, {skipped} already existed.")
    return jobs_by_subject, created_job_ids


# ─────────────────────────────────────────────────────────────────────────
# Candidates + pipeline
# ─────────────────────────────────────────────────────────────────────────

STAGE_PLAN = [
    "Applied",
    "Screened",
    "Interview",
    "Selected",
    "Offer",
    "Offer Accepted",
    "Onboarding",
    "Onboarded",
]
CANDIDATES_PER_STAGE = 6


def pick_job(jobs_by_subject, subject_key, counters):
    candidates = [
        j for j in jobs_by_subject.get(subject_key, []) if j["status"] != JobStatus.DRAFT
    ] or jobs_by_subject.get(subject_key, [])
    if not candidates:
        return None
    n = counters.get(subject_key, 0)
    counters[subject_key] = n + 1
    return candidates[n % len(candidates)]


def build_experience_years(stage_idx: int) -> float:
    # Later-stage (further along) candidates skew slightly more experienced.
    base = 1 + stage_idx * 0.4
    return round(base + random.uniform(0, 2), 1)


def ensure_candidate_role(db) -> int:
    role = db.query(UserRoles).filter(UserRoles.role_name == "candidate").first()
    if not role:
        raise RuntimeError("No 'candidate' role found in user_roles table.")
    return role.role_id


def seed_candidates(db, jobs_by_subject, hr_admin_id, candidate_role_id):
    counters: dict[str, int] = {}
    created_users = 0
    skipped_users = 0
    created_applications = 0
    skipped_applications = 0
    created_user_ids: list[int] = []

    idx = 0
    for stage_i, stage_name in enumerate(STAGE_PLAN):
        for _ in range(CANDIDATES_PER_STAGE):
            subject = ROTATION_SUBJECTS[idx % len(ROTATION_SUBJECTS)]
            job_entry = pick_job(jobs_by_subject, subject["key"], counters)
            if not job_entry:
                idx += 1
                continue

            first, last, gender = name_pool(idx)
            email = f"{first.lower()}.{last.lower()}{idx}@{DEMO_EMAIL_DOMAIN}"

            user = db.query(Users).filter(Users.email == email).first()
            if user:
                # Already seeded this candidate; also skip their application if present.
                existing_app = (
                    db.query(JobApplicant)
                    .filter(
                        JobApplicant.user_id == user.user_id,
                        JobApplicant.job_id == job_entry["id"],
                    )
                    .first()
                )
                if existing_app:
                    skipped_users += 1
                    skipped_applications += 1
                    idx += 1
                    continue
            else:
                applied_days_ago = 5 + stage_i * 6
                user = Users(
                    role_id=candidate_role_id,
                    first_name=first,
                    last_name=last,
                    gender=gender,
                    email=email,
                    password=get_password_hash("Demo@1234"),
                    mobile=f"98{idx:08d}",
                    user_status=1,
                    created_at=days_ago(applied_days_ago),
                    updated_at=days_ago(applied_days_ago),
                )
                db.add(user)
                db.flush()
                created_users += 1
                created_user_ids.append(user.user_id)

                exp_years = build_experience_years(stage_i)
                metadata = CandidateMetadata(
                    user_id=user.user_id,
                    about=(
                        f"Dedicated {subject['title']} with a passion for student growth "
                        f"and innovative teaching methods."
                    ),
                    city="Chennai",
                    state="Tamil Nadu",
                    country="India",
                    pincode="600006",
                    skills=json.dumps([s.strip() for s in subject["skills"].split(",")]),
                    languages="English, Tamil",
                    profile_status="complete",
                    created_at=days_ago(applied_days_ago),
                    updated_at=days_ago(applied_days_ago),
                )
                db.add(metadata)

                prior_school = FICTIONAL_SCHOOLS[idx % len(FICTIONAL_SCHOOLS)]
                end_year = 2025 - int(exp_years)
                experience = CandidateExperience(
                    user_id=user.user_id,
                    company_name=prior_school,
                    designation=subject["title"],
                    employment_type="Full-time",
                    start_date=f"{end_year - 1}-06",
                    end_date=f"{end_year}-04",
                    total_experience=f"{exp_years} yrs",
                    location="Chennai",
                    notice_period=random.choice(["Immediate", "15 days", "30 days", "60 days"]),
                )
                db.add(experience)

                education = CandidateEducationDetail(
                    user_id=user.user_id,
                    education_level="Graduation",
                    degree_name=subject["degree"],
                    specialization=subject["title"].replace(" Teacher", ""),
                    institution_name=f"{prior_school.split()[0]} College of Education",
                    university_name="University of Madras",
                    start_year=end_year - 4,
                    end_year=end_year - 1,
                    percentage=round(random.uniform(62, 91), 2),
                )
                db.add(education)

            applied_days_ago = 5 + stage_i * 6
            applied_at = days_ago(applied_days_ago)

            applicant = JobApplicant(
                job_id=job_entry["id"],
                user_id=user.user_id,
                mss_app_no="TEMP",
                applicant_job_status=None,
                applicant_stage=None,
                offer_acceptance_status=OfferAcceptanceStatus.PENDING,
                created_at=applied_at,
                updated_at=applied_at,
            )
            db.add(applicant)
            db.flush()
            applicant.mss_app_no = f"MSS-APP-{applicant.job_applicant_id}"

            questions = ensure_prescreen_questions(db, job_entry["id"], subject)
            for q in questions:
                db.add(
                    CandidateScreeningAnswer(
                        candidate_id=user.user_id,
                        job_id=job_entry["id"],
                        question_id=q.question_id,
                        answer=q.expected_answer or "Yes",
                        candidate_status=CandidateStatus.SCREENED,
                        created_at=applied_at,
                    )
                )

            _apply_stage(db, applicant, stage_name, job_entry, applied_at, hr_admin_id, subject)

            db.commit()
            created_applications += 1
            idx += 1

    print(f"Candidates: {created_users} created, {skipped_users} already existed.")
    print(f"Applications: {created_applications} created, {skipped_applications} already existed.")
    return created_user_ids


def _schedule_interview(db, applicant, job_entry, applied_at, hr_admin_id, status: InterviewStatus, when: datetime):
    start_dt = when.replace(minute=0, second=0, microsecond=0)
    end_dt = start_dt + timedelta(minutes=45)
    mode = random.choice([InterviewMode.ONLINE, InterviewMode.OFFLINE])
    interview = JobInterviewSchedule(
        job_id=job_entry["id"],
        job_applicant_id=applicant.job_applicant_id,
        interview_round="Round 1",
        interview_mode=mode,
        scheduled_date=when.date(),
        start_time=start_dt.time(),
        end_time=end_dt.time(),
        meeting_link="https://meet.google.com/demo-interview" if mode == InterviewMode.ONLINE else None,
        location=job_entry["unit"].unit_name if mode == InterviewMode.OFFLINE else None,
        address=job_entry["unit"].unit_name,
        interviewer_name=f"Principal, {job_entry['unit'].unit_name.split(',')[0]}",
        status=status,
        created_by=hr_admin_id,
        created_at=applied_at + timedelta(days=1),
        updated_at=applied_at + timedelta(days=1),
    )
    db.add(interview)
    db.flush()
    return interview


def _apply_stage(db, applicant, stage_name, job_entry, applied_at, hr_admin_id, subject):
    if stage_name == "Applied":
        return

    if stage_name == "Screened":
        applicant.applicant_stage = ApplicantStage.SCREENED
        applicant.updated_at = applied_at + timedelta(days=2)
        return

    if stage_name == "Interview":
        applicant.applicant_stage = ApplicantStage.INTERVIEW
        applicant.applicant_job_status = ApplicantJobStatus.NEXT_ROUND
        interview_at = applied_at + timedelta(days=5)
        _schedule_interview(db, applicant, job_entry, applied_at, hr_admin_id, InterviewStatus.SCHEDULED, interview_at)
        applicant.updated_at = interview_at
        return

    # Everything from "Selected" onward has already had a completed, successful interview.
    interview_at = applied_at + timedelta(days=5)
    interview = _schedule_interview(
        db, applicant, job_entry, applied_at, hr_admin_id, InterviewStatus.COMPLETED, interview_at
    )
    remark = InterviewRemark(
        job_interview_id=interview.job_interview_id,
        round="Round 1",
        remarks=f"Strong subject knowledge and classroom presence. Recommended for {subject['title']}.",
        applicant_status=ApplicantStatus.SELECTED,
        created_by=hr_admin_id,
        created_at=interview_at + timedelta(hours=2),
        updated_at=interview_at + timedelta(hours=2),
    )
    db.add(remark)

    if stage_name == "Selected":
        applicant.applicant_stage = ApplicantStage.INTERVIEW
        applicant.applicant_job_status = ApplicantJobStatus.SELECTED
        applicant.updated_at = interview_at + timedelta(hours=2)
        return

    # Offer and beyond
    applicant.applicant_job_status = ApplicantJobStatus.SELECTED
    offer_issued_at = interview_at + timedelta(days=3)
    joining_date = (offer_issued_at + timedelta(days=30)).date()
    probation = random.choice(["3 months", "6 months"])
    expiry_date = (offer_issued_at + timedelta(days=14)).date()
    salary = f"₹{random.randint(28, 55)},000/month"

    user = db.query(Users).filter(Users.user_id == applicant.user_id).first()
    name = f"{user.first_name} {user.last_name}".strip() if user else "Candidate"

    offer = JobOffer(
        job_applicant_id=applicant.job_applicant_id,
        offered_salary=salary,
        joining_date=joining_date,
        probation_period=probation,
        offer_issued_date=offer_issued_at,
        offer_expiry_date=expiry_date,
        offer_remarks="Congratulations! We are pleased to offer you this position.",
        offer_template="standard",
        offer_letter_doc=offer_letter_html(
            name, subject["title"], job_entry["unit"].unit_name, subject["department"],
            salary, joining_date, probation, expiry_date,
        ),
        issued_by=hr_admin_id,
        is_draft=0,
        created_at=offer_issued_at,
    )
    db.add(offer)
    applicant.issue_offer = 1

    if stage_name == "Offer":
        applicant.applicant_stage = ApplicantStage.OFFER
        applicant.updated_at = offer_issued_at
        return

    # Offer Accepted and beyond
    accepted_at = offer_issued_at + timedelta(days=3)
    applicant.applicant_stage = ApplicantStage.OFFER_ACCEPTED
    applicant.offer_acceptance_status = OfferAcceptanceStatus.ACCEPTED
    applicant.offer_accepted_on = accepted_at
    applicant.updated_at = accepted_at

    if stage_name == "Offer Accepted":
        return

    # Onboarding and beyond
    synced_at = accepted_at + timedelta(days=2)
    applicant.applicant_stage = ApplicantStage.ONBOARDING
    applicant.sync_masset = 1
    applicant.masset_synced_at = synced_at
    applicant.masset_synced_by = hr_admin_id
    applicant.updated_at = synced_at

    if stage_name == "Onboarding":
        return

    # Onboarded
    onboarded_at = synced_at + timedelta(days=4)
    applicant.applicant_stage = ApplicantStage.ONBOARDING_COMPLETED
    applicant.issue_appointment_order = 1
    applicant.masset_status = "onboarded"
    applicant.masset_employee_id = f"MSSEMP{2000 + applicant.job_applicant_id}"
    applicant.masset_sync_success_on = onboarded_at
    applicant.reporting_to = f"Principal, {job_entry['unit'].unit_name.split(',')[0]}"
    applicant.updated_at = onboarded_at


# ─────────────────────────────────────────────────────────────────────────
# Manifest (used by scripts/unseed_demo_data.py to remove exactly this data)
# ─────────────────────────────────────────────────────────────────────────

MANIFEST_PATH = "scripts/demo_data_manifest.json"


def _update_manifest(new_job_ids, new_user_ids):
    manifest = {"job_ids": [], "user_ids": []}
    if os.path.exists(MANIFEST_PATH):
        with open(MANIFEST_PATH) as f:
            manifest = json.load(f)

    manifest["job_ids"] = sorted(set(manifest.get("job_ids", [])) | set(new_job_ids))
    manifest["user_ids"] = sorted(set(manifest.get("user_ids", [])) | set(new_user_ids))

    with open(MANIFEST_PATH, "w") as f:
        json.dump(manifest, f, indent=2)


# ─────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────

def main():
    db = SessionLocal()
    try:
        units = db.query(Units).all()
        if not units:
            print("No units found — nothing to seed against. Aborting.")
            return

        admins = db.query(Admins).all()
        unit_admin_map = {a.unit_id: a.admin_id for a in admins if a.unit_id is not None}

        hr_admin = (
            db.query(Admins)
            .join(UserRoles, Admins.role_id == UserRoles.role_id)
            .filter(UserRoles.role_name == "hr_head")
            .first()
        )
        if not hr_admin:
            hr_admin = admins[0] if admins else None
        if not hr_admin:
            print("No admin accounts found — cannot attribute demo jobs/actions. Aborting.")
            return
        hr_admin_id = hr_admin.admin_id

        candidate_role_id = ensure_candidate_role(db)

        print(f"Seeding against {len(units)} units, HR admin_id={hr_admin_id}.")

        jobs_by_subject, created_job_ids = seed_jobs(db, units, unit_admin_map, hr_admin_id)
        db.commit()

        created_user_ids = seed_candidates(db, jobs_by_subject, hr_admin_id, candidate_role_id)

        _update_manifest(created_job_ids, created_user_ids)

        print("Done.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
