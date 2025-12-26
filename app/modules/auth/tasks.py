from fastapi_mail import ConnectionConfig, FastMail, MessageSchema
from loguru import logger

from app.core.config import settings
from app.core.taskiq import broker

mail_conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=True,
)


@broker.task(retry_on_error=True, max_tries=3)
async def send_welcome_email(email: str):
    message = MessageSchema(
        subject="Добро пожаловать в CodeVenture!",
        recipients=[email],
        body="Спасибо, что присоединились к нашему сообществу! :)",
        subtype="html",
    )

    fm = FastMail(mail_conf)
    await fm.send_message(message)
    logger.info(f"Отправлено приветственное письмо на почту: {email}")
