import os
from abc import ABC, abstractmethod
from email.message import EmailMessage as SMTPEmailMessage

from aiosmtplib import SMTP
import resend

from src.core.config.settings import config
from src.shared.infrastructure.logger import logger


class IEmailProvider(ABC):
    """
    Interface for email sending providers/vendors
    """

    @abstractmethod
    async def send_email(
        self,
        *,
        sender: str,
        recipients: list[str],
        subject: str,
        html_body: str,
    ) -> None:
        """
        Send an email notification using a specific vendor client.
        """
        pass


class SMTPProvider(IEmailProvider):
    """
    SMTP Email Provider (standard python aiosmtplib wrapper)
    """

    async def send_email(
        self,
        *,
        sender: str,
        recipients: list[str],
        subject: str,
        html_body: str,
    ) -> None:
        msg = SMTPEmailMessage()
        msg["To"] = ", ".join(recipients)
        msg["Subject"] = subject
        msg["From"] = sender

        msg.set_content("Please view this email in an HTML-compatible email viewer.")
        msg.add_alternative(
            html_body,
            subtype="html",
        )

        smtp = SMTP(
            hostname=config.SMTP_HOST,
            port=config.SMTP_PORT,
            timeout=30,
        )

        try:
            logger.info(
                f"[SMTP-Email] Connecting to SMTP server "
                f"{config.SMTP_HOST}:{config.SMTP_PORT}"
            )
            await smtp.connect()

            logger.info("[SMTP-Email] Logging in")
            await smtp.login(
                config.SMTP_USERNAME,
                config.SMTP_PASSWORD,
            )

            logger.info(f"[SMTP-Email] Sending email to {msg['To']}")
            await smtp.send_message(msg)
            logger.success(
                f"[SMTP-Email] Email sent successfully to {msg['To']} with subject '{msg['Subject']}'"
            )
        except TimeoutError:
            logger.error(f"[SMTP-Email] Timeout while sending email to {msg['To']}")
            raise
        except Exception as e:
            logger.error(f"[SMTP-Email] Failed to send email to {msg['To']}: {e!s}")
            raise
        finally:
            try:
                await smtp.quit()
            except Exception:
                pass


class ResendProvider(IEmailProvider):
    """
    Resend Email Provider using Resend Python SDK
    """

    def __init__(self) -> None:
        self.api_key = config.RESEND_API_KEY or os.environ.get("RESEND_API_KEY")

    async def send_email(
        self,
        *,
        sender: str,
        recipients: list[str],
        subject: str,
        html_body: str,
    ) -> None:
        api_key = self.api_key or os.environ.get("RESEND_API_KEY")
        if not api_key:
            raise ValueError(
                "Resend API key is not configured. Please set RESEND_API_KEY environment variable or settings."
            )
        resend.api_key = api_key

        params: resend.Emails.SendParams = {
            "from": sender,
            "to": recipients,
            "subject": subject,
            "html": html_body,
        }

        try:
            logger.info(
                f"[Resend-Email] Sending email to {recipients} with subject '{subject}'"
            )
            email = await resend.Emails.send_async(params)
            logger.success(
                f"[Resend-Email] Email sent successfully via Resend. Response: {email}"
            )
        except Exception as e:
            logger.error(f"[Resend-Email] Failed to send email to {recipients}: {e!s}")
            raise


class SendGridProvider(IEmailProvider):
    """
    SendGrid Email Provider placeholder for future implementation
    """

    async def send_email(
        self,
        *,
        sender: str,
        recipients: list[str],
        subject: str,
        html_body: str,
    ) -> None:
        logger.warning("[SendGrid-Email] SendGrid provider is not yet implemented.")
        raise NotImplementedError("SendGrid email provider is not implemented yet.")


class EmailProviderFactory:
    """
    Factory for producing email providers based on active configuration
    """

    @staticmethod
    def get_provider(provider_name: str) -> IEmailProvider:
        name = provider_name.lower().strip()
        if name == "smtp":
            return SMTPProvider()
        elif name == "resend":
            return ResendProvider()
        elif name == "sendgrid":
            return SendGridProvider()
        else:
            raise ValueError(f"Unsupported email provider: {provider_name}")
