from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def health():
    return {
        "service": "QUALITY_AGENT_PORTAL_ENGINE",
        "version": "V1.0",
        "status": "UP"
    }
