import { ScoreSeal } from './ScoreSeal'

interface ScoreComparisonProps {
  before: number
  after: number
}

export function ScoreComparison({ before, after }: ScoreComparisonProps) {
  const delta = Math.round(after - before)
  const improved = delta > 0

  return (
    <div className="flex items-center justify-center gap-8 sm:gap-14">
      <div className="flex flex-col items-center gap-2">
        <ScoreSeal score={before} label="BEFORE" size="md" />
      </div>

      <div className="flex flex-col items-center gap-1">
        <svg width="40" height="16" viewBox="0 0 40 16" fill="none">
          <path d="M0 8H36M36 8L28 1M36 8L28 15" stroke="var(--color-ink-soft)" strokeWidth="1.5" />
        </svg>
        {delta !== 0 && (
          <span
            className="font-mono text-xs font-medium"
            style={{ color: improved ? 'var(--color-seal)' : 'var(--color-flag)' }}
          >
            {improved ? '+' : ''}
            {delta}
          </span>
        )}
      </div>

      <div className="flex flex-col items-center gap-2">
        <ScoreSeal score={after} label="AFTER" size="lg" />
      </div>
    </div>
  )
}
