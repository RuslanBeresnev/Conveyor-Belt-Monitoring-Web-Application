from datetime import datetime
from json import JSONDecodeError
from typing import Annotated

import asyncio

from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import ValidationError
from sqlmodel import SQLModel, Session, select, text
from sqlalchemy.exc import OperationalError, DatabaseError
from passlib.context import CryptContext

from application.config import settings
from application.db_connection import engine
from application.models.db_models import (ObjectType, Object, DefectType, Photo, Defect, Relation, ConveyorParameters,
                                          LogType, Version, User)
from application.models.api_models import (ServiceInfoResponseModel, MaintenanceActionResponseModel,
                                           UserNotificationSettings)
from application.user_settings import save_user_settings, load_user_settings
from application.services.authentication_service import get_current_admin_user
from application.services.logging_service import create_log_record

router = APIRouter(prefix="/maintenance", tags=["Maintenance Service"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

connectedClients = set()


async def notify_clients(message: str):
    for queue in list(connectedClients):
        await queue.put(message)


def create_versions():
    return [Version()]


def create_conveyor_parameters():
    return [ConveyorParameters()]


def create_object_types():
    return [
        ObjectType(name="defect"),
        ObjectType(name="conv_state"),
        ObjectType(name="history"),
        ObjectType(name="photo"),
    ]


def create_defect_types():
    return [
        DefectType(name="chip", is_belt=False),
        DefectType(name="delamination", is_belt=False),
        DefectType(name="rope"),
        DefectType(name="crack"),
        DefectType(name="liftup"),
        DefectType(name="hole"),
        DefectType(name="tear"),
        DefectType(name="wear"),
        DefectType(name="joint"),
        DefectType(name="joint_worn"),
    ]


def create_objects(object_types):
    defect_type = next((object_type for object_type in object_types if object_type.name == "defect"), None)
    photo_type = next((object_type for object_type in object_types if object_type.name == "photo"), None)

    return [
        Object(type_object=defect_type, time=datetime(2025, 1, 1)),
        Object(type_object=defect_type, time=datetime(2025, 1, 2)),
        Object(type_object=photo_type, time=datetime(2025, 1, 1)),
        Object(type_object=photo_type, time=datetime(2025, 1, 2)),
    ]


def create_photos(objects_photo):
    with open("application/services/test_defect.jpg", "rb") as file:
        image_data = file.read()

    return [
        Photo(base_object=objects_photo[0], image=image_data),
        Photo(base_object=objects_photo[1], image=image_data),
    ]


def create_defects(objects_of_defects, defect_types, photos):
    defect_type_hole = next(defect_type for defect_type in defect_types if defect_type.name == "hole")
    defect_type_rope = next(defect_type for defect_type in defect_types if defect_type.name == "rope")

    return [
        Defect(
            base_object=objects_of_defects[0],
            type_object=defect_type_hole,
            box_width=400,
            box_length=400,
            location_width_in_frame=10,
            location_length_in_frame=10,
            location_width_in_conv=216,
            location_length_in_conv=4870000,
            photo_object=photos[0],
            probability=90,
            is_critical=False,
            is_extreme=True,
        ),
        Defect(
            base_object=objects_of_defects[1],
            type_object=defect_type_rope,
            box_width=500,
            box_length=500,
            location_width_in_frame=10,
            location_length_in_frame=10,
            location_width_in_conv=1530,
            location_length_in_conv=10516000,
            photo_object=photos[1],
            probability=95,
            is_critical=True,
            is_extreme=False,
        ),
    ]


def create_relations(defects):
    return [Relation(current_defect_object=defects[1], previous_defect_object=defects[0])]


def create_log_types():
    return [
        LogType(name="error"),
        LogType(name="warning"),
        LogType(name="info"),
        LogType(name="critical_defect"),
        LogType(name="extreme_defect"),
        LogType(name="action_info"),
        LogType(name="report_info"),
        LogType(name="message"),
        LogType(name="state_of_devices"),
    ]


def add_entities_to_session(session: Session, entities: list):
    for entity in entities:
        session.add(entity)


@router.get(path="/", response_model=ServiceInfoResponseModel, dependencies=[Depends(get_current_admin_user)])
def get_service_info():
    return ServiceInfoResponseModel(
        info="Service providing functionality to support a database and application"
    )


@router.get(path="/get_events")
async def subscribe_client_to_server_events(request: Request):
    async def event_generator():
        queue = asyncio.Queue()
        connectedClients.add(queue)
        while True:
            # On connection closing by client side
            if await request.is_disconnected():
                break
            try:
                data = await asyncio.wait_for(queue.get(), timeout=1)
                yield f"data: {data}\n\n"
            except asyncio.TimeoutError:
                # To be able to check the request.is_disconnected() condition
                continue
        connectedClients.discard(queue)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get(path="/check_server", response_model=MaintenanceActionResponseModel,
            dependencies=[Depends(get_current_admin_user)])
def check_server_availability():
    return MaintenanceActionResponseModel(maintenance_info="OK")


@router.get(path="/check_database", response_model=MaintenanceActionResponseModel,
            dependencies=[Depends(get_current_admin_user)])
def check_database_availability():
    try:
        with Session(engine) as session:
            session.connection().execute(text("SELECT 0"))
        return MaintenanceActionResponseModel(maintenance_info="OK")
    except UnicodeDecodeError as e:
        raise HTTPException(status_code=503, detail="Connection to the database could not be established "
                                                    "because connection string in configuration is invalid") from e
    except OperationalError as e:
        raise HTTPException(status_code=503, detail="Some problems with database connection") from e
    except DatabaseError as e:
        raise HTTPException(status_code=503, detail="Some problems in database") from e


@router.post(path="/create_tables", response_model=MaintenanceActionResponseModel)
def create_or_recreate_all_database_tables(user_admin: Annotated[User, Depends(get_current_admin_user)],
                                           test_mode: bool = False):
    if not test_mode:
        with Session(engine) as session:
            # Removing trigger function with trigger (SQLModel.metadata.drop_all() removes only tables)
            session.connection().execute(text("DROP FUNCTION IF EXISTS notify_on_new_defect CASCADE;"))
            session.commit()

    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)

    # Creating trigger and trigger function for the table "defects" (apart the case when running in the test mode)
    raw_sql = \
        """
        CREATE OR REPLACE FUNCTION notify_on_new_defect()
        RETURNS TRIGGER AS $$
        DECLARE
            payload TEXT;
        BEGIN
            payload := row_to_json(NEW)::TEXT;
            PERFORM pg_notify('new_defect', payload);
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        CREATE TRIGGER trigger_on_new_defect
        AFTER INSERT ON defects
        FOR EACH ROW
        EXECUTE FUNCTION notify_on_new_defect();
        """
    if not test_mode:
        with Session(engine) as session:
            session.connection().execute(text(raw_sql))
            session.commit()

    with Session(engine) as session:
        user_admin = User(username=settings.admin_username, role="Admin",
                          password=pwd_context.hash(settings.admin_password))
        session.add(user_admin)
        session.commit()

    return MaintenanceActionResponseModel(
        maintenance_info="All database tables and triggers were created"
    )


@router.post("/fill_database", response_model=MaintenanceActionResponseModel,
             dependencies=[Depends(get_current_admin_user)])
def fill_database_with_required_and_test_data():
    with Session(engine) as session:
        versions = create_versions()
        conveyor_params = create_conveyor_parameters()
        object_types = create_object_types()
        defect_types = create_defect_types()
        objects = create_objects(object_types)
        photos = create_photos(objects[2:4])
        defects = create_defects(objects[0:2], defect_types, photos)
        relations = create_relations(defects)
        log_types = create_log_types()

        data = [versions, conveyor_params, object_types, defect_types, objects, photos, defects, relations, log_types]
        for group_of_entities in data:
            add_entities_to_session(session, group_of_entities)

        session.commit()

    # Action logging
    create_log_record("info", "Database was filled with required fields and test defects")

    return MaintenanceActionResponseModel(
        maintenance_info="Database was filled with required fields and test defects"
    )


@router.post(path="/add_test_defect", response_model=MaintenanceActionResponseModel,
             dependencies=[Depends(get_current_admin_user)])
def add_test_defect_to_database():
    with Session(engine) as session:
        object_type_for_defect = session.exec(select(ObjectType).where(ObjectType.name == "defect")).one()
        object_type_for_photo = session.exec(select(ObjectType).where(ObjectType.name == "photo")).one()
        object_of_defect_type = session.exec(select(DefectType).where(DefectType.name == "wear")).one()

        object_of_defect = Object(type_object=object_type_for_defect, time=datetime(2025, 2, 1))
        object_of_photo = Object(type_object=object_type_for_photo, time=datetime(2025, 2, 1))
        session.add(object_of_defect)
        session.add(object_of_photo)

        with open("application/services/test_defect.jpg", "rb") as file:
            photo = Photo(base_object=object_of_photo, image=file.read())
        session.add(photo)

        defect = Defect(base_object=object_of_defect, type_object=object_of_defect_type, box_width=200,
                        box_length=200, location_width_in_frame=5, location_length_in_frame=5,
                        location_width_in_conv=450, location_length_in_conv=1210000, photo_object=photo,
                        probability=99, is_critical=False, is_extreme=False)
        session.add(defect)

        session.commit()

        # Action logging
        create_log_record("info", "New test defect was added to the database")

        return MaintenanceActionResponseModel(
            maintenance_info="New test defect was added to the database"
        )


@router.post(path="/make_relation", response_model=MaintenanceActionResponseModel,
             dependencies=[Depends(get_current_admin_user)])
def create_relation_between_two_defects_without_chain_checking(previous_defect_id: int, current_defect_id: int):
    with Session(engine) as session:
        if previous_defect_id == current_defect_id:
            # Action logging
            create_log_record("warning", "Failed to create relation for a defect with oneself "
                                         f"(id={current_defect_id})")
            raise HTTPException(status_code=403, detail="It is forbidden to create relation for a defect with oneself")

        previous_defect = session.exec(select(Defect).where(Defect.id == previous_defect_id)).first()
        current_defect = session.exec(select(Defect).where(Defect.id == current_defect_id)).first()
        if not previous_defect or not current_defect:
            # Action logging
            create_log_record("warning", "Failed to create relation between defects with "
                                         f"id={previous_defect_id} and id={current_defect_id}: id not found")
            raise HTTPException(status_code=404, detail=f"There are no defects with id={previous_defect_id} or with "
                                                        f"id={current_defect_id}")

        relation = Relation(previous_defect_object=previous_defect, current_defect_object=current_defect)
        session.add(relation)
        session.commit()

    # Action logging
    create_log_record("info", f"Relation between defect with id={previous_defect_id} and defect "
                              f"with id={current_defect_id} was created")

    return MaintenanceActionResponseModel(
        maintenance_info=f"Relation between defects with id={previous_defect_id} and id={current_defect_id} "
                         f"was created"
    )


@router.delete(path="/remove_relation", response_model=MaintenanceActionResponseModel,
               dependencies=[Depends(get_current_admin_user)])
def remove_relation_between_two_defects_without_chain_checking(previous_defect_id: int, current_defect_id: int):
    with Session(engine) as session:
        if previous_defect_id == current_defect_id:
            # Action logging
            create_log_record("warning", "Failed to remove relation for a defect with oneself "
                                         f"(id={current_defect_id})")
            raise HTTPException(status_code=403, detail="It is forbidden to remove relation for a defect with oneself")

        relation_for_current = session.exec(select(Relation).where(Relation.id_current == current_defect_id)).first()
        relation_for_previous = session.exec(select(Relation).where(Relation.id_previous == previous_defect_id)).first()
        if not relation_for_current or not relation_for_previous or relation_for_current != relation_for_previous:
            # Action logging
            create_log_record("warning", "Failed to remove relation between defects with "
                                         f"id={previous_defect_id} and id={current_defect_id}: id not found or "
                                         "defects not related")
            raise HTTPException(status_code=404, detail=f"Either there are no defects with id={previous_defect_id} and "
                                                        f"with id={current_defect_id} or these ones aren't related")

        session.delete(relation_for_current)
        session.commit()

    # Action logging
    create_log_record("info", f"Relation between defects with id={previous_defect_id} and "
                              f"id={current_defect_id} was removed")

    return MaintenanceActionResponseModel(
        maintenance_info=f"Relation between defects with id={previous_defect_id} and id={current_defect_id} was removed"
    )


@router.get(path="/get_user_notification_settings", response_model=UserNotificationSettings,
            dependencies=[Depends(get_current_admin_user)])
def get_user_notification_settings():
    try:
        user_settings = load_user_settings()
    except JSONDecodeError as e:
        raise HTTPException(status_code=500, detail="Invalid JSON-data in .user_settings file") from e

    if not user_settings:
        raise HTTPException(status_code=500, detail="There is no .user_settings file on the server")

    try:
        UserNotificationSettings(**user_settings)
    except ValidationError as e:
        raise HTTPException(status_code=500, detail="Incorrect notification settings in .user_settings file") from e

    return user_settings


@router.put(path="/update_user_notification_settings", response_model=UserNotificationSettings,
            dependencies=[Depends(get_current_admin_user)])
def update_user_notification_settings(updated_settings: UserNotificationSettings):
    save_user_settings(updated_settings.model_dump())
    return updated_settings
