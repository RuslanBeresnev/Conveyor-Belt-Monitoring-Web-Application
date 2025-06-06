from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import mimetypes

from io import BytesIO
from os.path import exists
from base64 import urlsafe_b64encode
from enum import Enum
from typing import IO
import requests

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File

from telegram import Bot
import telegram.error

from google.auth.exceptions import RefreshError, DefaultCredentialsError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from application.config import settings
from application.models.api_models import (TelegramNotification, GmailNotification, ServiceInfoResponseModel,
                                           TelegramNotificationResponseModel, GmailNotificationResponseModel)
from application.services.authentication_service import get_current_admin_user
from application.services.logging_service import create_log_record

router = APIRouter(prefix="/notification", tags=["Notification Service"],
                   dependencies=[Depends(get_current_admin_user)])

telegram_bot = Bot(token=settings.telegram_bot_token)

GOOGLE_CLIENT_SECRET_FILE = "client_secret.json"
GOOGLE_SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


class NotificationSendingErrorType(Enum):
    INVALID_BOT_TOKEN = "Token for Telegram-bot is incorrect"
    CHAT_WITH_USER_IS_NOT_REGISTERED = ("User has not sent a message to the bot or it has been for more than a day ago,"
                                        " so the chat with the user is not registered and has not found")
    TELEGRAM_ERROR = "Some error in Telegram API"
    INVALID_GMAIL_CLIENT_SECRET_FILE = "File 'client_secret.json' is incorrect"
    GMAIL_CLIENT_SECRET_FILE_ABSENCE = "File 'client_secret.json' does not exist"
    HTTP_ERROR = "Some http-error while sending notification by Gmail"
    INCORRECT_CREDENTIALS = "Credentials not found or incorrect"
    INVALID_MESSAGE_FORMAT = "Invalid message format"


notification_error_codes = {
    NotificationSendingErrorType.INVALID_BOT_TOKEN: 500,
    NotificationSendingErrorType.CHAT_WITH_USER_IS_NOT_REGISTERED: 404,
    NotificationSendingErrorType.TELEGRAM_ERROR: 500,
    NotificationSendingErrorType.INVALID_GMAIL_CLIENT_SECRET_FILE: 403,
    NotificationSendingErrorType.GMAIL_CLIENT_SECRET_FILE_ABSENCE: 403,
    NotificationSendingErrorType.HTTP_ERROR: 403,
    NotificationSendingErrorType.INCORRECT_CREDENTIALS: 403,
    NotificationSendingErrorType.INVALID_MESSAGE_FORMAT: 500
}


def _form_io_file_from_file_on_server(filename: str | None = None):
    io_file = None
    if filename:
        filedata = None
        with open(filename, "rb") as file:
            filedata = file.read()
        io_file = BytesIO(filedata)
        io_file.name = filename
    return io_file


async def _form_io_file_from_attached_file(attached_file: UploadFile | None = File(None)):
    io_file = None
    if attached_file:
        io_file = BytesIO(await attached_file.read())
        io_file.name = attached_file.filename
    return io_file


def write_telegram_user_name_and_chat_id_to_env_file(user_name, user_chat_id):
    settings.telegram_user_name = user_name
    settings.telegram_user_chat_id = user_chat_id

    settings_dump = settings.model_dump()
    settings_to_text = "\n".join(
        [f"{param_name} = \"{param_value}\"" for param_name, param_value in settings_dump.items()])

    with open(".env", "w", encoding="utf-8") as env:
        env.write(settings_to_text)


