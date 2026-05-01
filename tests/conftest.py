import os
os.environ["PIGENUS_SECRET_KEY"] = "test-secret-key-for-testing-only"
os.environ["PIGENUS_ADMIN_TOKEN"] = "test-admin-token"
os.environ["PIGENUS_DATABASE_URL"] = "sqlite://"
os.environ["PIGENUS_ENVIRONMENT"] = "testing"

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.pool import StaticPool

from pigenus.core.config import get_settings
get_settings.cache_clear()

from pigenus.main import app
from pigenus.security.dependencies import get_db
import pigenus.models  # ensure all models are registered


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(name="admin_user")
def admin_user_fixture(client: TestClient):
    response = client.post("/api/v1/auth/register", json={
        "username": "admin",
        "email": "admin@test.com",
        "password": "adminpassword123",
    })
    assert response.status_code == 201
    login_resp = client.post("/api/v1/auth/login", data={
        "username": "admin",
        "password": "adminpassword123",
    })
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    return {"user": response.json(), "token": token}


@pytest.fixture(name="test_worker")
def test_worker_fixture(client: TestClient, admin_user):
    response = client.post(
        "/api/v1/workers/register",
        json={
            "name": "test-worker",
            "hostname": "worker-host",
            "capabilities": ["cpu", "gpu"],
            "secret": "worker-secret-123",
        },
        headers={"Authorization": f"Bearer {admin_user['token']}"},
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture(name="test_job")
def test_job_fixture(client: TestClient, admin_user):
    response = client.post(
        "/api/v1/jobs",
        json={"title": "Test Job", "job_type": "shell_command", "priority": 5},
        headers={"Authorization": f"Bearer {admin_user['token']}"},
    )
    assert response.status_code == 201
    return response.json()
