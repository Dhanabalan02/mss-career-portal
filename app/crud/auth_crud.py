from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from datetime import datetime, timedelta, timezone
from app.core.logger import logger
from app.models import UserLoginLog, Admins, Users, UserRoles, LoginStatus
from app.core.security import verify_password, create_access_token, get_password_hash

OTP_VALIDITY_MINUTES = 10

ADMIN_ROLES = {"hr_head", "hr_admin", "school_admin", "hr_team"}

def authenticate_user_roles(
    db: Session,
    email: str,
    password: str,
    ip_address: str = None
) -> str:
    """Authenticates hr_head, hr_admin, school_admin and candidate users and returns a JWT token."""

    admin = (
        db.query(Admins)
        .options(joinedload(Admins.user_roles))
        .filter(Admins.email == email, Admins.is_active == 1)
        .first()
    )

    if admin and admin.user_roles.role_name in ADMIN_ROLES:
        role_name = admin.user_roles.role_name

        if not verify_password(password, admin.password):
            logger.warning(f"Failed login attempt for email: {email} from IP: {ip_address}")
            db.add(UserLoginLog(
                user_id=admin.admin_id,
                user_type=role_name,
                status=LoginStatus.failed,
                ip_address=ip_address,
                login_time=datetime.now(timezone.utc)
            ))
            db.commit()
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password.")

        token_data = {"sub": str(admin.admin_id), "role": role_name}
        access_token = create_access_token(data=token_data, expires_delta=timedelta(hours=8))

        db.add(UserLoginLog(
            user_id=admin.admin_id,
            user_type=role_name,
            login_type="password",
            status=LoginStatus.success,
            ip_address=ip_address,
            login_time=datetime.now(timezone.utc),
            session_id=access_token
        ))
        db.commit()
        logger.info(f"Successful login for {role_name} email: {email} from IP: {ip_address}")
        return {
            "access_token": access_token,
            "user_type": role_name,
            "token_type": "bearer",
            "user_id": admin.admin_id
        }

    candidate = (
        db.query(Users)
        .options(joinedload(Users.user_roles))
        .filter(Users.email == email, Users.user_status == 1)
        .first()
    )

    if not candidate or candidate.user_roles.role_name != "candidate":
        logger.warning(f"Unauthorized login attempt for email: {email} from IP: {ip_address}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or unauthorized access."
        )

    if not verify_password(password, candidate.password):
        logger.warning(f"Failed login attempt for email: {email} from IP: {ip_address}")
        db.add(UserLoginLog(
            user_id=candidate.user_id,
            user_type="candidate",
            status=LoginStatus.failed,
            ip_address=ip_address,
            login_time=datetime.now(timezone.utc)
        ))
        db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password.")

    token_data = {"sub": str(candidate.user_id), "role": "candidate"}
    access_token = create_access_token(data=token_data, expires_delta=timedelta(hours=8))

    db.add(UserLoginLog(
        user_id=candidate.user_id,
        user_type="candidate",
        status=LoginStatus.success,
        ip_address=ip_address,
        login_time=datetime.now(timezone.utc),
        session_id=access_token,
        login_type="password"
    ))
    db.commit()
    logger.info(f"Successful login for candidate email: {email} from IP: {ip_address}")
    return {
        "access_token": access_token,
        "user_type": "candidate",
        "token_type": "bearer",
        "name": f"{candidate.first_name} {candidate.last_name}".strip(),
        "user_id": candidate.user_id
    }


def logout_user_logs(
    db: Session, 
    admin_id: int, 
    session_id: str, 
    ip_address: str = None
):
    """Logs out the admin and updates the login log with logout time."""
    
    log_entry = db.query(UserLoginLog).filter(
        UserLoginLog.user_id == admin_id,
        UserLoginLog.session_id == session_id,
        UserLoginLog.status == LoginStatus.success
    ).order_by(UserLoginLog.login_time.desc()).first()
    
    if log_entry:
        log_entry.logout_time = datetime.now(timezone.utc)
        log_entry.session_id = None 
        db.commit()
        logger.info(f"Admin ID {admin_id} logged out from IP: {ip_address}")
    else:
        logger.warning(f"Logout attempt with invalid session for Admin ID {admin_id} from IP: {ip_address}")

