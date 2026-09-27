# Public Exhibit Manifest

This manifest describes the intended contents of the initial public Ground Truth exhibit.

## Included

- `README.md`
- `ARCHITECTURE.md`
- `SECURITY_MODEL.md`
- `EVIDENCE_MODEL.md`
- `ALPHA_COMPLETION.md`
- `DISCLOSURE_BOUNDARY.md`
- `LITERATURE_AND_PRIOR_ART.md`
- `AUTHORITY_LAB_DESIGN.md`
- `authority_lab/` — bounded public deterministic falsification harness
- `cases/authority_lab/` — bounded public fixture corpus
- `tests/test_authority_lab.py` — public harness regression tests

## Intentionally excluded

- private source implementation;
- database migrations;
- validators and enforcement workflows;
- private-core tests and non-public adversarial fixtures beyond the bounded public corpus;
- CI evidence archives;
- credentials, keys, endpoints, environment configuration;
- private Git history;
- future-phase work.

## Publication status boundary

The public repository already contains a bounded runnable Authority Lab and public fixtures. That public harness is separate from the private Ground Truth core.

Later reviewed Authority Lab v1 release-candidate work exists outside the currently transported GitHub history while exact Git transport is pending. Documentation may identify that work as reviewed locally / transport pending, but must not present untransported commits, tests, fixture counts, exact-head verdicts, or freeze checkpoints as remotely verifiable GitHub state.

## Historical checkpoint documents

Design records, hostile reviews, frontier deltas, casebooks, and research-pressure documents may preserve language that was correct at their exact reviewed checkpoint (for example, a future-work statement that later became implemented). Those files are retained as historical evidence and are not silently rewritten to simulate later knowledge. For current publication status, use the README, this manifest, and the exact Git history associated with the claim being made.

## Claim boundary

The exhibit may state that Ground Truth Alpha reached its terminal authorized lifecycle state.

It must not state or imply that Alpha completion constitutes production readiness, certification, regulatory compliance, formal verification, universal security, or authorization of a subsequent phase.
