from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select, desc

from .database_connection import engine
from .db_models import ConveyorParameters, ConveyorStatus
from .response_models import ServiceInfoResponseModel, ConveyorParametersResponseModel, ConveyorStatusResponseModel

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


@router.get(path="/status", response_model=ConveyorStatusResponseModel)
def get_general_status_of_conveyor():
    with Session(engine) as session:
        last_status_record = session.exec(select(ConveyorStatus).order_by(desc(ConveyorStatus.id))).first()
        if not last_status_record:
            raise HTTPException(status_code=404, detail=f"There are no records of general conveyor status yet")
        is_normal = not last_status_record.is_extreme and not last_status_record.is_critical
        response = ConveyorStatusResponseModel(
            is_normal=is_normal,
            is_extreme=last_status_record.is_extreme,
            is_critical=last_status_record.is_critical
        )
        return response
