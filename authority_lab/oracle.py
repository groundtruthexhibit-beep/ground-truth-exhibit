"""Deterministic oracle over public Authority Lab fixture state."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .model import (
    AuthorityOutcome,
    AuthorityStateBinding,
    BindingScope,
    FactState,
    INVARIANTS,
    MANDATORY_T3_FACTS,
    MUTATION_SPECS,
    MutationTargetKind,
    OBJECTIVE_BINDING_FACTS,
    ObjectiveBindingFacts,
    OracleInput,
    OracleResult,
    RELATIONAL_T3_FACTS,
    Reason,
    exact_value_equal,
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

STATE_MUTATION_TARGETS = tuple(
    dict.fromkeys(
        spec.target for spec in MUTATION_SPECS if spec.target_kind is MutationTargetKind.STATE
    )
)
RELATIONAL_MUTATION_TARGETS = tuple(
    spec.target for spec in MUTATION_SPECS if spec.target_kind is MutationTargetKind.RELATION
)
FACT_MUTATION_TARGETS = tuple(
    spec.target for spec in MUTATION_SPECS if spec.target_kind is MutationTargetKind.FACT
)
BINDING_MUTATION_TARGETS = tuple(
    spec.target for spec in MUTATION_SPECS if spec.target_kind is MutationTargetKind.BINDING
)

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

NEGATIVE_BINDING_STATES = {"INVALID", "REVOKED", "REJECTED", "SUPERSEDED"}


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


def _binding_scope_for_t3(case: OracleInput) -> BindingScope | None:
    boundary = case.facts.get("applicable_boundary")
    if boundary is None or boundary.state is not FactState.KNOWN:
        return None
    if not isinstance(boundary.value, str) or boundary.value == "":
        return None
    for fact_name, tuple_field in TUPLE_FACT_BINDINGS:
        fact = case.facts.get(fact_name)
        if (
            fact is None
            or fact.state is not FactState.KNOWN
            or fact.value != getattr(case.authority_tuple, tuple_field)
        ):
            return None
    return BindingScope(
        subject=case.authority_tuple.subject,
        artifact=case.authority_tuple.artifact,
        control_state=case.authority_tuple.control_state,
        identity_basis=case.authority_tuple.identity_basis,
        boundary_epoch=case.authority_tuple.boundary_epoch,
        decision=case.authority_tuple.decision,
        applicable_boundary=boundary.value,
    )


def _binding_scope_for_t1(case: OracleInput) -> BindingScope:
    state = case.t1_authority_state
    return BindingScope(
        subject=state.subject,
        artifact=state.artifact,
        control_state=state.control_state,
        identity_basis=state.identity_basis,
        boundary_epoch=state.boundary_epoch,
        decision=state.decision,
        applicable_boundary=state.applicable_boundary,
    )


def _binding_unavailable(
    case: OracleInput, phase: str, code: str, detail: str, facts: tuple[str, ...] = ()
) -> OracleResult:
    return _unavailable(case, f"{phase}_{code}", detail, facts)


def _admit_objective_contract(
    case: OracleInput,
    binding_facts: ObjectiveBindingFacts,
    expected_scope: BindingScope | None,
    phase: str,
) -> OracleResult:
    unavailable = tuple(
        name
        for name in OBJECTIVE_BINDING_FACTS
        if binding_facts.raw[name].state is FactState.UNKNOWN
    )
    conflicting = tuple(
        name
        for name in OBJECTIVE_BINDING_FACTS
        if binding_facts.raw[name].state is FactState.CONFLICTING
    )
    if expected_scope is None:
        unavailable = (*unavailable, "applicable_boundary")
    if unavailable or conflicting:
        return _binding_unavailable(
            case,
            phase,
            "OBJECTIVE_BINDING_UNAVAILABLE",
            "Required objective-binding facts are missing, unknown, or conflicting.",
            tuple(dict.fromkeys((*unavailable, *conflicting))),
        )

    objective = binding_facts.objective_identity
    contract = binding_facts.decision_contract_identity
    root = binding_facts.authority_root
    ordering = binding_facts.ordering
    if objective is None or contract is None or root is None or ordering is None:
        return _binding_unavailable(
            case,
            phase,
            "OBJECTIVE_BINDING_UNAVAILABLE",
            "Typed objective, contract, root, or ordering state is unavailable.",
        )
    assert expected_scope is not None

    if (
        root.boundary != expected_scope.applicable_boundary
        or root.boundary_epoch != expected_scope.boundary_epoch
        or root.root_id == expected_scope.subject
    ):
        return _binding_unavailable(
            case,
            phase,
            "AUTHORITY_ROOT_RELATIONSHIP_UNAVAILABLE",
            "The admitted root is not independently bound to the exact boundary and epoch.",
            ("authority_root",),
        )
    if (
        ordering.ordering_source_id != root.ordering_source_id
        or ordering.lineage != root.lineage
        or ordering.authority_generation != root.authority_generation
    ):
        return _binding_unavailable(
            case,
            phase,
            "AUTHORITATIVE_ORDERING_UNAVAILABLE",
            "Binding ordering is not established by the exact current root lineage.",
            ("binding_ordering",),
        )

    candidate_ids: dict[tuple[str, int], Any] = {}
    for candidate in binding_facts.candidates:
        key = (candidate.binding_id, candidate.binding_generation)
        prior = candidate_ids.get(key)
        if prior is not None and prior != candidate:
            return _binding_unavailable(
                case,
                phase,
                "OBJECTIVE_BINDING_CONFLICTING",
                "One binding identity and generation has conflicting candidate bodies.",
                ("objective_binding",),
            )
        candidate_ids[key] = candidate

    applicable = tuple(
        candidate
        for candidate in candidate_ids.values()
        if candidate.objective_id == objective.objective_id
        and candidate.objective_generation == objective.objective_generation
        and candidate.policy_id == objective.policy_id
        and candidate.policy_version == objective.policy_version
        and candidate.schema_id == contract.schema_id
        and candidate.scope == expected_scope
        and candidate.lineage == root.lineage
        and candidate.authority_generation == root.authority_generation
        and (
            (
                candidate.contract_id == contract.contract_id
                and candidate.contract_version == contract.contract_version
            )
            or (
                contract.derived_from != "NONE"
                and candidate.contract_id == contract.derived_from
            )
        )
    )
    selected = tuple(
        candidate
        for candidate in applicable
        if candidate.binding_id == ordering.head_binding_id
        and candidate.binding_generation == ordering.head_binding_generation
    )
    if len(selected) != 1:
        return _binding_unavailable(
            case,
            phase,
            "AUTHORITATIVE_ORDERING_UNAVAILABLE",
            "Authoritative ordering does not select exactly one applicable binding.",
            ("objective_binding", "binding_ordering"),
        )
    binding = selected[0]

    sources = tuple(
        source
        for source in set(binding_facts.sources)
        if source.root_id == root.root_id
        and source.source_id == binding.source_id
        and source.authority_generation == root.authority_generation
        and source.boundary == root.boundary
        and source.boundary_epoch == root.boundary_epoch
        and source.lineage == root.lineage
        and source.scope == expected_scope
    )
    if len(sources) != 1:
        return _binding_unavailable(
            case,
            phase,
            "BINDING_SOURCE_AUTHORITY_UNAVAILABLE",
            "The binding source lacks one exact independent root or delegation relationship.",
            ("binding_source_authority",),
        )
    source = sources[0]
    root_relationship = (
        source.relationship == "ROOT"
        and source.source_id == root.root_id
        and source.delegation_id == "NONE"
    )
    delegated_relationship = (
        source.relationship == "EXACT_DELEGATION"
        and source.source_id != root.root_id
        and source.delegation_id != "NONE"
    )
    producer_matches_source = (
        binding.producer_id == source.source_id
        and (
            (source.relationship == "ROOT" and binding.producer_kind == "AUTHORITY_ROOT")
            or (
                source.relationship == "EXACT_DELEGATION"
                and binding.producer_kind == "DELEGATE"
            )
        )
    )
    if (
        not (root_relationship or delegated_relationship)
        or not producer_matches_source
        or source.source_id == expected_scope.subject
    ):
        return _binding_unavailable(
            case,
            phase,
            "BINDING_SOURCE_AUTHORITY_UNAVAILABLE",
            "The candidate producer must exactly match a separately admitted root or delegate source.",
            ("objective_binding", "binding_source_authority"),
        )
    if source.status in {"REVOKED", "REJECTED"}:
        return OracleResult(
            AuthorityOutcome.DENIED,
            (
                Reason(
                    f"{phase}_BINDING_SOURCE_{source.status}",
                    "Current authoritative source or delegation state prohibits admission.",
                    ("binding_source_authority",),
                ),
            ),
            _engaged(case),
        )

    lifecycles = tuple(
        lifecycle
        for lifecycle in set(binding_facts.lifecycles)
        if lifecycle.binding_id == binding.binding_id
        and lifecycle.binding_generation == binding.binding_generation
        and lifecycle.source_id == binding.source_id
        and lifecycle.authority_generation == root.authority_generation
        and lifecycle.lineage == root.lineage
        and lifecycle.event_order == ordering.head_event_order
    )
    if len(lifecycles) != 1:
        return _binding_unavailable(
            case,
            phase,
            "BINDING_LIFECYCLE_UNAVAILABLE",
            "No unique authoritative lifecycle event establishes the selected binding state.",
            ("binding_lifecycle", "binding_ordering"),
        )
    lifecycle = lifecycles[0]
    if binding.disposition == "REJECT" or lifecycle.state in NEGATIVE_BINDING_STATES:
        return OracleResult(
            AuthorityOutcome.DENIED,
            (
                Reason(
                    f"{phase}_OBJECTIVE_BINDING_DENIED",
                    "Current authoritative binding state rejects, invalidates, revokes, or supersedes the exact use.",
                    ("objective_binding", "binding_lifecycle", "binding_ordering"),
                ),
            ),
            _engaged(case),
        )

    direct = (
        binding.contract_id == contract.contract_id
        and binding.contract_version == contract.contract_version
    )
    if not direct:
        transformations = tuple(
            transformation
            for transformation in set(binding_facts.transformations)
            if transformation.source_contract_id == binding.contract_id
            and transformation.source_contract_version == binding.contract_version
            and transformation.target_contract_id == contract.contract_id
            and transformation.target_contract_version == contract.contract_version
            and transformation.objective_id == objective.objective_id
            and transformation.objective_generation == objective.objective_generation
            and transformation.source_id == binding.source_id
            and transformation.authority_generation == root.authority_generation
            and transformation.boundary == root.boundary
            and transformation.boundary_epoch == root.boundary_epoch
            and transformation.lineage == root.lineage
            and transformation.scope == expected_scope
        )
        if len(transformations) != 1:
            return _binding_unavailable(
                case,
                phase,
                "TRANSFORMATION_ADMISSION_UNAVAILABLE",
                "Derived decision contract lacks one exact authoritative transformation admission.",
                ("contract_transformation_binding",),
            )
        if transformations[0].state in {"INVALID", "REVOKED", "REJECTED"}:
            return OracleResult(
                AuthorityOutcome.DENIED,
                (
                    Reason(
                        f"{phase}_TRANSFORMATION_ADMISSION_DENIED",
                        "The exact authoritative transformation admission is not usable.",
                        ("contract_transformation_binding",),
                    ),
                ),
                _engaged(case),
            )

    return OracleResult(
        AuthorityOutcome.AUTHORIZED,
        (
            Reason(
                f"{phase}_OBJECTIVE_BINDING_ADMITTED",
                "Exact current authoritative objective binding admits the decision contract.",
            ),
        ),
        _engaged(case),
    )


def _binding_mutation_mismatches(case: OracleInput) -> tuple[str, ...]:
    mismatches: list[str] = []
    for name in BINDING_MUTATION_TARGETS:
        before_fact = case.t1_binding_facts.raw[name]
        after_fact = case.t3_binding_facts.raw[name]
        before = before_fact.value if before_fact.state is FactState.KNOWN else before_fact.state.value
        after = after_fact.value if after_fact.state is FactState.KNOWN else after_fact.state.value
        mutations = _mutations_for(case, MutationTargetKind.BINDING, name)
        value = before
        for mutation in mutations:
            if not exact_value_equal(mutation.before, value):
                mismatches.append(name)
                break
            value = mutation.after
        else:
            if not exact_value_equal(value, after):
                mismatches.append(name)
    return tuple(dict.fromkeys(mismatches))


def _binding_identity_reuse_mismatches(case: OracleInput) -> tuple[str, ...]:
    before = case.t1_binding_facts
    after = case.t3_binding_facts
    mismatches: list[str] = []
    if (
        before.objective_identity is not None
        and after.objective_identity is not None
        and (
            before.objective_identity.objective_id,
            before.objective_identity.objective_generation,
        )
        == (
            after.objective_identity.objective_id,
            after.objective_identity.objective_generation,
        )
        and before.objective_identity != after.objective_identity
    ):
        mismatches.append("objective_identity")
    if (
        before.decision_contract_identity is not None
        and after.decision_contract_identity is not None
        and (
            before.decision_contract_identity.contract_id,
            before.decision_contract_identity.contract_version,
        )
        == (
            after.decision_contract_identity.contract_id,
            after.decision_contract_identity.contract_version,
        )
        and before.decision_contract_identity != after.decision_contract_identity
    ):
        mismatches.append("decision_contract_identity")
    if (
        before.authority_root is not None
        and after.authority_root is not None
        and (
            before.authority_root.root_id,
            before.authority_root.authority_generation,
        )
        == (after.authority_root.root_id, after.authority_root.authority_generation)
        and before.authority_root != after.authority_root
    ):
        mismatches.append("authority_root")
    prior_candidates = {
        (candidate.binding_id, candidate.binding_generation): candidate
        for candidate in before.candidates
    }
    for candidate in after.candidates:
        prior = prior_candidates.get((candidate.binding_id, candidate.binding_generation))
        if prior is not None and prior != candidate:
            mismatches.append("objective_binding")
    prior_transformations = {
        (transformation.transformation_id, transformation.transformation_generation): transformation
        for transformation in before.transformations
    }
    for transformation in after.transformations:
        prior = prior_transformations.get(
            (transformation.transformation_id, transformation.transformation_generation)
        )
        if prior is not None and prior != transformation:
            mismatches.append("contract_transformation_binding")
    return tuple(dict.fromkeys(mismatches))


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


def _mutations_for(
    case: OracleInput, kind: MutationTargetKind, target: str
) -> tuple[Any, ...]:
    return tuple(
        mutation
        for mutation in case.t2_mutations
        if mutation.target_kind is kind and mutation.target == target
    )


def _mutation_chain_mismatches(case: OracleInput) -> tuple[str, ...]:
    mismatches: list[str] = []
    for field in STATE_MUTATION_TARGETS:
        mutations = _mutations_for(case, MutationTargetKind.STATE, field)
        if not mutations:
            continue
        value = getattr(case.t1_authority_state, field)
        for mutation in mutations:
            if not exact_value_equal(mutation.before, value):
                mismatches.append(field)
                break
            value = mutation.after
        else:
            if not exact_value_equal(value, _current_state_value(case, field)):
                mismatches.append(field)
    for fact_name in RELATIONAL_MUTATION_TARGETS:
        mutations = _mutations_for(case, MutationTargetKind.RELATION, fact_name)
        if not mutations:
            continue
        value = mutations[0].before
        for mutation in mutations:
            if not exact_value_equal(mutation.before, value):
                mismatches.append(fact_name)
                break
            value = mutation.after
        else:
            fact = case.facts.get(fact_name)
            observed = (
                fact.value
                if fact is not None and fact.state is FactState.KNOWN
                else fact.state.value if fact is not None else FactState.UNKNOWN.value
            )
            if not exact_value_equal(value, observed):
                mismatches.append(fact_name)
    for fact_name in FACT_MUTATION_TARGETS:
        mutations = _mutations_for(case, MutationTargetKind.FACT, fact_name)
        if not mutations:
            continue
        value = mutations[0].before
        for mutation in mutations:
            if not exact_value_equal(mutation.before, value):
                mismatches.append(fact_name)
                break
            value = mutation.after
        else:
            fact = case.facts.get(fact_name)
            observed = (
                fact.value
                if fact is not None and fact.state is FactState.KNOWN
                else fact.state.value if fact is not None else FactState.UNKNOWN.value
            )
            if not exact_value_equal(value, observed):
                mismatches.append(fact_name)
    return tuple(dict.fromkeys(mismatches))


def _grant_mutations(case: OracleInput) -> tuple[Any, ...]:
    return _mutations_for(case, MutationTargetKind.STATE, "grant_id")


def _grant_path(case: OracleInput) -> tuple[str, ...]:
    mutations = _grant_mutations(case)
    if not mutations:
        current = _current_state_value(case, "grant_id")
        return (case.t1_authority_state.grant_id, current)
    return (case.t1_authority_state.grant_id, *(mutation.after for mutation in mutations))


def _consumption_regenerated(case: OracleInput) -> bool:
    consumed = case.t1_authority_state.consumption_state == "CONSUMED"
    for mutation in _mutations_for(case, MutationTargetKind.STATE, "consumption_state"):
        if mutation.after == "CONSUMED":
            consumed = True
        elif consumed and mutation.after == "UNUSED":
            return True
    return False


def _has_exact_mutation(case: OracleInput, target: str, before: Any, after: Any) -> bool:
    return any(
        exact_value_equal(mutation.before, before)
        and exact_value_equal(mutation.after, after)
        for mutation in _mutations_for(case, MutationTargetKind.STATE, target)
    )


def _changes_are_represented(
    case: OracleInput, before: AuthorityStateBinding, after: AuthorityStateBinding
) -> tuple[str, ...]:
    missing: list[str] = []
    for state_field in (
        "subject",
        "artifact",
        "identity_basis",
        "boundary_epoch",
        "applicable_boundary",
        "consumption_state",
    ):
        old = getattr(before, state_field)
        new = getattr(after, state_field)
        if old != new and not _has_exact_mutation(case, state_field, old, new):
            missing.append(state_field)
    context_or_control_changed = (
        before.execution_context != after.execution_context
        or before.control_state != after.control_state
    )
    if context_or_control_changed and not (
        _has_exact_mutation(
            case,
            "execution_context",
            before.execution_context,
            after.execution_context,
        )
        or _has_exact_mutation(
            case,
            "control_state",
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
    if case.schema_version == "authority-lab-v0":
        return _unavailable(
            case,
            "LEGACY_SCHEMA_UNAVAILABLE",
            "Authority Lab v0 has no objective-binding admission and cannot authorize.",
            ("schema_version", "objective_binding"),
        )

    unknown_mutation_fields = tuple(
        sorted(
            {mutation.field for mutation in case.t2_mutations if mutation.target is None},
            key=lambda value: value.encode("utf-8"),
        )
    )
    if unknown_mutation_fields:
        return _unavailable(
            case,
            "UNKNOWN_MUTATION_FIELD",
            "One or more structurally valid mutation fields have no admitted authority semantics.",
            unknown_mutation_fields,
        )

    t3_binding_result = _admit_objective_contract(
        case, case.t3_binding_facts, _binding_scope_for_t3(case), "T3"
    )
    if t3_binding_result.outcome is AuthorityOutcome.DENIED:
        return t3_binding_result

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
    t1_binding_result = _admit_objective_contract(
        case, case.t1_binding_facts, _binding_scope_for_t1(case), "T1"
    )
    if t1_binding_result.outcome is not AuthorityOutcome.AUTHORIZED:
        return t1_binding_result
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
    binding_identity_reuse = _binding_identity_reuse_mismatches(case)
    if binding_identity_reuse:
        return _unavailable(
            case,
            "OBJECTIVE_BINDING_IDENTITY_REUSED",
            "Objective, contract, root, or binding semantics changed without a new identity or generation.",
            binding_identity_reuse,
        )
    binding_mutation_mismatches = _binding_mutation_mismatches(case)
    if binding_mutation_mismatches:
        return _unavailable(
            case,
            "OBJECTIVE_BINDING_CONTINUITY_UNAVAILABLE",
            "Ordered T2 mutations do not produce the exact current objective-binding state.",
            binding_mutation_mismatches,
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
    continuity_mutations = tuple(
        mutation
        for mutation in case.t2_mutations
        if mutation.target_kind
        in {
            MutationTargetKind.STATE,
            MutationTargetKind.RELATION,
            MutationTargetKind.FACT,
        }
    )
    active_state = t1_state
    if differences or continuity_mutations:
        if case.reestablishment_state is not FactState.KNOWN or case.reestablishment is None:
            return _unavailable(
                case,
                "T1_T3_RELATIONSHIP_UNAVAILABLE",
                "MODEL_LIMITATION: changed authority state lacks explicit current re-establishment.",
                differences
                or tuple(dict.fromkeys(mutation.target for mutation in continuity_mutations)),
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

    if t3_binding_result.outcome is not AuthorityOutcome.AUTHORIZED:
        return t3_binding_result

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
