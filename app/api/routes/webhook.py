
from fastapi import APIRouter, Query, Request
from fastapi.responses import PlainTextResponse

from app.core.settings import settings

router = APIRouter(prefix="/webhook", tags=["WhatsApp"])


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
    try:
        payload = await request.json()
    except ValueError:
        return {"status": "invalid_json"}

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
