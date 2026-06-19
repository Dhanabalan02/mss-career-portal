from datetime import datetime, timedelta, timezone
from hmac import compare_digest
from typing import Any, Dict, Optional
import jwt
from passlib.context import CryptContext
from passlib.exc import UnknownHashError
from app.core.config import settings
import secrets
import string
from app.core.logger import logger

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"


def get_password_hash(password: str) -> str:
    """Hashes a plain text password for secure storage in the database."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compares a plain text password with a hashed database password."""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except UnknownHashError:
        return compare_digest(plain_password, hashed_password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Generates a secure JWT access token containing session metadata."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def generate_otp(length: int = 6) -> str:

    """Generates a secure random OTP consisting of digits."""
    digits = string.digits
    otp = ''.join(secrets.choice(digits) for _ in range(length))
    logger.info(f"Generated OTP: {otp} (length: {length})")
    return otp
