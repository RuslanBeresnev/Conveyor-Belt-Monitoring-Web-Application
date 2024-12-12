import telegram.error
from fastapi import FastAPI
from pydantic import BaseModel
from telegram import Bot
import requests
from base64 import urlsafe_b64encode
from os.path import exists
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import smtplib
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


def authenticate_user_in_gmail():
    """Аутентификация в Gmail с помощью OAuth 2.0"""
    credentials = None
    if exists("token.json"):
        credentials = Credentials.from_authorized_user_file("token.json", Data.GOOGLE_SCOPES)
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(Data.GOOGLE_CLIENT_SECRET_FILE, Data.GOOGLE_SCOPES)
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
    mail = MIMEText(notification.message)
    mail["from"] = Data.FROM_EMAIL
    mail["to"] = notification.to_email
    mail["subject"] = notification.subject

    formatted_mail = urlsafe_b64encode(mail.as_bytes()).decode()
    smtp_server = smtplib.SMTP("smtp.gmail.com", 587)
    smtp_server.starttls()
    smtp_server.ehlo()

    credentials = authenticate_user_in_gmail()
    smtp_server.docmd(
        "AUTH XOAUTH2",
        f"user={Data.FROM_EMAIL}\x01auth=Bearer {credentials.token}\x01\x01"
    )
    # Добавить обработку ошибок
    smtp_server.sendmail(Data.FROM_EMAIL, mail["to"], formatted_mail)

    smtp_server.quit()
    return {"status": "OK", "method": "gmail_notification", "message": notification.message}
