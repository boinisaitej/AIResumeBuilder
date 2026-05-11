"""Agent 1 — Skill Intake & Categorization.

Takes raw skills + experience and groups them into canonical resume buckets
with proficiency levels. Uses structured Pydantic output (no regex parsing).
"""
from __future__ import annotations
import json
from agents.state import ResumeState
from agents.schemas import SkillCategorization
from agents.tracing import traced


@traced("agent1_skill_intake")
def run(state: ResumeState) -> ResumeState:
    llm = state["llm_client"]
    profile = state["profile_data"]
    skills = profile.get("skills", [])
    experience = profile.get("experience", [])

    skill_lines = "\n".join(
        f"- {s['name']}: {s.get('years',0)}y {s.get('months',0)}m"
        for s in skills if s.get("name")
    ) or "No skills provided."

    prompt = f"""You are a technical skill categorization expert.

Candidate's raw skills with experience duration:
{skill_lines}

Work experience context (for inferring level appropriateness):
{json.dumps(experience, indent=2)[:1500]}

Categorize EACH skill into exactly one of these buckets:
- programming_languages    (Python, Java, Go, TypeScript, etc.)
- frameworks_libraries     (React, Django, Spring, PyTorch, etc.)
- databases                (PostgreSQL, MongoDB, Redis, etc.)
- cloud_devops             (AWS, Docker, Kubernetes, Terraform, etc.)
- ml_ai_data               (TensorFlow, LangChain, Pandas, scikit-learn, etc.)
- tools_software           (Git, Jira, Linux, VS Code, etc.)
- other                    (anything that doesn't fit cleanly)

For each skill also assign a level based on duration:
- 0-6 months          → "Beginner"
- 6 months - 2 years  → "Intermediate"
- 2+ years            → "Expert"

Rules:
- Only include skills the candidate explicitly provided.
- Do not invent skills.
- Every skill must appear in exactly one category.
- Return populated `skill_levels` map for ALL skills.
"""

    cat = llm.call_structured(prompt, SkillCategorization, temperature=0.1)

    state["categorization"]     = cat
    state["categorized_skills"] = cat.to_markdown()
    state["skill_level_map"]    = cat.skill_levels
    return state
