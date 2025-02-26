from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select

from .database_connection import engine
from .db_models import LogType, Log
from .response_models import ServiceInfoResponseModel, LogResponseModel

router = APIRouter(prefix="/logs", tags=["Logging Service"])


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


@router.get(path="/id={log_id}", response_model=LogResponseModel)
def get_log_by_id(log_id: int):
    with Session(engine) as session:
        log = session.exec(select(Log).where(Log.id == log_id)).first()
        if not log:
            raise HTTPException(status_code=404, detail=f"There is no log record with id={log_id}")
        response = form_response_model_from_log(log)
        return response
