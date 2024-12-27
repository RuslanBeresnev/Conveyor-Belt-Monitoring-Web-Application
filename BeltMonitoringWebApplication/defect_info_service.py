from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select
from base64 import b64encode
from datetime import datetime
from database_connection import engine
from db_models import Defect

router = APIRouter(prefix="/defect_info", tags=["Defects Information Service"])


class DefectResponseModel(BaseModel):
    id: int
    timestamp: datetime  # from Object model
    type: str  # from DefectType model
    is_on_belt: bool  # from DefectType model
    box_width_in_mm: int
    box_length_in_mm: int
    longitudinal_position: int  # "location_length_in_conv" parameter
    transverse_position: int  # "location_width_in_conv" parameter
    probability: int
    is_critical: bool
    is_extreme: bool
    base64_photo: str  # from Photo model (converted to base64 format)


@router.get("/")
def get_service_info():
    return {"info": "Service providing information about emerging defects, their types and other useful parameters"}


@router.get("/id={defect_id}", response_model=DefectResponseModel)
def get_defect_by_id(defect_id: int):
    with Session(engine) as session:
        defect = session.exec(select(Defect).where(Defect.id == defect_id)).first()
        if not defect:
            raise HTTPException(status_code=404, detail=f"There is no defect with id={defect_id}")
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
