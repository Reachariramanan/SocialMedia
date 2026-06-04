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

export const startAgentRun = (topic) =>
  request('/api/agent/run', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ topic: topic || "today's top trending news" }),
  }).then(r => r.json())

export const fetchAgentStatus = (runId) =>
  request(`/api/agent/status/${runId}`).then(r => r.json())

export const fetchAgentResult = (runId) =>
  request(`/api/agent/result/${runId}`).then(r => r.json())

export const fetchScheduler = () =>
  fetch('/api/agent/scheduler').then(r => r.ok ? r.json() : null).catch(() => null)

export const fetchXfetchStatus = () =>
  fetch('/api/xfetch/status').then(r => r.ok ? r.json() : null).catch(() => null)

export const fetchRuns = () =>
  request('/api/runs').then(r => r.json())

export const fetchRunHtml = (runId) =>
  request(`/api/runs/${runId}/html`).then(r => r.text())

export const fetchRunHistory = (runId) =>
  request(`/api/runs/${runId}/history`).then(r => r.json())

export const fetchDashboardLatest = () =>
  fetch('/api/dashboard/latest').then(r => r.ok ? r.text() : '').catch(() => '')
