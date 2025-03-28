from datetime import datetime
import requests

from fastapi import APIRouter, HTTPException
from sqlmodel import SQLModel, Session, select, text

from .db_models import (ObjectType, Object, DefectType, Photo, Defect, Relation, ConveyorParameters,
                        ConveyorStatus, LogType, Log, Version, CameraSettings)
from .database_connection import engine
from .api_models import ServiceInfoResponseModel, MaintenanceActionResponseModel, NewConveyorParameters

router = APIRouter(prefix="/maintenance", tags=["Maintenance Service"])


@router.get(path="/", response_model=ServiceInfoResponseModel)
def get_service_info():
    return ServiceInfoResponseModel(
        info="Service providing functionality to support a database and application"
    )


@router.post(path="/create_tables", response_model=MaintenanceActionResponseModel)
def create_or_recreate_all_database_tables(test_mode: bool = False):
    if not test_mode:
        with Session(engine) as session:
            # Removing trigger function with trigger (SQLModel.metadata.drop_all() removes only tables)
            session.connection().execute(text("DROP FUNCTION IF EXISTS notify_on_new_defect CASCADE;"))
            session.commit()

    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)

    # Creating trigger and trigger function for the table "defects" (apart the case when running in the test mode)
    raw_sql = """
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

    return MaintenanceActionResponseModel(
        maintenance_info="All database tables and triggers were created"
    )


@router.post(path="/fill_database", response_model=MaintenanceActionResponseModel)
def fill_database_with_required_and_test_data():
    # pylint: disable=R0914
    with Session(engine) as session:
        current_db_version = Version()
        session.add(current_db_version)

        conveyor_default_parameters = ConveyorParameters()
        session.add(conveyor_default_parameters)

        object_type_for_defect = ObjectType(name="defect")
        object_type_for_conv_state = ObjectType(name="conv_state")
        object_type_for_history = ObjectType(name="history")
        object_type_for_photo = ObjectType(name="photo")
        session.add(object_type_for_defect)
        session.add(object_type_for_conv_state)
        session.add(object_type_for_history)
        session.add(object_type_for_photo)

        defect_type_chip = DefectType(name="chip", is_belt=False)
        defect_type_delamination = DefectType(name="delamination", is_belt=False)
        defect_type_rope = DefectType(name="rope")
        defect_type_crack = DefectType(name="crack")
        defect_type_liftup = DefectType(name="liftup")
        defect_type_hole = DefectType(name="hole")
        defect_type_tear = DefectType(name="tear")
        defect_type_wear = DefectType(name="wear")
        defect_type_joint = DefectType(name="joint")
        defect_type_joint_worn = DefectType(name="joint_worn")
        session.add(defect_type_chip)
        session.add(defect_type_delamination)
        session.add(defect_type_rope)
        session.add(defect_type_crack)
        session.add(defect_type_liftup)
        session.add(defect_type_hole)
        session.add(defect_type_tear)
        session.add(defect_type_wear)
        session.add(defect_type_joint)
        session.add(defect_type_joint_worn)

        object_of_defect_1 = Object(type_object=object_type_for_defect, time=datetime(2025, 1, 1))
        object_of_defect_2 = Object(type_object=object_type_for_defect, time=datetime(2025, 1, 2))
        object_of_photo_1 = Object(type_object=object_type_for_photo, time=datetime(2025, 1, 1))
        object_of_photo_2 = Object(type_object=object_type_for_photo, time=datetime(2025, 1, 2))
        session.add(object_of_defect_1)
        session.add(object_of_defect_2)
        session.add(object_of_photo_1)
        session.add(object_of_photo_2)

        photo_1 = Photo(base_object=object_of_photo_1, image=open("application/test_defect.jpg", "rb").read())
        photo_2 = Photo(base_object=object_of_photo_2, image=open("application/test_defect.jpg", "rb").read())
        session.add(photo_1)
        session.add(photo_2)

        extreme_defect = Defect(base_object=object_of_defect_1, type_object=defect_type_hole, box_width=400,
                                box_length=400, location_width_in_frame=10, location_length_in_frame=10,
                                location_width_in_conv=10, location_length_in_conv=10, photo_object=photo_1,
                                probability=90, is_critical=False, is_extreme=True)
        critical_defect = Defect(base_object=object_of_defect_2, type_object=defect_type_rope, box_width=500,
                                 box_length=500, location_width_in_frame=10, location_length_in_frame=10,
                                 location_width_in_conv=10, location_length_in_conv=10, photo_object=photo_2,
                                 probability=95, is_critical=True, is_extreme=False)
        session.add(extreme_defect)
        session.add(critical_defect)

        defects_relation = Relation(current_defect_object=critical_defect, previous_defect_object=extreme_defect)
        session.add(defects_relation)

        log_type_error = LogType(name="error")
        log_type_warning = LogType(name="warning")
        log_type_info = LogType(name="info")
        log_type_critical_defect = LogType(name="critical_defect")
        log_type_extreme_defect = LogType(name="extreme_defect")
        log_type_action_info = LogType(name="action_info")
        log_type_report_info = LogType(name="report_info")
        log_type_message = LogType(name="message")
        log_type_state_of_devices = LogType(name="state_of_devices")
        session.add(log_type_error)
        session.add(log_type_warning)
        session.add(log_type_info)
        session.add(log_type_critical_defect)
        session.add(log_type_extreme_defect)
        session.add(log_type_action_info)
        session.add(log_type_report_info)
        session.add(log_type_message)
        session.add(log_type_state_of_devices)

        session.commit()

        # Action logging
        requests.post(url="http://127.0.0.1:8000/logs/create_record", params={"log_type": "info", "log_text":
            "Database was filled with required fields and test defects"})

        return MaintenanceActionResponseModel(
            maintenance_info="Database was filled with required fields and test defects"
        )


@router.post(path="/add_test_defect", response_model=MaintenanceActionResponseModel)
def add_test_defect_to_database():
    with Session(engine) as session:
        object_type_for_defect = session.exec(select(ObjectType).where(ObjectType.name == "defect")).one()
        object_type_for_photo = session.exec(select(ObjectType).where(ObjectType.name == "photo")).one()
        object_of_defect_type = session.exec(select(DefectType).where(DefectType.name == "wear")).one()

        object_of_defect = Object(type_object=object_type_for_defect, time=datetime(2025, 2, 1))
        object_of_photo = Object(type_object=object_type_for_photo, time=datetime(2025, 2, 1))
        session.add(object_of_defect)
        session.add(object_of_photo)

        photo = Photo(base_object=object_of_photo, image=open("application/test_defect.jpg", "rb").read())
        session.add(photo)

        defect = Defect(base_object=object_of_defect, type_object=object_of_defect_type, box_width=200,
                        box_length=200, location_width_in_frame=5, location_length_in_frame=5,
                        location_width_in_conv=5, location_length_in_conv=5, photo_object=photo,
                        probability=99, is_critical=False, is_extreme=False)
        session.add(defect)

        session.commit()

        # Action logging
        requests.post(url="http://127.0.0.1:8000/logs/create_record", params={"log_type": "info", "log_text":
            "New test defect was added to the database"})

        return MaintenanceActionResponseModel(
            maintenance_info="New test defect was added to the database"
        )


@router.post(path="/make_relation", response_model=MaintenanceActionResponseModel)
def create_relation_between_two_defects_without_chain_checking(previous_defect_id: int, current_defect_id: int):
    with Session(engine) as session:
        if previous_defect_id == current_defect_id:
            # Action logging
            requests.post(url="http://127.0.0.1:8000/logs/create_record", params={"log_type": "info", "log_text":
                f"Failed to create relation for a defect with oneself (id={current_defect_id})"})
            raise HTTPException(status_code=403, detail="It is forbidden to create relation for a defect with oneself")

        previous_defect = session.exec(select(Defect).where(Defect.id == previous_defect_id)).first()
        current_defect = session.exec(select(Defect).where(Defect.id == current_defect_id)).first()
        if not previous_defect or not current_defect:
            # Action logging
            requests.post(url="http://127.0.0.1:8000/logs/create_record", params={"log_type": "info", "log_text":
                f"Failed to create relation between defects with id={previous_defect_id} and id={current_defect_id}: "
                f"id not found"})
            raise HTTPException(status_code=404, detail=f"There are no defects with id={previous_defect_id} or with "
                                                        f"id={current_defect_id}")

        relation = Relation(previous_defect_object=previous_defect, current_defect_object=current_defect)
        session.add(relation)
        session.commit()

    # Action logging
    requests.post(url="http://127.0.0.1:8000/logs/create_record", params={"log_type": "info", "log_text":
        f"Relation between defect with id={previous_defect_id} and defect with id={current_defect_id} was created"})

    return MaintenanceActionResponseModel(
        maintenance_info=f"Relation between defects with id={previous_defect_id} and id={current_defect_id} "
                         f"was created"
    )


@router.post(path="/remove_relation", response_model=MaintenanceActionResponseModel)
def remove_relation_between_two_defects_without_chain_checking(previous_defect_id: int, current_defect_id: int):
    with (Session(engine) as session):
        if previous_defect_id == current_defect_id:
            # Action logging
            requests.post(url="http://127.0.0.1:8000/logs/create_record", params={"log_type": "info", "log_text":
                f"Failed to remove relation for a defect with oneself (id={current_defect_id})"})
            raise HTTPException(status_code=403, detail="It is forbidden to remove relation for a defect with oneself")

        relation_for_current = session.exec(select(Relation).where(Relation.id_current == current_defect_id)).first()
        relation_for_previous = session.exec(select(Relation).where(Relation.id_previous == previous_defect_id)).first()
        if not relation_for_current or not relation_for_previous or relation_for_current != relation_for_previous:
            # Action logging
            requests.post(url="http://127.0.0.1:8000/logs/create_record", params={"log_type": "info", "log_text":
                f"Failed to remove relation between defects with id={previous_defect_id} and id={current_defect_id}:"
                f"id not found or defects not related"})
            raise HTTPException(status_code=404, detail=f"Either there are no defects with id={previous_defect_id} and "
                                                        f"with id={current_defect_id} or these ones aren't related")

        session.delete(relation_for_current)
        session.commit()

    # Action logging
    requests.post(url="http://127.0.0.1:8000/logs/create_record", params={"log_type": "info", "log_text":
        f"Relation between defects with id={previous_defect_id} and id={current_defect_id} was removed"})

    return MaintenanceActionResponseModel(
        maintenance_info=f"Relation between defects with id={previous_defect_id} and id={current_defect_id} was removed"
    )


@router.post(path="/change_conveyor_parameters", response_model=MaintenanceActionResponseModel)
def change_base_parameters_of_conveyor(new_parameters: NewConveyorParameters):
    with Session(engine) as session:
        current_params = session.exec(select(ConveyorParameters).where(ConveyorParameters.id == 1)).one()
        current_params.belt_length = new_parameters.new_belt_length
        current_params.belt_width = new_parameters.new_belt_width
        current_params.belt_thickness = new_parameters.new_belt_thickness

        session.add(current_params)
        session.commit()

    # Action logging
    requests.post(url="http://127.0.0.1:8000/logs/create_record", params={"log_type": "info", "log_text":
        "Base parameters of the conveyor were updated"})

    return MaintenanceActionResponseModel(
        maintenance_info="Base parameters of the conveyor were updated"
    )
