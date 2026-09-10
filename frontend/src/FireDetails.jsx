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
          </div>

          <RiskPanel event={event} />
        </>
      )}
    </div>
  );
}
