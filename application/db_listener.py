import base64
from io import BytesIO
import json
import binascii
from asyncio import sleep

from asyncpg import connect
from sqlmodel import Session, select

from application.models.db_models import Defect
from application.services.defect_info_service import form_response_model_from_defect, determine_defect_criticality
from application.services.conveyor_info_service import create_record_of_current_general_conveyor_status
from application.services.notification_service import (send_telegram_notification_from_server,
                                                       send_gmail_notification_from_server)
from application.services.maintenance_service import notify_clients
from application.services.logging_service import create_log_record

from .config import settings
from .user_settings import load_user_settings
from .db_connection import engine


async def send_error_notification(subject: str, message: str):
    """
    Send notification in Telegram and by Gmail and to the client in the case when a new defect has appeared
    but defect info has turned out to be corrupted
    """
    # Action logging
    create_log_record("error", "New undefined defect has appeared on the conveyor, "
                               "but defect info has corrupted!")

    telegram_sending_details = None
    gmail_sending_details = None

    if not load_user_settings() or "Telegram" in load_user_settings()["new_defect_notification_scope"]:
        _, telegram_sending_details = await send_telegram_notification_from_server(f"{subject}\n\n{message}")
    if not load_user_settings() or "Gmail" in load_user_settings()["new_defect_notification_scope"]:
        _, gmail_sending_details = send_gmail_notification_from_server(subject, message)

    if telegram_sending_details is None and gmail_sending_details is None:
        await notify_clients(json.dumps({"title": subject, "text": message}))
    else:
        await notify_clients(
            json.dumps({"title": subject,
                        "text": "There were some errors when trying to send a notification via Telegram or Gmail. \n"
                                f"Telegram error info: {telegram_sending_details}; \n"
                                f"Gmail error info: {gmail_sending_details}. \n\n"
                                f"Failure notification info: \n{message}"}))


async def on_new_defect_notify_handler(_connection, _pid, _channel, payload):
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

    try:
        defect_photo = BytesIO(base64.b64decode(formatted_defect.base64_photo))
        defect_photo.name = "Defect.jpg"
    except (binascii.Error, TypeError):
        await send_error_notification(subject=f"{message_header} [Corrupted Photo]".upper(),
                                      message="New defect has appeared, but it seems like there is incorrect "
                                              "base64-encoded representation of the photo for the new defect!.\n"
                                              f"Defect info:\n\n{defect_to_text}")
        return

    # Action logging
    log_type = "warning" if criticality == "normal" else f"{criticality}_defect"
    create_log_record(log_type, f"New {criticality}-level defect with id={json_payload["id"]} "
                                f"has appeared on the conveyor!")

    # New defect may cause changing of the general conveyor status
    create_record_of_current_general_conveyor_status()

    telegram_sending_details = None
    gmail_sending_details = None

    # Notification sending
    if not load_user_settings() or "Telegram" in load_user_settings()["new_defect_notification_scope"]:
        _, telegram_sending_details = await send_telegram_notification_from_server(
            f"{message_header} \n\n{defect_to_text}", io_file=defect_photo)
    if not load_user_settings() or "Gmail" in load_user_settings()["new_defect_notification_scope"]:
        _, gmail_sending_details = send_gmail_notification_from_server(
            message_header, f"Defect info: \n\n{defect_to_text}", io_file=defect_photo)

    if telegram_sending_details is None and gmail_sending_details is None:
        await notify_clients(json.dumps({"title": message_header, "text": defect_to_text}))
    else:
        await notify_clients(
            json.dumps({"title": message_header,
                        "text": "There were some errors when trying to send notification via Telegram or Gmail. \n"
                                f"Telegram error info: {telegram_sending_details}; \n"
                                f"Gmail error info: {gmail_sending_details}. \n\n"
                                f"Notification info: \n{defect_to_text}"}))


async def listen_for_new_defects():
    db_connection = await connect(settings.database_url)
    await db_connection.add_listener("new_defect", on_new_defect_notify_handler)
    while True:
        await sleep(1)
