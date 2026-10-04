# Ground Truth PHI Disclosure Authority — Reproducibility Manifest v1

## Scope

Synthetic PHI authority research only. No real PHI. No legal-compliance claim. No claim
that the pinned case-study system is vulnerable.

## Pinned external comparison

`ethereum/zkapi@045b444ea1b52538d1b40273c7cb6ed09468a052`

## Ground Truth public reference

`groundtruthexhibit-beep/ground-truth-exhibit@74cd883736c7acde1ff0d0d2ad765f6e8771def0`

## Frozen Ground Truth structure

Tuple:
`(subject, artifact, control_state, identity_basis, boundary_epoch, decision)`

Invariants:
`INV-CONT`, `INV-DISC`, `INV-BND`, `INV-EVD`, `INV-USE`, `INV-CLO`

Outcomes:
`AUTHORIZED`, `DENIED`, `UNAVAILABLE`

## Primary PHI invariant

`NO CURRENT PHI DISCLOSURE AUTHORITY -> NO EXTERNAL INFERENCE EFFECT`

## Attack families

1. cumulative disclosure composition
2. disclosure-history rollback / ABA
3. authorization-to-execution mutation
4. derived-disclosure laundering
5. cross-recipient correlation / effective-controller collapse
6. consent/revocation race and delayed execution
7. partial execution / ambiguous send outcome
8. cross-session / memory contamination
9. model/provider migration continuity
10. composite adversarial disclosure continuity

## Interpretation

The individual reproducers intentionally contain naive baselines that demonstrate each
failure class. The repaired gates are research models of the required fail-closed
semantics, not production implementations.

The final composite PASS means no bypass was reproduced against the synthetic composite
gate under the tested inputs. It does not establish universal security.

## Next phase

- consolidate a typed PHI disclosure-authority context;
- map each required relation to existing Ground Truth v1 structures;
- design exact fixtures rather than a parallel authority engine;
- preserve positive `AUTHORIZED` reachability;
- hostile-review the integrated repair;
- finish manuscript claims/limitations and publication packaging.
