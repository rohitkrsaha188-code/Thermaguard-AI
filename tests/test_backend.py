import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

import ai_service  # noqa: E402
import data_service  # noqa: E402
import risk_service  # noqa: E402



# data_service

def test_normalize_event_valid_row():
    raw = {
        "id": "TEST-1", "latitude": "22.35", "longitude": "69.82",
        "brightness": "340.5", "frp": "200.1", "confidence": "88",
        "acquisition_time": "2026-09-01T10:00:00Z", "source": "VIIRS",
    }
    event = data_service.normalize_event(raw, fallback_id="fallback")
    assert event is not None
    assert event["id"] == "TEST-1"
    assert event["latitude"] == 22.35
    assert event["frp"] == 200.1
    assert isinstance(event["acquisition_time"], datetime)


def test_normalize_event_rejects_invalid_coordinates():
    raw = {"latitude": "999", "longitude": "69.82"}
    assert data_service.normalize_event(raw, fallback_id="x") is None


def test_normalize_event_handles_missing_optional_fields():
    raw = {"latitude": "10.0", "longitude": "20.0"}
    event = data_service.normalize_event(raw, fallback_id="x")
    assert event is not None
    assert event["brightness"] is None
    assert event["frp"] is None


def test_haversine_zero_distance():
    assert data_service.haversine_km(10.0, 20.0, 10.0, 20.0) == 0.0


def test_haversine_known_distance():
    # Roughly 1 degree of latitude ~ 111km
    d = data_service.haversine_km(0.0, 0.0, 1.0, 0.0)
    assert 108 < d < 113


def test_nearest_industrial_site_picks_closest():
    sites = [
        {"id": "A", "name": "Far", "latitude": 0.0, "longitude": 0.0},
        {"id": "B", "name": "Near", "latitude": 10.01, "longitude": 20.01},
    ]
    site, dist = data_service.nearest_industrial_site(10.0, 20.0, sites)
    assert site["id"] == "B"
    assert dist < 5


def test_nearest_industrial_site_empty_list():
    site, dist = data_service.nearest_industrial_site(10.0, 20.0, [])
    assert site is None
    assert dist is None


# risk_service - persistence detection

def _event(lat, lon, when):
    return {"latitude": lat, "longitude": lon, "acquisition_time": when}


def test_persistence_detects_repeated_nearby_events():
    base = datetime(2026, 9, 1)
    target = _event(22.35, 69.82, base)
    all_events = [
        target,
        _event(22.351, 69.821, base + timedelta(days=1)),
        _event(22.349, 69.819, base + timedelta(days=2)),
        _event(22.352, 69.822, base + timedelta(days=3)),
    ]
    result = risk_service.detect_persistence(target, all_events)
    assert result["persistence_count"] == 4
    assert result["persistent"] is True
    assert result["first_seen"] == base
    assert result["last_seen"] == base + timedelta(days=3)


def test_persistence_ignores_distant_events():
    base = datetime(2026, 9, 1)
    target = _event(22.35, 69.82, base)
    all_events = [target, _event(30.0, 80.0, base + timedelta(days=1))]
    result = risk_service.detect_persistence(target, all_events)
    assert result["persistence_count"] == 1
    assert result["persistent"] is False


def test_persistence_below_threshold_not_flagged():
    base = datetime(2026, 9, 1)
    target = _event(22.35, 69.82, base)
    all_events = [target, _event(22.351, 69.821, base + timedelta(days=1))]
    result = risk_service.detect_persistence(target, all_events)
    assert result["persistence_count"] == 2
    assert result["persistent"] is False  # below PERSISTENCE_MIN_COUNT (3)



# risk_service - risk scoring

def test_risk_score_is_bounded_0_to_100():
    event = {"frp": 5000, "brightness": 500, "confidence": 100}
    classification = {"label": "Industrial Fire"}
    persistence = {"persistence_count": 50, "persistent": True}
    result = risk_service.calculate_risk(event, classification, persistence, distance_km=0.1)
    assert 0 <= result["risk_score"] <= 100
    assert result["risk_level"] == "Critical"


def test_risk_score_low_for_weak_isolated_detection():
    event = {"frp": 2, "brightness": 290, "confidence": 20}
    classification = {"label": "Other / Unknown"}
    persistence = {"persistence_count": 1, "persistent": False}
    result = risk_service.calculate_risk(event, classification, persistence, distance_km=None)
    assert result["risk_score"] < 35
    assert result["risk_level"] == "Low"
    assert len(result["reasons"]) >= 1


def test_risk_reasons_mention_industrial_proximity_when_close():
    event = {"frp": 300, "brightness": 350, "confidence": 90}
    classification = {"label": "Industrial Fire"}
    persistence = {"persistence_count": 1, "persistent": False}
    result = risk_service.calculate_risk(event, classification, persistence, distance_km=0.5)
    assert any("industrial" in r.lower() for r in result["reasons"])


# ai_service - classification output shape

def test_classify_returns_expected_shape():
    event = {"brightness": 360, "frp": 300, "confidence": 85}
    result = ai_service.classify(event, distance_km=0.8, nearby_count=2, persistence_count=2)
    assert "label" in result
    assert "confidence" in result
    assert "probabilities" in result
    assert result["label"] in ai_service.CLASSES
    assert 0.0 <= result["confidence"] <= 1.0
    assert abs(sum(result["probabilities"].values()) - 1.0) < 0.05


def test_classify_falls_back_gracefully_without_model():
    """Even if the model somehow failed to load, the heuristic path must
    still return a well-formed, in-range result."""
    features = ai_service.build_features(
        {"brightness": 340, "frp": 200, "confidence": 80}, distance_km=1.0, nearby_count=1, persistence_count=1
    )
    label, confidence, probs = ai_service._heuristic_classify(features)
    assert label in ai_service.CLASSES
    assert 0.0 <= confidence <= 1.0
    assert abs(sum(probs.values()) - 1.0) < 0.05


# data_service - demo CSV loads without error

def test_demo_fires_csv_loads_and_has_events():
    events = data_service._load_fires_csv()
    assert len(events) > 0
    for e in events[:5]:
        assert -90 <= e["latitude"] <= 90
        assert -180 <= e["longitude"] <= 180


def test_demo_industrial_csv_loads_and_has_sites():
    sites = data_service._load_industrial_csv()
    assert len(sites) > 0
    assert all("name" in s for s in sites)
