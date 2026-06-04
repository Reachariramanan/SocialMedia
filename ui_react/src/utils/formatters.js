export function parseReport(text) {
  const s = { overview: [], active: [], watch: [] }
  let cur = null
  for (const raw of (text || '').split('\n')) {
    const ln = raw.trim()
    if (/^#{2,3}\s*overview$/i.test(ln))      { cur = 'overview'; continue }
    if (/^#{2,3}\s*active events$/i.test(ln)) { cur = 'active';   continue }
    if (/^#{2,3}\s*watch next$/i.test(ln))    { cur = 'watch';    continue }
    if (!ln) continue
    if (cur) s[cur].push(ln.replace(/^[-*]\s*/, ''))
  }
  return s
}

export function relTime(isoA, isoB) {
  if (!isoB) return 'latest'
  const abs = Math.abs(Math.round((new Date(isoA) - new Date(isoB)) / 60000))
  if (abs < 60) return `${abs} min${abs !== 1 ? 's' : ''}`
  const h = Math.floor(abs / 60), m = abs % 60
  return m ? `${h} hr ${m} min` : `${h} hr`
}

export function fmt(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

export function timeAgo(iso) {
  if (!iso) return ''
  const diff = Date.now() - new Date(iso).getTime()
  const m = Math.floor(diff / 60000)
  if (m < 1) return 'just now'
  if (m < 60) return `${m}m ago`
  const h = Math.floor(m / 60)
  if (h < 24) return `${h}h ago`
  return `${Math.floor(h / 24)}d ago`
}

export function parseOutput(raw) {
  if (!raw) return { type: 'text', value: '' }
  if (typeof raw === 'object') return { type: 'json', value: raw }
  const s = raw.trim()
  if (s.startsWith('<!') || s.startsWith('<html')) return { type: 'html', value: s }
  try {
    return { type: 'json', value: JSON.parse(s) }
  } catch {
    return { type: 'text', value: s }
  }
}
