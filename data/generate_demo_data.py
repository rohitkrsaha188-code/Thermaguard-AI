# import csv
# import random
# from datetime import datetime, timedelta

# random.seed(42)

# INDUSTRIAL_SITES = [
#     {"id": "IS-001", "name": "Jamnagar Refinery Complex", "type": "refinery", "lat": 22.3511, "lon": 69.8250},
#     {"id": "IS-002", "name": "Vizag Steel Plant", "type": "steel", "lat": 17.6868, "lon": 83.2185},
#     {"id": "IS-003", "name": "Bokaro Steel City Plant", "type": "steel", "lat": 23.6693, "lon": 86.1511},
#     {"id": "IS-004", "name": "Dahej Petrochemical Complex", "type": "petrochemical", "lat": 21.7051, "lon": 72.5680},
#     {"id": "IS-005", "name": "Vindhyachal Thermal Power Station", "type": "power_plant", "lat": 24.0975, "lon": 82.6425},
#     {"id": "IS-006", "name": "Talcher Coal Mines", "type": "mine", "lat": 20.9500, "lon": 85.2333},
#     {"id": "IS-007", "name": "Dhamra LNG Terminal", "type": "lng", "lat": 20.8167, "lon": 86.9333},
#     {"id": "IS-008", "name": "Paradip Refinery", "type": "refinery", "lat": 20.2650, "lon": 86.6110},
#     {"id": "IS-009", "name": "Korba Thermal Power Plant", "type": "power_plant", "lat": 22.3595, "lon": 82.7501},
#     {"id": "IS-010", "name": "Jharia Coalfield", "type": "mine", "lat": 23.7398, "lon": 86.4131},
#     {"id": "IS-011", "name": "Hazira Petrochemical Hub", "type": "petrochemical", "lat": 21.1167, "lon": 72.6500},
#     {"id": "IS-012", "name": "Rourkela Steel Plant", "type": "steel", "lat": 22.2604, "lon": 84.8536},
#     {"id": "IS-013", "name": "Kochi Refinery", "type": "refinery", "lat": 9.9667, "lon": 76.2833},
#     {"id": "IS-014", "name": "Dabhol LNG Terminal", "type": "lng", "lat": 17.5833, "lon": 73.1667},
#     {"id": "IS-015", "name": "Singrauli Power Cluster", "type": "power_plant", "lat": 24.1994, "lon": 82.6772},
#     {"id": "IS-016", "name": "Angul Industrial Estate", "type": "steel", "lat": 20.8400, "lon": 85.1000},
#     {"id": "IS-017", "name": "Barmer Oilfield Cluster", "type": "refinery", "lat": 25.7521, "lon": 71.3961},
#     {"id": "IS-018", "name": "Neyveli Lignite Mines", "type": "mine", "lat": 11.6104, "lon": 79.4737},
# ]

# # Natural/forest fire prone regions (away from industry), roughly Indian forest belts.
# NATURAL_ZONES = [
#     (30.3165, 78.0322),  # Uttarakhand forests
#     (11.4102, 76.6950),  # Nilgiris
#     (26.1584, 91.7898),  # Assam forests
#     (19.0760, 82.3200),  # Bastar/Chhattisgarh forests
#     (15.2993, 74.1240),  # Western Ghats, Goa
#     (27.5330, 88.5122),  # Sikkim/Darjeeling hills
# ]

# # Agriculture belts (Punjab/Haryana stubble-burning region).
# AGRI_ZONES = [
#     (30.7333, 76.7794),  # Punjab
#     (29.0588, 76.0856),  # Haryana
#     (26.8467, 80.9462),  # UP plains
# ]

# SOURCES = ["VIIRS", "MODIS"]

# CLASS_INFO = {
#     "Industrial Fire": dict(brightness=(330, 420), frp=(180, 650), confidence=(75, 98)),
#     "Gas Flare / Persistent Thermal Source": dict(brightness=(310, 360), frp=(40, 160), confidence=(70, 95)),
#     "Natural / Forest Fire": dict(brightness=(300, 360), frp=(15, 120), confidence=(50, 85)),
#     "Agricultural Fire": dict(brightness=(295, 340), frp=(8, 60), confidence=(45, 80)),
#     "Other / Unknown": dict(brightness=(290, 330), frp=(5, 40), confidence=(30, 60)),
# }

# BASE_DATE = datetime(2026, 8, 20)


# def jitter(lat, lon, km=3.0):
#     # ~0.009 deg latitude per km
#     dlat = random.uniform(-km, km) * 0.009
#     dlon = random.uniform(-km, km) * 0.009
#     return round(lat + dlat, 5), round(lon + dlon, 5)


