# Ground Truth v1 Research Freeze

## Freeze status

**RESEARCH FREEZE — ACTIVE**

Ground Truth v1 research is frozen at the reviewed Composite closure state:

- repository: `groundtruthexhibit-beep/ground-truth-exhibit`
- freeze branch: `docs/ground-truth-research-freeze-v1`
- research HEAD: `31d78aa158618ca8b72eb61e2f49b434e4319e9e`
- research parent: `406a37b4a0019a9eb9d8526b5d248dd1ebc6de20`
- freeze date: 2026-09-26

The documentation commit containing this record is publication metadata. The
research result frozen by this record is the exact research HEAD above.

## Frozen public contract

- schema: `authority-lab-v1`
- tuple: `(subject, artifact, control_state, identity_basis, boundary_epoch, decision)`
- invariants: `INV-CONT`, `INV-DISC`, `INV-BND`, `INV-EVD`, `INV-USE`, `INV-CLO`
- outcomes: `AUTHORIZED`, `DENIED`, `UNAVAILABLE`
- corpus: `LAB-V0-001..012` and `LAB-V1-013..466` (466 fixtures)
- public tests: 260/260 PASS on the freeze branch (259/259 at the Composite checkpoint, plus one test-only deterministic replay test)
- Authority Lab fixtures: 466/466 PASS at the Composite checkpoint

## Closing checkpoints

### Canonical T3 closure

- branch: `fix/authority-lab-v1-t3-execution-event-convergence`
- HEAD: `4e1eae61136fdda078c5e38f71e0f62f83fa92f9`
- parent: `74fba1f8fd537afb59996662affe1df64457d530`
- fixtures: 443/443 PASS; new range `LAB-V1-412..443`
- public tests: 257/257 PASS; focused tests: 7/7 PASS
- verdict: **PASS — NO REPRODUCIBLE IN-SCOPE CROSS-LAYER TEMPORAL-COMPOSITION OR STALE-EXECUTION BYPASS FOUND**

### Composite closure

- branch: `test/authority-lab-v1-composite-adversarial-continuity`
- HEAD: `31d78aa158618ca8b72eb61e2f49b434e4319e9e`
- parent: `406a37b4a0019a9eb9d8526b5d248dd1ebc6de20`
- commits: `406a37b4a0019a9eb9d8526b5d248dd1ebc6de20`, `31d78aa158618ca8b72eb61e2f49b434e4319e9e`
- fixtures: 466/466 PASS; new range `LAB-V1-444..466`
- public tests: 259/259 PASS; focused Composite tests: 2/2 PASS
- verdict: **PASS — NO REPRODUCIBLE IN-SCOPE COMPOSITE AUTHORITY-CONTINUITY COUNTEREXAMPLE FOUND**

## Meaning of PASS

PASS means that no reproducible counterexample was found within the exact tested
model, corpus, implementation, assumptions, repository state, and hostile-review
scope. It is an asymmetric falsification result, not proof of universal security.

## Explicit non-claims

This freeze does not claim formal proof, universal safety, complete authority
modeling, truthful external evidence, absence of hidden collusion, production
fitness, correctness of unmodeled effects, or direct observation of physical
reality. It does not authorize deployment or any future research claim.

## Frontier closure and version rule

The v1 sequence closes with objective binding, mutation closure, observation,
successor continuity, commitment and verifier durability, source/control-plane
independence, delegation, human approval, tool/target continuity, canonical T3,
and Composite review. No new authority-model frontier is part of Ground Truth v1
unless a reproducible counterexample against this frozen release candidate
reopens the research cycle.

Any new research must begin as an explicit post-freeze version. It must not
silently modify the v1 contract, corpus, verdicts, or evidence claims.

## Residual trust boundary

Ground Truth cannot locally detect a transition omitted before admitted evidence
construction, a consistent lie by all admitted sources, hidden collusion not
represented by protected source relations, compromise of the oracle or
canonicalization TCB, or a physical effect executed outside the modeled T3 path.
Runtime instrumentation, source truthfulness, durable anchor integrity, actual
independence, identity appraisal, and faithful effect execution remain external
trust assumptions.

## Publication-preparation next steps

1. Harvest exact manuscript evidence from this state.
2. Populate the evidence ladder and results table.
3. Use the canonical contract text without paraphrased drift.
4. Build the reproducibility package from exact commits and commands.
5. Perform a final manuscript and artifact hostile review.
6. Publish only after that separate human decision.
