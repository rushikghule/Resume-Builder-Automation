"""
Resume Parser Agent: turns raw resume text (from an uploaded file) into the
StructuredResume schema. If a template was chosen, the structured data is
already known and this node is a passthrough.
"""
import json
import logging
from langchain_core.messages import SystemMessage, HumanMessage
from app.llm_provider import get_llm_for_provider
from app.graph.state import GraphState

logger = logging.getLogger(__name__)

PARSE_PROMPT = """You are a precise resume parser. Extract structured data from the resume text below.

Return ONLY a JSON object (no markdown fences, no commentary) with this exact shape:
{{
  "name": "...",
  "email": "...",
  "phone": "...",
  "summary": "...",
  "skills": ["...", "..."],
  "experience": [
    {{"title": "...", "company": "...", "start_date": "...", "end_date": "...", "bullets": ["...", "..."]}}
  ],
  "education": [
    {{"degree": "...", "institution": "...", "year": "..."}}
  ]
}}

Rules:
- Only extract information actually present in the text. Do not invent details.
- If a field is missing, use an empty string or empty list.
- Keep bullets as they appear, one string per bullet point.

Resume text:
---
{resume_text}
---
"""


def resume_parser_node(state: GraphState) -> GraphState:
    if state.get("resume_source") == "template":
        # Template resumes are already structured — this node just confirms stage.
        return {**state, "stage": "resume_parsed"}

    raw_text = state.get("resume_raw_text", "")
    if not raw_text.strip():
        return {**state, "error": "No resume text found to parse.", "stage": "error"}

    llm = get_llm_for_provider(state.get("llm_provider", "groq"))
    messages = [
        SystemMessage(content="You are a precise, literal resume parsing assistant."),
        HumanMessage(content=PARSE_PROMPT.format(resume_text=raw_text[:8000])),
    ]

    try:
        response = llm.invoke(messages)
        content = response.content.strip()
        # strip accidental markdown fences
        if content.startswith("```"):
            content = content.strip("`")
            if content.startswith("json"):
                content = content[4:]
        parsed = json.loads(content)
        parsed["raw_text"] = raw_text
    except Exception as e:
        logger.warning("Resume parse failed, falling back to raw text only: %s", e)
        parsed = {"raw_text": raw_text, "name": "", "email": "", "phone": "",
                   "summary": "", "skills": [], "experience": [], "education": []}

    return {**state, "structured_resume": parsed, "stage": "resume_parsed"}
