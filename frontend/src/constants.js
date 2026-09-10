// Shared visual mappings so every component (map markers, charts, badges,
// alerts) uses the same color for a given classification or risk level.

export const CLASS_COLORS = {
  "Industrial Fire": "#ff5a36",
  "Gas Flare / Persistent Thermal Source": "#ffb238",
  "Natural / Forest Fire": "#4fd1ae",
  "Agricultural Fire": "#d9c46a",
  "Other / Unknown": "#5b6b84",
};

export const CLASS_SHORT_LABELS = {
  "Industrial Fire": "Industrial",
  "Gas Flare / Persistent Thermal Source": "Gas Flare",
  "Natural / Forest Fire": "Natural",
  "Agricultural Fire": "Agricultural",
  "Other / Unknown": "Unknown",
};

export const RISK_COLORS = {
  Critical: "#ff3b3b",
  High: "#ff8c3b",
  Medium: "#f0c64b",
  Low: "#46c98a",
};

export const RISK_LEVELS = ["Critical", "High", "Medium", "Low"];
export const CLASSIFICATIONS = Object.keys(CLASS_COLORS);
