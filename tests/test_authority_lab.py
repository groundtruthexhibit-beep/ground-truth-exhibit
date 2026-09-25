from __future__ import annotations

import json
import subprocess
import sys
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

from authority_lab.commitment import commitment_digest, state_key_digest, verifier_state_digest
from authority_lab.model import (
    AuthorityOutcome,
    ContinuityEffect,
    FactState,
    HarnessStatus,
    INVARIANTS,
    MANDATORY_T3_FACTS,
    MUTATION_CANONICAL_FIELDS,
    MUTATION_LEGACY_ALIASES,
    MUTATION_REGISTRY,
    MUTATION_SPECS,
    MutationTargetKind,
    OBSERVATION_PROFILE_ID,
    OBSERVATION_PROFILE_VERSION,
    OBSERVATION_SCOPE_FAMILIES,
    ObservationSegment,
    OracleInput,
    RELATIONAL_T3_FACTS,
    TUPLE_FIELDS,
)
from authority_lab.oracle import (
    BINDING_MUTATION_TARGETS,
    FACT_MUTATION_TARGETS,
    RELATIONAL_MUTATION_TARGETS,
    STATE_MUTATION_TARGETS,
    evaluate,
)
from authority_lab.runner import discover, format_trace, load_fixture, run_fixture, run_path


ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "cases" / "authority_lab"


def fixture(case_id: str) -> dict:
    return load_fixture(CASES / f"{case_id}.json")


def actual(payload: dict) -> AuthorityOutcome:
    return evaluate(OracleInput.from_fixture(payload)).outcome


def reissue_observation_commitment(payload: dict) -> None:
    """Reissue the exact test commitment after an authorized scope change."""
    facts = payload["t3"]["facts"]
    binding = facts["evidence_binding"]["value"]
    objective = facts["objective_binding"]["value"][-1]
    envelope = binding["commitment_envelopes"][0]
    envelope.update(
        objective_binding_id=objective["binding_id"],
        objective_binding_generation=objective["binding_generation"],
        decision_contract_id=binding["decision_contract_id"],
        decision_contract_version=binding["decision_contract_version"],
        source_id=binding["source_id"],
        authority_generation=binding["authority_generation"],
        boundary=binding["boundary"],
        boundary_epoch=binding["boundary_epoch"],
        lineage=binding["lineage"],
        ordering_source_id=binding["ordering_source_id"],
    )
    segments = [
        ObservationSegment.from_mapping(item)
        for item in binding["segments"]
        if item["segment_id"] in envelope["segment_ids"]
    ]
    digest = commitment_digest(envelope, segments)
    envelope.update(commitment_digest=digest, canonical_payload_digest=digest)
    for segment in binding["segments"]:
        if segment["segment_id"] in envelope["segment_ids"]:
            segment["stream_commitment"] = digest
    verification = binding["commitment_verifications"][0]
    verification.update(commitment_digest=digest, canonical_payload_digest=digest)
    binding["commitment_links"][0]["to_commitment_digest"] = digest
    checkpoint = binding["commitment_checkpoints"][0]
    checkpoint["head_commitment_digest"] = digest
    checkpoint["current_verifier_state_digest"] = verifier_state_digest(checkpoint)
    facts["freshness"]["value"].update(
        commitment_digest=digest,
        verifier_state_digest=checkpoint["current_verifier_state_digest"],
    )
    context = payload["_trusted_commitment_context"][0]
    context.update(
        exact_state_key_digest=state_key_digest(envelope),
        current_verifier_state_digest=checkpoint["current_verifier_state_digest"],
        head_commitment_digest=digest,
    )


def rebind_objective_binding(payload: dict, *, suffix: str) -> dict:
    """Create exact current binding relations for a changed test authority scope."""
    facts = payload["t3"]["facts"]
    scope = {
        "subject": payload["authority_tuple"]["subject"],
        "artifact": payload["authority_tuple"]["artifact"],
        "control_state": payload["authority_tuple"]["control_state"],
        "identity_basis": payload["authority_tuple"]["identity_basis"],
        "boundary_epoch": payload["authority_tuple"]["boundary_epoch"],
        "decision": payload["authority_tuple"]["decision"],
        "applicable_boundary": facts["applicable_boundary"]["value"],
    }
    before_values = {
        name: deepcopy(facts[name]["value"])
        for name in (
            "objective_binding",
            "binding_source_authority",
            "binding_lifecycle",
            "binding_ordering",
        )
    }
    binding = facts["objective_binding"]["value"][0]
    binding["binding_id"] = f"{binding['binding_id']}-{suffix}"
    binding["scope"] = deepcopy(scope)
    source = facts["binding_source_authority"]["value"][0]
    source["scope"] = deepcopy(scope)
    lifecycle = facts["binding_lifecycle"]["value"][0]
    lifecycle.update(
        {
            "binding_id": binding["binding_id"],
            "event_id": f"{lifecycle['event_id']}-{suffix}",
        }
    )
    facts["binding_ordering"]["value"]["head_binding_id"] = binding["binding_id"]
    for name, before in before_values.items():
        after = deepcopy(facts[name]["value"])
        if before != after:
            payload["t2"]["mutations"].append(
                {"field": name, "before": before, "after": after}
            )
    # Observation admission is independently root-issued, but it must identify
    # the exact current objective binding and decision contract it covers.
    observation = facts["evidence_binding"]["value"]
    freshness = facts["freshness"]["value"]
    observation.update(
        {
            "objective_binding_id": binding["binding_id"],
            "objective_binding_generation": binding["binding_generation"],
            "decision_contract_id": binding["contract_id"],
            "decision_contract_version": binding["contract_version"],
            "source_id": source["root_id"],
            "authority_generation": source["authority_generation"],
            "boundary": source["boundary"],
            "boundary_epoch": source["boundary_epoch"],
            "lineage": source["lineage"],
            "ordering_source_id": facts["binding_ordering"]["value"][
                "ordering_source_id"
            ],
        }
    )
    freshness.update(
        {
            "source_id": source["root_id"],
            "authority_generation": source["authority_generation"],
            "boundary": source["boundary"],
            "boundary_epoch": source["boundary_epoch"],
            "lineage": source["lineage"],
            "ordering_source_id": facts["binding_ordering"]["value"][
                "ordering_source_id"
            ],
        }
    )
    for record in observation["lifecycle_records"]:
        record.update(
            {
                "source_id": source["root_id"],
                "authority_generation": source["authority_generation"],
                "boundary": source["boundary"],
                "boundary_epoch": source["boundary_epoch"],
                "lineage": source["lineage"],
            }
        )
    for segment in observation["segments"]:
        segment["boundary_epoch"] = source["boundary_epoch"]
    reissue_observation_commitment(payload)
    return payload


def reestablish_artifact(
    payload: dict,
    *,
    artifact: str = "A2",
    evidence_id: str = "EV-A2-B1",
    grant_id: str | None = None,
    preserve_grant_transition: bool = False,
) -> dict:
    """Build exact changed-artifact state without deriving authority from expectations."""
    previous = deepcopy(payload["t1"]["authority_state"])
    current_grant = grant_id if grant_id is not None else previous["grant_id"]
    payload["authority_tuple"]["artifact"] = artifact
    payload["t2"]["mutations"].append(
        {"field": "artifact", "before": previous["artifact"], "after": artifact}
    )
    if current_grant != previous["grant_id"]:
        payload["t2"]["mutations"].append(
            {
                "field": "grant_id",
                "before": previous["grant_id"],
                "after": current_grant,
            }
        )
    payload["t3"]["facts"]["artifact_identity"]["value"] = artifact
    payload["t3"]["required_values"]["artifact_identity"] = artifact
    payload["t3"]["facts"]["decision_binding"]["value"] = evidence_id
    payload["t3"]["required_values"]["decision_binding"] = evidence_id
    payload["t3"]["facts"]["consumption_binding"]["value"].update(
        {"grant_id": current_grant, "artifact": artifact}
    )
    payload["t3"]["facts"]["delegation_binding"]["value"]["artifact"] = artifact
    payload["t3"]["facts"]["closure_binding"]["value"].update(
        {"source_artifact": artifact, "target_artifact": artifact}
    )
    current = deepcopy(previous)
    current.update(
        {
            "artifact": artifact,
            "evidence_id": evidence_id,
            "grant_id": current_grant,
            "consumption_state": payload["t3"]["facts"]["consumption_state"]["value"],
        }
    )
    payload["t3"]["reestablishment"] = {
        "state": "KNOWN",
        "value": {"previous_evidence_id": previous["evidence_id"], "current": current},
    }
    if preserve_grant_transition:
        payload["t3"]["grant_transition"] = {
            "state": "KNOWN",
            "value": {
                "relationship": "AUTHORITY_PRESERVING",
                "grant_path": [
                    previous["grant_id"],
                    *(
                        mutation["after"]
                        for mutation in payload["t2"]["mutations"]
                        if mutation["field"] == "grant_id"
                    ),
                ]
                if current_grant != previous["grant_id"]
                else [previous["grant_id"], previous["grant_id"]],
                "previous": previous,
                "current": deepcopy(current),
            },
        }
    rebind_objective_binding(payload, suffix="CURRENT-SCOPE")
    return payload


def reestablish_grant(
    payload: dict,
    *,
    grant_id: str = "G2",
    evidence_id: str = "EV-G2",
    include_transition: bool = False,
) -> dict:
    previous = deepcopy(payload["t1"]["authority_state"])
    payload["t2"]["mutations"].append(
        {"field": "grant_id", "before": previous["grant_id"], "after": grant_id}
    )
    payload["t3"]["facts"]["decision_binding"]["value"] = evidence_id
    payload["t3"]["required_values"]["decision_binding"] = evidence_id
    payload["t3"]["facts"]["consumption_binding"]["value"]["grant_id"] = grant_id
    current = deepcopy(previous)
    current.update({"grant_id": grant_id, "evidence_id": evidence_id})
    payload["t3"]["reestablishment"] = {
        "state": "KNOWN",
        "value": {"previous_evidence_id": previous["evidence_id"], "current": current},
    }
    if include_transition:
        payload["t3"]["grant_transition"] = {
            "state": "KNOWN",
            "value": {
                "relationship": "AUTHORITY_PRESERVING",
                "grant_path": [previous["grant_id"], grant_id],
                "previous": previous,
                "current": deepcopy(current),
            },
        }
    return payload


