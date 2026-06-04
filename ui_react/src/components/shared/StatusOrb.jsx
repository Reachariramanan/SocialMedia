import React from 'react'

export default function StatusOrb({ status = 'idle' }) {
  return <span className={`status-orb status-orb-${status}`} />
}
