from datetime import datetime
from base64 import b64encode
import subprocess
import time

from sqlmodel import SQLModel
from fastapi.testclient import TestClient
import pytest

from application.main import application
from application.database_connection import engine, settings

# Before running the tests, you need to change the DATABASE_URL value in the .env file to the test one.
# !!! If there is <requests.exceptions.ConnectionError> - increase <time.sleep(...)> value !!!

client = TestClient(application)


@pytest.fixture(scope="module", autouse=True)
def setup_module():
    process = subprocess.Popen(["uvicorn", "application.main:application", "--host", "127.0.0.1", "--port", "8000"])
    time.sleep(3)

    try:
        client.post(url="/maintenance/create_tables", params={"test_mode": True})
        client.post(url="/maintenance/fill_database")
        yield
    finally:
        SQLModel.metadata.drop_all(engine)
        process.terminate()

# Protection against changes to the production database
if settings.DATABASE_URL.split("/")[-1] != "test_db":
    raise ValueError("USING NON-TEST DATABASE CONNECTION PARAMETERS. CHANGE THE \"DATABASE_URL\" PARAMETER "
                     "IN THE .env FILE")

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
    "criticality": "extreme",
    "base64_photo": b64encode(open("application/test_defect.jpg", "rb").read()).decode()
}

defect_2_response_json = {
    "id": 2,
    "timestamp": datetime(2025, 1, 2).strftime("%Y-%m-%dT%H:%M:%S"),
    "type": "rope",
    "is_on_belt": True,
    "box_width_in_mm": 500,
    "box_length_in_mm": 500,
    "longitudinal_position": 10,
    "transverse_position": 10,
    "probability": 95,
    "criticality": "critical",
    "base64_photo": b64encode(open("application/test_defect.jpg", "rb").read()).decode()
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
    data = response.json()
    assert response.status_code == 200
    assert len(data) == 0


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
