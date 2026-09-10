from datetime import datetime

import config
from data_service import haversine_km

def detect_persistence(event: dict, all_events: list[dict]) -> dict:

    lat, lon = event["latitude"], event["longitude"]
    nearby_times = []

    for other in all_events:
        d = haversine_km(lat, lon, other["latitude"], other["longitude"])
        if d <= config.PERSISTENCE_RADIUS_KM:
            nearby_times.append(other["acquisition_time"])

    if not nearby_times:
        nearby_times = [event["acquisition_time"]]

    count = len(nearby_times)
    first_seen = min(nearby_times)
    last_seen = max(nearby_times)
    is_persistent = count >= config.PERSISTENCE_MIN_COUNT

    return {
        "persistence_count": count,
        "persistent": is_persistent,
        "first_seen": first_seen,
        "last_seen": last_seen,
    }


def _risk_level(score: int) -> str:
    for level, threshold in sorted(config.RISK_LEVEL_THRESHOLDS.items(), key=lambda kv: -kv[1]):
        if score >= threshold:
            return level
    return "Low"


def calculate_risk(event: dict, classification: dict, persistence: dict,
                    distance_km: float | None) -> dict:
    
    reasons = []
    score = 0.0

    frp = event.get("frp") or 0.0
    frp_pts = min(30.0, (frp / 500.0) * 30.0)
    score += frp_pts
    if frp_pts >= 20:
        reasons.append("High thermal intensity (FRP)")

    brightness = event.get("brightness") or 0.0
    brightness_pts = min(10.0, max(0.0, (brightness - 290.0) / 130.0) * 10.0)
    score += brightness_pts
    if brightness_pts >= 7:
        reasons.append("High brightness temperature")

    confidence = event.get("confidence") or 0.0
    confidence_pts = min(10.0, (confidence / 100.0) * 10.0)
    score += confidence_pts
    if confidence_pts >= 8:
        reasons.append("High-confidence satellite detection")

    if distance_km is not None:
        if distance_km <= 1.0:
            prox_pts = 25.0
            reasons.append(f"Very close to industrial infrastructure ({distance_km:.2f} km)")
        elif distance_km <= config.INDUSTRIAL_PROXIMITY_KM:
            prox_pts = 25.0 * (1 - distance_km / config.INDUSTRIAL_PROXIMITY_KM)
            reasons.append(f"Near industrial infrastructure ({distance_km:.2f} km)")
        else:
            prox_pts = 0.0
    else:
        prox_pts = 0.0
    score += prox_pts

    persistence_count = persistence.get("persistence_count", 1)
    persist_pts = min(15.0, max(0.0, persistence_count - 1) * 2.5)
    score += persist_pts
    if persistence.get("persistent"):
        reasons.append(f"Repeated thermal detections ({persistence_count} observations)")

    label = classification.get("label", "Other / Unknown")
    class_severity = {
        "Industrial Fire": 10.0,
        "Gas Flare / Persistent Thermal Source": 6.0,
        "Natural / Forest Fire": 4.0,
        "Agricultural Fire": 2.0,
        "Other / Unknown": 0.0,
    }
    class_pts = class_severity.get(label, 0.0)
    score += class_pts
    if label in ("Industrial Fire", "Gas Flare / Persistent Thermal Source"):
        reasons.append(f"Classified as {label}")

    final_score = int(round(min(100.0, score)))
    level = _risk_level(final_score)

    if not reasons:
        reasons.append("Low intensity, isolated, low-confidence detection")

    return {
        "risk_score": final_score,
        "risk_level": level,
        "reasons": reasons,
    }
