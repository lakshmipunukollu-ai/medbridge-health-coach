import uuid
from datetime import datetime

from sqlalchemy import Column, String, Boolean, Integer, DateTime, Text
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import relationship

from app.models.base import Base


class Patient(Base):
    __tablename__ = "patients"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    external_id = Column(String(255), nullable=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    phase = Column(String(20), nullable=False, default="PENDING")
    goal = Column(Text, nullable=True)
    consent_verified = Column(Boolean, nullable=False, default=False)
    unanswered_count = Column(Integer, nullable=False, default=0)
    last_interaction = Column(DateTime, nullable=True)
    program_summary = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    sessions = relationship("Session", back_populates="patient", lazy="dynamic")
    phase_logs = relationship(
        "PhaseTransitionLog", back_populates="patient", lazy="dynamic"
    )
    alerts = relationship("ClinicianAlert", back_populates="patient", lazy="dynamic")
