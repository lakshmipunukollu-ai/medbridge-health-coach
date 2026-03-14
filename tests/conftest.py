"""Test configuration and fixtures."""

import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# Override DATABASE_URL before importing app modules
os.environ["DATABASE_URL"] = "sqlite:///./test_medbridge.db"

from app.main import app
from app.database import get_db
from app.models.base import Base


# Test database setup
TEST_DB_URL = "sqlite:///./test_medbridge.db"
test_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    """Create tables before each test, drop after."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def db_session():
    """Direct database session for test setup."""
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def sample_patient(client):
    """Create and return a sample patient with consent."""
    response = client.post("/patients", json={
        "name": "Jane Doe",
        "email": "jane@example.com",
        "consent_verified": True,
    })
    return response.json()


@pytest.fixture
def sample_patient_no_consent(client):
    """Create and return a sample patient without consent."""
    response = client.post("/patients", json={
        "name": "Bob Smith",
        "email": "bob@example.com",
        "consent_verified": False,
    })
    return response.json()


@pytest.fixture
def active_patient(client, sample_patient):
    """Create a patient in ACTIVE phase (with goal set)."""
    patient_id = sample_patient["id"]
    # Send initial message (onboarding)
    client.post(f"/patients/{patient_id}/sessions", json={
        "message": "Hello, I want to start my exercises"
    })
    # Set a goal to trigger transition to ACTIVE
    client.post(f"/patients/{patient_id}/sessions", json={
        "message": "My goal is to improve my shoulder mobility"
    })
    # Get updated patient
    response = client.get(f"/patients/{patient_id}")
    return response.json()
