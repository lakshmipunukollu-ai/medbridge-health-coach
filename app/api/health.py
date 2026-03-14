"""Health check endpoint."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health_check():
    """Health check endpoint - returns 200 if service is running."""
    return {
        "status": "healthy",
        "service": "medbridge-health-coach",
        "version": "1.0.0",
    }
