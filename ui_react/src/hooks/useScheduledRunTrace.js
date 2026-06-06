import { useState, useEffect, useRef, useCallback } from 'react'
import { fetchRunLiveStatus, fetchRunPartialHistory } from '../utils/api'

export default function useScheduledRunTrace(runId, { onComplete } = {}) {
  const [status, setStatus] = useState('idle')
  const [roundsComplete, setRoundsComplete] = useState(0)
  const [partialHistory, setPartialHistory] = useState([])
  const pollRef = useRef(null)

  const poll = useCallback(async () => {
    if (!runId) return

    try {
      const s = await fetchRunLiveStatus(runId)
      setStatus(s.status || 'running')
      setRoundsComplete(s.history_count || 0)

      if (s.status === 'done' || s.status === 'error') {
        clearInterval(pollRef.current)
        if (onComplete) onComplete(runId)
      }
    } catch (e) {
      // Silently handle poll errors
    }

    try {
      const h = await fetchRunPartialHistory(runId)
      setPartialHistory(Array.isArray(h) ? h : [])
    } catch (e) {
      // Silently handle history fetch errors
    }
  }, [runId, onComplete])

  useEffect(() => {
    if (!runId) {
      clearInterval(pollRef.current)
      setStatus('idle')
      setRoundsComplete(0)
      setPartialHistory([])
      return
    }

    poll()
    pollRef.current = setInterval(poll, 2000)
    return () => clearInterval(pollRef.current)
  }, [runId, poll])

  const isRunning = status === 'running' || status === 'queued'

  return { isRunning, status, roundsComplete, partialHistory }
}
