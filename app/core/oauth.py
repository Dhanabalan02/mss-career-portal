import requests
from fastapi import HTTPException, status
from app.core.config import settings
from app.core.logger import logger

GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"

LINKEDIN_TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
LINKEDIN_USERINFO_URL = "https://api.linkedin.com/v2/userinfo"


def get_google_user_info(code: str) -> dict:
    """Exchanges a Google OAuth authorization code for the user's email and name."""
    token_response = requests.post(
        GOOGLE_TOKEN_URL,
        data={
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        },
    )
    if not token_response.ok:
        logger.warning(f"Google token exchange failed: {token_response.text}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Google authentication failed.")

    access_token = token_response.json().get("access_token")

    userinfo_response = requests.get(
        GOOGLE_USERINFO_URL,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    if not userinfo_response.ok:
        logger.warning(f"Google userinfo fetch failed: {userinfo_response.text}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Google authentication failed.")

    userinfo = userinfo_response.json()
    return {"email": userinfo.get("email"), "name": userinfo.get("name")}


def get_linkedin_user_info(code: str) -> dict:
    """Exchanges a LinkedIn OAuth authorization code for the user's email and name."""
    token_response = requests.post(
        LINKEDIN_TOKEN_URL,
        data={
            "code": code,
            "client_id": settings.LINKEDIN_CLIENT_ID,
            "client_secret": settings.LINKEDIN_CLIENT_SECRET,
            "redirect_uri": settings.LINKEDIN_REDIRECT_URI,
            "grant_type": "authorization_code",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    if not token_response.ok:
        logger.warning(f"LinkedIn token exchange failed: {token_response.text}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="LinkedIn authentication failed.")

    access_token = token_response.json().get("access_token")

    userinfo_response = requests.get(
        LINKEDIN_USERINFO_URL,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    if not userinfo_response.ok:
        logger.warning(f"LinkedIn userinfo fetch failed: {userinfo_response.text}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="LinkedIn authentication failed.")

    userinfo = userinfo_response.json()
    return {"email": userinfo.get("email"), "name": userinfo.get("name")}
