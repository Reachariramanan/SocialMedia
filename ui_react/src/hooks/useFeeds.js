import { useState, useCallback } from 'react'
import { fetchFeeds } from '../utils/api'

export default function useFeeds() {
  const [input, setInput] = useState('')
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const doFetch = useCallback(async (tags) => {
    const t = (tags || input).trim()
    if (!t) return
    setLoading(true)
    setError('')
    setResults(null)
    try {
      const data = await fetchFeeds(t)
      setResults(data)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }, [input])

  return { input, setInput, results, loading, error, doFetch }
}
