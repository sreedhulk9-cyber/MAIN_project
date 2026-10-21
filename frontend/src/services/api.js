/**
 * API client communicating with AgentOS FastAPI backend.
 */

const API_BASE = "http://127.0.0.1:8000/api";

export async function fetchHealth() {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error("Backend service unreachable");
  return res.json();
}

export async function searchAirports(query) {
  if (!query || query.trim().length === 0) return [];
  const res = await fetch(`${API_BASE}/airports/search?q=${encodeURIComponent(query.trim())}`);
  if (!res.ok) return [];
  return res.json();
}

export async function searchFlights(params) {
  const res = await fetch(`${API_BASE}/flights/search`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Search failed with status ${res.status}`);
  }

  return res.json();
}

export async function sendChatMessage(message, agent = null) {
  const payload = { message };
  if (agent) payload.agent = agent;

  const res = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Chat request failed with status ${res.status}`);
  }

  return res.json();
}
