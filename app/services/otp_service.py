import re
import logging
import requests
from app.core.config import settings

logger = logging.getLogger(__name__)


def normalize_whatsapp_number(mobile: str) -> str:
    """Return E.164 format (+91XXXXXXXXXX) for an Indian mobile number."""
    digits = re.sub(r"\D", "", mobile)
    if len(digits) == 10:
        return f"+91{digits}"
    if len(digits) == 12 and digits.startswith("91"):
        return f"+{digits}"
    if len(digits) > 10:
        return f"+{digits}"
    return mobile  # fallback — pass as-is


class OtpService:
    def __init__(self):
        # 1. Configured to hit Smartflo's production API URL
        self.api_url = "https://wb.omni.tatatelebusiness.com/whatsapp-cloud/messages"
        
        # 2. FIX: Pulled dynamically from your environment settings instead of hardcoding
        self.api_key = settings.WHATSAPP_API_KEY 

    def send_otp_message(self, to: str, otp: str) -> dict:
        formatted_to = normalize_whatsapp_number(to)
        template_name = "otp_service"
        language = "en"

        payload = {
            "to": formatted_to,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": language},
                "components": [
                    {
                        "type": "body",
                        "parameters": [
                            {"type": "text", "text": otp}
                        ]
                    },
                    {
                        "type": "button",
                        "sub_type": "url",
                        "index": 0,
                        "parameters": [
                            {"type": "text", "text": otp}
                        ]
                    }
                ]
            }
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        logger.info("[OTP] Sending to=%s otp=%s", formatted_to, otp)
        logger.debug("[OTP] Payload: %s", payload)

        try:
            response = requests.post(self.api_url, json=payload, headers=headers, timeout=10)
            body = {}
            try:
                body = response.json()
            except Exception:
                body = {"raw": response.text}

            success = 200 <= response.status_code < 300
            if success:
                logger.info("[OTP] Sent OK  status=%s body=%s", response.status_code, body)
            else:
                logger.error("[OTP] Failed  status=%s body=%s", response.status_code, body)

            return {
                "success": success,
                "http_code": response.status_code,
                "response": body,
            }

        except requests.exceptions.RequestException as e:
            logger.exception("[OTP] Request exception: %s", e)
            return {
                "success": False,
                "http_code": 500,
                "response": f"Request error: {str(e)}",
            }