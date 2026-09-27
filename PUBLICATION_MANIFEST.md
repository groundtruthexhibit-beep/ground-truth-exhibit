# Public Exhibit Manifest

This manifest describes the intended contents of the public Ground Truth exhibit
and its v1 research-freeze evidence package.

## Included

- `README.md`
- `ARCHITECTURE.md`
- `SECURITY_MODEL.md`
- `EVIDENCE_MODEL.md`
- `ALPHA_COMPLETION.md`
- `DISCLOSURE_BOUNDARY.md`
- `GROUND_TRUTH_RESEARCH_FREEZE.md`
- `GROUND_TRUTH_COUNTEREXAMPLE_CATALOG.md`
- `GROUND_TRUTH_THREAT_MODEL.md`
- `GROUND_TRUTH_LIMITATIONS.md`
- `GROUND_TRUTH_REPRODUCIBILITY.md`
- `GROUND_TRUTH_PAPER_EVIDENCE_MANIFEST.md`
- `GROUND_TRUTH_CANONICAL_CONTRACT.md`
- `GROUND_TRUTH_FIXTURE_AND_CANONICALIZATION.md`
- `authority_lab/`
- `cases/authority_lab/`
- `tests/test_authority_lab.py`

## Intentionally excluded

- private source implementation;
- database migrations;
- validators and enforcement workflows;
- private tests and adversarial fixtures not intentionally published in this exhibit;
- CI evidence archives;
- credentials, keys, endpoints, environment configuration;
- private Git history;
- future-phase work.

## Claim boundary

The exhibit may state that Ground Truth Alpha reached its terminal authorized lifecycle state.

It must not state or imply that Alpha completion constitutes production readiness, certification, regulatory compliance, formal verification, universal security, or authorization of a subsequent phase.

The v1 research freeze records bounded failure-to-falsify results at exact Git
states. It does not convert fixture agreement, hostile review, or reproducibility
evidence into a universal security or deployment claim.
