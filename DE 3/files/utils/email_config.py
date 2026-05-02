"""
Email Configuration and Alert Service
Handles email notifications for temperature alerts.
"""

import os
from typing import Dict, Optional
from datetime import datetime, timezone, timedelta

# Indian Standard Time (UTC+5:30)
IST = timezone(timedelta(hours=5, minutes=30))


class EmailAlert:
    """
    Email alert service for temperature monitoring.
    """
    
    def __init__(self, smtp_server: str = "", smtp_port: int = 587, 
                 sender_email: str = "", sender_password: str = ""):
        """
        Initialize email alert service.
        
        Args:
            smtp_server: SMTP server address
            smtp_port: SMTP port
            sender_email: Sender email address
            sender_password: Sender password
        """
        self.smtp_server = smtp_server or os.getenv("SMTP_SERVER", "")
        self.smtp_port = smtp_port or int(os.getenv("SMTP_PORT", "587"))
        self.sender_email = sender_email or os.getenv("SENDER_EMAIL", "")
        self.sender_password = sender_password or os.getenv("SENDER_PASSWORD", "")
        self.alert_log = []
    
    def send_alert(self, recipient_email: str, subject: str, 
                   alert_data: Dict) -> bool:
        """
        Send email alert for temperature anomaly.
        
        Args:
            recipient_email: Recipient email address
            subject: Email subject
            alert_data: Alert details
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Log the alert attempt
            log_entry = {
                "timestamp": datetime.now(IST),
                "recipient": recipient_email,
                "subject": subject,
                "status": "attempted",
                "alert_data": alert_data
            }
            self.alert_log.append(log_entry)
            
            # For now, we'll just log instead of actually sending emails
            # In production, you'd use smtplib here
            print(f"📧 Email alert logged (not sent in demo mode)")
            print(f"   To: {recipient_email}")
            print(f"   Subject: {subject}")
            print(f"   Alert: {alert_data}")
            
            return True
        
        except Exception as e:
            print(f"❌ Error sending email alert: {e}")
            return False
    
    def get_alert_log(self) -> list:
        """Get log of all alert emails."""
        return self.alert_log


# Global instance for Flask routes
email_alert_service = EmailAlert()
