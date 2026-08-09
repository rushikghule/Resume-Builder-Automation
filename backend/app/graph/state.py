"""State schema shared across all graph nodes."""
from typing import TypedDict, Optional, Literal


class ExperienceEntry(TypedDict, total=False):
    title: str
    company: str
    start_date: str
    end_date: str
    bullets: list[str]


class EducationEntry(TypedDict, total=False):
    degree: str
    institution: str
    year: str


class StructuredResume(TypedDict, total=False):
    name: str
    email: str
    phone: str
    summary: str
    skills: list[str]
    experience: list[ExperienceEntry]
    education: list[EducationEntry]
    raw_text: str  # fallback full text, always kept for reference


class StructuredJD(TypedDict, total=False):
    title: str
    seniority: str
    required_skills: list[str]
    nice_to_have_skills: list[str]
    key_phrases: list[str]
    raw_text: str


class ATSScoreBreakdown(TypedDict, total=False):
    keyword_overlap_score: float
    quantified_achievements_score: float
    section_completeness_score: float
    formatting_score: float
    title_alignment_score: float
    total_score: float
    matched_keywords: list[str]
    missing_keywords: list[str]
    notes: str


class ClarifyingQuestion(TypedDict, total=False):
    id: str
    question: str
    related_gap: str  # which missing keyword/skill this addresses


class GraphState(TypedDict, total=False):
    # inputs
    resume_source: Literal["template", "upload"]
    template_id: Optional[str]
    resume_raw_text: Optional[str]  # extracted text from uploaded file
    jd_raw_text: str
    llm_provider: str  # groq | openrouter | ollama, chosen per-session

    # derived
    structured_resume: StructuredResume
    structured_jd: StructuredJD
    baseline_score: ATSScoreBreakdown

    # human-in-the-loop
    clarifying_questions: list[ClarifyingQuestion]
    user_answers: dict[str, str]  # question id -> answer

    # output
    tailored_resume: StructuredResume
    final_score: ATSScoreBreakdown
    export_path: Optional[str]

    # control
    stage: str
    error: Optional[str]
