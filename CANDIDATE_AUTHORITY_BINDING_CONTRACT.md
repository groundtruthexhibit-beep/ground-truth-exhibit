# Frozen Candidate Next-Layer Authority-Binding Security Contract

This document freezes a candidate security contract for a future Ground Truth authority-binding layer.

It is design-only. It does not authorize implementation, a later phase, production use, or any authority transition.

## Candidate authority-binding tuple

The candidate tuple is:

`(subject, artifact, control_state, identity_basis, boundary_epoch, decision)`

Configuration is part of `control_state`.

Selectors such as paths, names, tags, handles, roles, labels, replica names, PID/UID/session identifiers, and similar references may locate candidates but do not by themselves prove identity.

## Decision outcomes

`AUTHORIZED` means the applicable authority boundary, bound tuple, and decision contract have been established and the authority decision succeeds.

`DENIED` means the applicable boundary and tuple are established and the decision contract is evaluated, but the required conditions fail.

`UNAVAILABLE` means the applicable boundary, tuple continuity, discriminator legality, evidence binding, or required evaluation cannot be established.

`DENIED` and `UNAVAILABLE` are distinct diagnostics. Neither authorizes an authority-bearing transition.

## INV-CONT — Verification-to-use continuity

An authority decision applies only if the live consume-time tuple is shown to match the tuple established at verification.

If any bound component cannot be shown continuous at the authority-consuming transition, the result is `UNAVAILABLE`.

Detection only after consumption is forensic and is not sufficient authorization.

## INV-DISC — Identity-bearing discriminator discipline

Identity-bearing fields must be established by the applicable identity basis, not by selector stability or content equality alone.

This applies at minimum to:

- `subject`
- `artifact`
- `boundary_epoch`

Names, roles, paths, labels, tags, handles, replica names, PID/UID/session identifiers, and similar selectors are not sufficient proof of identity continuity.

Raw byte or digest equality may be evidence of content equality, but does not by itself prove object identity, subject identity, control-state continuity, provenance, or authority continuity.

## INV-BND — Boundary identity is independent and epoch-bound

The applicable authority boundary is part of the bound tuple.

The requesting subject cannot select, replace, route around, or bootstrap that boundary to obtain a favorable result.

Reciprocal, cyclic, delegated, or collusive agreement among models or agents does not create an independent authority boundary.

A change of verifier, store, replica authority state, restart lineage, fork, rejoin, restoration, or other authority-relevant boundary event requires a distinguishable live `boundary_epoch` unless continuity is independently established.

## Lineage-bearing epoch tightening

`boundary_epoch` is not a reusable or restorable label.

It represents non-restorable authority lineage.

Any authority-relevant restart, rollback, fork, replica divergence, restoration, or mutation that could make a previously valid tuple appear current again must produce a distinguishable live epoch.

Restoring old artifact or control-state bytes must not restore an old authority epoch.

Copied or replayed epoch labels do not prove lineage continuity.

## INV-EVD — Evidence is tuple-bound and non-promotable

Evidence is bound to the exact tuple and decision for which it was admitted.

Evidence is not authority.

Evidence from one tuple, state, boundary epoch, identity basis, or decision must not be silently reused for another.

Weaker evidence must not be promoted into satisfying a stronger applicable decision contract.

If the required evidence binding or applicable evaluation cannot be established, the result is `UNAVAILABLE`.

## INV-USE — Consumption is not last-known-good

A one-shot authority decision instance authorizes at most one authority-consuming transition.

A continuing grant remains usable only while its defined validity conditions remain satisfied for the same bound tuple.

A required re-evaluation returning `DENIED` or `UNAVAILABLE` does not silently preserve permission.

Restart, rollback, residue, cached success, or duplicated decision state does not recreate authority.

## INV-CLO — No implicit transformation closure

Authority over an artifact does not implicitly authorize a composition, partition, encoding, wrapper, projection, measurement report, derivative, or other transformed object.

A derived object requires its own exact binding unless the applicable decision contract explicitly defines that transformation as authority-preserving.

Even where a transformation is contract-permitted, evidence does not itself become authority.

## Hostile coverage summary

The candidate model has been challenged in design analysis against classes including:

- pathname and selector replacement
- rename and rebind
- unlink and recreate
- same-path different-object substitution
- same-bytes different-object substitution
- mutation between verification and use
- ABA identity reuse
- rollback and generation reuse
- process, verifier, and authority-store restart
- stale evidence replay
- stale-grant inheritance
- configuration rotation
- verifier replacement and verifier shopping
- reciprocal or collusive agent delegation
- concurrent mutation
- measure-one-submit-another substitution
- identity-basis migration
- fork and rejoin
- cloned epochs
- replica promotion and split-brain lineage
- subject revocation and rebinding
- credential rotation
- role and PID/UID/session reuse
- namespace replacement
- snapshot restoration
- cross-host migration
- multi-replica one-shot consumption
- nested, overlapping, and derived-object decisions

No surviving counterexample from the assigned hostile set required a seventh invariant after the lineage-bearing epoch and discriminator-discipline tightenings were applied.

This is a design-analysis result, not a proof or implementation claim.

## Unresolved and out-of-objective boundaries

This candidate contract does not claim to solve:

- compromise of the live applicable authority boundary
- collision or second-preimage failure in the active identity basis
- contracts that explicitly define bearer semantics
- diagnostic or timing side channels involving `DENIED` versus `UNAVAILABLE`

Those remain separate security objectives or trust assumptions.

## Authority boundary of this record

This document freezes candidate design semantics only.

It does not authorize implementation.

It does not authorize a new phase.

It does not modify Alpha completion state.

It does not authorize production deployment, certification, regulatory compliance, formal verification, or universal security claims.

Any future implementation requires a separate explicit human authority decision after independent review of this frozen candidate contract.
