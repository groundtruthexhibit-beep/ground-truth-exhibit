"""Bounded public data model for Authority Lab v0."""

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
)

RELATIONAL_T3_FACTS = (
    "boundary_epoch_binding",
    "execution_control_binding",
    "consumption_binding",
    "delegation_binding",
    "closure_binding",
)


def _exact_string(value: Any, field: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field} must be a string")
    return value


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
    subject_mode: str

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "AuthorityStateBinding":
        fields = set(TUPLE_FIELDS) | {
            "evidence_id",
            "execution_context",
            "applicable_boundary",
            "grant_id",
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
    case_id: str
    authority_tuple: AuthorityTuple
    t1_result: AuthorityOutcome
    t1_evidence: tuple[str, ...]
    t1_authority_state: AuthorityStateBinding
    t2_creates_authority: bool
    t2_mutations: tuple[Mutation, ...]
    facts: Mapping[str, Fact]
    required_facts: tuple[str, ...]
    required_values: Mapping[str, Any]
    reestablishment_state: FactState
    reestablishment: Reestablishment | None
    prohibition: Prohibition
    applicable_invariants: tuple[str, ...]
    authority_question: str

    @classmethod
    def from_fixture(cls, fixture: Mapping[str, Any]) -> "OracleInput":
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
        mutations = tuple(
            Mutation(
                _exact_string(item["field"], "t2.mutations.field"),
                item.get("before"),
                item.get("after"),
            )
            for item in t2["mutations"]
        )
        return cls(
            case_id=str(fixture["case_id"]),
            authority_tuple=AuthorityTuple.from_mapping(fixture["authority_tuple"]),
            t1_result=AuthorityOutcome(t1["result"]),
            t1_evidence=evidence,
            t1_authority_state=AuthorityStateBinding.from_mapping(t1["authority_state"]),
            t2_creates_authority=creates_authority,
            t2_mutations=mutations,
            facts=facts,
            required_facts=required_facts,
            required_values=required_values,
            reestablishment_state=raw_reestablishment.state,
            reestablishment=reestablishment,
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
