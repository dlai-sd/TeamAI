"""Pytest configuration and fixtures"""
import pytest
from typing import Generator
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client() -> Generator:
    """FastAPI test client"""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def mock_db():
    """Mock database session"""
    # TODO: Implement mock database
    pass


@pytest.fixture
def mock_redis():
    """Mock Redis client"""
    # TODO: Implement mock Redis
    pass
