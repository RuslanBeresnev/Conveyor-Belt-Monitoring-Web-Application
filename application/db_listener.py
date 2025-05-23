from contextlib import asynccontextmanager
import base64
from io import BytesIO
import json
import binascii

import httpx
from fastapi import FastAPI
from asyncio import create_task, sleep
from httpx import AsyncClient, HTTPStatusError
from asyncpg import connect
from sqlmodel import Session, select

from .config import Settings
from .user_settings import load_user_settings
from .db_connection import engine
from application.models.db_models import Defect
from application.services.defect_info_service import form_response_model_from_defect, determine_defect_criticality

from application.services.maintenance_service import notify_clients

settings = Settings()


async def send_error_notification(subject: str, message: str):
    """
    Send notification in Telegram and by Gmail and to the client in the case when a new defect has appeared
    but defect info has turned out to be corrupted
    """
    async with AsyncClient(timeout=10) as client:
        # Action logging
        await client.post(url="http://127.0.0.1:8000/api/v1/logs/create_record", params={"log_type": "error", "log_text":
            f"New undefined defect has appeared on the conveyor, but defect info has corrupted!"})

        try:
            telegram_response = None
            gmail_response = None

            if not load_user_settings() or "Telegram" in load_user_settings()["new_defect_notification_scope"]:
                telegram_response = await client.post(url="http://127.0.0.1:8000/api/v1/notification/with_telegram",
                                                      params={"message": f"{subject}\n\n{message}"})
            if not load_user_settings() or "Gmail" in load_user_settings()["new_defect_notification_scope"]:
                gmail_response = await client.post(url="http://127.0.0.1:8000/api/v1/notification/with_gmail",
                                                   params={"subject": subject, "text": message})

            if telegram_response: telegram_response.raise_for_status()
            if gmail_response: gmail_response.raise_for_status()

            await notify_clients(json.dumps({"title": subject, "text": message}))
        except HTTPStatusError as e:
            try:
                details = json.loads(e.response.text).get("detail")
            except json.JSONDecodeError:
                if not e.response.text or e.response.text == "":
                    details = f"Some error with status-code = {e.response.status_code}"
                else:
                    details = e.response.text
            await notify_clients(
                json.dumps({"title": subject,
                            "text": "There were some errors when trying to send a notification via Telegram " \
                                    f"or Gmail.\n Error info: {details}.\n\nFailure notification info:\n{message}"}))
        except httpx.ReadTimeout as e:
            await notify_clients(
                json.dumps({"title": subject,
                            "text": "ReadTimeout error has occurred when trying to send a notification via Telegram " \
                                    f"or Gmail.\n\nFailure notification info:\n{message}"}))


async def on_new_defect_notify_handler(connection, pid, channel, payload):
    try:
        json_payload = json.loads(payload)
    except (json.JSONDecodeError, KeyError) as e:
        await send_error_notification(
            subject="New defect on the conveyor! [Corrupted Info]".upper(),
            message=f"New defect has appeared, but it seems the defect has corrupted info. Exception info: {e}")
        return

    with Session(engine) as session:
        new_defect = session.exec(select(Defect).where(Defect.id == json_payload["id"])).one()
        formatted_defect = form_response_model_from_defect(new_defect)
        criticality = determine_defect_criticality(new_defect)
    message_header = f"New {criticality}-level defect on the conveyor!".upper()
    defect_to_text = "\n".join([f"{key} = {str(value)}" for (key, value) in
                                formatted_defect.model_dump(exclude={"base64_photo"}).items()])

    defect_photo = None
    try:
        defect_photo = BytesIO(base64.b64decode(formatted_defect.base64_photo))
    except (binascii.Error, TypeError):
        await send_error_notification(subject=f"{message_header} [Corrupted Photo]".upper(),
                                      message="New defect has appeared, but it seems like there is incorrect "
                                              "base64-encoded representation of the photo for the new defect!.\n"
                                              f"Defect info:\n\n{defect_to_text}")
        return

    async with AsyncClient(timeout=10) as client:
        # Action logging
        log_type = "warning" if criticality == "normal" else f"{criticality}_defect"
        await client.post(url="http://127.0.0.1:8000/api/v1/logs/create_record", params={"log_type": log_type, "log_text":
            f"New {criticality}-level defect with id={json_payload["id"]} has appeared on the conveyor!"})

        # New defect may cause changing of the general conveyor status
        await client.post("http://127.0.0.1:8000/api/v1/conveyor_info/create_record")

        try:
            telegram_response = None
            gmail_response = None

            # Notification sending
            if not load_user_settings() or "Telegram" in load_user_settings()["new_defect_notification_scope"]:
                telegram_response = await client.post(url="http://127.0.0.1:8000/api/v1/notification/with_telegram",
                                                      params={"message": message_header + "\n\n" + defect_to_text},
                                                      files={"attached_file": ("Defect.jpg", defect_photo, "image/jpeg")})
            if not load_user_settings() or "Gmail" in load_user_settings()["new_defect_notification_scope"]:
                gmail_response = await client.post(url="http://127.0.0.1:8000/api/v1/notification/with_gmail",
                                                   params={"subject": message_header,
                                                           "text": f"Defect info:\n\n{defect_to_text}"},
                                                   files={"attached_file": ("Defect.jpg", defect_photo, "image/jpeg")})

            if telegram_response: telegram_response.raise_for_status()
            if gmail_response: gmail_response.raise_for_status()

            await notify_clients(json.dumps({"title": message_header, "text": defect_to_text}))
        except HTTPStatusError as e:
            try:
                details = json.loads(e.response.text).get("detail")
            except json.JSONDecodeError:
                if not e.response.text or e.response.text == "":
                    details = f"Some error with status-code = {e.response.status_code}"
                else:
                    details = e.response.text
            await notify_clients(
                json.dumps({"title": message_header,
                            "text": "There were some errors when trying to send a notification via Telegram " \
                                    f"or Gmail.\n Error info: {details}.\n\nNotification info:\n{defect_to_text}"}))
        except httpx.ReadTimeout as e:
            await notify_clients(
                json.dumps({"title": message_header,
                            "text": "ReadTimeout error has occurred when trying to send a notification via Telegram " \
                                    f"or Gmail.\n\nNotification info:\n{defect_to_text}"}))


async def listen_for_new_defects():
    db_connection = await connect(settings.DATABASE_URL)
    await db_connection.add_listener("new_defect", on_new_defect_notify_handler)
    while True:
        await sleep(1)


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_task(listen_for_new_defects())
    yield
