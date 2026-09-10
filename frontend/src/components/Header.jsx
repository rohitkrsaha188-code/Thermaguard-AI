export default function Header({ view, onViewChange, onRefresh, refreshing }) {
  return (
    <header className="header">
      <div className="header-brand">
        <h1 className="header-title">
          THERMAG<span className="accent">UARD</span> AI
        </h1>
        <span className="header-subtitle">Satellite Intelligence &amp; Industrial Fire Monitoring</span>
      </div>

      <div className="header-right">
        <nav className="view-tabs">
          <button
            className={`view-tab ${view === "map" ? "active" : ""}`}
            onClick={() => onViewChange("map")}
          >
            Map
          </button>
          <button
            className={`view-tab ${view === "dashboard" ? "active" : ""}`}
            onClick={() => onViewChange("dashboard")}
          >
            Dashboard
          </button>
        </nav>

        <button className="refresh-btn" onClick={onRefresh} disabled={refreshing}>
          {refreshing ? "Refreshing…" : "Refresh Data"}
        </button>
      </div>
    </header>
  );
}
