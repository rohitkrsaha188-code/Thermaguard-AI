export default function StatCards({ stats }) {
  if (!stats) return null;

  const cards = [
    { label: "Total Detections", value: stats.total_events },
    { label: "Industrial Fires", value: stats.industrial_fires },
    { label: "Natural Fires", value: stats.natural_fires },
    { label: "Agricultural Fires", value: stats.agricultural_fires },
    { label: "Gas Flares", value: stats.gas_flares },
    { label: "Persistent Sources", value: stats.persistent_sources },
    { label: "High Risk", value: stats.high_risk_events, className: "high" },
    { label: "Critical Alerts", value: stats.critical_events, className: "critical" },
  ];

  return (
    <div className="stat-strip">
      {cards.map((c) => (
        <div key={c.label} className={`stat-card ${c.className || ""}`}>
          <div className="stat-value">{c.value}</div>
          <div className="stat-label">{c.label}</div>
        </div>
      ))}
    </div>
  );
}
