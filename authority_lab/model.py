"""Bounded public data model for Authority Lab v1."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping


class AuthorityOutcome(str, Enum):
    AUTHORIZED = "AUTHORIZED"
    DENIED = "DENIED"
    UNAVAILABLE = "UNAVAILABLE"


class FactState(str, Enum):
    KNOWN = "KNOWN"
    UNKNOWN = "UNKNOWN"
    CONFLICTING = "CONFLICTING"


class HarnessStatus(str, Enum):
    PASS = "PASS"
    CASE_MISMATCH = "CASE_MISMATCH"


INVARIANTS = (
    "INV-CONT",
    "INV-DISC",
    "INV-BND",
    "INV-EVD",
    "INV-USE",
    "INV-CLO",
)

TUPLE_FIELDS = (
    "subject",
    "artifact",
    "control_state",
    "identity_basis",
    "boundary_epoch",
    "decision",
)

MANDATORY_T3_FACTS = (
    "subject_identity",
    "artifact_identity",
    "control_state",
    "identity_basis",
    "boundary_epoch",
    "decision_binding",
    "applicable_boundary",
    "evidence_binding",
    "execution_context",
    "freshness",
    "consumption_state",
    "boundary_epoch_binding",
    "execution_control_binding",
    "consumption_binding",
    "delegation_binding",
    "closure_binding",
    "objective_identity",
    "decision_contract_identity",
    "authority_root",
    "objective_binding",
    "binding_source_authority",
    "binding_lifecycle",
    "binding_ordering",
)

RELATIONAL_T3_FACTS = (
    "boundary_epoch_binding",
    "execution_control_binding",
    "consumption_binding",
    "delegation_binding",
    "closure_binding",
    "objective_identity",
    "decision_contract_identity",
    "authority_root",
    "objective_binding",
    "binding_source_authority",
    "binding_lifecycle",
    "binding_ordering",
)

OBJECTIVE_BINDING_FACTS = (
    "objective_identity",
    "decision_contract_identity",
    "authority_root",
    "objective_binding",
    "binding_source_authority",
    "binding_lifecycle",
    "binding_ordering",
)


def _exact_string(value: Any, field: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field} must be a string")
    return value


def _exact_nonempty_string(value: Any, field: str) -> str:
    value = _exact_string(value, field)
    if value == "":
        raise ValueError(f"{field} must be non-empty")
    return value


def _exact_generation(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{field} must be a non-negative integer")
    return value


def _require_exact_fields(value: Mapping[str, Any], fields: set[str], field: str) -> None:
    if set(value) != fields:
        raise ValueError(f"{field} must contain exactly {sorted(fields)}")


@dataclass(frozen=True)
class AuthorityTuple:
    subject: str
    artifact: str
    control_state: str
    identity_basis: str
    boundary_epoch: str
    decision: AuthorityOutcome

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "AuthorityTuple":
        if set(value) != set(TUPLE_FIELDS):
            raise ValueError("authority_tuple must contain exactly the six public fields")
        return cls(
            subject=_exact_string(value["subject"], "authority_tuple.subject"),
            artifact=_exact_string(value["artifact"], "authority_tuple.artifact"),
            control_state=_exact_string(value["control_state"], "authority_tuple.control_state"),
            identity_basis=_exact_string(value["identity_basis"], "authority_tuple.identity_basis"),
            boundary_epoch=_exact_string(value["boundary_epoch"], "authority_tuple.boundary_epoch"),
            decision=AuthorityOutcome(value["decision"]),
        )


@dataclass(frozen=True)
class BindingScope:
    subject: str
    artifact: str
    control_state: str
    identity_basis: str
    boundary_epoch: str
    decision: AuthorityOutcome
    applicable_boundary: str

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "BindingScope":
        fields = set(TUPLE_FIELDS) | {"applicable_boundary"}
        _require_exact_fields(value, fields, "binding scope")
        return cls(
            subject=_exact_nonempty_string(value["subject"], "binding scope.subject"),
            artifact=_exact_nonempty_string(value["artifact"], "binding scope.artifact"),
            control_state=_exact_nonempty_string(
                value["control_state"], "binding scope.control_state"
            ),
            identity_basis=_exact_nonempty_string(
                value["identity_basis"], "binding scope.identity_basis"
            ),
            boundary_epoch=_exact_nonempty_string(
                value["boundary_epoch"], "binding scope.boundary_epoch"
            ),
            decision=AuthorityOutcome(value["decision"]),
            applicable_boundary=_exact_nonempty_string(
                value["applicable_boundary"], "binding scope.applicable_boundary"
            ),
        )


@dataclass(frozen=True)
class ObjectiveIdentity:
    objective_id: str
    objective_generation: int
    policy_id: str
    policy_version: str

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "ObjectiveIdentity":
        fields = {"objective_id", "objective_generation", "policy_id", "policy_version"}
        _require_exact_fields(value, fields, "objective_identity")
        return cls(
            objective_id=_exact_nonempty_string(
                value["objective_id"], "objective_identity.objective_id"
            ),
            objective_generation=_exact_generation(
                value["objective_generation"], "objective_identity.objective_generation"
            ),
            policy_id=_exact_nonempty_string(
                value["policy_id"], "objective_identity.policy_id"
            ),
            policy_version=_exact_nonempty_string(
                value["policy_version"], "objective_identity.policy_version"
            ),
        )


@dataclass(frozen=True)
class DecisionContractIdentity:
    contract_id: str
    contract_version: str
    schema_id: str
    derived_from: str

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "DecisionContractIdentity":
        fields = {"contract_id", "contract_version", "schema_id", "derived_from"}
        _require_exact_fields(value, fields, "decision_contract_identity")
        return cls(
            contract_id=_exact_nonempty_string(
                value["contract_id"], "decision_contract_identity.contract_id"
            ),
            contract_version=_exact_nonempty_string(
                value["contract_version"], "decision_contract_identity.contract_version"
            ),
            schema_id=_exact_nonempty_string(
                value["schema_id"], "decision_contract_identity.schema_id"
            ),
            derived_from=_exact_nonempty_string(
                value["derived_from"], "decision_contract_identity.derived_from"
            ),
        )


@dataclass(frozen=True)
class AuthorityRoot:
    root_id: str
    boundary: str
    boundary_epoch: str
    lineage: str
    authority_generation: int
    ordering_source_id: str

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "AuthorityRoot":
        fields = {
            "root_id",
            "boundary",
            "boundary_epoch",
            "lineage",
            "authority_generation",
            "ordering_source_id",
        }
        _require_exact_fields(value, fields, "authority_root")
        return cls(
            root_id=_exact_nonempty_string(value["root_id"], "authority_root.root_id"),
            boundary=_exact_nonempty_string(value["boundary"], "authority_root.boundary"),
            boundary_epoch=_exact_nonempty_string(
                value["boundary_epoch"], "authority_root.boundary_epoch"
            ),
            lineage=_exact_nonempty_string(value["lineage"], "authority_root.lineage"),
            authority_generation=_exact_generation(
                value["authority_generation"], "authority_root.authority_generation"
            ),
            ordering_source_id=_exact_nonempty_string(
                value["ordering_source_id"], "authority_root.ordering_source_id"
            ),
        )


@dataclass(frozen=True)
class ObjectiveBinding:
    binding_id: str
    disposition: str
    objective_id: str
    objective_generation: int
    contract_id: str
    contract_version: str
    schema_id: str
    source_id: str
    authority_generation: int
    binding_generation: int
    lineage: str
    policy_id: str
    policy_version: str
    producer_kind: str
    producer_id: str
    scope: BindingScope

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "ObjectiveBinding":
        fields = {
            "binding_id",
            "disposition",
            "objective_id",
            "objective_generation",
            "contract_id",
            "contract_version",
            "schema_id",
            "source_id",
            "authority_generation",
            "binding_generation",
            "lineage",
            "policy_id",
            "policy_version",
            "producer_kind",
            "producer_id",
            "scope",
        }
        _require_exact_fields(value, fields, "objective_binding candidate")
        disposition = _exact_nonempty_string(
            value["disposition"], "objective_binding.disposition"
        )
        if disposition not in {"ADMIT", "REJECT"}:
            raise ValueError("objective_binding.disposition must be ADMIT or REJECT")
        scope = value["scope"]
        if not isinstance(scope, Mapping):
            raise ValueError("objective_binding.scope must be an object")
        return cls(
            binding_id=_exact_nonempty_string(
                value["binding_id"], "objective_binding.binding_id"
            ),
            disposition=disposition,
            objective_id=_exact_nonempty_string(
                value["objective_id"], "objective_binding.objective_id"
            ),
            objective_generation=_exact_generation(
                value["objective_generation"], "objective_binding.objective_generation"
            ),
            contract_id=_exact_nonempty_string(
                value["contract_id"], "objective_binding.contract_id"
            ),
            contract_version=_exact_nonempty_string(
                value["contract_version"], "objective_binding.contract_version"
            ),
            schema_id=_exact_nonempty_string(
                value["schema_id"], "objective_binding.schema_id"
            ),
            source_id=_exact_nonempty_string(
                value["source_id"], "objective_binding.source_id"
            ),
            authority_generation=_exact_generation(
                value["authority_generation"], "objective_binding.authority_generation"
            ),
            binding_generation=_exact_generation(
                value["binding_generation"], "objective_binding.binding_generation"
            ),
            lineage=_exact_nonempty_string(
                value["lineage"], "objective_binding.lineage"
            ),
            policy_id=_exact_nonempty_string(
                value["policy_id"], "objective_binding.policy_id"
            ),
            policy_version=_exact_nonempty_string(
                value["policy_version"], "objective_binding.policy_version"
            ),
            producer_kind=_exact_nonempty_string(
                value["producer_kind"], "objective_binding.producer_kind"
            ),
            producer_id=_exact_nonempty_string(
                value["producer_id"], "objective_binding.producer_id"
            ),
            scope=BindingScope.from_mapping(scope),
        )


@dataclass(frozen=True)
class BindingSourceAuthority:
    relationship: str
    root_id: str
    source_id: str
    delegation_id: str
    authority_generation: int
    boundary: str
    boundary_epoch: str
    lineage: str
    status: str
    scope: BindingScope

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "BindingSourceAuthority":
        fields = {
            "relationship",
            "root_id",
            "source_id",
            "delegation_id",
            "authority_generation",
            "boundary",
            "boundary_epoch",
            "lineage",
            "status",
            "scope",
        }
        _require_exact_fields(value, fields, "binding_source_authority relation")
        relationship = _exact_nonempty_string(
            value["relationship"], "binding_source_authority.relationship"
        )
        if relationship not in {"ROOT", "EXACT_DELEGATION"}:
            raise ValueError(
                "binding_source_authority.relationship must be ROOT or EXACT_DELEGATION"
            )
        status = _exact_nonempty_string(value["status"], "binding_source_authority.status")
        if status not in {"ACTIVE", "REVOKED", "REJECTED"}:
            raise ValueError(
                "binding_source_authority.status must be ACTIVE, REVOKED, or REJECTED"
            )
        scope = value["scope"]
        if not isinstance(scope, Mapping):
            raise ValueError("binding_source_authority.scope must be an object")
        return cls(
            relationship=relationship,
            root_id=_exact_nonempty_string(
                value["root_id"], "binding_source_authority.root_id"
            ),
            source_id=_exact_nonempty_string(
                value["source_id"], "binding_source_authority.source_id"
            ),
            delegation_id=_exact_nonempty_string(
                value["delegation_id"], "binding_source_authority.delegation_id"
            ),
            authority_generation=_exact_generation(
                value["authority_generation"],
                "binding_source_authority.authority_generation",
            ),
            boundary=_exact_nonempty_string(
                value["boundary"], "binding_source_authority.boundary"
            ),
            boundary_epoch=_exact_nonempty_string(
                value["boundary_epoch"], "binding_source_authority.boundary_epoch"
            ),
            lineage=_exact_nonempty_string(
                value["lineage"], "binding_source_authority.lineage"
            ),
            status=status,
            scope=BindingScope.from_mapping(scope),
        )


@dataclass(frozen=True)
class BindingLifecycle:
    binding_id: str
    binding_generation: int
    state: str
    event_id: str
    event_order: int
    source_id: str
    authority_generation: int
    lineage: str

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "BindingLifecycle":
        fields = {
            "binding_id",
            "binding_generation",
            "state",
            "event_id",
            "event_order",
            "source_id",
            "authority_generation",
            "lineage",
        }
        _require_exact_fields(value, fields, "binding_lifecycle record")
        state = _exact_nonempty_string(value["state"], "binding_lifecycle.state")
        if state not in {"ACTIVE", "INVALID", "REVOKED", "REJECTED", "SUPERSEDED"}:
            raise ValueError("unsupported binding_lifecycle.state")
        return cls(
            binding_id=_exact_nonempty_string(
                value["binding_id"], "binding_lifecycle.binding_id"
            ),
            binding_generation=_exact_generation(
                value["binding_generation"], "binding_lifecycle.binding_generation"
            ),
            state=state,
            event_id=_exact_nonempty_string(
                value["event_id"], "binding_lifecycle.event_id"
            ),
            event_order=_exact_generation(
                value["event_order"], "binding_lifecycle.event_order"
            ),
            source_id=_exact_nonempty_string(
                value["source_id"], "binding_lifecycle.source_id"
            ),
            authority_generation=_exact_generation(
                value["authority_generation"], "binding_lifecycle.authority_generation"
            ),
            lineage=_exact_nonempty_string(value["lineage"], "binding_lifecycle.lineage"),
        )


@dataclass(frozen=True)
class BindingOrdering:
    ordering_source_id: str
    lineage: str
    authority_generation: int
    head_binding_id: str
    head_binding_generation: int
    head_event_order: int

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "BindingOrdering":
        fields = {
            "ordering_source_id",
            "lineage",
            "authority_generation",
            "head_binding_id",
            "head_binding_generation",
            "head_event_order",
        }
        _require_exact_fields(value, fields, "binding_ordering")
        return cls(
            ordering_source_id=_exact_nonempty_string(
                value["ordering_source_id"], "binding_ordering.ordering_source_id"
            ),
            lineage=_exact_nonempty_string(value["lineage"], "binding_ordering.lineage"),
            authority_generation=_exact_generation(
                value["authority_generation"], "binding_ordering.authority_generation"
            ),
            head_binding_id=_exact_nonempty_string(
                value["head_binding_id"], "binding_ordering.head_binding_id"
            ),
            head_binding_generation=_exact_generation(
                value["head_binding_generation"],
                "binding_ordering.head_binding_generation",
            ),
            head_event_order=_exact_generation(
                value["head_event_order"], "binding_ordering.head_event_order"
            ),
        )


@dataclass(frozen=True)
class ContractTransformation:
    relationship: str
    transformation_id: str
    source_contract_id: str
    source_contract_version: str
    target_contract_id: str
    target_contract_version: str
    objective_id: str
    objective_generation: int
    source_id: str
    authority_generation: int
    transformation_generation: int
    boundary: str
    boundary_epoch: str
    lineage: str
    state: str
    scope: BindingScope

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "ContractTransformation":
        fields = {
            "relationship",
            "transformation_id",
            "source_contract_id",
            "source_contract_version",
            "target_contract_id",
            "target_contract_version",
            "objective_id",
            "objective_generation",
            "source_id",
            "authority_generation",
            "transformation_generation",
            "boundary",
            "boundary_epoch",
            "lineage",
            "state",
            "scope",
        }
        _require_exact_fields(value, fields, "contract_transformation_binding")
        relationship = _exact_nonempty_string(
            value["relationship"], "contract_transformation_binding.relationship"
        )
        if relationship != "ADMISSION_PRESERVING":
            raise ValueError(
                "contract_transformation_binding.relationship must be ADMISSION_PRESERVING"
            )
        state = _exact_nonempty_string(
            value["state"], "contract_transformation_binding.state"
        )
        if state not in {"ACTIVE", "INVALID", "REVOKED", "REJECTED"}:
            raise ValueError("unsupported contract_transformation_binding.state")
        scope = value["scope"]
        if not isinstance(scope, Mapping):
            raise ValueError("contract_transformation_binding.scope must be an object")
        return cls(
            relationship=relationship,
            transformation_id=_exact_nonempty_string(
                value["transformation_id"],
                "contract_transformation_binding.transformation_id",
            ),
            source_contract_id=_exact_nonempty_string(
                value["source_contract_id"],
                "contract_transformation_binding.source_contract_id",
            ),
            source_contract_version=_exact_nonempty_string(
                value["source_contract_version"],
                "contract_transformation_binding.source_contract_version",
            ),
            target_contract_id=_exact_nonempty_string(
                value["target_contract_id"],
                "contract_transformation_binding.target_contract_id",
            ),
            target_contract_version=_exact_nonempty_string(
                value["target_contract_version"],
                "contract_transformation_binding.target_contract_version",
            ),
            objective_id=_exact_nonempty_string(
                value["objective_id"], "contract_transformation_binding.objective_id"
            ),
            objective_generation=_exact_generation(
                value["objective_generation"],
                "contract_transformation_binding.objective_generation",
            ),
            source_id=_exact_nonempty_string(
                value["source_id"], "contract_transformation_binding.source_id"
            ),
            authority_generation=_exact_generation(
                value["authority_generation"],
                "contract_transformation_binding.authority_generation",
            ),
            transformation_generation=_exact_generation(
                value["transformation_generation"],
                "contract_transformation_binding.transformation_generation",
            ),
            boundary=_exact_nonempty_string(
                value["boundary"], "contract_transformation_binding.boundary"
            ),
            boundary_epoch=_exact_nonempty_string(
                value["boundary_epoch"],
                "contract_transformation_binding.boundary_epoch",
            ),
            lineage=_exact_nonempty_string(
                value["lineage"], "contract_transformation_binding.lineage"
            ),
            state=state,
            scope=BindingScope.from_mapping(scope),
        )


@dataclass(frozen=True)
class AuthorityStateBinding:
    subject: str
    artifact: str
    control_state: str
    identity_basis: str
    boundary_epoch: str
    decision: AuthorityOutcome
    evidence_id: str
    execution_context: str
    applicable_boundary: str
    grant_id: str
    consumption_state: str
    subject_mode: str

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "AuthorityStateBinding":
        fields = set(TUPLE_FIELDS) | {
            "evidence_id",
            "execution_context",
            "applicable_boundary",
            "grant_id",
            "consumption_state",
            "subject_mode",
        }
        if set(value) != fields:
            raise ValueError("authority_state must contain exactly the relational binding fields")
        return cls(
            subject=_exact_string(value["subject"], "authority_state.subject"),
            artifact=_exact_string(value["artifact"], "authority_state.artifact"),
            control_state=_exact_string(value["control_state"], "authority_state.control_state"),
            identity_basis=_exact_string(value["identity_basis"], "authority_state.identity_basis"),
            boundary_epoch=_exact_string(value["boundary_epoch"], "authority_state.boundary_epoch"),
            decision=AuthorityOutcome(value["decision"]),
            evidence_id=_exact_string(value["evidence_id"], "authority_state.evidence_id"),
            execution_context=_exact_string(
                value["execution_context"], "authority_state.execution_context"
            ),
            applicable_boundary=_exact_string(
                value["applicable_boundary"], "authority_state.applicable_boundary"
            ),
            grant_id=_exact_string(value["grant_id"], "authority_state.grant_id"),
            consumption_state=_exact_string(
                value["consumption_state"], "authority_state.consumption_state"
            ),
            subject_mode=_exact_string(value["subject_mode"], "authority_state.subject_mode"),
        )


@dataclass(frozen=True)
class Reestablishment:
    previous_evidence_id: str
    current: AuthorityStateBinding

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "Reestablishment":
        if set(value) != {"previous_evidence_id", "current"}:
            raise ValueError("reestablishment must bind previous_evidence_id to current state")
        current = value["current"]
        if not isinstance(current, Mapping):
            raise ValueError("reestablishment.current must be an object")
        return cls(
            previous_evidence_id=_exact_string(
                value["previous_evidence_id"], "reestablishment.previous_evidence_id"
            ),
            current=AuthorityStateBinding.from_mapping(current),
        )


@dataclass(frozen=True)
class GrantTransition:
    relationship: str
    grant_path: tuple[str, ...]
    previous: AuthorityStateBinding
    current: AuthorityStateBinding

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "GrantTransition":
        if set(value) != {"relationship", "grant_path", "previous", "current"}:
            raise ValueError(
                "grant_transition must bind one exact previous authority state "
                "to one exact current authority state"
            )
        previous = value["previous"]
        current = value["current"]
        if not isinstance(previous, Mapping) or not isinstance(current, Mapping):
            raise ValueError("grant_transition previous and current must be objects")
        raw_path = value["grant_path"]
        if not isinstance(raw_path, (list, tuple)) or len(raw_path) < 2:
            raise ValueError("grant_transition.grant_path must contain at least two grants")
        grant_path = tuple(
            _exact_string(item, "grant_transition.grant_path") for item in raw_path
        )
        if any(item == "" for item in grant_path):
            raise ValueError("grant_transition.grant_path grants must be non-empty")
        return cls(
            relationship=_exact_string(
                value["relationship"], "grant_transition.relationship"
            ),
            grant_path=grant_path,
            previous=AuthorityStateBinding.from_mapping(previous),
            current=AuthorityStateBinding.from_mapping(current),
        )


@dataclass(frozen=True)
class Fact:
    state: FactState
    value: Any = None
    values: tuple[Any, ...] = ()

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "Fact":
        state = FactState(value["state"])
        if state is FactState.KNOWN:
            if "value" not in value:
                raise ValueError("KNOWN facts require value")
            return cls(state=state, value=value["value"])
        if state is FactState.CONFLICTING:
            values = tuple(value.get("values", ()))
            if len(values) < 2:
                raise ValueError("CONFLICTING facts require at least two values")
            return cls(state=state, values=values)
        return cls(state=state)


def _fact_or_unknown(facts: Mapping[str, Fact], name: str) -> Fact:
    return facts.get(name, Fact(FactState.UNKNOWN))


def _known_object(fact: Fact, field: str) -> Mapping[str, Any] | None:
    if fact.state is not FactState.KNOWN:
        return None
    if not isinstance(fact.value, Mapping):
        raise ValueError(f"KNOWN {field} requires an object value")
    return fact.value


def _known_object_list(fact: Fact, field: str) -> tuple[Mapping[str, Any], ...]:
    if fact.state is not FactState.KNOWN:
        return ()
    if not isinstance(fact.value, (list, tuple)) or not fact.value:
        raise ValueError(f"KNOWN {field} requires a non-empty array")
    if not all(isinstance(item, Mapping) for item in fact.value):
        raise ValueError(f"KNOWN {field} entries must be objects")
    return tuple(fact.value)


@dataclass(frozen=True)
class ObjectiveBindingFacts:
    raw: Mapping[str, Fact]
    objective_identity: ObjectiveIdentity | None
    decision_contract_identity: DecisionContractIdentity | None
    authority_root: AuthorityRoot | None
    candidates: tuple[ObjectiveBinding, ...]
    sources: tuple[BindingSourceAuthority, ...]
    lifecycles: tuple[BindingLifecycle, ...]
    ordering: BindingOrdering | None
    transformations: tuple[ContractTransformation, ...]

    @classmethod
    def from_facts(cls, facts: Mapping[str, Fact]) -> "ObjectiveBindingFacts":
        objective_fact = _fact_or_unknown(facts, "objective_identity")
        contract_fact = _fact_or_unknown(facts, "decision_contract_identity")
        root_fact = _fact_or_unknown(facts, "authority_root")
        candidate_fact = _fact_or_unknown(facts, "objective_binding")
        source_fact = _fact_or_unknown(facts, "binding_source_authority")
        lifecycle_fact = _fact_or_unknown(facts, "binding_lifecycle")
        ordering_fact = _fact_or_unknown(facts, "binding_ordering")
        transformation_fact = _fact_or_unknown(
            facts, "contract_transformation_binding"
        )

        objective_value = _known_object(objective_fact, "objective_identity")
        contract_value = _known_object(contract_fact, "decision_contract_identity")
        root_value = _known_object(root_fact, "authority_root")
        ordering_value = _known_object(ordering_fact, "binding_ordering")

        return cls(
            raw={
                name: _fact_or_unknown(facts, name)
                for name in (*OBJECTIVE_BINDING_FACTS, "contract_transformation_binding")
            },
            objective_identity=(
                ObjectiveIdentity.from_mapping(objective_value)
                if objective_value is not None
                else None
            ),
            decision_contract_identity=(
                DecisionContractIdentity.from_mapping(contract_value)
                if contract_value is not None
                else None
            ),
            authority_root=(
                AuthorityRoot.from_mapping(root_value) if root_value is not None else None
            ),
            candidates=tuple(
                ObjectiveBinding.from_mapping(value)
                for value in _known_object_list(candidate_fact, "objective_binding")
            ),
            sources=tuple(
                BindingSourceAuthority.from_mapping(value)
                for value in _known_object_list(
                    source_fact, "binding_source_authority"
                )
            ),
            lifecycles=tuple(
                BindingLifecycle.from_mapping(value)
                for value in _known_object_list(lifecycle_fact, "binding_lifecycle")
            ),
            ordering=(
                BindingOrdering.from_mapping(ordering_value)
                if ordering_value is not None
                else None
            ),
            transformations=tuple(
                ContractTransformation.from_mapping(value)
                for value in _known_object_list(
                    transformation_fact, "contract_transformation_binding"
                )
            ),
        )


@dataclass(frozen=True)
class Prohibition:
    state: FactState
    applies: bool | None
    identifier: str

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "Prohibition":
        state = FactState(value["state"])
        applies = value.get("applies")
        if state is FactState.KNOWN and not isinstance(applies, bool):
            raise ValueError("KNOWN prohibition requires boolean applies")
        if state is not FactState.KNOWN:
            applies = None
        return cls(state=state, applies=applies, identifier=str(value.get("id", "unspecified")))


@dataclass(frozen=True)
class Mutation:
    field: str
    before: Any
    after: Any


@dataclass(frozen=True)
class OracleInput:
    schema_version: str
    case_id: str
    authority_tuple: AuthorityTuple
    t1_result: AuthorityOutcome
    t1_evidence: tuple[str, ...]
    t1_authority_state: AuthorityStateBinding
    t1_binding_facts: ObjectiveBindingFacts
    t2_creates_authority: bool
    t2_mutations: tuple[Mutation, ...]
    facts: Mapping[str, Fact]
    t3_binding_facts: ObjectiveBindingFacts
    required_facts: tuple[str, ...]
    required_values: Mapping[str, Any]
    reestablishment_state: FactState
    reestablishment: Reestablishment | None
    grant_transition_state: FactState
    grant_transition: GrantTransition | None
    prohibition: Prohibition
    applicable_invariants: tuple[str, ...]
    authority_question: str

    @classmethod
    def from_fixture(cls, fixture: Mapping[str, Any]) -> "OracleInput":
        schema_version = _exact_string(fixture.get("schema_version"), "schema_version")
        if schema_version not in {"authority-lab-v0", "authority-lab-v1"}:
            raise ValueError("unsupported fixture schema_version")
        t1 = fixture["t1"]
        t2 = fixture["t2"]
        t3 = fixture["t3"]
        invariants = tuple(fixture["applicable_invariants"])
        unknown_invariants = set(invariants) - set(INVARIANTS)
        if unknown_invariants:
            raise ValueError(f"unknown invariant identifiers: {sorted(unknown_invariants)}")
        if len(invariants) != len(set(invariants)):
            raise ValueError("applicable_invariants must not contain duplicates")
        creates_authority = t2["creates_authority"]
        if not isinstance(creates_authority, bool):
            raise ValueError("t2.creates_authority must be boolean")
        required_facts = tuple(t3["required_facts"])
        if len(required_facts) != len(set(required_facts)):
            raise ValueError("required_facts must not contain duplicates")
        facts = {name: Fact.from_mapping(raw) for name, raw in t3["facts"].items()}
        raw_t1_binding_facts = t1.get("binding_facts", {})
        if not isinstance(raw_t1_binding_facts, Mapping):
            raise ValueError("t1.binding_facts must be an object")
        t1_binding_fact_map = {
            name: Fact.from_mapping(raw) for name, raw in raw_t1_binding_facts.items()
        }
        required_values = dict(t3.get("required_values", {}))
        evidence = tuple(t1["evidence"])
        if not all(isinstance(item, str) for item in evidence):
            raise ValueError("t1.evidence identifiers must be strings")
        raw_reestablishment = Fact.from_mapping(
            t3.get("reestablishment", {"state": FactState.UNKNOWN.value})
        )
        reestablishment = None
        if raw_reestablishment.state is FactState.KNOWN:
            if not isinstance(raw_reestablishment.value, Mapping):
                raise ValueError("KNOWN reestablishment requires an object value")
            reestablishment = Reestablishment.from_mapping(raw_reestablishment.value)
        raw_grant_transition = Fact.from_mapping(
            t3.get("grant_transition", {"state": FactState.UNKNOWN.value})
        )
        grant_transition = None
        if raw_grant_transition.state is FactState.KNOWN:
            if not isinstance(raw_grant_transition.value, Mapping):
                raise ValueError("KNOWN grant_transition requires an object value")
            grant_transition = GrantTransition.from_mapping(raw_grant_transition.value)
        mutations = tuple(
            Mutation(
                _exact_string(item["field"], "t2.mutations.field"),
                item.get("before"),
                item.get("after"),
            )
            for item in t2["mutations"]
        )
        return cls(
            schema_version=schema_version,
            case_id=str(fixture["case_id"]),
            authority_tuple=AuthorityTuple.from_mapping(fixture["authority_tuple"]),
            t1_result=AuthorityOutcome(t1["result"]),
            t1_evidence=evidence,
            t1_authority_state=AuthorityStateBinding.from_mapping(t1["authority_state"]),
            t1_binding_facts=ObjectiveBindingFacts.from_facts(t1_binding_fact_map),
            t2_creates_authority=creates_authority,
            t2_mutations=mutations,
            facts=facts,
            t3_binding_facts=ObjectiveBindingFacts.from_facts(facts),
            required_facts=required_facts,
            required_values=required_values,
            reestablishment_state=raw_reestablishment.state,
            reestablishment=reestablishment,
            grant_transition_state=raw_grant_transition.state,
            grant_transition=grant_transition,
            prohibition=Prohibition.from_mapping(t3["prohibition"]),
            applicable_invariants=invariants,
            authority_question=str(t3["authority_question"]),
        )


@dataclass(frozen=True)
class Reason:
    code: str
    detail: str
    facts: tuple[str, ...] = ()


@dataclass(frozen=True)
class OracleResult:
    outcome: AuthorityOutcome
    reasons: tuple[Reason, ...]
    engaged_invariants: tuple[str, ...]


@dataclass(frozen=True)
class RunResult:
    case_id: str
    title: str
    expected: AuthorityOutcome
    actual: OracleResult
    status: HarnessStatus
    oracle_input: OracleInput
