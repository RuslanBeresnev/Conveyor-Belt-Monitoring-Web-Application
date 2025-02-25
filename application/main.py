from fastapi import FastAPI

from .notification_service import router as notification_service_router
from .defect_info_service import router as defect_info_service_router
from .conveyor_info_service import router as conveyor_info_service_router
from .logging_service import router as logging_service_router
from .response_models import ServiceInfoResponseModel

application = FastAPI()
application.include_router(notification_service_router)
application.include_router(defect_info_service_router)
application.include_router(conveyor_info_service_router)
application.include_router(logging_service_router)


@application.get(path="/", response_model=ServiceInfoResponseModel)
def get_application_info():
    return ServiceInfoResponseModel(
        info="Web-application for conveyor belt monitoring system"
    )
