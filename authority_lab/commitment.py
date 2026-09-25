"""Deterministic observation-commitment and durable-checkpoint helpers."""

from __future__ import annotations

import hashlib
from typing import Any, Mapping, Sequence

from .model import ENVELOPE_FIELDS, ObservationSegment


DOMAIN = b"AUTHORITY-LAB-OBSERVATION-COMMITMENT-V1\0"
STATE_DOMAIN = b"AUTHORITY-LAB-COMMITMENT-STATE-V1\0"


def _frame(value: Any) -> bytes:
    if isinstance(value, str):
        raw = value.encode("utf-8")
        return b"s" + str(len(raw)).encode("ascii") + b":" + raw
    if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
        raw = str(value).encode("ascii")
        return b"i" + str(len(raw)).encode("ascii") + b":" + raw
    if isinstance(value, (tuple, list)):
        return b"a" + str(len(value)).encode("ascii") + b":" + b"".join(
            _frame(item) for item in value
        )
    raise ValueError("canonical commitment values must be strings, unsigned integers, or arrays")


def commitment_digest(envelope: Mapping[str, Any], segments: Sequence[ObservationSegment]) -> str:
    """Hash the strict envelope body and exact referenced segments."""
    excluded = {"commitment_digest", "canonical_payload_digest", "signature_evidence_id"}
    body = [(name, envelope[name]) for name in ENVELOPE_FIELDS if name not in excluded]
    # stream_commitment is the backlink to this digest and is excluded to avoid
    # a circular fixed-point requirement; every other strict segment member is committed.
    segment_fields = tuple(
        name for name in ObservationSegment.__dataclass_fields__ if name != "stream_commitment"
    )
    segment_body = [
        tuple(getattr(segment, name) for name in segment_fields)
        for segment in segments
    ]
    encoded = _frame(tuple(tuple(item) for item in body)) + _frame(tuple(segment_body))
    return hashlib.sha256(DOMAIN + encoded).hexdigest()


def state_key_digest(values: Mapping[str, Any]) -> str:
    names = (
        "observation_binding_id", "observation_binding_generation", "source_id",
        "authority_generation", "boundary", "boundary_epoch", "lineage",
        "ordering_source_id", "observer_id", "observer_generation", "stream_id",
        "stream_generation",
    )
    return hashlib.sha256(STATE_DOMAIN + _frame(tuple(values[name] for name in names))).hexdigest()


def verifier_state_digest(checkpoint: Mapping[str, Any]) -> str:
    names = (
        "previous_verifier_state_digest", "verifier_state_id",
        "verifier_state_generation", "head_logical_position", "head_commitment_id",
        "head_commitment_digest", "freshness_challenge_id", "checkpoint_id",
        "checkpoint_generation",
    )
    return hashlib.sha256(STATE_DOMAIN + _frame(tuple(checkpoint[name] for name in names))).hexdigest()
