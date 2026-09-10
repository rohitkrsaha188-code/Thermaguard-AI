# THERMAGUARD AI — Software Requirements Specification (SRS)

**Version:** 1.0 | **Date:** September 2026 | **SIH PS-26162 | Disaster Management**

---

## 1. Project Overview

THERMAGUARD AI is an AI-powered satellite thermal intelligence system. It ingests NASA FIRMS satellite data, classifies fire events using a Random Forest ML model, detects persistent thermal sources, calculates risk scores, and shows everything on an interactive GIS map.

### Problem Solved
NASA FIRMS satellites detect hotspots but cannot classify them. THERMAGUARD AI classifies each into:
1. Industrial Fire
2. Natural / Forest Fire
3. Agricultural Fire
4. Gas Flare / Persistent Thermal Source
5. Other / Unknown

---

## 2. System Architecture

```
FRONTEND (React + Vite) — localhost:5173
        |
        | HTTP (Axios)
        v
BACKEND (FastAPI + Uvicorn) — localhost:8000
        |
   +---------+----------+-----------+
   |         |          |           |
data_service ai_service risk_service database
(FIRMS CSV) (ML model) (risk score) (SQLite)
        |
   NASA FIRMS API / data/fires.csv (fallback)
   OpenStreetMap API / data/industrial_sites.csv (fallback)
```

---

## 3. Functional Requirements

| ID | Requirement |
|---|---|
| FR-01 | Ingest thermal events from NASA FIRMS API or CSV fallback |
| FR-02 | Load industrial sites from OpenStreetMap or CSV fallback |
| FR-03 | Classify each event using Random Forest ML (5 classes) |
| FR-04 | Detect persistent sources (>=3 detections within 1.5 km) |
| FR-05 | Calculate risk score (0-100) and risk level per event |
| FR-06 | Display events on interactive Leaflet GIS map |
| FR-07 | Show analytics dashboard with charts and stat cards |
| FR-08 | Show alert panel for High and Critical events |
| FR-09 | Support on-demand data refresh |
| FR-10 | Filter events by classification, risk level, persistence, industrial proximity |

---

## 4. Non-Functional Requirements

| Requirement | Target |
|---|---|
| API response time | < 2 seconds |
| ML classification | < 100ms per event |
| Offline mode | Full functionality via CSV fallback |
| No external API key required | Yes (API key optional) |
| Database | SQLite (no install needed) |

---

## 5. Technology Stack

### Backend
- FastAPI 0.115.0 — REST API framework
- Uvicorn 0.30.6 — ASGI server
- SQLAlchemy 2.0.35 — ORM / SQLite
- Pydantic 2.9.2 — data validation
- scikit-learn 1.5.2 — Random Forest ML
- pandas 2.2.3 + numpy 1.26.4 — data processing
- joblib 1.4.2 — model serialization
- python-dotenv 1.0.1 — config management

### Frontend
- React 18.3.1 — UI framework
- Vite 5.4.8 — build tool
- react-leaflet 4.2.1 + leaflet 1.9.4 — interactive map
- Recharts 2.12.7 — analytics charts
- Axios 1.7.7 — HTTP client
- IBM Plex Sans / Mono — typography

### ML Model
- Algorithm: Random Forest (150 trees, max depth 10)
- Features: brightness, FRP, confidence, distance_to_industry, nearby_count, persistence_count, industrial_zone
- Classes: 5 fire types
- Training: 2000 synthetic samples (400 per class)
- File: models/fire_classifier.pkl

---

## 6. API Endpoints

Base URL: http://localhost:8000

| Method | Endpoint | Description |
|---|---|---|
| GET | /health | Server health check |
| GET | /api/events | All events (filterable) |
| GET | /api/events/stats | Statistics summary |
| GET | /api/events/alerts | High + Critical events |
| GET | /api/events/{id} | Single event |
| GET | /api/events/{id}/risk | Risk details |
| GET | /api/industrial-sites | Industrial sites |
| POST | /api/events/analyze | Analyze custom coordinate |
| POST | /api/data/refresh | Refresh all data |

Interactive docs: http://localhost:8000/docs

---

## 7. Risk Scoring

| Factor | Points |
|---|---|
| Industrial Fire classification | +30 |
| FRP > 300 MW | +20 |
| FRP 100-300 MW | +10 |
| Distance to industry < 1 km | +25 |
| Distance 1-5 km | +15 |
| Persistent source | +15 |
| Confidence > 80% | +10 |

Risk Levels: Critical (>=80) | High (>=60) | Medium (>=35) | Low (<35)

---

## 8. Adding Training Data

Open data/fires.csv and add rows:
```
id,latitude,longitude,brightness,frp,confidence,acquisition_time,source,true_class_demo_only
TG-9001,22.35,69.82,321.1,47.6,90.6,2026-09-10T10:00:00Z,MODIS,Industrial Fire
```

Labels must be exactly one of:
- Industrial Fire
- Natural / Forest Fire
- Agricultural Fire
- Gas Flare / Persistent Thermal Source
- Other / Unknown

After adding data, retrain: python ml/train.py
Then restart backend.

---

## 9. SETUP GUIDE — NEW LAPTOP

### STEP 1 — Install Prerequisites

Python 3.11+
  Download: https://python.org/downloads
  Windows: check "Add Python to PATH" during install
  Verify: python --version

Node.js 18+
  Download: https://nodejs.org
  Verify: node --version

---

### STEP 2 — Copy Project Files

Copy the entire "Thermaguard-AI" folder to new laptop.
OR clone from git: git clone <your-repo-url>

---

### STEP 3 — Install Backend Dependencies

Open terminal in project folder:
  cd "Thermaguard-AI"
  pip install -r requirements.txt

(On Mac/Linux use pip3 if pip not found)

---

### STEP 4 — Check / Train ML Model

Check: ls models/
Should show: fire_classifier.pkl

If missing, run:
  python ml/train.py

---

### STEP 5 — Start Backend

  cd backend
  uvicorn main:app --host 0.0.0.0 --port 8000 --reload

Wait for: "INFO: Application startup complete."
Backend: http://localhost:8000
API docs: http://localhost:8000/docs

---

### STEP 6 — Install Frontend Dependencies

Open a NEW terminal (keep backend running):
  cd "Thermaguard-AI/frontend"
  npm install

---

### STEP 7 — Start Frontend

  npm run dev

Wait for: "Local: http://localhost:5173/"
Open browser: http://localhost:5173

---

### EVERY TIME — Run Both Servers

TERMINAL 1 (Backend):
  cd "Thermaguard-AI/backend"
  uvicorn main:app --host 0.0.0.0 --port 8000

TERMINAL 2 (Frontend):
  cd "Thermaguard-AI/frontend"
  npm run dev

Open: http://localhost:5173

---

### TROUBLESHOOTING

| Problem | Fix |
|---|---|
| pip not found | Use pip3 |
| python not found | Use python3 |
| Port 8000 busy | Mac: kill $(lsof -t -i:8000) |
| ModuleNotFoundError | pip install -r requirements.txt |
| Map not loading | Check backend on port 8000 |
| Model not found | python ml/train.py |

---

THERMAGUARD AI v1.0 | SIH 2024 | PS-26162
