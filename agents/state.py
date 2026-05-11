"""Shared state object flowing through the LangGraph pipeline."""
from typing import TypedDict, Any, Optional
from agents.schemas import (
    SkillCategorization,
    SkillAnalysis,
    JDMatchAnalysis,
    ATSAnalysis,
    SkillRoadmap,
)


class ResumeState(TypedDict, total=False):
    # Inputs
    profile_data: dict           # personal_info, education, experience, skills, projects, certifications, job_description
    llm_client:   Any            # agents.llm.LLMClient instance — passed in, not serialized

    # Agent 1 outputs
    categorization:      Optional[SkillCategorization]
    categorized_skills:  str     # Markdown rendering for downstream prompts
    skill_level_map:     dict

    # Agent 2 outputs
    skill_analysis_obj:  Optional[SkillAnalysis]
    skill_analysis:      str
    jd_analysis_obj:     Optional[JDMatchAnalysis]
    jd_analysis:         str
    retrieved_jds:       list    # RAG context (list of dicts)

    # Agent 3 outputs
    resume_draft:        str

    # Agent 4 outputs
    ats_analysis_obj:    Optional[ATSAnalysis]
    ats_analysis:        str
    ats_score:           int

    # Agent 5 outputs
    readme_content:      str

    # Agent 6 outputs
    roadmap_obj:         Optional[SkillRoadmap]
    skill_suggestions:   str
    roadmap_text:        str
    roadmap_parsed:      list

    # Error tracking
    error:               str
