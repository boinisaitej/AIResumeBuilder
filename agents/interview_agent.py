"""Interview question generator (chunked, ~80 questions with answers).

Generates per-skill Basic / Intermediate / Expert questions plus shared
categories (behavioral, project deep-dive, system design, role-specific).

Strategy:
- One LLM call per top skill (12 Q&A: 4 Basic + 4 Intermediate + 4 Expert)
- One LLM call for shared categories (behavioral + project + sys-design + role)
- Total target: ~80 questions across 6-7 skills + ~30 common
"""
from __future__ import annotations
import json
from typing import Optional
from pydantic import BaseModel, Field
from agents.schemas import (
    InterviewQuestion, SkillQuestions, QuestionCategory, InterviewQuestionSet,
)
from agents.llm import LLMClient
from agents.tracing import traced


# Internal schema only used for the common-categories call
class _CommonQuestionsBlock(BaseModel):
    candidate_summary: str = ""
    target_role:       str = ""
    behavioral:        list[InterviewQuestion] = Field(default_factory=list)
    project_deep_dive: list[InterviewQuestion] = Field(default_factory=list)
    system_design:     list[InterviewQuestion] = Field(default_factory=list)
    role_specific:     list[InterviewQuestion] = Field(default_factory=list)


def _top_skills(profile: dict, max_skills: int = 6) -> list[str]:
    """Pick the candidate's top N skills ranked by experience duration."""
    skills = profile.get("skills", []) or []
    ranked = []
    for s in skills:
        name = (s.get("name") or "").strip()
        if not name:
            continue
        months = int(s.get("years", 0) or 0) * 12 + int(s.get("months", 0) or 0)
        ranked.append((months, name))
    ranked.sort(reverse=True)
    return [n for _, n in ranked][:max_skills]


@traced("interview_agent_skill")
def _generate_for_skill(
    skill: str,
    profile: dict,
    resume_draft: str,
    llm_client: LLMClient,
) -> SkillQuestions:
    """One LLM call → 12 questions for one skill (4 Basic + 4 Intermediate + 4 Expert)."""
    experience = profile.get("experience", [])
    projects   = profile.get("projects", [])

    prompt = f"""You are a senior technical interviewer.
Generate interview questions for the candidate's skill: **{skill}**.

Candidate context:
- Experience: {json.dumps(experience, indent=2)[:1000]}
- Projects:   {json.dumps(projects, indent=2)[:800]}

Resume excerpt (for ground-truth):
{resume_draft[:1500]}

Produce a `SkillQuestions` object for skill="{skill}" with EXACTLY:
- `basic`: 4 questions tagged difficulty="Basic"
       (definitions, syntax, "what does X do?" — answerable in 1-2 min)
- `intermediate`: 4 questions tagged difficulty="Intermediate"
       (use-cases, comparisons, "when would you choose X over Y?" — 2-4 min)
- `expert`: 4 questions tagged difficulty="Expert"
       (deep internals, performance tuning, design trade-offs — 4-6 min)

For EACH question include:
- `question`: clear and specific
- `answer`: a full 3-5 sentence model answer suitable as an interviewer rubric
- `difficulty`: exactly "Basic" / "Intermediate" / "Expert"

Tie questions to the candidate's actual experience and projects where possible.
Do NOT repeat the same question across tiers. Do NOT include questions for any
skill other than "{skill}".
"""
    return llm_client.call_structured(
        prompt,
        SkillQuestions,
        temperature=0.5,
        use_flash_lite=False,
    )


