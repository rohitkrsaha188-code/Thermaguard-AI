import axios from "axios";

// Backend URL is configurable via a Vite env var so the frontend can point
// at a different host/port without code changes.
const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const client = axios.create({ baseURL: BASE_URL, timeout: 15000 });

export async function getHealth() {
  const res = await client.get("/health");
  return res.data;
}

export async function getEvents(filters = {}) {
  const params = {};
  if (filters.classification) params.classification = filters.classification;
  if (filters.riskLevel) params.risk_level = filters.riskLevel;
  if (filters.persistentOnly) params.persistent = true;
  if (filters.industrialOnly) params.industrial_only = true;
  const res = await client.get("/api/events", { params });
  return res.data;
}

export async function getEvent(eventId) {
  const res = await client.get(`/api/events/${eventId}`);
  return res.data;
}

export async function getStats() {
  const res = await client.get("/api/events/stats");
  return res.data;
}

export async function getAlerts() {
  const res = await client.get("/api/events/alerts");
  return res.data;
}

export async function getEventRisk(eventId) {
  const res = await client.get(`/api/events/${eventId}/risk`);
  return res.data;
}

export async function getIndustrialSites() {
  const res = await client.get("/api/industrial-sites");
  return res.data;
}

export async function analyzeEvent(payload) {
  const res = await client.post("/api/events/analyze", payload);
  return res.data;
}

export async function refreshData() {
  const res = await client.post("/api/data/refresh");
  return res.data;
}

export default client;
