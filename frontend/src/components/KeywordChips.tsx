interface KeywordChipsProps {
  matched: string[]
  missing: string[]
}

export function KeywordChips({ matched, missing }: KeywordChipsProps) {
  return (
    <div className="space-y-4">
      {matched.length > 0 && (
        <div>
          <div className="font-mono text-xs tracking-widest text-[color:var(--color-seal)] mb-2">
            MATCHED · {matched.length}
          </div>
          <div className="flex flex-wrap gap-1.5">
            {matched.map((kw) => (
              <span
                key={kw}
                className="font-mono text-xs px-2 py-1 rounded-sm border"
                style={{
                  borderColor: 'var(--color-seal)',
                  color: 'var(--color-seal)',
                  background: 'rgba(43, 76, 63, 0.06)',
                }}
              >
                {kw}
              </span>
            ))}
          </div>
        </div>
      )}
      {missing.length > 0 && (
        <div>
          <div className="font-mono text-xs tracking-widest text-[color:var(--color-flag)] mb-2">
            MISSING · {missing.length}
          </div>
          <div className="flex flex-wrap gap-1.5">
            {missing.map((kw) => (
              <span
                key={kw}
                className="font-mono text-xs px-2 py-1 rounded-sm border border-dashed"
                style={{ borderColor: 'var(--color-flag)', color: 'var(--color-flag)' }}
              >
                {kw}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
