from fastapi import APIRouter
from database_connection import engine
from models import ObjectType, Object, DefectType, Photo, Defect

router = APIRouter(prefix="/defect_info", tags=["Defects Information Service"])


@router.get("/")
def get_service_info():
    return {"info": "Service providing information about emerging defects, their types and other useful parameters"}
