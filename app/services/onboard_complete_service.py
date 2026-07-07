import re
import logging
import requests
from app.core.config import settings

logger = logging.getLogger(__name__)


def normalize_whatsapp_number(mobile: str) -> str:
    digits = re.sub(r"\D", "", mobile)

    if len(digits) == 10:
        return f"+91{digits}"
    if len(digits) == 12 and digits.startswith("91"):
        return f"+{digits}"
    if len(digits) > 10:
        return f"+{digits}"

    return mobile


class OnboardCompleteService:
    def __init__(self):
        self.api_url = "https://wb.omni.tatatelebusiness.com/whatsapp-cloud/messages"
        self.api_key = settings.WHATSAPP_API_KEY

    def send_onboard_complete(
        self,
        to: str,
        candidate_name: str,
        employee_id: str,
        designation: str,
        department: str,
        date_of_joining: str,
    ) -> dict:

        formatted_to = normalize_whatsapp_number(to)

        payload = {
            "to": formatted_to,
            "type": "template",
            "template": {
                "name": "onboard_completion",
                "language": {
                    "code": "en"
                },
                "components": [
                    {
                        "type": "body",
                        "parameters": [
                            {
                                "type": "text",
                                "text": candidate_name
                            },
                            {
                                "type": "text",
                                "text": employee_id
                            },
                            {
                                "type": "text",
                                "text": designation
                            },
                            {
                                "type": "text",
                                "text": department
                            },
                            {
                                "type": "text",
                                "text": date_of_joining
                            }
                        ]
                    }
                ]
            }
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        logger.info(
            "[ONBOARD_COMPLETE] Sending notification to=%s",
            formatted_to
        )

        logger.debug("[ONBOARD_COMPLETE] Payload: %s", payload)

        try:
            response = requests.post(
                self.api_url,
                json=payload,
                headers=headers,
                timeout=10
            )

            try:
                body = response.json()
            except Exception:
                body = {"raw": response.text}

            success = 200 <= response.status_code < 300

            if success:
                logger.info(
                    "[ONBOARD_COMPLETE] Sent successfully status=%s body=%s",
                    response.status_code,
                    body
                )
            else:
                logger.error(
                    "[ONBOARD_COMPLETE] Failed status=%s body=%s",
                    response.status_code,
                    body
                )

            return {
                "success": success,
                "http_code": response.status_code,
                "response": body,
            }

        except requests.exceptions.RequestException as e:
            logger.exception("[ONBOARD_COMPLETE] Request exception: %s", e)

            return {
                "success": False,
                "http_code": 500,
                "response": f"Request error: {str(e)}",
            }