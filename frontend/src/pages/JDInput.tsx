import { useState } from 'react'
import type { LLMProvider } from '../api/client'

interface JDInputProps {
  onSubmit: (jdText: string, provider: LLMProvider) => void
  loading: boolean
}

const PROVIDERS: { id: LLMProvider; label: string; hint: string }[] = [
  { id: 'groq', label: 'Groq', hint: 'Fast, free-tier cloud' },
  { id: 'openrouter', label: 'OpenRouter', hint: 'Model marketplace' },
  { id: 'ollama', label: 'Ollama (local)', hint: 'qwen3:4b, runs on your machine' },
]

export function JDInput({ onSubmit, loading }: JDInputProps) {
  const [jd, setJd] = useState('')
  const [provider, setProvider] = useState<LLMProvider>('groq')

  return (
    <div className="max-w-3xl mx-auto px-6 py-16">
      <div className="mb-8">
        <p className="font-mono text-xs tracking-widest text-[color:var(--color-taupe)] mb-3">
          STEP 2 OF 3
        </p>
        <h1 className="font-display text-4xl font-semibold">Paste the job description</h1>
        <p className="font-body text-[color:var(--color-ink-soft)] mt-2">
          We'll compare it against your resume and score the match.
        </p>
      </div>

      <textarea
        value={jd}
        onChange={(e) => setJd(e.target.value)}
        placeholder="Paste the full job description here…"
        rows={12}
        className="w-full p-4 rounded-md border font-body text-sm leading-relaxed resize-y focus-visible:outline-none"
        style={{ borderColor: 'var(--color-paper-dim)', background: 'white' }}
      />

      <div className="mt-8">
        <p className="font-mono text-xs tracking-widest text-[color:var(--color-taupe)] mb-3">
          LLM PROVIDER
        </p>
        <div className="grid sm:grid-cols-3 gap-3">
          {PROVIDERS.map((p) => (
            <button
              key={p.id}
              onClick={() => setProvider(p.id)}
              className="text-left p-3 rounded-md border transition-colors duration-150"
              style={{
                borderColor: provider === p.id ? 'var(--color-seal)' : 'var(--color-paper-dim)',
                background: provider === p.id ? 'rgba(43, 76, 63, 0.06)' : 'white',
              }}
            >
              <p className="font-body text-sm font-medium">{p.label}</p>
              <p className="font-mono text-xs text-[color:var(--color-taupe)] mt-0.5">{p.hint}</p>
            </button>
          ))}
        </div>
      </div>

      <button
        onClick={() => jd.trim() && onSubmit(jd, provider)}
        disabled={!jd.trim() || loading}
        className="mt-8 px-6 py-3 rounded-md font-body text-sm font-medium text-white disabled:opacity-40 transition-opacity"
        style={{ background: 'var(--color-seal)' }}
      >
        {loading ? 'Analyzing…' : 'Analyze match'}
      </button>
    </div>
  )
}
