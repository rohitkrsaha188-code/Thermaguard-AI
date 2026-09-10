import { CLASS_COLORS, CLASSIFICATIONS, RISK_COLORS, RISK_LEVELS } from "../constants";

export default function Sidebar({ filters, onChange }) {
  const hasActiveFilters =
    filters.classification || filters.riskLevel || filters.persistentOnly || filters.industrialOnly;

  function setClassification(cls) {
    onChange({ ...filters, classification: filters.classification === cls ? null : cls });
  }

  function setRiskLevel(level) {
    onChange({ ...filters, riskLevel: filters.riskLevel === level ? null : level });
  }

  function toggle(key) {
    onChange({ ...filters, [key]: !filters[key] });
  }

  function clearAll() {
    onChange({ classification: null, riskLevel: null, persistentOnly: false, industrialOnly: false });
  }

  return (
    <aside className="sidebar">
      <div className="sidebar-section">
        <div className="sidebar-heading">Classification</div>
        {CLASSIFICATIONS.map((cls) => (
          <div
            key={cls}
            className={`filter-option ${filters.classification === cls ? "active" : ""}`}
            onClick={() => setClassification(cls)}
          >
            <span className="filter-dot" style={{ background: CLASS_COLORS[cls] }} />
            {cls}
          </div>
        ))}
      </div>

      <div className="sidebar-section">
        <div className="sidebar-heading">Risk Level</div>
        {RISK_LEVELS.map((level) => (
          <div
            key={level}
            className={`filter-option ${filters.riskLevel === level ? "active" : ""}`}
            onClick={() => setRiskLevel(level)}
          >
            <span className="filter-dot" style={{ background: RISK_COLORS[level] }} />
            {level}
          </div>
        ))}
      </div>

      <div className="sidebar-section">
        <div className="sidebar-heading">Filters</div>
        <div className="toggle-row">
          <span>Persistent sources only</span>
          <button
            className={`toggle-switch ${filters.persistentOnly ? "on" : ""}`}
            onClick={() => toggle("persistentOnly")}
            aria-label="Toggle persistent sources only"
          />
        </div>
        <div className="toggle-row">
          <span>Industrial events only</span>
          <button
            className={`toggle-switch ${filters.industrialOnly ? "on" : ""}`}
            onClick={() => toggle("industrialOnly")}
            aria-label="Toggle industrial events only"
          />
        </div>
      </div>

      {hasActiveFilters && (
        <button className="clear-filters" onClick={clearAll}>
          Clear all filters
        </button>
      )}
    </aside>
  );
}
