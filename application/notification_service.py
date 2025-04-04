from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import mimetypes

from io import BytesIO
from os.path import exists
from base64 import urlsafe_b64encode
from enum import Enum
import requests
import httpx

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends

from telegram import Bot
import telegram.error

from google.auth.exceptions import RefreshError, DefaultCredentialsError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .config import Settings
from .api_models import (TelegramNotification, GmailNotification, ServiceInfoResponseModel,
                         TelegramNotificationResponseModel, GmailNotificationResponseModel)

router = APIRouter(prefix="/notification", tags=["Notification Service"])
settings = Settings()

telegram_bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)

GOOGLE_CLIENT_SECRET_FILE = "client_secret.json"
GOOGLE_SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


class NotificationSendingErrorMessage(Enum):
    INVALID_BOT_TOKEN = "Token for Telegram-bot is incorrect"
    CHAT_WITH_USER_IS_NOT_REGISTERED = ("User has not sent a message to the bot or it has been for more than a day ago,"
                                        " so the chat with the user is not registered and has not found")
    TELEGRAM_ERROR = "Some error in Telegram API"
    INVALID_GMAIL_CLIENT_SECRET_FILE = "File 'client_secret.json' is incorrect"
    GMAIL_CLIENT_SECRET_FILE_ABSENCE = "File 'client_secret.json' does not exist"


def write_telegram_user_name_and_chat_id_to_env_file(user_name, user_chat_id):
    settings.TELEGRAM_USER_NAME = user_name
    settings.TELEGRAM_USER_CHAT_ID = user_chat_id

    settings_dump = settings.model_dump()
    settings_to_text = "\n".join(
        [f"{param_name} = \"{param_value}\"" for param_name, param_value in settings_dump.items()])

    with open(".env", "w") as env:
        env.write(settings_to_text)


def get_user_chat_id_in_telegram():
    """
    Returns a tuple (<id>, <username>, <error_message>), where <id> is the id of the Telegram chat with the user
    (if the user has once sent a message to the bot), <username> is unique user nick seems like "@test_user",
    <error_message> gives information in the case of emergency situation.
    """
    if settings.TELEGRAM_USER_NAME != "" and settings.TELEGRAM_USER_CHAT_ID != "":
        return settings.TELEGRAM_USER_CHAT_ID, settings.TELEGRAM_USER_NAME, None

    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/getUpdates"
    response = requests.get(url, timeout=3)
    updates = response.json()
    if not updates["ok"]:
        return None, None, NotificationSendingErrorMessage.INVALID_BOT_TOKEN
    if len(updates["result"]) > 0:
        user_chat_id = updates["result"][-1]["message"]["chat"]["id"]
        user_name = '@' + updates["result"][-1]["message"]["chat"]["username"]
        write_telegram_user_name_and_chat_id_to_env_file(user_name, user_chat_id)
        return user_chat_id, user_name, None
    return None, None, NotificationSendingErrorMessage.CHAT_WITH_USER_IS_NOT_REGISTERED


def authenticate():
    """
    Gmail authentication using OAuth 2.0
    """
    try:
        flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file=GOOGLE_CLIENT_SECRET_FILE,
                                                         scopes=GOOGLE_SCOPES)
        credentials = flow.run_local_server(port=0, access_type='offline', prompt='consent')
    except ValueError:
        return None, NotificationSendingErrorMessage.INVALID_GMAIL_CLIENT_SECRET_FILE
    except FileNotFoundError:
        return None, NotificationSendingErrorMessage.GMAIL_CLIENT_SECRET_FILE_ABSENCE
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


@router.get(path="/", response_model=ServiceInfoResponseModel)
def get_service_info():
    return ServiceInfoResponseModel(
        info="Notification service with Telegram or Gmail notification sending option"
    )


