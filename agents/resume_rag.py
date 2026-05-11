"""Resume-specific RAG retriever.

Chunks a single resume (by ## section headings, then by ~500-char windows for
long sections), embeds each chunk with Gemini `text-embedding-004`, and serves
top-K relevant chunks for any chatbot query.

Embeddings are cached in-process keyed by resume content hash, so the same
resume isn't re-embedded across reruns of the same Streamlit session.
"""
from __future__ import annotations
import hashlib, re
from typing import Optional

# Module-level cache: resume_hash → ResumeRetriever
_cache: dict[str, "ResumeRetriever"] = {}


def _hash(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()[:16]


def _chunk_resume(text: str, max_chunk_chars: int = 600) -> list[str]:
    """Split resume into semantic chunks.

    Strategy: split on Markdown `##` headings first; if any section is longer
    than `max_chunk_chars`, sub-split by paragraphs / sentence groups.
    """
    if not text or not text.strip():
        return []

    # Split on ## headings; keep the heading WITH its content
    sections = re.split(r"(?=^##\s)", text, flags=re.MULTILINE)
    sections = [s.strip() for s in sections if s.strip()]
    if len(sections) == 1:
        # No markdown headings — split by blank lines
        sections = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]

    chunks: list[str] = []
    for sec in sections:
        if len(sec) <= max_chunk_chars:
            chunks.append(sec)
            continue
        # Split long section by sentences/lines, packing up to max_chunk_chars
        lines = re.split(r"(?<=[.!?])\s+|\n", sec)
        buf, buf_len = [], 0
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if buf_len + len(line) + 1 > max_chunk_chars and buf:
                chunks.append(" ".join(buf))
                buf, buf_len = [], 0
            buf.append(line)
            buf_len += len(line) + 1
        if buf:
            chunks.append(" ".join(buf))

    # Drop tiny chunks (< 30 chars) and dedup
    seen, out = set(), []
    for c in chunks:
        c = c.strip()
        if len(c) < 30 or c in seen:
            continue
        out.append(c)
        seen.add(c)
    return out


class ResumeRetriever:
    """In-memory cosine-similarity retriever over resume chunks."""

    def __init__(self, resume_text: str, api_key: str):
        self.resume_text = resume_text or ""
        self.api_key     = api_key
        self.chunks: list[str] = _chunk_resume(self.resume_text)
        self._embeddings = None     # numpy array, built lazily
        self._emb_model  = None

    # ── Lazy embedding build ──────────────────────────────────────────────────
    def _build(self) -> None:
        if self._embeddings is not None or not self.chunks or not self.api_key:
            return
        try:
            import numpy as np
            from langchain_google_genai import GoogleGenerativeAIEmbeddings
            self._emb_model = GoogleGenerativeAIEmbeddings(
                model="models/text-embedding-004",
                google_api_key=self.api_key,
            )
            vecs = self._emb_model.embed_documents(self.chunks)
            self._embeddings = np.array(vecs, dtype="float32")
        except Exception as e:
            # If embedding fails (quota / network), retriever degrades to "no RAG"
            print(f"[resume_rag] embedding build failed: {e}")
            self._embeddings = None

    # ── Retrieve ──────────────────────────────────────────────────────────────
    def retrieve(self, query: str, k: int = 4) -> list[dict]:
        """Return top-K chunks ranked by cosine similarity to `query`.

        Each result is {"text", "score"}. Returns empty list if anything fails.
        """
        if not query or not query.strip() or not self.chunks:
            return []
        self._build()
        if self._embeddings is None or self._emb_model is None:
            # Fallback — return first K chunks unscored
            return [{"text": c, "score": 0.0} for c in self.chunks[:k]]

        try:
            import numpy as np
            qv = np.array(self._emb_model.embed_query(query), dtype="float32")
            denom = (np.linalg.norm(self._embeddings, axis=1) * np.linalg.norm(qv) + 1e-9)
            sims = (self._embeddings @ qv) / denom
            order = np.argsort(-sims)[:k]
            return [{"text": self.chunks[int(i)], "score": float(sims[int(i)])} for i in order]
        except Exception as e:
            print(f"[resume_rag] retrieve failed: {e}")
            return [{"text": c, "score": 0.0} for c in self.chunks[:k]]


def get_retriever(resume_text: str, api_key: str) -> ResumeRetriever:
    """Process-cached retriever keyed by resume hash."""
    key = _hash(resume_text)
    if key in _cache and _cache[key].api_key == api_key:
        return _cache[key]
    _cache[key] = ResumeRetriever(resume_text, api_key)
    return _cache[key]


def format_chunks_for_prompt(chunks: list[dict], max_chars: int = 1800) -> str:
    """Render retrieved chunks as a focused context block for the LLM."""
    if not chunks:
        return ""
    out = ["Most relevant excerpts from the candidate's resume:"]
    used = 0
    for i, c in enumerate(chunks, 1):
        chunk = f"\n[{i}] {c.get('text','').strip()}"
        if used + len(chunk) > max_chars:
            break
        out.append(chunk)
        used += len(chunk)
    return "\n".join(out)