def get_user_chat_id_in_telegram():
    """
    Returns a tuple (<id>, <username>, <error_message>), where <id> is the id of the Telegram chat with the user
    (if the user has once sent a message to the bot), <username> is unique user nick seems like "@test_user",
    <error_message> gives information in the case of emergency situation.
    """
    if settings.telegram_user_name != "" and settings.telegram_user_chat_id != "":
        return settings.telegram_user_chat_id, settings.telegram_user_name, None

    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/getUpdates"
    response = requests.get(url, timeout=3)
    updates = response.json()
    if not updates["ok"]:
        return None, None, NotificationSendingErrorType.INVALID_BOT_TOKEN
    if len(updates["result"]) > 0:
        user_chat_id = updates["result"][-1]["message"]["chat"]["id"]
        user_name = '@' + updates["result"][-1]["message"]["chat"]["username"]
        write_telegram_user_name_and_chat_id_to_env_file(user_name, user_chat_id)
        return user_chat_id, user_name, None
    return None, None, NotificationSendingErrorType.CHAT_WITH_USER_IS_NOT_REGISTERED


async def _send_data_by_telegram(message: str, attached_file: IO | None = None):
    user_chat_id, username, error_type = get_user_chat_id_in_telegram()

    if user_chat_id is None:
        # Action logging
        create_log_record("error", "Error has occurred while sending notification via Telegram. "
                                   f"Error info: \"{error_type.value}\"")
        return username, error_type

    error_type = None
    try:
        if attached_file is None:
            await telegram_bot.send_message(chat_id=user_chat_id, text=message)
        else:
            await telegram_bot.send_document(chat_id=user_chat_id, document=attached_file, caption=message)
    except telegram.error.InvalidToken:
        error_type = NotificationSendingErrorType.INVALID_BOT_TOKEN
        # Action logging
        create_log_record("error", "Error has occurred while sending notification via Telegram. "
                                   f"Error info: \"{error_type.value}\"")
        return username, error_type
    except telegram.error.TelegramError:
        error_type = NotificationSendingErrorType.TELEGRAM_ERROR
        # Action logging
        create_log_record("error", "Error has occurred while sending notification via Telegram. "
                                   f"Error info: \"{error_type.value}\"")
        return username, error_type

    # Action logging
    create_log_record("message", f"Notification \"{message}\" sent to {username} via Telegram")
    return username, error_type


async def send_telegram_notification_from_server(message: str, io_file: IO | None = None,
                                                 filename: str | None = None):
    if io_file is None:
        io_file = _form_io_file_from_file_on_server(filename)

    _, error_type = await _send_data_by_telegram(message=message, attached_file=io_file)
    if error_type:
        return notification_error_codes[error_type], error_type.value
    return None, None


def authenticate():
    """
    Gmail authentication using OAuth 2.0
    """
    try:
        flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file=GOOGLE_CLIENT_SECRET_FILE,
                                                         scopes=GOOGLE_SCOPES)
        credentials = flow.run_local_server(port=0, access_type='offline', prompt='consent')
    except ValueError:
        return None, NotificationSendingErrorType.INVALID_GMAIL_CLIENT_SECRET_FILE
    except FileNotFoundError:
        return None, NotificationSendingErrorType.GMAIL_CLIENT_SECRET_FILE_ABSENCE
    return credentials, None


def get_credentials():
    """
    Retrieve credentials from "token.json" (a token expires in one hour) or create new token with credentials
    """
    credentials = None
    error_message = None

    if exists("token.json"):
        try:
            credentials = Credentials.from_authorized_user_file(filename="token.json", scopes=GOOGLE_SCOPES)
        except ValueError:
            # The corrupted token has to be regenerated
            credentials, error_message = authenticate()
        if credentials.expired:
            if credentials.refresh_token:
                try:
                    credentials.refresh(Request())
                except RefreshError:
                    # RefreshError means that the refresh_token has expired and the usual token has to be regenerated
                    credentials, error_message = authenticate()
            else:
                credentials, error_message = authenticate()
    else:
        credentials, error_message = authenticate()

    if credentials:
        with open("token.json", "w", encoding="utf-8") as token:
            token.write(credentials.to_json())

    return credentials, error_message


