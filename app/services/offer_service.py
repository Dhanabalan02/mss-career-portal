import re
import requests
from app.core.config import settings
from app.core.logger import offer_logger


def normalize_whatsapp_number(mobile: str) -> str:
    digits = re.sub(r"\D", "", mobile)

    if len(digits) == 10:
        return f"+91{digits}"
    if len(digits) == 12 and digits.startswith("91"):
        return f"+{digits}"
    if len(digits) > 10:
        return f"+{digits}"

    return mobile


class OfferService:
    def __init__(self):
        self.api_url = "https://wb.omni.tatatelebusiness.com/whatsapp-cloud/messages"
        self.api_key = settings.WHATSAPP_API_KEY

    def issue_offer(
        self,
        to: str,
        candidate_name: str,
        job_title: str,
        document_url: str,
        filename: str = "Offer_Letter.pdf",
    ) -> dict:
        offer_logger.info(f"[OFFER] issue_offer called with to={to}, candidate_name={candidate_name}, job_title={job_title}, document_url={document_url}, filename={filename}")

        if getattr(settings, "ENABLE_EXTERNAL_SERVICES", True) is False:
            offer_logger.info("[OFFER] External services disabled. Skipping offer generation.")
            return {"success": True, "http_code": 200, "response": "Service disabled"}

        formatted_to = normalize_whatsapp_number(to)
        offer_logger.info(f"[OFFER] Normalized WhatsApp number: {formatted_to} (original: {to})")

        payload = {
            "to": formatted_to,
            "type": "template",
            "template": {
                "name": "issue_offer",
                "language": {
                    "code": "en"
                },
                "components": [
                    {
                        "type": "header",
                        "parameters": [
                            {
                                "type": "document",
                                "document": {
                                    "link": document_url,
                                    "filename": filename
                                }
                            }
                        ]
                    },
                    {
                        "type": "body",
                        "parameters": [
                            {
                                "type": "text",
                                "text": candidate_name  # Maps to {{1}}
                            },
                            {
                                "type": "text",
                                "text": job_title       # Maps to {{2}}
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

        offer_logger.info(
            "[OFFER] Sending offer letter to=%s job=%s",
            formatted_to,
            job_title
        )

        offer_logger.debug("[OFFER] Payload: %s", payload)

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
                offer_logger.info(
                    "[OFFER] Sent successfully status=%s body=%s",
                    response.status_code,
                    body
                )
            else:
                offer_logger.error(
                    "[OFFER] Failed status=%s body=%s",
                    response.status_code,
                    body
                )

            return {
                "success": success,
                "http_code": response.status_code,
                "response": body,
            }

        except requests.exceptions.RequestException as e:
            offer_logger.exception("[OFFER] Request exception: %s", e)

            return {
                "success": False,
                "http_code": 500,
                "response": f"Request error: {str(e)}",
            }