import os
os.environ["TESTING"] = "1"
from datetime import datetime
from base64 import b64encode

import pytest
from sqlmodel import SQLModel
from fastapi.testclient import TestClient

from application.main import application
from application.db_connection import engine, settings

# Before running the tests, you need to change the DATABASE_URL value in the .env file to the test one.


@pytest.fixture(scope="module")
def test_client():
    with TestClient(application) as client:
        yield client


@pytest.fixture(scope="module")
def auth_headers(test_client):
    login_response = test_client.post(url="/api/v1/auth/token",
                                      data={"username": settings.admin_username, "password": settings.admin_password})
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="module", autouse=True)
def setup_module(test_client, auth_headers):
    test_client.post(url="api/v1/maintenance/create_tables", params={"test_mode": True}, headers=auth_headers)
    test_client.post(url="api/v1/maintenance/fill_database", headers=auth_headers)
    yield
    SQLModel.metadata.drop_all(engine)


# Protection against changes to the production database
if settings.database_url.split("/")[-1] != "test_db":
    raise ValueError("USING NON-TEST DATABASE CONNECTION PARAMETERS. CHANGE THE \"DATABASE_URL\" PARAMETER "
                     "IN THE .env FILE")

with open("application/services/test_defect.jpg", "rb") as file:
    encoded_photo = b64encode(file.read()).decode()

defect_1_response_json = {
    "id": 1,
    "timestamp": datetime(2025, 1, 1).strftime("%Y-%m-%dT%H:%M:%S"),
    "type": "hole",
    "is_on_belt": True,
    "box_width_in_mm": 400,
    "box_length_in_mm": 400,
    "longitudinal_position": 4870000,
    "transverse_position": 216,
    "probability": 90,
    "criticality": "extreme",
    "base64_photo": encoded_photo
}

defect_2_response_json = {
    "id": 2,
    "timestamp": datetime(2025, 1, 2).strftime("%Y-%m-%dT%H:%M:%S"),
    "type": "rope",
    "is_on_belt": True,
    "box_width_in_mm": 500,
    "box_length_in_mm": 500,
    "longitudinal_position": 10516000,
    "transverse_position": 1530,
    "probability": 95,
    "criticality": "critical",
    "base64_photo": encoded_photo
}


def test_get_existing_defect_by_id(test_client, auth_headers):
    response = test_client.get(url="/api/v1/defect_info/id=2", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == defect_2_response_json


def test_get_non_existing_defect_by_id(test_client, auth_headers):
    response = test_client.get(url="/api/v1/defect_info/id=999", headers=auth_headers)
    assert response.status_code == 404


def test_get_defects_of_existing_type(test_client, auth_headers):
    response = test_client.get(url="/api/v1/defect_info/type=hole", headers=auth_headers)
    data = response.json()
    assert response.status_code == 200
    assert len(data) == 1
    assert data[0] == defect_1_response_json


def test_get_defects_of_non_existing_type(test_client, auth_headers):
    response = test_client.get(url="/api/v1/defect_info/type=wrong_type", headers=auth_headers)
    data = response.json()
    assert response.status_code == 200
    assert len(data) == 0


def test_get_critical_defects(test_client, auth_headers):
    response = test_client.get(url="/api/v1/defect_info/critical", headers=auth_headers)
    data = response.json()
    assert response.status_code == 200
    assert len(data) == 1
    assert data[0] == defect_2_response_json


def test_get_extreme_defects(test_client, auth_headers):
    response = test_client.get(url="/api/v1/defect_info/extreme", headers=auth_headers)
    data = response.json()
    assert response.status_code == 200
    assert len(data) == 1
    assert data[0] == defect_1_response_json
