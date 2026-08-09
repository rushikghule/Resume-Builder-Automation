import { useEffect, useState } from 'react'
import type { Template } from '../api/client'
import { fetchTemplates } from '../api/client'

interface ResumeSelectProps {
  onSelect: (choice: { source: 'template'; templateId: string } | { source: 'upload'; file: File }) => void
}

export function ResumeSelect({ onSelect }: ResumeSelectProps) {
  const [templates, setTemplates] = useState<Template[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchTemplates()
      .then(setTemplates)
      .catch(() => setError('Could not load templates. Is the backend running?'))
      .finally(() => setLoading(false))
  }, [])

  const handleFile = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) onSelect({ source: 'upload', file })
  }

  return (
    <div className="max-w-3xl mx-auto px-6 py-16">
      <div className="mb-10">
        <p className="font-mono text-xs tracking-widest text-[color:var(--color-taupe)] mb-3">
          STEP 1 OF 3
        </p>
        <h1 className="font-display text-4xl font-semibold text-[color:var(--color-ink)]">
          Start with a resume
        </h1>
        <p className="font-body text-[color:var(--color-ink-soft)] mt-2">
          Choose a template to fill in, or upload the resume you already have.
        </p>
      </div>

      {error && (
        <p className="font-body text-sm text-[color:var(--color-flag)] mb-6">{error}</p>
      )}

      {!loading && (
        <>
          <div className="grid sm:grid-cols-3 gap-4 mb-10">
            {templates.map((t) => (
              <button
                key={t.id}
                onClick={() => onSelect({ source: 'template', templateId: t.id })}
                className="text-left p-5 rounded-md border transition-colors duration-150 hover:border-[color:var(--color-seal)] focus-visible:border-[color:var(--color-seal)]"
                style={{ borderColor: 'var(--color-paper-dim)', background: 'white' }}
              >
                <p className="font-display text-lg font-semibold mb-1">{t.label}</p>
                <p className="font-body text-sm text-[color:var(--color-ink-soft)]">
                  {t.description}
                </p>
              </button>
            ))}
          </div>

          <div className="relative flex items-center gap-4 mb-10">
            <div className="h-px flex-1" style={{ background: 'var(--color-paper-dim)' }} />
            <span className="font-mono text-xs tracking-widest text-[color:var(--color-taupe)]">
              OR
            </span>
            <div className="h-px flex-1" style={{ background: 'var(--color-paper-dim)' }} />
          </div>

          <label
            className="flex flex-col items-center justify-center gap-2 p-10 rounded-md border-2 border-dashed cursor-pointer transition-colors duration-150 hover:border-[color:var(--color-seal)]"
            style={{ borderColor: 'var(--color-paper-dim)' }}
          >
            <span className="font-body text-sm font-medium">Upload your resume</span>
            <span className="font-mono text-xs text-[color:var(--color-taupe)]">
              PDF, DOCX, or TXT
            </span>
            <input type="file" accept=".pdf,.docx,.txt" className="hidden" onChange={handleFile} />
          </label>
        </>
      )}
    </div>
  )
}
