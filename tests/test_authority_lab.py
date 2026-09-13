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
        self.assert_unavailable_with_reason(payload, "DECISION_EVIDENCE_BINDING_MISMATCH")

    def test_unrelated_delegation_binding_cannot_authorize(self) -> None:
        payload = fixture("LAB-V0-010")
        payload["t3"]["facts"]["delegation_binding"]["value"] = "UNRELATED"
        self.assert_unavailable_with_reason(payload, "REQUIRED_VALUE_MISMATCH")

    def test_implicit_closure_cannot_authorize(self) -> None:
        payload = fixture("LAB-V0-010")
        payload["t3"]["facts"]["closure_binding"]["value"] = "IMPLICIT"
        self.assert_unavailable_with_reason(payload, "REQUIRED_VALUE_MISMATCH")

    def test_fixture_cannot_remove_any_mandatory_t3_fact(self) -> None:
        for field in MANDATORY_T3_FACTS:
            with self.subTest(field=field):
                payload = fixture("LAB-V0-001")
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
                    set(MANDATORY_T3_FACTS).issubset(payload["t3"]["required_values"])
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
        denied["t3"]["prohibition"] = {
            "state": "KNOWN",
            "applies": True,
            "id": "E2_EXECUTION_PROHIBITED",
        }
        self.assertIs(AuthorityOutcome.DENIED, actual(denied))

        authorized = deepcopy(denied)
        authorized["t3"]["prohibition"] = {"state": "KNOWN", "applies": False, "id": "none"}
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
        self.assertEqual(11, len(MANDATORY_T3_FACTS))

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
