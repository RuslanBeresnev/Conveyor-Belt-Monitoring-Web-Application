from datetime import datetime, timezone

from fastapi import APIRouter, Depends, status
from sqlmodel import Session, select, desc

from application.db_connection import engine
from application.models.db_models import ObjectType, Object, ConveyorParameters, ConveyorStatus, Defect
from application.models.api_models import (ServiceInfoResponseModel, ConveyorParametersResponseModel,
                                           ConveyorStatusResponseModel, NewConveyorParameters)
from application.services.authentication_service import get_current_admin_user
from application.services.logging_service import create_log_record

router = APIRouter(prefix="/conveyor_info", tags=["Conveyor General Information Service"],
                   dependencies=[Depends(get_current_admin_user)])


def determine_criticality_of_conveyor_status(conveyor_status: ConveyorStatus):
    if conveyor_status.is_critical:
        return "critical"
    if conveyor_status.is_extreme:
        return "extreme"
    return "normal"


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
            last_status_record = create_record_of_current_general_conveyor_status()
            return last_status_record
        return ConveyorStatusResponseModel(
            status=determine_criticality_of_conveyor_status(last_status_record)
        )


@router.post(path="/create_record", response_model=ConveyorStatusResponseModel, status_code=status.HTTP_201_CREATED)
def create_record_of_current_general_conveyor_status():
    with Session(engine) as session:
        conv_status_object_type = session.exec(select(ObjectType).where(ObjectType.name == "conv_state")).one()
        defects = session.exec(select(Defect)).all()

        count_of_critical_defects = sum(1 for defect in defects if defect.is_critical)
        count_of_extreme_defects = sum(1 for defect in defects if defect.is_extreme)

        current_status = None
        if count_of_critical_defects > 0:
            current_status = "critical"
        elif count_of_extreme_defects > 0:
            current_status = "extreme"
        else:
            current_status = "normal"

        previous_status = None
        last_status_record = session.exec(select(ConveyorStatus).order_by(desc(ConveyorStatus.id))).first()
        if last_status_record:
            previous_status = determine_criticality_of_conveyor_status(last_status_record)

        if last_status_record is None or current_status != previous_status:
            base_object_for_new_conv_status = Object(type_object=conv_status_object_type,
                                                     time=datetime.now(timezone.utc).replace(tzinfo=None))
            current_conv_status_object = ConveyorStatus(base_object=base_object_for_new_conv_status)

            current_conv_status_object.is_critical = current_status == "critical"
            current_conv_status_object.is_extreme = current_status == "extreme"

            session.add(conv_status_object_type)
            session.add(current_conv_status_object)
            session.commit()

            # Action logging
            create_log_record("state_of_devices", f"Set current general status of conveyor: "
                                                  f"\"{current_status}\"")

        return ConveyorStatusResponseModel(
            status=current_status
        )


@router.put(path="/change_parameters", response_model=ConveyorParametersResponseModel)
def change_base_conveyor_parameters(new_parameters: NewConveyorParameters):
    with Session(engine) as session:
        current_params = session.exec(select(ConveyorParameters).where(ConveyorParameters.id == 1)).one()
        current_params.belt_length = new_parameters.new_belt_length
        current_params.belt_width = new_parameters.new_belt_width
        current_params.belt_thickness = new_parameters.new_belt_thickness

        session.add(current_params)
        session.commit()

        # Action logging
        create_log_record("state_of_devices", "Base parameters of the conveyor were updated")

        return ConveyorParametersResponseModel(
            belt_length=current_params.belt_length,
            belt_width=current_params.belt_width,
            belt_thickness=current_params.belt_thickness
        )
