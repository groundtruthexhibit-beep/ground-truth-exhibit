# Layer 2 Commit-Time Authority Review

## Status and scope

This is a fresh public design review of Layer 2 commit-time authority. Historical candidates are `UNAVAILABLE` to this review. This record does not claim continuity, validation, inheritance, or authority from them.

This document is design evidence only. It is not implementation authority, does not authorize a later phase, does not change the roadmap, and does not authorize deployment, production use, certification, compliance, or formal-verification claims. Human adoption or merge is a separate human authority decision and does not convert this review into implementation authority.

## Frozen Layer 2 vocabulary

The exact frozen authority tuple is:

`(subject, artifact, control_state, identity_basis, boundary_epoch, decision)`

It has exactly six coordinates. Configuration and all authority-relevant effect, ordering, dependency, revocation, and consumption facts required by the applicable decision contract are represented through `control_state`; they are not additional tuple coordinates. Consumption is a semantic transition, not a coordinate.

The exact outcomes are:

- `AUTHORIZED`: the applicable authority boundary, exact tuple, required evidence, live preconditions, and commit-time evaluation are established, and the requested authority-consuming transition is permitted.
- `DENIED`: the applicable boundary and exact tuple are established and evaluable, but an established condition prohibits the requested transition.
- `UNAVAILABLE`: any required boundary, tuple identity, evidence binding, continuity, ordering, consumption status, commit status, or evaluation cannot be established.

Only `AUTHORIZED` permits the exact requested transition. `DENIED` and `UNAVAILABLE` permit no authority-bearing effect. Uncertainty is never converted into `DENIED` merely to obtain a determinate answer, and neither non-success outcome is treated as authority.

## Frozen invariant set

The exact Layer 2 invariant identifiers are `INV-CONT`, `INV-DISC`, `INV-BND`, `INV-EVD`, `INV-USE`, and `INV-CLO`. The set is frozen at six for this review, but this review does not claim that it is mathematically minimal, universally complete, or sufficient for every implementation or future objective.

### INV-CONT — verification-to-commit continuity

The exact live tuple used by the irreversible transition must be shown continuous with the tuple evaluated for authority. Continuity must hold through the commit point, not merely at request receipt, evidence admission, validation, or effect preparation. A change or unresolvable gap in any coordinate before commitment yields `UNAVAILABLE`, unless an established applicable condition instead yields `DENIED`.

### INV-DISC — identity-bearing discriminator discipline

Identity-bearing values must be established by the applicable `identity_basis`. A path, name, label, role, handle, tag, replica name, PID, UID, session identifier, address, or byte equality may select or compare a candidate but does not alone prove the identity of `subject`, `artifact`, or `boundary_epoch`. Replacement, ABA reuse, rollback, restoration, cloning, and same-content substitution cannot inherit authority merely through a stable selector or equal bytes.

### INV-BND — independent epoch-bound boundary

The applicable authority boundary must be independently established and bound to a non-restorable authority lineage expressed by `boundary_epoch`. The requester cannot choose, replace, route around, bootstrap, or collude into a favorable boundary. Restart, fork, restore, replica divergence, promotion, rejoin, verifier replacement, or another authority-relevant lineage event must be distinguishable unless continuity is independently established.

### INV-EVD — exact evidence binding and non-promotion

Evidence is bound to the exact tuple and decision for which it was admitted. Evidence is not authority. It cannot be silently replayed across a subject, artifact, control state, identity basis, boundary epoch, or decision, and weak evidence cannot become stronger through relabeling, repetition, aggregation, transformation, or consensus. Missing required binding or evaluation yields `UNAVAILABLE`.

### INV-USE — commit-time consumption discipline

A one-shot authority instance authorizes at most one committed authority-consuming transition. A continuing grant remains usable only while its exact current validity conditions hold. Cached success, retry, restart, rollback, failover, residue, duplicate delivery, or absence of a consumption record cannot recreate authority. Unknown prior consumption does not become fresh authority; it yields `UNAVAILABLE`.

### INV-CLO — no implicit transformation or aggregate closure

