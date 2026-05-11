"""Agent 3 — Resume Writer.

Generates the resume Markdown using the categorized skills from Agent 1 and
the analysis + JD match from Agent 2. Free-form Markdown output (templates
expect Markdown).
"""
from __future__ import annotations
import json
from agents.state import ResumeState
from agents.tracing import traced


@traced("agent3_resume_generation")
def run(state: ResumeState) -> ResumeState:
    llm     = state["llm_client"]
    profile = state["profile_data"]
    pi      = profile.get("personal_info", {})
    jd      = profile.get("job_description", "")

    cat = state.get("categorization")
    skill_lines = cat.resume_skill_lines() if cat else []
    skill_block = "\n".join(skill_lines) if skill_lines else "None."

    jd_obj = state.get("jd_analysis_obj")
    ats_keywords = []
    if jd_obj is not None:
        ats_keywords = jd_obj.ats_keywords_to_embed

    prompt = f"""You are an expert resume writer with 15+ years of experience.
Write a complete, ATS-optimized resume in clean Markdown.

CANDIDATE:
Full Name : {pi.get('first_name','')} {pi.get('last_name','')}
Location  : {pi.get('location','')}
Mobile    : {pi.get('mobile','')}
Email     : {pi.get('email','')}
LinkedIn  : {pi.get('linkedin','')}
GitHub    : {pi.get('github','')}

EDUCATION:
{json.dumps(profile.get('education', []), indent=2)}

WORK EXPERIENCE:
{json.dumps(profile.get('experience', []), indent=2)}

TECHNICAL SKILLS (use EXACTLY these grouped lines, do not modify):
{skill_block}

PROJECTS:
{json.dumps(profile.get('projects', []), indent=2)}

CERTIFICATIONS:
{json.dumps(profile.get('certifications', []), indent=2)}

{"OPTIMIZE FOR THIS JD (embed keywords naturally):" + chr(10) + jd[:600] if jd else ""}
{("ATS KEYWORDS TO EMBED: " + ", ".join(ats_keywords)) if ats_keywords else ""}

NON-NEGOTIABLE RULES:
1. NEVER print "Beginner" / "Intermediate" / "Expert" anywhere.
2. NEVER invent skills not in the input.
3. Use EXACTLY the technical-skills lines above.
4. Skip empty sections entirely — no heading if no content.
5. LinkedIn URL → hyperlink text "LinkedIn". GitHub → "GitHub". Project links → "View Project".
6. Action verbs: Led, Built, Engineered, Optimized, Delivered, Spearheaded.
7. Quantify achievements where possible.
8. Section ORDER: ## Summary → ## Experience → ## Education → ## Technical Skills → ## Projects → ## Certifications
9. Output Markdown ONLY — no meta-commentary, no preamble, no code-fence wrappers.
"""

    state["resume_draft"] = llm.call(prompt, temperature=0.3)
    return state
