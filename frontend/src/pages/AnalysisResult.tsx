import type { ATSScoreBreakdown } from '../api/client'
import { ScoreSeal } from '../components/ScoreSeal'
import { KeywordChips } from '../components/KeywordChips'

interface AnalysisResultProps {
  score: ATSScoreBreakdown
  onContinue: () => void
}

const SUBSCORES: { key: keyof ATSScoreBreakdown; label: string; weight: string }[] = [
  { key: 'keyword_overlap_score', label: 'Keyword overlap', weight: '40%' },
  { key: 'quantified_achievements_score', label: 'Quantified achievements', weight: '20%' },
  { key: 'section_completeness_score', label: 'Section completeness', weight: '15%' },
  { key: 'formatting_score', label: 'ATS-readable formatting', weight: '15%' },
  { key: 'title_alignment_score', label: 'Title / seniority alignment', weight: '10%' },
]

export function AnalysisResult({ score, onContinue }: AnalysisResultProps) {
  return (
    <div className="max-w-3xl mx-auto px-6 py-16">
      <p className="font-mono text-xs tracking-widest text-[color:var(--color-taupe)] mb-3">
        STEP 3 OF 3 · BASELINE
      </p>
      <h1 className="font-display text-4xl font-semibold mb-10">Here's where you stand</h1>

      <div className="flex justify-center mb-12">
        <ScoreSeal score={score.total_score} />
      </div>

      <div className="grid sm:grid-cols-2 gap-x-10 gap-y-3 mb-10 p-6 rounded-md" style={{ background: 'white', border: '1px solid var(--color-paper-dim)' }}>
        {SUBSCORES.map((s) => (
          <div key={s.key} className="flex items-center justify-between">
            <span className="font-body text-sm text-[color:var(--color-ink-soft)]">
              {s.label} <span className="font-mono text-xs opacity-60">({s.weight})</span>
            </span>
            <span className="font-mono text-sm font-medium">{Math.round(score[s.key] as number)}</span>
          </div>
        ))}
      </div>

      {score.notes && (
        <p className="font-body text-sm italic text-[color:var(--color-ink-soft)] mb-10 px-1">
          "{score.notes}"
        </p>
      )}

      <KeywordChips matched={score.matched_keywords} missing={score.missing_keywords} />

      <button
        onClick={onContinue}
        className="mt-10 px-6 py-3 rounded-md font-body text-sm font-medium text-white"
        style={{ background: 'var(--color-seal)' }}
      >
        Answer a few questions to improve this →
      </button>
    </div>
  )
}
