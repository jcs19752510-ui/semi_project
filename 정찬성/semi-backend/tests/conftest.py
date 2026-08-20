import os

os.environ.setdefault("DATABASE_URL", "postgresql+psycopg://semi:change-me@localhost:5432/semi")

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)
