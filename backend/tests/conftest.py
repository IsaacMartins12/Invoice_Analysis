"""Test configuration with in-memory SQLite database."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app

# In-memory SQLite for tests
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    """Create tables before each test, drop after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    """HTTP test client."""
    return TestClient(app)


@pytest.fixture
def auth_headers(client):
    """Register a user and return auth headers."""
    client.post("/api/auth/register", json={
        "name": "Test User",
        "email": "test@example.com",
        "password": "password123",
    })
    response = client.post("/api/auth/login", data={
        "username": "test@example.com",
        "password": "password123",
    }, headers={"Content-Type": "application/x-www-form-urlencoded"})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
