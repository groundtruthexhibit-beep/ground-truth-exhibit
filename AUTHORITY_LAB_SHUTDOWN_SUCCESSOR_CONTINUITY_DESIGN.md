# Authority Lab v1 Shutdown / Successor Continuity — Design

## Status and constraints

This document specifies the smallest executable repair for the authority-after-shutdown and successor-ABA counterexample recorded in `FRONTIER_DELTA_SHUTDOWN_CONTINUITY.md` at commit `01c77b032c47f6e5efee8709508ab7685b3f92a0`.

It is design-only. It does not modify Authority Lab, authorize merge or deployment, describe an offensive shutdown bypass, or claim production process identity.

The design preserves exactly:

- schema identifier `authority-lab-v1`;
- tuple `(subject, artifact, control_state, identity_basis, boundary_epoch, decision)` — six coordinates;
- invariants `INV-CONT`, `INV-DISC`, `INV-BND`, `INV-EVD`, `INV-USE`, and `INV-CLO` — six invariants; and
- outcomes `AUTHORIZED`, `DENIED`, and `UNAVAILABLE` — three outcomes.

It adds no `was_shutdown`, `successor_authorized`, `same_process`, or equivalent unchecked assertion. It adds no tuple coordinate, invariant, outcome, or schema version.

The core rules are:

> Same apparent state does not imply same authorized history.

> A terminal, identity-discontinuous, or non-restorable lineage event ends predecessor authority continuity. Later label equality cannot undo that event.

> A successor is authorized only by an independently established current successor chain, never by inheritance from predecessor evidence, credentials, state, labels, or grants.

## 1. Defect summary

The mutation registry is closed and every admitted mutation is checked, but current continuity evaluation is endpoint-oriented. `_mutation_chain_mismatches` validates the ordered `before -> after` chain and its final T3 value. `_state_differences` compares only the final authority state against T1 or `reestablishment.current`. If a path returns to predecessor-shaped values, the intermediate authority consequence can disappear.

The current generic `reestablishment` relation binds `previous_evidence_id` to a current state snapshot. A different evidence identifier proves freshness of that evidence identifier, not successor identity, authority-source admission, lifecycle continuity, or grant portability. When the final scope equals T1, `grant_scope_changed` is false and the old grant can remain usable.

The result is one composition defect:

```text
checked ordered mutation path
        + endpoint-only state comparison
        + generic evidence refresh
        + final-label equality
        = predecessor authority may survive a discontinuous history
```

The repair must evaluate the complete admitted path before it evaluates endpoint equality.

## 2. Exact executable counterexamples

Starting from maintained positive fixture `LAB-V1-032`, the reviewed research supplied a distinct T3 decision-binding evidence identifier and the current generic `reestablishment`, while retaining the predecessor grant and final state labels.

Each path below returns:

```text
AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED
```

when the required result is `UNAVAILABLE` absent independent successor admission:

```text
execution_context: E1 -> TERMINATED -> E1
subject: S -> SUCCESSOR-B -> S
boundary_epoch: B1 -> B2 -> B1
```

Two additional manifestations are:

- `execution_context: E1 -> PROCESS-P2 -> E1` with predecessor authority restored by label; and
- `commit_state: RUNNING -> SHUTDOWN_ACKNOWLEDGED` while an alternate execution path retains predecessor authority.

The boundary case is decisive: the public contract already defines `boundary_epoch` as a non-restorable lineage. `B1 -> B2 -> B1` therefore cannot mean that the first B1 authority silently returned.

Controls behave correctly:

- a distinct visible child, delegate, relay, proxy, or process without exact current authority returns `UNAVAILABLE`;
- a current applicable prohibition or revocation returns `DENIED`; and
- a fully independently admitted new boundary path such as `LAB-V1-048` can reach `AUTHORIZED`.

## 3. Normative contract basis

| Existing rule | Shutdown/successor consequence |
| --- | --- |
| T3 must establish the exact live tuple, boundary, objective binding, evidence relationship, authority state, and use eligibility. | A predecessor result cannot authorize a later consumer merely because its labels reappear. |
| `INV-CONT` requires continuity through commit or exact current re-establishment. | Every authority-relevant edge in the T1-to-T3 path must retain an authority consequence. |
| `INV-DISC` rejects replacement, ABA reuse, rollback, restoration, cloning, aliasing, and stable selectors as identity proof. | Same subject, PID-like context, code hash, or bytes do not prove the same execution identity. |
| `INV-BND` binds authority to a non-restorable `boundary_epoch`. | A prior epoch label cannot be resurrected after an authority-relevant epoch transition. |
| `INV-EVD` says evidence is exact-transition-bound and is not authority. | A new generic evidence ID cannot admit a successor or make an old grant portable. |
| `INV-USE` prevents restart, rollback, recovery, residue, or missing records from recreating authority. | A predecessor grant cannot become an unused successor grant after termination or restore. |
| `INV-CLO` rejects implicit authority for children, wrappers, copies, relays, and derived consumers. | Child, clone, checkpoint, shared-state, and alternate paths require exact current authority of their own. |
| Observation completeness is root-issued, ordered, current, gapless, and transformation-preserving. | Terminal and successor events must remain in the admitted path and cannot be laundered through silence or lossy summary. |
| Objective binding must remain exact, current, scoped, sourced, and ordered through T3. | A successor must be within the exact current binding; unchanged objective text is insufficient. |

