from fastapi import FastAPI
from notification_service import router as notification_service_router
from defect_info_service import router as defect_info_service_router

application = FastAPI()
application.include_router(notification_service_router)
application.include_router(defect_info_service_router)


@application.get("/")
def get_application_info():
    return {"info": "Web-application for conveyor belt monitoring system"}
