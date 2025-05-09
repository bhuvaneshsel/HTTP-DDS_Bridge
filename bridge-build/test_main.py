import pytest
from unittest.mock import patch
from main import app


@pytest.fixture
def client():
    app.testing = True
    return app.test_client()


# def test_dds_write_success(client):
#     payload = {"index": 42, "message": "test message"}
#     response = client.post("/DDS-write", json=payload)
#     assert response.status_code in (200, 503)
#     assert "status" in response.get_json()
    
# def test_dds_write_missing_message(client):
#     payload = {"index": 42}  # missing 'message'
#     response = client.post("/DDS-write", json=payload)
#     assert response.status_code == 400
#     assert "error" in response.get_json()


def test_dds_read_B_success(client):
    response = client.get("/DDS-read/B")
    assert response.status_code==200

def test_dds_read_A_success(client):
    response = client.get("/DDS-read/A")
    assert response.status_code==200

def test_dds_read_nonexistent_fail(client):
    nonexistent_type = "Nonexistent"
    response = client.get(f"/DDS-read/{nonexistent_type}")
    assert response.status_code==404
    assert response.get_json()["error"]==f"Publisher class for '{nonexistent_type}' not found"

def test_dds_read_no_param_fail(client):
    response = client.get("/DDS-read")
    assert response.status_code==400
    assert response.get_json()["error"]=="Missing DDS topic. Use /DDS-read/<dds_topic>"

def test_dds_write_A_success(client):
    message = {
        "x": 38.2,
        "y": True
    }
    response = client.post(
        "/DDS-write/A",
        json=message
    )
    assert response.status_code==200
    assert response.get_json()["status"]=="success"

def test_dds_write_B_success(client):
    message = {
        "aVal": {"x": 38.2, "y": True},
        "b": [1, 2, 3],
        "c": ["hello", "goodbye"]
    }
    response = client.post(
        "/DDS-write/B",
        json=message
    )
    assert response.status_code==200
    assert response.get_json()["status"]=="success"

def test_dds_write_incorrect_format_fail(client):
    message_text = "this is a test"
    response = client.post(
        "/DDS-write/A",
        json={}
    )
    assert response.status_code==400

def test_dds_write_no_param_fail(client):
    response = client.post("/DDS-write")
    assert response.status_code==400
    assert response.get_json()["error"]=="Missing topic name. Use /DDS-write/<topic_name>"
