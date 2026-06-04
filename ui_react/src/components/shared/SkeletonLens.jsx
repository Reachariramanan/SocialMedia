import React from 'react'

export default function SkeletonLens({ lines = 3 }) {
  return (
    <div className="skeleton-lens">
      {Array.from({ length: lines }, (_, i) => (
        <div key={i} className={`skeleton-line ${i % 3 === 2 ? 'skeleton-line-short' : i % 3 === 1 ? 'skeleton-line-medium' : ''}`} />
      ))}
    </div>
  )
}
