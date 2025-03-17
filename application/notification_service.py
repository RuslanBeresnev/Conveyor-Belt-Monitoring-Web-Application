from email.mime.text import MIMEText
from os.path import exists
from base64 import urlsafe_b64encode
from enum import Enum
import httpx

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import requests

from telegram import Bot
import telegram.error

from google.auth.exceptions import RefreshError, DefaultCredentialsError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .config import Settings
from .response_models import ServiceInfoResponseModel, TelegramNotificationResponseModel, GmailNotificationResponseModel

GOOGLE_CLIENT_SECRET_FILE = "client_secret.json"
GOOGLE_SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

router = APIRouter(prefix="/notification", tags=["Notification Service"])
settings = Settings()
telegram_bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)


class NotificationSendingErrorMessage(Enum):
    INVALID_BOT_TOKEN = "Token for Telegram-bot is incorrect"
    MESSAGE_FROM_USER_WAS_LONG_AGO = ("User has not sent a message to the bot for more than a day, "
                                      "so the chat with the user is not registered and has not found")
    TELEGRAM_ERROR = "Some error in Telegram API"
    INVALID_GMAIL_TOKEN_FILE = "File 'token.json' is incorrect"
    CREDENTIALS_REFRESHING_ERROR = "Credentials could not be refreshed"
    INVALID_GMAIL_CLIENT_SECRET_FILE = "File 'client_secret.json' is incorrect"
    GMAIL_CLIENT_SECRET_FILE_ABSENCE = "File 'client_secret.json' does not exist"


def get_user_chat_id_in_telegram():
    """
    Returns a pair (<id>, <username>, <error_message>), where <id> is the id of the Telegram chat with the user who last
    sent a message to the bot (the message must be sent during the day before server launch), <username> is unique user
    nick seems like "@test_user" (without '@'), <error_message> gives information in the case of emergency situation.
    """
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/getUpdates"
    response = requests.get(url, timeout=3)
    updates = response.json()
    if not updates["ok"]:
        return None, None, NotificationSendingErrorMessage.INVALID_BOT_TOKEN
    if len(updates["result"]) > 0:
        return (updates["result"][-1]["message"]["chat"]["id"], updates["result"][-1]["message"]["chat"]["username"],
                None)
    return None, None, NotificationSendingErrorMessage.MESSAGE_FROM_USER_WAS_LONG_AGO


def authenticate_and_get_credentials():
    """
    Gmail authentication using OAuth 2.0 (token expires in one hour after first authentication)
    """
    credentials = None
    if exists("token.json"):
        try:
            credentials = Credentials.from_authorized_user_file(filename="token.json", scopes=GOOGLE_SCOPES)
        except ValueError:
            return None, NotificationSendingErrorMessage.INVALID_GMAIL_TOKEN_FILE
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            try:
                credentials.refresh(Request())
            except RefreshError:
                return None, NotificationSendingErrorMessage.CREDENTIALS_REFRESHING_ERROR
        else:
            try:
                flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file=GOOGLE_CLIENT_SECRET_FILE,
                                                                 scopes=GOOGLE_SCOPES)
                credentials = flow.run_local_server(port=0)
            except ValueError:
                return None, NotificationSendingErrorMessage.INVALID_GMAIL_CLIENT_SECRET_FILE
            except FileNotFoundError:
                return None, NotificationSendingErrorMessage.GMAIL_CLIENT_SECRET_FILE_ABSENCE
        with open("token.json", "w", encoding="utf-8") as token:
            token.write(credentials.to_json())
    return credentials, None


class TelegramNotification(BaseModel):
    message: str


class GmailNotification(BaseModel):
    to_email: str
    subject: str
    message: str


@router.get(path="/", response_model=ServiceInfoResponseModel)
def get_service_info():
    return ServiceInfoResponseModel(
        info="Notification service with Telegram or Gmail notification sending option"
    )


@router.post("/with_telegram", response_model=TelegramNotificationResponseModel)
async def send_telegram_notification(notification: TelegramNotification):
    async with httpx.AsyncClient() as client:
        telegram_notification_error_codes = {NotificationSendingErrorMessage.INVALID_BOT_TOKEN: 500,
                                             NotificationSendingErrorMessage.MESSAGE_FROM_USER_WAS_LONG_AGO: 404}
        user_chat_id, username, error_message = get_user_chat_id_in_telegram()

        if user_chat_id is None:
            # Action logging
            await client.post(url="http://127.0.0.1:8000/logs/create_record", params={"log_type": "error", "log_text":
                f"Error has occurred while sending notification via Telegram. Error info: \"{error_message.value}\""})
            raise HTTPException(status_code=telegram_notification_error_codes[error_message],
                                detail=error_message.value)

        try:
            await telegram_bot.send_message(chat_id=user_chat_id, text=notification.message)
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
            f"@{username}"})

        return TelegramNotificationResponseModel(
            notification_method="telegram_notification",
            to_user='@' + username,
            sent_message=notification.message
        )


@router.post("/with_gmail", response_model=GmailNotificationResponseModel)
def send_gmail_notification(notification: GmailNotification):
    message = MIMEText(notification.message)
    message["to"] = notification.to_email
    message["subject"] = notification.subject
    formatted_message = {'raw': urlsafe_b64encode(message.as_bytes()).decode()}

    credentials, error_message = authenticate_and_get_credentials()
    if credentials is None:
        # Action logging
        requests.post(url="http://127.0.0.1:8000/logs/create_record", params={"log_type": "error", "log_text":
            f"Error has occurred while sending notification via Gmail. Error info: \"{error_message.value}\""})
        raise HTTPException(status_code=403, detail=error_message.value)

    try:
        gmail_service = build(serviceName="gmail", version="v1", credentials=credentials)
    except DefaultCredentialsError as exception:
        # Action logging
        requests.post(url="http://127.0.0.1:8000/logs/create_record", params={"log_type": "error", "log_text":
            f"Error has occurred while sending notification via Gmail. Error info: \"{error_message.value}\""})
        raise HTTPException(status_code=403, detail="Credentials not found or incorrect") from exception

    try:
        # pylint: disable=E1101
        gmail_service.users().messages().send(userId="me", body=formatted_message).execute()
    except HttpError as e:
        # Action logging
        requests.post(url="http://127.0.0.1:8000/logs/create_record", params={"log_type": "error", "log_text":
            f"Error has occurred while sending notification via Gmail. Error info: \"{e.error_details}\""})
        raise HTTPException(status_code=e.status_code, detail=e.error_details) from e
    except TypeError as e:
        # Action logging
        requests.post(url="http://127.0.0.1:8000/logs/create_record", params={"log_type": "error", "log_text":
            "Error has occurred while sending notification via Gmail: invalid message format"})
        raise HTTPException(status_code=500, detail="Invalid message format") from e

    # Action logging
    requests.post(url="http://127.0.0.1:8000/logs/create_record", params={"log_type": "action_info", "log_text":
        f"Notification with the subject \"{message["subject"]}\" was successfully sent via Gmail to the address "
        f"{message["to"]}"})

    return GmailNotificationResponseModel(
        notification_method="gmail_notification",
        to=message["to"],
        subject=message["subject"],
        sent_message=notification.message
    )
