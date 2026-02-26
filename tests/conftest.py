import os
import pytest
import shutil
from unittest.mock import patch
from pathlib import Path
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, delete
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
settings.running_tests = '1'  # TODO

from app.main import app
from app.core.database import Base, get_db
from app.models.files import FileMetadata



# --------------------------------------------------
# Choose database based on environment
# --------------------------------------------------

UPLOAD_DIR = Path(settings.storage_path if hasattr(settings, "storage_path") else "uploads")
# TODO
USE_DOCKER_DB = os.getenv("USE_DOCKER_DB", "0") == "1"
if USE_DOCKER_DB:
    TEST_DB_URL = settings.postgres_url
    engine = create_engine(TEST_DB_URL)
else:
    TEST_DB_URL = "sqlite:///./test.db"
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})

TestingSessionLocal = sessionmaker(bind=engine)

# --------------------------------------------------
# Create & drop tables
# --------------------------------------------------
@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

    # release sqlite lock on Windows
    engine.dispose()

    if not USE_DOCKER_DB and os.path.exists("test.db"):
        os.remove("test.db")

# --------------------------------------------------
# Override DB dependency
# --------------------------------------------------
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# --------------------------------------------------
# ⭐ Mock Celery so Redis is never called
# --------------------------------------------------
@pytest.fixture(autouse=True)
def mock_celery():
    """
    Prevent Celery from trying to connect to Redis
    during tests.
    """
    with patch("app.api.v1.routes.process_file.delay") as mock_delay:
        mock_delay.return_value = None
        yield mock_delay

# --------------------------------------------------
# Fixtures
# --------------------------------------------------
@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def cleanup_after_test(db_session):
    """
    Runs after every test:
    - clears FileMetadata table
    - removes uploaded files
    """
    yield  # run the test first

    # delete DB rows
    db_session.execute(delete(FileMetadata))
    db_session.commit()

    # delete files
    if UPLOAD_DIR.exists():
        shutil.rmtree(UPLOAD_DIR)
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

