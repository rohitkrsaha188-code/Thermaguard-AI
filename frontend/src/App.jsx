import { useEffect, useState } from "react";

import * as api from "./api";
import AlertPanel from "./components/AlertPanel";
import Header from "./components/Header";
import Sidebar from "./components/Sidebar";
import Dashboard from "./Dashboard";
import FireDetails from "./FireDetails";
import Map from "./Map";

const EMPTY_FILTERS = { classification: null, riskLevel: null, persistentOnly: false, industrialOnly: false };

export default function App() {
  const [view, setView] = useState("map");
  const [events, setEvents] = useState([]);
  const [industrialSites, setIndustrialSites] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [stats, setStats] = useState(null);
  const [filters, setFilters] = useState(EMPTY_FILTERS);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [focusEvent, setFocusEvent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [refreshing, setRefreshing] = useState(false);

  async function loadAll() {
    try {
      setError(null);
      const [eventsRes, sitesRes, alertsRes, statsRes] = await Promise.all([
        api.getEvents(filters),
        api.getIndustrialSites(),
        api.getAlerts(),
        api.getStats(),
      ]);
      setEvents(eventsRes);
      setIndustrialSites(sitesRes);
      setAlerts(alertsRes);
      setStats(statsRes);
    } catch (err) {
      console.error(err);
      setError(
        "Could not reach the THERMAGUARD AI backend. Make sure the FastAPI server is running on the configured URL."
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    setLoading(true);
    loadAll();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filters]);

  async function handleRefresh() {
    setRefreshing(true);
    try {
      await api.refreshData();
      await loadAll();
    } catch (err) {
      console.error(err);
      setError("Refresh failed - backend may be unreachable.");
    } finally {
      setRefreshing(false);
    }
  }

  function handleSelectEvent(event) {
    setSelectedEvent(event);
    setFocusEvent(event);
    setView("map");
  }

  if (error) {
    return (
      <div className="app-shell">
        <Header view={view} onViewChange={setView} onRefresh={handleRefresh} refreshing={false} />
        <div className="state-message" style={{ height: "100%" }}>
          <div className="state-title">Connection error</div>
          <div>{error}</div>
        </div>
      </div>
    );
  }

  return (
    <div className="app-shell">
      <Header view={view} onViewChange={setView} onRefresh={handleRefresh} refreshing={refreshing} />

      <div className="app-body">
        <Sidebar filters={filters} onChange={setFilters} />

        <div className="map-area">
          {loading ? (
            <div className="state-message">
              <div className="spinner" />
              <div>Loading thermal intelligence…</div>
            </div>
          ) : view === "map" ? (
            events.length === 0 ? (
              <div className="state-message">
                <div className="state-title">No events match these filters</div>
                <div>Try clearing filters or refreshing the data.</div>
              </div>
            ) : (
              <Map
                events={events}
                industrialSites={industrialSites}
                selectedEvent={selectedEvent}
                onSelectEvent={handleSelectEvent}
                focusEvent={focusEvent}
              />
            )
          ) : (
            <Dashboard events={events} stats={stats} />
          )}

          {view === "map" && !loading && <FireDetails event={selectedEvent} onClose={() => setSelectedEvent(null)} />}
          {view === "map" && !loading && <AlertPanel alerts={alerts} onSelect={handleSelectEvent} />}
        </div>
      </div>
    </div>
  );
}
