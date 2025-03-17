import requests

from fastapi import APIRouter, status
from sqlmodel import Session, select, desc

from .database_connection import engine
from .db_models import ObjectType, Object, ConveyorParameters, ConveyorStatus
from .response_models import ServiceInfoResponseModel, ConveyorParametersResponseModel, ConveyorStatusResponseModel

router = APIRouter(prefix="/conveyor_info", tags=["Conveyor General Information Service"])


def form_response_model_from_conveyor_status(conveyor_status: ConveyorStatus):
    """
    Create ConveyorStatusResponseModel from ConveyorStatus DB model using sqlmodel Relationship class and other DB models
    """
    is_normal = not conveyor_status.is_extreme and not conveyor_status.is_critical
    response = ConveyorStatusResponseModel(
        is_normal=is_normal,
        is_extreme=conveyor_status.is_extreme,
        is_critical=conveyor_status.is_critical
    )
    return response


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
            last_status_record = requests.post("http://127.0.0.1:8000/conveyor_info/create_record").json()
            return last_status_record
        response = form_response_model_from_conveyor_status(last_status_record)
        return response


def determine_criticality_of_conveyor_status(conveyor_status: ConveyorStatus):
    if conveyor_status.is_critical:
        return "critical"
    elif conveyor_status.is_extreme:
        return "extreme"
    else:
        return "normal"


@router.post(path="/create_record", response_model=ConveyorStatusResponseModel, status_code=status.HTTP_201_CREATED)
def create_record_of_current_general_conveyor_status():
    with Session(engine) as session:
        conv_status_object_type = session.exec(select(ObjectType).where(ObjectType.name == "conv_state")).one()
        base_object_for_new_conv_status = Object(type_object=conv_status_object_type)
        current_conv_status = ConveyorStatus(base_object=base_object_for_new_conv_status)

        critical_defects = requests.get("http://127.0.0.1:8000/defect_info/critical").json()
        extreme_defects = requests.get("http://127.0.0.1:8000/defect_info/extreme").json()
        if len(critical_defects) > 0:
            current_conv_status.is_extreme = False
            current_conv_status.is_critical = True
        elif len(extreme_defects) > 0:
            current_conv_status.is_extreme = True
            current_conv_status.is_critical = False
        else:
            current_conv_status.is_extreme = False
            current_conv_status.is_critical = False

        session.add(current_conv_status)
        session.commit()
        session.refresh(current_conv_status)

        # Action logging
        requests.post(url="http://127.0.0.1:8000/logs/create_record",
                      params={"log_type": "state_of_devices", "log_text": f"Current general status of conveyor is "
                                          f"\"{determine_criticality_of_conveyor_status(current_conv_status)}\""})

        response = form_response_model_from_conveyor_status(current_conv_status)
        return response
