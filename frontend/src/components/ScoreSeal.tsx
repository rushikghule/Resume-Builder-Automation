import { useEffect, useState } from 'react'

interface ScoreSealProps {
  score: number
  label?: string
  size?: 'lg' | 'md'
}

export function ScoreSeal({ score, label = 'ATS SCORE', size = 'lg' }: ScoreSealProps) {
  const [stamped, setStamped] = useState(false)

  useEffect(() => {
    const t = setTimeout(() => setStamped(true), 80)
    return () => clearTimeout(t)
  }, [])

  const dim = size === 'lg' ? 168 : 108
  const ring = size === 'lg' ? 6 : 4
  const numSize = size === 'lg' ? 'text-5xl' : 'text-3xl'

  const color =
    score >= 75 ? 'var(--color-seal)' : score >= 50 ? 'var(--color-taupe)' : 'var(--color-flag)'

  return (
    <div
      className="relative inline-flex flex-col items-center justify-center rounded-full select-none"
      style={{
        width: dim,
        height: dim,
        border: `${ring}px solid ${color}`,
        color,
        transform: stamped ? 'scale(1) rotate(-3deg)' : 'scale(1.4) rotate(-3deg)',
        opacity: stamped ? 1 : 0,
        transition: 'transform 260ms cubic-bezier(0.2, 0.9, 0.3, 1.2), opacity 180ms ease-out',
      }}
    >
      <div
        className="absolute inset-2 rounded-full"
        style={{ border: `1px solid ${color}`, opacity: 0.4 }}
      />
      <span className={`font-display font-bold ${numSize}`} style={{ fontVariantNumeric: 'tabular-nums' }}>
        {Math.round(score)}
      </span>
      <span
        className="font-mono tracking-widest mt-1"
        style={{ fontSize: size === 'lg' ? '9px' : '7px', opacity: 0.85 }}
      >
        {label}
      </span>
    </div>
  )
}