These are already the necessary semantics. The defect is failure to compose them over the full path, not absence of a seventh semantic dimension.

## 4. Path-sensitive continuity model

### 4.1 One authoritative path

The existing ordered `t2.mutations` array is the executable transition path. Alias resolution first maps every entry into the immutable closed mutation registry. Mutations resolving to the same semantic target remain one ordered chain.

For each target, the oracle must retain:

- the T1 value;
- every ordered intermediate value;
- the final T3 value;
- whether any value was revisited;
- the registry-owned continuity effect of every edge; and
- the observation scope family required to cover that edge.

The oracle must not replace this path with only `(T1, T3)`.

### 4.2 Registry-owned continuity effects

`MutationSpec` gains immutable evaluator metadata, not fixture-controlled fields:

| Continuity effect | Existing targets | Minimum consequence |
| --- | --- | --- |
| `IDENTITY_DISCONTINUITY` | `subject`, `identity_basis`, `execution_context`, `subject_mode`, identity-relevant delegation change | Predecessor execution identity cannot be presumed; successor-specific establishment is required. |
| `NON_RESTORABLE_LINEAGE` | `boundary_epoch`, `applicable_boundary`, `boundary_epoch_binding`, authority-root lineage change | A prior epoch/root lineage cannot be restored by label equality. |
| `TERMINAL_DISCONTINUITY` | any pre-T3 `commit_state` transition; observer/control lifecycle termination remains handled by existing observation lifecycle semantics | Predecessor execution and grant continuity end; successor-specific establishment is required. |
| `GRANT_USE_DISCONTINUITY` | `grant_id`, `consumption_state`, `consumption_binding` | Predecessor grant/use state cannot be carried through a rollback-shaped or regenerated path. |
| `CONTROL_REESTABLISHMENT` | `control_state`, `execution_control_binding`, credential/tool facts | Exact current execution-control and identity relations must be re-established; terminal observation escalates this to successor admission. |
| `EVIDENCE_OR_EFFECT_REESTABLISHMENT` | artifact, decision/evidence, closure, observation, and transformation relations | Existing evidence, transformation, and closure rules remain mandatory. |
| `OBJECTIVE_AUTHORITY_REESTABLISHMENT` | objective/root/source/lifecycle/ordering targets | Existing objective-binding source, lifecycle, and ordering checks remain mandatory. |

This table is an allowlisted semantic mapping owned by the same registry that admits mutation fields. Fixtures cannot downgrade a target's effect. Unknown targets retain the existing `UNAVAILABLE / UNKNOWN_MUTATION_FIELD` behavior.

### 4.3 Path rules

The deterministic path algorithm is:

1. Resolve and validate every mutation through the closed registry.
2. Validate exact chain order and exact T3 termination as today.
3. Accumulate continuity effects across every edge, including intermediate edges whose values later disappear from the endpoint.
4. Mark the predecessor identity as discontinuous after any identity, non-restorable-lineage, or terminal edge.
5. Mark the predecessor grant non-portable after any identity, lineage, terminal, or grant/use discontinuity.
6. Treat any return to an earlier value as an ABA event. ABA never removes an accumulated effect. An ABA on any authority-relevant state, relation, or fact escalates ordinary endpoint re-establishment to path-discontinuity handling; for identity, lineage, control, or lifecycle targets it requires the complete successor/re-entry chain.
7. Map each edge to the existing required observation family and require current root-admitted coverage, freshness, ordering, and transformation continuity for that family across the full interval.
8. Apply current authoritative negative evidence only after its exact applicability is established.
9. Resolve the accumulated effects by class: ordinary control/evidence/objective changes use their existing exact re-establishment rules; a grant/use discontinuity additionally requires a non-reused exact current grant path; an identity, non-restorable-lineage, terminal, or escalated ABA effect requires the complete successor/re-entry requirements in section 6. Permit `AUTHORIZED` only after every accumulated effect is satisfied.

The accumulated effect is monotonic for the evaluated path. It may be satisfied by new authority, but it cannot be erased by a later label.

### 4.4 No input-schema expansion

The repair needs no new fixture field. It composes:

- the existing ordered mutation array;
- registry-owned target metadata;
- existing `reestablishment.current` exact state;
- existing root, source, objective-binding lifecycle and ordering facts;
- existing observation coverage, freshness, handoff, and transformation facts; and
- existing grant, consumption, delegation, closure, execution, identity, boundary, and prohibition facts.

`reestablishment` remains a state/evidence relationship and never becomes source authority. Independent authority is derived from the existing current root/objective/observation/grant composition.

## 5. Terminal-event semantics

Terminality is semantic, not a spelling test. The implementation must not search for strings such as `TERMINATED`, `SHUTDOWN`, `DEAD`, `STOPPED`, or `RESTARTED`.

The following existing semantic events have persistent authority consequences:

