import type { ATSScoreBreakdown, StructuredResume } from '../api/client'
import { ScoreComparison } from '../components/ScoreComparison'
import { downloadUrl } from '../api/client'

interface TailoredResultProps {
  sessionId: string
  before: ATSScoreBreakdown
  after: ATSScoreBreakdown
  resume: StructuredResume
}

export function TailoredResult({ sessionId, before, after, resume }: TailoredResultProps) {
  return (
    <div className="max-w-3xl mx-auto px-6 py-16">
      <p className="font-mono text-xs tracking-widest text-[color:var(--color-taupe)] mb-3">
        DONE
      </p>
      <h1 className="font-display text-4xl font-semibold mb-10">Your tailored resume</h1>

      <div className="mb-12 p-8 rounded-md" style={{ background: 'white', border: '1px solid var(--color-paper-dim)' }}>
        <ScoreComparison before={before.total_score} after={after.total_score} />
      </div>

      <a
        href={downloadUrl(sessionId)}
        download
        className="inline-block px-6 py-3 rounded-md font-body text-sm font-medium text-white mb-12"
        style={{ background: 'var(--color-seal)' }}
      >
        Download as .docx
      </a>

      <div className="border-t pt-10" style={{ borderColor: 'var(--color-paper-dim)' }}>
        <p className="font-mono text-xs tracking-widest text-[color:var(--color-taupe)] mb-4">
          PREVIEW
        </p>
        <div className="p-8 rounded-md" style={{ background: 'white', border: '1px solid var(--color-paper-dim)' }}>
          <h2 className="font-display text-2xl font-semibold">{resume.name}</h2>
          <p className="font-mono text-xs text-[color:var(--color-ink-soft)] mt-1">
            {[resume.email, resume.phone].filter(Boolean).join(' · ')}
          </p>

          {resume.summary && (
            <p className="font-body text-sm mt-6 leading-relaxed">{resume.summary}</p>
          )}

          {resume.skills && resume.skills.length > 0 && (
            <div className="mt-6">
              <p className="font-mono text-xs tracking-widest text-[color:var(--color-taupe)] mb-2">
                SKILLS
              </p>
              <p className="font-body text-sm">{resume.skills.join(', ')}</p>
            </div>
          )}

          {resume.experience && resume.experience.length > 0 && (
            <div className="mt-6">
              <p className="font-mono text-xs tracking-widest text-[color:var(--color-taupe)] mb-2">
                EXPERIENCE
              </p>
              {resume.experience.map((exp, i) => (
                <div key={i} className="mb-4">
                  <p className="font-body text-sm font-medium">
                    {exp.title} — {exp.company}
                    <span className="font-mono text-xs text-[color:var(--color-taupe)] ml-2">
                      {exp.start_date} – {exp.end_date}
                    </span>
                  </p>
                  <ul className="mt-1 space-y-1">
                    {exp.bullets.map((b, j) => (
                      <li key={j} className="font-body text-sm text-[color:var(--color-ink-soft)] pl-4 relative before:content-['—'] before:absolute before:left-0">
                        {b}
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