@traced("interview_agent_common")
def _generate_common_categories(
    profile: dict,
    resume_draft: str,
    llm_client: LLMClient,
    target_role_hint: str = "",
) -> _CommonQuestionsBlock:
    """One LLM call → behavioral + project + system-design + role-specific."""
    pi         = profile.get("personal_info", {})
    experience = profile.get("experience", [])
    projects   = profile.get("projects", [])
    jd         = profile.get("job_description", "") or target_role_hint

    prompt = f"""You are a senior technical interviewer assembling the non-skill-specific
portion of an interview kit for this candidate.

CANDIDATE:
- Name : {pi.get('first_name','')} {pi.get('last_name','')}
- Skills: {", ".join(s.get('name','') for s in profile.get('skills',[]) if s.get('name'))[:300]}
- Experience: {json.dumps(experience, indent=2)[:1200]}
- Projects:   {json.dumps(projects, indent=2)[:1000]}

{"TARGET ROLE / JD:" + chr(10) + jd[:600] if jd else ""}

RESUME excerpt (for ground-truth):
{resume_draft[:1500]}

Produce a structured response with:
- `candidate_summary`: one paragraph the interviewer should read before the call
- `target_role`: the role these questions are calibrated for
- `behavioral`: 8 STAR-format questions probing real situations from their experience
- `project_deep_dive`: 8 questions probing 1-2 of their ACTUAL projects (use real names)
   covering design choices, trade-offs, alternatives considered, what they'd do differently
- `system_design`: 6 design questions matched to their domain
   (smaller / simpler ones if junior; complex if senior)
- `role_specific`: 6 questions tightly calibrated to the target role / JD

For EACH question include:
- `question`: specific, answerable in 3-5 minutes
- `answer`: 3-5 sentence model answer the interviewer can use as rubric
- `difficulty`: "Basic" / "Intermediate" / "Expert" — calibrated by seniority

RULES:
- Use the candidate's REAL projects + roles by name in project_deep_dive
- No duplicate questions across categories
- Total target: ~28 questions across the 4 lists
"""
    return llm_client.call_structured(
        prompt,
        _CommonQuestionsBlock,
        temperature=0.5,
        use_flash_lite=False,
    )


@traced("interview_agent")
def generate_interview_questions(
    profile: dict,
    resume_draft: str,
    llm_client: LLMClient,
    target_role: str = "",
    max_skills: int = 6,
    progress_cb=None,
) -> InterviewQuestionSet:
    """Build a full ~80-question interview Q&A set.

    Args:
        profile      : profile dict (personal_info / skills / experience / …)
        resume_draft : resume Markdown OR raw uploaded text for ground-truth
        llm_client   : shared LLM client
        target_role  : optional override (otherwise inferred from JD/experience)
        max_skills   : how many top skills to cover (default 6 → ≈72 skill Qs)
        progress_cb  : optional callable(stage:str, done:int, total:int) for UI updates
    """
    skills = _top_skills(profile, max_skills=max_skills)
    # Fallback: if no skills in profile, ask the model to pick them from the resume
    if not skills:
        skills = _infer_skills_from_resume(resume_draft, llm_client, max_skills=max_skills)

    total_stages = len(skills) + 1   # one call per skill + one for common
    stage = 0

    skill_blocks: list[SkillQuestions] = []
    for s in skills:
        stage += 1
        if progress_cb:
            try: progress_cb(f"Generating {s} questions", stage, total_stages)
            except Exception: pass
        try:
            sq = _generate_for_skill(s, profile, resume_draft, llm_client)
            if sq.skill_name == "" or sq.skill_name.lower() != s.lower():
                sq.skill_name = s   # normalize
            skill_blocks.append(sq)
        except Exception as e:
            # Skip a skill that fails — keep going for the others
            print(f"[interview_agent] skill={s} failed: {e}")

    stage += 1
    if progress_cb:
        try: progress_cb("Generating behavioral + project + role-specific", stage, total_stages)
        except Exception: pass
    common = _generate_common_categories(profile, resume_draft, llm_client, target_role)

    return InterviewQuestionSet(
        candidate_summary=common.candidate_summary,
        target_role=common.target_role or target_role,
        skill_questions=skill_blocks,
        behavioral=common.behavioral,
        project_deep_dive=common.project_deep_dive,
        system_design=common.system_design,
        role_specific=common.role_specific,
    )


# Tiny helper Pydantic schema for extracting skills from raw text when profile is sparse
class _SkillList(BaseModel):
    skills: list[str] = Field(default_factory=list)


def _infer_skills_from_resume(resume_text: str, llm_client: LLMClient, max_skills: int = 6) -> list[str]:
    """When profile has no skills (upload tab), infer top skills from the resume text."""
    if not resume_text.strip():
        return []
    prompt = f"""Extract the top {max_skills} most-prominent TECHNICAL skills from this resume.
Return a list of skill names only (e.g. "Python", "AWS", "React"). Do not invent skills.

RESUME:
{resume_text[:3500]}
"""
    try:
        result = llm_client.call_structured(prompt, _SkillList, temperature=0.1)
        return [s for s in result.skills if s.strip()][:max_skills]
    except Exception:
        return []
