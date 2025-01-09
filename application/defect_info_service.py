from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select
from base64 import b64encode
from .database_connection import engine
from .db_models import Defect, DefectType
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
        for defect, defect_type in results:
            response.append(form_response_model_from_defect(defect))
        return response


@router.get(path="/critical", response_model=list[DefectResponseModel])
def get_critical_defects():
    with Session(engine) as session:
        defects = session.exec(select(Defect).where(Defect.is_critical)).all()
        if not defects:
            raise HTTPException(status_code=404, detail=f"There is no critical-level defects")
        response = []
        for defect in defects:
            response.append(form_response_model_from_defect(defect))
        return response


@router.get(path="/extreme", response_model=list[DefectResponseModel])
def get_extreme_defects():
    with Session(engine) as session:
        defects = session.exec(select(Defect).where(Defect.is_extreme)).all()
        if not defects:
            raise HTTPException(status_code=404, detail=f"There is no extreme-level defects")
        response = []
        for defect in defects:
            response.append(form_response_model_from_defect(defect))
        return response
