"""LangGraph DAG wiring all 6 agents.

Exposes:
  - `build_graph()`       → compiled StateGraph (used by evals + app)
  - `run_pipeline(...)`   → blocking invocation returning final state
  - `stream_pipeline(...)`→ generator yielding (node_name, state) per node

The streaming variant powers the live UI in app.py — each agent's completion
fires an event so the workflow card updates in real time.
"""
from __future__ import annotations
from typing import Iterator
from langgraph.graph import StateGraph, END

from agents.state import ResumeState
from agents.llm import LLMClient
from agents import (
    agent1_skill_intake,
    agent2_skill_analysis,
    agent3_resume_generation,
    agent4_resume_analyzer,
    agent5_readme_generator,
    agent6_skill_suggestions,
)


NODES = [
    ("agent1_skill_intake",      agent1_skill_intake.run),
    ("agent2_skill_analysis",    agent2_skill_analysis.run),
    ("agent3_resume_generation", agent3_resume_generation.run),
    ("agent4_resume_analyzer",   agent4_resume_analyzer.run),
    ("agent5_readme_generator",  agent5_readme_generator.run),
    ("agent6_skill_suggestions", agent6_skill_suggestions.run),
]


def build_graph():
    g = StateGraph(ResumeState)
    for name, fn in NODES:
        g.add_node(name, fn)
    g.set_entry_point(NODES[0][0])
    for i in range(len(NODES) - 1):
        g.add_edge(NODES[i][0], NODES[i + 1][0])
    g.add_edge(NODES[-1][0], END)
    return g.compile()


def _initial_state(profile_data: dict, llm_client: LLMClient) -> ResumeState:
    return {
        "profile_data":        profile_data,
        "llm_client":          llm_client,
        "categorization":      None,
        "categorized_skills":  "",
        "skill_level_map":     {},
        "skill_analysis_obj":  None,
        "skill_analysis":      "",
        "jd_analysis_obj":     None,
        "jd_analysis":         "",
        "retrieved_jds":       [],
        "resume_draft":        "",
        "ats_analysis_obj":    None,
        "ats_analysis":        "",
        "ats_score":           0,
        "readme_content":      "",
        "roadmap_obj":         None,
        "skill_suggestions":   "",
        "roadmap_text":        "",
        "roadmap_parsed":      [],
        "error":               "",
    }


def run_pipeline(profile_data: dict, llm_client: LLMClient) -> ResumeState:
    """Blocking run — used by evals + non-streaming callers."""
    graph   = build_graph()
    initial = _initial_state(profile_data, llm_client)
    return graph.invoke(initial)


def stream_pipeline(
    profile_data: dict,
    llm_client: LLMClient,
) -> Iterator[tuple[str, ResumeState]]:
    """Yield (node_name, accumulated_state) after each agent completes.

    Used by app.py to update the workflow UI live as each agent finishes.
    """
    graph   = build_graph()
    initial = _initial_state(profile_data, llm_client)
    accumulated: dict = dict(initial)

    for event in graph.stream(initial, stream_mode="updates"):
        # `event` is {node_name: partial_state_update}
        for node_name, node_update in event.items():
            if isinstance(node_update, dict):
                accumulated.update(node_update)
            yield node_name, accumulated  # type: ignore[misc]
