import { useState } from 'react'
import { ResumeSelect } from './pages/ResumeSelect'
import { JDInput } from './pages/JDInput'
import { AnalysisResult } from './pages/AnalysisResult'
import { ClarifyingQuestions } from './pages/ClarifyingQuestions'
import { TailoredResult } from './pages/TailoredResult'
import { startSession, analyze, submitAnswers } from './api/client'
import type { AnalyzeResponse, AnswersResponse, LLMProvider } from './api/client'

type Step = 'resume' | 'jd' | 'analysis' | 'questions' | 'result'
type ResumeChoice =
  | { source: 'template'; templateId: string }
  | { source: 'upload'; file: File }

function App() {
  const [step, setStep] = useState<Step>('resume')
  const [resumeChoice, setResumeChoice] = useState<ResumeChoice | null>(null)
  const [sessionId, setSessionId] = useState('')
  const [analyzeResult, setAnalyzeResult] = useState<AnalyzeResponse | null>(null)
  const [finalResult, setFinalResult] = useState<AnswersResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleResumeSelect = (choice: ResumeChoice) => {
    setResumeChoice(choice)
    setStep('jd')
  }

  const handleJDSubmit = async (jdText: string, provider: LLMProvider) => {
    if (!resumeChoice) return
    setLoading(true)
    setError('')
    try {
      const sid = await startSession()
      setSessionId(sid)
      const result = await analyze({
        sessionId: sid,
        jdText,
        llmProvider: provider,
        resumeSource: resumeChoice.source,
        templateId: resumeChoice.source === 'template' ? resumeChoice.templateId : undefined,
        resumeFile: resumeChoice.source === 'upload' ? resumeChoice.file : undefined,
      })
      setAnalyzeResult(result)
      setStep('analysis')
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  const handleAnswersSubmit = async (answers: Record<string, string>) => {
    setLoading(true)
    setError('')
    try {
      const result = await submitAnswers(sessionId, answers)
      setFinalResult(result)
      setStep('result')
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen" style={{ background: 'var(--color-paper)' }}>
      <header className="border-b" style={{ borderColor: 'var(--color-paper-dim)' }}>
        <div className="max-w-3xl mx-auto px-6 py-5 flex items-center justify-between">
          <span className="font-display font-semibold text-lg">Resume ⇄ JD</span>
          <span className="font-mono text-xs text-[color:var(--color-taupe)]">
            local · no data leaves your machine except to your chosen LLM
          </span>
        </div>
      </header>

      {error && (
        <div className="max-w-3xl mx-auto px-6 pt-6">
          <p className="font-body text-sm px-4 py-3 rounded-md" style={{ background: 'rgba(196,54,45,0.08)', color: 'var(--color-flag)' }}>
            {error}
          </p>
        </div>
      )}

      {step === 'resume' && <ResumeSelect onSelect={handleResumeSelect} />}

      {step === 'jd' && <JDInput onSubmit={handleJDSubmit} loading={loading} />}

      {step === 'analysis' && analyzeResult && (
        <AnalysisResult
          score={analyzeResult.baseline_score}
          onContinue={() => setStep('questions')}
        />
      )}

      {step === 'questions' && analyzeResult && (
        <ClarifyingQuestions
          questions={analyzeResult.clarifying_questions}
          onSubmit={handleAnswersSubmit}
          loading={loading}
        />
      )}

      {step === 'result' && finalResult && (
        <TailoredResult
          sessionId={sessionId}
          before={finalResult.baseline_score}
          after={finalResult.final_score}
          resume={finalResult.tailored_resume}
        />
      )}
    </div>
  )
}

export default App
