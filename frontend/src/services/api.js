const API_BASE = 'http://localhost:8000/api';
const WS_BASE = 'ws://localhost:8000/api/stream/ws';

export async function fetchShelves() {
  const res = await fetch(`${API_BASE}/shelves`);
  if (!res.ok) throw new Error('Failed to fetch shelves');
  return res.json();
}

export async function fetchShelfDetails(shelfId) {
  const res = await fetch(`${API_BASE}/shelves/${shelfId}`);
  if (!res.ok) throw new Error('Failed to fetch shelf details');
  return res.json();
}

export async function fetchShelfHealth(shelfId) {
  const res = await fetch(`${API_BASE}/shelves/${shelfId}/health`);
  if (!res.ok) throw new Error('Failed to fetch shelf health');
  return res.json();
}

export async function fetchAlerts(shelfId = null, unacknowledgedOnly = true) {
  let url = `${API_BASE}/alerts?unacknowledged_only=${unacknowledgedOnly}`;
  if (shelfId) url += `&shelf_id=${shelfId}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error('Failed to fetch alerts');
  return res.json();
}

export async function acknowledgeAlert(alertId) {
  const res = await fetch(`${API_BASE}/alerts/${alertId}/acknowledge`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ is_acknowledged: true })
  });
  if (!res.ok) throw new Error('Failed to acknowledge alert');
  return res.json();
}

export async function acknowledgeAllAlerts(shelfId = null) {
  let url = `${API_BASE}/alerts/acknowledge-all`;
  if (shelfId) url += `?shelf_id=${shelfId}`;
  const res = await fetch(url, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to acknowledge all alerts');
  return res.json();
}

export async function fetchAnalyticsOverview() {
  const res = await fetch(`${API_BASE}/analytics/overview`);
  if (!res.ok) throw new Error('Failed to fetch analytics overview');
  return res.json();
}

export async function fetchHealthTrends() {
  const res = await fetch(`${API_BASE}/analytics/health-trends`);
  if (!res.ok) throw new Error('Failed to fetch health trends');
  return res.json();
}

export function getVideoFeedUrl(shelfId) {
  return `http://localhost:8000/api/stream/video_feed/${shelfId}?t=${Date.now()}`;
}

export function connectShelfWebSocket(shelfId, onMessage, onError) {
  const ws = new WebSocket(`${WS_BASE}/${shelfId}`);
  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onMessage(data);
    } catch (err) {
      console.error("WS Parse error", err);
    }
  };
  ws.onerror = (err) => {
    if (onError) onError(err);
  };
  return ws;
}
