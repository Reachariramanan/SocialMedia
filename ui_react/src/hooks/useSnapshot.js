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
  // Monotonic request id — only the most recent request may write state, so a
  // slower background fetch can never clobber a freshly-selected location.
  const reqIdRef = useRef(0)

  const loadDefault = useCallback(async () => {
    const myReq = ++reqIdRef.current
    try {
      setError('')
      const [snap, rep] = await Promise.all([fetchSnapshot(), fetchReport()])
      if (reqIdRef.current !== myReq) return
      setData(snap)
      setReport(rep)
      setLastRefresh(new Date())
    } catch (e) {
      if (reqIdRef.current === myReq) setError(e.message || 'load failed')
    } finally {
      if (reqIdRef.current === myReq) setLoading(false)
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
    const myReq = ++reqIdRef.current
    try {
      const snap = await fetchForLocation(country, city)
      if (reqIdRef.current !== myReq) return
      setData(snap)
      setReport('')
      setLastRefresh(new Date())
    } catch (e) {
      if (reqIdRef.current === myReq) setError(e.message || 'fetch failed')
    } finally {
      if (reqIdRef.current === myReq) setLoading(false)
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
      const myReq = ++reqIdRef.current
      // Only apply the poll result if it is still the latest request AND the
      // selected location hasn't changed mid-flight (so a worldwide poll can't
      // clobber a location, and vice-versa).
      const apply = (snap, expectedLoc) => {
        if (reqIdRef.current !== myReq) return
        if (locationRef.current !== expectedLoc) return
        setData(snap)
        setLastRefresh(new Date())
      }
      if (loc) {
        fetchForLocation(loc.country, loc.city)
          .then(snap => apply(snap, loc))
          .catch(() => {})
      } else {
        fetchSnapshot()
          .then(snap => apply(snap, null))
          .catch(() => {})
      }
    }, 30000)
    return () => clearInterval(id)
  }, [loadDefault])

  const snapshot = data?.snapshot ?? data ?? null

  return { snapshot, report, loading, error, lastRefresh, location, loadLocation, refresh }
}
