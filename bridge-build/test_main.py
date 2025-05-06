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


<<<<<<< Updated upstream
# def test_dds_read_direct(client):
#     response = client.get("/DDS-read/TestTopic")
#     assert response.status_code == 200
#     data = response.get_json()
#     assert "dds_name" in data
#     assert "data" in data
=======
>>>>>>> Stashed changes
def test_dds_read_returns_data(client):
    response = client.get("/DDS-read/B")

    json_data = print(response.get_json())
<<<<<<< Updated upstream
    assert isinstance(json_data, dict)

def test_dds_write_dynamic_topic_success(client):
    response = client.post("/DDS-write/B", json={"index": 1, "message": "test"})
    assert response.status_code == 200
    assert response.get_json()["status"] == "success"

def test_dds_write_nonexistent_topic(client):
    # C pub/sub does not exist
    response = client.post("/DDS-write/C", json={"index": 1, "message": "this should fail"})
    assert response.status_code == 404
=======
    assert response.status_code==200
>>>>>>> Stashed changes
