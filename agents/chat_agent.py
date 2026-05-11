"""ATS-reasoning chatbot — RAG-grounded on the user's resume.

For every user query we:
  1. Retrieve top-K most relevant chunks of THE candidate's resume
     (chunked + embedded by `agents.resume_rag`).
  2. Inject those chunks (not the whole resume) into the prompt.
  3. Include the ATS analysis + optional JD as fixed context.
  4. Carry a short rolling conversation history.

This makes the chatbot truly RAG-based: it cites real excerpts from the
candidate's resume rather than reasoning over a generic summary.
"""
from __future__ import annotations
from agents.llm import LLMClient
from agents.tracing import traced
from agents.resume_rag import get_retriever, format_chunks_for_prompt


SYSTEM_PROMPT = """You are a friendly, expert resume coach and ATS specialist.

You answer the candidate's questions about THEIR specific resume, ATS score,
and how to improve. Be concrete and actionable. Ground every claim in the
retrieved resume excerpts.

GUIDELINES:
- Quote specific lines / bullets from the retrieved excerpts when relevant.
- Quote the ATS analysis when explaining the score.
- Suggest exact wording rewrites, not vague advice.
- If the resume doesn't cover what's asked, say so honestly — never invent
  skills, experience, or accomplishments.
- If NO resume has been generated or uploaded yet, give general ATS coaching
  advice and gently invite the user to fill the form / upload a PDF for
  resume-specific answers.
- Keep responses focused — usually 4-8 sentences unless asked for detail.
- Use Markdown (bold, bullets) where it helps readability.
"""


@traced("chat_agent")
def chat_about_resume(
    user_message: str,
    history: list[dict],
    resume_text: str,
    ats_analysis: str,
    ats_score: int | None,
    job_description: str,
    llm_client: LLMClient,
    *,
    rag_k: int = 4,
) -> str:
    """RAG-grounded chatbot response.

    Args:
        user_message     : the user's latest question
        history          : prior turns as [{"role": "user"|"assistant", "content": "..."}]
        resume_text      : the candidate's resume (Markdown or raw text)
        ats_analysis     : the full ATS analysis text from the pipeline
        ats_score        : numeric ATS score 0-100 (or None)
        job_description  : optional JD/target role
        llm_client       : shared LLM client with key rotation
        rag_k            : how many resume chunks to retrieve per turn
    """
    has_resume = bool((resume_text or "").strip())
    has_ats    = bool((ats_analysis or "").strip()) or ats_score is not None

    # ── RAG: retrieve top-K resume chunks (only if a resume exists) ───────────
    rag_block = ""
    if has_resume:
        api_key = (llm_client._next_key() or "") if hasattr(llm_client, "_next_key") else ""
        chunks  = get_retriever(resume_text, api_key).retrieve(user_message, k=rag_k)
        rag_block = format_chunks_for_prompt(chunks)

    # If neither resume nor analysis available, signal that to the model
    if not has_resume and not has_ats:
        context_note = (
            "(No resume has been generated or uploaded yet. Give general ATS "
            "coaching advice and invite the user to either build a resume on "
            "the Build tab OR upload one on the Analyze tab for tailored answers.)"
        )
    elif not has_resume:
        context_note = "(No resume text yet — answer using the ATS analysis below.)"
    else:
        context_note = rag_block or "(resume retrieval temporarily unavailable)"

    score_line = f"ATS Score: {ats_score}/100" if ats_score is not None else "ATS Score: (not computed)"
    jd_block = (
        f"\nJOB DESCRIPTION / TARGET ROLE:\n{job_description[:1200]}\n"
        if (job_description or "").strip() else ""
    )

    # Keep last ~6 turns to stay within token budget
    history = (history or [])[-6:]
    history_block = ""
    for turn in history:
        role = "USER" if turn.get("role") == "user" else "ASSISTANT"
        history_block += f"\n{role}: {turn.get('content','')[:1200]}\n"

    prompt = f"""{SYSTEM_PROMPT}

────────────────────────────────────────────────────────────────────────────
{context_note}
────────────────────────────────────────────────────────────────────────────

ATS ANALYSIS:
{score_line}
{(ats_analysis or "")[:2200]}
{jd_block}
────────────────────────────────────────────────────────────────────────────

CONVERSATION SO FAR:
{history_block if history_block else "(this is the first message)"}

USER: {user_message}

A:"""

    return llm_client.call(prompt, temperature=0.5, use_flash_lite=True)


# Common starter prompts shown as quick-action chips in the UI
SUGGESTED_QUESTIONS = [
    "Why is my ATS score what it is?",
    "What are the top 3 changes that would raise my score?",
    "Which keywords from the JD am I missing?",
    "Rewrite my summary section to be stronger.",
    "What's the weakest bullet in my resume and why?",
    "How can I quantify my achievements better?",
]
