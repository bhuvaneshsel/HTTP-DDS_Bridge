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


def test_dds_read_returns_data(client):
    response = client.get("/DDS-read/B")
    response2 = client.get("/DDS-read/A")
    json_data = print(response.get_json())
    json_data2 = print(response2.get_json())
    assert response.status_code==200
    assert response2.status_code==200