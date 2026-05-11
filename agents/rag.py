"""RAG over a curated Job Description corpus.

Builds a persistent Chroma vector store from `data/jd_corpus.jsonl` using
Google's `text-embedding-004` model. Agents call `retrieve_similar_jds(query)`
to get the top-K most semantically similar job descriptions for grounding.

The store auto-builds on first use and persists to `.chroma/` so subsequent
runs skip embedding.
"""
from __future__ import annotations
import json, os
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CORPUS_PATH  = PROJECT_ROOT / "data" / "jd_corpus.jsonl"
CHROMA_PATH  = PROJECT_ROOT / ".chroma"
COLLECTION   = "jd_corpus"


_retriever_singleton: Optional["JDRetriever"] = None


class JDRetriever:
    """Wraps Chroma + Google embeddings. Lazy-initialized."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self._vector_store = None

    def _build_embeddings(self):
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        return GoogleGenerativeAIEmbeddings(
            model="models/text-embedding-004",
            google_api_key=self.api_key,
        )

    def _build_or_load(self):
        if self._vector_store is not None:
            return self._vector_store

        from langchain_community.vectorstores import Chroma
        emb = self._build_embeddings()

        # If persisted store exists, load it
        if (CHROMA_PATH / "chroma.sqlite3").exists():
            self._vector_store = Chroma(
                collection_name=COLLECTION,
                embedding_function=emb,
                persist_directory=str(CHROMA_PATH),
            )
            return self._vector_store

        # Otherwise build from corpus
        if not CORPUS_PATH.exists():
            raise FileNotFoundError(f"JD corpus missing: {CORPUS_PATH}")

        texts: list[str] = []
        metas: list[dict] = []
        with CORPUS_PATH.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)
                texts.append(rec["text"])
                metas.append({
                    "id":           rec.get("id", ""),
                    "role":         rec.get("role", ""),
                    "company_type": rec.get("company_type", ""),
                    "seniority":    rec.get("seniority", ""),
                    "skills":       ", ".join(rec.get("skills", [])),
                })

        CHROMA_PATH.mkdir(parents=True, exist_ok=True)
        self._vector_store = Chroma.from_texts(
            texts=texts,
            embedding=emb,
            metadatas=metas,
            collection_name=COLLECTION,
            persist_directory=str(CHROMA_PATH),
        )
        return self._vector_store

    def retrieve(self, query: str, k: int = 4) -> list[dict]:
        """Return top-K similar JDs as list of {role, skills, text, score}."""
        try:
            vs = self._build_or_load()
            results = vs.similarity_search_with_score(query, k=k)
        except Exception:
            # RAG is best-effort — never break the pipeline
            return []

        hits: list[dict] = []
        for doc, score in results:
            md = doc.metadata or {}
            hits.append({
                "role":         md.get("role", ""),
                "company_type": md.get("company_type", ""),
                "seniority":    md.get("seniority", ""),
                "skills":       md.get("skills", ""),
                "text":         doc.page_content,
                "score":        float(score),
            })
        return hits


def get_retriever(api_key: str) -> JDRetriever:
    """Process-wide singleton so we don't rebuild the index per call."""
    global _retriever_singleton
    if _retriever_singleton is None or _retriever_singleton.api_key != api_key:
        _retriever_singleton = JDRetriever(api_key)
    return _retriever_singleton


def retrieve_similar_jds(query: str, api_key: str, k: int = 4) -> list[dict]:
    """Convenience wrapper."""
    if not query or not query.strip() or not api_key:
        return []
    return get_retriever(api_key).retrieve(query, k=k)


def format_jds_for_prompt(hits: list[dict], max_chars: int = 1200) -> str:
    """Render retrieved JDs as a compact context block for the LLM."""
    if not hits:
        return ""
    parts = ["Reference job postings retrieved from corpus (for grounding only — do not invent skills):"]
    used = 0
    for i, h in enumerate(hits, 1):
        chunk = (
            f"\n[JD {i}] {h.get('role','')} ({h.get('seniority','')}, {h.get('company_type','')})\n"
            f"Key skills: {h.get('skills','')}\n"
            f"Excerpt: {h.get('text','')[:280]}"
        )
        if used + len(chunk) > max_chars:
            break
        parts.append(chunk)
        used += len(chunk)
    return "\n".join(parts)
