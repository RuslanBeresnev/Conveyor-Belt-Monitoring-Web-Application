from fastapi import FastAPI
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
from googleapiclient.discovery import build
import Data

application = FastAPI()

telegram_bot = Bot(token=Data.TELEGRAM_BOT_TOKEN)


def get_user_chat_id_in_telegram():
    '''
    Возвращает id Telegram-чата с пользователем, который последним отправил сообщение боту
    (сообщение должно быть отправлено в течение суток до запуска сервера)
    '''
    url = f"https://api.telegram.org/bot{Data.TELEGRAM_BOT_TOKEN}/getUpdates"
    response = requests.get(url)
    updates = response.json()
    if updates["ok"] and len(updates["result"]) > 0:
        return updates["result"][-1]["message"]["chat"]["id"]
    return -1


def authenticate_and_get_credentials():
    """Аутентификация в Gmail с помощью OAuth 2.0 (срок годности токена истекает через час после
    первой аутентификации)"""
    credentials = None
    if exists("token.json"):
        credentials = Credentials.from_authorized_user_file(filename="token.json", scopes=Data.GOOGLE_SCOPES)
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file=Data.GOOGLE_CLIENT_SECRET_FILE,
                                                             scopes=Data.GOOGLE_SCOPES)
            credentials = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(credentials.to_json())
    return credentials


class TelegramNotification(BaseModel):
    message: str


class GmailNotification(BaseModel):
    to_email: str
    subject: str
    message: str


@application.get("/")
def get_application_info():
    return {"info": "Web-application for conveyor belt monitoring system"}


@application.post("/notification_service/with_telegram")
async def send_telegram_notification(notification: TelegramNotification):
    # Добавить правильный возврат кодов ошибок при ошибках (а не просто оставить 200)
    user_chat_id = get_user_chat_id_in_telegram()
    if user_chat_id == -1:
        return {"status": "ERROR", "method": "telegram_notification", "error_message": "Chat with user not found"}
    try:
        await telegram_bot.send_message(chat_id=user_chat_id, text=notification.message)
    except telegram.error.TelegramError:
        return {"status": "ERROR", "method": "telegram_notification", "error_message": "Telegram error"}
    return {"status": "OK", "method": "telegram_notification", "message": notification.message}


@application.post("/notification_service/with_gmail")
def send_gmail_notification(notification: GmailNotification):
    message = MIMEText(notification.message)
    message["to"] = notification.to_email
    message["subject"] = notification.subject
    formatted_message = {'raw': urlsafe_b64encode(message.as_bytes()).decode()}

    credentials = authenticate_and_get_credentials()
    gmail_service = build(serviceName="gmail", version="v1", credentials=credentials)
    # Добавить обработку ошибок
    sent_message = gmail_service.users().messages().send(userId="me", body=formatted_message).execute()
    return {"status": "OK", "method": "gmail_notification", "message": notification.message}
