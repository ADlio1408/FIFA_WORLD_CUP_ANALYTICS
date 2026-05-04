/**
 * FIFA Analytics Platform — API Client
 * Connects frontend to FastAPI backend
 * Falls back to embedded data if API unavailable (offline/demo mode)
 */

const API_BASE = 'http://localhost:8000/api';

// ── Fetch wrapper with fallback ──────────────────────────────────────────────
async function apiFetch(endpoint, fallback = null) {
  try {
    const res = await fetch(API_BASE + endpoint, { signal: AbortSignal.timeout(3000) });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (e) {
    console.warn(`[API] ${endpoint} failed (${e.message}), using fallback`);
    return typeof fallback === 'function' ? fallback() : fallback;
  }
}

// ── API Methods ──────────────────────────────────────────────────────────────
const API = {
  kpis:        (year) => apiFetch(`/kpis${year ? '?year=' + year : ''}`),
  tournaments: (params = '') => apiFetch(`/tournaments${params}`),
  tournament:  (year) => apiFetch(`/tournaments/${year}`),
  matches:     (params = '') => apiFetch(`/matches${params}`),
  players:     (params = '') => apiFetch(`/players${params}`),
  topScorers:  (n = 10) => apiFetch(`/players/top?n=${n}`),
  teams:       (params = '') => apiFetch(`/teams${params}`),
  team:        (name) => apiFetch(`/teams/${encodeURIComponent(name)}`),
  goalsTrend:  () => apiFetch('/analytics/goals-trend'),
  stageBreakdown: (year) => apiFetch(`/analytics/stage-breakdown${year ? '?year=' + year : ''}`),
  countryPerf: () => apiFetch('/analytics/country-performance'),
  highScoring: (n = 10) => apiFetch(`/analytics/highest-scoring?n=${n}`),
  winners:     () => apiFetch('/analytics/winners-breakdown'),
  search:      (q) => apiFetch(`/search?q=${encodeURIComponent(q)}`),
};

// ── Status indicator ─────────────────────────────────────────────────────────
async function checkAPIStatus() {
  try {
    const res = await fetch(API_BASE.replace('/api', ''), { signal: AbortSignal.timeout(2000) });
    return res.ok;
  } catch { return false; }
}

window.API = API;
window.checkAPIStatus = checkAPIStatus;
