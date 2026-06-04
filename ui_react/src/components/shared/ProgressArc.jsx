import React from 'react'

export default function ProgressArc({ current = 0, total = 5, size = 64, strokeWidth = 3 }) {
  const radius = (size - strokeWidth) / 2
  const circumference = 2 * Math.PI * radius
  const progress = total > 0 ? current / total : 0
  const offset = circumference * (1 - progress)

  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} style={{ transform: 'rotate(-90deg)' }}>
      <circle
        cx={size / 2}
        cy={size / 2}
        r={radius}
        fill="none"
        stroke="var(--border)"
        strokeWidth={strokeWidth}
      />
      <circle
        cx={size / 2}
        cy={size / 2}
        r={radius}
        fill="none"
        stroke="var(--signal-blue)"
        strokeWidth={strokeWidth}
        strokeDasharray={circumference}
        strokeDashoffset={offset}
        strokeLinecap="round"
        style={{ transition: 'stroke-dashoffset 0.6s var(--ease-out)' }}
      />
      <text
        x={size / 2}
        y={size / 2}
        textAnchor="middle"
        dominantBaseline="central"
        fill="var(--text-primary)"
        fontSize="14"
        fontFamily="var(--font-mono)"
        fontWeight="600"
        style={{ transform: 'rotate(90deg)', transformOrigin: 'center' }}
      >
        {current}/{total}
      </text>
    </svg>
  )
}
