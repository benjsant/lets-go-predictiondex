#app/tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from extraction_pokemon.api.main import app
from extraction_pokemon.db.base import Base

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture
def db_session():
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    TestingSessionLocal = sessionmaker(bind=engine)

    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()

    yield session

    session.close()


@pytest.fixture
def client():
    return TestClient(app)
