import random
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split

random.seed(7)
np.random.seed(7)

MODEL_DIR = Path(__file__).resolve().parent.parent / "models"
MODEL_PATH = MODEL_DIR / "fire_classifier.pkl"

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


def sample_class(label: str, n: int) -> pd.DataFrame:
    """Generates n synthetic feature rows for one class, using distributions
    that reflect the physical intuition described in the problem statement."""
    rows = []
    for _ in range(n):
        if label == "Industrial Fire":
            brightness = np.random.normal(365, 25)
            frp = max(5, np.random.normal(340, 120))
            confidence = np.random.normal(85, 8)
            dist = abs(np.random.normal(1.2, 1.0))
            nearby = np.random.poisson(2) + 1
            persistence = np.random.randint(1, 4)

        elif label == "Gas Flare / Persistent Thermal Source":
            brightness = np.random.normal(330, 15)
            frp = max(5, np.random.normal(95, 40))
            confidence = np.random.normal(80, 10)
            dist = abs(np.random.normal(0.6, 0.5))
            nearby = np.random.poisson(2) + 1
            persistence = np.random.randint(4, 14)

        elif label == "Natural / Forest Fire":
            brightness = np.random.normal(325, 20)
            frp = max(2, np.random.normal(60, 35))
            confidence = np.random.normal(65, 15)
            dist = abs(np.random.normal(25, 15))
            nearby = np.random.poisson(0.2)
            persistence = np.random.randint(1, 3)

        elif label == "Agricultural Fire":
            brightness = np.random.normal(315, 15)
            frp = max(1, np.random.normal(30, 15))
            confidence = np.random.normal(60, 15)
            dist = abs(np.random.normal(10, 8))
            nearby = np.random.poisson(0.3)
            persistence = np.random.randint(1, 3)

        else:  # Other / Unknown
            brightness = np.random.normal(305, 20)
            frp = max(0.5, np.random.normal(18, 12))
            confidence = np.random.normal(40, 15)
            dist = abs(np.random.normal(20, 20))
            nearby = np.random.poisson(0.1)
            persistence = np.random.randint(1, 2)

        dist = max(0.05, dist)
        confidence = float(np.clip(confidence, 5, 100))
        industrial_zone = 1.0 if dist <= 5.0 else 0.0

        rows.append({
            "brightness": round(float(brightness), 1),
            "frp": round(float(frp), 1),
            "confidence": round(confidence, 1),
            "distance_to_industry_km": round(float(dist), 2),
            "nearby_industrial_count": int(nearby),
            "persistence_count": int(persistence),
            "industrial_zone_indicator": industrial_zone,
            "label": label,
        })
    return pd.DataFrame(rows)


def build_training_set(n_per_class=400) -> pd.DataFrame:
    frames = [sample_class(c, n_per_class) for c in CLASSES]
    df = pd.concat(frames, ignore_index=True)
    return df.sample(frac=1.0, random_state=7).reset_index(drop=True)  # shuffle


def main():
    print("Building synthetic training dataset (demo/prototype data - see README)...")
    df = build_training_set(n_per_class=400)
    print(f"Dataset shape: {df.shape}")
    print(df["label"].value_counts())

    X = df[FEATURE_NAMES]
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=7, stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=150,
        max_depth=10,
        min_samples_leaf=3,
        random_state=7,
        class_weight="balanced",
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    print("\n--- Evaluation on held-out test set ---")
    print(classification_report(y_test, y_pred))
    print("Confusion matrix (rows=true, cols=predicted):")
    print(confusion_matrix(y_test, y_pred, labels=CLASSES))

    importances = sorted(zip(FEATURE_NAMES, model.feature_importances_), key=lambda x: -x[1])
    print("\nFeature importances:")
    for name, imp in importances:
        print(f"  {name}: {imp:.3f}")

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(f"\nSaved model to {MODEL_PATH}")


if __name__ == "__main__":
    main()
