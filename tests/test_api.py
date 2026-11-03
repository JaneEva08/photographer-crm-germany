import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.db import Base, get_db
from backend.main import app


@pytest.fixture()
def client():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    def override_db():
        with TestingSession() as session:
            yield session

    app.dependency_overrides[get_db] = override_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


def test_client_deal_task_crud_and_partial_update(client):
    response = client.post("/clients", json={"name": "Anna Müller", "language": "DE"})
    assert response.status_code == 201
    client_id = response.json()["id"]
    response = client.patch(f"/clients/{client_id}", json={"phone": "+49 111"})
    assert response.status_code == 200
    assert response.json()["name"] == "Anna Müller"
    deal = client.post("/deals", json={"client_id": client_id, "title": "Portrait", "amount_eur": "320.00"})
    assert deal.status_code == 201
    assert client.patch(f"/deals/{deal.json()['id']}", json={"status": "booked"}).json()["title"] == "Portrait"
    task = client.post("/tasks", json={"client_id": client_id, "deal_id": deal.json()["id"], "title": "Send contract"})
    assert task.status_code == 201
    assert client.patch(f"/tasks/{task.json()['id']}", json={"completed": True}).json()["completed"] is True


def test_rejects_invalid_foreign_keys_and_supports_search(client):
    assert client.post("/deals", json={"client_id": 999, "title": "Portrait"}).status_code == 404
    client.post("/clients", json={"name": "Lena Hoffmann"})
    assert client.get("/clients?q=Hoffmann").json()[0]["name"] == "Lena Hoffmann"
    assert client.get("/clients?limit=0").status_code == 422
    created = client.post("/clients", json={"name": "Null Guard"}).json()
    assert client.patch(f"/clients/{created['id']}", json={"name": None}).status_code == 422
