from base64 import b64encode
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, and_, not_

from application.db_connection import engine
from application.models.db_models import Object, DefectType, Defect, Relation
from application.models.api_models import (ServiceInfoResponseModel, CountOfDefectGroupsResponseModel,
                                           DefectResponseModel, TypesOfDefectsResponseModel)
from application.services.authentication_service import get_current_admin_user
from application.services.conveyor_info_service import create_record_of_current_general_conveyor_status
from application.services.logging_service import create_log_record

router = APIRouter(prefix="/defect_info", tags=["Defects Information Service"],
                   dependencies=[Depends(get_current_admin_user)])


def determine_defect_criticality(defect: Defect):
    if defect.is_critical:
        return "critical"
    if defect.is_extreme:
        return "extreme"
    return "normal"


def determine_criticality_select_condition(criticality: str):
    if criticality == "critical":
        return Defect.is_critical
    if criticality == "extreme":
        return Defect.is_extreme
    if criticality == "normal":
        return and_(not_(Defect.is_critical), not_(Defect.is_extreme))
    return False


def form_response_model_from_defect(defect: Defect):
    """
    Create DefectResponseModel from Defect DB model using sqlmodel Relationship class and other DB models
    """
    response = DefectResponseModel(
        id=defect.id,
        timestamp=defect.base_object.time,
        type=defect.type_object.name,
        is_on_belt=defect.type_object.is_belt,
        box_width_in_mm=defect.box_width,
        box_length_in_mm=defect.box_length,
        longitudinal_position=defect.location_length_in_conv,
        transverse_position=defect.location_width_in_conv,
        probability=defect.probability,
        criticality=determine_defect_criticality(defect),
        base64_photo=b64encode(defect.photo_object.image).decode()
    )
    return response


@router.get(path="/", response_model=ServiceInfoResponseModel)
def get_service_info():
    return ServiceInfoResponseModel(
        info="Service providing information about emerging defects, their types and other useful parameters"
    )


@router.get(path="/count", response_model=CountOfDefectGroupsResponseModel)
def get_count_of_all_and_extreme_and_critical_defects():
    count_of_extreme = 0
    count_of_critical = 0

    with Session(engine) as session:
        defects = session.exec(select(Defect)).all()
        for defect in defects:
            if defect.is_critical:
                count_of_critical += 1
            elif defect.is_extreme:
                count_of_extreme += 1

    return CountOfDefectGroupsResponseModel(
        total=len(defects),
        extreme=count_of_extreme,
        critical=count_of_critical
    )


@router.get(path="/all", response_model=list[DefectResponseModel])
def get_all_defects():
    with Session(engine) as session:
        defects = session.exec(select(Defect).order_by(Defect.id)).all()
        return [form_response_model_from_defect(defect) for defect in defects]


@router.get(path="/id={defect_id}", response_model=DefectResponseModel)
def get_defect_by_id(defect_id: int):
    with Session(engine) as session:
        defect = session.exec(select(Defect).where(Defect.id == defect_id)).first()
        if not defect:
            raise HTTPException(status_code=404, detail=f"There is no defect with id={defect_id}")
        response = form_response_model_from_defect(defect)
        return response


@router.get(path="/type={defect_type}", response_model=list[DefectResponseModel])
def get_defects_of_certain_type(defect_type: str):
    with Session(engine) as session:
        results = session.exec(select(Defect, DefectType).join(DefectType).where(DefectType.name == defect_type).
                               order_by(Defect.id)).all()
        return [form_response_model_from_defect(defect) for defect, _ in results]


@router.get(path="/critical", response_model=list[DefectResponseModel])
def get_critical_defects():
    with Session(engine) as session:
        defects = session.exec(select(Defect).where(Defect.is_critical).order_by(Defect.id)).all()
        return [form_response_model_from_defect(defect) for defect in defects]


@router.get(path="/extreme", response_model=list[DefectResponseModel])
def get_extreme_defects():
    with Session(engine) as session:
        defects = session.exec(select(Defect).where(Defect.is_extreme).order_by(Defect.id)).all()
        return [form_response_model_from_defect(defect) for defect in defects]


@router.get(path="/by_period", response_model=list[DefectResponseModel])
def get_all_defects_in_certain_time_period(start_datetime: datetime = datetime.fromtimestamp(0, timezone.utc)
                                           .replace(tzinfo=None),
                                           end_datetime: datetime = datetime.now(timezone.utc).replace(tzinfo=None)):
    with Session(engine) as session:
        results = session.exec(select(Defect, Object).join(Object).
                               where(and_(start_datetime <= Object.time, Object.time <= end_datetime))
                               .order_by(Defect.id)).all()
        return [form_response_model_from_defect(defect) for defect, _ in results]


@router.get(path="/filtered", response_model=list[DefectResponseModel])
def get_filtered_defects_by_all_parameters(defect_type: str = "all", criticality: str = "all",
                                           start_datetime: datetime = datetime.fromtimestamp(0, timezone.utc)
                                           .replace(tzinfo=None),
                                           end_datetime: datetime = datetime.now(timezone.utc).replace(tzinfo=None)):
    type_select_condition = DefectType.name == defect_type
    criticality_select_condition = determine_criticality_select_condition(criticality)
    if defect_type == "all":
        type_select_condition = True
    if criticality == "all":
        criticality_select_condition = True

    with Session(engine) as session:
        results = session.exec(select(Defect, Object, DefectType).join(Object).join(DefectType).
                               where(and_(start_datetime <= Object.time, Object.time <= end_datetime,
                                          type_select_condition, criticality_select_condition))
                               .order_by(Defect.id)).all()
        return [form_response_model_from_defect(defect) for defect, _, _ in results]


