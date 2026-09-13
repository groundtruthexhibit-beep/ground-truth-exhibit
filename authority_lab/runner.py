"""Fixture loading, expectation comparison, and deterministic trace output."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Mapping

from .model import AuthorityOutcome, FactState, HarnessStatus, OracleInput, RunResult
from .oracle import evaluate


def load_fixture(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError("fixture root must be an object")
    if value.get("schema_version") != "authority-lab-v0":
        raise ValueError("unsupported fixture schema_version")
    return value


def run_fixture(fixture: Mapping[str, Any]) -> RunResult:
    # The oracle input deliberately excludes title, expected_outcome, and expected_reason.
    oracle_input = OracleInput.from_fixture(fixture)
    actual = evaluate(oracle_input)

    # Expected outcome is parsed only after the actual oracle result is fixed.
    expected = AuthorityOutcome(fixture["expected_outcome"])
    status = HarnessStatus.PASS if actual.outcome is expected else HarnessStatus.CASE_MISMATCH
    return RunResult(
        case_id=oracle_input.case_id,
        title=str(fixture["title"]),
        expected=expected,
        actual=actual,
        status=status,
        oracle_input=oracle_input,
    )


def run_path(path: str | Path) -> RunResult:
    return run_fixture(load_fixture(path))


def discover(directory: str | Path) -> tuple[Path, ...]:
    return tuple(sorted(Path(directory).glob("*.json")))


def format_trace(result: RunResult) -> str:
    case = result.oracle_input
    lines = [
        f"CASE: {result.case_id}",
        f"TITLE: {result.title}",
        "",
        "T1",
        f"result: {case.t1_result.value}",
        "",
        "T2",
        f"fixture_claims_authority: {str(case.t2_creates_authority).lower()}",
        "authority_created: false",
    ]
    for mutation in case.t2_mutations:
        lines.append(f"{mutation.field}: {mutation.before} -> {mutation.after}")
    lines.extend(("", "T3"))
    for name in case.required_facts:
        fact = case.facts.get(name)
        if fact is None:
            rendered = "UNKNOWN"
        elif fact.state is FactState.KNOWN:
            rendered = f"KNOWN({fact.value})"
        elif fact.state is FactState.CONFLICTING:
            rendered = f"CONFLICTING({','.join(str(value) for value in fact.values)})"
        else:
            rendered = "UNKNOWN"
        lines.append(f"{name}: {rendered}")
    lines.extend(
        (
            "",
            "ACTUAL_AUTHORITY_OUTCOME:",
            result.actual.outcome.value,
            "",
            "REASONS:",
        )
    )
    lines.extend(reason.code for reason in result.actual.reasons)
    lines.extend(("", "ENGAGED_INVARIANTS:"))
    lines.extend(result.actual.engaged_invariants)
    lines.extend(
        (
            "",
            "EXPECTED:",
            result.expected.value,
            "",
            "HARNESS_STATUS:",
            result.status.value,
        )
    )
    return "\n".join(lines)


def with_wrong_expectation(fixture: Mapping[str, Any], wrong: AuthorityOutcome) -> dict[str, Any]:
    """Return a test-only copy with an intentionally incorrect expectation."""
    changed = deepcopy(fixture)
    changed["expected_outcome"] = wrong.value
    return changed
