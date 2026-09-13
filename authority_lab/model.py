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
            subject=str(value["subject"]),
            artifact=str(value["artifact"]),
            control_state=str(value["control_state"]),
            identity_basis=str(value["identity_basis"]),
            boundary_epoch=str(value["boundary_epoch"]),
            decision=AuthorityOutcome(value["decision"]),
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
    t2_creates_authority: bool
    t2_mutations: tuple[Mutation, ...]
    facts: Mapping[str, Fact]
    required_facts: tuple[str, ...]
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
        mutations = tuple(
            Mutation(str(item["field"]), item.get("before"), item.get("after"))
            for item in t2["mutations"]
        )
        return cls(
            case_id=str(fixture["case_id"]),
            authority_tuple=AuthorityTuple.from_mapping(fixture["authority_tuple"]),
            t1_result=AuthorityOutcome(t1["result"]),
            t1_evidence=tuple(str(item) for item in t1["evidence"]),
            t2_creates_authority=creates_authority,
            t2_mutations=mutations,
            facts=facts,
            required_facts=required_facts,
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
