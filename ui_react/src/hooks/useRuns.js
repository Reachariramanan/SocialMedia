import { useState, useEffect, useCallback } from 'react'
import { fetchRuns, fetchRunHtml, fetchRunHistory } from '../utils/api'

export default function useRuns() {
  const [runs, setRuns] = useState([])
  const [selected, setSelected] = useState(null)
  const [html, setHtml] = useState('')
  const [history, setHistory] = useState(null)
  const [loading, setLoading] = useState(false)

  const load = useCallback(async () => {
    try {
      const data = await fetchRuns()
      const withHtml = data.filter(r => r.has_html)
      setRuns(withHtml)
      if (withHtml.length > 0 && !selected) {
        selectRun(withHtml[0])
      }
    } catch {}
  }, [])

  useEffect(() => { load() }, [load])

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

  return { runs, selected, html, history, loading, selectRun, reload: load }
}
