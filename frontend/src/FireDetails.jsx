import { useState, useEffect } from "react";
import { MapContainer, TileLayer, CircleMarker } from "react-leaflet";
import RiskPanel from "./components/RiskPanel";
import { CLASS_COLORS } from "./constants";

function fmt(value, unit = "", digits = 1) {
  if (value === null || value === undefined) return "—";
  return `${Number(value).toFixed(digits)}${unit}`;
}

function fmtDate(value) {
  if (!value) return "—";
  return new Date(value).toLocaleString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function FireDetails({ event, onClose }) {
  const open = !!event;
  const color = event ? CLASS_COLORS[event.classification] : "#5b6b84";
  
  const [afterOpacity, setAfterOpacity] = useState(1);

  // Reset opacity when switching events
  useEffect(() => {
    setAfterOpacity(1);
  }, [event?.id]);

  let beforeDateStr = "";
  let afterDateStr = "";

  if (event?.acquisition_time) {
    const afterDate = new Date(event.acquisition_time);
    afterDateStr = afterDate.toISOString().split("T")[0];

    const beforeDate = new Date(afterDate.getTime() - 5 * 24 * 60 * 60 * 1000);
    beforeDateStr = beforeDate.toISOString().split("T")[0];
  }

  return (
    <div className={`detail-panel ${open ? "open" : ""}`}>
      {event && (
        <>
          <div className="detail-header">
            <div>
              <div className="detail-id mono">{event.id}</div>
              <div className="detail-classification" style={{ color }}>
                {event.classification}
              </div>
            </div>
            <button className="close-btn" onClick={onClose} aria-label="Close details">
              ×
            </button>
          </div>

          <div className="detail-body">
            <div className="detail-row">
              <span className="k">Classification confidence</span>
              <span className="v">{fmt((event.classification_confidence || 0) * 100, "%", 0)}</span>
            </div>
            <div className="confidence-bar-track">
              <div
                className="confidence-bar-fill"
                style={{ width: `${(event.classification_confidence || 0) * 100}%`, background: color }}
              />
            </div>

            <div className="detail-row" style={{ marginTop: 14 }}>
              <span className="k">Latitude</span>
              <span className="v">{fmt(event.latitude, "", 5)}</span>
            </div>
            <div className="detail-row">
              <span className="k">Longitude</span>
              <span className="v">{fmt(event.longitude, "", 5)}</span>
            </div>
            <div className="detail-row">
              <span className="k">Acquisition time</span>
              <span className="v">{fmtDate(event.acquisition_time)}</span>
            </div>
            <div className="detail-row">
              <span className="k">Source</span>
              <span className="v">{event.source}</span>
            </div>
            <div className="detail-row">
              <span className="k">Brightness</span>
              <span className="v">{fmt(event.brightness, " K")}</span>
            </div>
            <div className="detail-row">
              <span className="k">FRP</span>
              <span className="v">{fmt(event.frp, " MW")}</span>
            </div>
            <div className="detail-row">
              <span className="k">Detection confidence</span>
              <span className="v">{fmt(event.confidence, "%", 0)}</span>
            </div>
            <div className="detail-row">
              <span className="k">Nearest industrial site</span>
              <span className="v">{event.industrial_site_name || "None nearby"}</span>
            </div>
            <div className="detail-row">
              <span className="k">Distance to facility</span>
              <span className="v">{fmt(event.distance_to_industry_km, " km", 2)}</span>
            </div>
            <div className="detail-row">
              <span className="k">Persistence</span>
              <span className="v">
                {event.persistence_count} detection{event.persistence_count === 1 ? "" : "s"}
                {event.persistent ? " (persistent)" : ""}
              </span>
            </div>
            {event.persistent && (
              <>
                <div className="detail-row">
                  <span className="k">First seen</span>
                  <span className="v">{fmtDate(event.first_seen)}</span>
                </div>
                <div className="detail-row">
                  <span className="k">Last seen</span>
                  <span className="v">{fmtDate(event.last_seen)}</span>
                </div>
              </>
            )}

            <div className="satellite-before-after" style={{ marginTop: 24, padding: 12, background: "#101621", borderRadius: 8, border: "1px solid #1f2937" }}>
              <div style={{ fontSize: 13, fontWeight: 600, color: "#8996a8", marginBottom: 10, textTransform: "uppercase", letterSpacing: "0.05em" }}>Satellite View (Before / After)</div>
              <div style={{ height: 180, width: "100%", borderRadius: 6, overflow: "hidden", position: "relative" }}>
                <MapContainer 
                  center={[event.latitude, event.longitude]} 
                  zoom={8} 
                  maxZoom={9}
                  zoomControl={false} 
                  attributionControl={false}
                  dragging={false}
                  scrollWheelZoom={false}
                  doubleClickZoom={false}
                  style={{ height: "100%", width: "100%", zIndex: 1 }}
                  key={event.id}
                >
                  <TileLayer
                    url={`https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/VIIRS_SNPP_CorrectedReflectance_TrueColor/default/${beforeDateStr}/GoogleMapsCompatible_Level9/{z}/{y}/{x}.jpg`}
                    maxZoom={9}
                  />
                  <TileLayer
                    url={`https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/VIIRS_SNPP_CorrectedReflectance_TrueColor/default/${afterDateStr}/GoogleMapsCompatible_Level9/{z}/{y}/{x}.jpg`}
                    maxZoom={9}
                    opacity={afterOpacity}
                  />
                  <CircleMarker center={[event.latitude, event.longitude]} radius={6} pathOptions={{ color: "#ef4444", fillColor: "transparent", weight: 2 }} />
                </MapContainer>
              </div>
              <div style={{ display: "flex", alignItems: "center", marginTop: 12, gap: 12 }}>
                <span style={{ fontSize: 12, color: afterOpacity < 0.5 ? "#fff" : "#64748b", transition: "color 0.2s" }}>Before</span>
                <input 
                  type="range" 
                  min="0" max="1" step="0.01" 
                  value={afterOpacity} 
                  onChange={(e) => setAfterOpacity(parseFloat(e.target.value))}
                  style={{ flex: 1, accentColor: "#ef4444", cursor: "pointer" }}
                />
                <span style={{ fontSize: 12, color: afterOpacity > 0.5 ? "#fff" : "#64748b", transition: "color 0.2s" }}>After</span>
              </div>
            </div>
          </div>

          <RiskPanel event={event} />
        </>
      )}
    </div>
  );
}
