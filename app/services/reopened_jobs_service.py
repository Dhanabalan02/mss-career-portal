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


class JobReopenedService:
    def __init__(self):
        self.api_url = "https://wb.omni.tatatelebusiness.com/whatsapp-cloud/messages"
        self.api_key = settings.WHATSAPP_API_KEY

    def send_job_reopened_message(
        self,
        to: str,
        candidate_name: str,
        job_title: str,
        company_name: str,
        apply_link: str,
    ) -> dict:

        formatted_to = normalize_whatsapp_number(to)

        payload = {
            "to": formatted_to,
            "type": "template",
            "template": {
                "name": "job_reopened",
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
                                "text": job_title
                            },
                            {
                                "type": "text",
                                "text": company_name
                            },
                            {
                                "type": "text",
                                "text": apply_link
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
            "[JOB_REOPENED] Sending notification to=%s job=%s",
            formatted_to,
            job_title
        )

        logger.debug("[JOB_REOPENED] Payload: %s", payload)

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
                    "[JOB_REOPENED] Sent successfully status=%s body=%s",
                    response.status_code,
                    body
                )
            else:
                logger.error(
                    "[JOB_REOPENED] Failed status=%s body=%s",
                    response.status_code,
                    body
                )

            return {
                "success": success,
                "http_code": response.status_code,
                "response": body,
            }

        except requests.exceptions.RequestException as e:
            logger.exception("[JOB_REOPENED] Request exception: %s", e)

            return {
                "success": False,
                "http_code": 500,
                "response": f"Request error: {str(e)}",
            }