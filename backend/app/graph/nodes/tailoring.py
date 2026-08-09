"""
Resume Tailoring Agent: rewrites/reorders the resume's summary, skills, and
experience bullets to better match the JD, using the human's answers to
clarifying questions as the ONLY source of new information. It must never
invent experience, tools, or achievements the candidate hasn't confirmed.
"""
import json
import logging
from langchain_core.messages import SystemMessage, HumanMessage
from app.llm_provider import get_llm_for_provider
from app.graph.state import GraphState

logger = logging.getLogger(__name__)

TAILOR_PROMPT = """You are tailoring a resume to better match a job description. You must be
completely truthful — only use information already in the original resume or explicitly
confirmed by the candidate's answers below. NEVER invent skills, tools, employers, or
achievements that aren't grounded in this material.

Original resume (JSON):
{resume}

Job description key requirements: {jd_skills}
Job title/seniority: {jd_title} / {jd_seniority}

Candidate's answers to clarifying questions (use ONLY if they confirm real experience):
{answers}

Rewrite the resume to:
1. Emphasize relevant existing experience using language/keywords that align with the JD.
2. Incorporate anything the candidate confirmed in their answers, worded naturally.
3. Reorder skills/bullets to lead with what's most relevant to this JD.
4. Keep it truthful — if an answer says "no" or doesn't confirm real experience, do not add that skill.

Return ONLY a JSON object in the exact same shape as the original resume:
{{
  "name": "...", "email": "...", "phone": "...", "summary": "...",
  "skills": ["..."],
  "experience": [{{"title": "...", "company": "...", "start_date": "...", "end_date": "...", "bullets": ["..."]}}],
  "education": [{{"degree": "...", "institution": "...", "year": "..."}}]
}}
"""


def tailoring_node(state: GraphState) -> GraphState:
    resume = state.get("structured_resume", {})
    jd = state.get("structured_jd", {})
    answers = state.get("user_answers", {})
    questions = state.get("clarifying_questions", [])

    # Pair question text with the answer for readability in the prompt
    qa_pairs = []
    for q in questions:
        ans = answers.get(q.get("id", ""), "")
        if ans:
            qa_pairs.append(f"Q: {q.get('question')}\nA: {ans}")
    qa_text = "\n\n".join(qa_pairs) if qa_pairs else "(no answers provided)"

    llm = get_llm_for_provider(state.get("llm_provider", "groq"))
    messages = [
        SystemMessage(content="You are a truthful, precise resume tailoring assistant. Never fabricate experience."),
        HumanMessage(content=TAILOR_PROMPT.format(
            resume=json.dumps(resume, indent=2)[:6000],
            jd_skills=json.dumps(jd.get("required_skills", []) + jd.get("nice_to_have_skills", [])),
            jd_title=jd.get("title", ""),
            jd_seniority=jd.get("seniority", ""),
            answers=qa_text,
        )),
    ]

    try:
        response = llm.invoke(messages)
        content = response.content.strip()
        if content.startswith("```"):
            content = content.strip("`")
            if content.startswith("json"):
                content = content[4:]
        tailored = json.loads(content)
        tailored["raw_text"] = resume.get("raw_text", "")
    except Exception as e:
        logger.warning("Tailoring failed, falling back to original resume: %s", e)
        tailored = resume

    return {**state, "tailored_resume": tailored, "stage": "tailored"}
