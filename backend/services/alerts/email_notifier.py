import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config.settings import settings

class EmailNotifier:
    def __init__(self):
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.smtp_user = settings.smtp_user
        self.smtp_password = settings.smtp_password
        self.from_email = settings.alert_from_email
    async def send_email_alert(self, recipients: list, alert: dict):
        msg = MIMEMultipart()
        msg['Subject'] = f"[{alert['severity'].upper()}] CloudFlow Alert: {alert['type']}"
        msg['From'] = self.from_email
        msg['To'] = ', '.join(recipients)
        body = f"""Alert Type: {alert['type']}
Severity: {alert['severity']}
Time: {alert['timestamp']}

Message:
{alert['message']}

Alert ID: {alert['alert_id']}
"""
        msg.attach(MIMEText(body, 'plain'))
        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            return True
        except Exception as e:
            print(f"Failed to send email: {str(e)}")
            return False
    async def send_custom_email(self, recipients: list, subject: str, body: str):
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = self.from_email
        msg['To'] = ', '.join(recipients)
        msg.attach(MIMEText(body, 'plain'))
        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            return True
        except Exception as e:
            print(f"Failed to send email: {str(e)}")
            return False
