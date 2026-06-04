import { useState, useEffect, useCallback, useRef } from 'react'
import { fetchSnapshot, fetchForLocation, fetchReport } from '../utils/api'

export default function useSnapshot() {
  const [data, setData] = useState(null)
  const [report, setReport] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [lastRefresh, setLastRefresh] = useState(null)
  const [location, setLocation] = useState(null)
  const locationRef = useRef(null)

  const loadDefault = useCallback(async () => {
    try {
      setError('')
      const [snap, rep] = await Promise.all([fetchSnapshot(), fetchReport()])
      setData(snap)
      setReport(rep)
      setLastRefresh(new Date())
    } catch (e) {
      setError(e.message || 'load failed')
    } finally {
      setLoading(false)
    }
  }, [])

  const loadLocation = useCallback(async (country, city) => {
    if (country === 'worldwide' || !country) {
      setLocation(null)
      locationRef.current = null
      loadDefault()
      return
    }
    const loc = { country, city }
    setLocation(loc)
    locationRef.current = loc
    setLoading(true)
    setError('')
    try {
      const snap = await fetchForLocation(country, city)
      setData(snap)
      setReport('')
      setLastRefresh(new Date())
    } catch (e) {
      setError(e.message || 'fetch failed')
    } finally {
      setLoading(false)
    }
  }, [loadDefault])

  const refresh = useCallback(() => {
    const loc = locationRef.current
    if (loc) {
      loadLocation(loc.country, loc.city)
    } else {
      loadDefault()
    }
  }, [loadDefault, loadLocation])

  useEffect(() => {
    loadDefault()
    const id = setInterval(() => {
      const loc = locationRef.current
      if (loc) {
        fetchForLocation(loc.country, loc.city)
          .then(snap => { setData(snap); setLastRefresh(new Date()) })
          .catch(() => {})
      } else {
        fetchSnapshot()
          .then(snap => { setData(snap); setLastRefresh(new Date()) })
          .catch(() => {})
      }
    }, 30000)
    return () => clearInterval(id)
  }, [loadDefault])

  const snapshot = data?.snapshot ?? data ?? null

  return { snapshot, report, loading, error, lastRefresh, location, loadLocation, refresh }
}
