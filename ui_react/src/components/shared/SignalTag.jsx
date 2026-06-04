import React from 'react'

export default function SignalTag({ name, active, onClick }) {
  const isHash = name.startsWith('#')
  return (
    <button
      className={`signal-tag ${isHash ? 'signal-tag-hash' : 'signal-tag-plain'} ${active ? 'signal-tag-active' : ''}`}
      onClick={onClick}
      title={name}
    >
      {name}
    </button>
  )
}