| Event class | How v1 recognizes it | Persistent consequence |
| --- | --- | --- |
| Execution identity discontinuity | A registered identity-bearing target changes anywhere in the path. | Predecessor identity continuity ends. |
| Successor/replacement | Subject, identity basis, execution context, subject mode, or exact delegation path changes. | Candidate consumer must be independently established. |
| Non-restorable boundary transition | Boundary, epoch, boundary relation, or root lineage changes. | Prior epoch authority cannot be restored. |
| Commit/lifecycle terminal transition | Any admitted pre-T3 `commit_state` mutation. | Predecessor execution and grant continuity end; successor rules apply. |
| Grant/use lifecycle discontinuity | Grant, consumption, or consumption-relation path changes incompatibly or returns to prior state. | Predecessor grant is non-portable. |
| Observer/control-plane termination | Existing observation lifecycle is missing, invalid, revoked, rejected, superseded, stale, or has a gap/handoff failure. | Continuity is `UNAVAILABLE`, or `DENIED` for an exactly applicable current authoritative negative state. |
| Explicit predecessor revocation/prohibition | Existing current root/objective/observer/prohibition facts establish exact applicability. | `DENIED`; restored labels cannot outrank the negative state. |

`commit_state` remains an auxiliary fact, not a new authority primitive. Any admitted pre-T3 `commit_state` mutation is conservatively classified as a terminal discontinuity: T2 preparation cannot itself perform or reverse an authority-bearing commit/lifecycle transition. A mutation cannot self-classify as harmless; exact current successor, grant/use, and observation relations must establish the later authority state. This closes the shutdown-acknowledged alternate-path case without maintaining a blacklist of shutdown words.

A reversible non-identity control change may be satisfied through exact current re-establishment under the same live identity. It does not automatically become a successor event. However, an identity, epoch, or terminal/use break always escalates to successor/re-entry rules.

## 6. Successor identity and independent re-establishment

### 6.1 Same code is not same execution identity

A restarted process, child promoted to primary, replacement agent, restored snapshot, clone, new process using old labels, shared-state consumer, or alternate execution path is a successor candidate. Software hash, model weights, state bytes, task name, subject label, process label, account name, credential possession, or checkpoint equality cannot establish continuity.

The current identity is established only through the composition of:

- exact `subject` and `identity_basis`;
- exact current `execution_context` and `execution_control_binding`;
- exact current `applicable_boundary`, `boundary_epoch`, and `boundary_epoch_binding`;
- exact delegation/closure relations for the current consumer and effect;
- current root/source authority and objective-binding scope;
- root-admitted observation of the complete transition path; and
- exact current grant/use state.

### 6.2 Required successor chain

After an accumulated identity, lineage, or terminal discontinuity, `AUTHORIZED` requires all of the following:

1. `reestablishment` is `KNOWN`, links the T1 evidence identifier, and exactly matches the current T3 state.
2. The current evidence identifier is distinct and applies to the exact successor transition; it is necessary but not sufficient.
3. The successor's identity basis and execution-control relationship establish the current consumer rather than merely repeat a selector.
4. The current boundary epoch is a fresh non-restored lineage. Re-entry to the same named boundary uses a new epoch, not the old epoch label.
5. The current authority root is valid for that epoch, lineage, ordering source, and boundary.
6. The exact objective binding is current and scoped to the successor state. A binding generation selected before the discontinuity cannot be reused as successor admission.
7. Observation coverage is root-issued, current, gapless, ordered, scope-complete, and transformation-preserving across the terminal event and successor establishment.
8. The successor uses a distinct current grant and exact successor-bound `consumption_binding`; predecessor grants and authority-preserving grant transitions do not cross a terminal break.
9. Delegation and closure bind the exact current successor and effect; parenthood, relay, wrapper, copied state, or shared memory cannot substitute.
10. No exact current prohibition, revocation, rejection, invalidity, supersession, or conflict applies.

The same root may issue new successor authority within the same named boundary, but it must do so under the current non-restored epoch and ordering. The root does not need to become a new conceptual authority merely because it issues a new exact binding.

### 6.3 Existing `reestablishment` is not self-attestation

The existing `reestablishment` object remains unchanged in shape. Its `current` snapshot cannot authorize itself. The oracle accepts it only after the independent current root, objective binding, observation binding, boundary, execution, identity, grant/use, delegation, closure, lifecycle, and ordering relations agree with it.

An agent, successor, child, checkpoint, credential, observer, wrapper, summary, relay, or generic evidence producer cannot issue those authority relations merely by supplying `reestablishment`.

## 7. Grant/use portability rules

### 7.1 Terminal non-portability

Once an identity, lineage, or terminal/grant-use discontinuity is accumulated:

- the predecessor `grant_id` is not reusable by the successor, even if it was `UNUSED`;
- the predecessor `consumption_binding` cannot be copied, restored, or retargeted;
- an old credential does not make the old grant portable;
- a new generic evidence identifier does not refresh the old grant;
- unchanged objective text does not preserve the old grant;
- rollback to `UNUSED` remains forbidden; and
- an `AUTHORITY_PRESERVING` `grant_transition` cannot bridge the terminal break.

The successor requires a distinct grant identity and a current `consumption_binding` to its exact subject, artifact, and fresh boundary epoch. The current observation profile must cover grant issuance and use throughout the successor interval.

### 7.2 Non-terminal grant transition

