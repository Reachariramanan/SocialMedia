import { useState, useEffect, useCallback } from 'react'

export default function useXtraction() {
  const [posts, setPosts] = useState([])
  const [loading, setLoading] = useState(false)

  const refresh = useCallback(async () => {
    setLoading(true)
    try {
      const r = await fetch('/api/xtraction/posts')
      if (r.ok) {
        const data = await r.json()
        setPosts(data.posts || [])
      }
    } catch (_) {
      // server may not be running
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    refresh()
  }, [refresh])

  return { posts, loading, refresh }
}
