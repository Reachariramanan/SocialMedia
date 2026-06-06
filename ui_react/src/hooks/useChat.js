import { useState, useCallback } from 'react'
import { sendChat } from '../utils/api'

/**
 * Chat dock state. Sends a message to /api/chat with the selected run as context.
 * - `onDeleteRun(runId)`  : called when the server reports a delete command.
 * - `reloadRuns()`        : called when the server reports a generate command, so the
 *                           new run shows up in the list once it completes.
 */
export default function useChat({ onDeleteRun, reloadRuns } = {}) {
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)

  const send = useCallback(async (text, runId) => {
    const trimmed = (text || '').trim()
    if (!trimmed || loading) return

    setMessages(prev => [...prev, { role: 'user', text: trimmed }])
    setLoading(true)
    try {
      const res = await sendChat(trimmed, runId)
      setMessages(prev => [...prev, { role: 'assistant', text: res.text || '(no response)' }])

      if (res.type === 'command' && res.action === 'generate') {
        // Poll a few times so the freshly-launched run appears in the list.
        reloadRuns?.()
        let n = 0
        const t = setInterval(() => {
          reloadRuns?.()
          if (++n >= 12) clearInterval(t)   // ~1 min of polling
        }, 5000)
      } else if (res.type === 'command' && res.action === 'delete') {
        if (res.run_id) onDeleteRun?.(res.run_id)
      }
    } catch (e) {
      setMessages(prev => [...prev, { role: 'assistant', text: `Error: ${e.message}` }])
    } finally {
      setLoading(false)
    }
  }, [loading, onDeleteRun, reloadRuns])

  const clear = useCallback(() => setMessages([]), [])

  return { messages, loading, send, clear }
}
