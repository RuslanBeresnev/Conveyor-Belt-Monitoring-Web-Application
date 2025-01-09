from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session
from datetime import datetime
from base64 import b64encode
import pytest
from application.main import application
from application.db_models import ObjectType, Object, DefectType, Photo, Defect
from application.database_connection import engine, settings

# Перед запуском тестов необходимо поменять значение DATABASE_URL в файле .env на тестовое


@pytest.fixture(scope="module", autouse=True)
def setup_module():
    yield
    # Очистка тестовой базы данных после серии тестов
    SQLModel.metadata.drop_all(engine)


def create_db_tables():
    SQLModel.metadata.create_all(engine)


def fill_db_with_data():
    with Session(engine) as session:
        object_type_for_defect = ObjectType(name="defect")
        object_type_for_conv_state = ObjectType(name="conv_state")
        object_type_for_history = ObjectType(name="history")
        object_type_for_photo = ObjectType(name="photo")
        session.add(object_type_for_defect)
        session.add(object_type_for_conv_state)
        session.add(object_type_for_history)
        session.add(object_type_for_photo)

        defect_type_chip = DefectType(name="chip", is_belt=False)
        defect_type_delamination = DefectType(name="delamination", is_belt=False)
        defect_type_rope = DefectType(name="rope")
        defect_type_crack = DefectType(name="crack")
        defect_type_liftup = DefectType(name="liftup")
        defect_type_hole = DefectType(name="hole")
        defect_type_tear = DefectType(name="tear")
        defect_type_wear = DefectType(name="wear")
        defect_type_joint = DefectType(name="joint")
        defect_type_joint_worn = DefectType(name="joint_worn")
        session.add(defect_type_chip)
        session.add(defect_type_delamination)
        session.add(defect_type_rope)
        session.add(defect_type_crack)
        session.add(defect_type_liftup)
        session.add(defect_type_hole)
        session.add(defect_type_tear)
        session.add(defect_type_wear)
        session.add(defect_type_joint)
        session.add(defect_type_joint_worn)

        object_of_defect_1 = Object(type_object=object_type_for_defect, time=datetime(2025, 1, 1))
        object_of_defect_2 = Object(type_object=object_type_for_defect, time=datetime(2025, 1, 2))
        object_of_photo_1 = Object(type_object=object_type_for_photo, time=datetime(2025, 1, 1))
        object_of_photo_2 = Object(type_object=object_type_for_photo, time=datetime(2025, 1, 2))
        session.add(object_of_defect_1)
        session.add(object_of_defect_2)
        session.add(object_of_photo_1)
        session.add(object_of_photo_2)

        photo_1 = Photo(base_object=object_of_photo_1, image="photo1".encode())
        photo_2 = Photo(base_object=object_of_photo_2, image="photo2".encode())
        session.add(photo_1)
        session.add(photo_2)

        extreme_defect = Defect(base_object=object_of_defect_1, type_object=defect_type_hole, box_width=400,
                                box_length=400, location_width_in_frame=10, location_length_in_frame=10,
                                location_width_in_conv=10, location_length_in_conv=10, photo_object=photo_1,
                                probability=90, is_critical=False, is_extreme=True)
        critical_defect = Defect(base_object=object_of_defect_2, type_object=defect_type_tear, box_width=500,
                                 box_length=500, location_width_in_frame=10, location_length_in_frame=10,
                                 location_width_in_conv=10, location_length_in_conv=10, photo_object=photo_2,
                                 probability=95, is_critical=True, is_extreme=False)
        session.add(extreme_defect)
        session.add(critical_defect)

        session.commit()

# Защита от изменения production базы данных
if settings.DATABASE_URL != "postgresql://test_user:test_password@localhost:5432/test_db":
    raise Exception("ИСПОЛЬЗУЮТСЯ НЕ ТЕСТОВЫЕ ПАРАМЕТРЫ ДЛЯ ПОДКЛЮЧЕНИЯ К БАЗЕ ДАННЫХ. "
                    "ИЗМЕНИТЕ ПАРАМЕТР \"DATABASE_URL\" В ФАЙЛЕ .env")

create_db_tables()
fill_db_with_data()
client = TestClient(application)

defect_1_response_json = {
    "id": 1,
    "timestamp": datetime(2025, 1, 1).strftime("%Y-%m-%dT%H:%M:%S"),
    "type": "hole",
    "is_on_belt": True,
    "box_width_in_mm": 400,
    "box_length_in_mm": 400,
    "longitudinal_position": 10,
    "transverse_position": 10,
    "probability": 90,
    "is_critical": False,
    "is_extreme": True,
    "base64_photo": b64encode("photo1".encode()).decode()
}

defect_2_response_json = {
    "id": 2,
    "timestamp": datetime(2025, 1, 2).strftime("%Y-%m-%dT%H:%M:%S"),
    "type": "tear",
    "is_on_belt": True,
    "box_width_in_mm": 500,
    "box_length_in_mm": 500,
    "longitudinal_position": 10,
    "transverse_position": 10,
    "probability": 95,
    "is_critical": True,
    "is_extreme": False,
    "base64_photo": b64encode("photo2".encode()).decode()
}


def test_get_existing_defect_by_id():
    response = client.get("/defect_info/id=2")
    assert response.status_code == 200
    assert response.json() == defect_2_response_json


def test_get_non_existing_defect_by_id():
    response = client.get("/defect_info/id=999")
    assert response.status_code == 404


def test_get_defects_of_existing_type():
    response = client.get("/defect_info/type=hole")
    data = response.json()
    assert response.status_code == 200
    assert len(data) == 1
    assert data[0] == defect_1_response_json


def test_get_defects_of_non_existing_type():
    response = client.get("/defect_info/type=wrong_type")
    assert response.status_code == 404


def test_get_critical_defects():
    response = client.get("/defect_info/critical")
    data = response.json()
    assert response.status_code == 200
    assert len(data) == 1
    assert data[0] == defect_2_response_json


def test_get_extreme_defects():
    response = client.get("/defect_info/extreme")
    data = response.json()
    assert response.status_code == 200
    assert len(data) == 1
    assert data[0] == defect_1_response_json
