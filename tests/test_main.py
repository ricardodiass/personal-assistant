
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



def test_webhook_receive_text_message():
    payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "messages": [
                                {
                                    "from": "5511999999999",
                                    "id": "wamid.test123",
                                    "type": "text",
                                    "text": {"body": "Olá, assistente!"},
                                }
                            ]
                        }
                    }
                ]
            }
        ],
    }

    response = client.post("/webhook", json=payload)

    assert response.status_code == 200
    assert response.json() == {
        "status": "received",
        "messages_count": 1,
        "messages": [
            {
                "from": "5511999999999",
                "id": "wamid.test123",
                "type": "text",
                "text": "Olá, assistente!",
            }
        ],
    }



def test_webhook_without_messages():
    payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "statuses": [
                                {
                                    "id": "wamid.test123",
                                    "status": "delivered",
                                }
                            ]
                        }
                    }
                ]
            }
        ],
    }

    response = client.post("/webhook", json=payload)

    assert response.status_code == 200
    assert response.json() == {
        "status": "received",
        "messages_count": 0,
        "messages": [],
    }



def test_webhook_invalid_json():
    response = client.post(
        "/webhook",
        content="{json-invalido",
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 200
    assert response.json() == {"status": "invalid_json"}
