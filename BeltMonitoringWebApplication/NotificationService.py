from fastapi import FastAPI
from pydantic import BaseModel
from enum import Enum

application = FastAPI()


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
def send_notification(notification: Notification):
    if notification.method == NotificationMethod.telegram_notification:
        return {"status": "OK", "method": NotificationMethod.telegram_notification, "message": notification.message}
    elif notification.method == NotificationMethod.gmail_notification:
        return {"status": "OK", "method": NotificationMethod.gmail_notification, "message": notification.message}