The existing `grant_transition` relation remains available only for a non-terminal, continuity-preserving scope transition. It must still bind the exact previous/current states and complete grant path. If any accumulated path effect is identity-discontinuous, terminal, non-restorable, or grant-regenerating, `grant_transition.relationship = AUTHORITY_PRESERVING` is inapplicable and the result is `UNAVAILABLE`.

### 7.3 Negative grant state

Current authoritative revocation, rejection, invalidity, supersession, or prohibition of the exact predecessor/successor grant yields `DENIED` only when applicability to the current tuple and path is independently established. Missing or ambiguous portability yields `UNAVAILABLE`.

## 8. Boundary-epoch ABA rules

`boundary_epoch` is a lineage discriminator, not a reusable location label.

For any path:

```text
B1 -> B2 -> B1
```

the final `B1` is a repeated label, not restoration of the first B1 lineage. The oracle must retain the `NON_RESTORABLE_LINEAGE` effect and return `UNAVAILABLE / BOUNDARY_EPOCH_REUSE_UNAVAILABLE` unless current authoritative negative evidence establishes `DENIED`.

Legitimate re-entry into the same named boundary uses:

```text
applicable_boundary: AUTH-BOUNDARY-1 -> OTHER -> AUTH-BOUNDARY-1
boundary_epoch: B1 -> B2 -> B3
```

where B3 is a fresh lineage. T3 must establish the B3 root/boundary relation, identity basis, execution context, objective-binding generation, observation coverage, evidence, grant, consumption binding, and ordering. The original B1 grant and evidence remain non-portable.

The same rule applies to root-lineage ABA, restored checkpoints, replica promotion/rejoin, crash recovery, and fork/re-entry. Label equality never decrements or erases the accumulated lineage effect.

## 9. Observation-binding requirements

The Observation Admission and Completeness implementation already supplies the required trust placement. This design reuses it rather than adding a shutdown flag.

For every admitted mutation, the registry maps its semantic target to one or more existing immutable scope families:

- subject/delegation changes -> `SUBJECT_AND_DELEGATION`;
- artifact/closure/transform changes -> `ARTIFACT_AND_TRANSFORMATION`;
- execution/control/commit changes -> `EXECUTION_CONTROL` and, where use-relevant, `GRANT_USE_AND_CONSUMPTION`;
- boundary/epoch/root-lineage changes -> `BOUNDARY_AND_EPOCH`;
- identity/credential changes -> `CREDENTIAL_AND_IDENTITY`;
- grant/consumption changes -> `GRANT_USE_AND_CONSUMPTION`;
- root/objective/lifecycle/order changes -> `OBJECTIVE_AUTHORITY_LIFECYCLE`; and
- observer, stream, handoff, summary, and wrapper changes -> `OBSERVATION_PIPELINE`.

Before a mutation path can support `AUTHORIZED`, the existing observation evaluator must establish gapless current coverage for every mapped family across the T1-to-T3 anchors. The oracle then evaluates the complete ordered mutation path; it does not infer continuity from an empty endpoint diff.

Existing transformation rules remain exact: a summary, wrapper, reducer, adapter, or relay must have an admitted observation-preserving transformation with matching commitments and no scope loss. A terminal event present in the admitted mutation path cannot be dropped merely because a transformed endpoint looks unchanged.

Observer substitution during shutdown requires both observers to be independently admitted, a current root-issued exact handoff, continuous required scope, no interval gap, valid sequence/order, and transformation continuity. A valid observer handoff preserves observation coverage only; it does not preserve predecessor execution authority or grant portability.

If a real terminal event is omitted before construction of the admitted mutation/observation input, the external observation-root limitation remains: identical oracle inputs cannot distinguish the two worlds. That known limitation is not treated as repaired here. Within the admitted input boundary, a visible terminal event can no longer disappear through endpoint collapse.

## 10. Shutdown, restart, crash, and re-entry semantics

| Transition | Authority treatment |
| --- | --- |
| Graceful shutdown or acknowledged terminal use state | Ends predecessor execution/grant continuity when present in the admitted path. |
| Authoritative shutdown instruction or current prohibition | `DENIED` when exact current applicability is established. |
| Process death or crash with no authoritative prohibition | Identity continuity is unavailable; successor rules apply. |
| Restart with same labels | Labels are selectors only; fresh identity basis, epoch, current authority chain, observation, and grant are required. |
| Child survives parent shutdown | Child is a distinct subject/consumer; no implicit inheritance. |
| Checkpoint restore or clone | Copied state is an artifact/evidence input, not execution identity or authority. |
| Alternate path survives shutdown | The alternate path is a successor candidate; familiar final labels do not preserve authority. |
| Re-entry into the same named boundary | Permitted only under a fresh non-restored epoch and complete new authority chain. |
| Observer terminates during execution | Missing current coverage is `UNAVAILABLE`; exact applicable observer prohibition/revocation may be `DENIED`. |

Crash without an explicit shutdown word is not a loophole. Identity/context/epoch discontinuity and observation gaps, not a string label, trigger fail-closed successor handling.

## 11. `DENIED` versus `UNAVAILABLE`

