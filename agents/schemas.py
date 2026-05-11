"""Pydantic schemas for structured LLM outputs.

Each agent returns a strongly-typed Pydantic model instead of free-form text
parsed with regex. This makes the pipeline reliable, testable, and lets us
validate the contract between agents.
"""
from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field


# ─────────────────────────────────────────────────────────────────────────────
# Agent 1 — Skill Intake / Categorization
# ─────────────────────────────────────────────────────────────────────────────
class SkillCategorization(BaseModel):
    """Skills grouped into resume categories + proficiency map."""
    programming_languages: list[str] = Field(default_factory=list)
    frameworks_libraries: list[str] = Field(default_factory=list)
    databases: list[str] = Field(default_factory=list)
    cloud_devops: list[str] = Field(default_factory=list)
    ml_ai_data: list[str] = Field(default_factory=list)
    tools_software: list[str] = Field(default_factory=list)
    other: list[str] = Field(default_factory=list)
    skill_levels: dict[str, str] = Field(
        default_factory=dict,
        description="Map of skill name to 'Beginner' / 'Intermediate' / 'Expert'",
    )

    def to_markdown(self) -> str:
        groups = [
            ("Programming Languages", self.programming_languages),
            ("Frameworks & Libraries", self.frameworks_libraries),
            ("Databases", self.databases),
            ("Cloud & DevOps", self.cloud_devops),
            ("ML / AI / Data Science", self.ml_ai_data),
            ("Tools & Software", self.tools_software),
            ("Other", self.other),
        ]
        out = []
        for name, items in groups:
            if items:
                out.append(f"**{name}:**")
                for sk in items:
                    lvl = self.skill_levels.get(sk, "")
                    suffix = f" [{lvl}]" if lvl else ""
                    out.append(f"- {sk}{suffix}")
                out.append("")
        return "\n".join(out)

    def resume_skill_lines(self) -> list[str]:
        groups = [
            ("Programming Languages", self.programming_languages),
            ("Frameworks & Libraries", self.frameworks_libraries),
            ("Databases", self.databases),
            ("Cloud & DevOps", self.cloud_devops),
            ("ML / AI / Data Science", self.ml_ai_data),
            ("Tools & Software", self.tools_software),
            ("Other", self.other),
        ]
        return [f"{name}: {', '.join(items)}" for name, items in groups if items]


# ─────────────────────────────────────────────────────────────────────────────
# Agent 2 — Skill Analysis
# ─────────────────────────────────────────────────────────────────────────────
class EligibleRole(BaseModel):
    role: str
    match_percent: int = Field(ge=0, le=100)
    why: str


class SkillAnalysis(BaseModel):
    domain_assessment: str = Field(description="Technical domain (e.g. Full Stack, ML/AI, DevOps)")
    skill_gap_analysis: str
    market_relevance: dict[str, str] = Field(
        default_factory=dict,
        description="Skill name -> 'High Demand' / 'Medium Demand' / 'Low Demand'",
    )
    top_5_skills_to_learn: list[str] = Field(default_factory=list)
    eligible_roles: list[EligibleRole] = Field(default_factory=list)


class JDMatchAnalysis(BaseModel):
    skills_present: list[str] = Field(default_factory=list)
    skills_missing: list[str] = Field(default_factory=list)
    ats_keywords_to_embed: list[str] = Field(default_factory=list)
    match_percent: int = Field(ge=0, le=100, default=0)
    recommended_tone: str = ""
    critical_gaps: list[str] = Field(default_factory=list)


# ─────────────────────────────────────────────────────────────────────────────
# Agent 4 — ATS Analysis
# ─────────────────────────────────────────────────────────────────────────────
class ATSAnalysis(BaseModel):
    ats_score: int = Field(ge=0, le=100, description="Overall ATS compatibility 0-100")
    strengths: list[str] = Field(default_factory=list, description="Top 5 strengths")
    weaknesses: list[str] = Field(default_factory=list, description="Top 5 weaknesses")
    keyword_gaps: list[str] = Field(default_factory=list)
    improvements: list[str] = Field(default_factory=list, description="Top 5 actionable improvements")
    verdict: str = ""


# ─────────────────────────────────────────────────────────────────────────────
# Agent 6 — Skill Suggestions / Roadmap
# ─────────────────────────────────────────────────────────────────────────────
class RoadmapPhase(BaseModel):
    phase: str = Field(description="e.g. 'Month 1-3 (Foundation)'")
    items: list[str] = Field(default_factory=list)


class SkillRoadmap(BaseModel):
    domain: str = ""
    eligible_roles_now: list[EligibleRole] = Field(default_factory=list)
    skills_unlock_roles: list[str] = Field(
        default_factory=list,
        description="Format: 'Learn X (est Y weeks) → Unlocks: Role1, Role2'",
    )
    cross_domain_opportunities: str = ""
    phases: list[RoadmapPhase] = Field(default_factory=list, description="3-month / 6-month / 12-month plan")
    top_certifications: list[str] = Field(default_factory=list)
    quick_wins: list[str] = Field(default_factory=list, description="3 quick wins this week")


