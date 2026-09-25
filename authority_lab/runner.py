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
    OBSERVATION_SCOPE_FAMILIES,
    OracleInput,
    RunResult,
)
from .oracle import analyze_continuity_path, evaluate


def load_fixture(path: str | Path) -> dict[str, Any]:
    fixture_path = Path(path)
    with fixture_path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError("fixture root must be an object")
    if value.get("schema_version") not in {"authority-lab-v0", "authority-lab-v1"}:
        raise ValueError("unsupported fixture schema_version")
    if "_trusted_commitment_context" in value:
        raise ValueError("fixture cannot supply harness-owned trusted commitment state")
    manifest_path = fixture_path.parent / "trusted_commitment_state.json"
    if value.get("schema_version") == "authority-lab-v1" and manifest_path.exists():
        with manifest_path.open("r", encoding="utf-8") as handle:
            manifest = json.load(handle)
        context = manifest.get(fixture_path.name, [])
        if not isinstance(context, list) or not all(isinstance(item, dict) for item in context):
            raise ValueError("trusted commitment state manifest entry is invalid")
        value["_trusted_commitment_context"] = context
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
    return tuple(sorted(Path(directory).glob("LAB-*.json")))


def _render_fact(fact: Any) -> str:
    if fact is None:
        return "UNKNOWN"
    if fact.state is FactState.KNOWN:
        return f"KNOWN({fact.value})"
    if fact.state is FactState.CONFLICTING:
        return f"CONFLICTING({','.join(str(value) for value in fact.values)})"
    return "UNKNOWN"


def _observation_trace(case: OracleInput) -> tuple[str, ...]:
    binding = case.observation_binding
    freshness = case.observation_freshness
    if binding is None:
        return ("OBSERVATION", "binding: UNAVAILABLE", "freshness: UNAVAILABLE")

    gaps: list[str] = []
    for family in OBSERVATION_SCOPE_FAMILIES:
        intervals = sorted(
            (segment.start_event_order, segment.end_event_order)
            for segment in binding.segments
            if family in segment.scope_families
        )
        cursor = binding.t1_anchor.event_order
        for start, end in intervals:
            if start > cursor:
                gaps.append(f"{family}:{cursor}-{start - 1}")
            cursor = max(cursor, end + 1)
        if cursor <= binding.t3_anchor.event_order:
            gaps.append(f"{family}:{cursor}-{binding.t3_anchor.event_order}")

    lines = [
        "OBSERVATION",
        f"profile: {binding.profile_id}@{binding.profile_version}",
        (
            "binding: "
            f"{binding.observation_binding_id}@{binding.observation_binding_generation} "
            f"source={binding.source_id}"
        ),
        (
            "interval: "
            f"{binding.t1_anchor.anchor_id}@{binding.t1_anchor.event_order} -> "
            f"{binding.t3_anchor.anchor_id}@{binding.t3_anchor.event_order}"
        ),
    ]
    lines.extend(
        "observer: "
        f"{observer.observer_id}@{observer.observer_generation} "
        f"state={observer.lifecycle_state} scopes={','.join(observer.scope_families)}"
        for observer in sorted(
            binding.observers,
            key=lambda value: (value.observer_id, value.observer_generation),
        )
    )
    lines.extend(
        "segment: "
        f"{segment.segment_id} observer={segment.observer_id}@{segment.observer_generation} "
        f"events={segment.start_event_order}-{segment.end_event_order} "
        f"sequence={segment.start_sequence}-{segment.end_sequence} "
        f"stream={segment.stream_id}@{segment.stream_generation}"
        for segment in sorted(
            binding.segments,
            key=lambda value: (
                value.start_event_order,
                value.end_event_order,
                value.segment_id,
            ),
        )
    )
    lines.extend(
        "handoff: "
        f"{handoff.handoff_id} {handoff.from_observer_id}->{handoff.to_observer_id} "
        f"at={handoff.handoff_event_order}"
        for handoff in sorted(binding.handoffs, key=lambda value: value.handoff_id)
    )
    lines.extend(
        "transformation: "
        f"{item.transformation_id}@{item.transformation_generation} "
        f"{item.source_stream_id}@{item.source_stream_generation}->"
        f"{item.target_stream_id}@{item.target_stream_generation}"
        for item in sorted(
            binding.transformations,
            key=lambda value: (value.transformation_id, value.transformation_generation),
        )
    )
    lines.extend(
        "commitment: "
        f"{item.values['commitment_id']} position={item.values['logical_position']} "
        f"digest={item.values['commitment_digest']} stream="
        f"{item.values['stream_id']}@{item.values['stream_generation']}"
        for item in binding.commitment_envelopes
    )
    lines.extend(
        "checkpoint: "
        f"{item.values['checkpoint_id']}@{item.values['checkpoint_generation']} "
        f"head={item.values['head_commitment_id']} state="
        f"{item.values['verifier_state_id']}@{item.values['verifier_state_generation']}"
        for item in binding.commitment_checkpoints
    )
    lines.append(f"trusted_commitment_states: {len(case.trusted_commitment_context)}")
    lines.append(f"gaps: {','.join(gaps) if gaps else 'none'}")
    lines.append(
        "freshness: "
        + (
            f"{freshness.head_anchor_id}@{freshness.head_event_order} "
            f"source={freshness.source_id}"
            if freshness is not None
            else "UNAVAILABLE"
        )
    )
    return tuple(lines)


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
        resolution = (
            f"canonical={mutation.canonical_field}; target={mutation.target_kind.value}:"
            f"{mutation.target}"
            if mutation.target is not None and mutation.target_kind is not None
            else "UNKNOWN"
        )
        metadata = (
            "; continuity_effects="
            f"{','.join(effect.value for effect in mutation.continuity_effects)}; "
            f"observation_scopes={','.join(mutation.observation_scope_families)}"
            if mutation.target is not None
            else ""
        )
        lines.append(
            f"{mutation.field} [{resolution}]: {mutation.before} -> {mutation.after}"
            f"{metadata}"
        )
    path = analyze_continuity_path(case)
    lines.extend(
        (
            "path_effects: "
            + (
                ",".join(sorted(effect.value for effect in path.effects))
                if path.effects
                else "none"
            ),
            "path_observation_scopes: "
            + (
                ",".join(
                    family
                    for family in OBSERVATION_SCOPE_FAMILIES
                    if family in path.observation_scope_families
                )
                if path.observation_scope_families
                else "none"
            ),
            f"path_aba_targets: {','.join(path.aba_targets) if path.aba_targets else 'none'}",
            f"successor_admission_required: {str(path.successor_break).lower()}",
        )
    )
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
    lines.extend(("", *_observation_trace(case)))
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
