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

class InterviewService:
    def __init__(self):
        self.api_url = "https://wb.omni.tatatelebusiness.com/whatsapp-cloud/messages"
        self.api_key = settings.OMNI_PORTAL_API_KEY

    def send_interview_scheduled(
        self,
        to: str,
        candidate_name: str,
        job_title: str,
        interview_mode: str,
        interview_date_time: str,
        interview_type: str,
        interview_link_location: str,
    ) -> dict:

        if getattr(settings, "ENABLE_EXTERNAL_SERVICES", True) is False:
            logger.info("External services disabled. Skipping notification.")
            return {"success": True, "http_code": 200, "response": "Service disabled"}

        formatted_to = normalize_whatsapp_number(to)

        label = "Meeting URL" if "online" in str(interview_mode).lower() else "Location"

        payload = {
            "to": formatted_to,
            "type": "template",
            "template": {
                "name": "interview_schedule",
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
                                "text": interview_type
                            },
                            {
                                "type": "text",
                                "text": interview_mode
                            },
                            {
                                "type": "text",
                                "text": interview_date_time
                            },
                            {
                                "type": "text",
                                "text": label
                            },
                            {
                                "type": "text",
                                "text": interview_link_location
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
            "[INTERVIEW SCHEDULED] Sending notification to=%s job=%s",
            formatted_to,
            job_title
        )

        logger.debug("[INTERVIEW SCHEDULED] Payload: %s", payload)
        logger.debug("[INTERVIEW SCHEDULED] Headers: %s", headers)
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
                    "[INTERVIEW SCHEDULED] Sent successfully status=%s body=%s",
                    response.status_code,
                    body
                )
            else:
                logger.error(
                    "[INTERVIEW SCHEDULED] Failed status=%s body=%s",
                    response.status_code,
                    body
                )

            return {
                "success": success,
                "http_code": response.status_code,
                "response": body,
            }

        except requests.exceptions.RequestException as e:
            logger.exception("[INTERVIEW SCHEDULED] Request exception: %s", e)

            return {
                "success": False,
                "http_code": 500,
                "response": f"Request error: {str(e)}",
            }
            
    def send_interview_rescheduled(
        self,
        to: str,
        candidate_name: str,
        job_title: str,
        interview_mode: str,
        interview_new_date_time: str,
        interview_type: str,
        interview_link_location: str,
        rescheduled_reason: str,
    ) -> dict:

        if getattr(settings, "ENABLE_EXTERNAL_SERVICES", True) is False:
            logger.info("External services disabled. Skipping notification.")
            return {"success": True, "http_code": 200, "response": "Service disabled"}

        formatted_to = normalize_whatsapp_number(to)

        label = "Meeting URL" if "online" in str(interview_mode).lower() else "Location"

        payload = {
            "to": formatted_to,
            "type": "template",
            "template": {
                "name": "interview_reschedule",
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
                                "text": interview_type
                            },
                            {
                                "type": "text",
                                "text": interview_mode
                            },
                            {
                                "type": "text",
                                "text": interview_new_date_time
                            },
                            {
                                "type": "text",
                                "text": label
                            },
                            {
                                "type": "text",
                                "text": interview_link_location
                            },
                            {
                                "type": "text",
                                "text": rescheduled_reason
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
            "[INTERVIEW RESCHEDULED] Sending notification to=%s job=%s",
            formatted_to,
            job_title
        )

        logger.debug("[INTERVIEW RESCHEDULED] Payload: %s", payload)
        
        logger.debug("[INTERVIEW RESCHEDULED] Headers: %s", headers)

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
                    "[INTERVIEW RESCHEDULED] Sent successfully status=%s body=%s",
                    response.status_code,
                    body
                )
            else:
                logger.error(
                    "[INTERVIEW RESCHEDULED] Failed status=%s body=%s",
                    response.status_code,
                    body
                )

            return {
                "success": success,
                "http_code": response.status_code,
                "response": body,
            }

        except requests.exceptions.RequestException as e:
            logger.exception("[INTERVIEW RESCHEDULED] Request exception: %s", e)

            return {
                "success": False,
                "http_code": 500,
                "response": f"Request error: {str(e)}",
            }
                        
    def send_interview_cancel(
        self,
        to: str,
        candidate_name: str,
        job_title: str,
        interview_round: str,
        interview_date_time: str,
        cancel_reason: str,
    ) -> dict:

        if getattr(settings, "ENABLE_EXTERNAL_SERVICES", True) is False:
            logger.info("External services disabled. Skipping notification.")
            return {"success": True, "http_code": 200, "response": "Service disabled"}

        formatted_to = normalize_whatsapp_number(to)

        payload = {
            "to": formatted_to,
            "type": "template",
            "template": {
                "name": "interview_cancellation",
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
                                "text": interview_round
                            },
                            {
                                "type": "text",
                                "text": interview_date_time
                            },
                            {
                                "type": "text",
                                "text": cancel_reason
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
            "[INTERVIEW CANCELLED] Sending notification to=%s job=%s",
            formatted_to,
            job_title
        )

        logger.debug("[INTERVIEW CANCELLED] Payload: %s", payload)

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
                    "[INTERVIEW CANCELLED] Sent successfully status=%s body=%s",
                    response.status_code,
                    body
                )
            else:
                logger.error(
                    "[INTERVIEW CANCELLED] Failed status=%s body=%s",
                    response.status_code,
                    body
                )

            return {
                "success": success,
                "http_code": response.status_code,
                "response": body,
            }

        except requests.exceptions.RequestException as e:
            logger.exception("[INTERVIEW CANCELLED] Request exception: %s", e)

            return {
                "success": False,
                "http_code": 500,
                "response": f"Request error: {str(e)}",
            }
            
    def send_admin_interview_schedule(
        self,
        to: str,
        job_title: str,
        candidate_name: str,
        interview_round: str,
        interview_mode: str,
        interview_date_time: str,
        interview_link_location: str,
    ) -> dict:

        if getattr(settings, "ENABLE_EXTERNAL_SERVICES", True) is False:
            logger.info("External services disabled. Skipping notification.")
            return {"success": True, "http_code": 200, "response": "Service disabled"}

        formatted_to = normalize_whatsapp_number(to)

        label = "Meeting URL" if "online" in str(interview_mode).lower() else "Location"

        payload = {
            "to": formatted_to,
            "type": "template",
            "template": {
                "name": "admin_interview_schedule",
                "language": {
                    "code": "en"
                },
                "components": [
                    {
                        "type": "body",
                        "parameters": [
                            {
                                "type": "text",
                                "text": job_title
                            },
                            {
                                "type": "text",
                                "text": candidate_name
                            },
                            {
                                "type": "text",
                                "text": interview_round
                            },
                            {
                                "type": "text",
                                "text": interview_mode
                            },
                            {
                                "type": "text",
                                "text": interview_date_time
                            },
                            {
                                "type": "text",
                                "text": label
                            },
                            {
                                "type": "text",
                                "text": interview_link_location
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
            "[ADMIN INTERVIEW SCHEDULED] Sending notification to=%s job=%s",
            formatted_to,
            job_title
        )

        logger.debug("[ADMIN INTERVIEW SCHEDULED] Payload: %s", payload)

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
                    "[ADMIN INTERVIEW SCHEDULED] Sent successfully status=%s body=%s",
                    response.status_code,
                    body
                )
            else:
                logger.error(
                    "[ADMIN INTERVIEW SCHEDULED] Failed status=%s body=%s",
                    response.status_code,
                    body
                )

            return {
                "success": success,
                "http_code": response.status_code,
                "response": body,
            }

        except requests.exceptions.RequestException as e:
            logger.exception("[ADMIN INTERVIEW SCHEDULED] Request exception: %s", e)

            return {
                "success": False,
                "http_code": 500,
                "response": f"Request error: {str(e)}",
            }
            
    def send_admin_interview_reschedule(
        self,
        to: str,
        job_title: str,
        candidate_name: str,
        interview_round: str,
        interview_mode: str,
        interview_new_date_time: str,
        interview_link_location: str,
    ) -> dict:

        if getattr(settings, "ENABLE_EXTERNAL_SERVICES", True) is False:
            logger.info("External services disabled. Skipping notification.")
            return {"success": True, "http_code": 200, "response": "Service disabled"}

        formatted_to = normalize_whatsapp_number(to)

        label = "Meeting URL" if "online" in str(interview_mode).lower() else "Location"

        payload = {
            "to": formatted_to,
            "type": "template",
            "template": {
                "name": "admin_interview_rescheduled",
                "language": {
                    "code": "en"
                },
                "components": [
                    {
                        "type": "body",
                        "parameters": [
                            {
                                "type": "text",
                                "text": job_title
                            },
                            {
                                "type": "text",
                                "text": candidate_name
                            },
                            {
                                "type": "text",
                                "text": interview_round
                            },
                            {
                                "type": "text",
                                "text": interview_mode
                            },
                            {
                                "type": "text",
                                "text": interview_new_date_time
                            },
                            {
                                "type": "text",
                                "text": label
                            },
                            {
                                "type": "text",
                                "text": interview_link_location
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
            "[ADMIN INTERVIEW RESCHEDULED] Sending notification to=%s job=%s",
            formatted_to,
            job_title
        )

        logger.debug("[ADMIN INTERVIEW RESCHEDULED] Payload: %s", payload)

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
                    "[ADMIN INTERVIEW RESCHEDULED] Sent successfully status=%s body=%s",
                    response.status_code,
                    body
                )
            else:
                logger.error(
                    "[ADMIN INTERVIEW RESCHEDULED] Failed status=%s body=%s",
                    response.status_code,
                    body
                )

            return {
                "success": success,
                "http_code": response.status_code,
                "response": body,
            }

        except requests.exceptions.RequestException as e:
            logger.exception("[ADMIN INTERVIEW RESCHEDULED] Request exception: %s", e)

            return {
                "success": False,
                "http_code": 500,
                "response": f"Request error: {str(e)}",
            }
            
    def send_admin_interview_cancel(
        self,
        to: str,
        job_title: str,
        candidate_name: str,
        interview_round: str,
        interview_date_time: str,
        cancel_reason: str,
    ) -> dict:

        if getattr(settings, "ENABLE_EXTERNAL_SERVICES", True) is False:
            logger.info("External services disabled. Skipping notification.")
            return {"success": True, "http_code": 200, "response": "Service disabled"}

        formatted_to = normalize_whatsapp_number(to)

        payload = {
            "to": formatted_to,
            "type": "template",
            "template": {
                "name": "admin_interview_cancelled",
                "language": {
                    "code": "en"
                },
                "components": [
                    {
                        "type": "body",
                        "parameters": [
                            {
                                "type": "text",
                                "text": job_title
                            },
                            {
                                "type": "text",
                                "text": candidate_name
                            },
                            {
                                "type": "text",
                                "text": interview_round
                            },
                            {
                                "type": "text",
                                "text": interview_date_time
                            },
                            {
                                "type": "text",
                                "text": cancel_reason
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
            "[ADMIN INTERVIEW CANCELLED] Sending notification to=%s job=%s",
            formatted_to,
            job_title
        )

        logger.debug("[ADMIN INTERVIEW CANCELLED] Payload: %s", payload)

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
                    "[ADMIN INTERVIEW CANCELLED] Sent successfully status=%s body=%s",
                    response.status_code,
                    body
                )
            else:
                logger.error(
                    "[ADMIN INTERVIEW CANCELLED] Failed status=%s body=%s",
                    response.status_code,
                    body
                )

            return {
                "success": success,
                "http_code": response.status_code,
                "response": body,
            }

        except requests.exceptions.RequestException as e:
            logger.exception("[ADMIN INTERVIEW CANCELLED] Request exception: %s", e)

            return {
                "success": False,
                "http_code": 500,
                "response": f"Request error: {str(e)}",
            }

    def send_interview_feedback(
        self,
        to: str,
        candidate_name: str,
        job_title: str,
        status: str,
        description: str,
    ) -> dict:

        if getattr(settings, "ENABLE_EXTERNAL_SERVICES", True) is False:
            logger.info("External services disabled. Skipping notification.")
            return {"success": True, "http_code": 200, "response": "Service disabled"}

        formatted_to = normalize_whatsapp_number(to)

        payload = {
            "to": formatted_to,
            "type": "template",
            "template": {
                "name": "interview_feedback",
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
                                "text": status
                            },
                            {
                                "type": "text",
                                "text": description
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
            "[INTERVIEW FEEDBACK] Sending notification to=%s job=%s",
            formatted_to,
            job_title
        )

        logger.debug("[INTERVIEW FEEDBACK] Payload: %s", payload)

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
                    "[INTERVIEW FEEDBACK] Sent successfully status=%s body=%s",
                    response.status_code,
                    body
                )
            else:
                logger.error(
                    "[INTERVIEW FEEDBACK] Failed status=%s body=%s",
                    response.status_code,
                    body
                )

            return {
                "success": success,
                "http_code": response.status_code,
                "response": body,
            }

        except requests.exceptions.RequestException as e:
            logger.exception("[INTERVIEW FEEDBACK] Request exception: %s", e)

            return {
                "success": False,
                "http_code": 500,
                "response": f"Request error: {str(e)}",
            }

            
        
    