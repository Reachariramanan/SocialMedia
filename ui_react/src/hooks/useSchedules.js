import { useState, useEffect, useCallback } from 'react'
import { fetchSchedules, createSchedule, deleteSchedule } from '../utils/api'

export default function useSchedules() {
  const [schedules, setSchedules] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const load = useCallback(async () => {
    try {
      const data = await fetchSchedules()
      setSchedules(Array.isArray(data) ? data : [])
    } catch {}
  }, [])

  // Load on mount, then poll — faster when a run is active
  useEffect(() => {
    load()
    const anyRunning = schedules.some(s => s.running_run_id)
    // When active: 3s, when idle: 15s (more responsive than original 30s)
    const interval = anyRunning ? 3000 : 15000
    const id = setInterval(load, interval)
    return () => clearInterval(id)
  }, [load, schedules])

  const create = useCallback(async (payload) => {
    setLoading(true)
    setError(null)
    try {
      const sched = await createSchedule(payload)
      setSchedules(prev => [...prev, sched])
      // Reload immediately to catch any scheduled run that fires quickly
      setTimeout(load, 100)
      return sched
    } catch (e) {
      setError(e.message || 'Could not create schedule')
      throw e
    } finally {
      setLoading(false)
    }
  }, [load])

  const remove = useCallback(async (id) => {
    try {
      await deleteSchedule(id)
    } catch {}
    setSchedules(prev => prev.filter(s => s.id !== id))
  }, [])

  const activeRun = schedules.find(s => s.running_run_id) || null

  return { schedules, loading, error, create, remove, reload: load, activeRun }
}
