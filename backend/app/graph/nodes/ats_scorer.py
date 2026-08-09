"""
ATS Scorer Agent: scores a StructuredResume against a StructuredJD using an
explicit, weighted rubric. Combines rule-based checks (keyword overlap,
section completeness, formatting flags) with one LLM call to judge quality
of quantified achievements and title/seniority alignment.

This produces a *proxy* ATS score, not a claim of matching any specific
real-world ATS product's exact algorithm — real systems vary and are
proprietary. The rubric is kept explicit and explainable rather than a
black-box number.
"""
import json
import re
import logging
from langchain_core.messages import SystemMessage, HumanMessage
from app.llm_provider import get_llm_for_provider
from app.graph.state import GraphState

logger = logging.getLogger(__name__)

WEIGHTS = {
    "keyword_overlap_score": 0.40,
    "quantified_achievements_score": 0.20,
    "section_completeness_score": 0.15,
    "formatting_score": 0.15,
    "title_alignment_score": 0.10,
}

QUALITY_PROMPT = """Evaluate this resume against the job description on two dimensions.
Return ONLY a JSON object (no markdown fences):
{{
  "quantified_achievements_score": <0-100, how well experience bullets use numbers/metrics to show impact>,
  "title_alignment_score": <0-100, how well the resume's summary/title matches the JD's seniority/role>,
  "notes": "<2-3 sentence explanation of the biggest gaps>"
}}

Resume summary: {summary}
Resume experience bullets: {bullets}
JD title/seniority: {jd_title} / {jd_seniority}
"""


def _keyword_overlap(resume_skills: list[str], resume_text: str, jd_required: list[str], jd_phrases: list[str]) -> tuple[float, list[str], list[str]]:
    """Case-insensitive substring match of JD required skills + key phrases against resume content."""
    haystack = (resume_text + " " + " ".join(resume_skills)).lower()
    all_targets = list(dict.fromkeys(jd_required + jd_phrases))  # dedupe, preserve order
    if not all_targets:
        return 100.0, [], []

    matched, missing = [], []
    for term in all_targets:
        pattern = re.escape(term.lower())
        if re.search(pattern, haystack):
            matched.append(term)
        else:
            missing.append(term)

    score = (len(matched) / len(all_targets)) * 100
    return round(score, 1), matched, missing


def _section_completeness(resume: dict) -> float:
    sections = ["name", "email", "summary", "skills", "experience", "education"]
    present = sum(1 for s in sections if resume.get(s))
    return round((present / len(sections)) * 100, 1)


def _formatting_score(resume: dict) -> float:
    """Since we control both templates and parsed structure, formatting risk here
    is mainly about whether parsing succeeded cleanly (proxy for 'ATS could read it')."""
    score = 100.0
    if not resume.get("raw_text") and not resume.get("experience"):
        score -= 40
    if not resume.get("skills"):
        score -= 20
    return max(score, 0.0)


def ats_scorer_node(state: GraphState, target_field: str = "baseline_score", resume_field: str = "structured_resume") -> GraphState:
    resume = state.get(resume_field, {})
    jd = state.get("structured_jd", {})

    kw_score, matched, missing = _keyword_overlap(
        resume.get("skills", []),
        resume.get("raw_text", "") + " " + json.dumps(resume.get("experience", [])),
        jd.get("required_skills", []),
        jd.get("key_phrases", []),
    )
    section_score = _section_completeness(resume)
    format_score = _formatting_score(resume)

    # LLM-assisted quality judgment
    llm = get_llm_for_provider(state.get("llm_provider", "groq"))
    bullets = []
    for exp in resume.get("experience", []):
        bullets.extend(exp.get("bullets", []))

    quant_score, title_score, notes = 50.0, 50.0, ""
    try:
        messages = [
            SystemMessage(content="You are a strict, consistent resume evaluator."),
            HumanMessage(content=QUALITY_PROMPT.format(
                summary=resume.get("summary", ""),
                bullets=json.dumps(bullets[:10]),
                jd_title=jd.get("title", ""),
                jd_seniority=jd.get("seniority", ""),
            )),
        ]
        response = llm.invoke(messages)
        content = response.content.strip()
        if content.startswith("```"):
            content = content.strip("`")
            if content.startswith("json"):
                content = content[4:]
        parsed = json.loads(content)
        quant_score = float(parsed.get("quantified_achievements_score", 50))
        title_score = float(parsed.get("title_alignment_score", 50))
        notes = parsed.get("notes", "")
    except Exception as e:
        logger.warning("ATS quality LLM scoring failed, using defaults: %s", e)

    breakdown = {
        "keyword_overlap_score": kw_score,
        "quantified_achievements_score": quant_score,
        "section_completeness_score": section_score,
        "formatting_score": format_score,
        "title_alignment_score": title_score,
        "matched_keywords": matched,
        "missing_keywords": missing,
        "notes": notes,
    }
    total = sum(breakdown[k] * WEIGHTS[k] for k in WEIGHTS)
    breakdown["total_score"] = round(total, 1)

    return {**state, target_field: breakdown, "stage": f"{target_field}_computed"}


def baseline_scorer_node(state: GraphState) -> GraphState:
    return ats_scorer_node(state, target_field="baseline_score", resume_field="structured_resume")


def final_scorer_node(state: GraphState) -> GraphState:
    return ats_scorer_node(state, target_field="final_score", resume_field="tailored_resume")
