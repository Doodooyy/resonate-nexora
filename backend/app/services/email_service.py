import smtplib
import logging
from email.message import EmailMessage
from typing import List, Dict, Any
from app.core.config import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("email_service")
settings = get_settings()

def send_decision_emails(job_title: str, company: str, decisions: List[Dict[str, Any]]):
    """
    Sends actual acceptance and rejection emails via SMTP.
    decisions: list of dicts with 'name', 'email', 'status' (shortlisted/rejected)
    """
    if not settings.SMTP_USERNAME or not settings.SMTP_PASSWORD:
        logger.warning("SMTP credentials not configured. Falling back to mock email logging.")
        _mock_send_emails(job_title, company, decisions)
        return

    logger.info(f"Connecting to SMTP server at {settings.SMTP_SERVER}:{settings.SMTP_PORT}...")
    
    try:
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            
            for d in decisions:
                msg = EmailMessage()
                msg['Subject'] = f"Update regarding your application for {job_title}"
                msg['From'] = f"{company} Recruiting <{settings.SMTP_USERNAME}>"
                msg['To'] = d['email']
                
                if d['status'] == "shortlisted":
                    content = f"""Dear {d['name']},

Congratulations! We are thrilled to inform you that you have been shortlisted for the {job_title} role at {company}.
Your application strongly aligned with our requirements, particularly your evidence of past projects.
A recruiter will be in touch shortly to schedule your first interview.

Best regards,
The {company} Hiring Team"""
                else:
                    content = f"""Dear {d['name']},

Thank you for applying to the {job_title} role at {company}. We appreciate the time you took to share your background with us.
While your profile is impressive, we have decided to move forward with other candidates whose experience more closely matches our specific requirements at this time.
We wish you the best in your job search.

Best regards,
The {company} Hiring Team"""

                msg.set_content(content)
                server.send_message(msg)
                logger.info(f"Successfully sent email to {d['email']}")
                
    except Exception as e:
        logger.error(f"Failed to send emails: {str(e)}")

def _mock_send_emails(job_title: str, company: str, decisions: List[Dict[str, Any]]):
    """Fallback mock email sender if credentials are not provided."""
    for d in decisions:
        logger.info("\n" + "-"*40)
        logger.info(f"MOCK TO: {d['email']}")
        logger.info(f"STATUS: {d['status'].upper()}")
        logger.info("-" * 40)
