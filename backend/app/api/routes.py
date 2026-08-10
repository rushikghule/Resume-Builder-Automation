import json
import uuid
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pypdf import PdfReader
from docx import Document as DocxDocument

from app.graph.graph import compiled_graph

router = APIRouter()

TEMPLATES_DIR = Path(__file__).resolve().parents[1] / "templates"


def _load_templates() -> list[dict]:
    templates = []
    for f in sorted(TEMPLATES_DIR.glob("*.json")):
        templates.append(json.loads(f.read_text()))
    return templates


def _extract_text_from_upload(file: UploadFile, raw_bytes: bytes) -> str:
    suffix = Path(file.filename).suffix.lower()
    if suffix == ".pdf":
        import io
        reader = PdfReader(io.BytesIO(raw_bytes))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    elif suffix == ".docx":
        import io
        doc = DocxDocument(io.BytesIO(raw_bytes))
        return "\n".join(p.text for p in doc.paragraphs)
    elif suffix == ".txt":
        return raw_bytes.decode("utf-8", errors="ignore")
    else:
        raise HTTPException(400, f"Unsupported file type: {suffix}. Use PDF, DOCX, or TXT.")


@router.get("/templates")
def list_templates():
    """List built-in resume templates for the user to choose from."""
    return _load_templates()


class StartSessionResponse(BaseModel):
    session_id: str


@router.post("/session", response_model=StartSessionResponse)
def start_session():
    return {"session_id": str(uuid.uuid4())}


@router.post("/session/{session_id}/analyze")
async def analyze(
    session_id: str,
    jd_text: str = Form(...),
    llm_provider: str = Form("groq"),
    resume_source: str = Form(...),  # "template" or "upload"
    template_id: Optional[str] = Form(None),
    resume_file: Optional[UploadFile] = File(None),
):
    """
    Run the graph from start through the human-in-the-loop pause point
    (parse_resume -> analyze_jd -> score_baseline -> generate_questions),
    then stop and return the baseline score + clarifying questions.
    """
    config = {"configurable": {"thread_id": session_id}}

    initial_state = {
        "session_id": session_id,
        "jd_raw_text": jd_text,
        "llm_provider": llm_provider,
        "resume_source": resume_source,
    }

    if resume_source == "template":
        if not template_id:
            raise HTTPException(400, "template_id required when resume_source is 'template'")
        templates = {t["id"]: t for t in _load_templates()}
        if template_id not in templates:
            raise HTTPException(404, f"Unknown template_id: {template_id}")
        initial_state["template_id"] = template_id
        initial_state["structured_resume"] = templates[template_id]["resume"]
    elif resume_source == "upload":
        if not resume_file:
            raise HTTPException(400, "resume_file required when resume_source is 'upload'")
        raw_bytes = await resume_file.read()
        text = _extract_text_from_upload(resume_file, raw_bytes)
        if not text.strip():
            raise HTTPException(400, "Could not extract text from uploaded file.")
        initial_state["resume_raw_text"] = text
    else:
        raise HTTPException(400, "resume_source must be 'template' or 'upload'")

    result = compiled_graph.invoke(initial_state, config=config)

    if result.get("error"):
        raise HTTPException(500, result["error"])

    return {
        "session_id": session_id,
        "baseline_score": result.get("baseline_score"),
        "clarifying_questions": result.get("clarifying_questions"),
        "structured_resume": result.get("structured_resume"),
        "structured_jd": result.get("structured_jd"),
    }


class AnswersRequest(BaseModel):
    answers: dict[str, str]  # question id -> answer text


@router.post("/session/{session_id}/answers")
def submit_answers(session_id: str, body: AnswersRequest):
    """
    Resume the graph from the human-in-the-loop pause point with the user's
    answers, running tailor_resume -> score_final -> export to completion.
    """
    config = {"configurable": {"thread_id": session_id}}

    # Update state with answers, then resume by invoking with None input
    # (LangGraph resumes from the last checkpoint when input is None).
    compiled_graph.update_state(config, {"user_answers": body.answers})
    result = compiled_graph.invoke(None, config=config)

    if result.get("error"):
        raise HTTPException(500, result["error"])

    return {
        "session_id": session_id,
        "tailored_resume": result.get("tailored_resume"),
        "baseline_score": result.get("baseline_score"),
        "final_score": result.get("final_score"),
        "export_path": result.get("export_path"),
    }


@router.get("/session/{session_id}/download")
def download_resume(session_id: str):
    config = {"configurable": {"thread_id": session_id}}
    state = compiled_graph.get_state(config)
    export_path = state.values.get("export_path") if state else None

    if not export_path or not Path(export_path).exists():
        raise HTTPException(404, "No exported resume found for this session.")

    return FileResponse(
        export_path,
        filename="Final_Resume.docx",
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