class AuthorityLabTests(unittest.TestCase):
    def assert_unavailable_with_reason(self, payload: dict, reason_code: str) -> None:
        result = evaluate(OracleInput.from_fixture(payload))
        self.assertIs(AuthorityOutcome.UNAVAILABLE, result.outcome)
        self.assertIn(reason_code, {reason.code for reason in result.reasons})

    def test_v1_contains_one_hundred_twelve_deterministic_fixtures(self) -> None:
        paths = discover(CASES)
        self.assertEqual(112, len(paths))
        self.assertEqual(paths, discover(CASES))

    def test_every_v0_fixture_matches_its_expected_outcome(self) -> None:
        results = [run_path(path) for path in discover(CASES)]
        self.assertTrue(all(result.status is HarnessStatus.PASS for result in results))

    def test_fresh_positive_is_authorized(self) -> None:
        self.assertIs(AuthorityOutcome.AUTHORIZED, actual(fixture("LAB-V0-001")))

    def test_second_fresh_positive_is_authorized(self) -> None:
        self.assertIs(AuthorityOutcome.AUTHORIZED, actual(fixture("LAB-V0-010")))

    def test_established_prohibition_is_denied(self) -> None:
        self.assertIs(AuthorityOutcome.DENIED, actual(fixture("LAB-V0-002")))

    def test_missing_required_fact_is_unavailable(self) -> None:
        payload = fixture("LAB-V0-001")
        del payload["t3"]["facts"]["applicable_boundary"]
        self.assertIs(AuthorityOutcome.UNAVAILABLE, actual(payload))

    def test_conflicting_required_fact_is_unavailable(self) -> None:
        self.assertIs(AuthorityOutcome.UNAVAILABLE, actual(fixture("LAB-V0-004")))

    def test_unknown_is_not_converted_to_denied(self) -> None:
        payload = fixture("LAB-V0-003")
        payload["t3"]["prohibition"] = {
            "state": FactState.UNKNOWN.value,
            "id": "not-established",
        }
        self.assertIs(AuthorityOutcome.UNAVAILABLE, actual(payload))

    def test_stale_t1_authorized_does_not_survive_t3(self) -> None:
        self.assertIs(AuthorityOutcome.UNAVAILABLE, actual(fixture("LAB-V0-007")))

    def test_t2_cannot_create_authority(self) -> None:
        payload = fixture("LAB-V0-001")
        payload["t1"]["result"] = AuthorityOutcome.UNAVAILABLE.value
        payload["authority_tuple"]["decision"] = AuthorityOutcome.UNAVAILABLE.value
        payload["t2"]["creates_authority"] = True
        self.assertIs(AuthorityOutcome.UNAVAILABLE, actual(payload))

    def test_t2_authority_claim_invalidates_otherwise_authorized_input(self) -> None:
        payload = fixture("LAB-V0-001")
        payload["t2"]["creates_authority"] = True
        self.assert_unavailable_with_reason(payload, "T2_AUTHORITY_CLAIM")

    def test_consumed_value_cannot_authorize(self) -> None:
        payload = fixture("LAB-V0-001")
        payload["t3"]["facts"]["consumption_state"]["value"] = "CONSUMED"
        self.assert_unavailable_with_reason(payload, "REQUIRED_VALUE_MISMATCH")

    def test_stale_freshness_cannot_authorize(self) -> None:
        payload = fixture("LAB-V0-001")
        payload["t3"]["facts"]["freshness"]["value"] = "STALE"
        self.assert_unavailable_with_reason(payload, "OBSERVATION_FRESHNESS_UNAVAILABLE")

    def test_wrong_evidence_binding_cannot_authorize(self) -> None:
        payload = fixture("LAB-V0-001")
        payload["t3"]["facts"]["evidence_binding"]["value"] = "STALE"
        self.assert_unavailable_with_reason(payload, "OBSERVATION_ADMISSION_UNAVAILABLE")

    def test_changed_execution_context_cannot_authorize_without_rebinding(self) -> None:
        payload = fixture("LAB-V0-001")
        payload["t3"]["facts"]["execution_context"]["value"] = "E2"
        self.assert_unavailable_with_reason(payload, "REQUIRED_VALUE_MISMATCH")

    def test_wrong_applicable_boundary_cannot_authorize(self) -> None:
        payload = fixture("LAB-V0-001")
        payload["t3"]["facts"]["applicable_boundary"]["value"] = "OTHER-BOUNDARY"
        self.assert_unavailable_with_reason(payload, "REQUIRED_VALUE_MISMATCH")

    def test_wrong_decision_binding_cannot_authorize(self) -> None:
        payload = fixture("LAB-V0-001")
        payload["t3"]["facts"]["decision_binding"]["value"] = "OTHER"
        self.assert_unavailable_with_reason(payload, "REQUIRED_VALUE_MISMATCH")

    def test_unrelated_delegation_binding_cannot_authorize(self) -> None:
        payload = fixture("LAB-V0-010")
        payload["t3"]["facts"]["delegation_binding"]["value"] = "UNRELATED"
        self.assert_unavailable_with_reason(payload, "DELEGATION_RELATIONSHIP_UNAVAILABLE")

    def test_implicit_closure_cannot_authorize(self) -> None:
        payload = fixture("LAB-V0-010")
        payload["t3"]["facts"]["closure_binding"]["value"] = "IMPLICIT"
        self.assert_unavailable_with_reason(payload, "CLOSURE_RELATIONSHIP_UNAVAILABLE")

    def test_fixture_cannot_remove_any_mandatory_t3_fact(self) -> None:
        for field in MANDATORY_T3_FACTS:
            with self.subTest(field=field):
                payload = fixture("LAB-V0-001")
                if field in payload["t3"]["required_facts"]:
                    payload["t3"]["required_facts"].remove(field)
                payload["t3"]["facts"][field] = {"state": "UNKNOWN"}
                self.assert_unavailable_with_reason(payload, "REQUIRED_FACT_UNAVAILABLE")

    def test_missing_required_value_cannot_authorize(self) -> None:
        payload = fixture("LAB-V0-001")
        del payload["t3"]["required_values"]["execution_context"]
        self.assert_unavailable_with_reason(payload, "REQUIRED_VALUE_UNSPECIFIED")

    def test_fixture_required_values_cannot_launder_nonpermitting_core_values(self) -> None:
        for field, value in (("consumption_state", "CONSUMED"),):
            with self.subTest(field=field):
                payload = fixture("LAB-V0-001")
                payload["t3"]["facts"][field]["value"] = value
                payload["t3"]["required_values"][field] = value
                self.assert_unavailable_with_reason(payload, "VALUE_NOT_AUTHORITY_PERMITTING")

    def test_every_fixture_specifies_the_mandatory_authority_values(self) -> None:
        for path in discover(CASES):
            with self.subTest(path=path.name):
                payload = load_fixture(path)
                self.assertTrue(
                    (set(MANDATORY_T3_FACTS) - set(RELATIONAL_T3_FACTS)).issubset(
                        payload["t3"]["required_values"]
                    )
                )
                self.assertTrue(
                    (set(payload["t3"]["required_facts"]) - set(RELATIONAL_T3_FACTS)).issubset(
                        payload["t3"]["required_values"]
                    )
                )

    def test_wrong_expectation_does_not_change_actual(self) -> None:
        payload = fixture("LAB-V0-001")
        payload["expected_outcome"] = AuthorityOutcome.DENIED.value
        result = run_fixture(payload)
        self.assertIs(AuthorityOutcome.AUTHORIZED, result.actual.outcome)
        self.assertIs(HarnessStatus.CASE_MISMATCH, result.status)

    def test_harness_status_is_not_an_authority_outcome(self) -> None:
        self.assertTrue(set(AuthorityOutcome).isdisjoint(set(HarnessStatus)))
        self.assertEqual(
            {"AUTHORIZED", "DENIED", "UNAVAILABLE"},
            {outcome.value for outcome in AuthorityOutcome},
        )

    def test_labels_titles_and_expectation_do_not_change_oracle(self) -> None:
        payload = fixture("LAB-V0-003")
        baseline = actual(payload)
        changed = deepcopy(payload)
        changed["case_id"] = "MISLEADING-AUTHORIZED-LABEL"
        changed["title"] = "Everything is authorized"
        changed["expected_outcome"] = AuthorityOutcome.AUTHORIZED.value
        self.assertIs(baseline, actual(changed))

    def test_derivative_and_aggregate_artifacts_do_not_inherit_authority(self) -> None:
        self.assertIs(AuthorityOutcome.UNAVAILABLE, actual(fixture("LAB-V0-011")))
        self.assertIs(AuthorityOutcome.UNAVAILABLE, actual(fixture("LAB-V0-012")))

    def test_delegated_actor_requires_explicit_current_binding(self) -> None:
        payload = fixture("LAB-V0-010")
        payload["t3"]["facts"]["delegation_binding"] = {"state": "UNKNOWN"}
        self.assertIs(AuthorityOutcome.UNAVAILABLE, actual(payload))

    def test_one_shot_consumption_uncertainty_does_not_regenerate_authority(self) -> None:
        self.assertIs(AuthorityOutcome.UNAVAILABLE, actual(fixture("LAB-V0-009")))

    def test_known_one_shot_consumption_is_denied(self) -> None:
        self.assertIs(AuthorityOutcome.DENIED, actual(fixture("LAB-V0-008")))

    def test_flagship_escape_three_way_derivation(self) -> None:
        unknown = fixture("LAB-V0-003")
        self.assertIs(AuthorityOutcome.UNAVAILABLE, actual(unknown))

        denied = deepcopy(unknown)
        denied["authority_tuple"]["control_state"] = "E2"
        denied["t3"]["facts"]["execution_context"] = {"state": "KNOWN", "value": "E2"}
        denied["t3"]["facts"]["boundary_continuity"] = {"state": "KNOWN", "value": "ESTABLISHED"}
        denied["t3"]["required_values"]["control_state"] = "E2"
        denied["t3"]["required_values"]["execution_context"] = "E2"
        denied["t3"]["facts"]["execution_control_binding"] = {
            "state": "KNOWN",
            "value": {"execution_context": "E2", "control_state": "E2"},
        }
        denied["t3"]["prohibition"] = {
            "state": "KNOWN",
            "applies": True,
            "id": "E2_EXECUTION_PROHIBITED",
        }
        self.assertIs(AuthorityOutcome.DENIED, actual(denied))

        authorized = fixture("LAB-V1-084")
        self.assertIs(AuthorityOutcome.AUTHORIZED, actual(authorized))

    def test_exact_tuple_and_invariant_sets_are_frozen(self) -> None:
        self.assertEqual(
            ("subject", "artifact", "control_state", "identity_basis", "boundary_epoch", "decision"),
            TUPLE_FIELDS,
        )
        self.assertEqual(
            ("INV-CONT", "INV-DISC", "INV-BND", "INV-EVD", "INV-USE", "INV-CLO"),
            INVARIANTS,
        )
        self.assertEqual(23, len(MANDATORY_T3_FACTS))

    def test_artifact_rebinding_cannot_reuse_old_evidence(self) -> None:
        payload = fixture("LAB-V0-001")
        payload["authority_tuple"]["artifact"] = "A2"
        payload["t3"]["facts"]["artifact_identity"]["value"] = "A2"
        payload["t3"]["required_values"]["artifact_identity"] = "A2"
        self.assert_unavailable_with_reason(payload, "T1_T3_RELATIONSHIP_UNAVAILABLE")

    def test_execution_hybrid_cannot_be_laundered_by_required_values(self) -> None:
        payload = fixture("LAB-V0-001")
        payload["t2"]["mutations"].append(
            {"field": "execution_context", "before": "E1", "after": "E2"}
        )
        payload["t3"]["facts"]["execution_context"]["value"] = "E2"
        payload["t3"]["required_values"]["execution_context"] = "E2"
        payload["t3"]["facts"]["execution_control_binding"]["value"][
            "execution_context"
        ] = "E2"
        self.assert_unavailable_with_reason(payload, "T1_T3_RELATIONSHIP_UNAVAILABLE")

    def test_derived_artifact_cannot_inherit_generic_closure(self) -> None:
        payload = fixture("LAB-V0-010")
        payload["authority_tuple"]["artifact"] = "REPORT-Z"
        payload["t3"]["facts"]["artifact_identity"]["value"] = "REPORT-Z"
        payload["t3"]["required_values"]["artifact_identity"] = "REPORT-Z"
        self.assert_unavailable_with_reason(payload, "T1_T3_RELATIONSHIP_UNAVAILABLE")

    def test_generic_explicit_token_is_not_relational_closure(self) -> None:
        payload = fixture("LAB-V0-010")
        payload["t3"]["facts"]["closure_binding"]["value"] = "EXPLICIT"
        payload["t3"]["required_values"]["closure_binding"] = "EXPLICIT"
        self.assert_unavailable_with_reason(payload, "CLOSURE_RELATIONSHIP_UNAVAILABLE")

    def test_boundary_must_be_relationally_bound_to_epoch(self) -> None:
        payload = fixture("LAB-V0-001")
        payload["t3"]["facts"]["applicable_boundary"]["value"] = "AUTH-BOUNDARY-2"
        payload["t3"]["required_values"]["applicable_boundary"] = "AUTH-BOUNDARY-2"
        self.assert_unavailable_with_reason(
            payload, "BOUNDARY_EPOCH_RELATIONSHIP_UNAVAILABLE"
        )

    def test_delegation_must_bind_exact_subject_and_artifact(self) -> None:
        payload = fixture("LAB-V0-010")
        payload["t3"]["facts"]["delegation_binding"]["value"]["delegate"] = "OTHER"
        payload["t3"]["required_values"]["delegation_binding"]["delegate"] = "OTHER"
        self.assert_unavailable_with_reason(payload, "DELEGATION_RELATIONSHIP_UNAVAILABLE")

    def test_control_state_cannot_form_hybrid_with_old_execution_context(self) -> None:
        payload = fixture("LAB-V0-001")
        payload["authority_tuple"]["control_state"] = "C2"
        payload["t3"]["facts"]["control_state"]["value"] = "C2"
        payload["t3"]["required_values"]["control_state"] = "C2"
        payload["t3"]["facts"]["execution_control_binding"]["value"]["control_state"] = (
            "C2"
        )
        self.assert_unavailable_with_reason(payload, "T1_T3_RELATIONSHIP_UNAVAILABLE")

    def test_empty_required_identity_is_unavailable(self) -> None:
        payload = fixture("LAB-V0-001")
        payload["authority_tuple"]["subject"] = ""
        payload["t3"]["facts"]["subject_identity"]["value"] = ""
        payload["t3"]["required_values"]["subject_identity"] = ""
        self.assert_unavailable_with_reason(payload, "INVALID_IDENTITY_VALUE")

    def test_identity_comparison_does_not_trim_or_normalize(self) -> None:
        payload = fixture("LAB-V0-001")
        payload["authority_tuple"]["subject"] = " S"
        payload["t3"]["facts"]["subject_identity"]["value"] = " S"
        payload["t3"]["required_values"]["subject_identity"] = " S"
        self.assert_unavailable_with_reason(payload, "T1_T3_RELATIONSHIP_UNAVAILABLE")

    def test_identity_numbers_are_not_coerced_to_strings(self) -> None:
        payload = fixture("LAB-V0-001")
        payload["authority_tuple"]["subject"] = 7
        with self.assertRaises(ValueError):
            OracleInput.from_fixture(payload)

    def test_t2_mutation_chain_cannot_disappear_at_t3(self) -> None:
        payload = fixture("LAB-V0-001")
        payload["t2"]["mutations"].append(
            {"field": "execution_context", "before": "E1", "after": "E2"}
        )
        self.assert_unavailable_with_reason(payload, "T2_T3_HYBRID_STATE")

    def test_old_grant_cannot_retarget_changed_artifact(self) -> None:
        payload = reestablish_artifact(fixture("LAB-V0-001"))
        self.assert_unavailable_with_reason(
            payload, "GRANT_EFFECT_RELATIONSHIP_UNAVAILABLE"
        )

    def test_fresh_evidence_does_not_retarget_old_grant(self) -> None:
        payload = reestablish_artifact(
            fixture("LAB-V0-001"), evidence_id="FRESH-EVIDENCE-FOR-A2"
        )
        self.assert_unavailable_with_reason(
            payload, "GRANT_EFFECT_RELATIONSHIP_UNAVAILABLE"
        )

    def test_required_values_cannot_launder_old_grant_for_new_effect(self) -> None:
        payload = reestablish_artifact(fixture("LAB-V0-001"))
        self.assertEqual("A2", payload["t3"]["required_values"]["artifact_identity"])
        self.assert_unavailable_with_reason(
            payload, "GRANT_EFFECT_RELATIONSHIP_UNAVAILABLE"
        )

    def test_full_state_reestablishment_does_not_retarget_old_grant(self) -> None:
        payload = reestablish_artifact(fixture("LAB-V0-001"))
        self.assertEqual(
            "A2", payload["t3"]["reestablishment"]["value"]["current"]["artifact"]
        )
        self.assert_unavailable_with_reason(
            payload, "GRANT_EFFECT_RELATIONSHIP_UNAVAILABLE"
        )

    def test_consumed_grant_cannot_reset_when_effect_changes(self) -> None:
        payload = reestablish_artifact(fixture("LAB-V0-001"))
        payload["t2"]["mutations"].extend(
            [
                {"field": "consumption", "before": "UNUSED", "after": "CONSUMED"},
                {"field": "consumption", "before": "CONSUMED", "after": "UNUSED"},
            ]
        )
        self.assert_unavailable_with_reason(
            payload, "CONSUMPTION_CONTINUITY_UNAVAILABLE"
        )

    def test_restart_does_not_retarget_old_grant_to_new_effect(self) -> None:
        payload = reestablish_artifact(fixture("LAB-V0-001"))
        payload["t2"]["mutations"].append(
            {"field": "execution_context", "before": "E1", "after": "E2"}
        )
        payload["t3"]["facts"]["execution_context"]["value"] = "E2"
        payload["t3"]["required_values"]["execution_context"] = "E2"
        payload["t3"]["facts"]["execution_control_binding"]["value"][
            "execution_context"
        ] = "E2"
        payload["t3"]["reestablishment"]["value"]["current"][
            "execution_context"
        ] = "E2"
        self.assert_unavailable_with_reason(
            payload, "PREDECESSOR_GRANT_NONPORTABLE"
        )

    def test_delegation_cannot_retarget_old_grant(self) -> None:
        payload = reestablish_artifact(
            fixture("LAB-V0-010"), artifact="REPORT-Z", evidence_id="EV-REPORT-Z"
        )
        self.assert_unavailable_with_reason(
            payload, "GRANT_EFFECT_RELATIONSHIP_UNAVAILABLE"
        )

    def test_exact_closure_cannot_retarget_old_grant(self) -> None:
        payload = reestablish_artifact(fixture("LAB-V0-001"))
        self.assertEqual(
            {"relationship": "EXACT_EFFECT", "source_artifact": "A2", "target_artifact": "A2"},
            payload["t3"]["facts"]["closure_binding"]["value"],
        )
        self.assert_unavailable_with_reason(
            payload, "GRANT_EFFECT_RELATIONSHIP_UNAVAILABLE"
        )

    def test_unchanged_effect_with_exact_grant_remains_authorized(self) -> None:
        self.assertIs(AuthorityOutcome.AUTHORIZED, actual(fixture("LAB-V0-001")))

    def test_changed_effect_with_distinct_exact_grant_can_authorize(self) -> None:
        payload = reestablish_artifact(
            fixture("LAB-V0-001"), grant_id="GRANT-A2"
        )
        self.assertIs(AuthorityOutcome.AUTHORIZED, actual(payload))

    def test_changed_effect_with_exact_grant_transition_can_authorize(self) -> None:
        payload = reestablish_artifact(
            fixture("LAB-V0-001"), preserve_grant_transition=True
        )
        self.assertIs(AuthorityOutcome.AUTHORIZED, actual(payload))

    def test_grant_transition_must_match_exact_previous_and_current_states(self) -> None:
        payload = reestablish_artifact(
            fixture("LAB-V0-001"), preserve_grant_transition=True
        )
        payload["t3"]["grant_transition"]["value"]["previous"]["artifact"] = "OTHER"
        self.assert_unavailable_with_reason(
            payload, "GRANT_TRANSITION_RELATIONSHIP_UNAVAILABLE"
        )

    def test_compound_transition_cannot_reset_consumption_across_epoch(self) -> None:
        payload = reestablish_artifact(
            fixture("LAB-V0-001"), preserve_grant_transition=True
        )
        payload["t2"]["mutations"].extend(
            [
                {"field": "boundary_epoch", "before": "B1", "after": "B2"},
                {"field": "consumption", "before": "UNUSED", "after": "CONSUMED"},
                {"field": "consumption", "before": "CONSUMED", "after": "UNUSED"},
            ]
        )
        payload["authority_tuple"]["boundary_epoch"] = "B2"
        payload["t3"]["facts"]["boundary_epoch"]["value"] = "B2"
        payload["t3"]["required_values"]["boundary_epoch"] = "B2"
        payload["t3"]["facts"]["boundary_epoch_binding"]["value"][
            "boundary_epoch"
        ] = "B2"
        payload["t3"]["facts"]["consumption_binding"]["value"][
            "boundary_epoch"
        ] = "B2"
        payload["t3"]["facts"]["delegation_binding"]["value"][
            "boundary_epoch"
        ] = "B2"
        current = payload["t3"]["reestablishment"]["value"]["current"]
        current["boundary_epoch"] = "B2"
        payload["t3"]["grant_transition"]["value"]["current"] = deepcopy(current)
        self.assert_unavailable_with_reason(
            payload, "CONSUMPTION_CONTINUITY_UNAVAILABLE"
        )

    def test_disappearing_grant_mutation_is_unavailable(self) -> None:
        payload = fixture("LAB-V0-001")
        payload["t2"]["mutations"].append(
            {"field": "grant_id", "before": "GRANT-001", "after": "G2"}
        )
        self.assert_unavailable_with_reason(payload, "T2_T3_HYBRID_STATE")

    def test_persisting_grant_mutation_with_current_authority_can_authorize(self) -> None:
        payload = reestablish_grant(fixture("LAB-V0-001"))
        self.assertIs(AuthorityOutcome.AUTHORIZED, actual(payload))

    def test_grant_mutation_cannot_resolve_to_unrecorded_third_grant(self) -> None:
        payload = reestablish_grant(fixture("LAB-V0-001"))
        payload["t3"]["facts"]["consumption_binding"]["value"]["grant_id"] = "G3"
        payload["t3"]["reestablishment"]["value"]["current"]["grant_id"] = "G3"
        self.assert_unavailable_with_reason(payload, "T2_T3_HYBRID_STATE")

    def test_disappearing_grant_mutation_after_restart_is_unavailable(self) -> None:
        payload = fixture("LAB-V0-001")
        payload["t2"]["mutations"].extend(
            [
                {"field": "grant_id", "before": "GRANT-001", "after": "G2"},
                {"field": "execution_context", "before": "E1", "after": "E2"},
            ]
        )
        payload["t3"]["facts"]["execution_context"]["value"] = "E2"
        payload["t3"]["required_values"]["execution_context"] = "E2"
        payload["t3"]["facts"]["execution_control_binding"]["value"][
            "execution_context"
        ] = "E2"
        self.assert_unavailable_with_reason(payload, "T2_T3_HYBRID_STATE")

    def test_grant_and_artifact_mutations_require_both_current_bindings(self) -> None:
        payload = reestablish_artifact(
            fixture("LAB-V0-001"), grant_id="G2", evidence_id="EV-A2-G2"
        )
        self.assertIs(AuthorityOutcome.AUTHORIZED, actual(payload))
        payload["t3"]["facts"]["consumption_binding"]["value"]["grant_id"] = "G3"
        payload["t3"]["reestablishment"]["value"]["current"]["grant_id"] = "G3"
        self.assert_unavailable_with_reason(payload, "T2_T3_HYBRID_STATE")

    def test_grant_mutation_cannot_hide_consumption(self) -> None:
        payload = reestablish_grant(fixture("LAB-V0-001"))
        payload["t2"]["mutations"].append(
            {"field": "consumption", "before": "UNUSED", "after": "CONSUMED"}
        )
        self.assert_unavailable_with_reason(payload, "T2_T3_HYBRID_STATE")

    def test_exact_grant_transition_can_establish_g1_to_g2(self) -> None:
        payload = reestablish_grant(
            fixture("LAB-V0-001"), include_transition=True
        )
        self.assertIs(AuthorityOutcome.AUTHORIZED, actual(payload))

    def test_exact_grant_transition_cannot_erase_explicit_return_path(self) -> None:
        payload = reestablish_grant(
            fixture("LAB-V0-001"), grant_id="GRANT-001", evidence_id="EV-G1-RETURN"
        )
        payload["t2"]["mutations"] = [
            {"field": "grant_id", "before": "GRANT-001", "after": "G2"},
            {"field": "grant_id", "before": "G2", "after": "GRANT-001"},
        ]
        previous = deepcopy(payload["t1"]["authority_state"])
        current = deepcopy(payload["t3"]["reestablishment"]["value"]["current"])
        payload["t3"]["grant_transition"] = {
            "state": "KNOWN",
            "value": {
                "relationship": "AUTHORITY_PRESERVING",
                "grant_path": ["GRANT-001", "G2", "GRANT-001"],
                "previous": previous,
                "current": current,
            },
        }
        self.assert_unavailable_with_reason(payload, "PREDECESSOR_GRANT_NONPORTABLE")

    def test_disappearing_decision_binding_mutation_is_unavailable(self) -> None:
        payload = fixture("LAB-V0-001")
        payload["t2"]["mutations"].append(
            {"field": "decision_binding", "before": "EV-A-B1", "after": "EV-OTHER"}
        )
        self.assert_unavailable_with_reason(payload, "T2_T3_HYBRID_STATE")

    def test_disappearing_delegation_mutation_is_unavailable(self) -> None:
        payload = fixture("LAB-V0-010")
        before = deepcopy(payload["t3"]["facts"]["delegation_binding"]["value"])
        after = deepcopy(before)
        after["delegate"] = "OTHER"
        payload["t2"]["mutations"].append(
            {"field": "delegation_binding", "before": before, "after": after}
        )
        self.assert_unavailable_with_reason(payload, "T2_T3_HYBRID_STATE")

    def test_disappearing_subject_mode_mutation_is_unavailable(self) -> None:
        payload = fixture("LAB-V0-001")
        payload["t2"]["mutations"].append(
            {"field": "subject_mode", "before": "DIRECT", "after": "DELEGATED"}
        )
        self.assert_unavailable_with_reason(payload, "T2_T3_HYBRID_STATE")

    def test_disappearing_closure_mutation_is_unavailable(self) -> None:
        payload = fixture("LAB-V0-001")
        before = deepcopy(payload["t3"]["facts"]["closure_binding"]["value"])
        after = deepcopy(before)
        after["target_artifact"] = "OTHER"
        payload["t2"]["mutations"].append(
            {"field": "closure_binding", "before": before, "after": after}
        )
        self.assert_unavailable_with_reason(payload, "T2_T3_HYBRID_STATE")

    def test_tuple_mismatch_is_unavailable(self) -> None:
        payload = fixture("LAB-V0-001")
        payload["t3"]["facts"]["artifact_identity"]["value"] = "OTHER"
        self.assertIs(AuthorityOutcome.UNAVAILABLE, actual(payload))

    def test_every_maintained_fixture_is_migrated_to_v1(self) -> None:
        for path in discover(CASES):
            with self.subTest(path=path.name):
                self.assertEqual("authority-lab-v1", load_fixture(path)["schema_version"])

    def test_unmigrated_v0_schema_cannot_authorize(self) -> None:
        payload = fixture("LAB-V0-001")
        payload["schema_version"] = "authority-lab-v0"
        self.assert_unavailable_with_reason(payload, "LEGACY_SCHEMA_UNAVAILABLE")

    def test_unknown_schema_version_fails_closed(self) -> None:
        payload = fixture("LAB-V0-001")
        payload["schema_version"] = "authority-lab-v2"
        with self.assertRaisesRegex(ValueError, "unsupported fixture schema_version"):
            OracleInput.from_fixture(payload)

    def test_binding_valid_shortcut_is_rejected(self) -> None:
        payload = fixture("LAB-V1-032")
        payload["t3"]["facts"]["objective_binding"]["value"][0][
            "binding_valid"
        ] = True
        with self.assertRaisesRegex(ValueError, "objective_binding candidate"):
            OracleInput.from_fixture(payload)

    def test_boolean_generation_is_rejected(self) -> None:
        payload = fixture("LAB-V1-032")
        payload["t3"]["facts"]["objective_binding"]["value"][0][
            "binding_generation"
        ] = True
        with self.assertRaisesRegex(ValueError, "non-negative integer"):
            OracleInput.from_fixture(payload)

    def test_missing_binding_is_unavailable(self) -> None:
        self.assertIs(AuthorityOutcome.UNAVAILABLE, actual(fixture("LAB-V1-013")))

    def test_unknown_binding_source_authority_is_unavailable(self) -> None:
        self.assertIs(AuthorityOutcome.UNAVAILABLE, actual(fixture("LAB-V1-014")))

    def test_unordered_binding_conflict_is_unavailable(self) -> None:
        self.assertIs(AuthorityOutcome.UNAVAILABLE, actual(fixture("LAB-V1-015")))

    def test_revoked_binding_is_denied(self) -> None:
        self.assertIs(AuthorityOutcome.DENIED, actual(fixture("LAB-V1-016")))

    def test_superseding_rejection_is_denied(self) -> None:
        self.assertIs(AuthorityOutcome.DENIED, actual(fixture("LAB-V1-017")))

    def test_t1_binding_revoked_at_t2_is_denied_at_t3(self) -> None:
        payload = fixture("LAB-V1-018")
        self.assertTrue(
            any(mutation["field"] == "binding_lifecycle" for mutation in payload["t2"]["mutations"])
        )
        self.assertIs(AuthorityOutcome.DENIED, actual(payload))

    def test_binding_producers_cannot_establish_source_authority(self) -> None:
        for case_id in ("LAB-V1-019", "LAB-V1-020", "LAB-V1-021"):
            with self.subTest(case_id=case_id):
                self.assertIs(AuthorityOutcome.UNAVAILABLE, actual(fixture(case_id)))

    def test_verifier_pass_without_binding_is_unavailable(self) -> None:
        self.assertIs(AuthorityOutcome.UNAVAILABLE, actual(fixture("LAB-V1-022")))

    def test_signature_does_not_establish_source_authority(self) -> None:
        payload = fixture("LAB-V1-023")
        self.assertEqual("VALID", payload["t3"]["facts"]["signature"]["value"])
        self.assertIs(AuthorityOutcome.UNAVAILABLE, actual(payload))

    def test_provenance_and_consensus_do_not_launder_source_authority(self) -> None:
        payload = fixture("LAB-V1-014")
        payload["t3"]["facts"].update(
            {
                "provenance": {"state": "KNOWN", "value": "EXACT"},
                "consensus": {"state": "KNOWN", "value": "UNANIMOUS"},
            }
        )
        self.assertIs(AuthorityOutcome.UNAVAILABLE, actual(payload))

    def test_model_producer_cannot_launder_an_authorized_root_identity(self) -> None:
        payload = fixture("LAB-V1-032")
        candidate = payload["t3"]["facts"]["objective_binding"]["value"][0]
        before = deepcopy(payload["t3"]["facts"]["objective_binding"]["value"])
        candidate["producer_kind"] = "MODEL"
        candidate["producer_id"] = "MODEL-M"
        payload["t2"]["mutations"].append(
            {
                "field": "objective_binding",
                "before": before,
                "after": deepcopy(
                    payload["t3"]["facts"]["objective_binding"]["value"]
                ),
            }
        )
        self.assertIs(AuthorityOutcome.UNAVAILABLE, actual(payload))

    def test_same_contract_under_wrong_objective_is_unavailable(self) -> None:
        self.assertIs(AuthorityOutcome.UNAVAILABLE, actual(fixture("LAB-V1-024")))

    def test_wrong_objective_generation_is_unavailable(self) -> None:
        self.assertIs(AuthorityOutcome.UNAVAILABLE, actual(fixture("LAB-V1-025")))

    def test_wrong_decision_contract_is_unavailable(self) -> None:
        payload = fixture("LAB-V1-032")
        payload["t3"]["facts"]["objective_binding"]["value"][0][
            "contract_id"
        ] = "OTHER-D"
        self.assertIs(AuthorityOutcome.UNAVAILABLE, actual(payload))

    def test_cross_boundary_binding_is_unavailable(self) -> None:
        self.assertIs(AuthorityOutcome.UNAVAILABLE, actual(fixture("LAB-V1-026")))

    def test_revoked_binding_delegate_is_denied(self) -> None:
        self.assertIs(AuthorityOutcome.DENIED, actual(fixture("LAB-V1-027")))

    def test_derived_contract_without_transformation_admission_is_unavailable(self) -> None:
        self.assertIs(AuthorityOutcome.UNAVAILABLE, actual(fixture("LAB-V1-028")))

    def test_exact_transformation_admission_can_authorize(self) -> None:
        self.assertIs(AuthorityOutcome.AUTHORIZED, actual(fixture("LAB-V1-029")))

    def test_stable_transformation_identity_cannot_hide_semantic_change(self) -> None:
        payload = fixture("LAB-V1-029")
        fact = payload["t3"]["facts"]["contract_transformation_binding"]
        payload["t1"]["binding_facts"]["decision_contract_identity"] = deepcopy(
            payload["t3"]["facts"]["decision_contract_identity"]
        )
        payload["t1"]["binding_facts"]["contract_transformation_binding"] = deepcopy(
            fact
        )
        payload["t2"]["mutations"] = []
        before = deepcopy(fact["value"])
        fact["value"][0]["target_contract_version"] = "3"
        payload["t3"]["facts"]["decision_contract_identity"]["value"][
            "contract_version"
        ] = "3"
        payload["t2"]["mutations"].extend(
            (
                {
                    "field": "contract_transformation_binding",
                    "before": before,
                    "after": deepcopy(fact["value"]),
                },
                {
                    "field": "decision_contract_identity",
                    "before": deepcopy(
                        payload["t1"]["binding_facts"]["decision_contract_identity"][
                            "value"
                        ]
                    ),
                    "after": deepcopy(
                        payload["t3"]["facts"]["decision_contract_identity"]["value"]
                    ),
                },
            )
        )
        self.assert_unavailable_with_reason(
            payload, "OBJECTIVE_BINDING_IDENTITY_REUSED"
        )

    def test_rollback_cannot_outrank_current_rejection(self) -> None:
        self.assertIs(AuthorityOutcome.DENIED, actual(fixture("LAB-V1-030")))

    def test_missing_authoritative_ordering_is_unavailable(self) -> None:
        self.assertIs(AuthorityOutcome.UNAVAILABLE, actual(fixture("LAB-V1-031")))

    def test_exact_objective_binding_positive_path_is_authorized(self) -> None:
        self.assertIs(AuthorityOutcome.AUTHORIZED, actual(fixture("LAB-V1-032")))

    def test_pr15_objective_fidelity_regression_has_three_outcomes(self) -> None:
        self.assertIs(AuthorityOutcome.UNAVAILABLE, actual(fixture("LAB-V1-013")))
        self.assertIs(AuthorityOutcome.DENIED, actual(fixture("LAB-V1-016")))
        self.assertIs(AuthorityOutcome.AUTHORIZED, actual(fixture("LAB-V1-032")))

    def test_cached_t1_binding_does_not_survive_unrecorded_t3_change(self) -> None:
        payload = fixture("LAB-V1-032")
        payload["t3"]["facts"]["objective_identity"]["value"][
            "objective_generation"
        ] = 2
        payload["t3"]["facts"]["objective_binding"]["value"][0][
            "objective_generation"
        ] = 2
        self.assert_unavailable_with_reason(
            payload, "OBJECTIVE_BINDING_IDENTITY_REUSED"
        )

    def test_missing_t1_binding_cannot_be_repaired_only_at_t3(self) -> None:
        payload = fixture("LAB-V1-032")
        payload["t1"]["binding_facts"]["objective_binding"] = {"state": "UNKNOWN"}
        self.assert_unavailable_with_reason(
            payload, "T1_OBJECTIVE_BINDING_UNAVAILABLE"
        )

    def test_current_revocation_precedes_irrelevant_missing_operational_fact(self) -> None:
        payload = fixture("LAB-V1-016")
        payload["t3"]["facts"]["execution_context"] = {"state": "UNKNOWN"}
        self.assertIs(AuthorityOutcome.DENIED, actual(payload))

    def test_unknown_tuple_fact_prevents_speculative_binding_denial(self) -> None:
        payload = fixture("LAB-V1-016")
        payload["t3"]["facts"]["subject_identity"] = {"state": "UNKNOWN"}
        self.assertIs(AuthorityOutcome.UNAVAILABLE, actual(payload))

    def test_ordering_source_must_match_the_admitted_root(self) -> None:
        payload = fixture("LAB-V1-032")
        payload["t3"]["facts"]["binding_ordering"]["value"][
            "ordering_source_id"
        ] = "REQUESTER-ORDER"
        self.assertIs(AuthorityOutcome.UNAVAILABLE, actual(payload))

    def test_expected_outcome_remains_outside_v1_oracle_input(self) -> None:
        payload = fixture("LAB-V1-032")
        payload["expected_outcome"] = AuthorityOutcome.DENIED.value
        result = run_fixture(payload)
        self.assertIs(AuthorityOutcome.AUTHORIZED, result.actual.outcome)
        self.assertIs(HarnessStatus.CASE_MISMATCH, result.status)

    def test_newer_authoritatively_ordered_admission_can_authorize(self) -> None:
        payload = fixture("LAB-V1-032")
        facts = payload["t3"]["facts"]
        before = {
            name: deepcopy(facts[name]["value"])
            for name in ("objective_binding", "binding_lifecycle", "binding_ordering")
        }
        old_binding = facts["objective_binding"]["value"][0]
        new_binding = deepcopy(old_binding)
        new_binding.update(
            {
                "binding_id": f"{old_binding['binding_id']}-G2",
                "binding_generation": 2,
            }
        )
        old_lifecycle = facts["binding_lifecycle"]["value"][0]
        new_lifecycle = deepcopy(old_lifecycle)
        new_lifecycle.update(
            {
                "binding_id": new_binding["binding_id"],
                "binding_generation": 2,
                "event_id": f"{old_lifecycle['event_id']}-G2",
                "event_order": 2,
            }
        )
        facts["objective_binding"]["value"] = [old_binding, new_binding]
        facts["binding_lifecycle"]["value"] = [old_lifecycle, new_lifecycle]
        facts["binding_ordering"]["value"].update(
            {
                "head_binding_id": new_binding["binding_id"],
                "head_binding_generation": 2,
                "head_event_order": 2,
            }
        )
        observation = facts["evidence_binding"]["value"]
        observation["objective_binding_id"] = new_binding["binding_id"]
        observation["objective_binding_generation"] = new_binding[
            "binding_generation"
        ]
        reissue_observation_commitment(payload)
        for name, old_value in before.items():
            payload["t2"]["mutations"].append(
                {
                    "field": name,
                    "before": old_value,
                    "after": deepcopy(facts[name]["value"]),
                }
            )
        self.assertIs(AuthorityOutcome.AUTHORIZED, actual(payload))

    def test_stable_binding_identity_cannot_hide_policy_change(self) -> None:
        payload = fixture("LAB-V1-032")
        facts = payload["t3"]["facts"]
        for name in ("objective_identity", "objective_binding"):
            before = deepcopy(facts[name]["value"])
            if name == "objective_identity":
                facts[name]["value"]["policy_version"] = "2"
            else:
                facts[name]["value"][0]["policy_version"] = "2"
            payload["t2"]["mutations"].append(
                {
                    "field": name,
                    "before": before,
                    "after": deepcopy(facts[name]["value"]),
                }
            )
        self.assert_unavailable_with_reason(
            payload, "OBJECTIVE_BINDING_IDENTITY_REUSED"
        )

    def test_candidate_array_order_cannot_overrule_authoritative_head(self) -> None:
        payload = fixture("LAB-V1-030")
        self.assertEqual(
            "REJECT",
            payload["t3"]["facts"]["objective_binding"]["value"][0][
                "disposition"
            ],
        )
        self.assertIs(AuthorityOutcome.DENIED, actual(payload))

    def test_v1_trace_includes_t1_and_transformation_admission_facts(self) -> None:
        trace = format_trace(run_path(CASES / "LAB-V1-029.json"))
        self.assertIn("T1\nresult: AUTHORIZED\nobjective_identity: KNOWN", trace)
        self.assertIn("contract_transformation_binding: KNOWN", trace)

    def test_oracle_execution_requires_no_network(self) -> None:
        with patch("socket.socket", side_effect=AssertionError("network access attempted")):
            results = [run_path(path) for path in discover(CASES)]
        self.assertTrue(all(result.status is HarnessStatus.PASS for result in results))

    def test_trace_separates_authority_outcome_and_harness_status(self) -> None:
        trace = format_trace(run_path(CASES / "LAB-V0-003.json"))
        self.assertIn("ACTUAL_AUTHORITY_OUTCOME:\nUNAVAILABLE", trace)
        self.assertIn("HARNESS_STATUS:\nPASS", trace)

    def test_cli_runs_one_case(self) -> None:
        completed = subprocess.run(
            [sys.executable, "-m", "authority_lab", "run", str(CASES / "LAB-V0-003.json")],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertIn("CASE: LAB-V0-003", completed.stdout)
        self.assertIn("HARNESS_STATUS:\nPASS", completed.stdout)

    def test_mutation_registry_canonical_vocabulary_is_exact(self) -> None:
        self.assertEqual(
            (
                "subject",
                "artifact",
                "control_state",
                "identity_basis",
                "boundary_epoch",
                "decision",
                "applicable_boundary",
                "consumption_state",
                "decision_binding",
                "evidence_id",
                "execution_context",
                "grant_id",
                "subject_mode",
                "boundary_epoch_binding",
                "closure_binding",
                "consumption_binding",
                "delegation_binding",
                "evidence_binding",
                "execution_control_binding",
                "freshness",
                "authority_root",
                "binding_lifecycle",
                "binding_ordering",
                "binding_source_authority",
                "contract_transformation_binding",
                "decision_contract_identity",
                "objective_binding",
                "objective_identity",
                "commit_state",
                "credential_identity",
                "tool_connector_identity",
            ),
            MUTATION_CANONICAL_FIELDS,
        )

    def test_mutation_registry_legacy_aliases_are_exact(self) -> None:
        self.assertEqual(
            {
                "principal": "subject",
                "privilege": "control_state",
                "consumption": "consumption_state",
                "actor_context": "execution_context",
                "credential": "credential_identity",
                "connector_endpoint": "tool_connector_identity",
            },
            dict(MUTATION_LEGACY_ALIASES),
        )

    def test_mutation_registry_is_immutable(self) -> None:
        with self.assertRaises(TypeError):
            MUTATION_REGISTRY["execution_host"] = MUTATION_SPECS[0]  # type: ignore[index]
        with self.assertRaises(TypeError):
            MUTATION_LEGACY_ALIASES["host"] = "control_state"  # type: ignore[index]

    def test_every_registry_spec_has_an_evaluator_target(self) -> None:
        target_sets = {
            MutationTargetKind.STATE: set(STATE_MUTATION_TARGETS),
            MutationTargetKind.RELATION: set(RELATIONAL_MUTATION_TARGETS),
            MutationTargetKind.BINDING: set(BINDING_MUTATION_TARGETS),
            MutationTargetKind.FACT: set(FACT_MUTATION_TARGETS),
        }
        for spec in MUTATION_SPECS:
            with self.subTest(field=spec.canonical_field):
                self.assertIn(spec.target, target_sets[spec.target_kind])
                self.assertIs(spec, MUTATION_REGISTRY[spec.canonical_field])
                for alias in spec.legacy_aliases:
                    self.assertIs(spec, MUTATION_REGISTRY[alias])

    def test_original_execution_host_counterexample_is_unavailable(self) -> None:
        payload = fixture("LAB-V1-032")
        payload["t2"]["mutations"].append(
            {
                "field": "execution_host",
                "before": "SANDBOX-S1",
                "after": "HOST-S2",
            }
        )
        self.assert_unavailable_with_reason(payload, "UNKNOWN_MUTATION_FIELD")

    def test_all_fourteen_demonstrated_unregistered_mutations_fail_closed(self) -> None:
        counterexamples = (
            ("execution_host", "SANDBOX-S1", "HOST-S2"),
            ("process_identity", "PROCESS-P1", "CHILD-P2"),
            ("acting_agent", "AGENT-A", "AGENT-B"),
            ("tool_identity", "TOOL-X", "TOOL-Y"),
            ("connector_identity", "CONNECTOR-X", "CONNECTOR-Y"),
            ("credential_context", "CRED-A", "CRED-B"),
            ("trust_domain", "DOMAIN-A", "DOMAIN-B"),
            ("tenant_account", "TENANT-A", "TENANT-B"),
            ("network_boundary", "PRIVATE-NET", "EXTERNAL-NET"),
            ("process_instance", "INSTANCE-1", "INSTANCE-2"),
            ("authority_state_representation", "RAW", "SUMMARY"),
            ("authority_consumer", "AGENT-A", "AGENT-B"),
            ("relay_actor", "AUTHORIZED-A", "UNAUTHORIZED-B"),
            ("execution_principal", "PRINCIPAL-A", "PRINCIPAL-B"),
        )
        for field, before, after in counterexamples:
            with self.subTest(field=field):
                payload = fixture("LAB-V1-032")
                payload["t2"]["mutations"].append(
                    {"field": field, "before": before, "after": after}
                )
                self.assert_unavailable_with_reason(payload, "UNKNOWN_MUTATION_FIELD")

    def test_unknown_mutation_precedes_otherwise_established_denial(self) -> None:
        payload = fixture("LAB-V1-032")
        payload["t2"]["mutations"].append(
            {"field": "execution_host", "before": "S1", "after": "S2"}
        )
        payload["t3"]["prohibition"] = {
            "state": "KNOWN",
            "applies": True,
            "id": "APPARENT_PROHIBITION",
        }
        self.assert_unavailable_with_reason(payload, "UNKNOWN_MUTATION_FIELD")

    def test_structurally_valid_unknown_names_are_unavailable(self) -> None:
        for field in (
            "executionhost",
            "wrapper_execution_host",
            "runtime_execution_host",
            "execution_host_v2",
            "host",
            "acting_subject",
            "acknowledgment",
            "monitor_context",
        ):
            with self.subTest(field=field):
                payload = fixture("LAB-V1-032")
                payload["t2"]["mutations"].append(
                    {"field": field, "before": "BEFORE", "after": "AFTER"}
                )
                self.assert_unavailable_with_reason(payload, "UNKNOWN_MUTATION_FIELD")

    def test_malformed_mutation_names_remain_input_failures(self) -> None:
        for field in (
            "Execution_Host",
            " execution_host",
            "execution_host ",
            "execution-host",
            "runtime.execution_host",
            "wrapper.execution_host",
            "executiοn_host",
            "execution_\u200bhost",
        ):
            with self.subTest(field=field):
                payload = fixture("LAB-V1-032")
                payload["t2"]["mutations"].append(
                    {"field": field, "before": "BEFORE", "after": "AFTER"}
                )
                with self.assertRaises(ValueError):
                    OracleInput.from_fixture(payload)

    def test_malformed_mutation_structures_remain_input_failures(self) -> None:
        malformed = (
            {"field": "control_state", "before": "C1"},
            {"field": "control_state", "before": "C1", "after": "C2", "extra": True},
            {"field": {"wrapped": "control_state"}, "before": "C1", "after": "C2"},
            {"wrapper": {"field": "control_state", "before": "C1", "after": "C2"}},
        )
        for mutation in malformed:
            with self.subTest(mutation=mutation):
                payload = fixture("LAB-V1-032")
                payload["t2"]["mutations"] = [mutation]
                with self.assertRaises(ValueError):
                    OracleInput.from_fixture(payload)

    def test_malformed_typed_mutation_values_remain_input_failures(self) -> None:
        for mutation in (
            {"field": "control_state", "before": 1, "after": "C2"},
            {"field": "boundary_epoch_binding", "before": [], "after": {}},
            {"field": "objective_binding", "before": {}, "after": {}},
        ):
            with self.subTest(mutation=mutation):
                payload = fixture("LAB-V1-032")
                payload["t2"]["mutations"] = [mutation]
                with self.assertRaises(ValueError):
                    OracleInput.from_fixture(payload)

    def test_noop_mutation_is_an_input_failure(self) -> None:
        payload = fixture("LAB-V1-032")
        payload["t2"]["mutations"].append(
            {"field": "control_state", "before": "C1", "after": "C1"}
        )
        with self.assertRaises(ValueError):
            OracleInput.from_fixture(payload)

    def test_retained_legacy_aliases_resolve_to_checked_targets(self) -> None:
        aliases = (
            ("principal", "S", "S2", "subject"),
            ("privilege", "C1", "C2", "control_state"),
            ("consumption", "UNUSED", "CONSUMED", "consumption_state"),
            ("actor_context", "E1", "E2", "execution_context"),
            ("credential", "CREDENTIAL-1", "CREDENTIAL-2", "credential_identity"),
            ("connector_endpoint", "CONNECTOR-1", "CONNECTOR-2", "tool_connector_identity"),
        )
        for field, before, after, target in aliases:
            with self.subTest(field=field):
                payload = fixture("LAB-V1-032")
                payload["t2"]["mutations"].append(
                    {"field": field, "before": before, "after": after}
                )
                oracle_input = OracleInput.from_fixture(payload)
                self.assertEqual(target, oracle_input.t2_mutations[0].target)
                self.assertIsNotNone(oracle_input.t2_mutations[0].canonical_field)
                self.assertIs(AuthorityOutcome.UNAVAILABLE, evaluate(oracle_input).outcome)

    def test_duplicate_same_transition_is_unavailable(self) -> None:
        payload = fixture("LAB-V1-032")
        payload["t2"]["mutations"].extend(
            [
                {"field": "control_state", "before": "C1", "after": "C2"},
                {"field": "control_state", "before": "C1", "after": "C2"},
            ]
        )
        self.assert_unavailable_with_reason(payload, "T2_T3_HYBRID_STATE")

    def test_duplicate_conflicting_transition_is_unavailable(self) -> None:
        payload = fixture("LAB-V1-032")
        payload["t2"]["mutations"].extend(
            [
                {"field": "control_state", "before": "C1", "after": "C2"},
                {"field": "control_state", "before": "C1", "after": "C3"},
            ]
        )
        self.assert_unavailable_with_reason(payload, "T2_T3_HYBRID_STATE")

    def test_reversed_transition_order_is_unavailable(self) -> None:
        payload = fixture("LAB-V1-032")
        payload["t2"]["mutations"].extend(
            [
                {"field": "control_state", "before": "C2", "after": "C3"},
                {"field": "control_state", "before": "C1", "after": "C2"},
            ]
        )
        self.assert_unavailable_with_reason(payload, "T2_T3_HYBRID_STATE")

    def test_canonical_and_alias_conflict_share_one_chain(self) -> None:
        payload = fixture("LAB-V1-032")
        payload["t2"]["mutations"].extend(
            [
                {"field": "control_state", "before": "C1", "after": "C2"},
                {"field": "privilege", "before": "C1", "after": "C3"},
            ]
        )
        self.assert_unavailable_with_reason(payload, "T2_T3_HYBRID_STATE")

    def test_canonical_and_unknown_combination_is_unavailable_as_unknown(self) -> None:
        payload = fixture("LAB-V1-032")
        payload["t2"]["mutations"].extend(
            [
                {"field": "control_state", "before": "C1", "after": "C2"},
                {"field": "execution_host", "before": "S1", "after": "S2"},
            ]
        )
        self.assert_unavailable_with_reason(payload, "UNKNOWN_MUTATION_FIELD")

    def test_round_trip_state_transition_requires_fresh_reestablishment(self) -> None:
        payload = fixture("LAB-V1-032")
        payload["t2"]["mutations"].extend(
            [
                {"field": "control_state", "before": "C1", "after": "C2"},
                {"field": "control_state", "before": "C2", "after": "C1"},
            ]
        )
        self.assert_unavailable_with_reason(payload, "T1_T3_RELATIONSHIP_UNAVAILABLE")

    def test_hostile_mutation_fixture_matrix_matches_independent_expectations(self) -> None:
        expected = {
            **{f"LAB-V1-{number:03d}": AuthorityOutcome.UNAVAILABLE for number in range(33, 46)},
            "LAB-V1-046": AuthorityOutcome.DENIED,
            "LAB-V1-047": AuthorityOutcome.UNAVAILABLE,
            "LAB-V1-048": AuthorityOutcome.AUTHORIZED,
        }
        for case_id, outcome in expected.items():
            with self.subTest(case_id=case_id):
                result = run_path(CASES / f"{case_id}.json")
                self.assertIs(HarnessStatus.PASS, result.status)
                self.assertIs(outcome, result.actual.outcome)

    def test_prohibited_cross_boundary_transition_is_denied(self) -> None:
        result = evaluate(OracleInput.from_fixture(fixture("LAB-V1-046")))
        self.assertIs(AuthorityOutcome.DENIED, result.outcome)
        self.assertIn("ESTABLISHED_PROHIBITION", {reason.code for reason in result.reasons})

    def test_fresh_cross_boundary_reestablishment_is_authorized(self) -> None:
        result = evaluate(OracleInput.from_fixture(fixture("LAB-V1-048")))
        self.assertIs(AuthorityOutcome.AUTHORIZED, result.outcome)
        self.assertIn("CURRENT_AUTHORITY_ESTABLISHED", {reason.code for reason in result.reasons})

    def test_stale_cross_boundary_reestablishment_is_unavailable(self) -> None:
        payload = fixture("LAB-V1-048")
        payload["t3"]["reestablishment"]["value"]["current"]["evidence_id"] = "EV-A-B1"
        self.assert_unavailable_with_reason(payload, "REESTABLISHMENT_EVIDENCE_REUSED")

    def test_unknown_value_comparison_is_type_exact(self) -> None:
        payload = fixture("LAB-V1-032")
        payload["t2"]["mutations"].append(
            {"field": "unknown_numeric_context", "before": 1, "after": True}
        )
        self.assert_unavailable_with_reason(payload, "UNKNOWN_MUTATION_FIELD")

    def test_boundary_laundering_fixtures_remain_unavailable(self) -> None:
        for case_id in (
            "LAB-V1-036",
            "LAB-V1-042",
            "LAB-V1-043",
        ):
            with self.subTest(case_id=case_id):
                self.assertIs(AuthorityOutcome.UNAVAILABLE, actual(fixture(case_id)))

    def test_unknown_mutation_expectation_cannot_control_oracle(self) -> None:
        payload = fixture("LAB-V1-033")
        payload["expected_outcome"] = "AUTHORIZED"
        result = run_fixture(payload)
        self.assertIs(AuthorityOutcome.UNAVAILABLE, result.actual.outcome)
        self.assertIs(HarnessStatus.CASE_MISMATCH, result.status)

    def test_trace_exposes_mutation_resolution(self) -> None:
        unknown_trace = format_trace(run_path(CASES / "LAB-V1-033.json"))
        alias_trace = format_trace(run_path(CASES / "LAB-V1-044.json"))
        self.assertIn("execution_host [UNKNOWN]", unknown_trace)
        self.assertIn(
            "actor_context [canonical=execution_context; target=STATE:execution_context]",
            alias_trace,
        )

    def test_observation_hostile_fixture_matrix_matches_independent_expectations(self) -> None:
        expected = {
            **{f"LAB-V1-{number:03d}": AuthorityOutcome.UNAVAILABLE for number in range(49, 58)},
            "LAB-V1-058": AuthorityOutcome.AUTHORIZED,
            **{f"LAB-V1-{number:03d}": AuthorityOutcome.UNAVAILABLE for number in range(59, 66)},
            "LAB-V1-066": AuthorityOutcome.AUTHORIZED,
            "LAB-V1-067": AuthorityOutcome.DENIED,
            "LAB-V1-068": AuthorityOutcome.AUTHORIZED,
        }
        for case_id, outcome in expected.items():
            with self.subTest(case_id=case_id):
                result = run_path(CASES / f"{case_id}.json")
                self.assertIs(HarnessStatus.PASS, result.status)
                self.assertIs(outcome, result.actual.outcome)

    def test_observation_profile_and_scope_vocabulary_are_frozen(self) -> None:
        self.assertEqual("AUTHORITY-LAB-OBSERVATION-PROFILE-1", OBSERVATION_PROFILE_ID)
        self.assertEqual(1, OBSERVATION_PROFILE_VERSION)
        self.assertEqual(
            (
                "SUBJECT_AND_DELEGATION",
                "ARTIFACT_AND_TRANSFORMATION",
                "EXECUTION_CONTROL",
                "BOUNDARY_AND_EPOCH",
                "CREDENTIAL_AND_IDENTITY",
                "GRANT_USE_AND_CONSUMPTION",
                "OBJECTIVE_AUTHORITY_LIFECYCLE",
                "OBSERVATION_PIPELINE",
            ),
            OBSERVATION_SCOPE_FAMILIES,
        )

    def test_absence_of_observation_cannot_imply_continuity(self) -> None:
        payload = fixture("LAB-V1-032")
        payload["t3"]["facts"]["evidence_binding"]["value"] = "EXACT"
        payload["t3"]["facts"]["freshness"]["value"] = "CURRENT"
        self.assert_unavailable_with_reason(payload, "OBSERVATION_ADMISSION_UNAVAILABLE")

    def test_unchecked_observation_completeness_boolean_is_malformed(self) -> None:
        payload = fixture("LAB-V1-032")
        payload["t3"]["facts"]["evidence_binding"]["value"][
            "observations_complete"
        ] = True
        with self.assertRaises(ValueError):
            OracleInput.from_fixture(payload)

    def test_root_observer_cycle_is_unavailable(self) -> None:
        payload = fixture("LAB-V1-032")
        root_id = payload["t3"]["facts"]["authority_root"]["value"]["root_id"]
        observation = payload["t3"]["facts"]["evidence_binding"]["value"]
        observation["observers"][0]["observer_id"] = root_id
        observation["segments"][0]["observer_id"] = root_id
        observation["lifecycle_records"][1]["target_id"] = root_id
        self.assert_unavailable_with_reason(payload, "OBSERVATION_ADMISSION_UNAVAILABLE")

    def test_delegate_observer_widening_is_unavailable(self) -> None:
        payload = fixture("LAB-V1-051")
        self.assert_unavailable_with_reason(payload, "OBSERVATION_ADMISSION_UNAVAILABLE")
        payload["t3"]["facts"]["evidence_binding"]["value"]["source_id"] = (
            "ROOT-AUTH-BOUNDARY-1"
        )
        self.assertIs(AuthorityOutcome.AUTHORIZED, actual(payload))

    def test_coverage_and_restart_gaps_are_unavailable(self) -> None:
        for case_id in ("LAB-V1-054", "LAB-V1-055"):
            with self.subTest(case_id=case_id):
                self.assert_unavailable_with_reason(
                    fixture(case_id), "OBSERVATION_COVERAGE_UNAVAILABLE"
                )

    def test_substitution_requires_exact_root_issued_handoff(self) -> None:
        self.assert_unavailable_with_reason(
            fixture("LAB-V1-057"), "OBSERVER_HANDOFF_UNAVAILABLE"
        )
        self.assertIs(AuthorityOutcome.AUTHORIZED, actual(fixture("LAB-V1-058")))

    def test_conflicting_observers_fail_closed_without_voting(self) -> None:
        self.assert_unavailable_with_reason(
            fixture("LAB-V1-059"), "OBSERVATION_CONFLICTING"
        )

    def test_observation_laundering_paths_are_unavailable(self) -> None:
        expected_reasons = {
            "LAB-V1-061": "OBSERVATION_TRANSFORMATION_UNAVAILABLE",
            "LAB-V1-062": "OBSERVATION_TRANSFORMATION_UNAVAILABLE",
            "LAB-V1-063": "OBSERVATION_ADMISSION_UNAVAILABLE",
            "LAB-V1-064": "OBSERVATION_ADMISSION_UNAVAILABLE",
            "LAB-V1-065": "OBSERVATION_TRANSFORMATION_UNAVAILABLE",
        }
        for case_id, reason in expected_reasons.items():
            with self.subTest(case_id=case_id):
                self.assert_unavailable_with_reason(fixture(case_id), reason)

    def test_duplicate_observation_segment_is_idempotent_but_conflict_is_not(self) -> None:
        payload = fixture("LAB-V1-032")
        segments = payload["t3"]["facts"]["evidence_binding"]["value"]["segments"]
        segments.append(deepcopy(segments[0]))
        self.assertIs(AuthorityOutcome.AUTHORIZED, actual(payload))
        segments[-1]["stream_commitment"] = "CONFLICTING-COMMITMENT"
        self.assert_unavailable_with_reason(payload, "OBSERVATION_CONFLICTING")

    def test_reordered_stream_sequence_cannot_hide_behind_interval_coverage(self) -> None:
        payload = fixture("LAB-V1-032")
        segments = payload["t3"]["facts"]["evidence_binding"]["value"]["segments"]
        segments[0].update(
            {"end_anchor_id": "MID", "end_event_order": 2, "end_sequence": 10}
        )
        after = deepcopy(segments[0])
        after.update(
            {
                "segment_id": "SEGMENT-REORDERED-AFTER",
                "start_anchor_id": "MID",
                "start_event_order": 2,
                "end_anchor_id": payload["t3"]["facts"]["evidence_binding"]["value"][
                    "t3_anchor"
                ]["anchor_id"],
                "end_event_order": 3,
                "start_sequence": 1,
                "end_sequence": 2,
            }
        )
        segments.append(after)
        self.assert_unavailable_with_reason(payload, "OBSERVATION_ORDERING_UNAVAILABLE")

    def test_multihop_transformation_cannot_drop_scope(self) -> None:
        payload = fixture("LAB-V1-061")
        transformations = payload["t3"]["facts"]["evidence_binding"]["value"][
            "transformations"
        ]
        first = transformations[0]
        first["scope_families"] = deepcopy(
            payload["t3"]["facts"]["evidence_binding"]["value"]["segments"][0][
                "scope_families"
            ]
        )
        second = deepcopy(first)
        second.update(
            {
                "transformation_id": "TRANSFORM-MULTIHOP-LOSS",
                "source_stream_id": first["target_stream_id"],
                "source_stream_generation": first["target_stream_generation"],
                "source_commitment": first["target_commitment"],
                "target_stream_id": "SUMMARY-MULTIHOP-LOSS",
                "target_commitment": "SUMMARY-COMMITMENT-MULTIHOP-LOSS",
                "scope_families": first["scope_families"][:-1],
            }
        )
        transformations.append(second)
        self.assert_unavailable_with_reason(
            payload, "OBSERVATION_TRANSFORMATION_UNAVAILABLE"
        )

    def test_current_root_issued_observer_revocation_is_denied(self) -> None:
        result = evaluate(OracleInput.from_fixture(fixture("LAB-V1-067")))
        self.assertIs(AuthorityOutcome.DENIED, result.outcome)
        self.assertIn("OBSERVATION_SOURCE_REVOKED", {r.code for r in result.reasons})

    def test_positive_root_issued_observation_path_remains_authorized(self) -> None:
        for case_id in ("LAB-V1-066", "LAB-V1-068"):
            with self.subTest(case_id=case_id):
                result = evaluate(OracleInput.from_fixture(fixture(case_id)))
                self.assertIs(AuthorityOutcome.AUTHORIZED, result.outcome)
                self.assertIn(
                    "CURRENT_AUTHORITY_ESTABLISHED",
                    {reason.code for reason in result.reasons},
                )

    def test_trace_exposes_observation_admission_and_coverage(self) -> None:
        trace = format_trace(run_path(CASES / "LAB-V1-058.json"))
        self.assertIn("OBSERVATION\nprofile: AUTHORITY-LAB-OBSERVATION-PROFILE-1@1", trace)
        self.assertIn("handoff: HANDOFF-LAB-V1-058", trace)
        self.assertIn("gaps: none", trace)
        self.assertIn("freshness: T3-ANCHOR-LAB-V1-032@3", trace)

    def test_shutdown_successor_fixture_matrix_matches_independent_expectations(self) -> None:
        expected = {
            **{f"LAB-V1-{number:03d}": AuthorityOutcome.UNAVAILABLE for number in range(69, 78)},
            "LAB-V1-078": AuthorityOutcome.DENIED,
            **{f"LAB-V1-{number:03d}": AuthorityOutcome.UNAVAILABLE for number in range(79, 84)},
            "LAB-V1-084": AuthorityOutcome.AUTHORIZED,
            "LAB-V1-085": AuthorityOutcome.AUTHORIZED,
            **{f"LAB-V1-{number:03d}": AuthorityOutcome.UNAVAILABLE for number in range(86, 89)},
        }
        for case_id, outcome in expected.items():
            with self.subTest(case_id=case_id):
                result = run_path(CASES / f"{case_id}.json")
                self.assertIs(HarnessStatus.PASS, result.status)
                self.assertIs(outcome, result.actual.outcome)

    def test_every_registry_spec_has_immutable_continuity_metadata(self) -> None:
        for spec in MUTATION_SPECS:
            with self.subTest(field=spec.canonical_field):
                self.assertIsInstance(spec.continuity_effects, tuple)
                self.assertTrue(spec.continuity_effects)
                self.assertTrue(all(isinstance(item, ContinuityEffect) for item in spec.continuity_effects))
                self.assertIsInstance(spec.observation_scope_families, tuple)
                self.assertTrue(spec.observation_scope_families)
                self.assertLessEqual(
                    set(spec.observation_scope_families), set(OBSERVATION_SCOPE_FAMILIES)
                )

    def test_execution_and_subject_aba_paths_remain_unavailable(self) -> None:
        for case_id in ("LAB-V1-069", "LAB-V1-070"):
            with self.subTest(case_id=case_id):
                self.assert_unavailable_with_reason(
                    fixture(case_id), "PREDECESSOR_GRANT_NONPORTABLE"
                )

    def test_boundary_epoch_aba_is_non_restorable(self) -> None:
        self.assert_unavailable_with_reason(
            fixture("LAB-V1-071"), "BOUNDARY_EPOCH_REUSE_UNAVAILABLE"
        )

    def test_restart_and_generic_evidence_cannot_reuse_predecessor_grant(self) -> None:
        for case_id in ("LAB-V1-072", "LAB-V1-073"):
            with self.subTest(case_id=case_id):
                self.assert_unavailable_with_reason(
                    fixture(case_id), "PREDECESSOR_GRANT_NONPORTABLE"
                )

    def test_fresh_generic_evidence_and_grant_do_not_admit_a_successor(self) -> None:
        payload = fixture("LAB-V1-069")
        payload["t2"]["mutations"].append(
            {"field": "grant_id", "before": "GRANT-001", "after": "GENERIC-GRANT-NEW"}
        )
        payload["t3"]["facts"]["consumption_binding"]["value"]["grant_id"] = (
            "GENERIC-GRANT-NEW"
        )
        payload["t3"]["reestablishment"]["value"]["current"]["grant_id"] = (
            "GENERIC-GRANT-NEW"
        )
        self.assert_unavailable_with_reason(payload, "SUCCESSOR_AUTHORITY_UNAVAILABLE")

    def test_credential_checkpoint_and_alternate_path_do_not_port_authority(self) -> None:
        for case_id in ("LAB-V1-075", "LAB-V1-076", "LAB-V1-077"):
            with self.subTest(case_id=case_id):
                self.assert_unavailable_with_reason(
                    fixture(case_id), "PREDECESSOR_GRANT_NONPORTABLE"
                )

    def test_restored_labels_do_not_evade_exact_current_revocation(self) -> None:
        result = evaluate(OracleInput.from_fixture(fixture("LAB-V1-078")))
        self.assertIs(AuthorityOutcome.DENIED, result.outcome)
        self.assertIn("ESTABLISHED_PROHIBITION", {reason.code for reason in result.reasons})

    def test_terminal_observation_failures_remain_fail_closed(self) -> None:
        expected_reasons = {
            "LAB-V1-079": "OBSERVATION_FRESHNESS_UNAVAILABLE",
            "LAB-V1-080": "OBSERVATION_TRANSFORMATION_UNAVAILABLE",
            "LAB-V1-081": "TERMINAL_EVENT_ORDERING_UNAVAILABLE",
            "LAB-V1-082": "TERMINAL_EVENT_ORDERING_UNAVAILABLE",
            "LAB-V1-083": "OBSERVATION_CONFLICTING",
        }
        for case_id, reason in expected_reasons.items():
            with self.subTest(case_id=case_id):
                self.assert_unavailable_with_reason(fixture(case_id), reason)

    def test_fresh_successor_and_legitimate_reentry_are_authorized(self) -> None:
        for case_id in ("LAB-V1-084", "LAB-V1-085"):
            with self.subTest(case_id=case_id):
                result = evaluate(OracleInput.from_fixture(fixture(case_id)))
                self.assertIs(AuthorityOutcome.AUTHORIZED, result.outcome)
                self.assertIn(
                    "CURRENT_AUTHORITY_ESTABLISHED",
                    {reason.code for reason in result.reasons},
                )

    def test_handoff_does_not_transfer_execution_authority(self) -> None:
        self.assert_unavailable_with_reason(
            fixture("LAB-V1-087"), "PREDECESSOR_GRANT_NONPORTABLE"
        )

    def test_identical_code_does_not_establish_execution_identity(self) -> None:
        self.assert_unavailable_with_reason(
            fixture("LAB-V1-088"), "PREDECESSOR_GRANT_NONPORTABLE"
        )

    def test_trace_exposes_continuity_effect_and_observation_scope(self) -> None:
        trace = format_trace(run_path(CASES / "LAB-V1-069.json"))
        self.assertIn("continuity_effects=IDENTITY_DISCONTINUITY", trace)
        self.assertIn("observation_scopes=EXECUTION_CONTROL,CREDENTIAL_AND_IDENTITY", trace)
        self.assertIn("path_aba_targets: execution_context", trace)
        self.assertIn("successor_admission_required: true", trace)

    def test_commitment_hostile_matrix_matches_independent_expectations(self) -> None:
        for number in range(89, 113):
            case_id = f"LAB-V1-{number:03d}"
            with self.subTest(case_id=case_id):
                self.assertIs(HarnessStatus.PASS, run_fixture(fixture(case_id)).status)

    def test_commitment_digest_is_recomputed_from_exact_body(self) -> None:
        payload = fixture("LAB-V1-032")
        binding = payload["t3"]["facts"]["evidence_binding"]["value"]
        binding["commitment_envelopes"][0]["objective_binding_id"] += "-ALTERED"
        self.assert_unavailable_with_reason(payload, "OBSERVATION_COMMITMENT_CONFLICTING")

    def test_isolated_equivocation_is_unavailable(self) -> None:
        self.assert_unavailable_with_reason(
            fixture("LAB-V1-090"), "OBSERVATION_COMMITMENT_EQUIVOCATION"
        )

    def test_replay_after_newer_checkpoint_is_unavailable(self) -> None:
        self.assert_unavailable_with_reason(
            fixture("LAB-V1-091"), "OBSERVATION_COMMITMENT_REPLAY"
        )

    def test_stream_generation_replay_is_unavailable(self) -> None:
        self.assert_unavailable_with_reason(
            fixture("LAB-V1-092"), "OBSERVATION_VERIFIER_STATE_UNAVAILABLE"
        )

    def test_self_updated_freshness_is_unavailable(self) -> None:
        self.assert_unavailable_with_reason(
            fixture("LAB-V1-094"), "OBSERVATION_FRESHNESS_UNAVAILABLE"
        )

    def test_missing_predecessor_relation_is_unavailable(self) -> None:
        self.assert_unavailable_with_reason(
            fixture("LAB-V1-095"), "OBSERVATION_COMMITMENT_UNIQUENESS_UNAVAILABLE"
        )

    def test_verifier_state_loss_and_rollback_fail_closed(self) -> None:
        expected = {
            "LAB-V1-103": "OBSERVATION_VERIFIER_STATE_UNAVAILABLE",
            "LAB-V1-104": "OBSERVATION_VERIFIER_ROLLBACK",
        }
        for case_id, reason in expected.items():
            with self.subTest(case_id=case_id):
                self.assert_unavailable_with_reason(fixture(case_id), reason)

    def test_subject_cannot_be_commitment_verifier(self) -> None:
        self.assert_unavailable_with_reason(
            fixture("LAB-V1-105"), "OBSERVATION_COMMITMENT_AUTHENTICITY_UNAVAILABLE"
        )

    def test_conflicting_witness_cannot_create_authority(self) -> None:
        self.assert_unavailable_with_reason(
            fixture("LAB-V1-106"), "OBSERVATION_WITNESS_CONFLICTING"
        )

    def test_incomplete_committed_scope_is_unavailable(self) -> None:
        self.assert_unavailable_with_reason(
            fixture("LAB-V1-107"), "OBSERVATION_COMMITMENT_CONFLICTING"
        )

    def test_unverified_commitment_is_unavailable(self) -> None:
        self.assert_unavailable_with_reason(
            fixture("LAB-V1-108"), "OBSERVATION_COMMITMENT_AUTHENTICITY_UNAVAILABLE"
        )

    def test_verification_must_bind_exact_issuer_key(self) -> None:
        payload = fixture("LAB-V1-032")
        verification = payload["t3"]["facts"]["evidence_binding"]["value"][
            "commitment_verifications"
        ][0]
        verification["issuer_key_id"] = "UNRELATED-KEY"
        self.assert_unavailable_with_reason(
            payload, "OBSERVATION_COMMITMENT_AUTHENTICITY_UNAVAILABLE"
        )

    def test_commitment_without_checkpoint_is_unavailable(self) -> None:
        self.assert_unavailable_with_reason(
            fixture("LAB-V1-109"), "OBSERVATION_COMMITMENT_UNIQUENESS_UNAVAILABLE"
        )

    def test_candidate_fixture_cannot_supply_trusted_state(self) -> None:
        path = CASES / "LAB-V1-032.json"
        raw = json.loads(path.read_text(encoding="utf-8"))
        raw["_trusted_commitment_context"] = []
        with self.assertRaises(ValueError):
            # Disk fixtures are never allowed to choose their own durable anchor.
            with patch("json.load", return_value=raw):
                load_fixture(path)

    def test_positive_commitment_and_successor_paths_remain_authorized(self) -> None:
        for case_id in ("LAB-V1-098", "LAB-V1-099", "LAB-V1-102", "LAB-V1-111", "LAB-V1-112"):
            with self.subTest(case_id=case_id):
                self.assertIs(AuthorityOutcome.AUTHORIZED, actual(fixture(case_id)))

    def test_fixture_files_are_valid_json_objects(self) -> None:
        for path in discover(CASES):
            with self.subTest(path=path.name):
                with path.open("r", encoding="utf-8") as handle:
                    self.assertIsInstance(json.load(handle), dict)


if __name__ == "__main__":
    unittest.main()
