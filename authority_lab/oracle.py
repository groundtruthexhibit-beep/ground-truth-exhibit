"""Deterministic oracle over public Authority Lab fixture state."""

from __future__ import annotations

from .model import (
    AuthorityOutcome,
    FactState,
    INVARIANTS,
    MANDATORY_T3_FACTS,
    OracleInput,
    OracleResult,
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
    "closure_binding": "EXPLICIT",
}


def _engaged(case: OracleInput) -> tuple[str, ...]:
    selected = set(case.applicable_invariants)
    return tuple(invariant for invariant in INVARIANTS if invariant in selected)


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
                "One or more authority-relevant facts are not established.",
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

    tuple_mismatches = []
    for fact_name, tuple_field in TUPLE_FACT_BINDINGS:
        if case.facts[fact_name].value != getattr(case.authority_tuple, tuple_field):
            tuple_mismatches.append(fact_name)
    if case.authority_tuple.decision is not case.t1_result:
        tuple_mismatches.append("decision_binding")
    if tuple_mismatches:
        return OracleResult(
            AuthorityOutcome.UNAVAILABLE,
            (
                Reason(
                    "EXACT_TUPLE_MISMATCH",
                    "Observed facts do not establish the exact requested authority tuple.",
                    tuple(tuple_mismatches),
                ),
            ),
            _engaged(case),
        )

    if case.facts["decision_binding"].value not in case.t1_evidence:
        return OracleResult(
            AuthorityOutcome.UNAVAILABLE,
            (
                Reason(
                    "DECISION_EVIDENCE_BINDING_MISMATCH",
                    "The current decision binding is not bound to the T1 evidence.",
                    ("decision_binding",),
                ),
            ),
            _engaged(case),
        )

    missing_value_requirements = tuple(
        name for name in required_facts if name not in case.required_values
    )
    if missing_value_requirements:
        return OracleResult(
            AuthorityOutcome.UNAVAILABLE,
            (
                Reason(
                    "REQUIRED_VALUE_UNSPECIFIED",
                    "Authority-permitting values are not specified for required facts.",
                    missing_value_requirements,
                ),
            ),
            _engaged(case),
        )

    value_mismatches = tuple(
        name
        for name in required_facts
        if case.facts[name].value != case.required_values[name]
    )
    if value_mismatches:
        return OracleResult(
            AuthorityOutcome.UNAVAILABLE,
            (
                Reason(
                    "REQUIRED_VALUE_MISMATCH",
                    "Established facts do not match the authority-permitting values required by the case schema.",
                    value_mismatches,
                ),
            ),
            _engaged(case),
        )

    if case.t2_creates_authority:
        return OracleResult(
            AuthorityOutcome.UNAVAILABLE,
            (
                Reason(
                    "T2_AUTHORITY_CLAIM",
                    "T2 preparation is non-authoritative and cannot create or preserve authority.",
                ),
            ),
            _engaged(case),
        )

    if case.t1_result is AuthorityOutcome.UNAVAILABLE:
        return OracleResult(
            AuthorityOutcome.UNAVAILABLE,
            (Reason("T1_UNAVAILABLE", "The necessary T1 authorization was not established."),),
            _engaged(case),
        )
    if case.t1_result is AuthorityOutcome.DENIED:
        return OracleResult(
            AuthorityOutcome.DENIED,
            (Reason("T1_DENIED", "The established T1 decision prohibits the transition."),),
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
        return OracleResult(
            AuthorityOutcome.UNAVAILABLE,
            (
                Reason(
                    "VALUE_NOT_AUTHORITY_PERMITTING",
                    "Known state alone does not establish an authority-permitting value.",
                    nonpermitting_values,
                ),
            ),
            _engaged(case),
        )

    return OracleResult(
        AuthorityOutcome.AUTHORIZED,
        (Reason("CURRENT_AUTHORITY_ESTABLISHED", "All required current facts are established and no applicable prohibition applies."),),
        _engaged(case),
    )
