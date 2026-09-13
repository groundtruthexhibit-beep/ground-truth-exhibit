from __future__ import annotations

import json
import subprocess
import sys
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

from authority_lab.model import (
    AuthorityOutcome,
    FactState,
    HarnessStatus,
    INVARIANTS,
    MANDATORY_T3_FACTS,
    OracleInput,
    RELATIONAL_T3_FACTS,
    TUPLE_FIELDS,
)
from authority_lab.oracle import evaluate
from authority_lab.runner import discover, format_trace, load_fixture, run_fixture, run_path


ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "cases" / "authority_lab"


def fixture(case_id: str) -> dict:
    return load_fixture(CASES / f"{case_id}.json")


def actual(payload: dict) -> AuthorityOutcome:
    return evaluate(OracleInput.from_fixture(payload)).outcome


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

    def test_v0_contains_twelve_deterministic_fixtures(self) -> None:
        paths = discover(CASES)
        self.assertEqual(12, len(paths))
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
        self.assert_unavailable_with_reason(payload, "REQUIRED_VALUE_MISMATCH")

    def test_wrong_evidence_binding_cannot_authorize(self) -> None:
        payload = fixture("LAB-V0-001")
        payload["t3"]["facts"]["evidence_binding"]["value"] = "STALE"
        self.assert_unavailable_with_reason(payload, "REQUIRED_VALUE_MISMATCH")

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
        for field, value in (
            ("consumption_state", "CONSUMED"),
            ("freshness", "STALE"),
            ("evidence_binding", "STALE"),
        ):
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
                    set(payload["t3"]["required_facts"]).issubset(
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

        authorized = deepcopy(denied)
        authorized["t3"]["prohibition"] = {"state": "KNOWN", "applies": False, "id": "none"}
        authorized["t3"]["facts"]["decision_binding"]["value"] = "EV-E2"
        authorized["t3"]["required_values"]["decision_binding"] = "EV-E2"
        authorized["t3"]["facts"]["consumption_binding"]["value"]["grant_id"] = (
            "GRANT-003-E2"
        )
        authorized["t3"]["reestablishment"] = {
            "state": "KNOWN",
            "value": {
                "previous_evidence_id": "EV-E1",
                "current": {
                    "subject": "S",
                    "artifact": "A",
                    "control_state": "E2",
                    "identity_basis": "I1",
                    "boundary_epoch": "B1",
                    "decision": "AUTHORIZED",
                    "evidence_id": "EV-E2",
                    "execution_context": "E2",
                    "applicable_boundary": "AUTH-BOUNDARY-1",
                    "grant_id": "GRANT-003-E2",
                    "consumption_state": "UNUSED",
                    "subject_mode": "DIRECT",
                },
            },
        }
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
        self.assertEqual(16, len(MANDATORY_T3_FACTS))

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
            payload, "GRANT_EFFECT_RELATIONSHIP_UNAVAILABLE"
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
            payload, "GRANT_EFFECT_RELATIONSHIP_UNAVAILABLE"
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

    def test_tuple_mismatch_is_unavailable(self) -> None:
        payload = fixture("LAB-V0-001")
        payload["t3"]["facts"]["artifact_identity"]["value"] = "OTHER"
        self.assertIs(AuthorityOutcome.UNAVAILABLE, actual(payload))

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

    def test_fixture_files_are_valid_json_objects(self) -> None:
        for path in discover(CASES):
            with self.subTest(path=path.name):
                with path.open("r", encoding="utf-8") as handle:
                    self.assertIsInstance(json.load(handle), dict)


if __name__ == "__main__":
    unittest.main()
