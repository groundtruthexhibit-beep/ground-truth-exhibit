"""PHI disclosure-authority convergence for Authority Lab v1."""
from __future__ import annotations
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any
from .model import AuthorityOutcome, FactState

PHI_BINDING_FACT = "phi_disclosure_binding"
PHI_CONTEXT_KEY = "phi_disclosure_authority_context"

BINDING_FIELDS = frozenset({
    "policy_id", "policy_generation", "subject_scope_id", "subject_id",
    "effect_digest", "information_classes", "recipient_id", "purpose_id",
    "authority_basis_id", "authority_basis_generation", "history_head_id",
    "history_head_generation", "memory_scope_id", "transformation_id",
    "tool_context_id", "effect_attempt_id", "effect_outcome_id", "use_id",
    "execution_event_id",
})

CONTEXT_FIELDS = frozenset({
    "policy_id", "policy_generation", "requirement", "subject_scope_id", "subject_id",
    "authority_basis_id", "authority_basis_generation", "authority_state",
    "recipient_id", "effective_domain_id", "recipient_domain_state", "purpose_id",
    "prohibited_purposes", "prohibited_recipients", "history_head_id",
    "history_head_generation", "history_complete", "history_classes",
    "max_cumulative_classes", "memory_scope_id", "memory_state",
    "transformation_id", "transformation_state", "tool_context_id",
    "effect_attempt_id", "effect_outcome_id", "effect_outcome", "use_id",
    "use_state", "execution_event_id", "effect_digest", "information_classes",
})

@dataclass(frozen=True)
class PHIGateResult:
    outcome: AuthorityOutcome
    code: str
    detail: str
    facts: tuple[str, ...] = (PHI_BINDING_FACT,)

def _result(outcome, code, detail, *facts):
    return PHIGateResult(outcome, code, detail, facts or (PHI_BINDING_FACT,))

