"""Shared Gemini LLM client with key rotation and structured output support.

Agents call `LLMClient.call(prompt)` for free-form text or
`LLMClient.call_structured(prompt, schema)` for Pydantic-validated output.
Keys rotate automatically on quota / rate-limit errors.
"""
from __future__ import annotations
import os
from typing import Type, TypeVar
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

T = TypeVar("T", bound=BaseModel)

DEFAULT_MODEL    = "gemini-2.5-flash"
FLASH_LITE_MODEL = "gemini-flash-lite-latest"


def is_quota_error(e: Exception) -> bool:
    msg = str(e).lower()
    return any(x in msg for x in ["quota", "429", "exhausted", "resource_exhausted", "rate limit"])


def _extract_text(content) -> str:
    """Normalize Gemini's content (string OR list of content-parts) to plain text."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for c in content:
            if isinstance(c, dict):
                if c.get("type") == "text" and "text" in c:
                    parts.append(c["text"])
                elif "text" in c:
                    parts.append(c["text"])
            elif isinstance(c, str):
                parts.append(c)
        return "\n".join(p for p in parts if p)
    return str(content)


class LLMClient:
    """Gemini client with N-key round-robin rotation on quota errors."""

    def __init__(self, keys: list[str]):
        self.keys: list[str] = [k.strip() for k in keys if k and k.strip()]
        self.exhausted: set[str] = set()
        self.call_count: int = 0
        self.token_estimate: int = 0

    # ──────────────────────────────────────────────────────────────────────────
    # Key management
    # ──────────────────────────────────────────────────────────────────────────
    def has_active_key(self) -> bool:
        return any(k not in self.exhausted for k in self.keys)

    def active_count(self) -> int:
        return sum(1 for k in self.keys if k not in self.exhausted)

    def _next_key(self) -> str | None:
        for k in self.keys:
            if k not in self.exhausted:
                return k
        return None

    def _mark_exhausted(self, key: str) -> None:
        self.exhausted.add(key)

    def add_keys(self, keys: list[str]) -> None:
        for k in keys:
            k = (k or "").strip()
            if k and k not in self.keys:
                self.keys.append(k)

    def reset_exhausted(self) -> None:
        self.exhausted.clear()

    # ──────────────────────────────────────────────────────────────────────────
    # LLM invocation
    # ──────────────────────────────────────────────────────────────────────────
    def _build_llm(self, key: str, *, model: str, temperature: float) -> ChatGoogleGenerativeAI:
        return ChatGoogleGenerativeAI(
            model=model,
            google_api_key=key,
            temperature=temperature,
            request_timeout=90,
        )

    def call(
        self,
        prompt: str,
        *,
        temperature: float = 0.3,
        use_flash_lite: bool = False,
        max_retries: int = 8,
    ) -> str:
        """Free-form text completion."""
        model = FLASH_LITE_MODEL if use_flash_lite else DEFAULT_MODEL
        last_err: Exception | None = None
        for _ in range(max_retries):
            key = self._next_key()
            if not key:
                raise RuntimeError("NO_KEYS")
            try:
                llm = self._build_llm(key, model=model, temperature=temperature)
                raw = llm.invoke([HumanMessage(content=prompt)]).content
                result = _extract_text(raw)
                self.call_count += 1
                self.token_estimate += (len(prompt) + len(result)) // 4
                return result
            except Exception as e:
                last_err = e
                if is_quota_error(e):
                    self._mark_exhausted(key)
                    continue
                raise
        if last_err and is_quota_error(last_err):
            raise RuntimeError("ALL_EXHAUSTED")
        raise last_err or RuntimeError("ALL_EXHAUSTED")

    def call_structured(
        self,
        prompt: str,
        schema: Type[T],
        *,
        temperature: float = 0.2,
        use_flash_lite: bool = False,
        max_retries: int = 8,
    ) -> T:
        """Structured Pydantic output via Gemini function calling."""
        model = FLASH_LITE_MODEL if use_flash_lite else DEFAULT_MODEL
        last_err: Exception | None = None
        for _ in range(max_retries):
            key = self._next_key()
            if not key:
                raise RuntimeError("NO_KEYS")
            try:
                llm = self._build_llm(key, model=model, temperature=temperature)
                structured = llm.with_structured_output(schema)
                result = structured.invoke(prompt)
                self.call_count += 1
                self.token_estimate += len(prompt) // 4
                return result  # type: ignore[return-value]
            except Exception as e:
                last_err = e
                if is_quota_error(e):
                    self._mark_exhausted(key)
                    continue
                raise
        if last_err and is_quota_error(last_err):
            raise RuntimeError("ALL_EXHAUSTED")
        raise last_err or RuntimeError("ALL_EXHAUSTED")


def from_env() -> LLMClient:
    """Build a client from GOOGLE_API_KEY / GOOGLE_API_KEY_1..8 env vars."""
    keys: list[str] = []
    for i in range(1, 9):
        k = os.getenv(f"GOOGLE_API_KEY_{i}", "").strip()
        if k:
            keys.append(k)
    single = os.getenv("GOOGLE_API_KEY", "").strip()
    if single and single not in keys:
        keys.append(single)
    return LLMClient(keys)
