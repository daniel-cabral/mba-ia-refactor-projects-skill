import logging
import smtplib

logger = logging.getLogger(__name__)


class NotificationService:
    """Sends e-mail notifications. SMTP settings are injected (see config.settings.Settings)."""

    def __init__(self, host, port, user, password):
        self.email_host = host
        self.email_port = port
        self.email_user = user
        self.email_password = password

    def send_email(self, to, subject, body):
        try:
            server = smtplib.SMTP(self.email_host, self.email_port)
            server.starttls()
            server.login(self.email_user, self.email_password)
            message = f"Subject: {subject}\n\n{body}"
            server.sendmail(self.email_user, to, message)
            server.quit()
            logger.info('Email sent for subject %r', subject)
            return True
        except (smtplib.SMTPException, OSError):
            logger.exception('Failed to send email')
            return False

    def notify_task_assigned(self, user, task):
        subject = f"Nova task atribuída: {task.title}"
        body = (
            f"Olá {user.name},\n\nA task '{task.title}' foi atribuída a você."
            f"\n\nPrioridade: {task.priority}\nStatus: {task.status}"
        )
        return self.send_email(user.email, subject, body)

    def notify_task_overdue(self, user, task):
        subject = f"Task atrasada: {task.title}"
        body = f"Olá {user.name},\n\nA task '{task.title}' está atrasada!\n\nData limite: {task.due_date}"
        return self.send_email(user.email, subject, body)