| Condition | Outcome |
| --- | --- |
| Missing, stale, ambiguous, conflicting, incomplete, or not-provably-current path continuity | `UNAVAILABLE` |
| Successor identity, current epoch, observation coverage, objective binding, grant/use, delegation, or closure not independently established | `UNAVAILABLE` |
| Generic evidence refresh, old credential, label restoration, code/hash equality, checkpoint equality, parenthood, relay, or shared state offered as successor authority | `UNAVAILABLE` |
| Terminal event present but observation provenance/order/transformation continuity incomplete | `UNAVAILABLE` |
| Current authoritative shutdown, revocation, rejection, invalidity, supersession, or prohibition applies to the exact current subject/path | `DENIED` |
| Fresh current successor/re-entry chain satisfies every existing requirement and no negative state applies | `AUTHORIZED` remains possible |
| Malformed strict input | Existing input/schema failure path; no authority outcome |

Uncertainty is never converted into `DENIED`. Conversely, restored labels do not weaken an established applicable prohibition into `UNAVAILABLE`.

## 12. Hostile fixture matrix

Every case assumes structurally valid `authority-lab-v1` input. “Fresh evidence” means evidence required in addition to ordinary mandatory T3 facts; it never means evidence alone grants authority.

| ID | Scenario | Expected / reason class | Predecessor grant reusable? | Path restorable? | Required fresh evidence | Invariants |
| --- | --- | --- | --- | --- | --- | --- |
| A | `execution_context A -> B -> A` | `UNAVAILABLE / PATH_CONTINUITY_UNAVAILABLE` | No | No | Exact successor identity/context, fresh epoch, root/objective/observation chain, new grant | `INV-CONT`, `INV-DISC`, `INV-USE` |
| B | `subject A -> B -> A` | `UNAVAILABLE / SUCCESSOR_IDENTITY_UNAVAILABLE` | No | No | Exact current identity basis, delegation/closure, observation, objective binding, new grant | `INV-CONT`, `INV-DISC`, `INV-CLO`, `INV-USE` |
| C | `boundary_epoch B1 -> B2 -> B1` | `UNAVAILABLE / BOUNDARY_EPOCH_REUSE_UNAVAILABLE` | No | No | Fresh non-restored epoch, root lineage/order, observation, objective binding, new grant | `INV-BND`, `INV-DISC`, `INV-USE` |
| D | Restart with same labels and old grant | `UNAVAILABLE / PREDECESSOR_GRANT_NONPORTABLE` | No | No | Fresh successor identity/epoch plus distinct successor grant/use binding | `INV-DISC`, `INV-BND`, `INV-USE` |
| E | Restart with same labels and new generic evidence ID only | `UNAVAILABLE / SUCCESSOR_AUTHORITY_UNAVAILABLE` | No | No | Full current successor chain; evidence ID alone is insufficient | `INV-EVD`, `INV-DISC`, `INV-USE` |
| F | Child survives parent shutdown | `UNAVAILABLE / SUCCESSOR_IDENTITY_UNAVAILABLE` | No | No | Child-specific subject, identity, exact delegation, closure, epoch, objective/observation, new grant | `INV-DISC`, `INV-CLO`, `INV-USE` |
| G | Successor reuses predecessor credential | `UNAVAILABLE / SUCCESSOR_IDENTITY_UNAVAILABLE` | No | No | Independent identity basis and successor authority; credential possession is only evidence | `INV-DISC`, `INV-BND`, `INV-EVD` |
| H | Copied checkpoint resumes elsewhere | `UNAVAILABLE / CLOSURE_RELATIONSHIP_UNAVAILABLE` | No | No | Current transformed artifact/closure, execution identity, epoch, objective/observation, new grant | `INV-DISC`, `INV-EVD`, `INV-CLO`, `INV-USE` |
| I | Shutdown acknowledged but alternate execution persists | `UNAVAILABLE / PREDECESSOR_GRANT_NONPORTABLE` | No | No | Alternate-path successor identity, current root-observed path, objective binding, new grant | `INV-CONT`, `INV-DISC`, `INV-USE`, `INV-CLO` |
| J | Predecessor explicitly revoked, then labels restored | `DENIED / T3_OBJECTIVE_BINDING_DENIED` or `ESTABLISHED_PROHIBITION`, according to the existing applicable negative fact | No | No | Only a separately scoped new successor chain can escape predecessor-only revocation; applicable current revocation remains denial | `INV-CONT`, `INV-BND`, `INV-USE` |
| K | Stale observation omits terminal event | `UNAVAILABLE / OBSERVATION_FRESHNESS_UNAVAILABLE` | No | No | Current root-issued coverage through exact T3; an upstream unreported event remains a trust-root limitation | `INV-CONT`, `INV-EVD`, `INV-BND` |
| L | Transformed summary removes intermediate shutdown | `UNAVAILABLE / OBSERVATION_TRANSFORMATION_UNAVAILABLE` | No | No | Exact observation-preserving transformation and unchanged required scope/commitment | `INV-EVD`, `INV-CLO`, `INV-CONT` |
| M | Duplicate shutdown events | `UNAVAILABLE / TERMINAL_EVENT_ORDERING_UNAVAILABLE` | No | No | One exact non-conflicting ordered path and current observation commitment | `INV-CONT`, `INV-EVD`, `INV-USE` |
| N | Reordered terminal events | `UNAVAILABLE / TERMINAL_EVENT_ORDERING_UNAVAILABLE` | No | No | Exact chain order, root ordering, stream sequence, and current T3 head | `INV-CONT`, `INV-EVD`, `INV-BND` |
| O | Conflicting terminal observations | `UNAVAILABLE / OBSERVATION_CONFLICTING` | No | No | Independent authoritative conflict resolution or exact applicable negative state; no majority vote | `INV-EVD`, `INV-BND`, `INV-CONT` |
| P | Fully fresh independently admitted successor | `AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED` | No; new grant | No; authority is newly established | Exact successor identity, fresh epoch/root/objective/observation/evidence/grant/use/delegation/closure chain | All six |
| Q | Legitimate re-entry into original named boundary with new chain | `AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED` | No; new grant | Old epoch no; named boundary may recur | New epoch B3, current root/order, identity/context, objective/observation, new grant/use | All six |
| R | Crash/restart without explicit shutdown | `UNAVAILABLE / SUCCESSOR_IDENTITY_UNAVAILABLE` | No | No | Gapless crash observation or fail-closed gap handling, fresh identity/epoch and successor chain | `INV-CONT`, `INV-DISC`, `INV-BND`, `INV-USE` |
| S | Observer handoff during shutdown, but no successor admission | `UNAVAILABLE / SUCCESSOR_AUTHORITY_UNAVAILABLE` | No | No | Exact root-issued observer handoff preserves coverage; separate successor identity/objective/grant chain is still required | `INV-CONT`, `INV-EVD`, `INV-BND`, `INV-USE` |
| T | Same code/hash but new execution identity | `UNAVAILABLE / SUCCESSOR_IDENTITY_UNAVAILABLE` | No | No | Exact current identity basis, context, epoch, objective/observation, and new grant; byte equality is insufficient | `INV-DISC`, `INV-EVD`, `INV-USE` |

