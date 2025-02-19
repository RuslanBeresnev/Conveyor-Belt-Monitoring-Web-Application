from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select

from .database_connection import engine
from .db_models import ConveyorParameters
from .response_models import ServiceInfoResponseModel, ConveyorParametersResponseModel

router = APIRouter(prefix="/conveyor_info", tags=["Conveyor General Information Service"])


@router.get(path="/", response_model=ServiceInfoResponseModel)
def get_service_info():
    return ServiceInfoResponseModel(
        info="Service providing information about conveyor parameters and general status"
    )


@router.get(path="/parameters", response_model=ConveyorParametersResponseModel)
def get_base_conveyor_parameters():
    with Session(engine) as session:
        # Always select first entry because table 'ConveyorParameters' stores info about the only one conveyor
        info = session.exec(select(ConveyorParameters).where(ConveyorParameters.id == 1)).one()
        return ConveyorParametersResponseModel(
            belt_length=info.belt_length,
            belt_width=info.belt_width,
            belt_thickness=info.belt_thickness
        )
