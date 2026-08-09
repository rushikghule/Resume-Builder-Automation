const BASE = '/api'

export interface Template {
  id: string
  label: string
  description: string
  resume: StructuredResume
}

export interface ExperienceEntry {
  title: string
  company: string
  start_date: string
  end_date: string
  bullets: string[]
}

export interface EducationEntry {
  degree: string
  institution: string
  year: string
}

export interface StructuredResume {
  name?: string
  email?: string
  phone?: string
  summary?: string
  skills?: string[]
  experience?: ExperienceEntry[]
  education?: EducationEntry[]
}

export interface ATSScoreBreakdown {
  keyword_overlap_score: number
  quantified_achievements_score: number
  section_completeness_score: number
  formatting_score: number
  title_alignment_score: number
  total_score: number
  matched_keywords: string[]
  missing_keywords: string[]
  notes: string
}

export interface ClarifyingQuestion {
  id: string
  question: string
  related_gap: string
}

export interface AnalyzeResponse {
  session_id: string
  baseline_score: ATSScoreBreakdown
  clarifying_questions: ClarifyingQuestion[]
  structured_resume: StructuredResume
  structured_jd: Record<string, unknown>
}

export interface AnswersResponse {
  session_id: string
  tailored_resume: StructuredResume
  baseline_score: ATSScoreBreakdown
  final_score: ATSScoreBreakdown
  export_path: string
}

export type LLMProvider = 'groq' | 'openrouter' | 'ollama'

export async function fetchTemplates(): Promise<Template[]> {
  const res = await fetch(`${BASE}/templates`)
  if (!res.ok) throw new Error('Failed to load templates')
  return res.json()
}

export async function startSession(): Promise<string> {
  const res = await fetch(`${BASE}/session`, { method: 'POST' })
  if (!res.ok) throw new Error('Failed to start session')
  const data = await res.json()
  return data.session_id
}

export async function analyze(params: {
  sessionId: string
  jdText: string
  llmProvider: LLMProvider
  resumeSource: 'template' | 'upload'
  templateId?: string
  resumeFile?: File
}): Promise<AnalyzeResponse> {
  const form = new FormData()
  form.append('jd_text', params.jdText)
  form.append('llm_provider', params.llmProvider)
  form.append('resume_source', params.resumeSource)
  if (params.templateId) form.append('template_id', params.templateId)
  if (params.resumeFile) form.append('resume_file', params.resumeFile)

  const res = await fetch(`${BASE}/session/${params.sessionId}/analyze`, {
    method: 'POST',
    body: form,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Analysis failed' }))
    throw new Error(err.detail || 'Analysis failed')
  }
  return res.json()
}

export async function submitAnswers(
  sessionId: string,
  answers: Record<string, string>
): Promise<AnswersResponse> {
  const res = await fetch(`${BASE}/session/${sessionId}/answers`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ answers }),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Failed to submit answers' }))
    throw new Error(err.detail || 'Failed to submit answers')
  }
  return res.json()
}

export function downloadUrl(sessionId: string): string {
  return `${BASE}/session/${sessionId}/download`
}