@router.get(path="/all_types", response_model=TypesOfDefectsResponseModel)
def get_all_types_of_defects():
    with Session(engine) as session:
        result = session.exec(select(DefectType)).all()
        types = [defect_type.name for defect_type in result]
        return TypesOfDefectsResponseModel(
            count=len(result),
            types=types
        )


@router.get(path="/id={current_defect_id}/previous", response_model=DefectResponseModel)
def get_previous_variation_of_defect_by_id_of_current_one(current_defect_id: int):
    with Session(engine) as session:
        current_defect = session.exec(select(Relation).where(Relation.id_current == current_defect_id)).first()
        if not current_defect:
            raise HTTPException(status_code=404, detail=f"There is no defect with id={current_defect_id} "
                                                        f"or previous variations for it")
        previous_defect = current_defect.previous_defect_object
        response = form_response_model_from_defect(previous_defect)
        return response


@router.get(path="/id={current_defect_id}/chain_of_previous", response_model=list[DefectResponseModel])
def get_chain_of_all_previous_variations_of_defect_by_id(current_defect_id: int):
    with Session(engine) as session:
        defect = session.exec(select(Defect).where(Defect.id == current_defect_id)).first()
        if not defect:
            raise HTTPException(status_code=404, detail=f"There is no defect with id={current_defect_id}")
        current_defect_in_chain = session.exec(select(Relation).where(Relation.id_current == current_defect_id)).first()
        if not current_defect_in_chain:
            return []

        response = []
        previous_defect = current_defect_in_chain.previous_defect_object
        while True:
            response.append(form_response_model_from_defect(previous_defect))
            if not previous_defect.current_defect_in_relation:
                break
            previous_defect = previous_defect.current_defect_in_relation.previous_defect_object
        return response


@router.put(path="/id={defect_id}/set_criticality", response_model=DefectResponseModel)
def change_criticality_of_defect_by_id(defect_id: int, is_extreme: bool, is_critical: bool):
    with Session(engine) as session:
        defect = session.exec(select(Defect).where(Defect.id == defect_id)).first()
        if not defect:
            # Action logging
            create_log_record("warning", f"Failed to change criticality of defect with id={defect_id}: "
                                         "defect not found")
            raise HTTPException(status_code=404, detail=f"There is no defect with id={defect_id}")

        previous_criticality = determine_defect_criticality(defect)
        # Processing case of mutually exclusive values defining
        if is_extreme and is_critical:
            is_extreme = False
            is_critical = True
        if defect.is_extreme == is_extreme and defect.is_critical == is_critical:
            response = form_response_model_from_defect(defect)
            return response
        defect.is_extreme = is_extreme
        defect.is_critical = is_critical
        current_criticality = determine_defect_criticality(defect)

        session.add(defect)
        session.commit()
        session.refresh(defect)

        # Actions logging
        create_log_record("action_info", f"Criticality of defect with id={defect.id} successfully has "
                                         f"changed from \"{previous_criticality}\" to \"{current_criticality}\"")

        # Defect criticality changing causes changing of the general conveyor status
        create_record_of_current_general_conveyor_status()

        response = form_response_model_from_defect(defect)
        return response


@router.delete(path="/id={defect_id}/delete", response_model=DefectResponseModel)
def delete_defect_by_id(defect_id: int):
    with Session(engine) as session:
        defect = session.exec(select(Defect).where(Defect.id == defect_id)).first()
        if not defect:
            # Action logging
            create_log_record("warning",f"Failed to remove defect with id={defect_id}: defect not found")
            raise HTTPException(status_code=404, detail=f"There is no defect with id={defect_id}")
        response = form_response_model_from_defect(defect)

        # Defect removing causes changing of defect variations chain (relinking the “previous” link from the next defect
        # in the chain to the previous one)
        next_variation_of_defect = session.exec(select(Relation).where(Relation.id_previous == defect_id)).first()
        if next_variation_of_defect and defect.current_defect_in_relation:
            next_variation_of_defect.previous_defect_object = defect.current_defect_in_relation.previous_defect_object

        # Within one photo can be two defects so that photo deletion make sense if there is only one defect in the photo
        if len(defect.photo_object.defects) == 1:
            # Link to the photo object so that "ON CASCADE" deletion does not remove the entire defect
            photo_object = defect.photo_object
            defect.photo_object = None
            session.delete(photo_object.base_object)
        session.delete(defect.base_object)
        session.commit()

        # Action logging
        create_log_record("action_info", f"Defect with id={defect_id} has removed successfully")

        # Action logging (if "Relation" model contains record with id of defect => progress chain of defect will change
        # anyway)
        if next_variation_of_defect or defect.current_defect_in_relation:
            create_log_record("info", f"Progress chain for defect with id={defect_id} has changed")

        # Defect removing causes changing of the general conveyor status
        create_record_of_current_general_conveyor_status()

        return response
