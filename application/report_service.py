import requests

from fastapi import APIRouter
from sqlmodel import Session

from .database_connection import engine
from .response_models import ServiceInfoResponseModel

router = APIRouter(prefix="/report", tags=["Reports Generation Service"])


@router.get(path="/", response_model=ServiceInfoResponseModel)
def get_service_info():
    return ServiceInfoResponseModel(
        info="Service for generating reports on defects and conveyor status in .pdf or .csv format"
    )
