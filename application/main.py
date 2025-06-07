import os
from asyncio import create_task

from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlmodel import Session, select
from passlib.context import CryptContext

from application.models.db_models import User
from application.models.api_models import ServiceInfoResponseModel

from application.services.authentication_service import router as authentication_service_router
from application.services.notification_service import router as notification_service_router
from application.services.defect_info_service import router as defect_info_service_router
from application.services.conveyor_info_service import router as conveyor_info_service_router
from application.services.logging_service import router as logging_service_router
from application.services.report_service import router as report_service_router
from application.services.maintenance_service import router as maintenance_service_router

from .config import settings
from .db_connection import engine
from .db_listener import listen_for_new_defects

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_admin_if_not_exists():
    with Session(engine) as session:
        User.__table__.create(engine, checkfirst=True)

        admin_user = session.exec(select(User).where(User.username == settings.admin_username)).first()
        if admin_user: return

        hashed_password = pwd_context.hash(settings.admin_password)
        admin_user = User(
            username=settings.admin_username,
            password=hashed_password,
            role="Admin"
        )

        session.add(admin_user)
        session.commit()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    create_admin_if_not_exists()
    if os.getenv("TESTING") != "1":
        create_task(listen_for_new_defects())
    yield


api_router = APIRouter(prefix="/api/v1")

api_router.include_router(authentication_service_router)
api_router.include_router(notification_service_router)
api_router.include_router(defect_info_service_router)
api_router.include_router(conveyor_info_service_router)
api_router.include_router(logging_service_router)
api_router.include_router(report_service_router)
api_router.include_router(maintenance_service_router)

application = FastAPI(lifespan=lifespan)
application.include_router(api_router)

origins = [f"http://{settings.client_address}:{settings.client_port}"]
application.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"]
)


@application.get(path="/api/v1", response_model=ServiceInfoResponseModel)
def get_api_info():
    return ServiceInfoResponseModel(
        info="API for conveyor belt monitoring system including six services: notification service, defect info service"
             ", conveyor info service, logging service, report service and maintenance service"
    )