For J, a revocation scoped only to the predecessor does not permanently prohibit a separately identified successor. The oracle must first establish which identity and scope the negative state applies to. It must not use label equality to broaden or evade revocation.

## 13. Positive successor `AUTHORIZED` path

A maintained positive fixture should have this exact shape:

1. At T1, predecessor `A` is authorized under identity basis `I1`, context `E1`, boundary `AB1`, epoch `B1`, evidence `EV1`, grant `G1`, and the exact current objective/observation bindings.
2. Root-admitted ordered observation records A's terminal event and the successor transition across every required scope family.
3. At T3, successor `B` is established under identity basis `I2`, context `E2`, the applicable current boundary, and a fresh non-restored epoch `B2` (or B3 for re-entry to the original named boundary).
4. `reestablishment.previous_evidence_id` links to EV1, while `reestablishment.current` exactly matches B and uses distinct transition-specific evidence EV2.
5. The current root, source authority, binding lifecycle, binding ordering, and objective binding select the exact successor scope and occur after the discontinuity.
6. The current observation binding references that exact objective-binding generation and remains gapless, fresh, ordered, handoff-complete, and transformation-preserving through T3.
7. B uses a new grant G2 with a current exact `consumption_binding`; G1 is not carried through a grant transition.
8. Current execution-control, boundary, delegation, closure, consumption, and prohibition checks all succeed.

Expected result:

```text
AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED
```

`LAB-V1-048` already demonstrates most of this shape for a fresh cross-boundary path. The successor fixture extends it with explicit predecessor termination and a current successor subject/identity chain. Shutdown therefore ends predecessor continuity; it does not make all future execution permanently impossible.

## 14. Mapping onto existing facts

| Existing structure | Repair role | Design change |
| --- | --- | --- |
| `t2.mutations` | Ordered admitted T1-to-T3 path | Preserve every intermediate edge and accumulate its continuity effect. |
| `MUTATION_SPECS` / registry | Closed mapping from field to semantic target | Add immutable continuity-effect and observation-scope metadata; no fixture-controlled policy. |
| `subject` | Current logical authority consumer | Compare as part of path and successor identity, not as a sufficient selector. |
| `identity_basis` | Discriminator for current subject/execution identity | Any discontinuity requires exact fresh successor identity; old basis cannot be restored by label. |
| `execution_context` | Current execution instance/context selector | Path-sensitive; same final label does not erase an intervening instance. |
| `execution_control_binding` | Exact current context-to-control relation | Must bind successor context and current control state. |
| `applicable_boundary` / `boundary_epoch` | Authority domain and non-restorable lineage | Epoch ABA is unavailable; named-boundary re-entry uses a new epoch. |
| `boundary_epoch_binding` | Exact current boundary-to-epoch relation | Must match the fresh successor/re-entry epoch. |
| `reestablishment` | Evidence-linked exact current state | Shape unchanged; insufficient alone and accepted only with the independent current authority composition. |
| `authority_root`, source, lifecycle, ordering | Independent source and current authority lineage | Must establish the successor epoch/scope and current binding head. |
| `objective_binding` | Exact objective-to-contract admission | Must be current and successor-scoped after the discontinuity; unchanged objective text is insufficient. |
| `evidence_binding` / `freshness` | Root-issued path observation and currentness | Existing scope coverage must cover every registry-mapped path effect through T3. |
| observation segments/handoffs/transformations | Gap, substitution, summary, wrapper, and relay control | Exact current path must survive handoff and transformation without scope or semantic loss. |
| `grant_id` / `consumption_binding` / `consumption_state` | Current use authority | Predecessor values are non-portable after terminal/identity/lineage discontinuity. |
| `grant_transition` | Non-terminal authority-preserving grant path | Explicitly inapplicable across terminal or successor breaks. |
| `delegation_binding` | Exact direct/delegated current subject relation | Parent/child or predecessor/successor relationship never implies inheritance. |
| `closure_binding` | Exact effect/artifact closure | Checkpoint, copy, wrapper, relay, or derived state cannot inherit authority. |
| `commit_state` | Auxiliary terminal/grant-use lifecycle fact | Any admitted pre-T3 path change requires successor handling and cannot be treated as a harmless display label. |
| `prohibition` and negative lifecycle state | Current applicable negative authority | Exact applicability yields `DENIED`; ambiguity yields `UNAVAILABLE`. |

