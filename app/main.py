"""
Medbridge AI Health Coach - FastAPI Application

A webhook-driven backend service that keeps patients engaged with their
Home Exercise Programs (HEPs) between clinical visits using a LangGraph
state machine agent.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine
from app.models.base import Base
from app.api.health import router as health_router
from app.api.patients import router as patients_router
from app.api.webhooks import router as webhooks_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - create tables on startup."""
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Medbridge AI Health Coach",
    description=(
        "AI health coaching agent that keeps patients engaged with their "
        "home exercise programs between clinical visits."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3007"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(health_router, tags=["Health"])
app.include_router(patients_router, tags=["Patients"])
app.include_router(webhooks_router, tags=["Webhooks"])
