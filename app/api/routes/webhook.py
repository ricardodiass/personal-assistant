import hashlib
import hmac

from fastapi import APIRouter, Query, Request
from fastapi.responses import PlainTextResponse

from app.core.settings import settings

router = APIRouter(prefix="/webhook", tags=["WhatsApp"])



def is_valid_signature(payload: bytes, signature: str | None) -> bool:
    app_secret = settings.whatsapp_app_secret

    if not app_secret or not signature:
        return False

    expected_signature = "sha256=" + hmac.new(
        app_secret.encode("utf-8"),
        payload,
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(expected_signature, signature)


@router.get("", response_class=PlainTextResponse)
def verify_webhook(
    mode: str | None = Query(default=None, alias="hub.mode"),
    verify_token: str | None = Query(default=None, alias="hub.verify_token"),
    challenge: str | None = Query(default=None, alias="hub.challenge"),
):
    if (
        mode == "subscribe"
        and verify_token == settings.whatsapp_verify_token
        and challenge is not None
    ):
        return challenge

    return PlainTextResponse(
        content="Verificação do webhook recusada",
        status_code=403,
    )



@router.post("")
async def receive_webhook(request: Request):
    signature = request.headers.get("X-Hub-Signature-256")
    raw_payload = await request.body()

    if not is_valid_signature(raw_payload, signature):
        return PlainTextResponse(
            content="Assinatura inválida",
            status_code=401,
        )

    try:
        payload = await request.json()
    except ValueError:
        return PlainTextResponse(
            content="JSON inválido",
            status_code=400,
        )

    messages = []

    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})

            for message in value.get("messages", []):
                messages.append(
                    {
                        "from": message.get("from"),
                        "id": message.get("id"),
                        "type": message.get("type"),
                        "text": message.get("text", {}).get("body"),
                    }
                )

    return {
        "status": "received",
        "messages_count": len(messages),
        "messages": messages,
    }