Authority over an artifact does not implicitly authorize a composition, partition, encoding, wrapper, projection, report, derivative, batch, aggregate, or other transformed object. Each distinct authority-bearing result requires exact binding unless the applicable decision contract explicitly defines an authority-preserving transformation. Separate valid decisions do not imply authority for their combined outcome.

## Commit-time authority model

For one requested effect, Layer 2 distinguishes three conceptual times:

- **T1 — evaluation:** the applicable boundary evaluates the exact tuple and may return `AUTHORIZED`, `DENIED`, or `UNAVAILABLE`.
- **T2 — preparation:** the consumer may reserve, stage, fence, or otherwise prepare the exact effect without yet treating it as committed.
- **T3 — irreversible boundary:** the effect becomes externally authoritative or cannot be withdrawn without a separate authority-bearing action.

A valid T1 `AUTHORIZED` result is necessary but does not, by itself, authorize T3. The consumer must preserve the exact tuple, applicable boundary, required evidence relationship, live authority conditions, and consumption eligibility from evaluation through T3. Immediately before and at the irreversible boundary, the commit-time evaluation must still be `AUTHORIZED`. If that cannot be established, the commit outcome is `UNAVAILABLE` and the effect must not newly cross T3.

T2 is not permission to publish, expose, apply, transfer, spend, actuate, or otherwise make the effect authoritative. Preparation must remain safely abortable or fenced from external authority until the T3 requirements are satisfied.

## Exact effect mapping

The following mapping is explicit Layer 2 semantics for the exact requested effect:

| Commit-time result | Required Layer 2 effect |
| --- | --- |
| `AUTHORIZED` and exact one-shot consumption is established at T3 | Commit that exact effect once; record no authority for any different or aggregate effect. |
| `AUTHORIZED` and an applicable continuing grant remains current at T3 | Commit only the exact effect and scope permitted by the current contract. |
| `DENIED` before T3 | Do not cross T3; discard or safely neutralize preparation. |
| `UNAVAILABLE` before T3 | Do not cross T3; fail closed and preserve uncertainty. |
| T3 may have occurred but commit or consumption cannot be established | Return and retain `UNAVAILABLE`; do not retry as fresh, do not assert non-commit, and do not reuse the authority instance. |
| T3 is established as committed but its acknowledgment is lost | Treat the effect as committed and the one-shot authority as consumed; lost acknowledgment is not non-commit. |

This mapping does not authorize compensation, rollback, a second effect, or retry. Any such authority-bearing action requires its own exact applicable tuple and decision.

## Aggregate and transaction semantics

Layer 2 provides no implicit aggregate atomicity. Individual `AUTHORIZED` decisions do not imply that all effects in a batch, transaction, graph, quorum result, handoff, or workflow commit together, nor that partial commit is impossible. An aggregate effect is a distinct artifact or contract scope under `INV-CLO` and must be explicitly bound in the tuple and `control_state`.

If the contract requires all-or-nothing behavior, the applicable authority design must explicitly identify the aggregate, its participants, ordering, failure semantics, and irreversible boundary. This review names that obligation but does not claim a public implementation mechanism or that atomicity exists.

## Ambiguity, acknowledgment, and recovery

Ambiguous commit fails closed. Absence of a local record, receipt, response, observation, or acknowledgment is not proof that T3 did not occur. Conversely, an attempted operation is not proof that T3 occurred. When authoritative commit state cannot be established, the outcome is `UNAVAILABLE` and uncertainty must remain durable rather than being repaired into apparently unused authority.

A lost acknowledgment after an established commit does not undo the commit and does not restore the grant. A timeout cannot convert a possibly consumed one-shot decision into fresh authority. Recovery, failover, replay, operator intervention, or replica promotion must not infer non-consumption from missing local state.

The strongest near-counterexample is: T1 returns `AUTHORIZED` for an unused one-shot decision; the effect crosses T3; the acknowledgment and local consumption write are lost; recovery observes the old decision as apparently unused and retries. The retry is blocked because lost acknowledgment is not non-commit, unknown prior consumption is not fresh authority, and `INV-CONT` plus `INV-USE` require `UNAVAILABLE`. Preventing or reconciling that state is an implementation obligation, not evidence that the first T1 result authorizes a second T3.

