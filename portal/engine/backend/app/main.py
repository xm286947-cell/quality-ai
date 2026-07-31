from fastapi import FastAPI
from api.health import router as health_router

app = FastAPI(
    title="QUALITY_AGENT_PORTAL_ENGINE",
    version="V1.0"
)

app.include_router(health_router)
