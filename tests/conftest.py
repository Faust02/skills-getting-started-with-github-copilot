import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Provide a test client for the FastAPI application"""
    return TestClient(app)


@pytest.fixture
def fresh_activities():
    """Provide a fresh copy of activities for each test"""
    return {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": []
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": []
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": []
        }
    }


@pytest.fixture(autouse=True)
def reset_activities(fresh_activities):
    """Reset activities to fresh state before each test"""
    activities.clear()
    activities.update(fresh_activities)
    yield
    activities.clear()
