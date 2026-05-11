"""Eval harness for the resume-builder pipeline.

Runs the LangGraph pipeline against every profile in `golden_profiles.jsonl`
and asserts structural properties of the output (not exact text — LLMs vary).

Usage:
    python -m evals.run_evals                  # run all, print summary
    python -m evals.run_evals --id p03_genai…  # run a single profile
    python -m evals.run_evals --limit 3        # run first N profiles
    python -m evals.run_evals --json results.json   # write JSON report

Requirements:
- GOOGLE_API_KEY (or GOOGLE_API_KEY_1..8) in environment
- Optional: LANGSMITH_API_KEY for traces

Exit code is the number of failed assertions, so the script works as a CI gate:
    python -m evals.run_evals && echo PASS || echo FAIL
"""
from __future__ import annotations
import argparse, json, sys, time
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

# Path so imports work when invoked from project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agents.llm import from_env, LLMClient
from agents.graph import run_pipeline

EVAL_FILE = Path(__file__).resolve().parent / "golden_profiles.jsonl"


@dataclass
class EvalCase:
    id: str
    expected_domain_keywords: list[str]
    min_ats_score: int
    expected_skills_in_resume: list[str]
    profile: dict


@dataclass
class CaseResult:
    id: str
    ats_score: int
    duration_s: float
    llm_calls: int
    passed: bool
    failures: list[str] = field(default_factory=list)
    domain: str = ""


def load_cases() -> list[EvalCase]:
    cases: list[EvalCase] = []
    with EVAL_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            cases.append(EvalCase(
                id=rec["id"],
                expected_domain_keywords=rec.get("expected_domain_keywords", []),
                min_ats_score=rec.get("min_ats_score", 0),
                expected_skills_in_resume=rec.get("expected_skills_in_resume", []),
                profile=rec["profile"],
            ))
    return cases


def run_case(case: EvalCase, client: LLMClient) -> CaseResult:
    start = time.time()
    failures: list[str] = []
    domain = ""
    ats_score = 0
    try:
        final = run_pipeline(case.profile, client)

        # Check 1: ATS score above floor
        ats_score = int(final.get("ats_score", 0))
        if ats_score < case.min_ats_score:
            failures.append(f"ats_score {ats_score} < min {case.min_ats_score}")

        # Check 2: resume_draft non-empty + contains expected skills
        resume = (final.get("resume_draft") or "").lower()
        if len(resume) < 200:
            failures.append(f"resume_draft too short ({len(resume)} chars)")
        for sk in case.expected_skills_in_resume:
            if sk.lower() not in resume:
                failures.append(f"expected skill '{sk}' not in resume_draft")

        # Check 3: structured outputs populated
        if not final.get("categorization"):
            failures.append("categorization (Pydantic) is empty")
        if not final.get("skill_analysis_obj"):
            failures.append("skill_analysis_obj (Pydantic) is empty")
        if not final.get("ats_analysis_obj"):
            failures.append("ats_analysis_obj (Pydantic) is empty")
        if not final.get("roadmap_obj"):
            failures.append("roadmap_obj (Pydantic) is empty")

        # Check 4: domain mentions an expected keyword
        sa = final.get("skill_analysis_obj")
        if sa is not None:
            domain = (sa.domain_assessment or "").lower()
            if case.expected_domain_keywords:
                if not any(k.lower() in domain for k in case.expected_domain_keywords):
                    failures.append(
                        f"domain '{domain[:80]}' missing all of {case.expected_domain_keywords}"
                    )

        # Check 5: roadmap phases populated
        phases = final.get("roadmap_parsed", []) or []
        if len(phases) < 2:
            failures.append(f"roadmap has only {len(phases)} phases (expected ≥2)")

        # Check 6: README non-trivial
        readme = final.get("readme_content") or ""
        if len(readme) < 300:
            failures.append(f"readme too short ({len(readme)} chars)")

    except Exception as e:
        failures.append(f"pipeline raised: {type(e).__name__}: {e}")

    return CaseResult(
        id=case.id,
        ats_score=ats_score,
        duration_s=round(time.time() - start, 2),
        llm_calls=client.call_count,
        passed=len(failures) == 0,
        failures=failures,
        domain=domain[:80],
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--id", help="Run a single case by ID")
    ap.add_argument("--limit", type=int, default=0, help="Run only first N cases")
    ap.add_argument("--json", help="Write JSON report to this path")
    args = ap.parse_args()

    cases = load_cases()
    if args.id:
        cases = [c for c in cases if c.id == args.id]
    if args.limit > 0:
        cases = cases[: args.limit]

    if not cases:
        print("No matching cases.")
        return 1

    client = from_env()
    if not client.has_active_key():
        print("ERROR: No GOOGLE_API_KEY[_1..8] found in environment.")
        return 2

    print(f"Running {len(cases)} eval case(s) with {client.active_count()} API key(s)…\n")
    results: list[CaseResult] = []
    for case in cases:
        print(f"  ▶ {case.id} … ", end="", flush=True)
        client.call_count = 0  # reset per-case counter
        r = run_case(case, client)
        results.append(r)
        if r.passed:
            print(f"PASS  ats={r.ats_score:>3}  {r.duration_s}s  calls={r.llm_calls}")
        else:
            print(f"FAIL  ats={r.ats_score:>3}  {r.duration_s}s  calls={r.llm_calls}")
            for f in r.failures:
                print(f"      └─ {f}")

    # Summary
    total   = len(results)
    passed  = sum(1 for r in results if r.passed)
    failed  = total - passed
    avg_ats = sum(r.ats_score for r in results) / total if total else 0
    avg_t   = sum(r.duration_s for r in results) / total if total else 0
    print(f"\n{'─'*60}")
    print(f"SUMMARY:  {passed}/{total} passed  ·  avg ATS {avg_ats:.1f}  ·  avg {avg_t:.1f}s/case")

    if args.json:
        Path(args.json).write_text(json.dumps([r.__dict__ for r in results], indent=2))
        print(f"Wrote {args.json}")

    return failed


if __name__ == "__main__":
    raise SystemExit(main())