# ─────────────────────────────────────────────────────────────────────────────
# Resume extraction (uploaded PDF → structured profile)
# ─────────────────────────────────────────────────────────────────────────────
class ExtractedPersonalInfo(BaseModel):
    first_name: str = ""
    last_name:  str = ""
    email:      str = ""
    mobile:     str = ""
    location:   str = ""
    linkedin:   str = ""
    github:     str = ""


class ExtractedEducation(BaseModel):
    degree:     str = ""
    college:    str = ""
    score:      str = ""
    start_date: str = ""
    end_date:   str = ""
    location:   str = ""


class ExtractedExperience(BaseModel):
    company:     str = ""
    role:        str = ""
    start_date:  str = ""
    end_date:    str = ""
    description: str = ""


class ExtractedSkill(BaseModel):
    name:   str = ""
    years:  int = 0
    months: int = 0


class ExtractedProject(BaseModel):
    name:        str = ""
    skills_used: str = ""
    start_date:  str = ""
    end_date:    str = ""
    link:        str = ""
    summary:     str = ""


class ExtractedCertification(BaseModel):
    name: str = ""
    date: str = ""
    link: str = ""


class ResumeExtraction(BaseModel):
    """Full structured extraction of an uploaded resume's content."""
    personal_info:  ExtractedPersonalInfo            = Field(default_factory=ExtractedPersonalInfo)
    education:      list[ExtractedEducation]         = Field(default_factory=list)
    experience:     list[ExtractedExperience]        = Field(default_factory=list)
    skills:         list[ExtractedSkill]             = Field(default_factory=list)
    projects:       list[ExtractedProject]           = Field(default_factory=list)
    certifications: list[ExtractedCertification]     = Field(default_factory=list)

    def to_profile(self) -> dict:
        """Convert to the dict shape the rest of the pipeline expects."""
        return {
            "personal_info":  self.personal_info.model_dump(),
            "education":      [e.model_dump() for e in self.education],
            "experience":     [x.model_dump() for x in self.experience],
            "skills":         [s.model_dump() for s in self.skills],
            "projects":       [p.model_dump() for p in self.projects],
            "certifications": [c.model_dump() for c in self.certifications],
            "job_description":"",
        }

    def missing_sections(self) -> list[str]:
        """Return a list of high-level section names that are empty/missing."""
        missing: list[str] = []
        pi = self.personal_info
        if not (pi.first_name or pi.last_name): missing.append("Name")
        if not pi.email:    missing.append("Email")
        if not pi.mobile:   missing.append("Mobile")
        if not pi.location: missing.append("Location")
        if not self.education:      missing.append("Education")
        if not self.experience:     missing.append("Experience")
        if not self.skills:         missing.append("Skills")
        if not self.projects:       missing.append("Projects")
        return missing


# ─────────────────────────────────────────────────────────────────────────────
# Interview question generator (per-skill Basic/Intermediate/Expert tiers)
# ─────────────────────────────────────────────────────────────────────────────
class InterviewQuestion(BaseModel):
    question:   str
    answer:     str = Field(description="Full 3-5 sentence model answer the interviewer can use as a rubric.")
    difficulty: str = Field(description="'Basic' / 'Intermediate' / 'Expert'")


class SkillQuestions(BaseModel):
    """Per-skill bucket with three difficulty tiers."""
    skill_name:   str
    basic:        list[InterviewQuestion] = Field(default_factory=list)
    intermediate: list[InterviewQuestion] = Field(default_factory=list)
    expert:       list[InterviewQuestion] = Field(default_factory=list)

    def total(self) -> int:
        return len(self.basic) + len(self.intermediate) + len(self.expert)


class QuestionCategory(BaseModel):
    """Generic category for behavioral / project / system-design / role-specific."""
    title:     str
    questions: list[InterviewQuestion] = Field(default_factory=list)


class InterviewQuestionSet(BaseModel):
    candidate_summary: str = ""
    target_role:       str = ""
    skill_questions:        list[SkillQuestions]   = Field(default_factory=list)
    behavioral:             list[InterviewQuestion] = Field(default_factory=list)
    project_deep_dive:      list[InterviewQuestion] = Field(default_factory=list)
    system_design:          list[InterviewQuestion] = Field(default_factory=list)
    role_specific:          list[InterviewQuestion] = Field(default_factory=list)

    def total_questions(self) -> int:
        total = sum(sq.total() for sq in self.skill_questions)
        total += len(self.behavioral) + len(self.project_deep_dive)
        total += len(self.system_design) + len(self.role_specific)
        return total
