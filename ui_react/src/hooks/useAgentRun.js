import { useState, useRef, useCallback } from 'react'
import { startAgentRun, fetchAgentStatus } from '../utils/api'

export default function useAgentRun(onComplete) {
  const [runId, setRunId] = useState(null)
  const [status, setStatus] = useState(null)
  const [rounds, setRounds] = useState([])
  const [error, setError] = useState('')
  const pollRef = useRef(null)

  const start = useCallback(async (topic) => {
    setError('')
    setRounds([])
    setStatus('queued')
    try {
      const data = await startAgentRun(topic)
      setRunId(data.run_id)

      pollRef.current = setInterval(async () => {
        try {
          const s = await fetchAgentStatus(data.run_id)
          setStatus(s.status)
          if (s.history_count) {
            setRounds(Array.from({ length: s.history_count }, (_, i) => i + 1))
          }
          if (s.status === 'done' || s.status === 'error') {
            clearInterval(pollRef.current)
            if (s.status === 'done' && onComplete) onComplete(data.run_id)
          }
        } catch {}
      }, 2000)
    } catch (e) {
      setError(e.message)
      setStatus(null)
    }
  }, [onComplete])

  const isRunning = status === 'queued' || status === 'running'

  return { start, runId, status, rounds, isRunning, error }
}
