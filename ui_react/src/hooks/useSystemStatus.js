import { useState, useEffect, useCallback } from 'react'
import { fetchXfetchStatus, fetchScheduler } from '../utils/api'

export default function useSystemStatus() {
  const [xfetch, setXfetch] = useState(null)
  const [scheduler, setScheduler] = useState(null)

  const load = useCallback(async () => {
    const [xf, sched] = await Promise.all([
      fetchXfetchStatus(),
      fetchScheduler(),
    ])
    setXfetch(xf)
    setScheduler(sched)
  }, [])

  useEffect(() => {
    load()
    const id = setInterval(load, 30000)
    return () => clearInterval(id)
  }, [load])

  const healthy = xfetch?.available !== false

  return { xfetch, scheduler, healthy, refresh: load }
}
