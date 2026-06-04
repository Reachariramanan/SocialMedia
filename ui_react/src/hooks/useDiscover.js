import { useState, useCallback } from 'react'
import { fetchDiscover } from '../utils/api'

export default function useDiscover() {
  const [input, setInput] = useState('')
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const doDiscover = useCallback(async (keywords) => {
    const kw = (keywords || input).trim()
    if (!kw) return
    setLoading(true)
    setError('')
    setResults(null)
    try {
      const data = await fetchDiscover(kw)
      setResults(data)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }, [input])

  return { input, setInput, results, loading, error, doDiscover }
}
