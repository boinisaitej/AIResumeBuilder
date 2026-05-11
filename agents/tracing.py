"""LangSmith tracing setup.

Activates automatically when `LANGSMITH_API_KEY` is set in the environment.
Each agent function is decorated with `@traced` so node-level latency, tokens,
and inputs/outputs appear in the LangSmith dashboard.

If LangSmith is not configured the decorator is a no-op — local dev still works.
"""
from __future__ import annotations
import os
from functools import wraps
from typing import Callable, TypeVar

F = TypeVar("F", bound=Callable)


def configure_langsmith() -> bool:
    """Enable LangSmith tracing if LANGSMITH_API_KEY is set. Returns True if active."""
    key = os.getenv("LANGSMITH_API_KEY", "").strip()
    if not key:
        os.environ["LANGCHAIN_TRACING_V2"] = "false"
        return False

    os.environ["LANGCHAIN_TRACING_V2"]    = "true"
    os.environ["LANGCHAIN_API_KEY"]       = key
    os.environ["LANGCHAIN_PROJECT"]       = os.getenv("LANGSMITH_PROJECT", "ai-resume-builder")
    os.environ["LANGCHAIN_ENDPOINT"]      = os.getenv(
        "LANGSMITH_ENDPOINT", "https://api.smith.langchain.com"
    )
    return True


_ACTIVE = configure_langsmith()


def traced(name: str | None = None) -> Callable[[F], F]:
    """Decorator that wraps a function with LangSmith's @traceable when active.

    Falls back to a no-op when LangSmith is not configured, so the same code
    runs identically with or without tracing.
    """
    def decorator(fn: F) -> F:
        if not _ACTIVE:
            return fn
        try:
            from langsmith import traceable
            return traceable(name=name or fn.__name__)(fn)  # type: ignore[return-value]
        except Exception:
            return fn

        @wraps(fn)
        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)
        return wrapper  # type: ignore[return-value]
    return decorator


def is_active() -> bool:
    return _ACTIVE
