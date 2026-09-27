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
- `LITERATURE_AND_PRIOR_ART.md`
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

- private-core source implementation not intentionally published here;
- private database migrations and operational enforcement workflows;
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

## Frozen v1 publication checkpoint

- freeze branch: `docs/ground-truth-research-freeze-v1`
- freeze documentation commit: `3d09acc804bc1271965696f2d9561143ca28b835`
- frozen research HEAD: `31d78aa158618ca8b72eb61e2f49b434e4319e9e`
- schema: `authority-lab-v1`
- tuple coordinates: 6
- invariants: 6
- outcomes: 3
- fixture corpus: `LAB-V0-001..012` + `LAB-V1-013..466`
- public tests on freeze branch: 260/260 PASS
- Authority Lab fixtures at research HEAD: 466/466 PASS

These values are remotely inspectable in the transported v1 Git history. They remain model- and environment-bounded evidence, not a universal security claim.
