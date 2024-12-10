from fastapi import FastAPI
from pydantic import BaseModel
from telegram import Bot
import requests
from enum import Enum

application = FastAPI()
TELEGRAM_BOT_TOKEN = "<Bot token>"
telegram_bot = Bot(token=TELEGRAM_BOT_TOKEN)


def get_user_chat_id():
    '''
    Возвращает id чата с пользователем, который последним отправил сообщение боту
    '''
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
    response = requests.get(url)
    updates = response.json()
    if updates["ok"] and len(updates) > 0:
        return updates["result"][-1]["message"]["chat"]["id"]
    return -1


class NotificationMethod(Enum):
    telegram_notification = "telegram_notification"
    gmail_notification = "gmail_notification"


class Notification(BaseModel):
    method: NotificationMethod
    message: str


@application.get("/")
def get_application_info():
    return {"info": "Web-application for conveyor belt monitoring system"}


@application.post("/notification_service")
async def send_notification(notification: Notification):
    if notification.method == NotificationMethod.telegram_notification:
        # Обработать в try/catch
        await telegram_bot.send_message(chat_id=get_user_chat_id(), text=notification.message)
        return {"status": "OK", "method": NotificationMethod.telegram_notification, "message": notification.message}
    elif notification.method == NotificationMethod.gmail_notification:
        # Добавить способ для Gmail
        return {"status": "OK", "method": NotificationMethod.gmail_notification, "message": notification.message}
