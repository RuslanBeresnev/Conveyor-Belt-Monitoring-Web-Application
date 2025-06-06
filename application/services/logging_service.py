from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, desc, text

from application.db_connection import engine
from application.models.db_models import ObjectType, Object, LogType, Log
from application.models.api_models import ServiceInfoResponseModel, LogResponseModel, AllLogsRemovingResponseModel
from application.services.authentication_service import get_current_admin_user

router = APIRouter(prefix="/logs", tags=["Logging Service"],
                   dependencies=[Depends(get_current_admin_user)])


def form_response_model_from_log(log: Log):
    """
    Create LogResponseModel from Log DB model using sqlmodel Relationship class and other DB models
    """
    response = LogResponseModel(
        id=log.id,
        timestamp=log.base_object.time,
        type=log.type_object.name,
        text=log.action
    )
    return response


@router.get(path="/", response_model=ServiceInfoResponseModel)
def get_service_info():
    return ServiceInfoResponseModel(
        info="Service providing all logs of the system behaviour, services and application entities"
    )


@router.get(path="/all", response_model=list[LogResponseModel])
def get_all_log_records_in_reverse_order():
    with Session(engine) as session:
        logs = session.exec(select(Log).order_by(desc(Log.id))).all()
        return [form_response_model_from_log(log) for log in logs]


@router.get(path="/id={log_id}", response_model=LogResponseModel)
def get_log_record_by_id(log_id: int):
    with Session(engine) as session:
        log = session.exec(select(Log).where(Log.id == log_id)).first()
        if not log:
            raise HTTPException(status_code=404, detail=f"There is no log record with id={log_id}")
        response = form_response_model_from_log(log)
        return response


@router.get(path="/type={log_type}", response_model=list[LogResponseModel])
def get_log_records_of_certain_type(log_type: str):
    with Session(engine) as session:
        results = session.exec(select(Log, LogType).join(LogType).where(LogType.name == log_type).
                               order_by(Log.id)).all()
        return [form_response_model_from_log(log) for log, _ in results]


@router.post(path="/create_record", response_model=LogResponseModel)
def create_log_record(log_type: str, log_text: str):
    with Session(engine) as session:
        log_record_object_type = session.exec(select(ObjectType).where(ObjectType.name == "history")).one()
        base_object_for_new_log_record = Object(type_object=log_record_object_type, time=datetime.now())
        session.add(base_object_for_new_log_record)
        log_type_object = session.exec(select(LogType).where(LogType.name == log_type)).first()
        if not log_type_object:
            raise HTTPException(status_code=404, detail=f"There is no log record type with title={log_type}")
        new_log_record = Log(action=log_text, base_object=base_object_for_new_log_record, type_object=log_type_object)

        session.add(new_log_record)
        session.commit()
        session.refresh(new_log_record)

        response = form_response_model_from_log(new_log_record)
        return response


@router.delete(path="/id={log_id}/delete", response_model=LogResponseModel)
def delete_log_record_by_id(log_id: int, log_deletion_event: bool = True):
    with Session(engine) as session:
        log = session.exec(select(Log).where(Log.id == log_id)).first()
        if not log:
            # Action logging
            create_log_record("warning",
                                               f"Failed to remove log record with id={log_id}: record not found")
            raise HTTPException(status_code=404, detail=f"There is no log record with id={log_id}")
        response = form_response_model_from_log(log)

        session.delete(log.base_object)
        session.commit()

        # Action logging
        if log_deletion_event:
            create_log_record("action_info",
                                               f"Log record with id={log_id} has removed successfully")

        return response


@router.delete(path="/delete_all", response_model=AllLogsRemovingResponseModel)
def delete_all_log_records(log_deletion_event: bool = True):
    with Session(engine) as session:
        all_logs = session.exec(select(Log)).all()
        count_to_remove = len(all_logs)

        if count_to_remove == 0:
            return AllLogsRemovingResponseModel(
                status="There were no log records, so nothing was deleted",
                count_of_removed=0
            )

        for log in all_logs:
            session.delete(log.base_object)
        # Reset to 1 auto-incremental id counter
        session.connection().execute(text(f"ALTER SEQUENCE {Log.__tablename__}_id_seq RESTART WITH 1"))
        session.commit()

        # Action logging
        if log_deletion_event:
            create_log_record("action_info", "All log records has removed successfully")

        return AllLogsRemovingResponseModel(
            status="All log records was deleted",
            count_of_removed=count_to_remove
        )
