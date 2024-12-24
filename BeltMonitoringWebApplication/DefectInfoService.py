from fastapi import APIRouter

router = APIRouter(prefix="/defect_info", tags=["Defects Information Service"])


@router.get("/")
def get_service_info():
    return {"info": "Service providing information about emerging defects, their types and other useful parameters"}
