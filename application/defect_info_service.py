from base64 import b64encode

from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select

from .database_connection import engine
from .db_models import Defect, DefectType, Relation
from .response_models import ServiceInfoResponseModel, DefectResponseModel

router = APIRouter(prefix="/defect_info", tags=["Defects Information Service"])


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
        is_critical=defect.is_critical,
        is_extreme=defect.is_extreme,
        base64_photo=b64encode(defect.photo_object.image).decode()
    )
    return response


@router.get(path="/", response_model=ServiceInfoResponseModel)
def get_service_info():
    return ServiceInfoResponseModel(
        info="Service providing information about emerging defects, their types and other useful parameters"
    )


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
        results = session.exec(select(Defect, DefectType).join(DefectType).
                               where(DefectType.name == defect_type)).all()
        if not results:
            raise HTTPException(status_code=404, detail=f"There is no defects of type '{defect_type}'")
        response = []
        for defect, _ in results:
            response.append(form_response_model_from_defect(defect))
        return response


@router.get(path="/critical", response_model=list[DefectResponseModel])
def get_critical_defects():
    with Session(engine) as session:
        defects = session.exec(select(Defect).where(Defect.is_critical)).all()
        if not defects:
            raise HTTPException(status_code=404, detail="There is no critical-level defects")
        response = []
        for defect in defects:
            response.append(form_response_model_from_defect(defect))
        return response


@router.get(path="/extreme", response_model=list[DefectResponseModel])
def get_extreme_defects():
    with Session(engine) as session:
        defects = session.exec(select(Defect).where(Defect.is_extreme)).all()
        if not defects:
            raise HTTPException(status_code=404, detail="There is no extreme-level defects")
        response = []
        for defect in defects:
            response.append(form_response_model_from_defect(defect))
        return response


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
        current_defect = session.exec(select(Relation).where(Relation.id_current == current_defect_id)).first()
        if not current_defect:
            raise HTTPException(status_code=404, detail=f"There is no defect with id={current_defect_id} "
                                                        f"or previous variations for it")

        response = []
        previous_defect = current_defect.previous_defect_object
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
            raise HTTPException(status_code=404, detail=f"There is no defect with id={defect_id}")

        defect.is_extreme = is_extreme
        defect.is_critical = is_critical
        session.add(defect)
        session.commit()
        session.refresh(defect)

        response = form_response_model_from_defect(defect)
        return response
