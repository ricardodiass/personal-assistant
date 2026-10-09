
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)



def test_home():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Personal Assistant está funcionando!",
        "status": "online",
        "environment": "development",
    }


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}



def test_webhook_verification_success():
    response = client.get(
        "/webhook",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": "change_me",
            "hub.challenge": "12345",
        },
    )

    assert response.status_code == 200
    assert response.text == "12345"


def test_webhook_verification_invalid_token():
    response = client.get(
        "/webhook",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": "token_errado",
            "hub.challenge": "12345",
        },
    )

    assert response.status_code == 403
    assert response.text == "Verificação do webhook recusada"