# def sample(rng):
#     lo, hi = rng
#     return round(random.uniform(lo, hi), 1)


# def make_event(event_id, cls, lat, lon, acq_time, source=None):
#     info = CLASS_INFO[cls]
#     return {
#         "id": event_id,
#         "latitude": lat,
#         "longitude": lon,
#         "brightness": sample(info["brightness"]),
#         "frp": sample(info["frp"]),
#         "confidence": sample(info["confidence"]),
#         "acquisition_time": acq_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
#         "source": source or random.choice(SOURCES),
#         "true_class_demo_only": cls,  # kept only for transparency in the demo CSV
#     }


# rows = []
# counter = 1


# def next_id():
#     global counter
#     eid = f"TG-{1000 + counter}"
#     counter += 1
#     return eid


# # 1) Industrial fires: near industrial sites, mostly one-off but some clustered
# for site in INDUSTRIAL_SITES:
#     n_events = random.randint(2, 5)
#     for _ in range(n_events):
#         lat, lon = jitter(site["lat"], site["lon"], km=random.uniform(0.3, 4.5))
#         day_offset = random.randint(0, 19)
#         acq = BASE_DATE + timedelta(days=day_offset, hours=random.randint(0, 23), minutes=random.randint(0, 59))
#         rows.append(make_event(next_id(), "Industrial Fire", lat, lon, acq))

# # 2) Persistent thermal sources / gas flares: same tight coordinate, many repeats over time
# flare_sites = random.sample(INDUSTRIAL_SITES, 6)
# for site in flare_sites:
#     flare_lat, flare_lon = jitter(site["lat"], site["lon"], km=0.4)
#     n_repeats = random.randint(6, 11)
#     for i in range(n_repeats):
#         lat = round(flare_lat + random.uniform(-0.003, 0.003), 5)
#         lon = round(flare_lon + random.uniform(-0.003, 0.003), 5)
#         day_offset = i * random.randint(1, 2)
#         acq = BASE_DATE + timedelta(days=day_offset, hours=random.randint(0, 23))
#         rows.append(make_event(next_id(), "Gas Flare / Persistent Thermal Source", lat, lon, acq))

# # 3) Natural / forest fires: far from industry, scattered, low persistence
# for zlat, zlon in NATURAL_ZONES:
#     n_events = random.randint(4, 8)
#     for _ in range(n_events):
#         lat, lon = jitter(zlat, zlon, km=random.uniform(5, 40))
#         day_offset = random.randint(0, 19)
#         acq = BASE_DATE + timedelta(days=day_offset, hours=random.randint(0, 23))
#         rows.append(make_event(next_id(), "Natural / Forest Fire", lat, lon, acq))

# # 4) Agricultural fires: plains belt, seasonal clustering, low FRP
# for zlat, zlon in AGRI_ZONES:
#     n_events = random.randint(6, 10)
#     for _ in range(n_events):
#         lat, lon = jitter(zlat, zlon, km=random.uniform(2, 25))
#         day_offset = random.randint(10, 19)  # clustered late in window (harvest season)
#         acq = BASE_DATE + timedelta(days=day_offset, hours=random.randint(5, 11))
#         rows.append(make_event(next_id(), "Agricultural Fire", lat, lon, acq))

# # 5) Other/unknown: random low-signal points scattered around, far from everything mapped
# for _ in range(10):
#     lat = round(random.uniform(8.0, 32.0), 5)
#     lon = round(random.uniform(70.0, 90.0), 5)
#     day_offset = random.randint(0, 19)
#     acq = BASE_DATE + timedelta(days=day_offset, hours=random.randint(0, 23))
#     rows.append(make_event(next_id(), "Other / Unknown", lat, lon, acq))

# random.shuffle(rows)

# fieldnames = ["id", "latitude", "longitude", "brightness", "frp", "confidence",
#               "acquisition_time", "source", "true_class_demo_only"]

# with open("fires.csv", "w", newline="") as f:
#     writer = csv.DictWriter(f, fieldnames=fieldnames)
#     writer.writeheader()
#     for r in rows:
#         writer.writerow(r)

# with open("industrial_sites.csv", "w", newline="") as f:
#     writer = csv.DictWriter(f, fieldnames=["id", "name", "type", "latitude", "longitude", "source"])
#     writer.writeheader()
#     for s in INDUSTRIAL_SITES:
#         writer.writerow({
#             "id": s["id"], "name": s["name"], "type": s["type"],
#             "latitude": s["lat"], "longitude": s["lon"], "source": "demo",
#         })

# print(f"Generated {len(rows)} fire events and {len(INDUSTRIAL_SITES)} industrial sites.")
