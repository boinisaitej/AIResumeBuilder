"""Agent 4 — ATS Resume Analyzer.

Scores the generated resume on ATS compatibility and produces structured
strengths / weaknesses / improvements. Uses gemini-flash-lite (cheaper + fast).
"""
from __future__ import annotations
from agents.state import ResumeState
from agents.schemas import ATSAnalysis
from agents.tracing import traced


@traced("agent4_resume_analyzer")
def run(state: ResumeState) -> ResumeState:
    llm     = state["llm_client"]
    profile = state["profile_data"]
    jd      = profile.get("job_description", "")

    prompt = f"""You are a certified ATS expert. Score and analyze this resume.

RESUME:
{state.get("resume_draft","")}

{("TARGET JD:" + chr(10) + jd) if jd else "No JD — give general assessment."}

Provide structured analysis:
- `ats_score`: integer 0-100 (be honest, calibrated)
- `strengths`: top 5 things this resume does well
- `weaknesses`: top 5 areas needing improvement
- `keyword_gaps`: ATS keywords missing relative to JD/role
- `improvements`: 5 specific, actionable rewrites
- `verdict`: 1-sentence final assessment
"""

    analysis = llm.call_structured(
        prompt, ATSAnalysis, temperature=0.2, use_flash_lite=True
    )

    md = [
        f"## ATS Score: **{analysis.ats_score}/100**",
        f"\n**Verdict:** {analysis.verdict}",
        "\n## Strengths",
    ]
    for s in analysis.strengths:
        md.append(f"- {s}")
    md.append("\n## Weaknesses")
    for w in analysis.weaknesses:
        md.append(f"- {w}")
    if analysis.keyword_gaps:
        md.append("\n## Keyword Gaps")
        for k in analysis.keyword_gaps:
            md.append(f"- {k}")
    md.append("\n## Improvements")
    for i in analysis.improvements:
        md.append(f"- {i}")

    state["ats_analysis_obj"] = analysis
    state["ats_analysis"]     = "\n".join(md)
    state["ats_score"]        = analysis.ats_score
    return state
