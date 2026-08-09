import { useState } from 'react'
import type { ClarifyingQuestion } from '../api/client'

interface ClarifyingQuestionsProps {
  questions: ClarifyingQuestion[]
  onSubmit: (answers: Record<string, string>) => void
  loading: boolean
}

export function ClarifyingQuestions({ questions, onSubmit, loading }: ClarifyingQuestionsProps) {
  const [answers, setAnswers] = useState<Record<string, string>>({})

  if (questions.length === 0) {
    return (
      <div className="max-w-3xl mx-auto px-6 py-16">
        <p className="font-body text-[color:var(--color-ink-soft)] mb-6">
          No gaps to clarify — your resume already covers this job's key requirements well.
        </p>
        <button
          onClick={() => onSubmit({})}
          className="px-6 py-3 rounded-md font-body text-sm font-medium text-white"
          style={{ background: 'var(--color-seal)' }}
        >
          Continue to tailored resume →
        </button>
      </div>
    )
  }

  return (
    <div className="max-w-3xl mx-auto px-6 py-16">
      <p className="font-mono text-xs tracking-widest text-[color:var(--color-taupe)] mb-3">
        A FEW QUESTIONS
      </p>
      <h1 className="font-display text-4xl font-semibold mb-2">Before we tailor it</h1>
      <p className="font-body text-[color:var(--color-ink-soft)] mb-10">
        Answer honestly — we'll only add what you confirm here. Leave blank to skip.
      </p>

      <div className="space-y-6 mb-10">
        {questions.map((q) => (
          <div key={q.id} className="p-5 rounded-md" style={{ background: 'white', border: '1px solid var(--color-paper-dim)' }}>
            <div className="flex items-center gap-2 mb-2">
              <span
                className="font-mono text-[10px] px-1.5 py-0.5 rounded-sm"
                style={{ background: 'rgba(196, 54, 45, 0.1)', color: 'var(--color-flag)' }}
              >
                {q.related_gap}
              </span>
            </div>
            <p className="font-body text-sm font-medium mb-3">{q.question}</p>
            <textarea
              rows={2}
              value={answers[q.id] || ''}
              onChange={(e) => setAnswers({ ...answers, [q.id]: e.target.value })}
              placeholder="Your answer…"
              className="w-full p-3 rounded-md border font-body text-sm resize-y focus-visible:outline-none"
              style={{ borderColor: 'var(--color-paper-dim)' }}
            />
          </div>
        ))}
      </div>

      <button
        onClick={() => onSubmit(answers)}
        disabled={loading}
        className="px-6 py-3 rounded-md font-body text-sm font-medium text-white disabled:opacity-40"
        style={{ background: 'var(--color-seal)' }}
      >
        {loading ? 'Tailoring…' : 'Build tailored resume →'}
      </button>
    </div>
  )
}
