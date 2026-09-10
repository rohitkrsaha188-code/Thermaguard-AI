import csv
import math
from datetime import datetime
from typing import Optional

import requests

import config


def haversine_km(lat1, lon1, lat2, lon2) -> float:
    """Great-circle distance between two points in kilometers."""
    r = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * r * math.asin(min(1.0, math.sqrt(a)))


def _safe_float(value) -> Optional[float]:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def normalize_event(raw: dict, fallback_id: str) -> Optional[dict]:
    """
    Turn a raw row (from FIRMS API, FIRMS CSV, or a manual submission) into a
    consistent dict. Returns None if the row is unusable (e.g. bad coordinates).
    """
    lat = _safe_float(raw.get("latitude"))
    lon = _safe_float(raw.get("longitude"))
    if lat is None or lon is None or not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
        return None

    acq_time_raw = raw.get("acquisition_time")
    acq_time = None
    if acq_time_raw:
        for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
            try:
                acq_time = datetime.strptime(acq_time_raw, fmt)
                break
            except (ValueError, TypeError):
                continue
    if acq_time is None:
        # FIRMS raw CSV format sometimes splits acq_date + acq_time (HHMM)
        acq_date = raw.get("acq_date")
        acq_hhmm = raw.get("acq_time", "0000")
        if acq_date:
            try:
                hh = str(acq_hhmm).zfill(4)[:2]
                mm = str(acq_hhmm).zfill(4)[2:]
                acq_time = datetime.strptime(f"{acq_date} {hh}:{mm}", "%Y-%m-%d %H:%M")
            except (ValueError, TypeError):
                acq_time = datetime.utcnow()
        else:
            acq_time = datetime.utcnow()

    return {
        "id": raw.get("id") or fallback_id,
        "latitude": lat,
        "longitude": lon,
        "brightness": _safe_float(raw.get("brightness") or raw.get("bright_ti4")),
        "frp": _safe_float(raw.get("frp")),
        "confidence": _safe_float(raw.get("confidence")),
        "acquisition_time": acq_time,
        "source": raw.get("source") or raw.get("satellite") or raw.get("instrument") or "unknown",
    }


def fetch_firms_data() -> tuple[list[dict], bool]:
    """
    Returns (events, used_live_api).
    Tries the live NASA FIRMS API only if a key is configured; otherwise (or
    on any failure) falls back to the bundled demo CSV.
    """
    if config.NASA_FIRMS_API_KEY:
        try:
            url = f"{config.NASA_FIRMS_URL}/{config.NASA_FIRMS_API_KEY}/VIIRS_SNPP_NRT/world/1"
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            reader = csv.DictReader(resp.text.splitlines())
            events = []
            for i, row in enumerate(reader):
                norm = normalize_event(row, fallback_id=f"FIRMS-{i}")
                if norm:
                    events.append(norm)
            if events:
                return events, True
        except (requests.RequestException, ValueError) as exc:
            print(f"[data_service] FIRMS live fetch failed, using demo data: {exc}")

    return _load_fires_csv(), False


def _load_fires_csv() -> list[dict]:
    events = []
    if not config.FIRES_CSV.exists():
        print(f"[data_service] Demo fires CSV not found at {config.FIRES_CSV}")
        return events
    with open(config.FIRES_CSV, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            norm = normalize_event(row, fallback_id=row.get("id", ""))
            if norm:
                # keep the demo-only ground-truth label around for training/demo purposes
                norm["_demo_true_class"] = row.get("true_class_demo_only")
                events.append(norm)
    return events


def fetch_industrial_sites() -> tuple[list[dict], bool]:
    """
    Returns (sites, used_live_overpass).
    Attempts a live Overpass query for a broad, generic bounding box only if
    explicitly enabled would be too slow/unreliable for a hackathon demo, so
    by default this uses the curated demo CSV. The live path is still wired
    up and will be used automatically if reachable.
    """
    try:
        query = """
        [out:json][timeout:5];
        (
          node["industrial"]["name"](8.0,68.0,32.0,90.0);
        );
        out center 20;
        """
        resp = requests.post(config.OVERPASS_URL, data={"data": query}, timeout=6)
        resp.raise_for_status()
        payload = resp.json()
        elements = payload.get("elements", [])
        if elements:
            sites = []
            for i, el in enumerate(elements):
                tags = el.get("tags", {})
                sites.append({
                    "id": f"OSM-{el.get('id', i)}",
                    "name": tags.get("name", f"Industrial Site {i}"),
                    "type": tags.get("industrial", "other"),
                    "latitude": el.get("lat"),
                    "longitude": el.get("lon"),
                    "source": "OSM",
                })
            return sites, True
    except (requests.RequestException, ValueError) as exc:
        print(f"[data_service] Overpass live fetch failed, using demo data: {exc}")

    return _load_industrial_csv(), False


def _load_industrial_csv() -> list[dict]:
    sites = []
    if not config.INDUSTRIAL_CSV.exists():
        print(f"[data_service] Demo industrial CSV not found at {config.INDUSTRIAL_CSV}")
        return sites
    with open(config.INDUSTRIAL_CSV, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            lat = _safe_float(row.get("latitude"))
            lon = _safe_float(row.get("longitude"))
            if lat is None or lon is None:
                continue
            sites.append({
                "id": row.get("id"),
                "name": row.get("name"),
                "type": row.get("type", "other"),
                "latitude": lat,
                "longitude": lon,
                "source": row.get("source", "demo"),
            })
    return sites


def nearest_industrial_site(lat: float, lon: float, sites: list[dict]) -> tuple[Optional[dict], Optional[float]]:
    """Returns (nearest_site, distance_km) or (None, None) if no sites available."""
    if not sites:
        return None, None
    best_site, best_dist = None, math.inf
    for site in sites:
        d = haversine_km(lat, lon, site["latitude"], site["longitude"])
        if d < best_dist:
            best_dist, best_site = d, site
    return best_site, round(best_dist, 3)


def count_nearby_sites(lat: float, lon: float, sites: list[dict], radius_km: float) -> int:
    return sum(1 for s in sites if haversine_km(lat, lon, s["latitude"], s["longitude"]) <= radius_km)
