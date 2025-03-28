from fastapi import FastAPI

from .db_listener import lifespan
from .notification_service import router as notification_service_router
from .defect_info_service import router as defect_info_service_router, settings
from .conveyor_info_service import router as conveyor_info_service_router
from .logging_service import router as logging_service_router
from .report_service import router as report_service_router
from .api_models import ServiceInfoResponseModel


application = FastAPI(lifespan=lifespan)
application.include_router(notification_service_router)
application.include_router(defect_info_service_router)
application.include_router(conveyor_info_service_router)
application.include_router(logging_service_router)
application.include_router(report_service_router)


@application.get(path="/", response_model=ServiceInfoResponseModel)
def get_application_info():
    return ServiceInfoResponseModel(
        info="Web-application for conveyor belt monitoring system"
    )
