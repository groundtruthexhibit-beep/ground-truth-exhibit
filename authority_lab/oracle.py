"""Deterministic oracle over public Authority Lab fixture state."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from .commitment import (
    anchor_digest,
    anchor_key_digest,
    commitment_digest,
    recovery_receipt_digest,
    state_key_digest,
    verifier_state_digest,
)

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
    RESERVED_HUMAN_APPROVAL_FACTS,
    RESERVED_TOOL_CONNECTOR_FACTS,
    RESERVED_T3_EXECUTION_FACTS,
    Reason,
    exact_value_equal,
)


from .phi_disclosure import evaluate_phi_disclosure


def _canonical_digest(domain: str, value: Mapping[str, Any]) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(f"{domain}\0{payload}".encode("utf-8")).hexdigest()


def human_approval_effect_digest(binding: Mapping[str, Any]) -> str:
    """Canonical exact effect identity; display text and approval claims are excluded."""
    fields = (
        "artifact", "effect", "subject_id", "subject_identity_basis", "executor_id",
        "delegation_chain_id", "tool_backend_id", "credential_generation",
        "execution_context", "boundary", "boundary_epoch", "objective_id",
        "objective_generation", "decision_contract_id", "decision_contract_version",
        "grant_id", "session_id", "session_generation", "transformation_id",
    )
    return _canonical_digest(
        "authority-lab-v1/human-approval-effect",
        {field: binding[field] for field in fields},
    )


def human_approval_request_digest(binding: Mapping[str, Any]) -> str:
    return _canonical_digest(
        "authority-lab-v1/human-approval-request",
        {
            "request_id": binding["request_id"],
            "request_generation": binding["request_generation"],
            "effect_digest": human_approval_effect_digest(binding),
            "display_digest": binding["display_digest"],
        },
    )


def human_approval_envelope_digest(envelope: Mapping[str, Any]) -> str:
    """Digest every signed approval-envelope member except the digest itself."""
    return _canonical_digest(
        "authority-lab-v1/human-approval-envelope",
        {
            field: value
            for field, value in envelope.items()
            if field != "canonical_payload_digest"
        },
    )


def tool_connector_context_digest(context: Mapping[str, Any]) -> str:
    """Canonical identity of every authority-relevant execution-target field."""
    return _canonical_digest(
        "authority-lab-v1/tool-connector-context",
        {
            field: value
            for field, value in context.items()
            if field != "context_digest"
        },
    )


def t3_execution_event_digest(event: Mapping[str, Any]) -> str:
    """Canonical identity of the protected terminal authority-consumption event."""
    return _canonical_digest(
        "authority-lab-v1/t3-execution-event",
        {field: value for field, value in event.items() if field != "execution_event_digest"},
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
        anchor_result = _evaluate_verifier_state_anchor(
            case, binding, root, envelope, checkpoint, expected_key
        )
        if anchor_result is not None:
            return anchor_result

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


def _evaluate_verifier_state_anchor(
    case: OracleInput,
    binding: ObservationBinding,
    root: Any,
    envelope: Mapping[str, Any],
    checkpoint: Mapping[str, Any],
    expected_state_key: str,
) -> OracleResult | None:
    """Join candidate evidence to one independently current monotonic anchor."""
    sources = [item.values for item in binding.anchor_source_admissions]
    anchors = [item.values for item in binding.verifier_state_anchors]
    if not sources or not anchors or not case.trusted_anchor_context:
        return _observation_unavailable(
            case, "VERIFIER_STATE_ANCHOR_UNAVAILABLE",
            "An independently retained verifier-state anchor is unavailable.",
            ("evidence_binding", "freshness"),
        )
    matching = [
        item for item in anchors
        if item["stream_id"] == envelope["stream_id"]
        and item["stream_generation"] == envelope["stream_generation"]
        and item["head_commitment_digest"] == envelope["commitment_digest"]
        and item["checkpoint_id"] == checkpoint["checkpoint_id"]
    ]
    if len(matching) != 1:
        return _observation_unavailable(
            case, "VERIFIER_STATE_ANCHOR_CONFLICTING",
            "No unique candidate anchor selects the exact commitment checkpoint.",
            ("evidence_binding",),
        )
    anchor = matching[0]
    source_matches = [
        item for item in sources
        if item["relationship"] == "VERIFIER_STATE_ANCHOR_SOURCE_ADMISSION"
        and item["scope"] == "VERIFIER_STATE_CURRENTNESS"
        and item["anchor_source_id"] == anchor["anchor_source_id"]
        and item["anchor_source_generation"] == anchor["anchor_source_generation"]
        and item["anchor_source_identity_basis"] == anchor["anchor_source_identity_basis"]
        and item["anchor_key_id"] == anchor["anchor_key_id"]
        and item["anchor_key_generation"] == anchor["anchor_key_generation"]
        and item["verifier_id"] == anchor["verifier_id"]
        and item["durable_state_id"] == anchor["durable_state_id"]
        and item["stream_id"] == anchor["stream_id"]
        and item["stream_generation"] == anchor["stream_generation"]
        and item["source_id"] == root.root_id
        and item["authority_generation"] == root.authority_generation
        and item["boundary"] == root.boundary
        and item["boundary_epoch"] == root.boundary_epoch
        and item["lineage"] == root.lineage
        and item["ordering_source_id"] == root.ordering_source_id
        and item["lifecycle_state"] == "ACTIVE"
    ]
    forbidden_sources = {
        case.authority_tuple.subject,
        envelope["observer_id"],
        anchor["verifier_id"],
    }
    negative_states = {"REVOKED", "REJECTED", "INVALID", "PROHIBITED"}
    if any(
        item["anchor_source_id"] == anchor["anchor_source_id"]
        and item["anchor_source_generation"] == anchor["anchor_source_generation"]
        and item["source_id"] == root.root_id
        and item["lifecycle_state"] in negative_states
        for item in sources
    ) or anchor["lifecycle_state"] in negative_states:
        return OracleResult(
            AuthorityOutcome.DENIED,
            (Reason("VERIFIER_STATE_ANCHOR_PROHIBITED", "Current authoritative lifecycle evidence rejects the verifier-state anchor lineage.", ("evidence_binding",)),),
            _engaged(case),
        )
    if len(source_matches) != 1 or anchor["anchor_source_id"] in forbidden_sources:
        return _observation_unavailable(
            case, "VERIFIER_STATE_ANCHOR_SOURCE_UNAVAILABLE",
            "The anchor lacks one exact independent root-issued source admission.",
            ("evidence_binding", "binding_source_authority"),
        )
    if (
        anchor["relationship"] != "VERIFIER_STATE_ANCHOR"
        or anchor["exact_state_key_digest"] != expected_state_key
        or anchor["head_logical_position"] != checkpoint["head_logical_position"]
        or anchor["head_commitment_id"] != checkpoint["head_commitment_id"]
        or anchor["verifier_state_digest"] != checkpoint["current_verifier_state_digest"]
        or anchor["checkpoint_generation"] != checkpoint["checkpoint_generation"]
        or anchor["freshness_challenge_id"] != checkpoint["freshness_challenge_id"]
        or anchor["source_id"] != root.root_id
        or anchor["authority_generation"] != root.authority_generation
        or anchor["boundary"] != root.boundary
        or anchor["boundary_epoch"] != root.boundary_epoch
        or anchor["lineage"] != root.lineage
        or anchor["ordering_source_id"] != root.ordering_source_id
        or anchor["lifecycle_state"] != "ACTIVE"
        or anchor["anchor_event_order"] > binding.t3_anchor.event_order
        or anchor["recovery_eligibility"] not in {"NORMAL", "RECOVERY_CHECKPOINT", "NOT_RECOVERABLE"}
        or anchor_digest(anchor) != anchor["anchor_digest"]
        or anchor["canonical_payload_digest"] != anchor["anchor_digest"]
    ):
        return _observation_unavailable(
            case, "VERIFIER_STATE_ANCHOR_CONFLICTING",
            "The candidate anchor is not exact for the selected verifier state.",
            ("evidence_binding", "freshness"),
        )
    if anchor["anchor_position"] == 0:
        if (
            anchor["predecessor_anchor_id"] != "GENESIS"
            or anchor["predecessor_anchor_generation"] != 0
            or anchor["predecessor_anchor_position"] != 0
            or anchor["predecessor_anchor_digest"] != "GENESIS-ANCHOR"
        ):
            return _observation_unavailable(case, "VERIFIER_STATE_ANCHOR_CONTINUITY_UNAVAILABLE", "Anchor genesis is not exact.", ("evidence_binding",))
    elif anchor["predecessor_anchor_position"] != anchor["anchor_position"] - 1:
        return _observation_unavailable(case, "VERIFIER_STATE_ANCHOR_CONTINUITY_UNAVAILABLE", "Anchor predecessor ordering is incomplete.", ("evidence_binding", "binding_ordering"))

    matching_contexts = [
        item for item in case.trusted_anchor_context
        if item.get("exact_anchor_key_digest") == anchor_key_digest(anchor)
    ]
    if not matching_contexts:
        return _observation_unavailable(case, "VERIFIER_STATE_ANCHOR_UNAVAILABLE", "No unique independently current anchor context exists.", ("evidence_binding", "freshness"))
    policy_ids = {
        item["required_domain_policy"]["policy_id"] for item in matching_contexts
    }
    if len(policy_ids) != 1:
        return _observation_unavailable(case, "REQUIRED_SOURCE_DOMAIN_CONFLICTING", "The candidate anchor maps to ambiguous protected domain policy.", ("evidence_binding",))
    policy_id = next(iter(policy_ids))
    required_domain_count = len(
        matching_contexts[0]["required_domain_policy"]["required_domains"]
    )
    contexts = list(matching_contexts)
    if required_domain_count > 1:
        contexts.extend(
            item for item in case.trusted_anchor_context
            if item not in matching_contexts
            and item["required_domain_policy"]["policy_id"] == policy_id
        )
    protected_result = _evaluate_protected_anchor_domains(
        case, binding, root, anchor, checkpoint, contexts
    )
    if protected_result is not None:
        return protected_result
    control_plane_result = _evaluate_control_plane_independence(
        case, binding, root, anchor, contexts
    )
    if control_plane_result is not None:
        return control_plane_result
    trusted = contexts[0]
    conflict = trusted.get("conflicting_anchor_digests", [])
    if conflict:
        return _observation_unavailable(case, "VERIFIER_STATE_REPLICA_CONFLICTING", "The independently admitted anchor context reports divergent heads.", ("evidence_binding",))
    trusted_position = trusted.get("anchor_position", -1)
    if trusted_position > anchor["anchor_position"]:
        return _observation_unavailable(case, "VERIFIER_STATE_ANCHOR_REPLAY", "The candidate replays a state older than the independently retained anchor.", ("evidence_binding", "freshness"))
    if trusted_position == anchor["anchor_position"] and trusted.get("anchor_digest") != anchor["anchor_digest"]:
        return _observation_unavailable(case, "VERIFIER_STATE_REPLICA_CONFLICTING", "The same anchor position selects an incompatible head.", ("evidence_binding",))
    exact = {
        "anchor_id": anchor["anchor_id"],
        "anchor_generation": anchor["anchor_generation"],
        "anchor_position": anchor["anchor_position"],
        "anchor_digest": anchor["anchor_digest"],
        "exact_state_key_digest": anchor["exact_state_key_digest"],
        "stream_id": anchor["stream_id"],
        "stream_generation": anchor["stream_generation"],
        "head_logical_position": anchor["head_logical_position"],
        "head_commitment_digest": anchor["head_commitment_digest"],
        "verifier_id": anchor["verifier_id"],
        "verifier_generation": anchor["verifier_generation"],
        "verifier_state_digest": anchor["verifier_state_digest"],
        "durable_state_id": anchor["durable_state_id"],
        "durable_state_generation": anchor["durable_state_generation"],
        "freshness_challenge_id": anchor["freshness_challenge_id"],
    }
    if any(trusted.get(name) != value for name, value in exact.items()):
        return _observation_unavailable(case, "VERIFIER_STATE_ANCHOR_ROLLBACK", "Verifier state and independently current anchor context do not exactly join.", ("evidence_binding", "freshness"))

    recovery_result = _evaluate_recovery_and_rotation(case, binding, root, anchor, trusted)
    if recovery_result is not None:
        return recovery_result
    return None


def _evaluate_protected_anchor_domains(
    case: OracleInput,
    binding: ObservationBinding,
    root: Any,
    anchor: Mapping[str, Any],
    checkpoint: Mapping[str, Any],
    contexts: list[Mapping[str, Any]],
) -> OracleResult | None:
    """Require protected adapter currentness and root-selected source domains."""
    policies = [item["required_domain_policy"] for item in contexts]
    first_policy = policies[0]
    negative_states = {"REVOKED", "REJECTED", "INVALID", "PROHIBITED"}
    if any(item["lifecycle_state"] in negative_states for item in policies):
        return OracleResult(
            AuthorityOutcome.DENIED,
            (Reason("SOURCE_DOMAIN_POLICY_PROHIBITED", "Current authoritative lifecycle evidence prohibits the required-domain policy.", ("evidence_binding",)),),
            _engaged(case),
        )
    policy_key = (
        first_policy["policy_id"], first_policy["policy_generation"],
        first_policy["membership_epoch"], tuple(first_policy["required_domains"]),
        tuple(first_policy["optional_domains"]), first_policy["selection_rule"],
        first_policy["boundary"], first_policy["boundary_epoch"],
        first_policy["source_id"], first_policy["authority_generation"],
        first_policy["ordering_source_id"], first_policy["freshness_challenge_id"],
        first_policy["lifecycle_state"],
    )
    if any((
        item["policy_id"], item["policy_generation"], item["membership_epoch"],
        tuple(item["required_domains"]), tuple(item["optional_domains"]),
        item["selection_rule"], item["boundary"], item["boundary_epoch"],
        item["source_id"], item["authority_generation"],
        item["ordering_source_id"], item["freshness_challenge_id"],
        item["lifecycle_state"],
    ) != policy_key for item in policies):
        return _observation_unavailable(case, "REQUIRED_SOURCE_DOMAIN_CONFLICTING", "Protected required-domain policies conflict.", ("evidence_binding",))
    if (
        first_policy["relationship"] != "REQUIRED_SOURCE_DOMAIN_POLICY"
        or first_policy["selection_rule"] != "ALL_LISTED"
        or not first_policy["required_domains"]
        or len(first_policy["required_domains"]) != len(set(first_policy["required_domains"]))
        or first_policy["source_id"] != root.root_id
        or first_policy["authority_generation"] != root.authority_generation
        or first_policy["ordering_source_id"] != root.ordering_source_id
        or first_policy["boundary"] != root.boundary
        or first_policy["boundary_epoch"] != root.boundary_epoch
        or first_policy["freshness_challenge_id"] != anchor["freshness_challenge_id"]
        or first_policy["lifecycle_state"] != "ACTIVE"
    ):
        return _observation_unavailable(case, "REQUIRED_SOURCE_DOMAIN_UNAVAILABLE", "No exact current root-selected source-domain policy exists.", ("evidence_binding", "freshness"))

    required = set(first_policy["required_domains"])
    views = [item["domain_view"] for item in contexts]
    view_domains = [item["domain_id"] for item in views]
    if set(view_domains) != required or len(view_domains) != len(set(view_domains)):
        return _observation_unavailable(case, "REQUIRED_SOURCE_DOMAIN_UNAVAILABLE", "A required protected source domain is missing, duplicated, or candidate-selected.", ("evidence_binding",))

    forbidden = {case.authority_tuple.subject, anchor["verifier_id"], anchor["anchor_source_id"]}
    domain_sources: list[tuple[str, str, str, str]] = []
    for context, view in zip(contexts, views):
        adapter = context["adapter_admission"]
        if adapter["lifecycle_state"] in negative_states:
            return OracleResult(
                AuthorityOutcome.DENIED,
                (Reason("ANCHOR_ADAPTER_PROHIBITED", "Current authoritative lifecycle evidence prohibits the anchor adapter.", ("evidence_binding",)),),
                _engaged(case),
            )
        if (
            adapter["relationship"] != "ANCHOR_ADAPTER_ADMISSION"
            or adapter["adapter_id"] in forbidden
            or adapter["anchor_source_id"] != anchor["anchor_source_id"]
            or adapter["anchor_source_generation"] != anchor["anchor_source_generation"]
            or adapter["stream_id"] != anchor["stream_id"]
            or adapter["stream_generation"] != anchor["stream_generation"]
            or adapter["boundary"] != root.boundary
            or adapter["boundary_epoch"] != root.boundary_epoch
            or adapter["source_id"] != root.root_id
            or adapter["authority_generation"] != root.authority_generation
            or adapter["ordering_source_id"] != root.ordering_source_id
            or adapter["freshness_challenge_id"] != anchor["freshness_challenge_id"]
            or adapter["lifecycle_state"] != "ACTIVE"
            or "VERIFIER_STATE_CURRENTNESS" not in adapter["covered_scope_families"]
            or adapter["start_event_order"] > binding.t1_anchor.event_order
            or adapter["end_event_order"] < binding.t3_anchor.event_order
            or context.get("adapter_source_id") != adapter["anchor_source_id"]
            or context.get("adapter_source_generation") != adapter["anchor_source_generation"]
            or context.get("adapter_observation_id") != adapter["adapter_observation_id"]
            or context.get("adapter_observation_generation") != adapter["adapter_observation_generation"]
            or context.get("adapter_event_order") != adapter["end_event_order"]
            or view["relationship"] != "DOMAIN_CHECKPOINT_VIEW"
            or view["domain_id"] != adapter["independence_domain"]
            or view["adapter_id"] != adapter["adapter_id"]
            or view["stream_id"] != anchor["stream_id"]
            or view["stream_generation"] != anchor["stream_generation"]
            or view["boundary"] != root.boundary
            or view["boundary_epoch"] != root.boundary_epoch
            or view["freshness_challenge_id"] != anchor["freshness_challenge_id"]
            or view["lifecycle_state"] != "ACTIVE"
        ):
            return _observation_unavailable(case, "ANCHOR_ADAPTER_CURRENTNESS_UNAVAILABLE", "The protected adapter admission/currentness join is missing, stale, or ambiguous.", ("evidence_binding", "freshness"))
        memberships = [
            item for item in context["source_domain_memberships"]
            if item["member_kind"] == "ADAPTER" and item["member_id"] == adapter["adapter_id"]
        ]
        if len(memberships) != 1:
            return _observation_unavailable(case, "SOURCE_DOMAIN_MEMBERSHIP_UNAVAILABLE", "Adapter source-domain membership is not uniquely established.", ("evidence_binding",))
        member = memberships[0]
        if member["lifecycle_state"] in negative_states:
            return OracleResult(
                AuthorityOutcome.DENIED,
                (Reason("SOURCE_DOMAIN_MEMBERSHIP_PROHIBITED", "Current authoritative lifecycle evidence prohibits the source-domain membership.", ("evidence_binding",)),),
                _engaged(case),
            )
        if (
            member["member_generation"] != adapter["adapter_generation"]
            or member["identity_basis"] != adapter["adapter_identity_basis"]
            or member["source_lineage"] != adapter["source_lineage"]
            or member["control_domain"] != adapter["control_domain"]
            or member["independence_domain"] != adapter["independence_domain"]
            or member["rollback_domain"] != adapter["rollback_domain"]
            or member["membership_epoch"] != first_policy["membership_epoch"]
            or member["source_id"] != root.root_id
            or member["authority_generation"] != root.authority_generation
            or member["ordering_source_id"] != root.ordering_source_id
            or member["boundary"] != root.boundary
            or member["boundary_epoch"] != root.boundary_epoch
            or member["freshness_challenge_id"] != anchor["freshness_challenge_id"]
            or member["lifecycle_state"] != "ACTIVE"
        ):
            return _observation_unavailable(case, "SOURCE_DOMAIN_MEMBERSHIP_UNAVAILABLE", "Adapter independence is not authoritatively appraised.", ("evidence_binding", "binding_source_authority"))
        domain_sources.append((
            member["source_lineage"], member["control_domain"],
            member["upstream_dependency"], member["rollback_domain"],
        ))
        if adapter["adapter_generation"] > 1:
            rotation = context.get("adapter_rotation")
            if (
                rotation is None
                or rotation["relationship"] != "ANCHOR_ADAPTER_ROTATION"
                or rotation["new_adapter_id"] != adapter["adapter_id"]
                or rotation["new_adapter_generation"] != adapter["adapter_generation"]
                or rotation["rotation_id"] != adapter["rotation_id"]
                or rotation["source_lineage"] != adapter["source_lineage"]
                or rotation["source_id"] != root.root_id
                or rotation["authority_generation"] != root.authority_generation
                or rotation["ordering_source_id"] != root.ordering_source_id
                or rotation["freshness_challenge_id"] != anchor["freshness_challenge_id"]
                or rotation["lifecycle_state"] != "ACTIVE"
            ):
                return _observation_unavailable(case, "ANCHOR_ADAPTER_ROTATION_UNAVAILABLE", "Adapter replacement lacks exact authorized continuity.", ("evidence_binding",))

    if len(domain_sources) != len(set(domain_sources)):
        return _observation_unavailable(case, "SOURCE_DOMAIN_INDEPENDENCE_UNAVAILABLE", "Multiple required domains share one authoritative source/control/rollback lineage.", ("evidence_binding", "binding_source_authority"))

    selected = {(item["anchor_position"], item["anchor_digest"], item["head_commitment_digest"]) for item in views}
    reconciliation = contexts[0].get("cross_domain_reconciliation")
    if len(selected) != 1:
        if reconciliation is None:
            return _observation_unavailable(case, "CROSS_DOMAIN_CHECKPOINT_CONFLICTING", "Required source domains report unresolved checkpoint disagreement.", ("evidence_binding",))
        if reconciliation["lifecycle_state"] in negative_states:
            return OracleResult(
                AuthorityOutcome.DENIED,
                (Reason("CROSS_DOMAIN_RECONCILIATION_PROHIBITED", "Current authoritative lifecycle evidence prohibits the reconciliation.", ("evidence_binding",)),),
                _engaged(case),
            )
        competing_domains = sorted(view["domain_id"] for view in views)
        competing_digests = sorted({view["anchor_digest"] for view in views})
        if (
            reconciliation["relationship"] != "CROSS_DOMAIN_CHECKPOINT_RECONCILIATION"
            or reconciliation["policy_id"] != first_policy["policy_id"]
            or reconciliation["membership_epoch"] != first_policy["membership_epoch"]
            or sorted(reconciliation["competing_domain_ids"]) != competing_domains
            or sorted(reconciliation["competing_anchor_digests"]) != competing_digests
            or reconciliation["selected_anchor_digest"] != anchor["anchor_digest"]
            or reconciliation["selected_head_commitment_digest"] != anchor["head_commitment_digest"]
            or reconciliation["source_id"] != root.root_id
            or reconciliation["authority_generation"] != root.authority_generation
            or reconciliation["ordering_source_id"] != root.ordering_source_id
            or reconciliation["freshness_challenge_id"] != anchor["freshness_challenge_id"]
            or reconciliation["lifecycle_state"] != "ACTIVE"
        ):
            return _observation_unavailable(case, "CROSS_DOMAIN_RECONCILIATION_UNAVAILABLE", "Checkpoint reconciliation is incomplete or unauthorized.", ("evidence_binding", "binding_ordering"))
    elif reconciliation is not None:
        return _observation_unavailable(case, "CROSS_DOMAIN_RECONCILIATION_UNAVAILABLE", "Unselected reconciliation data cannot manufacture authority.", ("evidence_binding",))

    witnesses = [item.values for item in binding.witness_source_admissions]
    protected_witnesses = contexts[0]["witness_source_memberships"]
    if witnesses or protected_witnesses:
        if len(witnesses) != len(protected_witnesses):
            return _observation_unavailable(case, "WITNESS_SOURCE_CONTINUITY_UNAVAILABLE", "Candidate witness selection differs from protected membership.", ("evidence_binding",))
        effective_domains: set[str] = set()
        used_memberships: set[tuple[str, int]] = set()
        for witness in witnesses:
            matches = [item for item in protected_witnesses if item["member_id"] == witness["witness_id"] and item["member_generation"] == witness["witness_generation"]]
            if len(matches) != 1:
                return _observation_unavailable(case, "WITNESS_SOURCE_CONTINUITY_UNAVAILABLE", "Witness identity lacks protected source membership.", ("evidence_binding",))
            member = matches[0]
            if member["lifecycle_state"] in negative_states:
                return OracleResult(
                    AuthorityOutcome.DENIED,
                    (Reason("WITNESS_SOURCE_PROHIBITED", "Current authoritative lifecycle evidence prohibits the witness source.", ("evidence_binding",)),),
                    _engaged(case),
                )
            key = (member["member_id"], member["member_generation"])
            if key in used_memberships:
                return _observation_unavailable(case, "WITNESS_SOURCE_CONTINUITY_UNAVAILABLE", "Duplicate witness identity cannot establish independence.", ("evidence_binding",))
            used_memberships.add(key)
            if (
                member["member_kind"] != "WITNESS_SOURCE"
                or member["identity_basis"] != witness["witness_identity_basis"]
                or member["source_lineage"] != witness["source_lineage"]
                or member["control_domain"] != witness["control_domain"]
                or member["source_id"] != root.root_id
                or member["authority_generation"] != root.authority_generation
                or member["ordering_source_id"] != root.ordering_source_id
                or member["boundary"] != root.boundary
                or member["boundary_epoch"] != root.boundary_epoch
                or member["freshness_challenge_id"] != anchor["freshness_challenge_id"]
                or member["lifecycle_state"] != "ACTIVE"
                or witness["witness_source_id"] != member["upstream_dependency"]
                or witness["anchor_digest"] != anchor["anchor_digest"]
                or witness["head_commitment_digest"] != anchor["head_commitment_digest"]
                or witness["source_id"] != root.root_id
                or witness["authority_generation"] != root.authority_generation
                or witness["boundary"] != root.boundary
                or witness["boundary_epoch"] != root.boundary_epoch
                or witness["ordering_source_id"] != root.ordering_source_id
                or witness["lifecycle_state"] != "ACTIVE"
                or "VERIFIER_STATE_CURRENTNESS" not in witness["covered_scope_families"]
                or witness["start_event_order"] > binding.t1_anchor.event_order
                or witness["end_event_order"] < binding.t3_anchor.event_order
            ):
                return _observation_unavailable(case, "WITNESS_COVERAGE_UNAVAILABLE", "Witness identity, source, scope, interval, freshness, or boundary is not exact.", ("evidence_binding", "freshness"))
            if member["member_generation"] > 1:
                transitions = [
                    item for item in contexts[0]["source_domain_transitions"]
                    if item["member_kind"] == "WITNESS_SOURCE"
                    and item["new_member_id"] == member["member_id"]
                    and item["new_member_generation"] == member["member_generation"]
                ]
                if len(transitions) != 1:
                    return _observation_unavailable(case, "WITNESS_HANDOFF_UNAVAILABLE", "Witness replacement lacks one exact authoritative predecessor transition.", ("evidence_binding",))
                transition = transitions[0]
                if (
                    transition["relationship"] != "SOURCE_DOMAIN_MEMBERSHIP_TRANSITION"
                    or transition["old_member_generation"] != member["member_generation"] - 1
                    or transition["new_source_lineage"] != member["source_lineage"]
                    or transition["independence_domain"] != member["independence_domain"]
                    or transition["boundary"] != root.boundary
                    or transition["boundary_epoch"] != root.boundary_epoch
                    or transition["source_id"] != root.root_id
                    or transition["authority_generation"] != root.authority_generation
                    or transition["ordering_source_id"] != root.ordering_source_id
                    or transition["freshness_challenge_id"] != anchor["freshness_challenge_id"]
                    or transition["lifecycle_state"] != "ACTIVE"
                ):
                    return _observation_unavailable(case, "WITNESS_HANDOFF_UNAVAILABLE", "Witness source-lineage transition is stale, ambiguous, or unauthorized.", ("evidence_binding", "binding_ordering"))
            effective_domains.add(member["independence_domain"])
        if len(effective_domains) < contexts[0].get("required_witness_domains", 0):
            return _observation_unavailable(case, "WITNESS_SOURCE_CONTINUITY_UNAVAILABLE", "Witness multiplicity does not establish protected independent domains.", ("evidence_binding",))
    return None


CONTROL_PLANE_ROLES = frozenset({
    "POLICY_ROOT", "ORDERER", "OBSERVER", "COMMITMENT_PRODUCER",
    "COMMITMENT_VERIFIER", "ANCHOR_SOURCE", "ANCHOR_ADAPTER",
    "WITNESS_SOURCE", "RECONCILIATION_AUTHORITY", "RECOVERY_AUTHORITY",
})


def _effective_domain(item: Mapping[str, Any]) -> tuple[str, str, str, str]:
    return (
        item["source_lineage"], item["control_domain"],
        item.get("upstream_dependency", item.get("appraisal_root_id", "")),
        item["rollback_domain"],
    )


def _applicable_control_plane_roles(
    binding: ObservationBinding,
    root: Any,
    anchor: Mapping[str, Any],
    contexts: list[Mapping[str, Any]],
) -> set[tuple[str, str, int]]:
    roles: set[tuple[str, str, int]] = {
        ("POLICY_ROOT", root.root_id, root.authority_generation),
        ("ORDERER", root.ordering_source_id, root.authority_generation),
        ("COMMITMENT_VERIFIER", anchor["verifier_id"], anchor["verifier_generation"]),
        ("ANCHOR_SOURCE", anchor["anchor_source_id"], anchor["anchor_source_generation"]),
    }
    roles.update(
        ("OBSERVER", item.observer_id, item.observer_generation)
        for item in binding.observers
    )
    roles.update(
        ("COMMITMENT_PRODUCER", item.values["observer_id"], item.values["observer_generation"])
        for item in binding.commitment_envelopes
    )
    roles.update(
        ("COMMITMENT_VERIFIER", item.values["verifier_id"], item.values["verifier_generation"])
        for item in binding.commitment_verifiers
    )
    roles.update(
        ("ANCHOR_SOURCE", item.values["anchor_source_id"], item.values["anchor_source_generation"])
        for item in binding.anchor_source_admissions
    )
    roles.update(
        ("ANCHOR_ADAPTER", item["adapter_admission"]["adapter_id"], item["adapter_admission"]["adapter_generation"])
        for item in contexts
    )
    roles.update(
        ("WITNESS_SOURCE", item.values["witness_id"], item.values["witness_generation"])
        for item in binding.witness_source_admissions
    )
    reconciliation = contexts[0].get("cross_domain_reconciliation")
    if reconciliation is not None:
        roles.add((
            "RECONCILIATION_AUTHORITY", reconciliation["source_id"],
            reconciliation["authority_generation"],
        ))
    roles.update(
        (
            "RECOVERY_AUTHORITY", item.values["recovery_authority_id"],
            item.values["recovery_authority_generation"],
        )
        for item in binding.recovery_installations
    )
    return roles


def _control_plane_identity_expectations(
    binding: ObservationBinding,
    root: Any,
    anchor: Mapping[str, Any],
    contexts: list[Mapping[str, Any]],
) -> dict[tuple[str, str, int], tuple[str, str | None, int | None]] | None:
    """Return exact identity/key expectations, or None on conflicting records."""
    result: dict[tuple[str, str, int], tuple[str, str | None, int | None]] = {}

    def add(role: str, member_id: str, generation: int, identity: str,
            key_id: str | None = None, key_generation: int | None = None) -> bool:
        item = (identity, key_id, key_generation)
        index = (role, member_id, generation)
        if index in result and result[index] != item:
            return False
        result[index] = item
        return True

    if not add("POLICY_ROOT", root.root_id, root.authority_generation, root.lineage):
        return None
    if not add("ORDERER", root.ordering_source_id, root.authority_generation, root.ordering_source_id):
        return None
    for item in binding.observers:
        if not add("OBSERVER", item.observer_id, item.observer_generation, item.observer_identity_basis):
            return None
    for record in binding.commitment_envelopes:
        item = record.values
        if not add("COMMITMENT_PRODUCER", item["observer_id"], item["observer_generation"], item["observer_identity_basis"], item["issuer_key_id"], item["issuer_key_generation"]):
            return None
    for record in binding.commitment_verifiers:
        item = record.values
        if not add("COMMITMENT_VERIFIER", item["verifier_id"], item["verifier_generation"], item["verifier_identity_basis"]):
            return None
    if not add("COMMITMENT_VERIFIER", anchor["verifier_id"], anchor["verifier_generation"], anchor["verifier_identity_basis"]):
        return None
    for record in binding.anchor_source_admissions:
        item = record.values
        if not add("ANCHOR_SOURCE", item["anchor_source_id"], item["anchor_source_generation"], item["anchor_source_identity_basis"], item["anchor_key_id"], item["anchor_key_generation"]):
            return None
    if not add("ANCHOR_SOURCE", anchor["anchor_source_id"], anchor["anchor_source_generation"], anchor["anchor_source_identity_basis"], anchor["anchor_key_id"], anchor["anchor_key_generation"]):
        return None
    for context in contexts:
        item = context["adapter_admission"]
        if not add("ANCHOR_ADAPTER", item["adapter_id"], item["adapter_generation"], item["adapter_identity_basis"]):
            return None
    for record in binding.witness_source_admissions:
        item = record.values
        if not add("WITNESS_SOURCE", item["witness_id"], item["witness_generation"], item["witness_identity_basis"]):
            return None
    reconciliation = contexts[0].get("cross_domain_reconciliation")
    if reconciliation is not None and not add("RECONCILIATION_AUTHORITY", reconciliation["source_id"], reconciliation["authority_generation"], reconciliation["source_id"]):
        return None
    for record in binding.recovery_installations:
        item = record.values
        if not add("RECOVERY_AUTHORITY", item["recovery_authority_id"], item["recovery_authority_generation"], item["recovery_authority_identity_basis"]):
            return None
    return result


def _control_plane_unavailable(
    case: OracleInput, code: str, detail: str,
) -> OracleResult:
    return _observation_unavailable(
        case, code, detail, ("evidence_binding", "binding_source_authority", "freshness"),
    )


def _evaluate_control_plane_independence(
    case: OracleInput,
    binding: ObservationBinding,
    root: Any,
    anchor: Mapping[str, Any],
    contexts: list[Mapping[str, Any]],
) -> OracleResult | None:
    """Close every selected authority role through protected appraisal facts."""
    negative_states = {"REVOKED", "REJECTED", "INVALID", "PROHIBITED"}
    policy = contexts[0]["control_plane_policy"]
    memberships = contexts[0]["control_plane_memberships"]
    appraisal_roots = contexts[0]["independence_appraisal_roots"]
    transitions = contexts[0]["control_plane_membership_transitions"]
    consolidations = contexts[0]["authorized_consolidations"]

    protected_keys = (
        "control_plane_policy", "control_plane_memberships",
        "independence_appraisal_roots", "control_plane_membership_transitions",
        "authorized_consolidations",
    )
    if any(
        any(context[name] != contexts[0][name] for name in protected_keys)
        for context in contexts[1:]
    ):
        return _control_plane_unavailable(
            case, "CONTROL_PLANE_POLICY_CONFLICTING",
            "Protected control-plane contexts disagree about policy or membership.",
        )
    if policy["lifecycle_state"] in negative_states:
        return OracleResult(
            AuthorityOutcome.DENIED,
            (Reason("CONTROL_PLANE_POLICY_PROHIBITED", "Current authoritative evidence prohibits the control-plane policy.", ("evidence_binding",)),),
            _engaged(case),
        )
    applicable = _applicable_control_plane_roles(binding, root, anchor, contexts)
    identity_expectations = _control_plane_identity_expectations(
        binding, root, anchor, contexts
    )
    if identity_expectations is None or set(identity_expectations) != applicable:
        return _control_plane_unavailable(
            case, "CONTROL_PLANE_IDENTITY_CONFLICTING",
            "Selected authority records disagree about protected role identity or key generation.",
        )
    applicable_roles = {role for role, _, _ in applicable}
    required_roles = policy["required_roles"]
    separation_sets = policy["required_separation_sets"]
    if (
        policy["relationship"] != "CONTROL_PLANE_SEPARATION_POLICY"
        or policy["selection_rule"] != "ALL_APPLICABLE"
        or not isinstance(required_roles, (list, tuple))
        or not required_roles
        or len(required_roles) != len(set(required_roles))
        or set(required_roles) != applicable_roles
        or not set(required_roles).issubset(CONTROL_PLANE_ROLES)
        or not isinstance(separation_sets, (list, tuple))
        or not all(isinstance(group, (list, tuple)) and group for group in separation_sets)
        or any(not set(group).issubset(applicable_roles) for group in separation_sets)
        or policy["source_id"] != root.root_id
        or policy["authority_generation"] != root.authority_generation
        or policy["ordering_source_id"] != root.ordering_source_id
        or policy["boundary"] != root.boundary
        or policy["boundary_epoch"] != root.boundary_epoch
        or policy["freshness_challenge_id"] != anchor["freshness_challenge_id"]
        or policy["lifecycle_state"] != "ACTIVE"
    ):
        return _control_plane_unavailable(
            case, "APPLICABLE_ROLE_POLICY_UNAVAILABLE",
            "No exact current all-applicable control-plane role policy exists.",
        )

    membership_index: dict[tuple[str, str, int], Mapping[str, Any]] = {}
    for item in memberships:
        key = (item["role"], item["member_id"], item["member_generation"])
        if key in membership_index:
            return _control_plane_unavailable(
                case, "CONTROL_PLANE_MEMBERSHIP_CONFLICTING",
                "A selected control-plane role has duplicate protected membership.",
            )
        membership_index[key] = item
    if set(membership_index) != applicable:
        return _control_plane_unavailable(
            case, "CONTROL_PLANE_MEMBERSHIP_UNAVAILABLE",
            "Protected role membership does not exactly cover the selected authority path.",
        )

    root_index = {
        (item["appraisal_root_id"], item["appraisal_root_generation"]): item
        for item in appraisal_roots
    }
    if len(root_index) != len(appraisal_roots):
        return _control_plane_unavailable(
            case, "INDEPENDENCE_APPRAISAL_CONFLICTING",
            "Independence-appraisal root identity is ambiguous.",
        )
    required_root_ids = policy["required_appraisal_root_ids"]
    if (
        not isinstance(required_root_ids, (list, tuple))
        or not required_root_ids
        or set(required_root_ids) != {item[0] for item in root_index}
    ):
        return _control_plane_unavailable(
            case, "INDEPENDENCE_APPRAISAL_ROOT_UNAVAILABLE",
            "The protected policy does not select the exact appraisal-root set.",
        )
    for appraisal in appraisal_roots:
        if appraisal["lifecycle_state"] in negative_states:
            return OracleResult(
                AuthorityOutcome.DENIED,
                (Reason("INDEPENDENCE_APPRAISAL_ROOT_PROHIBITED", "Current authoritative evidence prohibits an independence-appraisal root.", ("evidence_binding",)),),
                _engaged(case),
            )
        if (
            appraisal["relationship"] != "INDEPENDENCE_APPRAISAL_ROOT_ADMISSION"
            or appraisal["membership_epoch"] != policy["membership_epoch"]
            or appraisal["boundary"] != root.boundary
            or appraisal["boundary_epoch"] != root.boundary_epoch
            or appraisal["start_event_order"] > binding.t1_anchor.event_order
            or appraisal["end_event_order"] < binding.t3_anchor.event_order
            or appraisal["source_id"] == root.root_id
            or appraisal["source_id"] in {item["member_id"] for item in memberships}
            or not isinstance(appraisal["authority_generation"], int)
            or appraisal["authority_generation"] < 1
            or appraisal["freshness_challenge_id"] != anchor["freshness_challenge_id"]
            or appraisal["lifecycle_state"] != "ACTIVE"
        ):
            return _control_plane_unavailable(
                case, "INDEPENDENCE_APPRAISAL_ROOT_UNAVAILABLE",
                "An appraisal root is stale, out of scope, or not current.",
            )

    for key, item in membership_index.items():
        if item["lifecycle_state"] in negative_states:
            return OracleResult(
                AuthorityOutcome.DENIED,
                (Reason("CONTROL_PLANE_MEMBERSHIP_PROHIBITED", "Current authoritative evidence prohibits a selected role membership.", ("evidence_binding",)),),
                _engaged(case),
            )
        if (
            item["relationship"] != "CONTROL_PLANE_ROLE_MEMBERSHIP"
            or item["role"] not in CONTROL_PLANE_ROLES
            or item["membership_epoch"] != policy["membership_epoch"]
            or item["boundary"] != root.boundary
            or item["boundary_epoch"] != root.boundary_epoch
            or item["start_event_order"] > binding.t1_anchor.event_order
            or item["end_event_order"] < binding.t3_anchor.event_order
            or item["source_id"] != root.root_id
            or item["authority_generation"] != root.authority_generation
            or item["ordering_source_id"] != root.ordering_source_id
            or item["freshness_challenge_id"] != anchor["freshness_challenge_id"]
            or item["lifecycle_state"] != "ACTIVE"
            or not isinstance(item["authority_scope"], (list, tuple))
            or "AUTHORITY_DECISION" not in item["authority_scope"]
        ):
            return _control_plane_unavailable(
                case, "CONTROL_PLANE_MEMBERSHIP_UNAVAILABLE",
                "A selected role membership is stale, incomplete, or out of scope.",
            )
        expected_identity, expected_key, expected_key_generation = identity_expectations[key]
        if (
            item["identity_basis"] != expected_identity
            or (expected_key is not None and item["credential_or_key_id"] != expected_key)
            or (
                expected_key_generation is not None
                and item["credential_or_key_generation"] != expected_key_generation
            )
        ):
            return _control_plane_unavailable(
                case, "CONTROL_PLANE_IDENTITY_UNAVAILABLE",
                "Protected membership does not bind the exact selected role identity and key generation.",
            )
        appraisal_root = root_index.get((item["appraiser_id"], item["appraiser_generation"]))
        if appraisal_root is not None:
            if item["appraisal_root_id"] != appraisal_root["appraisal_root_id"]:
                return _control_plane_unavailable(case, "INDEPENDENCE_APPRAISAL_UNAVAILABLE", "Membership appraisal does not close at its selected root.")
            if item["member_id"] == appraisal_root["appraisal_root_id"] or _effective_domain(item) == _effective_domain(appraisal_root):
                return _control_plane_unavailable(case, "INDEPENDENCE_APPRAISAL_CYCLE", "An appraisal root is inside the effective domain it appraises.")

    # Follow every appraisal edge. It must terminate at an admitted root and may
    # not self-support or cycle through another selected role.
    by_identity = {
        (item["member_id"], item["member_generation"]): item
        for item in memberships
    }
    for start in memberships:
        seen: set[tuple[str, int]] = set()
        node = start
        while True:
            node_key = (node["member_id"], node["member_generation"])
            if node_key in seen:
                return _control_plane_unavailable(case, "INDEPENDENCE_APPRAISAL_CYCLE", "The protected appraisal graph contains a cycle.")
            seen.add(node_key)
            target_key = (node["appraiser_id"], node["appraiser_generation"])
            appraisal_root = root_index.get(target_key)
            if appraisal_root is not None:
                if node["appraisal_root_id"] != appraisal_root["appraisal_root_id"]:
                    return _control_plane_unavailable(case, "INDEPENDENCE_APPRAISAL_UNAVAILABLE", "The appraisal chain terminates at the wrong root.")
                break
            target = by_identity.get(target_key)
            if target is None:
                return _control_plane_unavailable(case, "INDEPENDENCE_APPRAISAL_UNAVAILABLE", "The appraisal chain has no admitted terminal root.")
            node = target

    transition_index = {
        (item["role"], item["new_member_id"], item["new_member_generation"]): item
        for item in transitions
    }
    for key, item in membership_index.items():
        if item["member_generation"] <= 1 and policy["membership_epoch"] <= 1:
            continue
        transition = transition_index.get(key)
        if (
            transition is None
            or transition["relationship"] != "CONTROL_PLANE_MEMBERSHIP_TRANSITION"
            or transition["new_member_id"] != item["member_id"]
            or transition["new_member_generation"] != item["member_generation"]
            or transition["old_member_generation"] != max(0, item["member_generation"] - 1)
            or transition["transition_reason"] not in {"ROTATION", "SEPARATION", "CONSOLIDATION", "RECOVERY"}
            or not isinstance(transition["old_effective_domain"], (list, tuple))
            or len(transition["old_effective_domain"]) != 4
            or transition["new_effective_domain"] != _effective_domain(item)
            or transition["policy_id"] != policy["policy_id"]
            or transition["membership_epoch"] != policy["membership_epoch"]
            or transition["appraisal_root_id"] != item["appraisal_root_id"]
            or transition["boundary"] != root.boundary
            or transition["boundary_epoch"] != root.boundary_epoch
            or transition["source_id"] != root.root_id
            or transition["authority_generation"] != root.authority_generation
            or transition["ordering_source_id"] != root.ordering_source_id
            or transition["freshness_challenge_id"] != anchor["freshness_challenge_id"]
            or transition["lifecycle_state"] != "ACTIVE"
        ):
            return _control_plane_unavailable(case, "CONTROL_PLANE_MEMBERSHIP_TRANSITION_UNAVAILABLE", "Role replacement lacks one exact protected membership transition.")

    allowed_ids = policy["allowed_consolidation_ids"]
    if not isinstance(allowed_ids, (list, tuple)) or set(allowed_ids) != {item["consolidation_id"] for item in consolidations}:
        return _control_plane_unavailable(case, "ROLE_CONSOLIDATION_UNAVAILABLE", "The exact authorized consolidation set is unavailable.")
    permitted_pairs: set[frozenset[str]] = set()
    for consolidation in consolidations:
        if consolidation["lifecycle_state"] in negative_states:
            return OracleResult(
                AuthorityOutcome.DENIED,
                (Reason("ROLE_CONSOLIDATION_PROHIBITED", "Current authoritative evidence prohibits role consolidation.", ("evidence_binding",)),),
                _engaged(case),
            )
        roles = consolidation["roles"]
        member_keys = consolidation["member_keys"]
        selected_members = [
            item for key, item in membership_index.items()
            if f"{key[0]}:{key[1]}:{key[2]}" in member_keys
        ]
        if (
            consolidation["relationship"] != "AUTHORIZED_ROLE_CONSOLIDATION"
            or not isinstance(roles, (list, tuple))
            or len(roles) < 2
            or not set(roles).issubset(applicable_roles)
            or not isinstance(member_keys, (list, tuple))
            or len(member_keys) != len(set(member_keys))
            or len(selected_members) != len(member_keys)
            or {item["role"] for item in selected_members} != set(roles)
            or len({_effective_domain(item) for item in selected_members}) != 1
            or consolidation["effective_domain"] != _effective_domain(selected_members[0])
            or consolidation["policy_id"] != policy["policy_id"]
            or consolidation["membership_epoch"] != policy["membership_epoch"]
            or consolidation["appraisal_root_id"] not in required_root_ids
            or consolidation["boundary"] != root.boundary
            or consolidation["boundary_epoch"] != root.boundary_epoch
            or consolidation["source_id"] != root.root_id
            or consolidation["authority_generation"] != root.authority_generation
            or consolidation["ordering_source_id"] != root.ordering_source_id
            or consolidation["freshness_challenge_id"] != anchor["freshness_challenge_id"]
            or consolidation["lifecycle_state"] != "ACTIVE"
        ):
            return _control_plane_unavailable(case, "ROLE_CONSOLIDATION_UNAVAILABLE", "Role consolidation is stale, incomplete, or unauthorized.")
        permitted_pairs.add(frozenset(roles))

    domains_by_role: dict[str, set[tuple[str, str, str, str]]] = {}
    for item in memberships:
        domains_by_role.setdefault(item["role"], set()).add(_effective_domain(item))
    for group in separation_sets:
        seen_domains: dict[tuple[str, str, str, str], set[str]] = {}
        seen_components: list[dict[str, set[str]]] = [{}, {}, {}, {}]
        for role in group:
            for domain in domains_by_role.get(role, set()):
                seen_domains.setdefault(domain, set()).add(role)
                for index, value in enumerate(domain):
                    seen_components[index].setdefault(value, set()).add(role)
        for roles in seen_domains.values():
            if len(roles) > 1 and not any(roles.issubset(pair) for pair in permitted_pairs):
                return _control_plane_unavailable(case, "CONTROL_PLANE_INDEPENDENCE_UNAVAILABLE", "Nominally distinct roles share one protected effective authority domain.")
        for component in seen_components:
            for roles in component.values():
                if len(roles) > 1 and not any(roles.issubset(pair) for pair in permitted_pairs):
                    return _control_plane_unavailable(case, "CONTROL_PLANE_INDEPENDENCE_UNAVAILABLE", "Required roles share a protected source, controller, upstream dependency, or rollback domain.")
    return None


def _delegation_result(
    case: OracleInput,
    outcome: AuthorityOutcome,
    code: str,
    detail: str,
) -> OracleResult:
    return OracleResult(outcome, (Reason(code, detail, ("delegation_binding",)),), _engaged(case))


def _scope_is_subset(child: Mapping[str, Any], parent: Mapping[str, Any]) -> bool:
    for field in (
        "actions", "artifacts", "tools", "semantic_scopes", "boundaries",
        "subject_classes",
    ):
        if not set(child[field]).issubset(set(parent[field])):
            return False
    return (
        child["valid_from_order"] >= parent["valid_from_order"]
        and child["valid_until_order"] <= parent["valid_until_order"]
        and child["maximum_depth"] <= parent["maximum_depth"]
    )


def _evaluate_delegation_authority(
    case: OracleInput,
    active_state: Any,
) -> tuple[OracleResult | None, Mapping[str, Any] | None]:
    """Validate a protected root-closed delegation chain and return its terminal edge."""
    contexts = tuple(
        item["delegation_authority_context"] for item in case.trusted_anchor_context
    )
    if not contexts:
        return (
            _delegation_result(
                case, AuthorityOutcome.UNAVAILABLE,
                "DELEGATION_AUTHORITY_CONTEXT_UNAVAILABLE",
                "Harness-owned delegation authority context is unavailable.",
            ),
            None,
        )
    if active_state.subject_mode == "DIRECT":
        protected_fields = (
            "delegation_principals", "delegation_grants",
            "delegation_lifecycle_records", "delegation_ordering_heads",
            "delegation_principal_transitions", "delegation_grant_transitions",
            "delegation_terminal_uses",
        )
        if any(context[field] for context in contexts for field in protected_fields):
            return (
                _delegation_result(
                    case, AuthorityOutcome.UNAVAILABLE, "DELEGATION_CONFLICTING",
                    "Direct authority has incompatible protected delegated-authority state.",
                ),
                None,
            )
        return None, None
    first = contexts[0]
    if any(context != first for context in contexts[1:]):
        return (
            _delegation_result(
                case, AuthorityOutcome.UNAVAILABLE, "DELEGATION_CONFLICTING",
                "Protected delegation authority contexts conflict.",
            ),
            None,
        )
    policy = first["delegation_policy"]
    root = case.t3_binding_facts.authority_root
    binding = case.observation_binding
    freshness = case.observation_freshness
    if root is None or binding is None or freshness is None:
        return (
            _delegation_result(
                case, AuthorityOutcome.UNAVAILABLE,
                "DELEGATION_ROOT_AUTHORITY_UNAVAILABLE",
                "Delegation cannot be joined to the current root and observation interval.",
            ),
            None,
        )
    if (
        policy["relationship"] != "DELEGATION_AUTHORITY_POLICY"
        or policy["selection_rule"] != "ALL_APPLICABLE"
        or policy["boundary"] != root.boundary
        or policy["boundary_epoch"] != root.boundary_epoch
        or policy["source_id"] != root.root_id
        or policy["authority_generation"] != root.authority_generation
        or policy["ordering_source_id"] != root.ordering_source_id
        or policy["freshness_challenge_id"] != freshness.freshness_challenge_id
        or policy["lifecycle_state"] != "ACTIVE"
    ):
        return (
            _delegation_result(
                case, AuthorityOutcome.UNAVAILABLE,
                "DELEGATION_ROOT_AUTHORITY_UNAVAILABLE",
                "Delegation policy lacks an exact current applicable root join.",
            ),
            None,
        )

    principals = first["delegation_principals"]
    grants = first["delegation_grants"]
    lifecycles = first["delegation_lifecycle_records"]
    heads = first["delegation_ordering_heads"]
    uses = first["delegation_terminal_uses"]
    candidate = case.facts["delegation_binding"].value

    if active_state.subject_mode != "DELEGATED" or not isinstance(candidate, Mapping):
        return (
            _delegation_result(
                case, AuthorityOutcome.UNAVAILABLE,
                "DELEGATION_RELATIONSHIP_UNAVAILABLE",
                "The evaluated subject relationship is not an exact delegated relationship.",
            ),
            None,
        )
    if len(heads) != 1:
        return (
            _delegation_result(
                case, AuthorityOutcome.UNAVAILABLE, "DELEGATION_ORDERING_UNAVAILABLE",
                "Delegation authority lacks one unique current ordering head.",
            ),
            None,
        )
    head = heads[0]
    if (
        head["relationship"] != "DELEGATION_ORDERING_HEAD"
        or head["root_id"] != root.root_id
        or head["source_id"] != root.root_id
        or head["authority_generation"] != root.authority_generation
        or head["lineage"] != root.lineage
        or head["boundary"] != root.boundary
        or head["boundary_epoch"] != root.boundary_epoch
        or head["freshness_challenge_id"] != freshness.freshness_challenge_id
        or head["lifecycle_state"] != "ACTIVE"
        or head["head_event_order"] > binding.t3_anchor.event_order
    ):
        return (
            _delegation_result(
                case, AuthorityOutcome.UNAVAILABLE, "DELEGATION_ORDERING_UNAVAILABLE",
                "Delegation ordering head is not exactly current and root-applicable.",
            ),
            None,
        )

    grant_by_key: dict[tuple[str, int], Mapping[str, Any]] = {}
    for grant in grants:
        key = (grant["grant_id"], grant["grant_generation"])
        if key in grant_by_key:
            return (
                _delegation_result(
                    case, AuthorityOutcome.UNAVAILABLE, "DELEGATION_CONFLICTING",
                    "Protected delegation grant identities conflict.",
                ),
                None,
            )
        grant_by_key[key] = grant
    key = (head["head_grant_id"], head["head_grant_generation"])
    chain_reversed: list[Mapping[str, Any]] = []
    seen_grants: set[tuple[str, int]] = set()
    seen_principals: set[tuple[str, int, str]] = set()
    while True:
        if key in seen_grants:
            return (
                _delegation_result(
                    case, AuthorityOutcome.UNAVAILABLE, "DELEGATION_CHAIN_CYCLE",
                    "Delegation chain repeats a protected grant.",
                ),
                None,
            )
        grant = grant_by_key.get(key)
        if grant is None:
            return (
                _delegation_result(
                    case, AuthorityOutcome.UNAVAILABLE, "DELEGATION_CHAIN_INCOMPLETE",
                    "Delegation chain is missing a required edge.",
                ),
                None,
            )
        seen_grants.add(key)
        delegate_node = (
            grant["delegate_id"], grant["delegate_generation"],
            grant["delegate_identity_basis"],
        )
        if delegate_node in seen_principals:
            return (
                _delegation_result(
                    case, AuthorityOutcome.UNAVAILABLE, "DELEGATION_CHAIN_CYCLE",
                    "Delegation chain repeats a principal authority node.",
                ),
                None,
            )
        seen_principals.add(delegate_node)
        if (
            grant["delegator_id"] == grant["delegate_id"]
            and grant["delegator_generation"] == grant["delegate_generation"]
        ):
            return (
                _delegation_result(
                    case, AuthorityOutcome.UNAVAILABLE, "DELEGATION_CHAIN_CYCLE",
                    "Self-delegation cannot bootstrap authority.",
                ),
                None,
            )
        chain_reversed.append(grant)
        if grant["parent_grant_id"] == "ROOT_AUTHORITY":
            break
        key = (grant["parent_grant_id"], grant["parent_grant_generation"])
        if len(chain_reversed) > policy["maximum_chain_depth"]:
            return (
                _delegation_result(
                    case, AuthorityOutcome.UNAVAILABLE, "DELEGATION_CHAIN_INCOMPLETE",
                    "Delegation chain exceeds the root-authorized maximum depth.",
                ),
                None,
            )
    chain = tuple(reversed(chain_reversed))
    if len(chain) > policy["maximum_chain_depth"]:
        return (
            _delegation_result(
                case, AuthorityOutcome.UNAVAILABLE, "DELEGATION_CHAIN_INCOMPLETE",
                "Delegation chain exceeds policy depth.",
            ),
            None,
        )

    principal_transitions = first["delegation_principal_transitions"]
    grant_transitions = first["delegation_grant_transitions"]
    chain_nodes = {
        (grant["delegator_id"], grant["delegator_generation"])
        for grant in chain
    } | {
        (grant["delegate_id"], grant["delegate_generation"])
        for grant in chain
    }
    for transition in principal_transitions:
        old_node = (
            transition["old_principal_id"], transition["old_principal_generation"]
        )
        new_node = (
            transition["new_principal_id"], transition["new_principal_generation"]
        )
        if (
            old_node not in chain_nodes
            and new_node not in chain_nodes
        ) or transition["event_order"] > head["head_event_order"]:
            continue
        exact_grant_transitions = tuple(
            item for item in grant_transitions
            if item["event_order"] == transition["event_order"]
            and item["source_id"] == root.root_id
            and item["authority_generation"] == root.authority_generation
            and item["lineage"] == root.lineage
            and item["boundary"] == root.boundary
            and item["boundary_epoch"] == root.boundary_epoch
            and item["lifecycle_state"] == "ACTIVE"
        )
        if new_node not in chain_nodes or len(exact_grant_transitions) != 1:
            return (
                _delegation_result(
                    case, AuthorityOutcome.UNAVAILABLE,
                    "DELEGATION_SUCCESSOR_AUTHORITY_UNAVAILABLE",
                    "A principal transition lacks one exact successor-specific grant transition.",
                ),
                None,
            )

    principal_by_key = {
        (item["principal_id"], item["principal_generation"], item["identity_basis"]): item
        for item in principals
    }
    if len(principal_by_key) != len(principals):
        return (
            _delegation_result(
                case, AuthorityOutcome.UNAVAILABLE,
                "DELEGATION_PRINCIPAL_ADMISSION_UNAVAILABLE",
                "Protected principal admissions are ambiguous.",
            ),
            None,
        )
    lifecycle_by_target: dict[tuple[str, str, int], list[Mapping[str, Any]]] = {}
    for record in lifecycles:
        lifecycle_by_target.setdefault(
            (record["target_kind"], record["target_id"], record["target_generation"]), []
        ).append(record)

    previous: Mapping[str, Any] | None = None
    for index, grant in enumerate(chain):
        if (
            grant["relationship"] != "DELEGATION_GRANT"
            or grant["chain_id"] != head["chain_id"]
            or grant["root_id"] != root.root_id
            or grant["source_id"] != root.root_id
            or grant["authority_generation"] != root.authority_generation
            or grant["lineage"] != root.lineage
            or grant["boundary"] != root.boundary
            or grant["boundary_epoch"] != root.boundary_epoch
            or grant["created_event_order"] > grant["effective_start_order"]
            or grant["effective_start_order"] > head["head_event_order"]
            or grant["effective_end_order"] < head["head_event_order"]
            or grant["hop_depth"] != index
            or grant["maximum_depth"] > policy["maximum_chain_depth"]
        ):
            return (
                _delegation_result(
                    case, AuthorityOutcome.UNAVAILABLE, "DELEGATION_CURRENTNESS_UNAVAILABLE",
                    "A delegation edge is stale, misordered, or outside the applicable root context.",
                ),
                None,
            )
        delegator_key = (
            grant["delegator_id"], grant["delegator_generation"],
            grant["delegator_identity_basis"],
        )
        delegate_key = (
            grant["delegate_id"], grant["delegate_generation"],
            grant["delegate_identity_basis"],
        )
        delegator = principal_by_key.get(delegator_key)
        delegate = principal_by_key.get(delegate_key)
        if delegator is None:
            return (
                _delegation_result(
                    case, AuthorityOutcome.UNAVAILABLE,
                    "DELEGATION_SOURCE_AUTHORITY_UNAVAILABLE",
                    "The exact delegator lacks independent protected admission.",
                ),
                None,
            )
        if delegate is None:
            return (
                _delegation_result(
                    case, AuthorityOutcome.UNAVAILABLE, "DELEGATE_ADMISSION_UNAVAILABLE",
                    "The exact delegate lacks independent protected admission.",
                ),
                None,
            )
        for principal, role in ((delegator, "DELEGATOR"), (delegate, "DELEGATE")):
            if (
                role not in principal["roles"]
                or principal["root_id"] != root.root_id
                or principal["source_id"] != root.root_id
                or principal["authority_generation"] != root.authority_generation
                or principal["lineage"] != root.lineage
                or principal["boundary"] != root.boundary
                or principal["boundary_epoch"] != root.boundary_epoch
                or principal["start_event_order"] > head["head_event_order"]
                or principal["end_event_order"] < head["head_event_order"]
                or principal["freshness_challenge_id"] != freshness.freshness_challenge_id
                or principal["lifecycle_state"] != "ACTIVE"
            ):
                return (
                    _delegation_result(
                        case, AuthorityOutcome.UNAVAILABLE,
                        "DELEGATION_PRINCIPAL_ADMISSION_UNAVAILABLE",
                        "A delegation principal is not exactly current, scoped, and root-admitted.",
                    ),
                    None,
                )
        records = lifecycle_by_target.get(
            ("GRANT", grant["grant_id"], grant["grant_generation"]), []
        )
        if len(records) != 1:
            return (
                _delegation_result(
                    case, AuthorityOutcome.UNAVAILABLE,
                    "DELEGATION_CURRENTNESS_UNAVAILABLE",
                    "A delegation grant lacks one authoritative lifecycle record.",
                ),
                None,
            )
        lifecycle = records[0]
        if lifecycle["state"] in {"REVOKED", "REJECTED", "PROHIBITED"}:
            return (
                _delegation_result(
                    case, AuthorityOutcome.DENIED, "DELEGATION_REVOKED",
                    "A current applicable upstream delegation edge is revoked or prohibited.",
                ),
                None,
            )
        if (
            lifecycle["state"] != "ACTIVE"
            or grant["lifecycle_state"] != "ACTIVE"
            or lifecycle["event_order"] > head["head_event_order"]
            or lifecycle["source_id"] != root.root_id
            or lifecycle["authority_generation"] != root.authority_generation
        ):
            return (
                _delegation_result(
                    case, AuthorityOutcome.UNAVAILABLE,
                    "DELEGATION_CURRENTNESS_UNAVAILABLE",
                    "A delegation grant is stale, expired, superseded, or unordered.",
                ),
                None,
            )
        if previous is None:
            if grant["parent_grant_id"] != "ROOT_AUTHORITY" or grant["delegator_id"] != root.root_id:
                return (
                    _delegation_result(
                        case, AuthorityOutcome.UNAVAILABLE,
                        "DELEGATION_ROOT_AUTHORITY_UNAVAILABLE",
                        "Delegation chain does not terminate at the independently admitted root.",
                    ),
                    None,
                )
        else:
            if (
                grant["parent_grant_id"] != previous["grant_id"]
                or grant["parent_grant_generation"] != previous["grant_generation"]
                or grant["delegator_id"] != previous["delegate_id"]
                or grant["delegator_generation"] != previous["delegate_generation"]
                or grant["delegator_identity_basis"] != previous["delegate_identity_basis"]
            ):
                return (
                    _delegation_result(
                        case, AuthorityOutcome.UNAVAILABLE,
                        "DELEGATION_CHAIN_INCOMPLETE",
                        "Delegation chain contains an unrelated splice or missing edge.",
                    ),
                    None,
                )
            if not previous["further_delegation"]:
                return (
                    _delegation_result(
                        case, AuthorityOutcome.UNAVAILABLE,
                        "DELEGABLE_SCOPE_UNAVAILABLE",
                        "Action authority does not independently establish delegation authority.",
                    ),
                    None,
                )
            if not _scope_is_subset(grant["action_scope"], previous["delegable_scope"]):
                return (
                    _delegation_result(
                        case, AuthorityOutcome.UNAVAILABLE, "DELEGATION_SCOPE_WIDENING",
                        "A downstream delegation edge widens upstream delegable scope.",
                    ),
                    None,
                )
        previous = grant

    terminal = chain[-1]
    if len(uses) != 1:
        return (
            _delegation_result(
                case, AuthorityOutcome.UNAVAILABLE, "DELEGATION_GRANT_USE_UNAVAILABLE",
                "Delegated execution lacks one exact protected terminal-use binding.",
            ),
            None,
        )
    use = uses[0]
    objective = case.t3_binding_facts.objective_identity
    contract = case.t3_binding_facts.decision_contract_identity
    expected_use = (
        use["relationship"] == "DELEGATION_TERMINAL_USE"
        and use["chain_id"] == terminal["chain_id"]
        and use["terminal_grant_id"] == terminal["grant_id"]
        and use["terminal_grant_generation"] == terminal["grant_generation"]
        and use["execution_grant_id"] == active_state.grant_id
        and use["subject_id"] == case.authority_tuple.subject
        and use["subject_generation"] == terminal["delegate_generation"]
        and use["subject_identity_basis"] == case.authority_tuple.identity_basis
        and use["artifact"] == case.authority_tuple.artifact
        and use["boundary"] == root.boundary
        and use["boundary_epoch"] == root.boundary_epoch
        and use["execution_context"] == case.facts["execution_context"].value
        and use["consumption_state"] == case.facts["consumption_state"].value
        and objective is not None
        and use["objective_id"] == objective.objective_id
        and use["objective_generation"] == objective.objective_generation
        and contract is not None
        and use["decision_contract_id"] == contract.contract_id
        and use["decision_contract_version"] == contract.contract_version
        and use["use_event_order"] == head["head_event_order"]
        and use["freshness_challenge_id"] == freshness.freshness_challenge_id
        and use["lifecycle_state"] == "ACTIVE"
        and use["effect"] in terminal["action_scope"]["actions"]
        and use["artifact"] in terminal["action_scope"]["artifacts"]
        and use["tool"] in terminal["action_scope"]["tools"]
    )
    if not expected_use:
        return (
            _delegation_result(
                case, AuthorityOutcome.UNAVAILABLE, "DELEGATION_GRANT_USE_UNAVAILABLE",
                "Terminal execution is not bound to the exact current delegation chain and effect.",
            ),
            None,
        )
    expected_candidate = {
        "relationship": "EXACT_DELEGATION",
        "delegator": terminal["delegator_id"],
        "delegate": terminal["delegate_id"],
        "artifact": use["artifact"],
        "control_state": case.authority_tuple.control_state,
        "boundary_epoch": use["boundary_epoch"],
        "applicable_boundary": use["boundary"],
    }
    if not _relation_matches(candidate, expected_candidate):
        code = (
            "DELEGATION_SOURCE_AUTHORITY_UNAVAILABLE"
            if candidate.get("delegator") != terminal["delegator_id"]
            else "DELEGATION_RELATIONSHIP_UNAVAILABLE"
        )
        return (
            _delegation_result(
                case, AuthorityOutcome.UNAVAILABLE, code,
                "Candidate delegation does not match the protected current terminal edge.",
            ),
            None,
        )
    return None, terminal


def _approval_result(
    case: OracleInput, outcome: AuthorityOutcome, code: str, detail: str
) -> OracleResult:
    return OracleResult(
        outcome, (Reason(code, detail, ("human_approval_binding",)),), _engaged(case)
    )


def _evaluate_human_approval(
    case: OracleInput,
    active_state: AuthorityStateBinding,
    protected_terminal_grant: Mapping[str, Any] | None,
) -> OracleResult | None:
    """Join a typed approval/use relation to independently protected approval authority."""
    contexts = tuple(
        item["human_approval_authority_context"]
        for item in case.trusted_anchor_context
    )
    if not contexts:
        return _approval_result(
            case, AuthorityOutcome.UNAVAILABLE, "HUMAN_APPROVAL_POLICY_UNAVAILABLE",
            "Protected human-approval policy state is unavailable.",
        )
    first = contexts[0]
    if any(item != first for item in contexts[1:]):
        return _approval_result(
            case, AuthorityOutcome.UNAVAILABLE, "HUMAN_APPROVAL_POLICY_CONFLICTING",
            "Protected human-approval policy contexts conflict.",
        )
    policy = first["approval_policy"]
    root = case.t3_binding_facts.authority_root
    objective = case.t3_binding_facts.objective_identity
    contract = case.t3_binding_facts.decision_contract_identity
    freshness = case.observation_freshness
    observation = case.observation_binding
    if root is None or objective is None or contract is None or freshness is None or observation is None:
        return _approval_result(
            case, AuthorityOutcome.UNAVAILABLE, "HUMAN_APPROVAL_POLICY_UNAVAILABLE",
            "Approval policy cannot join the current authority and observation context.",
        )
    if (
        policy["relationship"] != "HUMAN_APPROVAL_POLICY"
        or policy["selection_rule"] != "ALL_APPLICABLE"
        or policy["source_id"] != root.root_id
        or policy["authority_generation"] != root.authority_generation
        or policy["ordering_source_id"] != root.ordering_source_id
        or policy["boundary"] != root.boundary
        or policy["boundary_epoch"] != root.boundary_epoch
        or policy["objective_id"] != objective.objective_id
        or policy["objective_generation"] != objective.objective_generation
        or policy["decision_contract_id"] != contract.contract_id
        or policy["decision_contract_version"] != contract.contract_version
        or policy["freshness_challenge_id"] != freshness.freshness_challenge_id
    ):
        return _approval_result(
            case, AuthorityOutcome.UNAVAILABLE, "HUMAN_APPROVAL_POLICY_UNAVAILABLE",
            "Approval policy is not exact, current, root-issued, and applicable.",
        )
    if policy["lifecycle_state"] in {"REVOKED", "REJECTED", "PROHIBITED"}:
        return _approval_result(
            case, AuthorityOutcome.DENIED, "HUMAN_APPROVAL_POLICY_PROHIBITED",
            "The current authoritative approval policy is revoked or prohibited.",
        )
    if policy["lifecycle_state"] != "ACTIVE":
        return _approval_result(
            case, AuthorityOutcome.UNAVAILABLE, "HUMAN_APPROVAL_POLICY_UNAVAILABLE",
            "Approval policy lifecycle is not current.",
        )

    reserved = RESERVED_HUMAN_APPROVAL_FACTS.intersection(case.facts)
    if reserved:
        return _approval_result(
            case, AuthorityOutcome.UNAVAILABLE, "HUMAN_APPROVAL_RELATIONSHIP_UNAVAILABLE",
            "Generic approval facts cannot establish typed human approval authority.",
        )
    binding = case.human_approval_binding
    if policy["requirement"] == "NONE":
        if binding is not None:
            return _approval_result(
                case, AuthorityOutcome.UNAVAILABLE, "HUMAN_APPROVAL_POLICY_CONFLICTING",
                "Candidate approval evidence conflicts with the selected no-approval policy.",
            )
        return None
    if policy["requirement"] != "REQUIRED" or binding is None:
        return _approval_result(
            case, AuthorityOutcome.UNAVAILABLE, "HUMAN_APPROVAL_REQUIRED",
            "The selected policy requires a typed current human approval relation.",
        )

    chain_id = (
        protected_terminal_grant["chain_id"]
        if protected_terminal_grant is not None else "DIRECT"
    )
    expected_policy_values = {
        "policy_id": binding["policy_id"],
        "policy_generation": binding["policy_generation"],
        "artifact": binding["artifact"],
        "effect": binding["effect"],
        "subject_id": binding["subject_id"],
        "executor_id": binding["executor_id"],
        "delegation_chain_id": binding["delegation_chain_id"],
        "tool_backend_id": binding["tool_backend_id"],
        "credential_generation": binding["credential_generation"],
        "execution_context": binding["execution_context"],
        "boundary": binding["boundary"],
        "boundary_epoch": binding["boundary_epoch"],
        "objective_id": binding["objective_id"],
        "objective_generation": binding["objective_generation"],
        "decision_contract_id": binding["decision_contract_id"],
        "decision_contract_version": binding["decision_contract_version"],
        "grant_id": binding["grant_id"],
        "session_id": binding["session_id"],
        "session_generation": binding["session_generation"],
        "transformation_id": binding["transformation_id"],
    }
    if any(policy[name] != value for name, value in expected_policy_values.items()):
        return _approval_result(
            case, AuthorityOutcome.UNAVAILABLE, "HUMAN_APPROVAL_SCOPE_UNAVAILABLE",
            "Approval policy does not admit the exact requested effect and context.",
        )
    if (
        binding["relationship"] != "EXACT_HUMAN_APPROVAL"
        or binding["artifact"] != case.authority_tuple.artifact
        or binding["subject_id"] != case.authority_tuple.subject
        or binding["subject_identity_basis"] != case.authority_tuple.identity_basis
        or binding["executor_id"] != case.authority_tuple.subject
        or binding["delegation_chain_id"] != chain_id
        or binding["execution_context"] != case.facts["execution_context"].value
        or binding["boundary"] != case.facts["applicable_boundary"].value
        or binding["boundary_epoch"] != case.authority_tuple.boundary_epoch
        or binding["grant_id"] != active_state.grant_id
        or binding["objective_id"] != objective.objective_id
        or binding["objective_generation"] != objective.objective_generation
        or binding["decision_contract_id"] != contract.contract_id
        or binding["decision_contract_version"] != contract.contract_version
        or binding["effect_digest"] != human_approval_effect_digest(binding)
        or binding["request_digest"] != human_approval_request_digest(binding)
    ):
        return _approval_result(
            case, AuthorityOutcome.UNAVAILABLE, "HUMAN_APPROVAL_EFFECT_UNAVAILABLE",
            "Approval is not bound to the exact canonical current execution effect.",
        )

    heads = first["approval_ordering_heads"]
    if len(heads) != 1:
        return _approval_result(
            case, AuthorityOutcome.UNAVAILABLE, "HUMAN_APPROVAL_ORDERING_UNAVAILABLE",
            "Approval authority lacks one unique all-applicable ordering head.",
        )
    head = heads[0]
    envelopes = tuple(binding["approval_envelopes"])
    envelope_ids = tuple(item["approval_id"] for item in envelopes)
    if (
        head["relationship"] != "HUMAN_APPROVAL_ORDERING_HEAD"
        or head["policy_id"] != policy["policy_id"]
        or head["policy_generation"] != policy["policy_generation"]
        or head["request_id"] != binding["request_id"]
        or head["request_generation"] != binding["request_generation"]
        or head["request_digest"] != binding["request_digest"]
        or head["effect_digest"] != binding["effect_digest"]
        or tuple(head["approval_ids"]) != envelope_ids
        or head["source_id"] != root.root_id
        or head["authority_generation"] != root.authority_generation
        or head["ordering_source_id"] != root.ordering_source_id
        or head["boundary"] != root.boundary
        or head["boundary_epoch"] != root.boundary_epoch
        or head["freshness_challenge_id"] != freshness.freshness_challenge_id
        or head["lifecycle_state"] != "ACTIVE"
        or head["head_event_order"] > observation.t3_anchor.event_order
    ):
        return _approval_result(
            case, AuthorityOutcome.UNAVAILABLE, "HUMAN_APPROVAL_ORDERING_UNAVAILABLE",
            "Approval ordering head is incomplete, stale, or not root-applicable.",
        )

    verifications = {
        (item["approval_id"], item["approval_generation"]): item
        for item in binding["approval_verifications"]
    }
    if len(verifications) != len(binding["approval_verifications"]):
        return _approval_result(
            case, AuthorityOutcome.UNAVAILABLE, "HUMAN_APPROVAL_CONFLICTING",
            "Approval verification identities conflict.",
        )

    admissions = {
        (item["approver_id"], item["approver_generation"], item["identity_basis"]): item
        for item in first["approver_admissions"]
    }
    lifecycle = {
        (item["approval_id"], item["approval_generation"]): item
        for item in first["approval_lifecycle_records"]
    }
    use_states = {
        (item["approval_id"], item["approval_generation"]): item
        for item in first["approval_use_states"]
    }
    if (
        len(admissions) != len(first["approver_admissions"])
        or len(lifecycle) != len(first["approval_lifecycle_records"])
        or len(use_states) != len(first["approval_use_states"])
    ):
        return _approval_result(
            case, AuthorityOutcome.UNAVAILABLE, "HUMAN_APPROVAL_CONFLICTING",
            "Protected approval identities or current state conflict.",
        )

    effective_domains: set[str] = set()
    for envelope in envelopes:
        record = lifecycle.get((envelope["approval_id"], envelope["approval_generation"]))
        if record is not None and record["state"] in {"REVOKED", "REJECTED", "PROHIBITED"}:
            return _approval_result(
                case, AuthorityOutcome.DENIED, "HUMAN_APPROVAL_REVOKED",
                "A current applicable human approval is revoked, rejected, or prohibited.",
            )
        admission = admissions.get((
            envelope["approver_id"], envelope["approver_generation"],
            envelope["approver_identity_basis"],
        ))
        if admission is None:
            return _approval_result(
                case, AuthorityOutcome.UNAVAILABLE, "HUMAN_APPROVER_ADMISSION_UNAVAILABLE",
                "The exact approver lacks independent protected admission.",
            )
        if (
            envelope["approval_source_id"] != admission["approval_source_id"]
            or envelope["approval_source_generation"] != admission["approval_source_generation"]
            or envelope["role"] not in admission["roles"]
            or envelope["effective_domain"] != admission["effective_domain"]
            or admission["source_id"] != root.root_id
            or admission["authority_generation"] != root.authority_generation
            or admission["boundary"] != root.boundary
            or admission["boundary_epoch"] != root.boundary_epoch
            or admission["ordering_source_id"] != root.ordering_source_id
            or admission["freshness_challenge_id"] != freshness.freshness_challenge_id
            or admission["lifecycle_state"] != "ACTIVE"
            or admission["start_event_order"] > head["head_event_order"]
            or admission["end_event_order"] < head["head_event_order"]
        ):
            return _approval_result(
                case, AuthorityOutcome.UNAVAILABLE, "HUMAN_APPROVER_ADMISSION_UNAVAILABLE",
                "Approver identity, role, source, boundary, or currentness is unavailable.",
            )
        verification = verifications.get(
            (envelope["approval_id"], envelope["approval_generation"])
        )
        envelope_digest = human_approval_envelope_digest(envelope)
        if (
            envelope["canonical_payload_digest"] != envelope_digest
            or verification is None
            or verification["relationship"] != "HUMAN_APPROVAL_VERIFICATION"
            or verification["envelope_digest"] != envelope_digest
            or verification["verifier_id"] != policy["approval_verifier_id"]
            or verification["verifier_generation"] != policy["approval_verifier_generation"]
            or verification["approval_source_id"] != admission["approval_source_id"]
            or verification["approval_source_generation"] != admission["approval_source_generation"]
            or verification["disposition"] != envelope["disposition"]
            or verification["verification_event_order"] > head["head_event_order"]
            or verification["freshness_challenge_id"] != freshness.freshness_challenge_id
            or verification["source_id"] != root.root_id
            or verification["authority_generation"] != root.authority_generation
            or verification["boundary"] != root.boundary
            or verification["boundary_epoch"] != root.boundary_epoch
            or verification["lifecycle_state"] != "ACTIVE"
        ):
            return _approval_result(
                case, AuthorityOutcome.UNAVAILABLE, "HUMAN_APPROVAL_VERIFICATION_UNAVAILABLE",
                "Approval envelope authenticity is not exactly and currently verified.",
            )
        if envelope["disposition"] in {"REJECTED", "PROHIBITED"}:
            return _approval_result(
                case, AuthorityOutcome.DENIED, "HUMAN_APPROVAL_REJECTED",
                "A current exactly verified human decision rejects or prohibits the effect.",
            )
        scalar_matches = (
            envelope["policy_id"] == binding["policy_id"]
            and envelope["policy_generation"] == binding["policy_generation"]
            and envelope["request_id"] == binding["request_id"]
            and envelope["request_generation"] == binding["request_generation"]
            and envelope["request_digest"] == binding["request_digest"]
            and envelope["effect_digest"] == binding["effect_digest"]
            and envelope["artifact"] == binding["artifact"]
            and envelope["effect"] == binding["effect"]
            and envelope["subject_id"] == binding["subject_id"]
            and envelope["executor_id"] == binding["executor_id"]
            and envelope["delegation_chain_id"] == binding["delegation_chain_id"]
            and envelope["tool_backend_id"] == binding["tool_backend_id"]
            and envelope["execution_context"] == binding["execution_context"]
            and envelope["boundary"] == binding["boundary"]
            and envelope["boundary_epoch"] == binding["boundary_epoch"]
            and envelope["session_id"] == binding["session_id"]
            and envelope["session_generation"] == binding["session_generation"]
            and envelope["freshness_challenge_id"] == freshness.freshness_challenge_id
            and envelope["disposition"] == "APPROVED"
            and envelope["lifecycle_state"] == "ACTIVE"
            and envelope["use_policy"] == policy["use_policy"]
            and envelope["maximum_uses"] == policy["maximum_uses"]
            and envelope["issuance_order"] <= head["head_event_order"]
            and envelope["expiry_order"] >= head["head_event_order"]
            and record is not None
            and record["state"] == "ACTIVE"
            and record["event_order"] <= head["head_event_order"]
            and record["source_id"] == root.root_id
            and record["authority_generation"] == root.authority_generation
        )
        if not scalar_matches:
            return _approval_result(
                case, AuthorityOutcome.UNAVAILABLE, "HUMAN_APPROVAL_CURRENTNESS_UNAVAILABLE",
                "Approval content, lifecycle, expiry, scope, or freshness is not exact and current.",
            )
        state = use_states.get((envelope["approval_id"], envelope["approval_generation"]))
        use = binding["approval_use"]
        if state is None:
            return _approval_result(
                case, AuthorityOutcome.UNAVAILABLE, "HUMAN_APPROVAL_USE_STATE_UNAVAILABLE",
                "Protected durable approval-use state is unavailable.",
            )
        if (
            state["request_id"] != binding["request_id"]
            or state["request_generation"] != binding["request_generation"]
            or state["session_id"] != binding["session_id"]
            or state["session_generation"] != binding["session_generation"]
            or state["source_id"] != root.root_id
            or state["authority_generation"] != root.authority_generation
            or state["boundary"] != root.boundary
            or state["boundary_epoch"] != root.boundary_epoch
            or state["freshness_challenge_id"] != freshness.freshness_challenge_id
            or state["lifecycle_state"] != "ACTIVE"
            or use["use_position"] != state["next_use_position"]
            or state["accepted_use_count"] >= policy["maximum_uses"]
        ):
            return _approval_result(
                case, AuthorityOutcome.UNAVAILABLE, "HUMAN_APPROVAL_REPLAY",
                "Approval is consumed, replayed, rolled back, or outside its bounded-use state.",
            )
        effective_domains.add(admission["effective_domain"])

    use = binding["approval_use"]
    if (
        use["relationship"] != "EXACT_HUMAN_APPROVAL_USE"
        or tuple(use["approval_ids"]) != envelope_ids
        or any(use[name] != binding[name] for name in (
            "request_id", "request_generation", "request_digest", "effect_digest",
            "subject_id", "executor_id", "delegation_chain_id", "tool_backend_id",
            "execution_context", "boundary", "boundary_epoch", "session_id",
            "session_generation", "grant_id",
        ))
        or use["use_event_order"] != head["head_event_order"]
        or use["freshness_challenge_id"] != freshness.freshness_challenge_id
        or len(verifications) != len(envelopes)
    ):
        return _approval_result(
            case, AuthorityOutcome.UNAVAILABLE, "HUMAN_APPROVAL_USE_UNAVAILABLE",
            "Approval use is not exact for the current execution.",
        )
    required_roles = set(policy["required_roles"])
    selected_roles = {item["role"] for item in envelopes}
    if (
        len(envelopes) != policy["required_approver_count"]
        or not required_roles.issubset(selected_roles)
        or not set(policy["required_effective_domains"]).issubset(effective_domains)
        or len(effective_domains) < policy["required_approver_count"]
    ):
        return _approval_result(
            case, AuthorityOutcome.UNAVAILABLE, "HUMAN_APPROVER_INDEPENDENCE_UNAVAILABLE",
            "Required approver roles and independent effective domains are incomplete.",
        )
    return None


def _tool_result(
    case: OracleInput, outcome: AuthorityOutcome, code: str, detail: str
) -> OracleResult:
    return OracleResult(
        outcome, (Reason(code, detail, ("tool_connector_use_binding",)),), _engaged(case)
    )


def _t3_result(case: OracleInput, code: str, detail: str) -> OracleResult:
    return _unavailable(case, code, detail, ("evidence_binding", "binding_ordering"))


def _evaluate_t3_execution_event(
    case: OracleInput,
    active_state: AuthorityStateBinding,
) -> OracleResult | None:
    """Converge all authority heads on one harness-owned terminal event."""
    if RESERVED_T3_EXECUTION_FACTS.intersection(case.facts):
        return _t3_result(case, "T3_EXECUTION_EVENT_SELF_ASSERTED", "Candidate event or cached authority outcome cannot establish T3.")
    events = tuple(item["t3_execution_event"] for item in case.trusted_anchor_context)
    if not events:
        return _t3_result(case, "T3_EXECUTION_EVENT_UNAVAILABLE", "Protected T3 execution event is unavailable.")
    event = events[0]
    if any(item != event for item in events[1:]):
        return _t3_result(case, "T3_EXECUTION_EVENT_CONFLICTING", "Protected anchor views select conflicting terminal events.")
    observation = case.observation_binding
    freshness = case.observation_freshness
    root = case.t3_binding_facts.authority_root
    objective = case.t3_binding_facts.objective_identity
    contract = case.t3_binding_facts.decision_contract_identity
    if None in (observation, freshness, root, objective, contract):
        return _t3_result(case, "T3_AUTHORITY_CONVERGENCE_UNAVAILABLE", "Terminal event cannot join current protected authority heads.")
    assert observation is not None and freshness is not None and root is not None
    assert objective is not None and contract is not None
    if event["execution_event_digest"] != t3_execution_event_digest(event):
        return _t3_result(case, "T3_EXECUTION_EVENT_DIGEST_UNAVAILABLE", "Terminal event digest is not canonical.")

    approval = case.trusted_anchor_context[0]["human_approval_authority_context"]
    delegation = case.trusted_anchor_context[0]["delegation_authority_context"]
    tool = case.trusted_anchor_context[0]["tool_connector_authority_context"]
    approval_policy = approval["approval_policy"]
    delegation_policy = delegation["delegation_policy"]
    tool_policy = tool["tool_connector_policy"]
    policy_set = {
        "approval": [approval_policy["policy_id"], approval_policy["policy_generation"]],
        "delegation": [delegation_policy["policy_id"], delegation_policy["policy_generation"]],
        "tool": [tool_policy["policy_id"], tool_policy["policy_generation"]],
        "control_plane": [
            case.trusted_anchor_context[0]["control_plane_policy"]["policy_id"],
            case.trusted_anchor_context[0]["control_plane_policy"]["policy_generation"],
        ],
        "required_domains": [
            case.trusted_anchor_context[0]["required_domain_policy"]["policy_id"],
            case.trusted_anchor_context[0]["required_domain_policy"]["policy_generation"],
        ],
    }
    policy_digest = _canonical_digest("authority-lab-v1/t3-policy-set", policy_set)
    tool_records = tuple(tool["execution_contexts"])
    tool_uses = tuple(tool["protected_terminal_uses"])
    tool_context = tool_records[0] if len(tool_records) == 1 else None
    tool_use = tool_uses[0] if len(tool_uses) == 1 else None
    delegation_uses = tuple(delegation["delegation_terminal_uses"])
    delegation_use = delegation_uses[0] if len(delegation_uses) == 1 else None
    approval_binding = case.human_approval_binding
    approval_use = approval_binding["approval_use"] if approval_binding is not None else None
    anchor_set = sorted(
        ({
            "verifier_id": item["verifier_id"],
            "verifier_generation": item["verifier_generation"],
            "verifier_state_digest": item["verifier_state_digest"],
            "anchor_id": item["anchor_id"],
            "anchor_generation": item["anchor_generation"],
            "anchor_position": item["anchor_position"],
            "anchor_digest": item["anchor_digest"],
        } for item in case.trusted_anchor_context),
        key=lambda item: (item["anchor_id"], item["anchor_generation"]),
    )
    anchor_set_digest = _canonical_digest("authority-lab-v1/t3-anchor-set", {"anchors": anchor_set})
    chain_id = delegation_use["chain_id"] if delegation_use is not None else "DIRECT"
    expected = {
        "relationship": "T3_EXECUTION_EVENT",
        "event_order": observation.t3_anchor.event_order,
        "t3_anchor_id": observation.t3_anchor.anchor_id,
        "subject_id": case.authority_tuple.subject,
        "subject_identity_basis": case.authority_tuple.identity_basis,
        "executor_id": tool_policy["executor_id"],
        "artifact": case.authority_tuple.artifact,
        "effect": tool_policy["effect"],
        "boundary": root.boundary,
        "boundary_epoch": root.boundary_epoch,
        "execution_context": case.facts["execution_context"].value,
        "objective_id": objective.objective_id,
        "objective_generation": objective.objective_generation,
        "decision_contract_id": contract.contract_id,
        "decision_contract_version": contract.contract_version,
        "delegation_chain_id": chain_id,
        "delegation_use_id": (
            f"DELEGATION-USE-{chain_id}" if delegation_use is not None else "NONE"
        ),
        "approval_policy_id": approval_policy["policy_id"] if approval_policy["requirement"] == "REQUIRED" else "NONE",
        "approval_use_id": approval_use["use_id"] if approval_use is not None else "NONE",
        "tool_context_id": tool_context["context_id"] if tool_context is not None else "NONE",
        "tool_context_generation": tool_context["context_generation"] if tool_context is not None else 0,
        "tool_context_digest": tool_context["context_digest"] if tool_context is not None else "NONE",
        "tool_use_id": tool_use["use_id"] if tool_use is not None else "NONE",
        "grant_id": active_state.grant_id,
        "consumption_state": case.facts["consumption_state"].value,
        "terminal_use_id": tool_use["use_id"] if tool_use is not None else active_state.grant_id,
        "verifier_id": "T3-VERIFIER-SET",
        "verifier_generation": max(item["verifier_generation"] for item in anchor_set),
        "verifier_state_digest": anchor_set_digest,
        "anchor_id": "T3-ANCHOR-SET",
        "anchor_generation": max(item["anchor_generation"] for item in anchor_set),
        "anchor_position": max(item["anchor_position"] for item in anchor_set),
        "anchor_digest": anchor_set_digest,
        "policy_set_digest": policy_digest,
        "source_id": root.root_id,
        "authority_generation": root.authority_generation,
        "lineage": root.lineage,
        "ordering_source_id": root.ordering_source_id,
        "freshness_challenge_id": freshness.freshness_challenge_id,
        "lifecycle_state": "ACTIVE",
    }
    if any(not exact_value_equal(event[name], value) for name, value in expected.items()):
        return _t3_result(case, "T3_AUTHORITY_CONVERGENCE_UNAVAILABLE", "Protected authority heads do not converge on the exact canonical terminal event.")
    t3 = event["event_order"]
    if freshness.head_event_order != t3:
        return _t3_result(case, "T3_AUTHORITY_CONVERGENCE_UNAVAILABLE", "Observation freshness does not select canonical T3.")
    if tool_use is not None and tool_use["use_event_order"] != t3:
        return _t3_result(case, "T3_AUTHORITY_CONVERGENCE_UNAVAILABLE", "Tool use references a different terminal event.")
    if delegation_use is not None and delegation_use["use_event_order"] != t3:
        return _t3_result(case, "T3_AUTHORITY_CONVERGENCE_UNAVAILABLE", "Delegation use does not cover canonical T3.")
    if approval_use is not None and approval_use["use_event_order"] != t3:
        return _t3_result(case, "T3_AUTHORITY_CONVERGENCE_UNAVAILABLE", "Approval use does not cover canonical T3.")
    return None


def _evaluate_tool_connector_authority(
    case: OracleInput,
    active_state: AuthorityStateBinding,
    protected_terminal_grant: Mapping[str, Any] | None,
) -> OracleResult | None:
    """Join exact T3 use to independently protected effect-capable target state."""
    contexts = tuple(
        item["tool_connector_authority_context"]
        for item in case.trusted_anchor_context
    )
    if not contexts:
        return _tool_result(case, AuthorityOutcome.UNAVAILABLE, "TOOL_CONNECTOR_POLICY_UNAVAILABLE", "Protected tool/connector policy is unavailable.")
    first = contexts[0]
    if any(item != first for item in contexts[1:]):
        return _tool_result(case, AuthorityOutcome.UNAVAILABLE, "TOOL_CONNECTOR_CONTEXT_CONFLICTING", "Protected tool/connector contexts conflict.")
    policy = first["tool_connector_policy"]
    root = case.t3_binding_facts.authority_root
    objective = case.t3_binding_facts.objective_identity
    contract = case.t3_binding_facts.decision_contract_identity
    freshness = case.observation_freshness
    observation = case.observation_binding
    if root is None or objective is None or contract is None or freshness is None or observation is None:
        return _tool_result(case, AuthorityOutcome.UNAVAILABLE, "TOOL_CONNECTOR_POLICY_UNAVAILABLE", "Tool policy cannot join current authority and observation state.")
    if (
        policy["relationship"] != "TOOL_CONNECTOR_POLICY"
        or policy["selection_rule"] != "ALL_APPLICABLE"
        or policy["source_id"] != root.root_id
        or policy["authority_generation"] != root.authority_generation
        or policy["lineage"] != root.lineage
        or policy["ordering_source_id"] != root.ordering_source_id
        or policy["boundary"] != root.boundary
        or policy["boundary_epoch"] != root.boundary_epoch
        or policy["objective_id"] != objective.objective_id
        or policy["objective_generation"] != objective.objective_generation
        or policy["decision_contract_id"] != contract.contract_id
        or policy["decision_contract_version"] != contract.contract_version
        or policy["freshness_challenge_id"] != freshness.freshness_challenge_id
    ):
        return _tool_result(case, AuthorityOutcome.UNAVAILABLE, "TOOL_CONNECTOR_POLICY_UNAVAILABLE", "Tool policy is not exact, current, root-issued, and applicable.")
    if policy["lifecycle_state"] in {"REVOKED", "REJECTED", "PROHIBITED"}:
        return _tool_result(case, AuthorityOutcome.DENIED, "TOOL_CONNECTOR_PROHIBITED", "The current tool/connector policy is revoked or prohibited.")
    if policy["lifecycle_state"] != "ACTIVE":
        return _tool_result(case, AuthorityOutcome.UNAVAILABLE, "TOOL_CONNECTOR_POLICY_UNAVAILABLE", "Tool policy lifecycle is unavailable.")

    if RESERVED_TOOL_CONNECTOR_FACTS.intersection(case.facts):
        return _tool_result(case, AuthorityOutcome.UNAVAILABLE, "TOOL_CONNECTOR_SELF_ASSERTED", "Candidate tool, backend, credential, or permission facts cannot establish protected execution-target authority.")
    candidate = case.tool_connector_use_binding
    if policy["requirement"] == "NONE":
        if candidate is not None:
            return _tool_result(case, AuthorityOutcome.UNAVAILABLE, "TOOL_CONNECTOR_POLICY_CONFLICTING", "Candidate tool use conflicts with the selected no-tool policy.")
        return None
    if policy["requirement"] != "REQUIRED" or candidate is None:
        return _tool_result(case, AuthorityOutcome.UNAVAILABLE, "TOOL_CONNECTOR_USE_UNAVAILABLE", "The selected policy requires one exact current tool/connector use.")

    records = tuple(first["execution_contexts"])
    selections = tuple(first["execution_target_selection"])
    uses = tuple(first["protected_terminal_uses"])
    if len(records) != 1 or len(selections) != 1 or len(uses) != 1:
        return _tool_result(case, AuthorityOutcome.UNAVAILABLE, "TOOL_CONNECTOR_SELECTION_UNAVAILABLE", "All-applicable selection lacks one unique context, head, and use.")
    current, selection, protected_use = records[0], selections[0], uses[0]
    prohibited = {"REVOKED", "REJECTED", "PROHIBITED"}
    if current["lifecycle_state"] in prohibited or protected_use["lifecycle_state"] in prohibited:
        return _tool_result(case, AuthorityOutcome.DENIED, "TOOL_CONNECTOR_REVOKED", "The current execution target, credential, permission, or use is prohibited.")
    digest = tool_connector_context_digest(current)
    if current["context_digest"] != digest:
        return _tool_result(case, AuthorityOutcome.UNAVAILABLE, "TOOL_CONNECTOR_CONTEXT_DIGEST_UNAVAILABLE", "Protected execution-target context digest is not canonical.")
    exact_current = (
        current["relationship"] == "TOOL_CONNECTOR_EXECUTION_CONTEXT"
        and current["source_id"] == root.root_id
        and current["authority_generation"] == root.authority_generation
        and current["lineage"] == root.lineage
        and current["ordering_source_id"] == root.ordering_source_id
        and current["freshness_challenge_id"] == freshness.freshness_challenge_id
        and current["boundary"] == root.boundary
        and current["boundary_epoch"] == root.boundary_epoch
        and current["execution_context"] == case.facts["execution_context"].value
        and current["subject_id"] == case.authority_tuple.subject
        and current["artifact"] == case.authority_tuple.artifact
        and current["objective_id"] == objective.objective_id
        and current["objective_generation"] == objective.objective_generation
        and current["decision_contract_id"] == contract.contract_id
        and current["decision_contract_version"] == contract.contract_version
        and current["grant_id"] == active_state.grant_id
        and current["effect"] in current["permissions"]
        and current["start_event_order"] <= selection["head_event_order"] <= current["end_event_order"]
        and current["lifecycle_state"] == "ACTIVE"
        and current["operator_id"] not in {case.authority_tuple.subject, current["executor_id"]}
    )
    if not exact_current:
        return _tool_result(case, AuthorityOutcome.UNAVAILABLE, "TOOL_CONNECTOR_CURRENTNESS_UNAVAILABLE", "Execution-target identity, permissions, source lineage, boundary, or currentness is unavailable.")
    if (
        selection["relationship"] != "TOOL_CONNECTOR_SELECTION_HEAD"
        or selection["policy_id"] != policy["policy_id"]
        or selection["policy_generation"] != policy["policy_generation"]
        or selection["context_id"] != current["context_id"]
        or selection["context_generation"] != current["context_generation"]
        or selection["context_digest"] != digest
        or selection["source_id"] != root.root_id
        or selection["authority_generation"] != root.authority_generation
        or selection["lineage"] != root.lineage
        or selection["ordering_source_id"] != root.ordering_source_id
        or selection["boundary"] != root.boundary
        or selection["boundary_epoch"] != root.boundary_epoch
        or selection["freshness_challenge_id"] != freshness.freshness_challenge_id
        or selection["lifecycle_state"] != "ACTIVE"
        or selection["head_event_order"] > observation.t3_anchor.event_order
    ):
        return _tool_result(case, AuthorityOutcome.UNAVAILABLE, "TOOL_CONNECTOR_SELECTION_UNAVAILABLE", "The root-selected execution target is stale, conflicting, or unavailable.")

    transitions = tuple(first["component_transitions"])
    if current["context_generation"] > 1:
        applicable = tuple(item for item in transitions if item["new_context_id"] == current["context_id"] and item["new_context_generation"] == current["context_generation"])
        if len(applicable) != 1:
            return _tool_result(case, AuthorityOutcome.UNAVAILABLE, "TOOL_CONNECTOR_TRANSITION_UNAVAILABLE", "Successor target lacks one exact authorized transition.")
        transition = applicable[0]
        valid_transition_classes = {
            "TOOL": {"ROTATION"},
            "CONNECTOR": {"HANDOFF"},
            "BACKEND": {"MIGRATION"},
            "CREDENTIAL": {"ROTATION"},
            "PERMISSION": {"NARROWING", "EXPANSION"},
        }
        old_permissions = frozenset(transition["old_permissions"])
        new_permissions = frozenset(transition["new_permissions"])
        permission_transition_valid = (
            new_permissions == frozenset(current["permissions"])
            and (
                transition["transition_class"] == "NARROWING"
                and new_permissions < old_permissions
                or transition["transition_class"] == "EXPANSION"
                and old_permissions < new_permissions
                or transition["component_kind"] != "PERMISSION"
                and old_permissions == new_permissions
            )
        )
        if (
            transition["relationship"] != "TOOL_COMPONENT_TRANSITION"
            or transition["transition_class"] not in valid_transition_classes.get(
                transition["component_kind"], set()
            )
            or transition["old_context_id"] == transition["new_context_id"]
            or transition["old_context_generation"] + 1 != transition["new_context_generation"]
            or transition["old_context_digest"] == transition["new_context_digest"]
            or transition["new_context_digest"] != digest
            or not permission_transition_valid
            or transition["source_id"] != root.root_id
            or transition["authority_generation"] != root.authority_generation
            or transition["lineage"] != root.lineage
            or transition["ordering_source_id"] != root.ordering_source_id
            or transition["boundary"] != root.boundary
            or transition["boundary_epoch"] != root.boundary_epoch
            or transition["freshness_challenge_id"] != freshness.freshness_challenge_id
            or transition["lifecycle_state"] != "ACTIVE"
            or transition["event_order"] < current["start_event_order"]
            or transition["event_order"] > selection["head_event_order"]
        ):
            return _tool_result(case, AuthorityOutcome.UNAVAILABLE, "TOOL_CONNECTOR_TRANSITION_UNAVAILABLE", "Tool rotation, connector handoff, backend migration, credential rotation, or permission transition is not authorized.")
        if transition["approval_revalidation"] == "REQUIRED" and (
            case.human_approval_binding is None
            or any(
                envelope["issuance_order"] < transition["event_order"]
                for envelope in case.human_approval_binding["approval_envelopes"]
            )
        ):
            return _tool_result(case, AuthorityOutcome.UNAVAILABLE, "TOOL_CONNECTOR_APPROVAL_REVALIDATION_UNAVAILABLE", "The authorized component transition requires fresh human reapproval.")
        if transition["delegation_revalidation"] == "REQUIRED" and (
            protected_terminal_grant is None
            or protected_terminal_grant["created_event_order"] < transition["event_order"]
        ):
            return _tool_result(case, AuthorityOutcome.UNAVAILABLE, "TOOL_CONNECTOR_DELEGATION_REVALIDATION_UNAVAILABLE", "The authorized component transition requires a fresh delegation regrant.")
    elif transitions:
        return _tool_result(case, AuthorityOutcome.UNAVAILABLE, "TOOL_CONNECTOR_TRANSITION_CONFLICTING", "Unselected transition state cannot create target authority.")

    approval_id = (
        case.human_approval_binding["policy_id"]
        if case.human_approval_binding is not None else "NONE"
    )
    chain_id = protected_terminal_grant["chain_id"] if protected_terminal_grant is not None else "DIRECT"
    if case.human_approval_binding is not None and (
        case.human_approval_binding["tool_backend_id"] != current["backend_id"]
        or case.human_approval_binding["credential_generation"] != current["credential_generation"]
    ):
        return _tool_result(case, AuthorityOutcome.UNAVAILABLE, "TOOL_CONNECTOR_APPROVAL_MISMATCH", "Human approval does not bind the actual protected backend and credential generation.")
    if protected_terminal_grant is not None and current["logical_tool_id"] not in protected_terminal_grant["action_scope"]["tools"]:
        return _tool_result(case, AuthorityOutcome.UNAVAILABLE, "TOOL_CONNECTOR_DELEGATION_MISMATCH", "Delegation does not admit the actual protected logical tool.")

    expected = {
        "policy_id": policy["policy_id"], "policy_generation": policy["policy_generation"],
        "context_id": current["context_id"], "context_generation": current["context_generation"],
        "context_digest": digest, "logical_tool_id": current["logical_tool_id"],
        "tool_generation": current["tool_generation"], "connector_id": current["connector_id"],
        "connector_generation": current["connector_generation"], "backend_id": current["backend_id"],
        "backend_generation": current["backend_generation"], "target_id": current["target_id"],
        "target_generation": current["target_generation"], "credential_id": current["credential_id"],
        "credential_generation": current["credential_generation"], "permission_scope_id": current["permission_scope_id"],
        "permission_scope_generation": current["permission_scope_generation"],
        "permissions": tuple(current["permissions"]), "operator_lineage": current["operator_lineage"],
        "subject_id": current["subject_id"], "executor_id": current["executor_id"],
        "artifact": current["artifact"], "effect": current["effect"],
        "delegation_chain_id": chain_id, "approval_policy_id": approval_id,
        "boundary": current["boundary"], "boundary_epoch": current["boundary_epoch"],
        "execution_context": current["execution_context"], "objective_id": current["objective_id"],
        "objective_generation": current["objective_generation"],
        "decision_contract_id": current["decision_contract_id"],
        "decision_contract_version": current["decision_contract_version"],
        "grant_id": current["grant_id"], "freshness_challenge_id": freshness.freshness_challenge_id,
    }
    if candidate["relationship"] != "EXACT_TOOL_CONNECTOR_USE" or any(candidate[name] != value for name, value in expected.items()):
        return _tool_result(case, AuthorityOutcome.UNAVAILABLE, "TOOL_CONNECTOR_USE_UNAVAILABLE", "Candidate use is not bound to the exact protected execution target.")
    if (
        protected_use["relationship"] != "TOOL_CONNECTOR_TERMINAL_USE"
        or any(protected_use[name] != value for name, value in {
            "context_id": current["context_id"], "context_generation": current["context_generation"],
            "context_digest": digest, "subject_id": current["subject_id"],
            "executor_id": current["executor_id"], "artifact": current["artifact"],
            "effect": current["effect"], "delegation_chain_id": chain_id,
            "approval_policy_id": approval_id, "grant_id": current["grant_id"],
            "boundary": current["boundary"], "boundary_epoch": current["boundary_epoch"],
            "execution_context": current["execution_context"],
        }.items())
        or protected_use["use_id"] != candidate["use_id"]
        or protected_use["use_event_order"] != candidate["use_event_order"]
        or protected_use["use_event_order"] != selection["head_event_order"]
        or protected_use["source_id"] != root.root_id
        or protected_use["authority_generation"] != root.authority_generation
        or protected_use["freshness_challenge_id"] != freshness.freshness_challenge_id
        or protected_use["lifecycle_state"] != "ACTIVE"
    ):
        return _tool_result(case, AuthorityOutcome.UNAVAILABLE, "TOOL_CONNECTOR_USE_UNAVAILABLE", "Protected terminal use is stale, incomplete, or mismatched.")
    return None


def _evaluate_recovery_and_rotation(
    case: OracleInput,
    binding: ObservationBinding,
    root: Any,
    anchor: Mapping[str, Any],
    trusted: Mapping[str, Any],
) -> OracleResult | None:
    recoveries = [item.values for item in binding.recovery_installations]
    if trusted.get("recovery_required", False):
        if len(recoveries) != 1:
            return _observation_unavailable(case, "VERIFIER_STATE_RECOVERY_UNAVAILABLE", "Recovery lacks one exact installation relation.", ("evidence_binding",))
        recovery = recoveries[0]
        ordered = tuple(range(recovery["replay_start_position"], recovery["replay_end_position"] + 1))
        if (
            recovery["relationship"] != "VERIFIER_STATE_RECOVERY_INSTALLATION"
            or recovery["source_anchor_digest"] != trusted.get("recovery_source_anchor_digest")
            or recovery["final_head_commitment_digest"] != anchor["head_commitment_digest"]
            or recovery["final_verifier_state_digest"] != anchor["verifier_state_digest"]
            or recovery["target_verifier_id"] != anchor["verifier_id"]
            or recovery["target_verifier_generation"] != anchor["verifier_generation"]
            or recovery["target_durable_state_id"] != anchor["durable_state_id"]
            or recovery["target_durable_state_generation"] != anchor["durable_state_generation"]
            or len(recovery["replay_commitment_ids"]) != len(ordered)
            or len(recovery["replay_commitment_digests"]) != len(ordered)
            or recovery["installation_receipt_digest"] != trusted.get("installation_receipt_digest")
            or recovery_receipt_digest(recovery) != recovery["installation_receipt_digest"]
            or recovery["recovery_authority_id"] in {
                case.authority_tuple.subject,
                anchor["verifier_id"],
                anchor["anchor_source_id"],
                root.root_id,
                root.ordering_source_id,
            }
            or recovery["source_id"] != root.root_id
            or recovery["authority_generation"] != root.authority_generation
            or recovery["boundary"] != root.boundary
            or recovery["boundary_epoch"] != root.boundary_epoch
            or recovery["lineage"] != root.lineage
            or recovery["ordering_source_id"] != root.ordering_source_id
            or recovery["lifecycle_state"] != "ACTIVE"
        ):
            return _observation_unavailable(case, "VERIFIER_STATE_RECOVERY_INCOMPLETE", "Recovery replay or installation is incomplete, reordered, or circular.", ("evidence_binding", "binding_ordering"))
    elif recoveries:
        return _observation_unavailable(case, "VERIFIER_STATE_RECOVERY_UNAVAILABLE", "Candidate recovery data is not selected by independently current anchor state.", ("evidence_binding",))

    if trusted.get("verifier_rotation_required", False):
        rotations = [item.values for item in binding.verifier_rotations]
        if len(rotations) != 1 or rotations[0]["new_verifier_id"] != anchor["verifier_id"] or rotations[0]["new_verifier_generation"] != anchor["verifier_generation"] or rotations[0]["source_anchor_digest"] != trusted.get("rotation_source_anchor_digest") or rotations[0]["source_id"] != root.root_id or rotations[0]["lifecycle_state"] != "ACTIVE":
            return _observation_unavailable(case, "VERIFIER_ROTATION_UNAVAILABLE", "Verifier replacement lacks exact current rotation authority.", ("evidence_binding",))
    if trusted.get("anchor_rotation_required", False):
        rotations = [item.values for item in binding.anchor_rotations]
        if len(rotations) != 1 or rotations[0]["new_anchor_source_id"] != anchor["anchor_source_id"] or rotations[0]["new_anchor_generation"] != anchor["anchor_source_generation"] or rotations[0]["new_anchor_digest"] != anchor["anchor_digest"] or rotations[0]["source_id"] != root.root_id or rotations[0]["lifecycle_state"] != "ACTIVE":
            return _observation_unavailable(case, "ANCHOR_ROTATION_UNAVAILABLE", "Anchor replacement lacks exact old-to-new continuity.", ("evidence_binding",))

    witness_sources = [item.values for item in binding.witness_source_admissions]
    required_domains = trusted.get("required_witness_domains", 0)
    if required_domains:
        valid = [item for item in witness_sources if item["anchor_digest"] == anchor["anchor_digest"] and item["head_commitment_digest"] == anchor["head_commitment_digest"] and item["source_id"] == root.root_id and item["lifecycle_state"] == "ACTIVE"]
        domains = {item["control_domain"] for item in valid}
        source_lineages = {(item["witness_source_id"], item["source_lineage"], item["control_domain"]) for item in valid}
        if len(domains) < required_domains or len(source_lineages) < required_domains:
            return _observation_unavailable(case, "WITNESS_SOURCE_CONTINUITY_UNAVAILABLE", "Witness multiplicity does not establish required independent source continuity.", ("evidence_binding",))
        if trusted.get("witness_conflict", False):
            return _observation_unavailable(case, "OBSERVATION_WITNESS_CONFLICTING", "Admitted witness sources conflict about the selected anchor.", ("evidence_binding",))
    return None


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

    # Establish the admitted observation history before relying on any authority
    # relationship derived from that history.  This also keeps an unavailable
    # commitment/anchor diagnostic from being masked by a later protected join.
    observation_result = _evaluate_observation(case)
    if observation_result.outcome is not AuthorityOutcome.AUTHORIZED:
        return observation_result

    t3_result = _evaluate_t3_execution_event(case, active_state)
    if t3_result is not None:
        return t3_result

    phi_result = evaluate_phi_disclosure(case)
    if phi_result is not None and phi_result.outcome is not AuthorityOutcome.AUTHORIZED:
        return OracleResult(
            phi_result.outcome,
            (Reason(phi_result.code, phi_result.detail, phi_result.facts),),
            _engaged(case),
        )

    delegation_result, protected_terminal_grant = _evaluate_delegation_authority(
        case, active_state
    )
    if delegation_result is not None:
        return delegation_result
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
        if protected_terminal_grant is None:
            return _unavailable(
                case,
                "DELEGATION_SOURCE_AUTHORITY_UNAVAILABLE",
                "Protected terminal delegation authority is unavailable.",
                ("delegation_binding",),
            )
        delegation_expected = {
            "relationship": "EXACT_DELEGATION",
            "delegator": protected_terminal_grant["delegator_id"],
            "delegate": protected_terminal_grant["delegate_id"],
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

    approval_result = _evaluate_human_approval(
        case, active_state, protected_terminal_grant
    )
    if approval_result is not None:
        return approval_result

    tool_result = _evaluate_tool_connector_authority(
        case, active_state, protected_terminal_grant
    )
    if tool_result is not None:
        return tool_result

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