def _send_data_by_gmail(subject: str, text: str, attached_file: IO | None = None):
    if attached_file is None:
        message = MIMEText(text)
    else:
        message = MIMEMultipart()

    message["to"] = settings.gmail_address
    message["subject"] = subject

    if attached_file:
        text = MIMEText(text)
        message.attach(text)

        mime_type, _ = mimetypes.guess_type(attached_file.name)
        if mime_type is None:
            mime_type = "application/octet-stream"
        main_type, sub_type = mime_type.split("/")

        attachment = MIMEBase(main_type, sub_type)
        attachment.set_payload(attached_file.read())
        encoders.encode_base64(attachment)
        attachment.add_header("Content-Disposition",
                              f'attachment; filename="{attached_file.name}"')
        message.attach(attachment)

    formatted_message = {'raw': urlsafe_b64encode(message.as_bytes()).decode()}

    credentials, error_type = get_credentials()
    if credentials is None:
        # Action logging
        create_log_record("error", "Error has occurred while sending notification via Gmail. "
                                   f"Error info: \"{error_type.value}\"")
        return error_type

    try:
        gmail_service = build(serviceName="gmail", version="v1", credentials=credentials)
    except DefaultCredentialsError:
        error_type = NotificationSendingErrorType.INCORRECT_CREDENTIALS
        # Action logging
        create_log_record("error", "Error has occurred while sending notification via Gmail. "
                                   f"Error info: {error_type.value}")
        return error_type

    try:
        # pylint: disable=E1101
        gmail_service.users().messages().send(userId="me", body=formatted_message).execute()
    except HttpError:
        error_type = NotificationSendingErrorType.HTTP_ERROR
        # Action logging
        create_log_record("error", "Error has occurred while sending notification via Gmail. "
                                   f"Error info: {error_type.value}")
        return error_type

    except TypeError:
        error_type = NotificationSendingErrorType.INVALID_MESSAGE_FORMAT
        # Action logging
        create_log_record("error", "Error has occurred while sending notification via Gmail. "
                                   f"Error info: {error_type.value}")
        return error_type

    # Action logging
    create_log_record("message", f"Notification with the subject \"{message["subject"]}\" sent to "
                                 f"{message["to"]} via Gmail")
    return None


def send_gmail_notification_from_server(subject: str, text: str, io_file: IO | None = None,
                                              filename: str | None = None):
    if io_file is None:
        io_file = _form_io_file_from_file_on_server(filename)

    error_type = _send_data_by_gmail(subject=subject, text=text, attached_file=io_file)
    if error_type:
        return notification_error_codes[error_type], error_type.value
    return None, None


@router.get(path="/", response_model=ServiceInfoResponseModel)
def get_service_info():
    return ServiceInfoResponseModel(
        info="Notification service with Telegram or Gmail notification sending option"
    )


@router.post("/with_telegram", response_model=TelegramNotificationResponseModel)
async def send_telegram_notification(notification: TelegramNotification = Depends(),
                                     attached_file: UploadFile | None = File(None)):
    io_file = await _form_io_file_from_attached_file(attached_file)

    username, error_type = await _send_data_by_telegram(message=notification.message, attached_file=io_file)
    if error_type:
        raise HTTPException(status_code=notification_error_codes[error_type], detail=error_type.value)

    return TelegramNotificationResponseModel(
        notification_method="telegram_notification",
        to_user=username,
        sent_message=notification.message,
        attached_file=attached_file.filename if attached_file else None
    )


@router.post("/with_gmail", response_model=GmailNotificationResponseModel)
async def send_gmail_notification(notification: GmailNotification = Depends(),
                                  attached_file: UploadFile | None = File(None)):
    io_file = await _form_io_file_from_attached_file(attached_file)

    error_type = _send_data_by_gmail(subject=notification.subject, text=notification.text, attached_file=io_file)
    if error_type:
        raise HTTPException(status_code=notification_error_codes[error_type], detail=error_type.value)

    return GmailNotificationResponseModel(
        notification_method="gmail_notification",
        to=settings.gmail_address,
        subject=notification.subject,
        sent_text=notification.text,
        attached_file=attached_file.filename if attached_file else None
    )