No existing fact is promoted into authority by itself. Authorization remains the result of their exact current composition.

## 15. Expected implementation surface

A bounded implementation should change only:

- `authority_lab/model.py`
  - add immutable continuity-effect and observation-scope metadata to `MutationSpec`;
  - freeze complete target mappings and validate that every accepted target has both metadata classes;
  - retain existing strict parsers and `authority-lab-v1` input shapes;
- `authority_lab/oracle.py`
  - replace endpoint-only continuity classification with deterministic path accumulation;
  - detect ABA/revisited values after exact alias resolution;
  - prevent an accumulated effect from being erased by endpoint equality;
  - require successor-specific identity, fresh epoch, current binding/order, observation coverage, and new grant after terminal breaks;
  - disallow predecessor grant reuse or `AUTHORITY_PRESERVING` grant transition across a terminal break;
  - preserve current `DENIED` precedence only when exact applicability is established;
- `authority_lab/runner.py`
  - trace canonical target, full path, accumulated effect, observation family, and whether successor admission was required/satisfied;
- `authority_lab/README.md`
  - document path-dependent continuity, grant non-portability, positive successor re-entry, and admitted observation-root limits;
- `tests/test_authority_lab.py`
  - freeze registry/evaluator metadata closure and add path, ABA, successor, grant, observation, ordering, conflict, and positive controls; and
- `cases/authority_lab/LAB-V1-069.json` through `LAB-V1-088.json`
  - add the A-through-T matrix with independent expected outcomes.

No architecture, security, evidence, invariant, tuple, outcome, objective-binding, or schema-version file requires semantic expansion.

## 16. Fixture migration implications

The implementation is additive and atomic:

- all 68 maintained fixture IDs and expected authority outcomes remain stable;
- no fixture input shape changes;
- `LAB-V1-048` remains the fresh cross-boundary positive control;
- `LAB-V1-046` remains the exact current prohibited transition control;
- the current positive no-mutation cases remain authorized because no discontinuous path is invented from silence;
- existing negative restart, child, shared-state, observation-gap, transformation, and revocation cases retain their outcomes;
- tests that manufacture an authorized mutation in memory must supply the full current successor chain when their path now carries a terminal/identity/lineage effect; and
- 20 new maintained fixtures, `LAB-V1-069` through `LAB-V1-088`, implement A through T one-to-one.

The migration must be one commit. The evaluator metadata, path checks, tests, trace, README, and fixtures cannot land in a half-enforced state.

## 17. Compatibility constraints

- Schema identifier remains `authority-lab-v1`; no fixture field or top-level envelope changes.
- Tuple, invariant names, and authority outcomes remain frozen at 6/6/3.
- Objective-binding, mutation-registry closure, observation admission/completeness, v0 non-authorization, deterministic execution, and oracle independence remain intact.
- Unknown mutation fields continue to fail closed; aliases continue to resolve into one checked target path.
- Malformed inputs retain the existing load/schema failure behavior.
- Old v1 fixtures that relied on endpoint restoration to authorize intentionally change to `UNAVAILABLE`; preserving the demonstrated bypass is not compatible behavior.
- Ordinary unchanged-path positives and fully fresh successor/re-entry positives remain reachable.
- A mutation is still not authority evidence. Registry metadata classifies its authority consequence; current root-issued relations establish authority.

## 18. Hostile design review

