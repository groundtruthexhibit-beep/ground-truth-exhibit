"""Deterministic oracle over public Authority Lab fixture state."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from .commitment import commitment_digest, state_key_digest, verifier_state_digest

from .model import (
    AuthorityOutcome,
    AuthorityStateBinding,
    BindingScope,
    ContinuityEffect,
    FactState,
    INVARIANTS,
    MANDATORY_T3_FACTS,
    MUTATION_SPECS,
    MutationTargetKind,
    OBJECTIVE_BINDING_FACTS,
    OBSERVATION_PROFILE_ID,
    OBSERVATION_PROFILE_VERSION,
    OBSERVATION_SCOPE_FAMILIES,
    ObservationBinding,
    ObservationHandoff,
    ObservationSegment,
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
NEGATIVE_OBSERVATION_STATES = {"INVALID", "REVOKED", "REJECTED", "SUPERSEDED"}

SUCCESSOR_BREAK_EFFECTS = frozenset(
    {
        ContinuityEffect.IDENTITY_DISCONTINUITY,
        ContinuityEffect.NON_RESTORABLE_LINEAGE,
        ContinuityEffect.TERMINAL_DISCONTINUITY,
    }
)
GRANT_NONPORTABLE_EFFECTS = frozenset(
    {
        *SUCCESSOR_BREAK_EFFECTS,
        ContinuityEffect.GRANT_USE_DISCONTINUITY,
    }
)


@dataclass(frozen=True)
class ContinuityPath:
    effects: frozenset[ContinuityEffect]
    observation_scope_families: frozenset[str]
    aba_targets: tuple[str, ...]

    @property
    def successor_break(self) -> bool:
        # Any authority-relevant ABA path is history-discontinuous even when
        # the individual field would otherwise support non-terminal rebinding.
        return bool(self.effects & SUCCESSOR_BREAK_EFFECTS) or bool(self.aba_targets)

    @property
    def grant_nonportable(self) -> bool:
        return bool(self.effects & GRANT_NONPORTABLE_EFFECTS)


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


def analyze_continuity_path(case: OracleInput) -> ContinuityPath:
    """Retain every semantic path effect, including endpoint-restoring ABA edges."""
    histories: dict[tuple[MutationTargetKind, str], list[Any]] = {}
    effects: set[ContinuityEffect] = set()
    observation_scopes: set[str] = set()
    aba_targets: list[str] = []
    for mutation in case.t2_mutations:
        if mutation.target_kind is None or mutation.target is None:
            continue
        effects.update(mutation.continuity_effects)
        observation_scopes.update(mutation.observation_scope_families)
        key = (mutation.target_kind, mutation.target)
        history = histories.setdefault(key, [mutation.before])
        if any(exact_value_equal(mutation.after, prior) for prior in history):
            aba_targets.append(mutation.target)
        history.append(mutation.after)
    return ContinuityPath(
        frozenset(effects),
        frozenset(observation_scopes),
        tuple(dict.fromkeys(aba_targets)),
    )


def _fresh_successor_chain_established(
    case: OracleInput, active_state: AuthorityStateBinding
) -> bool:
    """Require an independently current identity, epoch, grant, and objective chain."""
    t1 = case.t1_authority_state
    before = case.t1_binding_facts
    after = case.t3_binding_facts
    if (
        active_state.identity_basis == t1.identity_basis
        or active_state.execution_context == t1.execution_context
        or active_state.boundary_epoch == t1.boundary_epoch
        or active_state.grant_id == t1.grant_id
    ):
        return False
    if case.grant_transition is not None:
        return False
    if (
        before.authority_root is None
        or after.authority_root is None
        or before.ordering is None
        or after.ordering is None
    ):
        return False
    before_root = before.authority_root
    after_root = after.authority_root
    if (
        after_root.boundary_epoch != active_state.boundary_epoch
        or (
            after_root.root_id,
            after_root.authority_generation,
            after_root.lineage,
            after_root.boundary_epoch,
        )
        == (
            before_root.root_id,
            before_root.authority_generation,
            before_root.lineage,
            before_root.boundary_epoch,
        )
    ):
        return False
    if (
        after.ordering.head_event_order <= before.ordering.head_event_order
        or (
            after.ordering.head_binding_id,
            after.ordering.head_binding_generation,
        )
        == (
            before.ordering.head_binding_id,
            before.ordering.head_binding_generation,
        )
    ):
        return False
    return True


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


def _has_exact_mutation_path(
    case: OracleInput, target: str, before: Any, after: Any
) -> bool:
    mutations = _mutations_for(case, MutationTargetKind.STATE, target)
    return bool(mutations) and exact_value_equal(mutations[0].before, before) and exact_value_equal(
        mutations[-1].after, after
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
        if old != new and not _has_exact_mutation_path(case, state_field, old, new):
            missing.append(state_field)
    context_or_control_changed = (
        before.execution_context != after.execution_context
        or before.control_state != after.control_state
    )
    if context_or_control_changed and not (
        _has_exact_mutation_path(
            case,
            "execution_context",
            before.execution_context,
            after.execution_context,
        )
        or _has_exact_mutation_path(
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


def _observation_unavailable(
    case: OracleInput, code: str, detail: str, facts: tuple[str, ...] = ()
) -> OracleResult:
    return _unavailable(case, code, detail, facts)


def _observation_denied(
    case: OracleInput, state: str, detail: str, facts: tuple[str, ...]
) -> OracleResult:
    return OracleResult(
        AuthorityOutcome.DENIED,
        (Reason(f"OBSERVATION_SOURCE_{state}", detail, facts),),
        _engaged(case),
    )


def _valid_handoff(
    binding: ObservationBinding,
    handoff: ObservationHandoff,
    before: ObservationSegment,
    after: ObservationSegment,
    family: str,
) -> bool:
    return (
        handoff.source_id == binding.source_id
        and handoff.authority_generation == binding.authority_generation
        and handoff.boundary == binding.boundary
        and handoff.boundary_epoch == binding.boundary_epoch
        and handoff.lineage == binding.lineage
        and handoff.from_observer_id == before.observer_id
        and handoff.from_observer_generation == before.observer_generation
        and handoff.to_observer_id == after.observer_id
        and handoff.to_observer_generation == after.observer_generation
        and handoff.from_segment_id == before.segment_id
        and handoff.to_segment_id == after.segment_id
        and family in handoff.scope_families
        and handoff.handoff_anchor_id in {before.end_anchor_id, after.start_anchor_id}
        and before.end_event_order <= handoff.handoff_event_order
        and handoff.handoff_event_order <= after.start_event_order
    )


def _evaluate_commitment_envelope(
    case: OracleInput,
    binding: ObservationBinding,
    root: Any,
    segments: Mapping[str, ObservationSegment],
) -> OracleResult:
    """Require a verified, uniquely checkpointed head backed by caller-owned state."""
    envelopes = [record.values for record in binding.commitment_envelopes]
    verifiers = [record.values for record in binding.commitment_verifiers]
    verifications = [record.values for record in binding.commitment_verifications]
    links = [record.values for record in binding.commitment_links]
    checkpoints = [record.values for record in binding.commitment_checkpoints]
    if not envelopes or not verifiers or not verifications or not links or not checkpoints:
        return _observation_unavailable(
            case, "OBSERVATION_COMMITMENT_UNIQUENESS_UNAVAILABLE",
            "Observation records lack an exact verified commitment and durable unique-head checkpoint.",
            ("evidence_binding", "freshness"),
        )

    logical: dict[tuple[Any, ...], str] = {}
    stream_heads: dict[tuple[str, int], Mapping[str, Any]] = {}
    for envelope in envelopes:
        key = tuple(envelope[name] for name in (
            "observation_binding_id", "observation_binding_generation", "observer_id",
            "observer_generation", "stream_id", "stream_generation", "logical_position",
            "start_event_order", "end_event_order", "start_sequence", "end_sequence",
        ))
        previous = logical.get(key)
        if previous is not None and previous != envelope["commitment_digest"]:
            return _observation_unavailable(
                case, "OBSERVATION_COMMITMENT_EQUIVOCATION",
                "The same logical observation position has incompatible commitments.",
                ("evidence_binding",),
            )
        logical[key] = envelope["commitment_digest"]
        named = [segments.get(identifier) for identifier in envelope["segment_ids"]]
        if any(item is None for item in named):
            return _observation_unavailable(case, "OBSERVATION_COMMITMENT_CONFLICTING", "A commitment names an unavailable segment.", ("evidence_binding",))
        exact_segments = [item for item in named if item is not None]
        digest = commitment_digest(envelope, exact_segments)
        observer = next((item for item in binding.observers if item.observer_id == envelope["observer_id"] and item.observer_generation == envelope["observer_generation"]), None)
        stream = sorted(
            (item for item in segments.values() if item.stream_id == envelope["stream_id"] and item.stream_generation == envelope["stream_generation"]),
            key=lambda value: (value.start_event_order, value.start_sequence, value.segment_id),
        )
        if (
            envelope["relationship"] != "OBSERVATION_HISTORY_COMMITMENT"
            or envelope["commitment_format"] != "AUTHORITY-LAB-OBSERVATION-COMMITMENT-V1"
            or envelope["commitment_digest_algorithm"] != "SHA-256"
            or digest != envelope["canonical_payload_digest"]
            or digest != envelope["commitment_digest"]
            or observer is None
            or observer.observer_identity_basis != envelope["observer_identity_basis"]
            or tuple(item.segment_id for item in sorted(stream, key=lambda value: (value.start_event_order, value.start_sequence, value.segment_id))) != envelope["segment_ids"]
            or any(item.stream_commitment != digest for item in stream)
            or not stream
            or envelope["start_anchor_id"] != stream[0].start_anchor_id
            or envelope["start_event_order"] != stream[0].start_event_order
            or envelope["end_anchor_id"] != stream[-1].end_anchor_id
            or envelope["end_event_order"] != stream[-1].end_event_order
            or envelope["start_sequence"] != stream[0].start_sequence
            or envelope["end_sequence"] != stream[-1].end_sequence
            or tuple(envelope["scope_families"]) != tuple(OBSERVATION_SCOPE_FAMILIES)
            or envelope["observation_binding_id"] != binding.observation_binding_id
            or envelope["observation_binding_generation"] != binding.observation_binding_generation
            or envelope["objective_binding_id"] != binding.objective_binding_id
            or envelope["objective_binding_generation"] != binding.objective_binding_generation
            or envelope["decision_contract_id"] != binding.decision_contract_id
            or envelope["decision_contract_version"] != binding.decision_contract_version
            or envelope["source_id"] != root.root_id
            or envelope["authority_generation"] != root.authority_generation
            or envelope["boundary"] != root.boundary
            or envelope["boundary_epoch"] != root.boundary_epoch
            or envelope["lineage"] != root.lineage
            or envelope["ordering_source_id"] != root.ordering_source_id
        ):
            return _observation_unavailable(case, "OBSERVATION_COMMITMENT_CONFLICTING", "The commitment body is not exact for the admitted observation history.", ("evidence_binding",))
        stream_heads[(envelope["stream_id"], envelope["stream_generation"])] = envelope

        verifier_matches = [item for item in verifiers if item["verifier_id"] not in {case.authority_tuple.subject, envelope["observer_id"], root.root_id, root.ordering_source_id} and item["role"] == "OBSERVATION_COMMITMENT_APPRAISER" and tuple(item["scope_families"]) == tuple(OBSERVATION_SCOPE_FAMILIES) and item["source_id"] == root.root_id and item["authority_generation"] == root.authority_generation and item["boundary"] == root.boundary and item["boundary_epoch"] == root.boundary_epoch and item["lineage"] == root.lineage and item["ordering_source_id"] == root.ordering_source_id and item["lifecycle_state"] == "ACTIVE"]
        verified = [item for item in verifications if item["commitment_id"] == envelope["commitment_id"] and item["commitment_digest"] == digest and item["canonical_payload_digest"] == digest and item["signature_evidence_id"] == envelope["signature_evidence_id"] and item["issuer_key_id"] == envelope["issuer_key_id"] and item["issuer_key_generation"] == envelope["issuer_key_generation"] and item["freshness_challenge_id"] == envelope["freshness_challenge_id"] and item["verification_event_order"] <= binding.t3_anchor.event_order and item["disposition"] == "VERIFIED" and any(v["verifier_id"] == item["verifier_id"] and v["verifier_generation"] == item["verifier_generation"] for v in verifier_matches)]
        if len(verified) != 1:
            return _observation_unavailable(case, "OBSERVATION_COMMITMENT_AUTHENTICITY_UNAVAILABLE", "No exact independently admitted verifier establishes commitment authenticity.", ("evidence_binding",))
        link_matches = [item for item in links if item["to_commitment_id"] == envelope["commitment_id"] and item["to_commitment_digest"] == digest and item["to_logical_position"] == envelope["logical_position"]]
        if len(link_matches) != 1 or (envelope["logical_position"] == 0 and link_matches[0]["relationship"] != "GENESIS") or (envelope["logical_position"] > 0 and link_matches[0]["relationship"] not in {"EXTENDS", "CORRECTS", "SUPERSEDES"}) or link_matches[0]["from_commitment_id"] != envelope["predecessor_commitment_id"] or link_matches[0]["from_commitment_digest"] != envelope["predecessor_commitment_digest"] or link_matches[0]["from_logical_position"] != max(envelope["logical_position"] - 1, 0) or link_matches[0]["stream_id"] != envelope["stream_id"] or link_matches[0]["stream_generation"] != envelope["stream_generation"] or link_matches[0]["ordering_source_id"] != root.ordering_source_id or link_matches[0]["source_id"] != root.root_id or link_matches[0]["authority_generation"] != root.authority_generation or link_matches[0]["boundary"] != root.boundary or link_matches[0]["boundary_epoch"] != root.boundary_epoch or link_matches[0]["lineage"] != root.lineage or not any(v["verifier_id"] == link_matches[0]["verifier_id"] and v["verifier_generation"] == link_matches[0]["verifier_generation"] for v in verifier_matches):
            return _observation_unavailable(case, "OBSERVATION_COMMITMENT_CONTINUITY_UNAVAILABLE", "The commitment lacks one exact append-only predecessor relationship.", ("evidence_binding",))

        candidate_checkpoints = [item for item in checkpoints if item["head_commitment_id"] == envelope["commitment_id"] and item["head_commitment_digest"] == digest and item["head_logical_position"] == envelope["logical_position"] and item["stream_id"] == envelope["stream_id"] and item["stream_generation"] == envelope["stream_generation"]]
        if len(candidate_checkpoints) != 1:
            return _observation_unavailable(case, "OBSERVATION_COMMITMENT_UNIQUENESS_UNAVAILABLE", "No unique current checkpoint selects this commitment.", ("evidence_binding",))
        checkpoint = candidate_checkpoints[0]
        if checkpoint["relationship"] != "UNIQUE_CURRENT_COMMITMENT_HEAD" or checkpoint["observation_binding_id"] != binding.observation_binding_id or checkpoint["observation_binding_generation"] != binding.observation_binding_generation or checkpoint["ordering_source_id"] != root.ordering_source_id or checkpoint["source_id"] != root.root_id or checkpoint["authority_generation"] != root.authority_generation or checkpoint["boundary"] != root.boundary or checkpoint["boundary_epoch"] != root.boundary_epoch or checkpoint["lineage"] != root.lineage or checkpoint["freshness_challenge_id"] != envelope["freshness_challenge_id"] or checkpoint["checkpoint_event_order"] > binding.t3_anchor.event_order or checkpoint["lifecycle_state"] != "ACTIVE" or verifier_state_digest(checkpoint) != checkpoint["current_verifier_state_digest"]:
            return _observation_unavailable(case, "OBSERVATION_COMMITMENT_UNIQUENESS_UNAVAILABLE", "The current checkpoint is not exact or independently ordered.", ("evidence_binding",))
        context = [item for item in case.trusted_commitment_context if item.get("stream_id") == envelope["stream_id"] and item.get("stream_generation") == envelope["stream_generation"]]
        expected_key = state_key_digest({**envelope, "source_id": root.root_id, "authority_generation": root.authority_generation, "boundary": root.boundary, "boundary_epoch": root.boundary_epoch, "lineage": root.lineage, "ordering_source_id": root.ordering_source_id})
        if len(context) != 1 or context[0].get("exact_state_key_digest") != expected_key:
            return _observation_unavailable(case, "OBSERVATION_VERIFIER_STATE_UNAVAILABLE", "Harness-owned durable verifier state is unavailable for the exact stream lineage.", ("evidence_binding",))
        trusted = context[0]
        if trusted.get("previous_verifier_state_digest") != checkpoint["previous_verifier_state_digest"] or trusted.get("current_verifier_state_digest") != checkpoint["current_verifier_state_digest"] or trusted.get("head_commitment_digest") != digest or trusted.get("checkpoint_id") != checkpoint["checkpoint_id"] or trusted.get("freshness_challenge_id") != envelope["freshness_challenge_id"]:
            reason = "OBSERVATION_COMMITMENT_REPLAY" if trusted.get("head_logical_position", -1) > envelope["logical_position"] else "OBSERVATION_VERIFIER_ROLLBACK"
            return _observation_unavailable(case, reason, "The candidate commitment does not advance the independently retained durable verifier state.", ("evidence_binding", "freshness"))

    witnesses = [record.values for record in binding.commitment_witnesses]
    for checkpoint in checkpoints:
        applicable = [item for item in witnesses if item["checkpoint_id"] == checkpoint["checkpoint_id"] and item["checkpoint_generation"] == checkpoint["checkpoint_generation"]]
        if applicable and any(item["head_commitment_id"] != checkpoint["head_commitment_id"] or item["head_commitment_digest"] != checkpoint["head_commitment_digest"] or item["disposition"] != "CONFIRMED" for item in applicable):
            return _observation_unavailable(case, "OBSERVATION_WITNESS_CONFLICTING", "Witness evidence conflicts with the independently ordered commitment checkpoint.", ("evidence_binding",))

    freshness = case.observation_freshness
    selected = [item for item in stream_heads.values() if freshness is not None and item["commitment_id"] == freshness.commitment_id and item["commitment_digest"] == freshness.commitment_digest]
    if len(selected) != 1:
        return _observation_unavailable(case, "OBSERVATION_FRESHNESS_UNAVAILABLE", "Freshness does not select one exact durable commitment head.", ("freshness",))
    head = selected[0]
    checkpoint = next(item for item in checkpoints if item["head_commitment_id"] == head["commitment_id"])
    if freshness is None or freshness.checkpoint_id != checkpoint["checkpoint_id"] or freshness.checkpoint_generation != checkpoint["checkpoint_generation"] or freshness.verifier_state_id != checkpoint["verifier_state_id"] or freshness.verifier_state_generation != checkpoint["verifier_state_generation"] or freshness.verifier_state_digest != checkpoint["current_verifier_state_digest"] or freshness.freshness_challenge_id != checkpoint["freshness_challenge_id"]:
        return _observation_unavailable(case, "OBSERVATION_FRESHNESS_UNAVAILABLE", "Verifier-bound freshness is stale, self-issued, or not bound to the current checkpoint.", ("freshness",))
    return OracleResult(AuthorityOutcome.AUTHORIZED, (Reason("OBSERVATION_COMMITMENT_ESTABLISHED", "A current authentic uniquely checkpointed observation history is established.", ("evidence_binding", "freshness")),), _engaged(case))


def _evaluate_observation(case: OracleInput) -> OracleResult:
    binding = case.observation_binding
    if binding is None:
        return _observation_unavailable(
            case,
            "OBSERVATION_ADMISSION_UNAVAILABLE",
            "A strict root-issued observation binding is not established.",
            ("evidence_binding",),
        )
    freshness = case.observation_freshness
    if freshness is None:
        return _observation_unavailable(
            case,
            "OBSERVATION_FRESHNESS_UNAVAILABLE",
            "A strict observation freshness relationship is not established at T3.",
            ("freshness",),
        )

    facts = case.t3_binding_facts
    root = facts.authority_root
    contract = facts.decision_contract_identity
    ordering = facts.ordering
    if root is None or contract is None or ordering is None:
        return _observation_unavailable(
            case,
            "OBSERVATION_ADMISSION_UNAVAILABLE",
            "Observation admission lacks the independently established current root context.",
            ("authority_root", "binding_ordering"),
        )
    selected = tuple(
        candidate
        for candidate in facts.candidates
        if candidate.binding_id == ordering.head_binding_id
        and candidate.binding_generation == ordering.head_binding_generation
    )
    if len(selected) != 1:
        return _observation_unavailable(
            case,
            "OBSERVATION_ADMISSION_UNAVAILABLE",
            "Observation admission cannot identify one exact selected objective binding.",
            ("objective_binding", "binding_ordering"),
        )
    objective_binding = selected[0]
    if (
        binding.profile_id != OBSERVATION_PROFILE_ID
        or binding.profile_version != OBSERVATION_PROFILE_VERSION
        or binding.objective_binding_id != objective_binding.binding_id
        or binding.objective_binding_generation != objective_binding.binding_generation
        or binding.decision_contract_id != contract.contract_id
        or binding.decision_contract_version != contract.contract_version
        or binding.source_id != root.root_id
        or binding.authority_generation != root.authority_generation
        or binding.boundary != root.boundary
        or binding.boundary_epoch != root.boundary_epoch
        or binding.lineage != root.lineage
        or binding.ordering_source_id != root.ordering_source_id
        or binding.source_id == case.authority_tuple.subject
    ):
        return _observation_unavailable(
            case,
            "OBSERVATION_ADMISSION_UNAVAILABLE",
            "Observation admission is not issued by the exact current authority root for this binding and boundary.",
            ("evidence_binding", "authority_root", "objective_binding"),
        )
    if binding.t3_anchor.event_order < binding.t1_anchor.event_order:
        return _observation_unavailable(
            case,
            "OBSERVATION_ORDERING_UNAVAILABLE",
            "The observation interval is not authoritatively ordered from T1 through T3.",
            ("evidence_binding",),
        )

    lifecycle_ids: dict[str, Any] = {}
    lifecycle_heads: dict[tuple[str, str, int], Any] = {}
    for record in binding.lifecycle_records:
        prior = lifecycle_ids.get(record.record_id)
        if prior is not None and prior != record:
            return _observation_unavailable(
                case,
                "OBSERVATION_CONFLICTING",
                "One lifecycle record identity has conflicting bodies.",
                ("evidence_binding",),
            )
        lifecycle_ids[record.record_id] = record
        if (
            record.source_id != root.root_id
            or record.authority_generation != root.authority_generation
            or record.boundary != root.boundary
            or record.boundary_epoch != root.boundary_epoch
            or record.lineage != root.lineage
            or record.event_order > binding.t3_anchor.event_order
        ):
            return _observation_unavailable(
                case,
                "OBSERVATION_ORDERING_UNAVAILABLE",
                "Observation lifecycle state is not ordered by the exact current root lineage.",
                ("evidence_binding",),
            )
        key = (record.target_kind, record.target_id, record.target_generation)
        head = lifecycle_heads.get(key)
        if head is None or record.event_order > head.event_order:
            lifecycle_heads[key] = record
        elif record.event_order == head.event_order and record != head:
            return _observation_unavailable(
                case,
                "OBSERVATION_CONFLICTING",
                "One observation lifecycle target has conflicting current heads.",
                ("evidence_binding",),
            )

    binding_head = lifecycle_heads.get(
        ("OBSERVATION_BINDING", binding.observation_binding_id, binding.observation_binding_generation)
    )
    if binding_head is None:
        return _observation_unavailable(
            case,
            "OBSERVATION_ADMISSION_UNAVAILABLE",
            "The observation binding has no current root-issued lifecycle head.",
            ("evidence_binding",),
        )
    if binding_head.state in NEGATIVE_OBSERVATION_STATES:
        return _observation_denied(
            case,
            binding_head.state,
            "Current root-issued lifecycle evidence rejects the observation binding.",
            ("evidence_binding",),
        )

    observers: dict[tuple[str, int], Any] = {}
    for observer in binding.observers:
        key = (observer.observer_id, observer.observer_generation)
        prior = observers.get(key)
        if prior is not None and prior != observer:
            return _observation_unavailable(
                case,
                "OBSERVATION_CONFLICTING",
                "One observer identity and generation has conflicting admissions.",
                ("evidence_binding",),
            )
        observers[key] = observer
        if (
            observer.observation_binding_id != binding.observation_binding_id
            or observer.observation_binding_generation != binding.observation_binding_generation
            or observer.observer_id
            in {
                case.authority_tuple.subject,
                binding.source_id,
                root.root_id,
                root.ordering_source_id,
            }
        ):
            return _observation_unavailable(
                case,
                "OBSERVATION_ADMISSION_UNAVAILABLE",
                "Observer identity or admission is self-issued, circular, or bound to another observation contract.",
                ("evidence_binding",),
            )
        observer_head = lifecycle_heads.get(("OBSERVER", *key))
        if observer_head is None or observer_head.state != observer.lifecycle_state:
            return _observation_unavailable(
                case,
                "OBSERVATION_ADMISSION_UNAVAILABLE",
                "Observer admission lacks one matching current root-issued lifecycle head.",
                ("evidence_binding",),
            )
        if observer_head.state in NEGATIVE_OBSERVATION_STATES:
            return _observation_denied(
                case,
                observer_head.state,
                "Current root-issued lifecycle evidence rejects an applicable observer.",
                ("evidence_binding",),
            )
    if not observers:
        return _observation_unavailable(
            case,
            "OBSERVATION_ADMISSION_UNAVAILABLE",
            "No independently admitted observer is established.",
            ("evidence_binding",),
        )
    scope_union = {family for observer in observers.values() for family in observer.scope_families}
    if scope_union != set(OBSERVATION_SCOPE_FAMILIES):
        return _observation_unavailable(
            case,
            "OBSERVATION_SCOPE_UNAVAILABLE",
            "Admitted observers do not cover the complete immutable observation profile.",
            ("evidence_binding",),
        )

    segments: dict[str, ObservationSegment] = {}
    for segment in binding.segments:
        prior = segments.get(segment.segment_id)
        if prior is not None and prior != segment:
            return _observation_unavailable(
                case,
                "OBSERVATION_CONFLICTING",
                "One segment identity has conflicting bodies.",
                ("evidence_binding",),
            )
        segments[segment.segment_id] = segment
        observer = observers.get((segment.observer_id, segment.observer_generation))
        if (
            observer is None
            or not set(segment.scope_families).issubset(observer.scope_families)
            or segment.boundary_epoch != binding.boundary_epoch
            or segment.observation_binding_generation != binding.observation_binding_generation
        ):
            return _observation_unavailable(
                case,
                "OBSERVATION_COVERAGE_UNAVAILABLE",
                "A coverage segment is not bound to an admitted observer, scope, epoch, and observation generation.",
                ("evidence_binding",),
            )
        if (
            segment.end_event_order < segment.start_event_order
            or segment.end_sequence < segment.start_sequence
            or segment.start_event_order < binding.t1_anchor.event_order
            or segment.end_event_order > binding.t3_anchor.event_order
        ):
            return _observation_unavailable(
                case,
                "OBSERVATION_ORDERING_UNAVAILABLE",
                "A coverage segment has stale, reversed, or out-of-interval ordering.",
                ("evidence_binding",),
            )
    if not segments:
        return _observation_unavailable(
            case,
            "OBSERVATION_COVERAGE_UNAVAILABLE",
            "No ordered observation coverage segments are established.",
            ("evidence_binding",),
        )

    handoff_ids: dict[str, ObservationHandoff] = {}
    for handoff in binding.handoffs:
        prior = handoff_ids.get(handoff.handoff_id)
        if prior is not None and prior != handoff:
            return _observation_unavailable(
                case,
                "OBSERVATION_CONFLICTING",
                "One handoff identity has conflicting bodies.",
                ("evidence_binding",),
            )
        handoff_ids[handoff.handoff_id] = handoff
        before = segments.get(handoff.from_segment_id)
        after = segments.get(handoff.to_segment_id)
        if before is None or after is None or not all(
            _valid_handoff(binding, handoff, before, after, family)
            for family in handoff.scope_families
        ):
            return _observation_unavailable(
                case,
                "OBSERVER_HANDOFF_UNAVAILABLE",
                "Observer substitution is not established by one exact root-issued handoff.",
                ("evidence_binding",),
            )

    for family in OBSERVATION_SCOPE_FAMILIES:
        coverage = sorted(
            (segment for segment in segments.values() if family in segment.scope_families),
            key=lambda item: (item.start_event_order, item.end_event_order, item.segment_id),
        )
        if (
            not coverage
            or coverage[0].start_event_order != binding.t1_anchor.event_order
            or coverage[-1].end_event_order != binding.t3_anchor.event_order
        ):
            return _observation_unavailable(
                case,
                "OBSERVATION_COVERAGE_UNAVAILABLE",
                "A required observation family lacks complete T1-through-T3 coverage.",
                ("evidence_binding", family),
            )
        covered_end = coverage[0].end_event_order
        for before, after in zip(coverage, coverage[1:]):
            if after.start_event_order > covered_end + 1:
                return _observation_unavailable(
                    case,
                    "OBSERVATION_COVERAGE_UNAVAILABLE",
                    "A required observation family contains an uncovered interval.",
                    ("evidence_binding", family),
                )
            changed_stream = (
                before.observer_id,
                before.observer_generation,
                before.stream_id,
                before.stream_generation,
            ) != (
                after.observer_id,
                after.observer_generation,
                after.stream_id,
                after.stream_generation,
            )
            valid_handoff = any(
                _valid_handoff(binding, handoff, before, after, family)
                for handoff in handoff_ids.values()
            )
            if changed_stream and not valid_handoff:
                if after.start_event_order <= before.end_event_order:
                    return _observation_unavailable(
                        case,
                        "OBSERVATION_CONFLICTING",
                        "Overlapping admitted streams disagree without an authoritative handoff.",
                        ("evidence_binding", family),
                    )
                return _observation_unavailable(
                    case,
                    "OBSERVER_HANDOFF_UNAVAILABLE",
                    "Observer or stream substitution lacks a complete root-issued handoff.",
                    ("evidence_binding", family),
                )
            covered_end = max(covered_end, after.end_event_order)

    stream_segments: dict[tuple[str, int], list[ObservationSegment]] = {}
    for segment in segments.values():
        stream_segments.setdefault((segment.stream_id, segment.stream_generation), []).append(segment)
    stream_commitments: dict[tuple[str, int], str] = {}
    stream_scopes: dict[tuple[str, int], set[str]] = {}
    for stream_key, stream in stream_segments.items():
        commitments_for_stream = {segment.stream_commitment for segment in stream}
        if len(commitments_for_stream) != 1:
            return _observation_unavailable(
                case,
                "OBSERVATION_CONFLICTING",
                "One stream identity and generation has conflicting commitments.",
                ("evidence_binding",),
            )
        stream_commitments[stream_key] = next(iter(commitments_for_stream))
        stream_scopes[stream_key] = {
            family for segment in stream for family in segment.scope_families
        }
        ordered = sorted(stream, key=lambda item: (item.start_event_order, item.segment_id))
        for before, after in zip(ordered, ordered[1:]):
            if (
                after.start_event_order - before.end_event_order
                != after.start_sequence - before.end_sequence
            ):
                return _observation_unavailable(
                    case,
                    "OBSERVATION_ORDERING_UNAVAILABLE",
                    "An admitted observation stream has a gap, rollback, duplicate suppression, or reordered sequence.",
                    ("evidence_binding",),
                )

    transformation_ids: dict[str, Any] = {}
    graph: dict[tuple[str, int], tuple[str, int]] = {}
    target_sources: dict[tuple[str, int], tuple[str, int]] = {}
    for transformation in binding.transformations:
        prior = transformation_ids.get(transformation.transformation_id)
        if prior is not None and prior != transformation:
            return _observation_unavailable(
                case,
                "OBSERVATION_CONFLICTING",
                "One observation transformation identity has conflicting bodies.",
                ("evidence_binding",),
            )
        transformation_ids[transformation.transformation_id] = transformation
        if (
            transformation.source_id != root.root_id
            or transformation.authority_generation != root.authority_generation
            or transformation.boundary != root.boundary
            or transformation.boundary_epoch != root.boundary_epoch
            or transformation.lineage != root.lineage
        ):
            return _observation_unavailable(
                case,
                "OBSERVATION_TRANSFORMATION_UNAVAILABLE",
                "An observation transformation is not admitted by the exact current root.",
                ("evidence_binding",),
            )
        if transformation.lifecycle_state in NEGATIVE_OBSERVATION_STATES:
            return _observation_denied(
                case,
                transformation.lifecycle_state,
                "Current root-issued lifecycle evidence rejects an observation transformation.",
                ("evidence_binding",),
            )
        source_key = (
            transformation.source_stream_id,
            transformation.source_stream_generation,
        )
        if stream_commitments.get(source_key) != transformation.source_commitment:
            return _observation_unavailable(
                case,
                "OBSERVATION_TRANSFORMATION_UNAVAILABLE",
                "A transformed stream lacks exact source commitment continuity.",
                ("evidence_binding",),
            )
        target_key = (
            transformation.target_stream_id,
            transformation.target_stream_generation,
        )
        if source_key in graph and (
            graph[source_key] != target_key
            or stream_commitments.get(target_key) != transformation.target_commitment
        ):
            return _observation_unavailable(
                case,
                "OBSERVATION_TRANSFORMATION_UNAVAILABLE",
                "Fan-out transformation cannot preserve observation authority in v1.",
                ("evidence_binding",),
            )
        prior_source = target_sources.get(target_key)
        if prior_source is not None and prior_source != source_key:
            return _observation_unavailable(
                case,
                "OBSERVATION_TRANSFORMATION_UNAVAILABLE",
                "Fan-in transformation cannot preserve observation authority in v1.",
                ("evidence_binding",),
            )
        if target_key in stream_commitments and (
            target_key not in target_sources
            or stream_commitments[target_key] != transformation.target_commitment
        ):
            return _observation_unavailable(
                case,
                "OBSERVATION_TRANSFORMATION_UNAVAILABLE",
                "A transformation conflicts with an existing stream identity or commitment.",
                ("evidence_binding",),
            )
        graph[source_key] = target_key
        target_sources[target_key] = source_key
        source_scopes = stream_scopes.get(source_key)
        if source_scopes is None or set(transformation.scope_families) != source_scopes:
            return _observation_unavailable(
                case,
                "OBSERVATION_TRANSFORMATION_UNAVAILABLE",
                "A transformation drops or widens an authority-relevant observation scope.",
                ("evidence_binding",),
            )
        stream_commitments[target_key] = transformation.target_commitment
        stream_scopes[target_key] = set(transformation.scope_families)
    for start in graph:
        seen: set[tuple[str, int]] = set()
        node = start
        while node in graph:
            if node in seen:
                return _observation_unavailable(
                    case,
                    "OBSERVATION_TRANSFORMATION_UNAVAILABLE",
                    "Observation transformation lineage is cyclic.",
                    ("evidence_binding",),
                )
            seen.add(node)
            node = graph[node]

    if (
        freshness.observation_binding_id != binding.observation_binding_id
        or freshness.observation_binding_generation != binding.observation_binding_generation
        or freshness.profile_id != binding.profile_id
        or freshness.profile_version != binding.profile_version
        or freshness.boundary != binding.boundary
        or freshness.boundary_epoch != binding.boundary_epoch
        or freshness.lineage != binding.lineage
        or freshness.source_id != root.root_id
        or freshness.authority_generation != root.authority_generation
        or freshness.ordering_source_id != root.ordering_source_id
        or freshness.head_anchor_id != binding.t3_anchor.anchor_id
        or freshness.head_event_order != binding.t3_anchor.event_order
    ):
        return _observation_unavailable(
            case,
            "OBSERVATION_FRESHNESS_UNAVAILABLE",
            "Observation evidence is stale or does not terminate at the exact current T3 anchor.",
            ("freshness", "evidence_binding"),
        )

    commitment_result = _evaluate_commitment_envelope(case, binding, root, segments)
    if commitment_result.outcome is not AuthorityOutcome.AUTHORIZED:
        return commitment_result

    return OracleResult(
        AuthorityOutcome.AUTHORIZED,
        (
            Reason(
                "OBSERVATION_COVERAGE_ESTABLISHED",
                "Root-issued observation admission establishes complete current ordered coverage.",
                ("evidence_binding", "freshness"),
            ),
        ),
        _engaged(case),
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
        if "commit_state" in mutation_chain_mismatches:
            return _unavailable(
                case,
                "TERMINAL_EVENT_ORDERING_UNAVAILABLE",
                "Terminal lifecycle events are duplicated, reordered, or do not resolve to the exact observed T3 state.",
                ("commit_state",),
            )
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

    continuity_path = analyze_continuity_path(case)
    if "boundary_epoch" in continuity_path.aba_targets:
        return _unavailable(
            case,
            "BOUNDARY_EPOCH_REUSE_UNAVAILABLE",
            "A returned boundary label does not restore the predecessor boundary lineage.",
            ("boundary_epoch",),
        )
    if continuity_path.grant_nonportable and active_state.grant_id == t1_state.grant_id:
        return _unavailable(
            case,
            "PREDECESSOR_GRANT_NONPORTABLE",
            "A predecessor grant cannot cross an identity, lineage, terminal, or grant/use discontinuity.",
            ("grant_id", "consumption_binding"),
        )
    if continuity_path.successor_break and not _fresh_successor_chain_established(
        case, active_state
    ):
        return _unavailable(
            case,
            "SUCCESSOR_AUTHORITY_UNAVAILABLE",
            "The path contains an execution-identity, lineage, or terminal break without an independently current successor authority chain.",
            tuple(
                dict.fromkeys(
                    (
                        *continuity_path.aba_targets,
                        "identity_basis",
                        "execution_context",
                        "boundary_epoch",
                        "grant_id",
                    )
                )
            ),
        )

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

    observation_result = _evaluate_observation(case)
    if observation_result.outcome is not AuthorityOutcome.AUTHORIZED:
        return observation_result

    return OracleResult(
        AuthorityOutcome.AUTHORIZED,
        (
            Reason(
                "CURRENT_AUTHORITY_ESTABLISHED",
                "All required current facts, observation coverage, and relationships are established and no applicable prohibition applies.",
            ),
        ),
        _engaged(case),
    )
