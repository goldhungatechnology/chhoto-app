import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from pathlib import Path

from aiosmtplib import SMTP
import resend

from src.core.config.settings import config
from src.shared.infrastructure.logger import logger


@dataclass(frozen=True)
class InlineImage:
    """
    Represents an image to be embedded inline in an email using CID (Content-ID).

    Attributes:
        cid: The Content-ID header value (without angle brackets). The HTML
             template references this via ``<img src="cid:<cid>">``.
        file_path: Absolute path to the image file on disk.
        mime_type: MIME type of the image, e.g. ``image/png``.
    """

    cid: str
    file_path: Path
    mime_type: str = "image/png"


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
        inline_images: list["InlineImage"] | None = None,
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
        inline_images: list["InlineImage"] | None = None,
    ) -> None:
        if inline_images:
            msg = MIMEMultipart("related")
            msg["To"] = ", ".join(recipients)
            msg["Subject"] = subject
            msg["From"] = sender

            # multipart/alternative inside multipart/related
            alt_part = MIMEMultipart("alternative")
            alt_part.attach(
                MIMEText(
                    "Please view this email in an HTML-compatible email viewer.",
                    "plain",
                )
            )
            alt_part.attach(MIMEText(html_body, "html"))
            msg.attach(alt_part)

            for img in inline_images:
                img_data = img.file_path.read_bytes()
                mime_img = MIMEImage(img_data, _subtype=img.mime_type.split("/", 1)[1])
                mime_img.add_header("Content-ID", f"<{img.cid}>")
                mime_img.add_header("Content-Disposition", "inline", filename=img.cid)
                msg.attach(mime_img)
        else:
            msg = MIMEMultipart("alternative")
            msg["To"] = ", ".join(recipients)
            msg["Subject"] = subject
            msg["From"] = sender

            msg.attach(
                MIMEText(
                    "Please view this email in an HTML-compatible email viewer.",
                    "plain",
                )
            )
            msg.attach(MIMEText(html_body, "html"))

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
        inline_images: list["InlineImage"] | None = None,
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

        if inline_images:
            import base64

            params["attachments"] = [
                {
                    "filename": img.file_path.name,
                    "content": base64.b64encode(img.file_path.read_bytes()).decode(),
                    "content_type": img.mime_type,
                    "content_id": img.cid,
                }
                for img in inline_images
            ]

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
        inline_images: list["InlineImage"] | None = None,
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
