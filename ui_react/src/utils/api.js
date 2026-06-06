async function request(url, options) {
  const r = await fetch(url, options)
  if (!r.ok) {
    const body = await r.json().catch(() => ({}))
    throw new Error(body.error || `HTTP ${r.status}`)
  }
  return r
}

export const fetchSnapshot = () =>
  request('/api/snapshot').then(r => r.json())

export const fetchForLocation = (country, city) => {
  const params = new URLSearchParams({ country })
  if (city) params.set('city', city)
  return request(`/api/fetch?${params}`).then(r => r.json())
}

export const fetchReport = () =>
  fetch('/api/report').then(r => r.ok ? r.text() : '')

export const fetchFeeds = (tags, limit = 8) =>
  request(`/api/feeds?tags=${encodeURIComponent(tags)}&limit=${limit}`).then(r => r.json())

export const fetchDiscover = (keywords, limit = 50) =>
  request(`/api/discover?keywords=${encodeURIComponent(keywords)}&limit=${limit}`).then(r => r.json())

export const startAgentRun = (topic, skill = 'html_report_writer') =>
  request('/api/agent/run', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ topic: topic || "today's top trending news", skill }),
  }).then(r => r.json())

export const fetchAgentStatus = (runId) =>
  request(`/api/agent/status/${runId}`).then(r => r.json())

export const fetchAgentResult = (runId) =>
  request(`/api/agent/result/${runId}`).then(r => r.json())

export const fetchScheduler = () =>
  fetch('/api/agent/scheduler').then(r => r.ok ? r.json() : null).catch(() => null)

export const fetchSchedules = () =>
  request('/api/schedules').then(r => r.json())

export const createSchedule = ({ topic, type, interval_sec, run_at }) =>
  request('/api/schedules', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ topic, type, interval_sec, run_at }),
  }).then(r => r.json())

export const deleteSchedule = (id) =>
  request(`/api/schedules/${id}`, { method: 'DELETE' }).then(r => r.json())

export const fetchXfetchStatus = () =>
  fetch('/api/xfetch/status').then(r => r.ok ? r.json() : null).catch(() => null)

export const fetchRuns = () =>
  request('/api/runs').then(r => r.json())

export const fetchRunHtml = (runId) =>
  request(`/api/runs/${runId}/html`).then(r => r.text())

export const fetchRunHistory = (runId) =>
  request(`/api/runs/${runId}/history`).then(r => r.json())

export const fetchRunLiveStatus = (runId) =>
  request(`/api/runs/${runId}/status`).then(r => r.json())

export const fetchRunPartialHistory = (runId) =>
  request(`/api/runs/${runId}/partial_history`).then(r => r.json())

export const deleteRun = (runId) =>
  request(`/api/runs/${runId}`, { method: 'DELETE' }).then(r => r.json())

export const sendChat = (message, runId) =>
  request('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, run_id: runId || null }),
  }).then(r => r.json())

export const fetchDashboardLatest = () =>
  fetch('/api/dashboard/latest').then(r => r.ok ? r.text() : '').catch(() => '')
