#!/usr/bin/env python3
"""Expectation-independent hostile review for integrated PHI disclosure authority."""

from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from authority_lab.model import AuthorityOutcome, OracleInput
from authority_lab.oracle import evaluate
from authority_lab.runner import load_fixture

CASES = Path("cases/authority_lab")


def fixture(case_id: str) -> dict:
    return load_fixture(CASES / f"{case_id}.json")


def actual(payload: dict) -> AuthorityOutcome:
    return evaluate(OracleInput.from_fixture(payload)).outcome


class PHIHostileReview(unittest.TestCase):
    def test_positive_control(self):
        self.assertIs(AuthorityOutcome.AUTHORIZED, actual(fixture("LAB-V1-469")))

    def test_required_binding_missing_fails_closed(self):
        self.assertIs(AuthorityOutcome.UNAVAILABLE, actual(fixture("LAB-V1-468")))

    def test_revocation_is_current_negative(self):
        self.assertIs(AuthorityOutcome.DENIED, actual(fixture("LAB-V1-470")))

    def test_incomplete_history_fails_closed(self):
        self.assertIs(AuthorityOutcome.UNAVAILABLE, actual(fixture("LAB-V1-471")))

    def test_cumulative_effective_domain_limit_denies(self):
        self.assertIs(AuthorityOutcome.DENIED, actual(fixture("LAB-V1-472")))

    def test_purpose_drift_without_negative_is_unavailable(self):
        self.assertIs(AuthorityOutcome.UNAVAILABLE, actual(fixture("LAB-V1-473")))

    def test_explicit_purpose_negative_denies(self):
        self.assertIs(AuthorityOutcome.DENIED, actual(fixture("LAB-V1-474")))

    def test_transform_laundering_fails_closed(self):
        self.assertIs(AuthorityOutcome.UNAVAILABLE, actual(fixture("LAB-V1-475")))

    def test_memory_scope_laundering_fails_closed(self):
        self.assertIs(AuthorityOutcome.UNAVAILABLE, actual(fixture("LAB-V1-476")))

    def test_ambiguous_effect_cannot_be_replayed(self):
        self.assertIs(AuthorityOutcome.UNAVAILABLE, actual(fixture("LAB-V1-477")))

    def test_provider_migration_under_old_binding_fails_closed(self):
        self.assertIs(AuthorityOutcome.UNAVAILABLE, actual(fixture("LAB-V1-478")))

    def test_candidate_cannot_self_select_phi_policy(self):
        payload = fixture("LAB-V1-464")
        positive = fixture("LAB-V1-469")
        payload["t3"]["facts"]["phi_disclosure_binding"] = copy.deepcopy(
            positive["t3"]["facts"]["phi_disclosure_binding"]
        )
        payload["t3"]["required_facts"].append("phi_disclosure_binding")
        payload["t3"]["required_values"]["phi_disclosure_binding"] = copy.deepcopy(
            positive["t3"]["facts"]["phi_disclosure_binding"]["value"]
        )
        self.assertIs(AuthorityOutcome.UNAVAILABLE, actual(payload))

    def test_candidate_cannot_inject_trusted_phi_context(self):
        raw = json.loads((CASES / "LAB-V1-464.json").read_text())
        raw["_trusted_phi_disclosure_context"] = {"requirement": "NONE"}
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "candidate.json"
            p.write_text(json.dumps(raw))
            with self.assertRaisesRegex(ValueError, "trusted PHI disclosure"):
                load_fixture(p)

    def test_protected_context_unknown_field_is_rejected(self):
        payload = fixture("LAB-V1-469")
        payload["_trusted_anchor_context"][0]["phi_disclosure_authority_context"]["forged"] = True
        with self.assertRaisesRegex(ValueError, "contain exactly"):
            actual(payload)

    def test_wrong_effect_digest_does_not_reach_denied_or_authorized(self):
        payload = fixture("LAB-V1-469")
        payload["t3"]["facts"]["phi_disclosure_binding"]["value"]["effect_digest"] = "WRONG"
        payload["t3"]["required_values"]["phi_disclosure_binding"]["effect_digest"] = "WRONG"
        self.assertIs(AuthorityOutcome.UNAVAILABLE, actual(payload))

    def test_wrong_execution_event_does_not_reach_denied_or_authorized(self):
        payload = fixture("LAB-V1-469")
        payload["t3"]["facts"]["phi_disclosure_binding"]["value"]["execution_event_id"] = "OTHER-T3"
        payload["t3"]["required_values"]["phi_disclosure_binding"]["execution_event_id"] = "OTHER-T3"
        self.assertIs(AuthorityOutcome.UNAVAILABLE, actual(payload))

    def test_current_negative_does_not_apply_to_mismatched_effect(self):
        payload = fixture("LAB-V1-470")
        payload["t3"]["facts"]["phi_disclosure_binding"]["value"]["effect_digest"] = "WRONG"
        payload["t3"]["required_values"]["phi_disclosure_binding"]["effect_digest"] = "WRONG"
        self.assertIs(AuthorityOutcome.UNAVAILABLE, actual(payload))

    def test_policy_none_does_not_accept_candidate_phi_binding(self):
        payload = fixture("LAB-V1-467")
        positive = fixture("LAB-V1-469")
        payload["t3"]["facts"]["phi_disclosure_binding"] = copy.deepcopy(
            positive["t3"]["facts"]["phi_disclosure_binding"]
        )
        payload["t3"]["required_facts"].append("phi_disclosure_binding")
        payload["t3"]["required_values"]["phi_disclosure_binding"] = copy.deepcopy(
            positive["t3"]["facts"]["phi_disclosure_binding"]["value"]
        )
        self.assertIs(AuthorityOutcome.UNAVAILABLE, actual(payload))


if __name__ == "__main__":
    unittest.main(verbosity=2)
