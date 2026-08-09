"""
Wires all nodes into a single LangGraph StateGraph with a human-in-the-loop
interrupt before the tailoring step, so the frontend can collect answers to
clarifying questions before the graph proceeds.
"""
# NEW
import sqlite3
from pathlib import Path
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver

from app.graph.state import GraphState
from app.graph.nodes.resume_parser import resume_parser_node
from app.graph.nodes.jd_analyzer import jd_analyzer_node
from app.graph.nodes.ats_scorer import baseline_scorer_node, final_scorer_node
from app.graph.nodes.clarifying import clarifying_questions_node
from app.graph.nodes.tailoring import tailoring_node
from app.graph.nodes.export import export_node


def build_graph():
    graph = StateGraph(GraphState)

    graph.add_node("parse_resume", resume_parser_node)
    graph.add_node("analyze_jd", jd_analyzer_node)
    graph.add_node("score_baseline", baseline_scorer_node)
    graph.add_node("generate_questions", clarifying_questions_node)
    graph.add_node("tailor_resume", tailoring_node)
    graph.add_node("score_final", final_scorer_node)
    graph.add_node("export", export_node)

    graph.set_entry_point("parse_resume")
    graph.add_edge("parse_resume", "analyze_jd")
    graph.add_edge("analyze_jd", "score_baseline")
    graph.add_edge("score_baseline", "generate_questions")
    # Graph pauses here (interrupt_after) — frontend collects user_answers,
    # then resumes execution from "tailor_resume".
    graph.add_edge("generate_questions", "tailor_resume")
    graph.add_edge("tailor_resume", "score_final")
    graph.add_edge("score_final", "export")
    graph.add_edge("export", END)

    # NEW
    db_path = Path(__file__).resolve().parents[2] / "checkpoints.db"
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    checkpointer = SqliteSaver(conn)
    return graph.compile(checkpointer=checkpointer, interrupt_after=["generate_questions"])


# Singleton compiled graph, imported by the API layer
compiled_graph = build_graph()
