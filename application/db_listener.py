from contextlib import asynccontextmanager
import base64
from io import BytesIO
import json
import binascii

from fastapi import FastAPI
from asyncio import create_task, sleep
from httpx import AsyncClient
from asyncpg import connect
from sqlmodel import Session, select

from .config import Settings
from .database_connection import engine
from .db_models import Defect
from .defect_info_service import form_response_model_from_defect, determine_defect_criticality

settings = Settings()


async def send_error_notification(subject: str, message: str):
    """
    Send notification in Telegram and by Gmail in the case when a new defect has appeared but defect info
    has turned out to be corrupted
    """
    async with AsyncClient() as client:
        await client.post(url="http://127.0.0.1:8000/notification/with_telegram",
                          params={"message": f"{subject}\n\n{message}"})
        await client.post(url="http://127.0.0.1:8000/notification/with_gmail",
                          params={"subject": subject, "text": message})
        await client.post(url="http://127.0.0.1:8000/logs/create_record", params={"log_type": "error", "log_text":
            f"New undefined defect has appeared on the conveyor, but defect info has corrupted!"})


async def on_new_defect_notify_handler(connection, pid, channel, payload):
    try:
        json_payload = json.loads(payload)
    except (json.JSONDecodeError, KeyError) as e:
        await send_error_notification(
            subject="New defect on the conveyor! [Corrupted Info]".upper(),
            message=f"New defect has appeared, but it seems the defect has corrupted info. Exception info: {e}")

    with Session(engine) as session:
        new_defect = session.exec(select(Defect).where(Defect.id == json_payload["id"])).one()
        formatted_defect = form_response_model_from_defect(new_defect)
        criticality = determine_defect_criticality(new_defect)
    message_header = f"New {criticality}-level defect on the conveyor!".upper()
    defect_to_text = "\n".join([f"{key} = {str(value)}" for (key, value) in
                                formatted_defect.model_dump(exclude={"base64_photo"}).items()])

    # New defect may cause changing of the general conveyor status
    async with AsyncClient() as client:
        await client.post("http://127.0.0.1:8000/conveyor_info/create_record")

    defect_photo = None
    try:
        defect_photo = BytesIO(base64.b64decode(formatted_defect.base64_photo))
    except (binascii.Error, TypeError):
        await send_error_notification(subject="New defect on the conveyor! [Corrupted Photo]".upper(),
                                      message="New defect has appeared, but it seems like there is incorrect "
                                              "base64-encoded representation of the photo for the new defect!.\n"
                                              f"Defect info:\n\n{defect_to_text}")

    async with AsyncClient() as client:
        await client.post(url="http://127.0.0.1:8000/notification/with_telegram",
                          params={"message": message_header + "\n\n" + defect_to_text},
                          files={"attached_file": ("Defect.jpg", defect_photo, "image/jpeg")})
        await client.post(url="http://127.0.0.1:8000/notification/with_gmail",
                          params={"subject": message_header, "text": f"Defect info:\n\n{defect_to_text}"},
                          files={"attached_file": ("Defect.jpg", defect_photo, "image/jpeg")})
        # Action logging
        log_type = "warning" if criticality == "normal" else f"{criticality}_defect"
        await client.post(url="http://127.0.0.1:8000/logs/create_record", params={"log_type": log_type, "log_text":
            f"New {criticality} level defect with id={json_payload["id"]} has appeared on the conveyor!"})


async def listen_for_new_defects():
    db_connection = await connect(settings.DATABASE_URL)
    await db_connection.add_listener("new_defect", on_new_defect_notify_handler)
    while True:
        await sleep(1)


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_task(listen_for_new_defects())
    yield
