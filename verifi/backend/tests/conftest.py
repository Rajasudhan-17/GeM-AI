import pytest
import asyncio
from fastapi.testclient import TestClient
from app.main import app
from app.repositories.seed import seed_database_and_documents


@pytest.fixture(autouse=True)
def initialize_test_database():
    """Seeds the in-memory database before each test run."""
    asyncio.run(seed_database_and_documents())


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client