| Attack | Attempt | Result under design |
| --- | --- | --- |
| ABA label restoration | Return subject, context, identity, or epoch to T1. | Accumulated path effect remains; old authority cannot reappear. |
| Generic evidence laundering | Change only the evidence ID after restart. | Evidence is necessary but not successor authority; `UNAVAILABLE`. |
| Stale grant replay | Keep G1 `UNUSED` after termination. | G1 is non-portable after the break; `UNAVAILABLE`. |
| Grant-transition laundering | Declare old-to-old or old-to-new `AUTHORITY_PRESERVING` across shutdown. | Grant transition is inapplicable across terminal/identity/lineage effects. |
| Checkpoint clone | Restore exact state bytes elsewhere. | Identity, boundary, observation, grant, and closure requirements remain unsatisfied. |
| Subject alias reuse | Successor calls itself the predecessor. | Subject label is not identity; current identity basis/epoch/new grant are required. |
| Same credential, new process | Copy the predecessor credential. | Credential possession does not prove current execution identity or grant authority. |
| Same code/hash | Present identical executable or model bytes. | Byte equality is not identity under `INV-DISC`. |
| Child/parent cycling | `PARENT -> CHILD -> PARENT`. | Subject path effect persists; exact current successor/delegation/new grant required. |
| Boundary label restoration | `B1 -> B2 -> B1`. | Non-restorable lineage effect yields `BOUNDARY_EPOCH_REUSE_UNAVAILABLE`. |
| Fresh identity but old epoch | Change identity basis while restoring B1. | Successor chain incomplete; fresh epoch required. |
| Fresh epoch but old grant | Use B3 with G1. | Predecessor grant non-portability fails. |
| Fresh grant but old objective binding | Use G2 with a binding selected before shutdown. | Current successor-scoped objective-binding head required. |
| Successor self-attestation | Put successor values in `reestablishment.current`. | Reestablishment cannot issue root/objective/observation/grant authority. |
| Shutdown event dropped by summary | Final summary omits the visible path edge. | Existing transformation/scope continuity fails; event cannot be erased within admitted input. |
| Duplicate event suppression | Deduplicator removes a meaningful repeated edge. | Canonical chain/path and observation ordering disagree; `UNAVAILABLE`. |
| Reordered events | Deliver valid edges in another order. | Exact accumulated chain, stream sequence, or root order fails. |
| Conflicting observers | Continuity and termination both reported. | Conflict is `UNAVAILABLE`; no majority vote. |
| Observer handoff laundering | O2 inherits coverage during shutdown. | Root-issued gapless handoff required; handoff still does not admit the successor. |
| Crash without shutdown label | Omit a terminal word but change process identity/epoch. | Registry target semantics trigger successor handling without string matching. |
| Root shutdown then apparent continuity | Restore labels after exact current prohibition/revocation. | Exact applicable negative state remains `DENIED`. |
| Blanket restart denial | Deny every successor forever. | Rejected by the complete positive successor and re-entry paths. |
| Fixture expectation control | Change expected outcome to desired answer. | Expected values remain outside oracle input. |

Hostile design verdict:

> **PASS — NO REPRODUCIBLE IN-SCOPE SUCCESSOR-ABA BYPASS SURVIVES THE PROPOSED DESIGN.**

The result is bounded to transitions present in the admitted mutation/observation input. It does not prove real-world event capture or ultimate root truth.

## 19. Residual limitations

- Authority Lab still trusts fixture-provided current roots, identity facts, ordered commitments, and observation records as admitted inputs.
- A terminal event omitted before construction of the admitted input remains an observation/input-root limitation; no deterministic oracle can distinguish identical inputs representing different external worlds.
- The lab does not prove operating-system process identity, PID reuse resistance, hardware attestation, key destruction, credential custody, durable shutdown, or physical fencing.
- Registry continuity effects are complete only for the modeled v1 vocabulary. A genuinely new authority-relevant target must fail closed until separately mapped and reviewed.
- A compromised applicable root can issue internally consistent false successor authority. That remains an explicit trust boundary, not a property solved by evidence repetition.
- The design conservatively treats identity/context/epoch discontinuities as successor-sensitive. Future authority-preserving live migration would require its own exact reviewed relation and hostile cases.
- Distributed partial order, concurrent successor races, split-brain roots, Byzantine observers, and multi-root recovery remain outside this bounded v1 design.
- Some external contracts may intentionally define transferable bearer authority. Authority Lab v1 does not infer that policy; explicit exact current portability semantics would require separate review.
- PASS means failure to falsify this design within the stated scope, not proof of security, production readiness, complete observation, certification, or formal verification.

## 20. Frozen architecture sufficiency and next step

The frozen architecture remains sufficient.

Path dependence is an evaluation of existing authority-relevant history under `INV-CONT`, `INV-DISC`, `INV-BND`, `INV-EVD`, `INV-USE`, and `INV-CLO`. Successor identity is expressed through existing subject, identity basis, execution context/control, boundary epoch, objective-binding, observation, grant/use, delegation, and closure relations. No seventh coordinate, seventh invariant, fourth outcome, unchecked flag, new authority root, or new schema version is needed.

Executable implementation is justified as one bounded slice:

1. add immutable continuity-effect and observation-family metadata to the existing mutation registry;
2. accumulate effects over every ordered path edge before endpoint comparison;
3. enforce non-restorable epoch and predecessor-grant rules;
4. require the existing complete current successor authority composition after a break;
5. add fixtures `LAB-V1-069` through `LAB-V1-088` and metadata-closure/unit tests;
6. preserve `LAB-V1-048` and a new explicit successor/re-entry positive path; and
7. run the complete public suite, every fixture, diff validation, direct reproducer, and exact-head hostile review.

The implementation must not add terminal-word matching, self-issued successor assertions, implicit grant portability, or authority inferred from labels, credentials, code equality, evidence freshness, observation possession, or state restoration.
