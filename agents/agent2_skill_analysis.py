"""Agent 2 — Skill Analysis (RAG-augmented).

Analyzes the candidate's profile against retrieved similar job descriptions
from the JD corpus. Produces structured SkillAnalysis + optional JDMatch.
"""
from __future__ import annotations
import json
from agents.state import ResumeState
from agents.schemas import SkillAnalysis, JDMatchAnalysis
from agents.rag import retrieve_similar_jds, format_jds_for_prompt
from agents.tracing import traced


@traced("agent2_skill_analysis")
def run(state: ResumeState) -> ResumeState:
    llm     = state["llm_client"]
    profile = state["profile_data"]
    jd      = profile.get("job_description", "").strip()

    # ── RAG: retrieve similar JDs from the corpus ──────────────────────────────
    skill_names = [s.get("name","") for s in profile.get("skills",[]) if s.get("name")]
    rag_query   = jd if jd else "Candidate skills: " + ", ".join(skill_names)
    api_key     = (llm._next_key() or "") if hasattr(llm, "_next_key") else ""
    hits        = retrieve_similar_jds(rag_query, api_key=api_key, k=4)
    rag_block   = format_jds_for_prompt(hits)
    state["retrieved_jds"] = hits

    # ── Structured skill analysis ──────────────────────────────────────────────
    prompt = f"""You are a senior technical recruiter and career strategist.

Candidate's categorized skill profile:
{state.get("categorized_skills","")}

Skill levels:
{json.dumps(state.get("skill_level_map", {}), indent=2)}

Work experience:
{json.dumps(profile.get("experience", []), indent=2)[:1500]}

{("Target JD:" + chr(10) + jd) if jd else ""}

{rag_block}

Provide a comprehensive structured analysis:
- `domain_assessment`: which technical domain this candidate belongs to (e.g. Full Stack, ML/AI, DevOps)
- `skill_gap_analysis`: critical missing skills given the retrieved JDs + target role
- `market_relevance`: per-skill demand rating (High/Medium/Low for 2025-2026)
- `top_5_skills_to_learn`: prioritized list
- `eligible_roles`: 6-8 specific roles candidate can apply for NOW with match % and reasoning
"""

    analysis = llm.call_structured(prompt, SkillAnalysis, temperature=0.3)

    # ── Render markdown for downstream prompts + UI ─────────────────────────────
    md_parts = [
        f"## Domain Assessment\n{analysis.domain_assessment}",
        f"\n## Skill Gap Analysis\n{analysis.skill_gap_analysis}",
        "\n## Market Relevance 2025-2026",
    ]
    for sk, rel in analysis.market_relevance.items():
        md_parts.append(f"- **{sk}**: {rel}")
    md_parts.append("\n## Top 5 Skills to Learn Next")
    for s in analysis.top_5_skills_to_learn:
        md_parts.append(f"- {s}")
    md_parts.append("\n## Eligible Roles Right Now")
    for r in analysis.eligible_roles:
        md_parts.append(f"- **{r.role}** ({r.match_percent}%) — {r.why}")

    state["skill_analysis_obj"] = analysis
    state["skill_analysis"]     = "\n".join(md_parts)

    # ── Optional JD match (structured) ─────────────────────────────────────────
    if jd:
        jd_prompt = f"""Analyze this JD against the candidate's skills:

JD:
{jd[:2000]}

Candidate skills:
{state.get("categorized_skills","")}

Return structured JD-match analysis with:
- `skills_present`: which JD-required skills the candidate has
- `skills_missing`: required skills NOT in the candidate profile
- `ats_keywords_to_embed`: keywords to weave into the resume naturally
- `match_percent`: overall fit 0-100
- `recommended_tone`: resume tone for this company type
- `critical_gaps`: urgent missing skills to address
"""
        jd_obj = llm.call_structured(jd_prompt, JDMatchAnalysis, temperature=0.2)
        state["jd_analysis_obj"] = jd_obj
        md = [
            f"**Overall Match: {jd_obj.match_percent}%**",
            f"\n**Recommended tone:** {jd_obj.recommended_tone}",
            "\n**Skills present:** " + ", ".join(jd_obj.skills_present),
            "\n**Skills missing:** " + ", ".join(jd_obj.skills_missing),
            "\n**ATS keywords to embed:** " + ", ".join(jd_obj.ats_keywords_to_embed),
            "\n**Critical gaps:**",
        ]
        for g in jd_obj.critical_gaps:
            md.append(f"- {g}")
        state["jd_analysis"] = "\n".join(md)
    else:
        state["jd_analysis_obj"] = None
        state["jd_analysis"]     = ""

    return state
