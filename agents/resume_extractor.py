"""Resume extractor — uploaded PDF text → structured `ResumeExtraction`.

Used by Tab 2 (Upload & Analyze) so the optimized PDF + interview agent see a
fully populated profile (name, email, education, experience, skills, projects,
certifications) instead of empty placeholders.
"""
from __future__ import annotations
from agents.schemas import ResumeExtraction
from agents.llm import LLMClient
from agents.tracing import traced


@traced("resume_extractor")
def extract_resume(raw_text: str, llm_client: LLMClient) -> ResumeExtraction:
    """Parse a raw resume text blob into a structured profile.

    Returns a `ResumeExtraction`. Any field the resume doesn't mention is left
    blank (rather than invented).
    """
    if not raw_text or not raw_text.strip():
        return ResumeExtraction()

    prompt = f"""You are a resume parser. Extract structured fields from the resume text below.

RESUME TEXT:
{raw_text[:6000]}

RULES:
1. Only extract information that is EXPLICITLY in the resume. Never invent.
2. For dates, copy them as written (e.g. "Jun 2023", "2020 - Present").
3. For skills with no duration mentioned in the resume, set years and months to 0.
   If the resume mentions a duration (e.g. "Python (5 years)"), parse it.
4. For LinkedIn / GitHub: extract the full URL if present, else leave blank.
5. For email and mobile: extract verbatim.
6. For location: extract city + country/state if present.
7. For experience description: combine bullet points into 1-3 sentences capturing
   the most impactful achievements (with metrics if present).
8. For project summary: 1-2 sentences describing what was built + impact.
9. If a section is entirely missing from the resume, return an empty list/empty string.

Be thorough — extract EVERY education entry, EVERY job, EVERY skill, EVERY project,
EVERY certification you can find in the text.
"""

    return llm_client.call_structured(
        prompt,
        ResumeExtraction,
        temperature=0.1,
        use_flash_lite=False,
    )
