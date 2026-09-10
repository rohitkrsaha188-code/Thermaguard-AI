import { useMemo } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import StatCards from "./components/StatCards";
import { CLASS_COLORS, CLASS_SHORT_LABELS, RISK_COLORS, RISK_LEVELS } from "./constants";

function buildClassificationData(events) {
  const counts = {};
  for (const e of events) counts[e.classification] = (counts[e.classification] || 0) + 1;
  return Object.entries(counts).map(([classification, count]) => ({
    classification: CLASS_SHORT_LABELS[classification] || classification,
    count,
    color: CLASS_COLORS[classification] || "#5b6b84",
  }));
}

function buildRiskData(events) {
  const counts = { Low: 0, Medium: 0, High: 0, Critical: 0 };
  for (const e of events) {
    if (counts[e.risk_level] !== undefined) counts[e.risk_level] += 1;
  }
  return RISK_LEVELS.slice()
    .reverse()
    .map((level) => ({ level, count: counts[level], color: RISK_COLORS[level] }));
}

function buildTimelineData(events) {
  const counts = {};
  for (const e of events) {
    const day = new Date(e.acquisition_time).toISOString().slice(0, 10);
    counts[day] = (counts[day] || 0) + 1;
  }
  return Object.entries(counts)
    .sort(([a], [b]) => (a < b ? -1 : 1))
    .map(([day, count]) => ({ day: day.slice(5), count }));
}

export default function Dashboard({ events, stats }) {
  const classificationData = useMemo(() => buildClassificationData(events), [events]);
  const riskData = useMemo(() => buildRiskData(events), [events]);
  const timelineData = useMemo(() => buildTimelineData(events), [events]);

  const industrialCount = events.filter((e) => e.industrial_site_id).length;
  const nonIndustrialCount = events.length - industrialCount;

  return (
    <div className="dashboard">
      <StatCards stats={stats} />

      <div className="dashboard-grid">
        <div className="chart-panel">
          <h3>Classification distribution</h3>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={classificationData} layout="vertical" margin={{ left: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#232c3a" horizontal={false} />
              <XAxis type="number" stroke="#8996a8" fontSize={11} />
              <YAxis type="category" dataKey="classification" stroke="#8996a8" fontSize={11} width={80} />
              <Tooltip contentStyle={{ background: "#161d29", border: "1px solid #2f3b4e", fontSize: 12 }} />
              <Bar dataKey="count" radius={[0, 3, 3, 0]}>
                {classificationData.map((d, i) => (
                  <Cell key={i} fill={d.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-panel">
          <h3>Risk distribution</h3>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={riskData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#232c3a" vertical={false} />
              <XAxis dataKey="level" stroke="#8996a8" fontSize={11} />
              <YAxis stroke="#8996a8" fontSize={11} allowDecimals={false} />
              <Tooltip contentStyle={{ background: "#161d29", border: "1px solid #2f3b4e", fontSize: 12 }} />
              <Bar dataKey="count" radius={[3, 3, 0, 0]}>
                {riskData.map((d, i) => (
                  <Cell key={i} fill={d.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-panel">
          <h3>Thermal events over time</h3>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={timelineData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#232c3a" />
              <XAxis dataKey="day" stroke="#8996a8" fontSize={11} />
              <YAxis stroke="#8996a8" fontSize={11} allowDecimals={false} />
              <Tooltip contentStyle={{ background: "#161d29", border: "1px solid #2f3b4e", fontSize: 12 }} />
              <Line type="monotone" dataKey="count" stroke="#ff5a36" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-panel">
          <h3>Industrial vs. non-industrial proximity</h3>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart
              data={[
                { name: "Near industrial site", count: industrialCount },
                { name: "No nearby facility", count: nonIndustrialCount },
              ]}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#232c3a" vertical={false} />
              <XAxis dataKey="name" stroke="#8996a8" fontSize={11} />
              <YAxis stroke="#8996a8" fontSize={11} allowDecimals={false} />
              <Tooltip contentStyle={{ background: "#161d29", border: "1px solid #2f3b4e", fontSize: 12 }} />
              <Bar dataKey="count" radius={[3, 3, 0, 0]} fill="#4fd1ae" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
