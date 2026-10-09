import hashlib
import hmac
import json

from fastapi.testclient import TestClient

from app.main import app
from app.core.settings import settings

client = TestClient(app)

TEST_APP_SECRET = "segredo-de-teste"


def sign_payload(payload: dict) -> tuple[str, str]:
    body = json.dumps(payload).encode("utf-8")
    signature = hmac.new(
        TEST_APP_SECRET.encode("utf-8"),
        body,
        hashlib.sha256,
    ).hexdigest()

    return body.decode("utf-8"), f"sha256={signature}"


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


def test_webhook_receive_text_message(monkeypatch):
    monkeypatch.setattr(
        settings, "whatsapp_app_secret", TEST_APP_SECRET
    )

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

    body, signature = sign_payload(payload)

    response = client.post(
        "/webhook",
        content=body,
        headers={
            "Content-Type": "application/json",
            "X-Hub-Signature-256": signature,
        },
    )

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


def test_webhook_without_messages(monkeypatch):
    monkeypatch.setattr(
        settings, "whatsapp_app_secret", TEST_APP_SECRET
    )

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

    body, signature = sign_payload(payload)

    response = client.post(
        "/webhook",
        content=body,
        headers={
            "Content-Type": "application/json",
            "X-Hub-Signature-256": signature,
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "status": "received",
        "messages_count": 0,
        "messages": [],
    }


def test_webhook_invalid_json(monkeypatch):
    monkeypatch.setattr(
        settings, "whatsapp_app_secret", TEST_APP_SECRET
    )

    body = "{json-invalido"
    signature = "sha256=" + hmac.new(
        TEST_APP_SECRET.encode("utf-8"),
        body.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    response = client.post(
        "/webhook",
        content=body,
        headers={
            "Content-Type": "application/json",
            "X-Hub-Signature-256": signature,
        },
    )

    assert response.status_code == 400
    assert response.text == "JSON inválido"


def test_webhook_invalid_signature(monkeypatch):
    monkeypatch.setattr(
        settings, "whatsapp_app_secret", TEST_APP_SECRET
    )

    payload = {"object": "whatsapp_business_account"}

    response = client.post(
        "/webhook",
        json=payload,
        headers={"X-Hub-Signature-256": "sha256=assinatura-errada"},
    )

    assert response.status_code == 401
    assert response.text == "Assinatura inválida"


def test_webhook_missing_signature(monkeypatch):
    monkeypatch.setattr(
        settings, "whatsapp_app_secret", TEST_APP_SECRET
    )

    response = client.post(
        "/webhook",
        json={"object": "whatsapp_business_account"},
    )

    assert response.status_code == 401
    assert response.text == "Assinatura inválida"
