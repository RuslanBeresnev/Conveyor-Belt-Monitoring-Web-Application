from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select

from .database_connection import engine
from .response_models import ServiceInfoResponseModel

router = APIRouter(prefix="/logs", tags=["Logging Service"])


@router.get(path="/", response_model=ServiceInfoResponseModel)
def get_service_info():
    return ServiceInfoResponseModel(
        info="Service providing all logs of the system behaviour, services and application entities"
    )
