"""Deterministic oracle over public Authority Lab fixture state."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .model import (
    AuthorityOutcome,
    AuthorityStateBinding,
    FactState,
    INVARIANTS,
    MANDATORY_T3_FACTS,
    OracleInput,
    OracleResult,
    RELATIONAL_T3_FACTS,
    Reason,
)


TUPLE_FACT_BINDINGS = (
    ("subject_identity", "subject"),
    ("artifact_identity", "artifact"),
    ("control_state", "control_state"),
    ("identity_basis", "identity_basis"),
    ("boundary_epoch", "boundary_epoch"),
)

AUTHORITY_PERMITTING_VALUES = {
    "consumption_state": "UNUSED",
    "evidence_binding": "CURRENT",
    "freshness": "CURRENT",
}

STATE_MUTATION_FIELDS = {
    "subject": ("subject",),
    "artifact": ("artifact",),
    "identity_basis": ("identity_basis",),
    "boundary_epoch": ("boundary_epoch",),
    "applicable_boundary": ("applicable_boundary",),
    "consumption_state": ("consumption", "consumption_state"),
}

CANONICAL_MUTATION_STATE_FIELDS = {
    "subject": ("subject",),
    "artifact": ("artifact",),
    "control_state": ("control_state",),
    "identity_basis": ("identity_basis",),
    "boundary_epoch": ("boundary_epoch",),
    "execution_context": ("execution_context",),
    "applicable_boundary": ("applicable_boundary",),
    "decision": ("decision",),
    "evidence_id": ("evidence_id", "decision_binding"),
    "grant_id": ("grant_id",),
    "subject_mode": ("subject_mode",),
    "consumption_state": ("consumption", "consumption_state"),
}

RELATIONAL_MUTATION_FACTS = {
    "evidence_binding": ("evidence_binding",),
    "freshness": ("freshness",),
    "boundary_epoch_binding": ("boundary_epoch_binding",),
    "execution_control_binding": ("execution_control_binding",),
    "consumption_binding": ("consumption_binding",),
    "delegation_binding": ("delegation_binding",),
    "closure_binding": ("closure_binding",),
}

GRANT_SCOPE_FIELDS = (
    "subject",
    "artifact",
    "control_state",
    "identity_basis",
    "boundary_epoch",
    "decision",
    "execution_context",
    "applicable_boundary",
    "subject_mode",
)


def _engaged(case: OracleInput) -> tuple[str, ...]:
    selected = set(case.applicable_invariants)
    return tuple(invariant for invariant in INVARIANTS if invariant in selected)


def _unavailable(
    case: OracleInput, code: str, detail: str, facts: tuple[str, ...] = ()
) -> OracleResult:
    return OracleResult(
        AuthorityOutcome.UNAVAILABLE,
        (Reason(code, detail, facts),),
        _engaged(case),
    )


def _relation_matches(value: Any, expected: Mapping[str, Any]) -> bool:
    return (
        isinstance(value, Mapping)
        and set(value) == set(expected)
        and all(value[name] == expected[name] for name in expected)
    )


def _state_differences(case: OracleInput, state: AuthorityStateBinding) -> tuple[str, ...]:
    consumption = case.facts["consumption_binding"].value
    current_grant = consumption.get("grant_id") if isinstance(consumption, Mapping) else None
    current_subject_mode = (
        case.reestablishment.current.subject_mode
        if case.reestablishment is not None
        else case.t1_authority_state.subject_mode
    )
    current = {
        "subject": case.authority_tuple.subject,
        "artifact": case.authority_tuple.artifact,
        "control_state": case.authority_tuple.control_state,
        "identity_basis": case.authority_tuple.identity_basis,
        "boundary_epoch": case.authority_tuple.boundary_epoch,
        "decision": case.authority_tuple.decision,
        "evidence_id": case.facts["decision_binding"].value,
        "execution_context": case.facts["execution_context"].value,
        "applicable_boundary": case.facts["applicable_boundary"].value,
        "grant_id": current_grant,
        "consumption_state": case.facts["consumption_state"].value,
        "subject_mode": current_subject_mode,
    }
    return tuple(name for name, value in current.items() if value != getattr(state, name))


def _current_state_value(case: OracleInput, field: str) -> Any:
    if field in {"subject", "artifact", "control_state", "identity_basis", "boundary_epoch"}:
        return getattr(case.authority_tuple, field)
    if field == "decision":
        return case.authority_tuple.decision
    if field == "evidence_id":
        return case.facts["decision_binding"].value
    if field == "grant_id":
        consumption = case.facts["consumption_binding"].value
        return consumption.get("grant_id") if isinstance(consumption, Mapping) else None
    if field == "subject_mode":
        if case.reestablishment is not None:
            return case.reestablishment.current.subject_mode
        return case.t1_authority_state.subject_mode
    return case.facts[field].value


def _mutation_chain_mismatches(case: OracleInput) -> tuple[str, ...]:
    mismatches: list[str] = []
    for field, mutation_fields in CANONICAL_MUTATION_STATE_FIELDS.items():
        mutations = tuple(
            mutation for mutation in case.t2_mutations if mutation.field in mutation_fields
        )
        if not mutations:
            continue
        value = getattr(case.t1_authority_state, field)
        for mutation in mutations:
            if mutation.before != value:
                mismatches.append(field)
                break
            value = mutation.after
        else:
            if value != _current_state_value(case, field):
                mismatches.append(field)
    for fact_name, mutation_fields in RELATIONAL_MUTATION_FACTS.items():
        mutations = tuple(
            mutation for mutation in case.t2_mutations if mutation.field in mutation_fields
        )
        if not mutations:
            continue
        value = mutations[0].before
        for mutation in mutations:
            if mutation.before != value:
                mismatches.append(fact_name)
                break
            value = mutation.after
        else:
            if value != case.facts[fact_name].value:
                mismatches.append(fact_name)
    return tuple(dict.fromkeys(mismatches))


def _grant_mutations(case: OracleInput) -> tuple[Any, ...]:
    return tuple(
        mutation for mutation in case.t2_mutations if mutation.field == "grant_id"
    )


def _grant_path(case: OracleInput) -> tuple[str, ...]:
    mutations = _grant_mutations(case)
    if not mutations:
        current = _current_state_value(case, "grant_id")
        return (case.t1_authority_state.grant_id, current)
    return (case.t1_authority_state.grant_id, *(mutation.after for mutation in mutations))


def _consumption_regenerated(case: OracleInput) -> bool:
    consumed = case.t1_authority_state.consumption_state == "CONSUMED"
    for mutation in case.t2_mutations:
        if mutation.field not in {"consumption", "consumption_state"}:
            continue
        if mutation.after == "CONSUMED":
            consumed = True
        elif consumed and mutation.after == "UNUSED":
            return True
    return False


def _has_exact_mutation(
    case: OracleInput, fields: tuple[str, ...], before: Any, after: Any
) -> bool:
    return any(
        mutation.field in fields and mutation.before == before and mutation.after == after
        for mutation in case.t2_mutations
    )


def _changes_are_represented(
    case: OracleInput, before: AuthorityStateBinding, after: AuthorityStateBinding
) -> tuple[str, ...]:
    missing: list[str] = []
    for state_field, mutation_fields in STATE_MUTATION_FIELDS.items():
        old = getattr(before, state_field)
        new = getattr(after, state_field)
        if old != new and not _has_exact_mutation(case, mutation_fields, old, new):
            missing.append(state_field)
    context_or_control_changed = (
        before.execution_context != after.execution_context
        or before.control_state != after.control_state
    )
    if context_or_control_changed and not (
        _has_exact_mutation(
            case,
            ("execution_context",),
            before.execution_context,
            after.execution_context,
        )
        or _has_exact_mutation(
            case,
            ("control_state",),
            before.control_state,
            after.control_state,
        )
    ):
        missing.append("execution_context/control_state")
    return tuple(missing)


def _invalid_identity_fields(case: OracleInput) -> tuple[str, ...]:
    values = {
        "subject": case.authority_tuple.subject,
        "artifact": case.authority_tuple.artifact,
        "control_state": case.authority_tuple.control_state,
        "identity_basis": case.authority_tuple.identity_basis,
        "boundary_epoch": case.authority_tuple.boundary_epoch,
        "decision_binding": case.facts["decision_binding"].value,
        "applicable_boundary": case.facts["applicable_boundary"].value,
        "execution_context": case.facts["execution_context"].value,
    }
    return tuple(
        name for name, value in values.items() if not isinstance(value, str) or value == ""
    )


def _state_has_empty_identifier(state: AuthorityStateBinding) -> bool:
    return any(
        value == ""
        for value in (
            state.subject,
            state.artifact,
            state.control_state,
            state.identity_basis,
            state.boundary_epoch,
            state.evidence_id,
            state.execution_context,
            state.applicable_boundary,
            state.grant_id,
            state.consumption_state,
            state.subject_mode,
        )
    )


def evaluate(case: OracleInput) -> OracleResult:
    """Compute an authority outcome without fixture expectation access."""
    required_facts = tuple(dict.fromkeys((*MANDATORY_T3_FACTS, *case.required_facts)))
    unestablished: list[str] = []
    conflicting: list[str] = []
    for name in required_facts:
        fact = case.facts.get(name)
        if fact is None or fact.state is FactState.UNKNOWN:
            unestablished.append(name)
        elif fact.state is FactState.CONFLICTING:
            conflicting.append(name)

    reasons: list[Reason] = []
    if unestablished:
        reasons.append(
            Reason(
                "REQUIRED_FACT_UNAVAILABLE",
                "One or more authority-relevant facts or relationships are not established.",
                tuple(unestablished),
            )
        )
    if conflicting:
        reasons.append(
            Reason(
                "REQUIRED_FACT_CONFLICTING",
                "One or more authority-relevant facts conflict without authoritative resolution.",
                tuple(conflicting),
            )
        )
    if case.prohibition.state is FactState.UNKNOWN:
        reasons.append(
            Reason("PROHIBITION_STATE_UNAVAILABLE", "Applicable prohibition state is not established.")
        )
    elif case.prohibition.state is FactState.CONFLICTING:
        reasons.append(
            Reason("PROHIBITION_STATE_CONFLICTING", "Applicable prohibition state is conflicting.")
        )
    if reasons:
        return OracleResult(AuthorityOutcome.UNAVAILABLE, tuple(reasons), _engaged(case))

    tuple_mismatches = tuple(
        fact_name
        for fact_name, tuple_field in TUPLE_FACT_BINDINGS
        if case.facts[fact_name].value != getattr(case.authority_tuple, tuple_field)
    )
    if tuple_mismatches:
        return _unavailable(
            case,
            "EXACT_TUPLE_MISMATCH",
            "Observed facts do not establish the exact requested authority tuple.",
            tuple_mismatches,
        )

    invalid_identities = _invalid_identity_fields(case)
    if invalid_identities:
        return _unavailable(
            case,
            "INVALID_IDENTITY_VALUE",
            "Required identity-bearing values must be non-empty exact strings.",
            invalid_identities,
        )

    value_required_facts = tuple(
        name for name in required_facts if name not in RELATIONAL_T3_FACTS
    )
    missing_value_requirements = tuple(
        name for name in value_required_facts if name not in case.required_values
    )
    if missing_value_requirements:
        return _unavailable(
            case,
            "REQUIRED_VALUE_UNSPECIFIED",
            "Case expectations do not specify values for required facts; they cannot create authority.",
            missing_value_requirements,
        )
    value_mismatches = tuple(
        name
        for name in value_required_facts
        if case.facts[name].value != case.required_values[name]
    )
    if value_mismatches:
        return _unavailable(
            case,
            "REQUIRED_VALUE_MISMATCH",
            "Observed values differ from the case inputs; aligned expectations alone cannot establish authority.",
            value_mismatches,
        )

    if case.t2_creates_authority:
        return _unavailable(
            case,
            "T2_AUTHORITY_CLAIM",
            "T2 preparation is non-authoritative and cannot create or preserve authority.",
        )

    expected_boundary_relation = {
        "applicable_boundary": case.facts["applicable_boundary"].value,
        "boundary_epoch": case.authority_tuple.boundary_epoch,
    }
    if not _relation_matches(
        case.facts["boundary_epoch_binding"].value, expected_boundary_relation
    ):
        return _unavailable(
            case,
            "BOUNDARY_EPOCH_RELATIONSHIP_UNAVAILABLE",
            "IMPLEMENTATION_OBLIGATION: the applicable boundary is not exactly bound to the current epoch.",
            ("boundary_epoch_binding",),
        )

    if case.t1_result is AuthorityOutcome.UNAVAILABLE:
        return _unavailable(
            case,
            "T1_UNAVAILABLE",
            "The necessary T1 authorization was not established.",
        )
    if case.t1_result is AuthorityOutcome.DENIED:
        return OracleResult(
            AuthorityOutcome.DENIED,
            (Reason("T1_DENIED", "The established T1 decision prohibits the transition."),),
            _engaged(case),
        )
    if case.authority_tuple.decision is AuthorityOutcome.UNAVAILABLE:
        return _unavailable(
            case,
            "CURRENT_DECISION_UNAVAILABLE",
            "The current exact tuple does not establish an authority-permitting decision.",
            ("decision",),
        )
    if case.authority_tuple.decision is AuthorityOutcome.DENIED:
        return OracleResult(
            AuthorityOutcome.DENIED,
            (Reason("CURRENT_DECISION_DENIED", "The current exact decision prohibits the transition."),),
            _engaged(case),
        )
    if case.prohibition.applies:
        return OracleResult(
            AuthorityOutcome.DENIED,
            (
                Reason(
                    "ESTABLISHED_PROHIBITION",
                    f"Established applicable condition prohibits the transition: {case.prohibition.identifier}.",
                ),
            ),
            _engaged(case),
        )

    nonpermitting_values = tuple(
        name
        for name, permitting_value in AUTHORITY_PERMITTING_VALUES.items()
        if name in required_facts and case.facts[name].value != permitting_value
    )
    if nonpermitting_values:
        return _unavailable(
            case,
            "VALUE_NOT_AUTHORITY_PERMITTING",
            "Known state alone does not establish an authority-permitting value.",
            nonpermitting_values,
        )

    t1_state = case.t1_authority_state
    if t1_state.decision is not case.t1_result or t1_state.evidence_id not in case.t1_evidence:
        return _unavailable(
            case,
            "T1_AUTHORITY_RELATIONSHIP_UNAVAILABLE",
            "MODEL_LIMITATION: T1 evidence and decision are not explicitly bound to one evaluated state.",
            ("t1.authority_state",),
        )
    if _state_has_empty_identifier(t1_state):
        return _unavailable(
            case,
            "T1_AUTHORITY_RELATIONSHIP_UNAVAILABLE",
            "Required T1 relational identifiers must be non-empty.",
            ("t1.authority_state",),
        )
    if t1_state.consumption_state != "UNUSED":
        return _unavailable(
            case,
            "T1_GRANT_NOT_CONSUMABLE",
            "The evaluated T1 grant was not established as unused.",
            ("t1.authority_state.consumption_state",),
        )

    mutation_chain_mismatches = _mutation_chain_mismatches(case)
    if mutation_chain_mismatches:
        return _unavailable(
            case,
            "T2_T3_HYBRID_STATE",
            "IMPLEMENTATION_OBLIGATION: ordered T2 mutations do not produce the exact observed T3 state.",
            mutation_chain_mismatches,
        )
    if _consumption_regenerated(case):
        return _unavailable(
            case,
            "CONSUMPTION_CONTINUITY_UNAVAILABLE",
            "IMPLEMENTATION_OBLIGATION: a consumed grant cannot be reset to unused by preparation, restart, recovery, or re-establishment.",
            ("consumption_state", "consumption_binding"),
        )

    differences = _state_differences(case, t1_state)
    grant_mutations = _grant_mutations(case)
    active_state = t1_state
    if differences or grant_mutations:
        if case.reestablishment_state is not FactState.KNOWN or case.reestablishment is None:
            return _unavailable(
                case,
                "T1_T3_RELATIONSHIP_UNAVAILABLE",
                "MODEL_LIMITATION: changed authority state lacks explicit current re-establishment.",
                differences or ("grant_id",),
            )
        reestablishment = case.reestablishment
        if reestablishment.previous_evidence_id != t1_state.evidence_id:
            return _unavailable(
                case,
                "REESTABLISHMENT_LINEAGE_UNAVAILABLE",
                "Current re-establishment is not linked to the evaluated T1 evidence.",
                ("reestablishment",),
            )
        if reestablishment.current.evidence_id == t1_state.evidence_id:
            return _unavailable(
                case,
                "REESTABLISHMENT_EVIDENCE_REUSED",
                "Changed authority-relevant state requires a distinct current evidence binding.",
                ("reestablishment",),
            )
        current_differences = _state_differences(case, reestablishment.current)
        if current_differences:
            return _unavailable(
                case,
                "REESTABLISHMENT_TARGET_MISMATCH",
                "The explicit re-establishment does not bind the exact current T3 state.",
                current_differences,
            )
        if _state_has_empty_identifier(reestablishment.current):
            return _unavailable(
                case,
                "REESTABLISHMENT_TARGET_MISMATCH",
                "Required re-established relational identifiers must be non-empty.",
                ("reestablishment",),
            )
        missing_mutations = _changes_are_represented(case, t1_state, reestablishment.current)
        if missing_mutations:
            return _unavailable(
                case,
                "T2_CHANGE_RELATIONSHIP_UNAVAILABLE",
                "Authority-relevant T1-to-T3 changes are not represented by exact T2 transitions.",
                missing_mutations,
            )
        active_state = reestablishment.current

    grant_scope_changed = any(
        getattr(t1_state, field) != getattr(active_state, field)
        for field in GRANT_SCOPE_FIELDS
    )
    grant_returns_to_prior_identity = bool(grant_mutations) and (
        active_state.grant_id == t1_state.grant_id
    )
    transition = case.grant_transition
    transition_valid = (
        case.grant_transition_state is FactState.KNOWN
        and transition is not None
        and transition.relationship == "AUTHORITY_PRESERVING"
        and transition.grant_path == _grant_path(case)
        and transition.previous == t1_state
        and transition.current == active_state
    )
    if transition is not None and not transition_valid:
        return _unavailable(
            case,
            "GRANT_TRANSITION_RELATIONSHIP_UNAVAILABLE",
            "MODEL_LIMITATION: the declared grant transition does not bind the exact observed grant path and authority states.",
            ("grant_transition",),
        )
    if (
        (grant_scope_changed and active_state.grant_id == t1_state.grant_id)
        or grant_returns_to_prior_identity
    ) and not transition_valid:
        return _unavailable(
            case,
            "GRANT_EFFECT_RELATIONSHIP_UNAVAILABLE",
            "MODEL_LIMITATION: the prior grant cannot be retargeted to changed exact authority scope without an explicit authority-preserving transition.",
            ("grant_transition",),
        )

    expected_execution_relation = {
        "execution_context": case.facts["execution_context"].value,
        "control_state": case.authority_tuple.control_state,
    }
    if not _relation_matches(
        case.facts["execution_control_binding"].value, expected_execution_relation
    ):
        return _unavailable(
            case,
            "EXECUTION_CONTROL_RELATIONSHIP_UNAVAILABLE",
            "IMPLEMENTATION_OBLIGATION: execution context is not exactly bound to control state.",
            ("execution_control_binding",),
        )

    expected_consumption_relation = {
        "grant_id": active_state.grant_id,
        "subject": case.authority_tuple.subject,
        "artifact": case.authority_tuple.artifact,
        "boundary_epoch": case.authority_tuple.boundary_epoch,
    }
    if not _relation_matches(
        case.facts["consumption_binding"].value, expected_consumption_relation
    ):
        return _unavailable(
            case,
            "CONSUMPTION_RELATIONSHIP_UNAVAILABLE",
            "IMPLEMENTATION_OBLIGATION: consumption state is not bound to the exact grant and effect.",
            ("consumption_binding",),
        )

    delegation = case.facts["delegation_binding"].value
    if active_state.subject_mode == "DIRECT":
        delegation_expected = {
            "relationship": "DIRECT",
            "subject": case.authority_tuple.subject,
            "artifact": case.authority_tuple.artifact,
            "control_state": case.authority_tuple.control_state,
            "boundary_epoch": case.authority_tuple.boundary_epoch,
            "applicable_boundary": case.facts["applicable_boundary"].value,
        }
    elif active_state.subject_mode == "DELEGATED":
        delegation_expected = {
            "relationship": "EXACT_DELEGATION",
            "delegator": delegation.get("delegator") if isinstance(delegation, Mapping) else None,
            "delegate": case.authority_tuple.subject,
            "artifact": case.authority_tuple.artifact,
            "control_state": case.authority_tuple.control_state,
            "boundary_epoch": case.authority_tuple.boundary_epoch,
            "applicable_boundary": case.facts["applicable_boundary"].value,
        }
    else:
        return _unavailable(
            case,
            "DELEGATION_RELATIONSHIP_UNAVAILABLE",
            "MODEL_LIMITATION: the evaluated subject relationship is not represented.",
            ("t1.authority_state.subject_mode",),
        )
    if (
        not _relation_matches(delegation, delegation_expected)
        or (
            active_state.subject_mode == "DELEGATED"
            and (
                not isinstance(delegation_expected["delegator"], str)
                or delegation_expected["delegator"] == ""
            )
        )
    ):
        return _unavailable(
            case,
            "DELEGATION_RELATIONSHIP_UNAVAILABLE",
            "IMPLEMENTATION_OBLIGATION: subject authority is not bound to the exact effect, state, boundary, and epoch.",
            ("delegation_binding",),
        )

    closure_expected = {
        "relationship": "EXACT_EFFECT",
        "source_artifact": case.authority_tuple.artifact,
        "target_artifact": case.authority_tuple.artifact,
    }
    if not _relation_matches(case.facts["closure_binding"].value, closure_expected):
        return _unavailable(
            case,
            "CLOSURE_RELATIONSHIP_UNAVAILABLE",
            "MODEL_LIMITATION: generic closure cannot authorize a distinct derived artifact.",
            ("closure_binding",),
        )

    return OracleResult(
        AuthorityOutcome.AUTHORIZED,
        (
            Reason(
                "CURRENT_AUTHORITY_ESTABLISHED",
                "All required current facts and relationships are established and no applicable prohibition applies.",
            ),
        ),
        _engaged(case),
    )
