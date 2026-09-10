from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import ai_service
import config
import data_service
import risk_service
from database import Base, SessionLocal, engine, get_db
from models import EventOut, IndustrialSite, IndustrialSiteOut, RawEventIn, RiskOut, StatsOut, ThermalEvent

_pipeline_state = {"used_live_firms": False, "used_live_osm": False}


def run_pipeline(db: Session) -> None:
    """
    Full pipeline described in the architecture doc:
    FIRMS -> normalize -> OSM context -> features -> ML classify ->
    persistence -> risk -> persist to DB.
    """
    raw_events, used_live_firms = data_service.fetch_firms_data()
    sites, used_live_osm = data_service.fetch_industrial_sites()
    _pipeline_state["used_live_firms"] = used_live_firms
    _pipeline_state["used_live_osm"] = used_live_osm

    # Refresh industrial sites table
    db.query(IndustrialSite).delete()
    for s in sites:
        db.add(IndustrialSite(
            id=s["id"], name=s["name"], type=s["type"],
            latitude=s["latitude"], longitude=s["longitude"], source=s.get("source", "demo"),
        ))
    db.commit()

    db.query(ThermalEvent).delete()
    db.commit()

    processed = 0
    for event in raw_events:
        try:
            site, dist = data_service.nearest_industrial_site(event["latitude"], event["longitude"], sites)
            nearby_count = data_service.count_nearby_sites(
                event["latitude"], event["longitude"], sites, config.INDUSTRIAL_PROXIMITY_KM
            )
            persistence = risk_service.detect_persistence(event, raw_events)
            classification = ai_service.classify(event, dist, nearby_count, persistence["persistence_count"])
            risk = risk_service.calculate_risk(event, classification, persistence, dist)

            db.add(ThermalEvent(
                id=event["id"],
                latitude=event["latitude"],
                longitude=event["longitude"],
                brightness=event.get("brightness"),
                frp=event.get("frp"),
                confidence=event.get("confidence"),
                acquisition_time=event["acquisition_time"],
                source=event.get("source", "unknown"),
                classification=classification["label"],
                classification_confidence=classification["confidence"],
                risk_score=risk["risk_score"],
                risk_level=risk["risk_level"],
                risk_reasons="|".join(risk["reasons"]),
                persistence_count=persistence["persistence_count"],
                persistent=persistence["persistent"],
                first_seen=persistence["first_seen"],
                last_seen=persistence["last_seen"],
                industrial_site_id=site["id"] if site else None,
                industrial_site_name=site["name"] if site else None,
                distance_to_industry_km=dist,
                created_at=datetime.utcnow(),
            ))
            processed += 1
        except Exception as exc:  # noqa: BLE001 - one bad record must not kill the pipeline
            print(f"[pipeline] Skipping event {event.get('id')} due to error: {exc}")
            continue

    db.commit()
    print(f"[pipeline] Processed {processed}/{len(raw_events)} events "
          f"(live FIRMS={used_live_firms}, live OSM={used_live_osm})")


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    ai_service.load_model()
    db = SessionLocal()
    try:
        if db.query(ThermalEvent).count() == 0:
            run_pipeline(db)
    finally:
        db.close()
    yield


app = FastAPI(title="THERMAGUARD AI", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "live_firms": _pipeline_state["used_live_firms"],
        "live_osm": _pipeline_state["used_live_osm"],
    }


@app.get("/api/events", response_model=list[EventOut])
def get_events(
    classification: str | None = Query(None),
    risk_level: str | None = Query(None),
    persistent: bool | None = Query(None),
    industrial_only: bool | None = Query(None),
    db: Session = Depends(get_db),
):
    q = db.query(ThermalEvent)
    if classification:
        q = q.filter(ThermalEvent.classification == classification)
    if risk_level:
        q = q.filter(ThermalEvent.risk_level == risk_level)
    if persistent is not None:
        q = q.filter(ThermalEvent.persistent == persistent)
    if industrial_only:
        q = q.filter(ThermalEvent.industrial_site_id.isnot(None))
    events = q.order_by(ThermalEvent.risk_score.desc()).all()
    return [EventOut.from_orm_event(e) for e in events]


