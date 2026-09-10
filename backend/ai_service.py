from pathlib import Path
from typing import Optional

import joblib
import pandas as pd

import config

CLASSES = [
    "Industrial Fire",
    "Natural / Forest Fire",
    "Agricultural Fire",
    "Gas Flare / Persistent Thermal Source",
    "Other / Unknown",
]

FEATURE_NAMES = [
    "brightness", "frp", "confidence", "distance_to_industry_km",
    "nearby_industrial_count", "persistence_count", "industrial_zone_indicator",
]

_model = None
_model_loaded_attempted = False


def load_model():
    """Loads the model once and caches it. Returns None if unavailable."""
    global _model, _model_loaded_attempted
    if _model_loaded_attempted:
        return _model
    _model_loaded_attempted = True

    if Path(config.MODEL_PATH).exists():
        try:
            _model = joblib.load(config.MODEL_PATH)
            print(f"[ai_service] Loaded model from {config.MODEL_PATH}")
        except Exception as exc:  # noqa: BLE001 - want to fall back on any load issue
            print(f"[ai_service] Failed to load model, using heuristic fallback: {exc}")
            _model = None
    else:
        print(f"[ai_service] No trained model found at {config.MODEL_PATH}. "
              f"Run `python ml/train.py` first. Using heuristic fallback for now.")
    return _model


def build_features(event: dict, distance_km: Optional[float], nearby_count: int,
                    persistence_count: int) -> list[float]:
    """Builds the flat feature vector consumed by the model."""
    brightness = event.get("brightness") or 300.0
    frp = event.get("frp") or 10.0
    confidence = event.get("confidence") or 50.0
    dist = distance_km if distance_km is not None else 999.0
    industrial_zone_indicator = 1.0 if dist <= config.INDUSTRIAL_PROXIMITY_KM else 0.0

    return [
        float(brightness), float(frp), float(confidence), float(dist),
        float(nearby_count), float(persistence_count), industrial_zone_indicator,
    ]


def _heuristic_classify(features: list[float]) -> tuple[str, float, dict]:
    """Rule-based fallback used only when no trained model is available."""
    brightness, frp, confidence, dist, nearby_count, persistence_count, industrial_zone = features

    if industrial_zone and persistence_count >= config.PERSISTENCE_MIN_COUNT and frp < 180:
        label = "Gas Flare / Persistent Thermal Source"
        score = 0.72
    elif industrial_zone and frp >= 150:
        label = "Industrial Fire"
        score = 0.78
    elif dist > 15 and frp < 130:
        label = "Natural / Forest Fire"
        score = 0.6
    elif dist > 5 and frp < 70:
        label = "Agricultural Fire"
        score = 0.55
    else:
        label = "Other / Unknown"
        score = 0.4

    probs = {c: round((1 - score) / (len(CLASSES) - 1), 3) for c in CLASSES}
    probs[label] = round(score, 3)
    return label, score, probs


def classify(event: dict, distance_km: Optional[float], nearby_count: int,
             persistence_count: int) -> dict:
    """
    Returns:
        {"label": str, "confidence": float, "probabilities": {class: prob}, "model_used": bool}
    """
    features = build_features(event, distance_km, nearby_count, persistence_count)
    model = load_model()

    if model is not None:
        try:
            X = pd.DataFrame([features], columns=FEATURE_NAMES)
            pred = model.predict(X)[0]
            if hasattr(model, "predict_proba"):
                proba = model.predict_proba(X)[0]
                probabilities = {cls: round(float(p), 3) for cls, p in zip(model.classes_, proba)}
                confidence = probabilities.get(pred, max(proba))
            else:
                probabilities = {pred: 1.0}
                confidence = 1.0
            return {
                "label": pred,
                "confidence": round(float(confidence), 3),
                "probabilities": probabilities,
                "model_used": True,
            }
        except Exception as exc:  # noqa: BLE001
            print(f"[ai_service] Model prediction failed, falling back to heuristic: {exc}")

    label, confidence, probabilities = _heuristic_classify(features)
    return {
        "label": label,
        "confidence": confidence,
        "probabilities": probabilities,
        "model_used": False,
    }
