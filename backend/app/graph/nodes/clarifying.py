"""
Generates 2-4 targeted clarifying questions based on the baseline ATS score's
missing keywords, so the human can confirm relevant experience before the
Tailoring Agent rewrites anything. This node does NOT interrupt the graph
itself — the FastAPI layer handles pausing after this node returns and
resuming once answers arrive (see api/routes.py).
"""
import json
import logging
from langchain_core.messages import SystemMessage, HumanMessage
from app.llm_provider import get_llm_for_provider
from app.graph.state import GraphState

logger = logging.getLogger(__name__)

QUESTIONS_PROMPT = """Based on the missing keywords/skills below, write 2-4 short, specific
clarifying questions to ask the candidate. Each question should help uncover whether they
actually have relevant (even informal/transferable) experience for that gap, so we never
invent experience they don't have.

Return ONLY a JSON array (no markdown fences):
[
  {{"id": "q1", "question": "...", "related_gap": "<the missing keyword/skill>"}},
  ...
]

Missing keywords/skills: {missing}
Resume summary for context: {summary}
"""


def clarifying_questions_node(state: GraphState) -> GraphState:
    baseline = state.get("baseline_score", {})
    missing = baseline.get("missing_keywords", [])[:8]

    if not missing:
        return {**state, "clarifying_questions": [], "stage": "questions_ready"}

    llm = get_llm_for_provider(state.get("llm_provider", "groq"))
    resume = state.get("structured_resume", {})

    try:
        messages = [
            SystemMessage(content="You write concise, specific clarifying questions for a resume assistant."),
            HumanMessage(content=QUESTIONS_PROMPT.format(
                missing=json.dumps(missing),
                summary=resume.get("summary", ""),
            )),
        ]
        response = llm.invoke(messages)
        content = response.content.strip()
        if content.startswith("```"):
            content = content.strip("`")
            if content.startswith("json"):
                content = content[4:]
        questions = json.loads(content)
    except Exception as e:
        logger.warning("Clarifying question generation failed, using fallback: %s", e)
        questions = [
            {"id": f"q{i+1}", "question": f"Do you have any experience with '{term}', even informal or academic?", "related_gap": term}
            for i, term in enumerate(missing[:4])
        ]

    return {**state, "clarifying_questions": questions, "stage": "questions_ready"}