@app.get("/api/events/stats", response_model=StatsOut)
def get_stats(db: Session = Depends(get_db)):
    events = db.query(ThermalEvent).all()
    if not events:
        return StatsOut(
            total_events=0, industrial_fires=0, natural_fires=0, agricultural_fires=0,
            gas_flares=0, other_unknown=0, persistent_sources=0, high_risk_events=0,
            critical_events=0,
        )

    def count_class(name):
        return sum(1 for e in events if e.classification == name)

    return StatsOut(
        total_events=len(events),
        industrial_fires=count_class("Industrial Fire"),
        natural_fires=count_class("Natural / Forest Fire"),
        agricultural_fires=count_class("Agricultural Fire"),
        gas_flares=count_class("Gas Flare / Persistent Thermal Source"),
        other_unknown=count_class("Other / Unknown"),
        persistent_sources=sum(1 for e in events if e.persistent),
        high_risk_events=sum(1 for e in events if e.risk_level == "High"),
        critical_events=sum(1 for e in events if e.risk_level == "Critical"),
    )


@app.get("/api/events/alerts", response_model=list[EventOut])
def get_alerts(db: Session = Depends(get_db)):
    events = (
        db.query(ThermalEvent)
        .filter(ThermalEvent.risk_level.in_(["High", "Critical"]))
        .order_by(ThermalEvent.risk_score.desc())
        .all()
    )
    return [EventOut.from_orm_event(e) for e in events]


@app.get("/api/events/{event_id}", response_model=EventOut)
def get_event(event_id: str, db: Session = Depends(get_db)):
    event = db.query(ThermalEvent).filter(ThermalEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail=f"Event {event_id} not found")
    return EventOut.from_orm_event(event)


@app.get("/api/events/{event_id}/risk", response_model=RiskOut)
def get_event_risk(event_id: str, db: Session = Depends(get_db)):
    event = db.query(ThermalEvent).filter(ThermalEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail=f"Event {event_id} not found")
    return RiskOut(
        event_id=event.id,
        risk_score=event.risk_score or 0,
        risk_level=event.risk_level or "Low",
        reasons=(event.risk_reasons or "").split("|") if event.risk_reasons else [],
    )


@app.get("/api/industrial-sites", response_model=list[IndustrialSiteOut])
def get_industrial_sites(db: Session = Depends(get_db)):
    return db.query(IndustrialSite).all()


@app.post("/api/events/analyze", response_model=EventOut)
def analyze_event(payload: RawEventIn, db: Session = Depends(get_db)):
    """Runs the full pipeline on a single ad-hoc event, without persisting the
    raw source - useful for judges to test a coordinate live during the demo."""
    raw = payload.model_dump()
    raw["acquisition_time"] = (raw.get("acquisition_time") or datetime.utcnow()).strftime("%Y-%m-%dT%H:%M:%SZ") \
        if isinstance(raw.get("acquisition_time"), datetime) else raw.get("acquisition_time")

    event = data_service.normalize_event(raw, fallback_id=f"MANUAL-{int(datetime.utcnow().timestamp())}")
    if event is None:
        raise HTTPException(status_code=400, detail="Invalid coordinates supplied")

    sites = [
        {"id": s.id, "name": s.name, "type": s.type, "latitude": s.latitude, "longitude": s.longitude}
        for s in db.query(IndustrialSite).all()
    ]
    existing_events = [
        {"latitude": e.latitude, "longitude": e.longitude, "acquisition_time": e.acquisition_time}
        for e in db.query(ThermalEvent).all()
    ]

    site, dist = data_service.nearest_industrial_site(event["latitude"], event["longitude"], sites)
    nearby_count = data_service.count_nearby_sites(
        event["latitude"], event["longitude"], sites, config.INDUSTRIAL_PROXIMITY_KM
    )
    persistence = risk_service.detect_persistence(event, existing_events + [event])
    classification = ai_service.classify(event, dist, nearby_count, persistence["persistence_count"])
    risk = risk_service.calculate_risk(event, classification, persistence, dist)

    new_event = ThermalEvent(
        id=event["id"],
        latitude=event["latitude"],
        longitude=event["longitude"],
        brightness=event.get("brightness"),
        frp=event.get("frp"),
        confidence=event.get("confidence"),
        acquisition_time=event["acquisition_time"],
        source=event.get("source", "manual"),
        classification=classification["label"],
        classification_confidence=classification["confidence"],
        risk_score=risk["risk_score"],
        risk_level=risk["risk_level"],
        risk_reasons="|".join(risk["reasons"]),
        persistence_count=persistence["persistence_count"],
        persistent=persistence["persistent"],
        first_seen=persistence["first_seen"],
        last_seen=persistence["last_seen"],
        industrial_site_id=site["id"] if site else None,
        industrial_site_name=site["name"] if site else None,
        distance_to_industry_km=dist,
        created_at=datetime.utcnow(),
    )
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    return EventOut.from_orm_event(new_event)


@app.post("/api/data/refresh")
def refresh_data(db: Session = Depends(get_db)):
    """Re-runs the full ingestion + classification + risk pipeline."""
    run_pipeline(db)
    return {"status": "refreshed", **_pipeline_state}
