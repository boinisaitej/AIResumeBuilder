"""Agent 5 — GitHub README Generator.

Produces a polished GitHub profile README from the categorized skills,
analysis, and resume draft. Free-form Markdown output.
"""
from __future__ import annotations
import json
from agents.state import ResumeState
from agents.tracing import traced


@traced("agent5_readme_generator")
def run(state: ResumeState) -> ResumeState:
    llm     = state["llm_client"]
    profile = state["profile_data"]
    pi      = profile.get("personal_info", {})
    name    = f"{pi.get('first_name','')} {pi.get('last_name','')}".strip()

    domain = ""
    if state.get("skill_analysis_obj"):
        domain = state["skill_analysis_obj"].domain_assessment

    prompt = f"""Create a polished, recruiter-friendly GitHub profile README for this developer.

Developer: {name}
Email   : {pi.get('email','')}
LinkedIn: {pi.get('linkedin','')}
GitHub  : {pi.get('github','')}
Location: {pi.get('location','')}
Domain  : {domain}

Categorized skills:
{state.get("categorized_skills","")[:1200]}

Skill analysis (for context):
{state.get("skill_analysis","")[:800]}

Projects:
{json.dumps(profile.get('projects', []), indent=2)[:1200]}

ATS summary:
{state.get("ats_analysis","")[:400]}

Produce a README.md with:
1. Headline with role/specialization
2. About Me (2-3 sentences)
3. Tech Stack table — categorized
4. GitHub stats placeholder badges (shields.io syntax)
5. Featured Projects (3-5)
6. Currently Learning section
7. 12-month learning roadmap (3 horizons)
8. Roles I'm targeting
9. Contact section with all links

Style: emojis throughout, shields.io badge markdown, tables for skills,
section dividers. Output the README markdown only — no commentary.
"""

    state["readme_content"] = llm.call(prompt, temperature=0.4)
    return state
