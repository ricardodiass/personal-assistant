
from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.core.settings import settings
from app.api.routes.webhook import router as webhook_router

app = FastAPI(
    title=settings.app_name,
    description="Assistente pessoal integrado ao WhatsApp",
    version="0.1.0",
    debug=settings.app_debug,
)


@app.get("/")
def home():
    return {
        "message": f"{settings.app_name} está funcionando!",
        "status": "online",
        "environment": settings.app_env,
    }


app.include_router(health_router)
app.include_router(webhook_router)
