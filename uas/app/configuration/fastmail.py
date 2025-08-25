from app.configuration.settings import settings
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from starlette.background import BackgroundTasks

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=settings.MAIL_TEMPLATE_FOLDER,
)

# Initialize FastMail with the configuration
fast_mail = FastMail(conf)


# Function to send email
async def send_email(
    recipients: list[str],
    subject: str,
    template_file: str,
    context: dict,
    background_tasks: BackgroundTasks,
):
    # Create the email message
    message = MessageSchema(
        subject=subject,
        recipients=recipients,
        template_body=context,
        subtype=MessageType.html,
    )
    # Add the email sending task to background tasks
    background_tasks.add_task(
        fast_mail.send_message, message, template_name=template_file
    )
