from fastapi import FastAPI, APIRouter

from .db_listener import lifespan
from .notification_service import router as notification_service_router
from .defect_info_service import router as defect_info_service_router
from .conveyor_info_service import router as conveyor_info_service_router
from .logging_service import router as logging_service_router
from .report_service import router as report_service_router
from .maintenance_service import router as maintenance_service_router
from .api_models import ServiceInfoResponseModel

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(notification_service_router)
api_router.include_router(defect_info_service_router)
api_router.include_router(conveyor_info_service_router)
api_router.include_router(logging_service_router)
api_router.include_router(report_service_router)
api_router.include_router(maintenance_service_router)

application = FastAPI(lifespan=lifespan)
application.include_router(api_router)


@application.get(path="/api/v1", response_model=ServiceInfoResponseModel)
def get_api_info():
    return ServiceInfoResponseModel(
        info="API for conveyor belt monitoring system including six services: notification service, defect info service"
             ", conveyor info service, logging service, report service and maintenance service"
    )