## Seventh-coordinate and seventh-invariant challenge

This review attempted to add `commit`, `effect`, `consumption`, `time`, and `transaction` as a seventh tuple coordinate. None is admitted. The `artifact` and `decision` identify what is requested, while authority-relevant commit, effect, ordering, transaction, and consumption facts required to decide it belong in `control_state`. T1/T2/T3 describe evaluation semantics and the authority-consuming transition; they do not change tuple arity. Omitting a required fact from `control_state` makes evaluation `UNAVAILABLE` rather than creating an implicit coordinate.

This review also challenged the six invariants with a proposed seventh invariant, “commit atomicity.” The proposal does not survive as an independent Layer 2 semantic invariant. For a single exact effect, authority continuity through T3 is required by `INV-CONT`, one-shot exclusivity and uncertainty are required by `INV-USE`, and a different aggregate effect is blocked by `INV-CLO`. Atomic fencing, durable recording, idempotency, reconciliation, and transaction protocols are implementation obligations. Where an aggregate atomicity claim is desired, it must be an explicit contract property; Layer 2 does not supply it implicitly.

Determination: no seventh coordinate or seventh invariant is required by this bounded design challenge. This is not a claim that six invariants are minimal, that all possible attacks have been enumerated, or that a future changed objective could not require another coordinate or invariant.

## Six unresolved boundaries

The following six boundaries remain unresolved and are preserved rather than claimed as solved:

1. **Compromised live applicable authority boundary.** The model does not prove correct decisions when the live boundary or its controlling trust root is compromised.
2. **Identity-basis failure.** Collision, second-preimage, corruption, forgery, or failure of properties assumed by the active `identity_basis` remains outside the reviewed guarantee.
3. **Explicit bearer semantics.** A contract that intentionally treats possession as authority has separate semantics and must state them explicitly; this review neither imports nor resolves them.
4. **`DENIED`/`UNAVAILABLE` side channels.** Timing, diagnostics, traffic shape, and other observability differences between these results are not claimed confidential or indistinguishable.
5. **External-world commit observability and enforcement.** The mechanisms that fence, durably identify, reconcile, or prove an irreversible effect across external systems are private implementation and integration obligations, not solved by this public design review.
6. **Contract completeness and aggregate guarantees.** The review does not prove that every authority-relevant fact has been modeled, that arbitrary multi-effect systems are atomic, or that the invariant set is minimal or universally complete.

These boundaries do not relax fail-closed behavior. If a required fact within an applicable evaluation cannot be established because one of them is encountered, Layer 2 does not manufacture `AUTHORIZED`.

## Hostile-review verdict

**PASS — bounded design review only.** No publication-blocking internal contradiction, tuple expansion, outcome expansion, invariant expansion, T1-to-T3 authority shortcut, implicit aggregate atomicity, optimistic ambiguous-commit retry, historical-authority claim, or private-detail disclosure was found in this document.

The strongest near-counterexample is the committed-effect/lost-acknowledgment/retry case above. It is contained by `INV-CONT`, `INV-USE`, explicit T3 effect mapping, and `UNAVAILABLE`; it exposes demanding implementation obligations but no independent seventh invariant.

PASS is review evidence, not proof, authority, implementation readiness, roadmap movement, or permission to begin a later phase.

## Public/private and authority boundary

This public record states only design semantics, hostile reasoning, outcome mapping, trust boundaries, and implementation obligations at an abstract level. It discloses no private source, validator, enforcement workflow, database schema or migration, test or adversarial fixture, evidence archive, credential, key, endpoint, environment configuration, deployment topology, recovery procedure, or unpublished implementation mechanism.

The private authoritative core remains separate from this public exhibit. Nothing here asserts that the private core implements these semantics or authorizes disclosure of private evidence.

Implementation remains unauthorized. No later phase is authorized. The roadmap is unchanged. Human adoption remains a separate explicit decision. Publication or merge of this design evidence does not create authority.