def _oauth_get_or_create_user(db: Session, email: str, name: str, provider: str, ip_address: str) -> Users:
    """Looks up an existing candidate by email or creates one for OAuth sign-in."""
    import secrets

    user = db.query(Users).filter(Users.email == email, Users.user_status == 1).first()
    if user:
        if user.oauth_provider != provider:
            user.oauth_provider = provider
            db.commit()
            db.refresh(user)
        return user

    parts = (name or "").strip().split(" ", 1)
    first_name = parts[0] or "User"
    last_name = parts[1] if len(parts) > 1 else ""

    candidate_role = db.query(UserRoles).filter(UserRoles.role_name == "candidate").first()
    if not candidate_role:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Candidate role is not configured."
        )

    user = Users(
        role_id=candidate_role.role_id,
        email=email,
        first_name=first_name,
        last_name=last_name,
        gender="",
        mobile="",
        password=get_password_hash(secrets.token_urlsafe(32)),
        user_status=1,
        oauth_provider=provider
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info(f"New user created via {provider} login: {email} from IP: {ip_address}")
    return user


def googlelogin(
    db: Session,
    email: str,
    name: str,
    ip_address: str = None
) -> dict:
    """Handles Google login, creating a new user if necessary, and returns user info + JWT."""
    user = _oauth_get_or_create_user(db, email, name, "Google", ip_address)

    token_data = {"sub": str(user.user_id), "role": "candidate"}
    access_token = create_access_token(data=token_data, expires_delta=timedelta(hours=8))

    db.add(UserLoginLog(
        user_id=user.user_id,
        user_type="candidate",
        status=LoginStatus.success,
        ip_address=ip_address,
        login_time=datetime.now(timezone.utc),
        session_id=access_token,
        login_type="google"
    ))
    db.commit()
    logger.info(f"Successful Google login for email: {email} from IP: {ip_address}")

    return {
        "access_token": access_token,
        "user_type": "candidate",
        "token_type": "bearer",
        "name": f"{user.first_name} {user.last_name}".strip(),
        "user_id": user.user_id,
        "email": user.email,
    }


def linkedin_login(
    db: Session,
    email: str,
    name: str,
    ip_address: str = None
) -> dict:
    """Handles LinkedIn login, creating a new user if necessary, and returns user info + JWT."""
    user = _oauth_get_or_create_user(db, email, name, "LinkedIn", ip_address)

    token_data = {"sub": str(user.user_id), "role": "candidate"}
    access_token = create_access_token(data=token_data, expires_delta=timedelta(hours=8))

    db.add(UserLoginLog(
        user_id=user.user_id,
        user_type="candidate",
        status=LoginStatus.success,
        ip_address=ip_address,
        login_time=datetime.now(timezone.utc),
        session_id=access_token,
        login_type="linkedin"
    ))
    db.commit()
    logger.info(f"Successful LinkedIn login for email: {email} from IP: {ip_address}")

    return {
        "access_token": access_token,
        "user_type": "candidate",
        "token_type": "bearer",
        "name": f"{user.first_name} {user.last_name}".strip(),
        "user_id": user.user_id,
        "email": user.email,
    }

def register_candidate(
    db: Session,
    email: str,
    first_name: str,
    last_name: str,
    mobile: str,
    password: str,
    ip_address: str = None
) -> dict:
    """Registers a new candidate and returns a JWT token."""

    existing_user = db.query(Users).filter(
        (Users.email == email) | (Users.mobile == mobile),
        Users.user_status == 1
    ).first()

    if existing_user:
        logger.warning(f"Registration attempt with existing email or mobile: {email}, {mobile} from IP: {ip_address}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or mobile already registered."
        )

    candidate_role = db.query(UserRoles).filter(UserRoles.role_name == "candidate").first()
    if not candidate_role:
        logger.error("Registration failed: 'candidate' role is not configured in user_roles.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Candidate role is not configured."
        )

    new_user = Users(
        role_id=candidate_role.role_id,
        email=email,
        first_name=first_name,
        last_name=last_name,
        gender="",
        mobile=mobile,
        password=get_password_hash(password),
        user_status=1
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token_data = {"sub": str(new_user.user_id), "role": "candidate"}
    access_token = create_access_token(data=token_data, expires_delta=timedelta(hours=8))

    success_log = UserLoginLog(
        user_id=new_user.user_id,
        user_type="candidate",
        status=LoginStatus.success,
        ip_address=ip_address,
        login_time=datetime.now(timezone.utc),
        session_id=access_token)

    logger.info(f"New candidate registered with email: {email} from IP: {ip_address}")
    db.add(success_log)
    db.commit()

    return {
        "access_token": access_token,
        "user_type": "candidate",
        "token_type": "bearer",
        "name": f"{first_name} {last_name}".strip(),
        "user_id": new_user.user_id
    }


def get_candidate_profile_db(db: Session, user_id: int) -> dict:
    """Retrieves full candidate profile details for the given user_id."""
    from app.models import CandidateMetadata, CandidateEducationDetail, CandidateExperience
    
    user = db.query(Users).filter(Users.user_id == user_id, Users.user_status == 1).first()
    if not user:
        raise HTTPException(status_code=404, detail="Candidate not found.")
        
    meta = db.query(CandidateMetadata).filter(CandidateMetadata.user_id == user_id).first()
    education = db.query(CandidateEducationDetail).filter(CandidateEducationDetail.user_id == user_id).all()
    experience = db.query(CandidateExperience).filter(CandidateExperience.user_id == user_id).all()
    
    skills_list = []
    if meta and meta.skills:
        try:
            import json
            skills_list = json.loads(meta.skills)
            if not isinstance(skills_list, list):
                skills_list = [meta.skills]
        except Exception:
            skills_list = [s.strip() for s in meta.skills.split(",") if s.strip()]
        
    return {
        "user_id": user.user_id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "gender": user.gender,
        "email": user.email,
        "mobile": user.mobile,
        "image_path": user.image_path,
        "metadata": {
            "date_of_birth": meta.date_of_birth.strftime("%Y-%m-%d") if (meta and meta.date_of_birth and hasattr(meta.date_of_birth, 'strftime')) else (meta.date_of_birth if meta and meta.date_of_birth else None),
            "personal_address": meta.personal_address if meta else None,
            "city": meta.city if meta else None,
            "state": meta.state if meta else None,
            "country": meta.country if meta else None,
            "pincode": meta.pincode if meta else None,
            "skills": skills_list,
            "resume_doc": meta.resume_doc if meta else None,
            "profile_status": meta.profile_status if meta else None,
            "about": meta.about,
            "designation": experience[0].designation if experience else None,
            "company": experience[0].company_name if experience else None,
            "experience": experience[0].total_experience if experience else None,
            "salary": experience[0].salary if experience else None,
            "notice_period": experience[0].notice_period if experience else None,
            "employment_type": experience[0].employment_type if experience else None,
            "languages": meta.languages,
            "blood_group": meta.blood_group,
            "marital_status": meta.marital_status,
        } if meta else None,
        "education": [
            {
                "candidate_education_details_id": edu.candidate_education_details_id,
                "education_level": edu.education_level,
                "degree_name": edu.degree_name,
                "specialization": edu.specialization,
                "institution_name": edu.institution_name,
                "university_name": edu.university_name,
                "start_year": edu.start_year,
                "end_year": edu.end_year,
                "percentage": float(edu.percentage) if edu.percentage else None,
                "cgpa": float(edu.cgpa) if edu.cgpa else None,
            }
            for edu in education
        ],
        "experience": [
            {
                "candidate_experience_id": exp.candidate_experience_id,
                "company_name": exp.company_name,
                "job_title": exp.designation,
                "employment_type": exp.employment_type,
                "start_date": exp.start_date.strftime("%Y-%m") if hasattr(exp.start_date, 'strftime') else (exp.start_date[:7] if exp.start_date else None),
                "end_date": exp.end_date.strftime("%Y-%m") if hasattr(exp.end_date, 'strftime') else (exp.end_date[:7] if exp.end_date else None),
                "total_experience": exp.total_experience,
                "location": exp.location,
                "description": exp.description,
            }
            for exp in experience
        ]
    }


def update_candidate_profile_db(db: Session, user_id: int, data: dict) -> dict:
    """Updates candidate users, candidate_metadata, candidate_education_details, and candidate_experience tables."""
    from datetime import date
    from app.models import CandidateMetadata, CandidateEducationDetail, CandidateExperience
    
    user = db.query(Users).filter(Users.user_id == user_id, Users.user_status == 1).first()
    if not user:
        raise HTTPException(status_code=404, detail="Candidate not found.")
        
    # 1. Update basic user details
    user.first_name = data.get("first_name", user.first_name)
    user.last_name = data.get("last_name", user.last_name)
    user.gender = data.get("gender", user.gender)
    user.mobile = data.get("mobile", user.mobile)
    if "image_path" in data:
        user.image_path = data["image_path"]
        
    # 2. Update CandidateMetadata
    meta = db.query(CandidateMetadata).filter(CandidateMetadata.user_id == user_id).first()
    if not meta:
        meta = CandidateMetadata(user_id=user_id)
        db.add(meta)
        
    metadata_in = data.get("metadata")
    if metadata_in:
        dob_str = metadata_in.get("date_of_birth")
        if dob_str:
            meta.date_of_birth = date.fromisoformat(dob_str)
        elif "date_of_birth" in metadata_in:
            meta.date_of_birth = None
            
        meta.personal_address = metadata_in.get("personal_address", meta.personal_address)
        meta.city = metadata_in.get("city", meta.city)
        meta.state = metadata_in.get("state", meta.state)
        meta.country = metadata_in.get("country", meta.country)
        meta.pincode = metadata_in.get("pincode", meta.pincode)
        meta.resume_doc = metadata_in.get("resume_doc", meta.resume_doc)
        meta.profile_status = "complete"
        
        meta.about = metadata_in.get("about", meta.about)
        meta.languages = metadata_in.get("languages", meta.languages)
        meta.blood_group = metadata_in.get("blood_group", meta.blood_group)
        meta.marital_status = metadata_in.get("marital_status", meta.marital_status)
        
        skills = metadata_in.get("skills")
        if isinstance(skills, list):
            import json
            meta.skills = json.dumps([s.strip() for s in skills if s.strip()])
        elif skills is None and "skills" in metadata_in:
            meta.skills = None
            
    # 3. Update Education Details (delete and recreate)
    education_in = data.get("education")
    if education_in is not None:
        db.query(CandidateEducationDetail).filter(CandidateEducationDetail.user_id == user_id).delete()
        for edu in education_in:
            new_edu = CandidateEducationDetail(
                user_id=user_id,
                education_level=edu.get("education_level") or edu.get("degree_name") or "Degree",
                degree_name=edu.get("degree_name"),
                specialization=edu.get("specialization"),
                institution_name=edu.get("institution_name"),
                university_name=edu.get("university_name"),
                start_year=edu.get("start_year"),
                end_year=edu.get("end_year"),
                percentage=edu.get("percentage"),
                cgpa=edu.get("cgpa")
            )
            db.add(new_edu)
            
    # 4. Update Experience Details (delete and recreate)
    experience_in = data.get("experience") or []
    metadata_in = data.get("metadata", {})
    
    # Check if there are summary details in the metadata
    has_summary = any(metadata_in.get(k) for k in ["designation", "company", "salary",  "notice_period"])
    
    db.query(CandidateExperience).filter(CandidateExperience.user_id == user_id).delete()
    
    if experience_in:
        for i, exp in enumerate(experience_in):
            start_date_val = None
            start_str = exp.get("start_date")
            if start_str:
                if len(start_str) == 7:
                    start_str += "-01"
                
            end_date_val = None
            end_str = exp.get("end_date")
            if end_str:
                if len(end_str) == 7:
                    end_str += "-01"
                
            new_exp = CandidateExperience(
                user_id=user_id,
                company_name=exp.get("company_name", "Unknown"),
                designation=exp.get("job_title", "Unknown"),
                employment_type=exp.get("employment_type", "Full-time"),
                start_date=start_str or "Unknown",
                end_date=end_str or "Unknown",
                total_experience=exp.get("total_experience"),
                description=exp.get("description"),
            )
            
            # Map the summary fields to the primary/first experience record
            if i == 0 and has_summary:
                new_exp.salary = metadata_in.get("salary")
                new_exp.notice_period = metadata_in.get("notice_period")
                # Also capture the total experience and designation if it was updated in the summary form
                new_exp.total_experience = metadata_in.get("experience", new_exp.total_experience)
                new_exp.designation = metadata_in.get("designation", new_exp.designation)
                new_exp.company_name = metadata_in.get("company", new_exp.company_name)
                
            db.add(new_exp)
    elif has_summary:
        # Create a single record for the summary if no historical experiences provided
        new_exp = CandidateExperience(
            user_id=user_id,
            company_name=metadata_in.get("company", "Unknown"),
            designation=metadata_in.get("designation", "Unknown"),
            employment_type=metadata_in.get("employment_type", "Full-time"),
            total_experience=metadata_in.get("experience"),
            salary=metadata_in.get("salary"),
            notice_period=metadata_in.get("notice_period"),
            start_date="Unknown",
            end_date="Unknown"
        )
        db.add(new_exp)
            
    db.commit()
    return get_candidate_profile_db(db, user_id)


def get_interviewers_db(db: Session) -> list:
    """Returns all admins with role_id=3 (interviewers) as a list of dicts."""
    interviewers = (
        db.query(Admins)
        .filter(Admins.role_id == 3, Admins.is_active == 1)
        .all()
    )
    return [
        {
            "id": i.admin_id,
            "email": i.email,
            "name": i.school_name or i.email  # fallback to email if name not set
        }
        for i in interviewers
    ]

def update_candidate_resume_db(db: Session, user_id: int, resume_path: str) -> dict:
    """Updates candidate's resume_doc path."""
    from app.models import CandidateMetadata
    
    meta = db.query(CandidateMetadata).filter(CandidateMetadata.user_id == user_id).first()
    if not meta:
        meta = CandidateMetadata(user_id=user_id)
        db.add(meta)
    
    meta.resume_doc = resume_path
    db.commit()
    return {"message": "Resume uploaded successfully", "resume_doc": resume_path}

def update_candidate_profile_image_db(db: Session, user_id: int, image_path: str) -> dict:
    """Updates candidate's profile image path in the users table."""
    user = db.query(Users).filter(Users.user_id == user_id, Users.user_status == 1).first()
    if not user:
        raise HTTPException(status_code=404, detail="Candidate not found.")
        
    user.image_path = image_path
    db.commit()
    return {"message": "Profile image uploaded successfully", "image_path": image_path}


def get_user_by_mobile(db: Session, mobile: str):
    # Normalise to last 10 digits so we match regardless of stored format
    digits = "".join(filter(str.isdigit, mobile))[-10:]
    return (
        db.query(Users)
        .filter(
            Users.mobile.in_([digits, f"+91{digits}"]),
            Users.user_status == 1,
        )
        .first()
    )


def store_otp(db: Session, user_id: int, otp: int, purpose: str = "password update"):
    from app.models.otp_logs_model import OTPLog
    # Invalidate previous unverified OTPs for this user and purpose
    db.query(OTPLog).filter(
        OTPLog.user_id == user_id, 
        OTPLog.purpose == purpose, 
        OTPLog.is_verified == 0
    ).update({"is_verified": -1})
    
    otp_log = OTPLog(user_id=user_id, otp=otp, is_verified=0, purpose=purpose)
    db.add(otp_log)
    db.commit()


def verify_otp(db: Session, user_id: int, otp: int, purpose: str = "password update") -> bool:
    from app.models.otp_logs_model import OTPLog
    
    # Validity is 90 seconds
    time_threshold = datetime.now(timezone.utc) - timedelta(seconds=90)
    
    otp_log = db.query(OTPLog).filter(
        OTPLog.user_id == user_id,
        OTPLog.otp == otp,
        OTPLog.purpose == purpose,
        OTPLog.is_verified == 0,
        OTPLog.created_at >= time_threshold
    ).order_by(OTPLog.created_at.desc()).first()
    
    if otp_log:
        otp_log.is_verified = 1
        db.commit()
        return True
    return False


def update_user_password(db: Session, user_id: int, new_password: str) -> bool:
    user = db.query(Users).filter(Users.user_id == user_id, Users.user_status == 1).first()
    if user:
        user.password = get_password_hash(new_password)
        db.commit()
        return True
    return False
