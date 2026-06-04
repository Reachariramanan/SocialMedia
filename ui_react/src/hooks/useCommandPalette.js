import { useState, useEffect, useCallback, useMemo } from 'react'
import { PRESETS } from '../data/locations'

export default function useCommandPalette({ runs, onLocationSelect, onStartRun, onDiscoverOpen, onFeedsOpen }) {
  const [isOpen, setIsOpen] = useState(false)
  const [search, setSearch] = useState('')

  const toggle = useCallback(() => {
    setIsOpen(v => !v)
    setSearch('')
  }, [])

  const close = useCallback(() => {
    setIsOpen(false)
    setSearch('')
  }, [])

  useEffect(() => {
    function handler(e) {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault()
        toggle()
      }
      if (e.key === 'Escape' && isOpen) {
        close()
      }
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [toggle, close, isOpen])

  const filteredLocations = useMemo(() => {
    const q = search.trim().toLowerCase()
    if (!q) return PRESETS.slice(0, 8)
    return PRESETS.filter(p => p.label.toLowerCase().includes(q)).slice(0, 12)
  }, [search])

  const filteredRuns = useMemo(() => {
    const q = search.trim().toLowerCase()
    if (!runs) return []
    if (!q) return runs.slice(0, 5)
    return runs.filter(r => r.topic?.toLowerCase().includes(q)).slice(0, 8)
  }, [search, runs])

  const actions = useMemo(() => {
    const q = search.trim().toLowerCase()
    const all = [
      { id: 'run', label: 'Generate Report...', hint: '/run', action: () => { close(); onStartRun?.() } },
      { id: 'discover', label: 'Discover Tweets...', hint: '/discover', action: () => { close(); onDiscoverOpen?.() } },
      { id: 'feeds', label: 'Fetch Feeds...', hint: '/feeds', action: () => { close(); onFeedsOpen?.() } },
    ]
    if (!q) return all
    return all.filter(a => a.label.toLowerCase().includes(q) || a.hint.includes(q))
  }, [search, close, onStartRun, onDiscoverOpen, onFeedsOpen])

  const selectLocation = useCallback((preset) => {
    close()
    onLocationSelect?.(preset.country, preset.city)
  }, [close, onLocationSelect])

  const selectRun = useCallback((run) => {
    close()
  }, [close])

  return {
    isOpen, search, setSearch,
    toggle, close,
    filteredLocations, filteredRuns, actions,
    selectLocation, selectRun,
  }
}
