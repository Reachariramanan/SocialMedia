import React, { useState, useRef, useEffect } from 'react'
import { MessageSquare, Send } from 'lucide-react'
import useChat from '../../hooks/useChat'

/**
 * Bottom chat dock for the agentic framework view.
 * - Free-form Q&A about the selected report (routed to the LLM server-side).
 * - Commands: "generate <topic>" launches a report; "delete" removes the selected one.
 */
export default function ChatDock({ selectedRun, onDeleteRun, reloadRuns }) {
  const { messages, loading, send } = useChat({ onDeleteRun, reloadRuns })
  const [text, setText] = useState('')
  const bodyRef = useRef(null)

  useEffect(() => {
    if (bodyRef.current) bodyRef.current.scrollTop = bodyRef.current.scrollHeight
  }, [messages, loading])

  const submit = () => {
    if (!text.trim() || loading) return
    send(text, selectedRun?.run_id)
    setText('')
  }

  return (
    <div className="chat-dock">
      <div className="chat-dock-header">
        <MessageSquare size={11} style={{ display: 'inline', marginRight: 6 }} />
        Assistant
        <span className="chat-dock-hint">
          {selectedRun ? `· ${selectedRun.topic || 'report'}` : '· no report selected'}
        </span>
      </div>

      <div className="chat-dock-body" ref={bodyRef}>
        {messages.length === 0 && (
          <div className="chat-empty">
            Ask about the selected report, or type <code>generate &lt;topic&gt;</code> /
            <code> delete</code>.
          </div>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`chat-msg chat-msg-${m.role}`}>
            {m.text}
          </div>
        ))}
        {loading && <div className="chat-msg chat-msg-assistant chat-msg-loading">…</div>}
      </div>

      <div className="chat-dock-input">
        <textarea
          className="chat-textarea"
          placeholder="Message the assistant…"
          value={text}
          onChange={e => setText(e.target.value)}
          onKeyDown={e => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault()
              submit()
            }
          }}
          rows={1}
          disabled={loading}
        />
        <button className="chat-send-btn" onClick={submit} disabled={loading || !text.trim()} title="Send">
          <Send size={14} />
        </button>
      </div>
    </div>
  )
}
