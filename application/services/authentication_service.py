from datetime import datetime, timedelta,  timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlmodel import Session, select
from jose import jwt, JWTError
from passlib.context import CryptContext

from application.config import settings
from application.db_connection import engine
from application.models.db_models import User
from application.models.api_models import ServiceInfoResponseModel, TokenResponseModel

ALGORITHM = "HS256"

router = APIRouter(prefix="/auth", tags=["Authentication Service"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expiration_delta: timedelta = None):
    to_encode = data.copy()
    expiration_timestamp = datetime.now(timezone.utc) + (expiration_delta or timedelta(minutes=15))
    to_encode.update({"exp": expiration_timestamp})
    return jwt.encode(to_encode, settings.jwt_sign_secret_key, algorithm=ALGORITHM)


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.jwt_sign_secret_key, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError as e:
        raise credentials_exception from e

    with Session(engine) as session:
        user = session.exec(select(User).where(User.username == username)).first()
        if user is None:
            raise credentials_exception
        return user


def get_current_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.role != "Admin":
        raise HTTPException(status_code=403, detail="Forbidden: you do not have sufficient rights "
                                                    "to access this resource")
    return current_user


@router.get(path="/", response_model=ServiceInfoResponseModel)
def get_service_info():
    return ServiceInfoResponseModel(
        info="Service handling authentication of users"
    )


@router.post("/token", response_model=TokenResponseModel)
def login_in_system_and_get_token(form_data: OAuth2PasswordRequestForm = Depends()):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.username == form_data.username)).first()
        if not user or not verify_password(form_data.password, user.password):
            raise HTTPException(status_code=401, detail="Incorrect username or password")

        token = create_access_token(data={"sub": form_data.username, "role": user.role},
                                    expiration_delta=timedelta(minutes=settings.auth_token_expiration_minutes))
        return {"access_token": token, "token_type": "bearer"}
