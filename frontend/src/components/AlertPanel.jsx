import { useState } from "react";

import { RISK_COLORS } from "../constants";

export default function AlertPanel({ alerts, onSelect }) {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <div className="alert-panel" style={collapsed ? { maxHeight: 40 } : undefined}>
      <div className="alert-panel-header" onClick={() => setCollapsed(!collapsed)} style={{ cursor: "pointer" }}>
        <span>
          High &amp; Critical Alerts <span className="alert-count">({alerts.length})</span>
        </span>
        <span>{collapsed ? "▲" : "▼"}</span>
      </div>

      {!collapsed && (
        <div className="alert-list">
          {alerts.length === 0 && (
            <div className="state-message" style={{ padding: 20 }}>
              No high-risk or critical events right now.
            </div>
          )}
          {alerts.map((event) => (
        <div key={event.id} className="alert-item" onClick={() => onSelect(event)}>
       <span
                className="alert-level-dot"
           style={{ background: RISK_COLORS[event.risk_level] || RISK_COLORS.Low }}
              />
              <div className="alert-item-main">
        <div className="alert-item-title">{event.classification}</div>
            <div className="alert-item-meta">
              {event.id} · {event.industrial_site_name || "no nearby facility"}
                </div>
         </div>
          <span className="alert-score" style={{ color: RISK_COLORS[event.risk_level] }}>
                {event.risk_score}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
