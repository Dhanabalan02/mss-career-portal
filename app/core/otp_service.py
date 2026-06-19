import requests
from app.core.config import settings

class OtpService:
    def __init__(self):
        self.api_url = "https://wb.omni.tatatelebusiness.com/whatsapp-cloud/messages"
        self.api_key = settings.WHATSAPP_API_KEY

    def send_otp_message(self, to: str, otp: str) -> dict:
        template_name = "otp_service"
        language = "en"

        # Structured exactly like your PHP payload layout
        payload = {
            "to": to,
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

        try:
            response = requests.post(self.api_url, json=payload, headers=headers, timeout=10)
            
            return {
                "success": 200 <= response.status_code < 300,
                "http_code": response.status_code,
                "response": response.json() if response.text else {}
            }
            
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "http_code": 500,
                "response": f"Request error: {str(e)}"
            }