@router.post("/with_telegram", response_model=TelegramNotificationResponseModel)
async def send_telegram_notification(notification: TelegramNotification = Depends(),
                                     attached_file: UploadFile | str = File(None)):
    async with httpx.AsyncClient() as client:
        telegram_notification_error_codes = {NotificationSendingErrorMessage.INVALID_BOT_TOKEN: 500,
                                             NotificationSendingErrorMessage.CHAT_WITH_USER_IS_NOT_REGISTERED: 404}
        user_chat_id, username, error_message = get_user_chat_id_in_telegram()

        if user_chat_id is None:
            # Action logging
            await client.post(url="http://127.0.0.1:8000/logs/create_record", params={"log_type": "error", "log_text":
                f"Error has occurred while sending notification via Telegram. Error info: \"{error_message.value}\""})
            raise HTTPException(status_code=telegram_notification_error_codes[error_message],
                                detail=error_message.value)

        try:
            if attached_file == "":
                await telegram_bot.send_message(chat_id=user_chat_id, text=notification.message)
            else:
                attached_file_bytes = BytesIO(await attached_file.read())
                attached_file_bytes.name = attached_file.filename
                await telegram_bot.send_document(chat_id=user_chat_id, document=attached_file_bytes,
                                                 caption=notification.message)
        except telegram.error.TelegramError as exception:
            # Action logging
            await client.post(url="http://127.0.0.1:8000/logs/create_record", params={"log_type": "error", "log_text":
                f"Error has occurred while sending notification via Telegram. Error info: "
                f"\"{NotificationSendingErrorMessage.TELEGRAM_ERROR.value}\""})
            raise HTTPException(status_code=500,
                                detail=NotificationSendingErrorMessage.TELEGRAM_ERROR.value) from exception

        # Action logging
        await client.post(url="http://127.0.0.1:8000/logs/create_record", params={"log_type": "action_info", "log_text":
            f"Notification with the text \"{notification.message}\" was successfully sent via Telegram to the user "
            f"{username}"})

        return TelegramNotificationResponseModel(
            notification_method="telegram_notification",
            to_user=username,
            sent_message=notification.message,
            attached_file=attached_file.filename if attached_file != "" else None
        )


@router.post("/with_gmail", response_model=GmailNotificationResponseModel)
async def send_gmail_notification(notification: GmailNotification = Depends(),
                                  attached_file: UploadFile | str = File(None)):
    async with httpx.AsyncClient() as client:
        if attached_file == "":
            message = MIMEText(notification.text)
        else:
            message = MIMEMultipart()

        message["to"] = settings.GMAIL_ADDRESS
        message["subject"] = notification.subject

        if attached_file != "":
            text = MIMEText(notification.text)
            message.attach(text)

            mime_type, _ = mimetypes.guess_type(attached_file.filename)
            if mime_type is None:
                mime_type = "application/octet-stream"
            main_type, sub_type = mime_type.split("/")

            attachment = MIMEBase(main_type, sub_type)
            attachment.set_payload(await attached_file.read())
            encoders.encode_base64(attachment)
            attachment.add_header("Content-Disposition",
                                  f'attachment; filename="{attached_file.filename}"')
            message.attach(attachment)

        formatted_message = {'raw': urlsafe_b64encode(message.as_bytes()).decode()}

        credentials, error_message = get_credentials()
        if credentials is None:
            # Action logging
            await client.post(url="http://127.0.0.1:8000/logs/create_record", params={"log_type": "error", "log_text":
                f"Error has occurred while sending notification via Gmail. Error info: \"{error_message.value}\""})
            raise HTTPException(status_code=403, detail=error_message.value)

        try:
            gmail_service = build(serviceName="gmail", version="v1", credentials=credentials)
        except DefaultCredentialsError as exception:
            # Action logging
            await client.post(url="http://127.0.0.1:8000/logs/create_record", params={"log_type": "error", "log_text":
                f"Error has occurred while sending notification via Gmail. Error info: \"{error_message.value}\""})
            raise HTTPException(status_code=403, detail="Credentials not found or incorrect") from exception

        try:
            # pylint: disable=E1101
            gmail_service.users().messages().send(userId="me", body=formatted_message).execute()
        except HttpError as e:
            # Action logging
            await client.post(url="http://127.0.0.1:8000/logs/create_record", params={"log_type": "error", "log_text":
                f"Error has occurred while sending notification via Gmail. Error info: \"{e.error_details}\""})
            raise HTTPException(status_code=e.status_code, detail=e.error_details) from e
        except TypeError as e:
            # Action logging
            await client.post(url="http://127.0.0.1:8000/logs/create_record", params={"log_type": "error", "log_text":
                "Error has occurred while sending notification via Gmail: invalid message format"})
            raise HTTPException(status_code=500, detail="Invalid message format") from e

        # Action logging
        await client.post(url="http://127.0.0.1:8000/logs/create_record", params={"log_type": "action_info", "log_text":
            f"Notification with the subject \"{message["subject"]}\" was successfully sent via Gmail to the address "
            f"{message["to"]}"})

        return GmailNotificationResponseModel(
            notification_method="gmail_notification",
            to=message["to"],
            subject=message["subject"],
            sent_text=notification.text,
            attached_file=attached_file.filename if attached_file != "" else None
        )
