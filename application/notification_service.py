from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from telegram import Bot
import telegram.error
from email.mime.text import MIMEText
import requests
from os.path import exists
from base64 import urlsafe_b64encode
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError, DefaultCredentialsError
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from enum import Enum
from .config import Settings
from .response_models import ServiceInfoResponseModel, TelegramNotificationResponseModel, GmailNotificationResponseModel

GOOGLE_CLIENT_SECRET_FILE = "client_secret.json"
GOOGLE_SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

router = APIRouter(prefix="/notification", tags=["Notification Service"])
settings = Settings()
telegram_bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)


class NotificationSendingErrorMessage(Enum):
    invalid_bot_token = "Token for Telegram-bot is incorrect"
    message_from_user_was_long_ago = ("User has not sent a message to the bot for more than a day, "
                                      "so the chat with the user is not registered and has not found")
    telegram_error = "Some error in Telegram API"
    invalid_gmail_token_file = "File 'token.json' is incorrect"
    credentials_refreshing_error = "Credentials could not be refreshed"
    invalid_gmail_client_secret_file = "File 'client_secret.json' is incorrect"
    gmail_client_secret_file_absence = "File 'client_secret.json' does not exist"


def get_user_chat_id_in_telegram():
    """
    Возвращает пару (id, error_message), где id - id Telegram-чата с пользователем, который последним отправил сообщение
    боту (сообщение должно быть отправлено в течение суток до запуска серверe), а error_message - сообщение при
    возникновении ошибки.
    """
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/getUpdates"
    response = requests.get(url)
    updates = response.json()
    if not updates["ok"]:
        return None, NotificationSendingErrorMessage.invalid_bot_token
    if len(updates["result"]) > 0:
        return updates["result"][-1]["message"]["chat"]["id"], None
    return None, NotificationSendingErrorMessage.message_from_user_was_long_ago


def authenticate_and_get_credentials():
    """Аутентификация в Gmail с помощью OAuth 2.0 (срок годности токена истекает через час после
    первой аутентификации)"""
    credentials = None
    if exists("token.json"):
        try:
            credentials = Credentials.from_authorized_user_file(filename="token.json", scopes=GOOGLE_SCOPES)
        except ValueError:
            return None, NotificationSendingErrorMessage.invalid_gmail_token_file
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            try:
                credentials.refresh(Request())
            except RefreshError:
                return None, NotificationSendingErrorMessage.credentials_refreshing_error
        else:
            try:
                flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file=GOOGLE_CLIENT_SECRET_FILE,
                                                                 scopes=GOOGLE_SCOPES)
                credentials = flow.run_local_server(port=0)
            except ValueError:
                return None, NotificationSendingErrorMessage.invalid_gmail_client_secret_file
            except FileNotFoundError:
                return None, NotificationSendingErrorMessage.gmail_client_secret_file_absence
        with open("token.json", "w") as token:
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
    telegram_notification_error_codes = {NotificationSendingErrorMessage.invalid_bot_token: 500,
                                         NotificationSendingErrorMessage.message_from_user_was_long_ago: 404}
    user_chat_id, error_message = get_user_chat_id_in_telegram()
    if user_chat_id is None:
        raise HTTPException(status_code=telegram_notification_error_codes[error_message],
                            detail=error_message.value)
    try:
        await telegram_bot.send_message(chat_id=user_chat_id, text=notification.message)
    except telegram.error.TelegramError:
        raise HTTPException(status_code=500, detail=NotificationSendingErrorMessage.telegram_error.value)

    return TelegramNotificationResponseModel(
        notification_method="telegram_notification",
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
        raise HTTPException(status_code=403, detail=error_message.value)
    try:
        gmail_service = build(serviceName="gmail", version="v1", credentials=credentials)
    except DefaultCredentialsError:
        raise HTTPException(status_code=403, detail="Credentials not found or incorrect")
    try:
        sent_message = gmail_service.users().messages().send(userId="me", body=formatted_message).execute()
        print(gmail_service.users())
    except HttpError as e:
        raise HTTPException(status_code=e.status_code, detail=e.error_details)
    except TypeError:
        raise HTTPException(status_code=500, detail="Invalid message format")

    return GmailNotificationResponseModel(
        notification_method="gmail_notification",
        to=message["to"],
        subject=message["subject"],
        sent_message=notification.message
    )
