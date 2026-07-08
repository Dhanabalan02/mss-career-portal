import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.sender_email = settings.SENDER_EMAIL
        self.sender_password = settings.SENDER_PASSWORD

    def send_otp_email(self, to_email: str, otp: str) -> dict:
        subject = "Your Verification Code"
        body = f"Hello,\n\nYour 4-digit verification code is: {otp}\n\nPlease do not share this code with anyone. It will expire in 10 minutes.\n\nBest regards,\nMSS Career Portal Team"

        msg = MIMEMultipart()
        msg['From'] = self.sender_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)

            logger.info(f"[OTP Email] Sent successfully to {to_email}")
            return {"success": True, "message": "Email sent successfully."}
        except Exception as e:
            logger.exception(f"[OTP Email] Failed to send email to {to_email}: {e}")
            return {"success": False, "message": str(e)}
