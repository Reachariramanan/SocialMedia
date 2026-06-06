import { useState, useEffect, useCallback } from 'react'
import { fetchRuns, fetchRunHtml, fetchRunHistory, deleteRun } from '../utils/api'

export default function useRuns() {
  const [runs, setRuns] = useState([])
  const [selected, setSelected] = useState(null)
  const [html, setHtml] = useState('')
  const [history, setHistory] = useState(null)
  const [loading, setLoading] = useState(false)

  const selectRun = useCallback(async (run) => {
    setSelected(run)
    setLoading(true)
    setHtml('')
    setHistory(null)
    try {
      const h = await fetchRunHtml(run.run_id)
      setHtml(h)
    } catch {}
    try {
      const hist = await fetchRunHistory(run.run_id)
      setHistory(hist)
    } catch {}
    setLoading(false)
  }, [])

  const load = useCallback(async () => {
    try {
      const data = await fetchRuns()
      const withHtml = data.filter(r => r.has_html)
      setRuns(withHtml)
      // Auto-select the newest report only when nothing is selected yet. Read
      // `selected` functionally so this stays correct across reloads without
      // re-creating the callback on every change.
      if (withHtml.length > 0) {
        setSelected(prev => {
          if (!prev) selectRun(withHtml[0])
          return prev
        })
      }
    } catch {}
  }, [selectRun])

  useEffect(() => { load() }, [load])

  const remove = useCallback(async (runId) => {
    try {
      await deleteRun(runId)
    } catch {}
    setRuns(prev => prev.filter(r => r.run_id !== runId))
    setSelected(prev => {
      if (prev?.run_id === runId) {
        setHtml('')
        setHistory(null)
        return null
      }
      return prev
    })
  }, [])

  return { runs, selected, html, history, loading, selectRun, remove, reload: load }
}
