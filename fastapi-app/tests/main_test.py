import pytest
from fastapi.testclient import TestClient
from app.main import app


def test_addition():
    assert 2 + 2 == 4


@pytest.fixture
def sample_list():
    return [1, 2, 3, 4, 5]


def test_sample_list(sample_list):
    assert len(sample_list) == 5


# Test with multiple parameters
@pytest.mark.parametrize("input, expected", [(1, 1), (2, 4)])
def test_sqaure(input, expected):
    assert input**2 == expected


client = TestClient(app)


# test with api
def test_root_endpoint_api():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World", "database_status": "connected"}
