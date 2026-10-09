from fastapi import FastAPI

from app.api.routes.health import router as health_router

app = FastAPI(
    title="Personal Assistant",
    description="Assistente pessoal integrado ao WhatsApp",
    version="0.1.0",
)


@app.get("/")
def home():
    return {
        "message": "Personal Assistant está funcionando!",
        "status": "online",
    }


app.include_router(health_router)
