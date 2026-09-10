import { RISK_COLORS } from "../constants";

export default function RiskPanel({ event }) {
  const level = event.risk_level || "Low";
  const color = RISK_COLORS[level] || RISK_COLORS.Low;

  return (
    <div className="risk-block">
      <div className="risk-score-row">
        <span className="risk-score-value" style={{ color }}>
          {event.risk_score ?? "—"}
        </span>
        <span
          className="risk-level-tag"
          style={{ color, background: `${color}1a`, border: `1px solid ${color}` }}
        >
          {level.toUpperCase()}
        </span>
        <span style={{ color: "var(--text-tertiary)", fontSize: "11px" }}>/ 100</span>
      </div>

      <ul className="risk-reasons">
        {(event.risk_reasons || []).map((reason, i) => (
          <li key={i}>{reason}</li>
        ))}
      </ul>

      <p className="risk-disclaimer">
        Prototype decision-support score, not a scientifically validated risk certification.
        Weighted from FRP, brightness, confidence, industrial proximity, persistence, and
        classification.
      </p>
    </div>
  );
}
