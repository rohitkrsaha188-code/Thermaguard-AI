from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String

from database import Base



# ORM models
class IndustrialSite(Base):
    __tablename__ = "industrial_sites"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    source = Column(String, default="csv")


class ThermalEvent(Base):
    __tablename__ = "thermal_events"

    id = Column(String, primary_key=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    brightness = Column(Float, nullable=True)
    frp = Column(Float, nullable=True)
    confidence = Column(Float, nullable=True)
    acquisition_time = Column(DateTime, nullable=False)
    source = Column(String, default="unknown")

    classification = Column(String, nullable=True)
    classification_confidence = Column(Float, nullable=True)

    risk_score = Column(Integer, nullable=True)
    risk_level = Column(String, nullable=True)
    risk_reasons = Column(String, nullable=True)  # stored as "|"-joined string

    persistence_count = Column(Integer, default=1)
    persistent = Column(Boolean, default=False)
    first_seen = Column(DateTime, nullable=True)
    last_seen = Column(DateTime, nullable=True)

    industrial_site_id = Column(String, ForeignKey("industrial_sites.id"), nullable=True)
    industrial_site_name = Column(String, nullable=True)
    distance_to_industry_km = Column(Float, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

# Pydantic schemas (API layer)
class IndustrialSiteOut(BaseModel):
    id: str
    name: str
    type: str
    latitude: float
    longitude: float
    source: str

    class Config:
        from_attributes = True


class EventOut(BaseModel):
    id: str
    latitude: float
    longitude: float
    brightness: Optional[float] = None
    frp: Optional[float] = None
    confidence: Optional[float] = None
    acquisition_time: datetime
    source: str
    classification: Optional[str] = None
    classification_confidence: Optional[float] = None
    risk_score: Optional[int] = None
    risk_level: Optional[str] = None
    risk_reasons: list[str] = Field(default_factory=list)
    persistence_count: int = 1
    persistent: bool = False
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    industrial_site_id: Optional[str] = None
    industrial_site_name: Optional[str] = None
    distance_to_industry_km: Optional[float] = None

    class Config:
        from_attributes = True

    @staticmethod
    def from_orm_event(event: ThermalEvent) -> "EventOut":
        data = {c.name: getattr(event, c.name) for c in event.__table__.columns}
        data["risk_reasons"] = (event.risk_reasons or "").split("|") if event.risk_reasons else []
        return EventOut(**data)


class StatsOut(BaseModel):
    total_events: int
    industrial_fires: int
    natural_fires: int
    agricultural_fires: int
    gas_flares: int
    other_unknown: int
    persistent_sources: int
    high_risk_events: int
    critical_events: int


class RiskOut(BaseModel):
    event_id: str
    risk_score: int
    risk_level: str
    reasons: list[str]


class RawEventIn(BaseModel):
    """Payload for POST /api/events/analyze - a single raw thermal detection."""
    latitude: float
    longitude: float
    brightness: Optional[float] = None
    frp: Optional[float] = None
    confidence: Optional[float] = None
    acquisition_time: Optional[datetime] = None
    source: Optional[str] = "manual"
