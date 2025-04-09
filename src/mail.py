from logging import getLogger
from pathlib import Path

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from fastapi_mail.errors import ConnectionErrors

from src.conf.config import Settings
from src.domain.models import User
from src.utils import create_email_token

logger = getLogger(__name__)


async def send_email(user: User, settings: Settings) -> None:
    conf = ConnectionConfig(
        MAIL_USERNAME=settings.MAIL_USERNAME,
        MAIL_PASSWORD=settings.MAIL_PASSWORD,
        MAIL_FROM=settings.MAIL_FROM,
        MAIL_PORT=settings.MAIL_PORT,
        MAIL_SERVER=settings.MAIL_SERVER,
        MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
        MAIL_STARTTLS=settings.MAIL_STARTTLS,
        MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
        USE_CREDENTIALS=settings.USE_CREDENTIALS,
        VALIDATE_CERTS=settings.VALIDATE_CERTS,
        TEMPLATE_FOLDER=Path(__file__).parent / "templates",
    )

    try:
        token = create_email_token(
            data={"user_id": user.id},
            settings=settings,
        )
        verify_url = (
            f"http://{settings.HOST}:{settings.PORT}/auth/confirm-email/{token}"
        )
        logger.info(f"verify_url is: {verify_url}")
        message = MessageSchema(
            subject="Confirm your email",
            recipients=[user.email],
            template_body={"verify_url": verify_url},
            subtype=MessageType.html,
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="verify_email.html")
    except ConnectionErrors:
        logger.exception("Error sending email")
