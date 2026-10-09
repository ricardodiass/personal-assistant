
from fastapi import APIRouter, Query
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