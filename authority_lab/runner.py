"""Fixture loading, expectation comparison, and deterministic trace output."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Mapping

from .model import (
    AuthorityOutcome,
    FactState,
    HarnessStatus,
    MANDATORY_T3_FACTS,
    OBJECTIVE_BINDING_FACTS,
    OracleInput,
    RunResult,
)
from .oracle import evaluate


def load_fixture(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError("fixture root must be an object")
    if value.get("schema_version") not in {"authority-lab-v0", "authority-lab-v1"}:
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


def _render_fact(fact: Any) -> str:
    if fact is None:
        return "UNKNOWN"
    if fact.state is FactState.KNOWN:
        return f"KNOWN({fact.value})"
    if fact.state is FactState.CONFLICTING:
        return f"CONFLICTING({','.join(str(value) for value in fact.values)})"
    return "UNKNOWN"


def format_trace(result: RunResult) -> str:
    case = result.oracle_input
    lines = [
        f"CASE: {result.case_id}",
        f"TITLE: {result.title}",
        "",
        "T1",
        f"result: {case.t1_result.value}",
    ]
    t1_binding_fact_names = (
        *OBJECTIVE_BINDING_FACTS,
        *(
            ("contract_transformation_binding",)
            if case.t1_binding_facts.raw["contract_transformation_binding"].state
            is not FactState.UNKNOWN
            else ()
        ),
    )
    for name in t1_binding_fact_names:
        lines.append(f"{name}: {_render_fact(case.t1_binding_facts.raw[name])}")
    lines.extend(
        (
            "",
            "T2",
            f"fixture_claims_authority: {str(case.t2_creates_authority).lower()}",
            "authority_created: false",
        )
    )
    for mutation in case.t2_mutations:
        lines.append(f"{mutation.field}: {mutation.before} -> {mutation.after}")
    lines.extend(("", "T3"))
    required_facts = tuple(
        dict.fromkeys(
            (
                *MANDATORY_T3_FACTS,
                *case.required_facts,
                *case.required_values,
                *(
                    ("contract_transformation_binding",)
                    if "contract_transformation_binding" in case.facts
                    else ()
                ),
            )
        )
    )
    for name in required_facts:
        fact = case.facts.get(name)
        lines.append(f"{name}: {_render_fact(fact)}")
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