def _exact_fields(value: Any, fields: frozenset[str], name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{name} must be an object")
    if set(value) != set(fields):
        raise ValueError(f"{name} must contain exactly {sorted(fields)}")
    return value

def _string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{name} must be a non-empty string")
    return value

def _integer(value: Any, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{name} must be a non-negative integer")
    return value

def _boolean(value: Any, name: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(f"{name} must be boolean")
    return value

def _string_tuple(value: Any, name: str) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        raise ValueError(f"{name} must be an array")
    result = tuple(_string(item, name) for item in value)
    if len(result) != len(set(result)):
        raise ValueError(f"{name} must not contain duplicates")
    if result != tuple(sorted(result, key=lambda item: item.encode("utf-8"))):
        raise ValueError(f"{name} must be canonically sorted")
    return result

def _parse_binding(value: Any) -> dict[str, Any]:
    value = _exact_fields(value, BINDING_FIELDS, "phi_disclosure_binding")
    result = dict(value)
    for name in (
        "policy_id", "subject_scope_id", "subject_id", "effect_digest", "recipient_id",
        "purpose_id", "authority_basis_id", "history_head_id", "memory_scope_id",
        "transformation_id", "tool_context_id", "effect_attempt_id", "effect_outcome_id",
        "use_id", "execution_event_id",
    ):
        result[name] = _string(value[name], f"phi_disclosure_binding.{name}")
    for name in ("policy_generation", "authority_basis_generation", "history_head_generation"):
        result[name] = _integer(value[name], f"phi_disclosure_binding.{name}")
    result["information_classes"] = _string_tuple(value["information_classes"], "phi_disclosure_binding.information_classes")
    return result

def _parse_context(value: Any) -> dict[str, Any]:
    value = _exact_fields(value, CONTEXT_FIELDS, "trusted phi_disclosure_authority_context")
    result = dict(value)
    for name in (
        "policy_id", "requirement", "subject_scope_id", "subject_id", "authority_basis_id",
        "authority_state", "recipient_id", "effective_domain_id", "recipient_domain_state",
        "purpose_id", "history_head_id", "memory_scope_id", "memory_state",
        "transformation_id", "transformation_state", "tool_context_id", "effect_attempt_id",
        "effect_outcome_id", "effect_outcome", "use_id", "use_state", "execution_event_id",
        "effect_digest",
    ):
        result[name] = _string(value[name], f"trusted phi context.{name}")
    for name in ("policy_generation", "authority_basis_generation", "history_head_generation", "max_cumulative_classes"):
        result[name] = _integer(value[name], f"trusted phi context.{name}")
    result["history_complete"] = _boolean(value["history_complete"], "trusted phi context.history_complete")
    for name in ("prohibited_purposes", "prohibited_recipients", "history_classes", "information_classes"):
        result[name] = _string_tuple(value[name], f"trusted phi context.{name}")
    if result["requirement"] not in {"NONE", "REQUIRED"}:
        raise ValueError("trusted phi context.requirement must be NONE or REQUIRED")
    return result

def _find_context(case: Any):
    found = []
    for anchor in case.trusted_anchor_context:
        raw = anchor.get(PHI_CONTEXT_KEY)
        if raw is not None:
            found.append((_parse_context(raw), anchor))
    if not found:
        return None, None
    if len(found) != 1:
        raise ValueError("exactly one trusted PHI disclosure context is required when PHI policy applies")
    return found[0]

def evaluate_phi_disclosure(case: Any) -> PHIGateResult | None:
    fact = case.facts.get(PHI_BINDING_FACT)
    context, anchor = _find_context(case)
    if context is None:
        if fact is None:
            return None
        return _result(AuthorityOutcome.UNAVAILABLE, "PHI_DISCLOSURE_POLICY_UNAVAILABLE", "Candidate PHI disclosure state cannot select protected PHI policy.")
    if context["requirement"] == "NONE":
        if fact is not None:
            return _result(AuthorityOutcome.UNAVAILABLE, "PHI_DISCLOSURE_POLICY_UNAVAILABLE", "Candidate PHI disclosure state is present while protected policy is NONE.")
        return PHIGateResult(AuthorityOutcome.AUTHORIZED, "PHI_DISCLOSURE_NOT_APPLICABLE", "Protected PHI policy is NONE.", ())
    if fact is None or fact.state is FactState.UNKNOWN:
        return _result(AuthorityOutcome.UNAVAILABLE, "PHI_DISCLOSURE_BINDING_UNAVAILABLE", "Required PHI disclosure binding is not established.")
    if fact.state is FactState.CONFLICTING:
        return _result(AuthorityOutcome.UNAVAILABLE, "PHI_DISCLOSURE_BINDING_CONFLICTING", "Required PHI disclosure binding is conflicting.")
    binding = _parse_binding(fact.value)
    exact = (
        "policy_id", "policy_generation", "subject_scope_id", "subject_id", "effect_digest",
        "recipient_id", "authority_basis_id", "authority_basis_generation", "history_head_id",
        "history_head_generation", "effect_attempt_id", "effect_outcome_id", "use_id", "execution_event_id",
    )
    mismatches = tuple(name for name in exact if binding[name] != context[name])
    if mismatches:
        return _result(AuthorityOutcome.UNAVAILABLE, "PHI_T3_CONVERGENCE_UNAVAILABLE", "PHI binding does not match protected current context.", *mismatches)
    if binding["subject_id"] != case.authority_tuple.subject:
        return _result(AuthorityOutcome.UNAVAILABLE, "PHI_SUBJECT_SCOPE_UNAVAILABLE", "PHI subject scope does not match evaluated subject.", "subject_id")
    if tuple(binding["information_classes"]) != tuple(context["information_classes"]):
        return _result(AuthorityOutcome.UNAVAILABLE, "PHI_INFORMATION_CLASS_UNAVAILABLE", "Information classes do not match protected classification.", "information_classes")
    event = anchor.get("t3_execution_event") if anchor is not None else None
    if not isinstance(event, Mapping) or (
        event.get("execution_event_id") != context["execution_event_id"]
        or event.get("execution_event_digest") != context["effect_digest"]
        or event.get("tool_context_id") != context["tool_context_id"]
        or binding["tool_context_id"] != event.get("tool_context_id")
    ):
        return _result(AuthorityOutcome.UNAVAILABLE, "PHI_T3_CONVERGENCE_UNAVAILABLE", "PHI authority does not converge on canonical T3/tool context.", "execution_event_id", "effect_digest", "tool_context_id")
    if binding["purpose_id"] in context["prohibited_purposes"]:
        return _result(AuthorityOutcome.DENIED, "PHI_PURPOSE_PROHIBITED", "Current protected PHI policy prohibits the requested purpose.", "purpose_id")
    if binding["recipient_id"] in context["prohibited_recipients"]:
        return _result(AuthorityOutcome.DENIED, "PHI_RECIPIENT_PROHIBITED", "Current protected PHI policy prohibits the requested recipient.", "recipient_id")
    if context["authority_state"] in {"REVOKED", "REJECTED", "PROHIBITED"}:
        return _result(AuthorityOutcome.DENIED, "PHI_AUTHORITY_REVOKED", "Current protected PHI authority basis is negative.", "authority_basis_id")
    cumulative = set(context["history_classes"]) | set(binding["information_classes"])
    if len(cumulative) > context["max_cumulative_classes"]:
        return _result(AuthorityOutcome.DENIED, "PHI_CUMULATIVE_DISCLOSURE_PROHIBITED", "Current effective-domain disclosure exceeds protected cumulative policy.", "history_head_id", "recipient_id")
    if context["authority_state"] != "ACTIVE":
        return _result(AuthorityOutcome.UNAVAILABLE, "PHI_AUTHORITY_BASIS_UNAVAILABLE", "Current PHI authority basis is not active.", "authority_basis_id")
    if not context["history_complete"]:
        return _result(AuthorityOutcome.UNAVAILABLE, "PHI_HISTORY_UNAVAILABLE", "Current monotonic PHI disclosure history is incomplete.", "history_head_id")
    if context["recipient_domain_state"] != "ACTIVE":
        return _result(AuthorityOutcome.UNAVAILABLE, "PHI_RECIPIENT_DOMAIN_UNAVAILABLE", "Effective recipient domain is unavailable.", "recipient_id")
    if binding["purpose_id"] != context["purpose_id"]:
        return _result(AuthorityOutcome.UNAVAILABLE, "PHI_PURPOSE_UNAVAILABLE", "Requested purpose does not match current admitted purpose.", "purpose_id")
    if binding["memory_scope_id"] != context["memory_scope_id"] or (binding["memory_scope_id"] != "NONE" and context["memory_state"] != "ACTIVE"):
        return _result(AuthorityOutcome.UNAVAILABLE, "PHI_MEMORY_SCOPE_UNAVAILABLE", "Memory/session scope is not currently authorized.", "memory_scope_id")
    if binding["transformation_id"] != context["transformation_id"] or (binding["transformation_id"] != "NONE" and context["transformation_state"] != "ACTIVE"):
        return _result(AuthorityOutcome.UNAVAILABLE, "PHI_TRANSFORMATION_UNAVAILABLE", "Derived disclosure lacks exact current transformation authority.", "transformation_id")
    if context["effect_outcome"] in {"AMBIGUOUS", "IN_FLIGHT"}:
        return _result(AuthorityOutcome.UNAVAILABLE, "PHI_EFFECT_OUTCOME_UNAVAILABLE", "Prior PHI effect outcome is ambiguous or in flight.", "effect_outcome_id")
    if context["effect_outcome"] == "EFFECT_CONFIRMED" and context["use_state"] != "FRESH":
        return _result(AuthorityOutcome.UNAVAILABLE, "PHI_USE_UNAVAILABLE", "Confirmed PHI effect cannot replay stale/consumed use.", "use_id")
    if context["effect_outcome"] not in {"NOT_STARTED", "NON_EFFECT_CONFIRMED", "EFFECT_CONFIRMED"}:
        return _result(AuthorityOutcome.UNAVAILABLE, "PHI_EFFECT_OUTCOME_UNAVAILABLE", "PHI effect outcome is not admitted.", "effect_outcome_id")
    if context["use_state"] not in {"UNUSED", "FRESH"}:
        return _result(AuthorityOutcome.UNAVAILABLE, "PHI_USE_UNAVAILABLE", "PHI terminal use is not currently usable.", "use_id")
    return PHIGateResult(AuthorityOutcome.AUTHORIZED, "PHI_DISCLOSURE_AUTHORITY_ESTABLISHED", "Exact current PHI disclosure authority converges at T3.", (PHI_BINDING_FACT,))
