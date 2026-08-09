"""
JD Analyzer Agent: extracts structured requirements from a pasted job
description — required skills, nice-to-haves, seniority, key phrases.
"""
import json
import logging
from langchain_core.messages import SystemMessage, HumanMessage
from app.llm_provider import get_llm_for_provider
from app.graph.state import GraphState

logger = logging.getLogger(__name__)

JD_PROMPT = """You are a precise job-description analyzer. Extract structured requirements from the JD below.

Return ONLY a JSON object (no markdown fences, no commentary) with this exact shape:
{{
  "title": "...",
  "seniority": "junior|mid|senior|lead|unclear",
  "required_skills": ["...", "..."],
  "nice_to_have_skills": ["...", "..."],
  "key_phrases": ["...", "..."]
}}

Rules:
- required_skills: hard requirements explicitly stated (technologies, tools, certifications, years of experience).
- nice_to_have_skills: things listed as "preferred", "bonus", or "plus".
- key_phrases: important recurring terms/phrases an ATS keyword scan would look for (5-15 items).
- Be literal — only include what's actually in the text.

Job description:
---
{jd_text}
---
"""


def jd_analyzer_node(state: GraphState) -> GraphState:
    jd_text = state.get("jd_raw_text", "")
    if not jd_text.strip():
        return {**state, "error": "No job description provided.", "stage": "error"}

    llm = get_llm_for_provider(state.get("llm_provider", "groq"))
    messages = [
        SystemMessage(content="You are a precise job description analysis assistant."),
        HumanMessage(content=JD_PROMPT.format(jd_text=jd_text[:8000])),
    ]

    try:
        response = llm.invoke(messages)
        content = response.content.strip()
        if content.startswith("```"):
            content = content.strip("`")
            if content.startswith("json"):
                content = content[4:]
        parsed = json.loads(content)
        parsed["raw_text"] = jd_text
    except Exception as e:
        logger.warning("JD parse failed, falling back to minimal structure: %s", e)
        parsed = {"raw_text": jd_text, "title": "", "seniority": "unclear",
                   "required_skills": [], "nice_to_have_skills": [], "key_phrases": []}

    return {**state, "structured_jd": parsed, "stage": "jd_parsed"}
