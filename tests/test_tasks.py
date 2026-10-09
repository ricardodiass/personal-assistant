import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.core.database import Base, SessionLocal, engine
from app.main import app
from app.models import TaskModel


Base.metadata.create_all(bind=engine)

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_tasks():
    with SessionLocal() as db:
        db.execute(delete(TaskModel))
        db.commit()

    yield

    with SessionLocal() as db:
        db.execute(delete(TaskModel))
        db.commit()


def test_create_task():
    response = client.post(
        "/tasks/",
        json={"title": "Estudar Docker", "description": "Praticar containers"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Estudar Docker"
    assert data["description"] == "Praticar containers"
    assert data["completed"] is False
    assert "id" in data


def test_list_tasks():
    client.post("/tasks/", json={"title": "Estudar Python"})
    client.post("/tasks/", json={"title": "Estudar Docker"})

    response = client.get("/tasks/")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_complete_task():
    created = client.post(
        "/tasks/",
        json={"title": "Estudar PostgreSQL"},
    ).json()

    response = client.patch(f"/tasks/{created['id']}/complete")

    assert response.status_code == 200
    assert response.json()["completed"] is True


def test_complete_task_not_found():
    response = client.patch("/tasks/id-inexistente/complete")

    assert response.status_code == 404


def test_delete_task():
    created = client.post(
        "/tasks/",
        json={"title": "Tarefa temporária"},
    ).json()

    response = client.delete(f"/tasks/{created['id']}")

    assert response.status_code == 204
    assert client.get("/tasks/").json() == []


def test_delete_task_not_found():
    response = client.delete("/tasks/id-inexistente")

    assert response.status_code == 404


def test_create_task_without_title():
    response = client.post("/tasks/", json={"description": "Sem título"})

    assert response.status_code == 422


def test_create_task_with_empty_title():
    response = client.post("/tasks/", json={"title": ""})

    assert response.status_code == 422
