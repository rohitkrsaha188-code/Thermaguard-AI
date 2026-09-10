from pathlib import Path

import joblib
import pandas as pd

MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "fire_classifier.pkl"

FEATURE_NAMES = [
    "brightness", "frp", "confidence", "distance_to_industry_km",
    "nearby_industrial_count", "persistence_count", "industrial_zone_indicator",
]

# A few illustrative example events to eyeball before a live demo.
SAMPLES = {
    "Near-refinery high-intensity fire": [378.0, 480.0, 92.0, 0.6, 3, 2, 1.0],
    "Persistent flare at industrial site": [332.0, 85.0, 81.0, 0.4, 2, 9, 1.0],
    "Remote forest fire": [320.0, 55.0, 62.0, 32.0, 0, 1, 0.0],
    "Stubble-burning agricultural fire": [312.0, 22.0, 58.0, 9.0, 0, 1, 0.0],
    "Weak, ambiguous detection": [298.0, 12.0, 35.0, 18.0, 0, 1, 0.0],
}


def main():
    if not MODEL_PATH.exists():
        print(f"No model found at {MODEL_PATH}. Run `python train.py` first.")
        return

    model = joblib.load(MODEL_PATH)
    print(f"Loaded model from {MODEL_PATH}\n")

    for name, features in SAMPLES.items():
        X = pd.DataFrame([features], columns=FEATURE_NAMES)
        pred = model.predict(X)[0]
        proba = model.predict_proba(X)[0]
        probs = {cls: round(float(p), 3) for cls, p in zip(model.classes_, proba)}
        print(f"{name}")
        print(f"  features: {dict(zip(FEATURE_NAMES, features))}")
        print(f"  -> predicted: {pred}  (confidence {probs[pred]:.2f})")
        print(f"  -> probabilities: {probs}\n")


if __name__ == "__main__":
    main()
