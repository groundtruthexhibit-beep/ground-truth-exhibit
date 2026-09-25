"""Bounded public data model for Authority Lab v1."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
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


class MutationTargetKind(str, Enum):
    STATE = "STATE"
    RELATION = "RELATION"
    BINDING = "BINDING"
    FACT = "FACT"


@dataclass(frozen=True)
class MutationSpec:
    canonical_field: str
    target_kind: MutationTargetKind
    target: str
    legacy_aliases: tuple[str, ...] = ()


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
    "evidence_binding",
    "freshness",
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

OBSERVATION_PROFILE_ID = "AUTHORITY-LAB-OBSERVATION-PROFILE-1"
OBSERVATION_PROFILE_VERSION = 1
OBSERVATION_SCOPE_FAMILIES = (
    "SUBJECT_AND_DELEGATION",
    "ARTIFACT_AND_TRANSFORMATION",
    "EXECUTION_CONTROL",
    "BOUNDARY_AND_EPOCH",
    "CREDENTIAL_AND_IDENTITY",
    "GRANT_USE_AND_CONSUMPTION",
    "OBJECTIVE_AUTHORITY_LIFECYCLE",
    "OBSERVATION_PIPELINE",
)
OBSERVATION_LIFECYCLE_STATES = (
    "ACTIVE",
    "INVALID",
    "REVOKED",
    "REJECTED",
    "SUPERSEDED",
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


def _exact_scope_families(value: Any, field: str) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)) or not value:
        raise ValueError(f"{field} must be a non-empty array")
    families = tuple(_exact_nonempty_string(item, field) for item in value)
    if len(families) != len(set(families)):
        raise ValueError(f"{field} must not contain duplicates")
    unknown = set(families) - set(OBSERVATION_SCOPE_FAMILIES)
    if unknown:
        raise ValueError(f"{field} contains unknown scope families: {sorted(unknown)}")
    return families


def _exact_lifecycle_state(value: Any, field: str) -> str:
    state = _exact_nonempty_string(value, field)
    if state not in OBSERVATION_LIFECYCLE_STATES:
        raise ValueError(f"{field} is unsupported")
    return state


def exact_value_equal(left: Any, right: Any) -> bool:
    """Compare fixture values without Python bool/int or container coercion."""
    if type(left) is not type(right):
        return False
    if isinstance(left, Mapping):
        return set(left) == set(right) and all(
            exact_value_equal(left[key], right[key]) for key in left
        )
    if isinstance(left, (list, tuple)):
        return len(left) == len(right) and all(
            exact_value_equal(left_item, right_item)
            for left_item, right_item in zip(left, right)
        )
    return bool(left == right)


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
class ObservationAnchor:
    anchor_id: str
    event_order: int

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any], field: str) -> "ObservationAnchor":
        _require_exact_fields(value, {"anchor_id", "event_order"}, field)
        return cls(
            _exact_nonempty_string(value["anchor_id"], f"{field}.anchor_id"),
            _exact_generation(value["event_order"], f"{field}.event_order"),
        )


@dataclass(frozen=True)
class ObserverAdmission:
    observer_id: str
    observer_generation: int
    observer_identity_basis: str
    scope_families: tuple[str, ...]
    lifecycle_state: str
    observation_binding_id: str
    observation_binding_generation: int

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "ObserverAdmission":
        field = "evidence_binding.observers"
        _require_exact_fields(
            value,
            {
                "observer_id",
                "observer_generation",
                "observer_identity_basis",
                "scope_families",
                "lifecycle_state",
                "observation_binding_id",
                "observation_binding_generation",
            },
            f"{field} entry",
        )
        return cls(
            _exact_nonempty_string(value["observer_id"], f"{field}.observer_id"),
            _exact_generation(value["observer_generation"], f"{field}.observer_generation"),
            _exact_nonempty_string(
                value["observer_identity_basis"], f"{field}.observer_identity_basis"
            ),
            _exact_scope_families(value["scope_families"], f"{field}.scope_families"),
            _exact_lifecycle_state(value["lifecycle_state"], f"{field}.lifecycle_state"),
            _exact_nonempty_string(
                value["observation_binding_id"], f"{field}.observation_binding_id"
            ),
            _exact_generation(
                value["observation_binding_generation"],
                f"{field}.observation_binding_generation",
            ),
        )


@dataclass(frozen=True)
class ObservationSegment:
    segment_id: str
    observer_id: str
    observer_generation: int
    stream_id: str
    stream_generation: int
    scope_families: tuple[str, ...]
    start_anchor_id: str
    start_event_order: int
    end_anchor_id: str
    end_event_order: int
    start_sequence: int
    end_sequence: int
    stream_commitment: str
    boundary_epoch: str
    observation_binding_generation: int

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "ObservationSegment":
        field = "evidence_binding.segments"
        _require_exact_fields(
            value,
            {
                "segment_id", "observer_id", "observer_generation", "stream_id",
                "stream_generation", "scope_families", "start_anchor_id",
                "start_event_order", "end_anchor_id", "end_event_order",
                "start_sequence", "end_sequence", "stream_commitment",
                "boundary_epoch", "observation_binding_generation",
            },
            f"{field} entry",
        )
        return cls(
            _exact_nonempty_string(value["segment_id"], f"{field}.segment_id"),
            _exact_nonempty_string(value["observer_id"], f"{field}.observer_id"),
            _exact_generation(value["observer_generation"], f"{field}.observer_generation"),
            _exact_nonempty_string(value["stream_id"], f"{field}.stream_id"),
            _exact_generation(value["stream_generation"], f"{field}.stream_generation"),
            _exact_scope_families(value["scope_families"], f"{field}.scope_families"),
            _exact_nonempty_string(value["start_anchor_id"], f"{field}.start_anchor_id"),
            _exact_generation(value["start_event_order"], f"{field}.start_event_order"),
            _exact_nonempty_string(value["end_anchor_id"], f"{field}.end_anchor_id"),
            _exact_generation(value["end_event_order"], f"{field}.end_event_order"),
            _exact_generation(value["start_sequence"], f"{field}.start_sequence"),
            _exact_generation(value["end_sequence"], f"{field}.end_sequence"),
            _exact_nonempty_string(value["stream_commitment"], f"{field}.stream_commitment"),
            _exact_nonempty_string(value["boundary_epoch"], f"{field}.boundary_epoch"),
            _exact_generation(
                value["observation_binding_generation"],
                f"{field}.observation_binding_generation",
            ),
        )


@dataclass(frozen=True)
class ObservationHandoff:
    relationship: str
    handoff_id: str
    from_observer_id: str
    from_observer_generation: int
    to_observer_id: str
    to_observer_generation: int
    from_segment_id: str
    to_segment_id: str
    scope_families: tuple[str, ...]
    handoff_anchor_id: str
    handoff_event_order: int
    source_id: str
    authority_generation: int
    boundary: str
    boundary_epoch: str
    lineage: str

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "ObservationHandoff":
        field = "evidence_binding.handoffs"
        _require_exact_fields(
            value,
            {
                "relationship", "handoff_id", "from_observer_id",
                "from_observer_generation", "to_observer_id",
                "to_observer_generation", "from_segment_id", "to_segment_id",
                "scope_families", "handoff_anchor_id", "handoff_event_order",
                "source_id", "authority_generation", "boundary", "boundary_epoch",
                "lineage",
            },
            f"{field} entry",
        )
        relationship = _exact_nonempty_string(value["relationship"], f"{field}.relationship")
        if relationship != "AUTHORITY_PRESERVING_OBSERVER_HANDOFF":
            raise ValueError(f"{field}.relationship is unsupported")
        return cls(
            relationship,
            _exact_nonempty_string(value["handoff_id"], f"{field}.handoff_id"),
            _exact_nonempty_string(value["from_observer_id"], f"{field}.from_observer_id"),
            _exact_generation(
                value["from_observer_generation"], f"{field}.from_observer_generation"
            ),
            _exact_nonempty_string(value["to_observer_id"], f"{field}.to_observer_id"),
            _exact_generation(
                value["to_observer_generation"], f"{field}.to_observer_generation"
            ),
            _exact_nonempty_string(value["from_segment_id"], f"{field}.from_segment_id"),
            _exact_nonempty_string(value["to_segment_id"], f"{field}.to_segment_id"),
            _exact_scope_families(value["scope_families"], f"{field}.scope_families"),
            _exact_nonempty_string(value["handoff_anchor_id"], f"{field}.handoff_anchor_id"),
            _exact_generation(value["handoff_event_order"], f"{field}.handoff_event_order"),
            _exact_nonempty_string(value["source_id"], f"{field}.source_id"),
            _exact_generation(value["authority_generation"], f"{field}.authority_generation"),
            _exact_nonempty_string(value["boundary"], f"{field}.boundary"),
            _exact_nonempty_string(value["boundary_epoch"], f"{field}.boundary_epoch"),
            _exact_nonempty_string(value["lineage"], f"{field}.lineage"),
        )


@dataclass(frozen=True)
class ObservationTransformation:
    relationship: str
    transformation_id: str
    transformation_generation: int
    source_stream_id: str
    source_stream_generation: int
    source_commitment: str
    target_stream_id: str
    target_stream_generation: int
    target_commitment: str
    scope_families: tuple[str, ...]
    source_id: str
    authority_generation: int
    boundary: str
    boundary_epoch: str
    lineage: str
    lifecycle_state: str

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "ObservationTransformation":
        field = "evidence_binding.transformations"
        _require_exact_fields(
            value,
            {
                "relationship", "transformation_id", "transformation_generation",
                "source_stream_id", "source_stream_generation", "source_commitment",
                "target_stream_id", "target_stream_generation", "target_commitment",
                "scope_families", "source_id", "authority_generation", "boundary",
                "boundary_epoch", "lineage", "lifecycle_state",
            },
            f"{field} entry",
        )
        relationship = _exact_nonempty_string(value["relationship"], f"{field}.relationship")
        if relationship != "OBSERVATION_PRESERVING":
            raise ValueError(f"{field}.relationship is unsupported")
        return cls(
            relationship,
            _exact_nonempty_string(
                value["transformation_id"], f"{field}.transformation_id"
            ),
            _exact_generation(
                value["transformation_generation"], f"{field}.transformation_generation"
            ),
            _exact_nonempty_string(value["source_stream_id"], f"{field}.source_stream_id"),
            _exact_generation(
                value["source_stream_generation"], f"{field}.source_stream_generation"
            ),
            _exact_nonempty_string(value["source_commitment"], f"{field}.source_commitment"),
            _exact_nonempty_string(value["target_stream_id"], f"{field}.target_stream_id"),
            _exact_generation(
                value["target_stream_generation"], f"{field}.target_stream_generation"
            ),
            _exact_nonempty_string(value["target_commitment"], f"{field}.target_commitment"),
            _exact_scope_families(value["scope_families"], f"{field}.scope_families"),
            _exact_nonempty_string(value["source_id"], f"{field}.source_id"),
            _exact_generation(value["authority_generation"], f"{field}.authority_generation"),
            _exact_nonempty_string(value["boundary"], f"{field}.boundary"),
            _exact_nonempty_string(value["boundary_epoch"], f"{field}.boundary_epoch"),
            _exact_nonempty_string(value["lineage"], f"{field}.lineage"),
            _exact_lifecycle_state(value["lifecycle_state"], f"{field}.lifecycle_state"),
        )


@dataclass(frozen=True)
class ObservationLifecycle:
    record_id: str
    target_kind: str
    target_id: str
    target_generation: int
    state: str
    event_id: str
    event_order: int
    source_id: str
    authority_generation: int
    boundary: str
    boundary_epoch: str
    lineage: str

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "ObservationLifecycle":
        field = "evidence_binding.lifecycle_records"
        _require_exact_fields(
            value,
            {
                "record_id", "target_kind", "target_id", "target_generation", "state",
                "event_id", "event_order", "source_id", "authority_generation",
                "boundary", "boundary_epoch", "lineage",
            },
            f"{field} entry",
        )
        target_kind = _exact_nonempty_string(value["target_kind"], f"{field}.target_kind")
        if target_kind not in {"OBSERVATION_BINDING", "OBSERVER"}:
            raise ValueError(f"{field}.target_kind is unsupported")
        return cls(
            _exact_nonempty_string(value["record_id"], f"{field}.record_id"),
            target_kind,
            _exact_nonempty_string(value["target_id"], f"{field}.target_id"),
            _exact_generation(value["target_generation"], f"{field}.target_generation"),
            _exact_lifecycle_state(value["state"], f"{field}.state"),
            _exact_nonempty_string(value["event_id"], f"{field}.event_id"),
            _exact_generation(value["event_order"], f"{field}.event_order"),
            _exact_nonempty_string(value["source_id"], f"{field}.source_id"),
            _exact_generation(value["authority_generation"], f"{field}.authority_generation"),
            _exact_nonempty_string(value["boundary"], f"{field}.boundary"),
            _exact_nonempty_string(value["boundary_epoch"], f"{field}.boundary_epoch"),
            _exact_nonempty_string(value["lineage"], f"{field}.lineage"),
        )


def _typed_object_array(value: Any, field: str, parser: Any) -> tuple[Any, ...]:
    if not isinstance(value, (list, tuple)):
        raise ValueError(f"{field} must be an array")
    if not all(isinstance(item, Mapping) for item in value):
        raise ValueError(f"{field} entries must be objects")
    return tuple(parser(item) for item in value)


@dataclass(frozen=True)
class ObservationBinding:
    relationship: str
    observation_binding_id: str
    observation_binding_generation: int
    profile_id: str
    profile_version: int
    objective_binding_id: str
    objective_binding_generation: int
    decision_contract_id: str
    decision_contract_version: str
    source_id: str
    authority_generation: int
    boundary: str
    boundary_epoch: str
    lineage: str
    ordering_source_id: str
    t1_anchor: ObservationAnchor
    t3_anchor: ObservationAnchor
    observers: tuple[ObserverAdmission, ...]
    segments: tuple[ObservationSegment, ...]
    handoffs: tuple[ObservationHandoff, ...]
    transformations: tuple[ObservationTransformation, ...]
    lifecycle_records: tuple[ObservationLifecycle, ...]

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "ObservationBinding":
        field = "evidence_binding"
        _require_exact_fields(
            value,
            {
                "relationship", "observation_binding_id",
                "observation_binding_generation", "profile_id", "profile_version",
                "objective_binding_id", "objective_binding_generation",
                "decision_contract_id", "decision_contract_version", "source_id",
                "authority_generation", "boundary", "boundary_epoch", "lineage",
                "ordering_source_id", "t1_anchor", "t3_anchor", "observers",
                "segments", "handoffs", "transformations", "lifecycle_records",
            },
            field,
        )
        relationship = _exact_nonempty_string(value["relationship"], f"{field}.relationship")
        if relationship != "OBSERVATION_COVERAGE":
            raise ValueError(f"{field}.relationship must be OBSERVATION_COVERAGE")
        t1_anchor = value["t1_anchor"]
        t3_anchor = value["t3_anchor"]
        if not isinstance(t1_anchor, Mapping) or not isinstance(t3_anchor, Mapping):
            raise ValueError(f"{field} anchors must be objects")
        return cls(
            relationship,
            _exact_nonempty_string(
                value["observation_binding_id"], f"{field}.observation_binding_id"
            ),
            _exact_generation(
                value["observation_binding_generation"],
                f"{field}.observation_binding_generation",
            ),
            _exact_nonempty_string(value["profile_id"], f"{field}.profile_id"),
            _exact_generation(value["profile_version"], f"{field}.profile_version"),
            _exact_nonempty_string(
                value["objective_binding_id"], f"{field}.objective_binding_id"
            ),
            _exact_generation(
                value["objective_binding_generation"],
                f"{field}.objective_binding_generation",
            ),
            _exact_nonempty_string(
                value["decision_contract_id"], f"{field}.decision_contract_id"
            ),
            _exact_nonempty_string(
                value["decision_contract_version"], f"{field}.decision_contract_version"
            ),
            _exact_nonempty_string(value["source_id"], f"{field}.source_id"),
            _exact_generation(value["authority_generation"], f"{field}.authority_generation"),
            _exact_nonempty_string(value["boundary"], f"{field}.boundary"),
            _exact_nonempty_string(value["boundary_epoch"], f"{field}.boundary_epoch"),
            _exact_nonempty_string(value["lineage"], f"{field}.lineage"),
            _exact_nonempty_string(value["ordering_source_id"], f"{field}.ordering_source_id"),
            ObservationAnchor.from_mapping(t1_anchor, f"{field}.t1_anchor"),
            ObservationAnchor.from_mapping(t3_anchor, f"{field}.t3_anchor"),
            _typed_object_array(value["observers"], f"{field}.observers", ObserverAdmission.from_mapping),
            _typed_object_array(value["segments"], f"{field}.segments", ObservationSegment.from_mapping),
            _typed_object_array(value["handoffs"], f"{field}.handoffs", ObservationHandoff.from_mapping),
            _typed_object_array(
                value["transformations"],
                f"{field}.transformations",
                ObservationTransformation.from_mapping,
            ),
            _typed_object_array(
                value["lifecycle_records"],
                f"{field}.lifecycle_records",
                ObservationLifecycle.from_mapping,
            ),
        )


@dataclass(frozen=True)
class ObservationFreshness:
    relationship: str
    observation_binding_id: str
    observation_binding_generation: int
    profile_id: str
    profile_version: int
    boundary: str
    boundary_epoch: str
    lineage: str
    source_id: str
    authority_generation: int
    ordering_source_id: str
    head_anchor_id: str
    head_event_order: int

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "ObservationFreshness":
        field = "freshness"
        _require_exact_fields(
            value,
            {
                "relationship", "observation_binding_id",
                "observation_binding_generation", "profile_id", "profile_version",
                "boundary", "boundary_epoch", "lineage", "source_id",
                "authority_generation", "ordering_source_id", "head_anchor_id",
                "head_event_order",
            },
            field,
        )
        relationship = _exact_nonempty_string(value["relationship"], f"{field}.relationship")
        if relationship != "OBSERVATION_CURRENT_AT_T3":
            raise ValueError(f"{field}.relationship must be OBSERVATION_CURRENT_AT_T3")
        return cls(
            relationship,
            _exact_nonempty_string(
                value["observation_binding_id"], f"{field}.observation_binding_id"
            ),
            _exact_generation(
                value["observation_binding_generation"],
                f"{field}.observation_binding_generation",
            ),
            _exact_nonempty_string(value["profile_id"], f"{field}.profile_id"),
            _exact_generation(value["profile_version"], f"{field}.profile_version"),
            _exact_nonempty_string(value["boundary"], f"{field}.boundary"),
            _exact_nonempty_string(value["boundary_epoch"], f"{field}.boundary_epoch"),
            _exact_nonempty_string(value["lineage"], f"{field}.lineage"),
            _exact_nonempty_string(value["source_id"], f"{field}.source_id"),
            _exact_generation(value["authority_generation"], f"{field}.authority_generation"),
            _exact_nonempty_string(value["ordering_source_id"], f"{field}.ordering_source_id"),
            _exact_nonempty_string(value["head_anchor_id"], f"{field}.head_anchor_id"),
            _exact_generation(value["head_event_order"], f"{field}.head_event_order"),
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


_MUTATION_FIELD_PATTERN = re.compile(r"[a-z][a-z0-9_]*", re.ASCII)

MUTATION_SPECS = (
    MutationSpec("subject", MutationTargetKind.STATE, "subject", ("principal",)),
    MutationSpec("artifact", MutationTargetKind.STATE, "artifact"),
    MutationSpec("control_state", MutationTargetKind.STATE, "control_state", ("privilege",)),
    MutationSpec("identity_basis", MutationTargetKind.STATE, "identity_basis"),
    MutationSpec("boundary_epoch", MutationTargetKind.STATE, "boundary_epoch"),
    MutationSpec("decision", MutationTargetKind.STATE, "decision"),
    MutationSpec("applicable_boundary", MutationTargetKind.STATE, "applicable_boundary"),
    MutationSpec(
        "consumption_state", MutationTargetKind.STATE, "consumption_state", ("consumption",)
    ),
    MutationSpec("decision_binding", MutationTargetKind.STATE, "evidence_id"),
    MutationSpec("evidence_id", MutationTargetKind.STATE, "evidence_id"),
    MutationSpec(
        "execution_context", MutationTargetKind.STATE, "execution_context", ("actor_context",)
    ),
    MutationSpec("grant_id", MutationTargetKind.STATE, "grant_id"),
    MutationSpec("subject_mode", MutationTargetKind.STATE, "subject_mode"),
    MutationSpec("boundary_epoch_binding", MutationTargetKind.RELATION, "boundary_epoch_binding"),
    MutationSpec("closure_binding", MutationTargetKind.RELATION, "closure_binding"),
    MutationSpec("consumption_binding", MutationTargetKind.RELATION, "consumption_binding"),
    MutationSpec("delegation_binding", MutationTargetKind.RELATION, "delegation_binding"),
    MutationSpec("evidence_binding", MutationTargetKind.RELATION, "evidence_binding"),
    MutationSpec(
        "execution_control_binding", MutationTargetKind.RELATION, "execution_control_binding"
    ),
    MutationSpec("freshness", MutationTargetKind.RELATION, "freshness"),
    MutationSpec("authority_root", MutationTargetKind.BINDING, "authority_root"),
    MutationSpec("binding_lifecycle", MutationTargetKind.BINDING, "binding_lifecycle"),
    MutationSpec("binding_ordering", MutationTargetKind.BINDING, "binding_ordering"),
    MutationSpec(
        "binding_source_authority", MutationTargetKind.BINDING, "binding_source_authority"
    ),
    MutationSpec(
        "contract_transformation_binding",
        MutationTargetKind.BINDING,
        "contract_transformation_binding",
    ),
    MutationSpec(
        "decision_contract_identity",
        MutationTargetKind.BINDING,
        "decision_contract_identity",
    ),
    MutationSpec("objective_binding", MutationTargetKind.BINDING, "objective_binding"),
    MutationSpec("objective_identity", MutationTargetKind.BINDING, "objective_identity"),
    MutationSpec("commit_state", MutationTargetKind.FACT, "commit_state"),
    MutationSpec(
        "credential_identity", MutationTargetKind.FACT, "credential_identity", ("credential",)
    ),
    MutationSpec(
        "tool_connector_identity",
        MutationTargetKind.FACT,
        "tool_connector_identity",
        ("connector_endpoint",),
    ),
)


def _build_mutation_registry() -> Mapping[str, MutationSpec]:
    registry: dict[str, MutationSpec] = {}
    for spec in MUTATION_SPECS:
        for field in (spec.canonical_field, *spec.legacy_aliases):
            if field in registry:
                raise RuntimeError(f"duplicate mutation registry field: {field}")
            registry[field] = spec
    return MappingProxyType(registry)


MUTATION_REGISTRY = _build_mutation_registry()
MUTATION_CANONICAL_FIELDS = tuple(spec.canonical_field for spec in MUTATION_SPECS)
MUTATION_LEGACY_ALIASES = MappingProxyType(
    {
        alias: spec.canonical_field
        for spec in MUTATION_SPECS
        for alias in spec.legacy_aliases
    }
)


def _validate_relation_mutation_value(spec: MutationSpec, value: Mapping[str, Any], field: str) -> None:
    exact_fields = {
        "boundary_epoch_binding": {"applicable_boundary", "boundary_epoch"},
        "execution_control_binding": {"execution_context", "control_state"},
        "consumption_binding": {"grant_id", "subject", "artifact", "boundary_epoch"},
        "closure_binding": {"relationship", "source_artifact", "target_artifact"},
    }
    if spec.target == "delegation_binding":
        relationship = value.get("relationship")
        if relationship == "DIRECT":
            fields = {
                "relationship",
                "subject",
                "artifact",
                "control_state",
                "boundary_epoch",
                "applicable_boundary",
            }
        elif relationship == "EXACT_DELEGATION":
            fields = {
                "relationship",
                "delegator",
                "delegate",
                "artifact",
                "control_state",
                "boundary_epoch",
                "applicable_boundary",
            }
        else:
            raise ValueError(f"{field}.relationship is unsupported")
    else:
        fields = exact_fields[spec.target]
    _require_exact_fields(value, fields, field)
    for name in fields:
        _exact_nonempty_string(value[name], f"{field}.{name}")


def _validate_mutation_value(spec: MutationSpec, value: Any, field: str) -> None:
    if spec.target_kind in {MutationTargetKind.STATE, MutationTargetKind.FACT}:
        _exact_string(value, field)
        if spec.target == "decision":
            AuthorityOutcome(value)
        return
    if (
        spec.target_kind is MutationTargetKind.RELATION
        and spec.target in {"evidence_binding", "freshness"}
    ):
        if isinstance(value, str):
            _exact_string(value, field)
        elif isinstance(value, Mapping):
            parser = (
                ObservationBinding.from_mapping
                if spec.target == "evidence_binding"
                else ObservationFreshness.from_mapping
            )
            parser(value)
        else:
            raise ValueError(f"{field} must be a typed object or legacy string marker")
        return
    if isinstance(value, str):
        if value not in {FactState.UNKNOWN.value, FactState.CONFLICTING.value}:
            raise ValueError(f"{field} relation marker must be UNKNOWN or CONFLICTING")
        return
    if spec.target_kind is MutationTargetKind.RELATION:
        if not isinstance(value, Mapping):
            raise ValueError(f"{field} must be an object or fact-state marker")
        _validate_relation_mutation_value(spec, value, field)
        return
    if spec.target in {
        "objective_binding",
        "binding_source_authority",
        "binding_lifecycle",
        "contract_transformation_binding",
    }:
        if not isinstance(value, (list, tuple)) or not value:
            raise ValueError(f"{field} must be a non-empty array or fact-state marker")
        if not all(isinstance(item, Mapping) for item in value):
            raise ValueError(f"{field} entries must be objects")
        parsers = {
            "objective_binding": ObjectiveBinding.from_mapping,
            "binding_source_authority": BindingSourceAuthority.from_mapping,
            "binding_lifecycle": BindingLifecycle.from_mapping,
            "contract_transformation_binding": ContractTransformation.from_mapping,
        }
        for item in value:
            parsers[spec.target](item)
        return
    if not isinstance(value, Mapping):
        raise ValueError(f"{field} must be an object or fact-state marker")
    parsers = {
        "objective_identity": ObjectiveIdentity.from_mapping,
        "decision_contract_identity": DecisionContractIdentity.from_mapping,
        "authority_root": AuthorityRoot.from_mapping,
        "binding_ordering": BindingOrdering.from_mapping,
    }
    parsers[spec.target](value)


@dataclass(frozen=True)
class Mutation:
    field: str
    before: Any
    after: Any
    canonical_field: str | None
    target_kind: MutationTargetKind | None
    target: str | None

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "Mutation":
        if not isinstance(value, Mapping):
            raise ValueError("t2.mutations entries must be objects")
        _require_exact_fields(value, {"field", "before", "after"}, "t2.mutations entry")
        field = _exact_string(value["field"], "t2.mutations.field")
        if _MUTATION_FIELD_PATTERN.fullmatch(field) is None:
            raise ValueError("t2.mutations.field must be exact ASCII lower snake case")
        before = value["before"]
        after = value["after"]
        if exact_value_equal(before, after):
            raise ValueError("t2.mutations must describe a change")
        spec = MUTATION_REGISTRY.get(field)
        if spec is not None:
            _validate_mutation_value(spec, before, f"t2.mutations.{field}.before")
            _validate_mutation_value(spec, after, f"t2.mutations.{field}.after")
        return cls(
            field=field,
            before=before,
            after=after,
            canonical_field=spec.canonical_field if spec is not None else None,
            target_kind=spec.target_kind if spec is not None else None,
            target=spec.target if spec is not None else None,
        )


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
    observation_binding: ObservationBinding | None
    observation_freshness: ObservationFreshness | None
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
        raw_mutations = t2["mutations"]
        if not isinstance(raw_mutations, (list, tuple)):
            raise ValueError("t2.mutations must be an array")
        mutations = tuple(Mutation.from_mapping(item) for item in raw_mutations)
        observation_binding = None
        observation_binding_fact = facts.get("evidence_binding")
        if (
            observation_binding_fact is not None
            and observation_binding_fact.state is FactState.KNOWN
            and isinstance(observation_binding_fact.value, Mapping)
        ):
            observation_binding = ObservationBinding.from_mapping(
                observation_binding_fact.value
            )
        elif (
            observation_binding_fact is not None
            and observation_binding_fact.state is FactState.KNOWN
            and not isinstance(observation_binding_fact.value, str)
        ):
            raise ValueError("KNOWN evidence_binding requires a typed object or legacy string")
        observation_freshness = None
        observation_freshness_fact = facts.get("freshness")
        if (
            observation_freshness_fact is not None
            and observation_freshness_fact.state is FactState.KNOWN
            and isinstance(observation_freshness_fact.value, Mapping)
        ):
            observation_freshness = ObservationFreshness.from_mapping(
                observation_freshness_fact.value
            )
        elif (
            observation_freshness_fact is not None
            and observation_freshness_fact.state is FactState.KNOWN
            and not isinstance(observation_freshness_fact.value, str)
        ):
            raise ValueError("KNOWN freshness requires a typed object or legacy string")
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
            observation_binding=observation_binding,
            observation_freshness=observation_freshness,
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
