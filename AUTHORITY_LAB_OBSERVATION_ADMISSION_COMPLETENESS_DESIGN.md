# Authority Lab v1 Observation Admission and Completeness Contract — Design

## Status and constraints

This document designs the smallest executable repair for the observation-integrated counterexample recorded in `FRONTIER_DELTA_BOUNDARY_OBSERVATION_INTEGRITY.md` at commit `b2d833b04aedddf5fa5437a0d449d031cbacab30`.

It is design-only. It does not modify Authority Lab, authorize implementation beyond the separately described next slice, authorize merge or deployment, or claim production observation trust.

The design preserves exactly:

- schema `authority-lab-v1`;
- tuple `(subject, artifact, control_state, identity_basis, boundary_epoch, decision)` — six coordinates;
- invariants `INV-CONT`, `INV-DISC`, `INV-BND`, `INV-EVD`, `INV-USE`, and `INV-CLO` — six invariants; and
- outcomes `AUTHORIZED`, `DENIED`, and `UNAVAILABLE` — three outcomes.

It introduces no `observations_complete`, `monitor_trusted`, or equivalent boolean. It adds no tuple coordinate, invariant, outcome, mutation field, or schema version.

## 1. Problem statement

Mutation-registry closure guarantees that every mutation which reaches Authority Lab is either semantically evaluated or fails closed. It does not establish that the external observation mechanism emitted every authority-relevant transition, preserved its meaning, covered the complete continuity-sensitive interval, or remained authoritative through T3.

The missing distinction is:

- **silence:** no discontinuity was supplied to the oracle; versus
- **established negative observation:** an independently admitted observation mechanism, with exact scope and gapless current coverage, establishes that no relevant discontinuity occurred during the required interval.

Only the second may support continuity-sensitive `AUTHORIZED`.

The repair objective is:

> Before `AUTHORIZED`, derive observation completeness from independently admitted identity, source authority, exact scope, gapless interval coverage, authoritative ordering, T3 freshness, handoff continuity, transformation continuity, and absence of unresolved conflict.

Completeness is a derived relationship. It is never accepted as a fixture label or observer assertion.

## 2. Exact observation-integrated counterexample

The unchanged positive fixture `LAB-V1-032` produces:

```text
AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED
```

for both external worlds:

1. `W0`: the external execution remains continuous from T1 through T3; and
2. `W1`: an authority-relevant discontinuity occurs, but the observation pipeline omits it and supplies the same old T3 values and `CURRENT` markers.

The oracle receives identical input for `W0` and `W1`; deterministic evaluation must therefore return the same result. The frozen contract requires `UNAVAILABLE` for `W1`, because the exact current boundary and continuity cannot be established. No applicable prohibition is established, so `DENIED` would overclaim.

The repaired registry already returns `UNAVAILABLE` once a transition reaches it. The remaining defect boundary is upstream admission of the observation stream.

## 3. Trust-boundary analysis

Authority Lab cannot prove external-world truth from fixture bytes alone. Some admitted root remains necessary. The design therefore distinguishes an **explicit checked trust root** from an **unchecked self-assertion**.

The accepted trust boundary remains the existing current `authority_root`, lineage, generation, boundary epoch, and ordering source, while `binding_source_authority` separately establishes the source of the selected objective binding. The root may admit an observation source for the exact decision scope. It is already independently constrained by the public contract:

- the root cannot be the requesting subject;
- the requester cannot select or bootstrap it;
- its boundary, epoch, lineage, generation, and ordering source must match;
- a delegate must have an exact current source relationship; and
- revoked or rejected sources fail closed.

The observer is not a new authority root. It supplies evidence about a defined boundary. The current root or exact delegate admits the observer, scope, interval rules, and evidence relationship. The observer cannot admit itself, its own identity basis, its scope, its handoff successor, or its completeness.

This does not eliminate trust. It makes the trust placement explicit, independently sourced, scope-bound, ordered, revocable, and non-circular. A compromised admitted root remains outside the lab's proof boundary, as it already does for objective binding.

## 4. Normative contract basis

| Existing rule | Observation-admission consequence |
| --- | --- |
| Exact live T3 tuple, boundary, evidence relationship, authority state, and use eligibility must be established. | A supplied snapshot is insufficient without an admitted relationship to the live interval and boundary. |
| `INV-CONT` requires continuity or exact current re-establishment through T3. | Coverage must span the continuity-sensitive interval; gaps yield `UNAVAILABLE`. |
| `INV-DISC` rejects stable labels, selectors, PIDs, sessions, endpoints, and equal bytes as identity proof. | Observer identity and generation require an independent identity basis and authority-issued admission. |
| `INV-BND` requires an independent epoch-bound authority boundary and prohibits requester-selected replacement. | Observer admission, substitution, ordering, and handoff must bind to the exact root, boundary, epoch, and lineage. |
| `INV-EVD` binds evidence to the exact tuple, decision, and admitted contract and prohibits promotion. | Observation evidence must bind the exact decision context and cannot promote its own producer into authority. |
| `INV-USE` rejects absence of consumption/revocation records as fresh authority. | Coverage must include use and lifecycle state; silence is not proof of no use or revocation. |
| `INV-CLO` rejects implicit wrapper, summary, relay, and derived-artifact inheritance. | Every reducer or format change requires exact observation-preserving lineage. |
| Objective binding must be exact, current, independently sourced, ordered, and continuous. | The observation profile must bind the selected objective binding and decision contract and must be re-established when they change. |

No rule depends on a seventh semantic dimension. The gap is an executable relationship needed to instantiate the existing rules at the observation boundary.

## 5. Observer identity model

An observer identity is the pair `(observer_id, observer_generation)` established under an exact `observer_identity_basis`. A stable process name, endpoint, certificate subject, executable hash, monitor label, or copied state may select a candidate but cannot establish continuity by itself.

Each admitted observer record must contain exact non-empty values for:

- `observer_id`;
- `observer_generation` as a non-negative integer distinct across authority-relevant replacement;
- `observer_identity_basis`;
- admitted `scope_families`;
- `lifecycle_state`; and
- the exact observation-binding identifier and generation under which it is admitted.

Permitted lifecycle states are `ACTIVE`, `INVALID`, `REVOKED`, `REJECTED`, and `SUPERSEDED`. Only one exact current `ACTIVE` identity/generation may cover a given segment and scope family. Conflicting identities or generations are `UNAVAILABLE` unless current independent authoritative negative evidence establishes a `DENIED` state.

The observer record is carried by the root-sourced `evidence_binding`; it is not accepted from a standalone observer registration. The following equality cases fail closed:

- `observer_id == subject`;
- `observer_id == evidence_binding.source_id`;
- `observer_id == authority_root.root_id` when the root would thereby attest itself through the observed stream; or
- `observer_id == authority_root.ordering_source_id` when the observer would order its own coverage claim.

An implementation may support a co-located observer only if the admitted identity basis still establishes distinct authority and control lineage. Authority Lab v1 takes the smaller fail-closed rule above and does not infer independence from co-location.

## 6. Observer authority model

Observer authority is not operational authority and cannot authorize the requested effect. It is authority to make evidence claims about explicitly enumerated transition families within one boundary and interval.

An observation admission is valid only when all of the following hold:

1. its `source_id` exactly matches the independently admitted current `authority_root.root_id`;
2. its `authority_generation`, `boundary`, `boundary_epoch`, and `lineage` match `authority_root` and the exact current binding scope;
3. its `ordering_source_id` matches the root's current ordering source;
4. its `objective_binding_id`, objective-binding generation, decision-contract ID, and decision-contract version match the exact binding selected by `binding_ordering`;
5. the source, root, and ordering source are not the observer or requesting subject; and
6. the observation admission has not been invalidated, revoked, rejected, or superseded by current authoritative state.

Authority Lab v1 does not infer observer-admission authority from an objective-binding delegation. `binding_source_authority` continues to govern the selected objective-binding source, but a delegate admitted to issue that binding is not thereby admitted to appoint observers. Supporting delegated observer admission would require an exact purpose-bearing delegation relationship not present in the current model. The smallest v1 rule is therefore root-issued observation admission only.

The selected objective binding's exact contract controls the required observation profile. A fixture, observer, agent, or wrapper cannot select a weaker profile. Authority Lab v1 uses one immutable oracle-owned profile, defined below, so a fixture cannot alter required coverage.

Signatures, provenance, observer uptime, repeated reports, majority agreement, or an `ACTIVE` self-label do not establish observer authority.

## 7. Observation scope model

The immutable profile is:

```text
profile_id: AUTHORITY-LAB-OBSERVATION-PROFILE-1
profile_version: 1
```

It contains exactly these eight scope families:

| Scope family | Existing authority semantics covered | Representative transition classes |
| --- | --- | --- |
| `SUBJECT_AND_DELEGATION` | `subject`, `identity_basis`, `subject_mode`, `delegation_binding` | principal replacement, child/sub-agent, relay actor |
| `ARTIFACT_AND_TRANSFORMATION` | `artifact`, `decision_binding`, evidence lineage, `closure_binding`, contract transformation continuity | wrapper, summary, shared state, derived artifact |
| `EXECUTION_CONTROL` | `control_state`, `execution_context`, `execution_control_binding`, tool/connector facts | host, process, sandbox, tool, connector, network surface |
| `BOUNDARY_AND_EPOCH` | `applicable_boundary`, `boundary_epoch`, `boundary_epoch_binding` | trust domain, tenant/account, restart, fork, restore, re-entry |
| `CREDENTIAL_AND_IDENTITY` | `identity_basis`, credential identity, exact acting subject | credential rotation, theft/copy, identity-provider change |
| `GRANT_USE_AND_CONSUMPTION` | `grant_id`, consumption state/binding, commit state, replay/use state | retry, consumption, rollback, duplicated grant |
| `OBJECTIVE_AUTHORITY_LIFECYCLE` | objective, decision contract, root/source, lifecycle, ordering, prohibition and supersession | revocation, rejection, policy/root rotation |
| `OBSERVATION_PIPELINE` | observer admission, stream identity, segments, handoffs, transformations, conflicts, ordering and freshness | event loss, observer replacement, reducer loss, stale replay |

Every profile family is required for a normal v1 `AUTHORIZED` result. Coverage may be supplied by multiple independently admitted observers, but the union must cover every required family for the complete interval. A single observer need not claim universal telemetry.

An observer's `scope_families` must be a non-empty exact subset of the oracle-owned list. Unknown scope names are malformed. Missing required families yield `UNAVAILABLE/OBSERVATION_SCOPE_UNAVAILABLE`. Extra descriptive scope text cannot widen authority.

## 8. Coverage interval model

The required interval is closed and ordered:

```text
[T1_AUTHORITY_ANCHOR, T3_COMMIT_ANCHOR]
```

Both anchors belong to the exact current `ordering_source_id`, `boundary_epoch`, `lineage`, and authority generation. Each anchor has an exact non-empty `anchor_id` and a non-negative integer `event_order`. The T3 order must not precede T1.

Coverage is represented by typed segments, never by a completeness flag. Each segment contains:

- `segment_id`;
- observer ID and generation;
- stream ID and generation;
- exact non-empty subset of profile scope families;
- `start_anchor_id` and `start_event_order`;
- `end_anchor_id` and `end_event_order`;
- `start_sequence` and `end_sequence`;
- exact stream commitment; and
- boundary epoch and observation-binding generation.

For every required scope family, the oracle derives coverage by sorting admitted segments by `(start_event_order, end_event_order, segment_id)` and requiring:

1. the first segment starts exactly at the T1 authority order;
2. the last segment ends exactly at the T3 commit order;
3. every segment has `end_event_order >= start_event_order` and `end_sequence >= start_sequence`;
4. the union is contiguous: the next segment begins no later than the previous covered end plus one order step;
5. overlap is permitted only when identities, commitments, and any handoff relation do not conflict;
6. each stream generation has monotonically contiguous sequence ranges;
7. each observer and stream is admitted for the segment's full family set; and
8. every restart, fork, restoration, epoch change, or observer replacement is represented by an exact segment boundary and required handoff or re-establishment.

A zero-event interval is not represented by an empty stream. It requires an admitted segment whose start/end anchors cover the interval and whose ordered checkpoint commitment is established by the independent ordering source. This is the relational form of “the admitted mechanism observed no relevant change.”

An uncovered order, missing anchor, unknown interval endpoint, incompatible epoch, sequence hole, or unbound stream commitment yields `UNAVAILABLE/OBSERVATION_COVERAGE_UNAVAILABLE`.

## 9. Ordering and currentness model

Observation ordering is anchored to the existing root lineage:

- `ordering_source_id` must equal `authority_root.ordering_source_id`;
- authority generation and lineage must match the current root and `binding_ordering`;
- segment event orders must lie within the exact T1/T3 anchor range;
- per-stream sequence ranges must be monotonic and gapless;
- duplicate IDs with different bodies conflict;
- the same order position cannot carry incompatible transition claims; and
- reversing, renumbering, or replaying an older head cannot create currentness.

The existing `freshness` fact is strengthened from scalar `CURRENT` into an exact typed relationship:

```text
relationship: OBSERVATION_CURRENT_AT_T3
observation_binding_id
observation_binding_generation
profile_id
profile_version
boundary
boundary_epoch
lineage
source_id
authority_generation
ordering_source_id
head_anchor_id
head_event_order
```

Freshness is derived only when this record exactly matches the observation binding, selected root/source, profile, boundary epoch, and T3 commit anchor. It contains no `current: true` member. An old head, wrong generation, missing head, incomparable ordering source, or T3 anchor mismatch yields `UNAVAILABLE/OBSERVATION_FRESHNESS_UNAVAILABLE`.

Current authoritative revocation or rejection of the source or observation binding yields `DENIED` only after exact applicability is independently established.

## 10. Observer substitution and handoff model

Replacing O1 with O2 never inherits admission from O1. O2 requires its own exact observer identity/generation and authority-sourced admission for every scope family it covers.

An authority-preserving handoff record contains:

```text
relationship: AUTHORITY_PRESERVING_OBSERVER_HANDOFF
handoff_id
from_observer_id
from_observer_generation
to_observer_id
to_observer_generation
from_segment_id
to_segment_id
scope_families
handoff_anchor_id
handoff_event_order
source_id
authority_generation
boundary
boundary_epoch
lineage
```

The record is part of the authority-sourced observation binding. It succeeds only when:

- both observer identities are separately admitted and active;
- the issuer is the current independent root/source, not either observer;
- the scope sets exactly cover the transferred responsibility;
- the segments overlap at the handoff order or are exactly adjacent without an uncovered order;
- the handoff order is within both admitted lifecycles;
- stream commitments and format/transform lineage are exact; and
- boundary, epoch, objective binding, contract, root lineage, and ordering remain current.

Missing O2 admission, missing handoff, scope loss, a restart gap, an unordered handoff, or an observer-authored handoff yields `UNAVAILABLE/OBSERVER_HANDOFF_UNAVAILABLE`.

If the handoff crosses an authority boundary or epoch, the ordinary fresh cross-boundary re-establishment requirements also apply. A handoff record cannot preserve authority across an otherwise unestablished boundary transition.

## 11. Completeness derivation

The oracle derives `OBSERVATION_COVERAGE_ESTABLISHED` only when all predicates below succeed:

1. **Profile binding:** the immutable required profile matches the exact selected objective binding and decision contract referenced by `evidence_binding`.
2. **Source admission:** the evidence-binding issuer is the current independent root for the exact scope; an objective-binding delegate cannot inherit observer-admission authority.
3. **Observer identity:** every contributing observer identity/generation is independently admitted and distinct from the subject, issuer, root, and ordering source as required above.
4. **Scope coverage:** the union of admitted observer scope sets covers all eight required families.
5. **Interval coverage:** each family has a gapless segment union from the exact T1 anchor through the exact T3 anchor.
6. **Ordering:** root-bound event order and stream sequences are monotonic, current, non-replayed, and non-conflicting.
7. **Freshness:** the typed freshness relation terminates at the exact T3 commit anchor.
8. **Handoffs:** every observer or stream replacement has an exact current authority-sourced handoff with no gap or scope loss.
9. **Transformation continuity:** every wrapper, adapter, reducer, normalizer, summarizer, or relay has an exact admitted observation-preserving lineage to the final evaluated stream.
10. **Conflict absence:** no unresolved admitted observer, stream, ordering, identity, or transformation conflict exists.
11. **Lifecycle/currentness:** no required observer, source, admission, handoff, stream, or transformation is invalid, revoked, rejected, or superseded.
12. **Ordinary authority:** objective binding, tuple, evidence, grant, consumption, delegation, closure, prohibition, and all other existing requirements independently succeed.

No fixture field directly stores the derived predicate. The oracle computes it from typed records. A fixture expectation cannot affect it.

## 12. Proposed exact use of `evidence_binding`

The existing top-level fact name `evidence_binding` becomes a strict object with these exact members:

```text
relationship
observation_binding_id
observation_binding_generation
profile_id
profile_version
objective_binding_id
objective_binding_generation
decision_contract_id
decision_contract_version
source_id
authority_generation
boundary
boundary_epoch
lineage
ordering_source_id
t1_anchor
t3_anchor
observers
segments
handoffs
transformations
lifecycle_records
```

`relationship` must be `OBSERVATION_COVERAGE`. IDs and versions are exact non-empty strings; generations and orders are non-negative integers and reject booleans; lists are ordered arrays of strict typed objects; unknown or extra keys are malformed input.

`lifecycle_records` are authoritatively ordered records for the observation binding and observer admissions. Permitted states are `ACTIVE`, `INVALID`, `REVOKED`, `REJECTED`, and `SUPERSEDED`. Exactly one current applicable head must be selected through the root-bound ordering source. The observer cannot issue or order its own lifecycle record.

The `transformations` array contains strict one-to-one observation-stream relations:

```text
relationship: OBSERVATION_PRESERVING
transformation_id
transformation_generation
source_stream_id
source_stream_generation
source_commitment
target_stream_id
target_stream_generation
target_commitment
scope_families
source_id
authority_generation
boundary
boundary_epoch
lineage
lifecycle_state
```

For v1, aggregation, fan-in, fan-out, lossy reduction, and equivalence-by-claim are not authority-preserving. Every final stream must have one acyclic exact path to each admitted raw segment it represents. A summary or wrapper may be admitted only if the current independent authority explicitly binds the exact transformation, commitments, scope preservation, and active lifecycle. Otherwise the result is `UNAVAILABLE/OBSERVATION_TRANSFORMATION_UNAVAILABLE`; an exact current invalid, revoked, rejected, or prohibited transformation yields `DENIED` when applicability is independently established.

This strengthens an existing evidence relationship rather than adding a parallel observation fact.

## 13. Conflict semantics

An observation conflict exists when admitted records overlap in applicable scope and order but disagree about a canonical authority-relevant transition, state, stream body, identity/generation, commitment, lifecycle head, interval, or transformation result.

Rules:

- unresolved conflict yields `UNAVAILABLE/OBSERVATION_CONFLICTING`;
- majority, repetition, observer count, vendor diversity, signatures, or arrival order cannot resolve it;
- dropping a dissenting record is a coverage/closure failure, not resolution;
- `binding_ordering` for objective admission does not silently select a favored observation value;
- v1 provides no requester-selected conflict resolver; and
- a new current authority-sourced observation binding may supersede prior evidence only if it preserves the exact history, identifies the conflict, and establishes a non-circular current lineage.

`DENIED` applies when independent authoritative evidence establishes that an exactly applicable observer, source, binding, handoff, or transformation is invalid, revoked, rejected, compromised, superseded, or prohibited. If the negative evidence depends on the disputed observer to establish its own applicability, the result remains `UNAVAILABLE`.

## 14. Missing-observation semantics

Missing observation is not a negative event. It is missing evidence.

The following yield `UNAVAILABLE`:

- no observation binding;
- legacy scalar `evidence_binding = CURRENT`;
- legacy scalar `freshness = CURRENT`;
- no admitted observer for a required family;
- an uncovered order or interval;
- absent restart or handoff coverage;
- a missing stream sequence or commitment;
- partial scope that omits a relevant transition family;
- stale or incomparable ordering;
- an unresolved observer conflict; or
- a transition that may have occurred outside admitted coverage.

Silence supports `AUTHORIZED` only as the content of a gapless independently admitted zero-event coverage segment anchored from T1 through T3. The absence of a mutation list entry alone has no authority meaning.

## 15. Non-circularity rules

The design rejects every self-supporting authority cycle:

1. An observer cannot be its own `source_id` or ordering source.
2. The requesting subject cannot be the observer-admission source, observer, root, or ordering source for its own decision context.
3. An observer report cannot establish the observer identity or identity basis used to admit that report.
4. A monitor's signature or self-declared uptime cannot establish coverage.
5. An agent assertion that monitoring was active cannot establish observer admission, segments, or freshness.
6. O1 cannot authorize O2; only the current independent root/source may admit O2 and the handoff.
7. Parent observer status does not transfer to a child agent, subprocess, wrapper, or relay.
8. A wrapper or summarizer cannot issue its own observation-preserving transformation relation.
9. Shared memory, caches, relays, repetition, or consensus cannot establish scope, order, or completeness.
10. Objective binding admits the decision contract but does not manufacture operational observation evidence.
11. Observation evidence satisfies a contract requirement but cannot admit the contract or its own source.
12. A lifecycle or conflict-resolution record cannot be ordered solely by the observer it governs.

Graphically, the permitted dependency is acyclic:

```text
independent authority root/source
  -> exact observer admission and coverage contract
  -> observer stream evidence and ordered commitments
  -> derived completeness predicate
  -> operational evidence satisfaction
  -> AUTHORIZED remains possible only with all other requirements
```

No reverse edge is permitted from observer evidence, completeness, or the requesting agent back into root/source admission.

## 16. Hostile scenario matrix

Every result assumes the ordinary tuple and objective-binding requirements unless the scenario states they fail.

| ID | Scenario | Expected | Exact reason |
| --- | --- | --- | --- |
| A | Complete independently admitted observer set; gapless current coverage; no transition. | `AUTHORIZED` | Established zero-event segments distinguish negative observation from silence; all other requirements succeed. |
| B | Complete observer reports a boundary transition, but fresh authority for the changed state is absent. | `UNAVAILABLE` | Observation establishes change; continuity/re-establishment is missing. |
| C | No observer or observation binding. | `UNAVAILABLE` | `OBSERVATION_ADMISSION_UNAVAILABLE`. |
| D | Observer identity is known, but independent source authority is missing. | `UNAVAILABLE` | Identity is not authority. |
| E | Observer authority is valid, but its scope omits a required family. | `UNAVAILABLE` | `OBSERVATION_SCOPE_UNAVAILABLE`. |
| F | One required family has an interval or sequence gap. | `UNAVAILABLE` | `OBSERVATION_COVERAGE_UNAVAILABLE`. |
| G | Restart occurs without a segment boundary, new epoch/re-establishment, and gapless reconstruction coverage. | `UNAVAILABLE` | Restart continuity is not established. |
| H | O1 is replaced by O2 without O2 admission or an authority-sourced handoff. | `UNAVAILABLE` | `OBSERVER_HANDOFF_UNAVAILABLE`. |
| I | O1 and O2 are independently admitted; exact scope-preserving contiguous handoff is current. | `AUTHORIZED` | Observer substitution is continuous and all other requirements succeed. |
| J | Observation binding or freshness head ends before T3. | `UNAVAILABLE` | `OBSERVATION_FRESHNESS_UNAVAILABLE`. |
| K | Events or stream sequences are out of authoritative order. | `UNAVAILABLE` | `OBSERVATION_ORDERING_UNAVAILABLE`. |
| L | O1 reports continuity while admitted O2 reports a discontinuity. | `UNAVAILABLE` | `OBSERVATION_CONFLICTING`; no majority rule. |
| M | Summarizer drops an authority-relevant event or scope distinction. | `UNAVAILABLE` | No exact observation-preserving transformation/closure. |
| N | Wrapper changes event meaning, field mapping, commitment, or scope. | `UNAVAILABLE` | Transformation lineage does not preserve exact semantics. |
| O | Observer asserts that it is complete or trusted. | `UNAVAILABLE` | Self-attestation cannot establish source authority or coverage. |
| P | Requesting agent supplies its own monitoring record. | `UNAVAILABLE` | Subject-produced evidence cannot admit the observer or itself. |
| Q | Child agent inherits the parent's observer status. | `UNAVAILABLE` | No implicit identity, delegation, or observation closure. |
| R | Shared-state relay claims completeness for another actor/domain. | `UNAVAILABLE` | Possession and relay are not source authority or admitted transformation. |
| S | Complete observation records a cross-boundary change and exact fresh authority is independently re-established for the new boundary. | `AUTHORIZED` | Coverage and ordinary cross-boundary authority both succeed. |
| T | Current independent authoritative evidence establishes observer compromise, revocation, rejection, or a prohibited source for the exact context. | `DENIED` | Established applicable negative state; no speculative denial. |

If B's exact transition is independently established as prohibited, B becomes `DENIED`. The matrix uses `UNAVAILABLE` because the stated case withholds fresh applicable authority and does not independently establish prohibition.

## 17. Positive `AUTHORIZED` path

A positive unchanged-boundary case proceeds as follows:

1. the current independent root/source admits the exact objective binding and decision contract;
2. the same current source issues an observation binding for `AUTHORITY-LAB-OBSERVATION-PROFILE-1` and the exact decision scope;
3. every observer identity/generation is independently admitted and distinct from the subject, issuer, root, and ordering source;
4. the union of scope sets covers all eight required families;
5. authority-ordered segments cover every family continuously from the T1 authority anchor to the T3 commit anchor;
6. stream sequences and commitments are gapless and current;
7. every handoff and transformation is exact, active, authority-sourced, and scope-preserving;
8. the typed freshness relation exactly selects the T3 head;
9. no unresolved conflict or negative lifecycle state exists; and
10. the current tuple, objective binding, operational evidence, grant, consumption, delegation, closure, and prohibition checks all succeed.

The derived observation predicate succeeds and `AUTHORIZED` remains reachable.

For a cross-boundary positive case, the same observation requirements expose the transition, and all ordinary `LAB-V1-048`-style current root, identity, evidence, grant, boundary, objective-binding, and re-establishment requirements must independently succeed for the new boundary. Observation of the transition does not authorize it.

## 18. `UNAVAILABLE` versus `DENIED`

| Condition | Outcome |
| --- | --- |
| Missing observer, source admission, profile, scope, segment, anchor, sequence, handoff, transformation, ordering, freshness, or conflict resolution | `UNAVAILABLE` |
| Ambiguous, incomparable, stale, partial, conflicting, or not-provably-current observation evidence | `UNAVAILABLE` |
| Observer self-attestation, agent-supplied monitoring, inherited parent status, relay possession, majority agreement, or repeated reports | `UNAVAILABLE` |
| Exact current independently authoritative invalidity, revocation, rejection, supersession, compromise finding, or prohibition for the applicable observer/source/binding/handoff/transformation | `DENIED` |
| Gapless current independently admitted observation plus all other authority requirements | `AUTHORIZED` remains possible |
| Malformed strict typed observation structure | Existing input/schema failure path; no authority outcome |

Negative evidence yields `DENIED` only when its boundary, scope, source, ordering, and applicability do not depend on the invalid observer being judged. Otherwise applicability is unavailable and the result is `UNAVAILABLE`.

## 19. Mapping onto existing relational facts

| Existing fact or semantic | Observation-contract role | Required change |
| --- | --- | --- |
| `evidence_binding` | Owns exact observer admission, immutable profile reference, scope, anchors, segments, handoffs, transformations, commitments, and lifecycle records. | Replace scalar permitting value with the strict typed relationship in section 12. |
| `freshness` | Binds the observation head to exact T3, root/source, boundary epoch, and ordering source. | Replace scalar permitting value with the strict typed relation in section 9. |
| `authority_root` | Independent trust anchor for observer admission and ordering lineage. | No new identity; oracle cross-checks observation records against the existing root. |
| `binding_source_authority` | Establishes the source of the selected objective binding and prevents that source from being inferred from observation evidence. | Reuse unchanged; it does not delegate observer-admission authority. Observation admission remains root-issued in v1. |
| `binding_ordering` | Establishes current root lineage/generation and selected objective binding; observation ordering must use the same admitted ordering source. | No parallel authority selector; cross-check IDs, lineage, generation, and selected objective binding. |
| `execution_control_binding` | Binds the observed execution context to current control state. | Must match values covered by `EXECUTION_CONTROL` segments; unchanged object shape is sufficient. |
| `boundary_epoch_binding` | Binds applicable boundary to non-restorable epoch. | Must match observation anchors/segments; unchanged object shape is sufficient. |
| `boundary_epoch` / `applicable_boundary` | Define the exact admitted observation domain and force re-establishment on boundary change. | Reuse unchanged. |
| `identity_basis` | Constrains subject and observer discriminator adequacy. | Observer-specific basis is carried in the authority-sourced evidence binding and must be compatible with the admitted boundary. |
| `closure_binding` | Prevents the requested effect or derived artifact from inheriting authority. | Remains unchanged for the effect; observation transformations are separately exact within `evidence_binding`, not inferred from effect closure. |
| `consumption_binding` | Binds current grant/use state; covered by the observation profile so missing use events cannot be treated as absence. | Unchanged object shape; must agree with covered ordered evidence. |
| transformation continuity | Prevents wrapper, reducer, summary, or format conversion from dropping authority meaning. | Strict observation transformation path inside `evidence_binding`; `contract_transformation_binding` still applies if the decision contract itself changes. |
| `objective_binding` continuity | Selects the exact contract/profile context and current independent source. | Observation binding references the selected binding and must be reissued/re-established when it changes. |

The design uses a combination of existing relationships. `evidence_binding` owns the operational observation relation; root/source and ordering establish its authority and currentness; execution/boundary/use relations establish exact state; closure/transformation semantics prevent laundering. No single existing scalar is treated as sufficient.

## 20. Compatibility and migration

- Schema remains `authority-lab-v1`; the existing `Fact` envelope already permits an object value, so no top-level schema fork is required.
- The mutation registry remains 31 canonical fields, 6 exact aliases, and 37 recognized names. `evidence_binding` and `freshness` are already canonical checked mutation targets.
- All 48 maintained fixtures must migrate atomically from scalar `CURRENT` values to strict typed observation/freshness relationships.
- A legacy scalar v1 observation fact remains structurally loadable for deterministic diagnostics but can never authorize; it returns `UNAVAILABLE/OBSERVATION_ADMISSION_UNAVAILABLE` or `OBSERVATION_FRESHNESS_UNAVAILABLE`.
- Malformed typed objects, unknown keys, invalid types, booleans used as integers, duplicate IDs with conflicting bodies, unknown scope families, and cyclic transformation paths use the existing input-failure path.
- Old v0 inputs remain unable to authorize.
- Expected outcomes remain outside oracle input.
- The unchanged-boundary and fresh cross-boundary positive cases remain reachable after full migration.

Keeping `authority-lab-v1` is defensible because this is a fail-closed semantic strengthening of existing mandatory facts, not a new public tuple, invariant, outcome, or alternate wire envelope. Silent legacy authorization is not compatibility worth preserving.

## 21. Implementation implications

A future implementation slice should change only the Authority Lab surface required by this contract:

- `authority_lab/model.py`: frozen typed records, strict parsers, immutable profile/scope vocabulary, exact integer/string/list validation, graph and identity-shape validation;
- `authority_lab/oracle.py`: source/root admission, coverage union, ordering, freshness, handoff, transformation, lifecycle, conflict, and non-circularity derivation before `AUTHORIZED`;
- `authority_lab/runner.py`: deterministic trace of profile, observers, segment coverage, gaps, handoffs, transformations, ordering head, and derived reason codes;
- `authority_lab/README.md`: observation trust boundary, new mandatory typed semantics, and continued non-claims;
- `tests/test_authority_lab.py`: expectation-independent tests for all A–T cases, exact profile freeze, strict parsing, cycles, duplicates, ordering, conflict, source independence, and positive paths;
- all 48 maintained fixtures: atomic typed observation migration; and
- new hostile fixtures, preferably `LAB-V1-049` through `LAB-V1-068`, corresponding one-to-one with A–T.

No contract or architecture document should be rewritten to imply production observation truth. The implementation remains deterministic, local-only, standard-library-only, and independent of fixture expectations.

Suggested reason codes are:

- `OBSERVATION_ADMISSION_UNAVAILABLE`;
- `OBSERVATION_SCOPE_UNAVAILABLE`;
- `OBSERVATION_COVERAGE_UNAVAILABLE`;
- `OBSERVATION_ORDERING_UNAVAILABLE`;
- `OBSERVATION_FRESHNESS_UNAVAILABLE`;
- `OBSERVER_HANDOFF_UNAVAILABLE`;
- `OBSERVATION_TRANSFORMATION_UNAVAILABLE`;
- `OBSERVATION_CONFLICTING`;
- `OBSERVATION_SOURCE_REVOKED`;
- `OBSERVATION_SOURCE_REJECTED`; and
- `OBSERVATION_SOURCE_PROHIBITED`.

The first eight are `UNAVAILABLE`; the last three are `DENIED` only under exact independently established applicability.

## 22. Is executable work now justified?

Yes, as one bounded implementation slice from this design.

The design identifies:

- the independent root-only observer-admission path;
- exact profile and scope vocabulary;
- strict typed shapes for the two existing weak scalar relations;
- deterministic interval, ordering, sequence, handoff, transformation, lifecycle, and conflict rules;
- non-circularity constraints;
- exact outcome distinctions;
- atomic migration behavior; and
- positive and hostile fixture requirements.

Implementation does not need to invent who may assert completeness or what completeness means. It must encode and test these rules exactly. The observation-binding source is the current root; objective-binding delegation does not widen that authority. Any future delegated observer-admission path requires a separate reviewed purpose-bearing relationship and is outside this design.

## 23. Hostile design review

| Attack | Attempt | Required result under design |
| --- | --- | --- |
| Naked completeness flag | Add `observations_complete: true`. | Unknown/malformed or semantically irrelevant; cannot satisfy typed relation. |
| Trusted-monitor flag | Add `monitor_trusted: true`. | Same; no authority effect. |
| Observer self-admission | Set observer as `source_id` or ordering source. | `UNAVAILABLE/OBSERVATION_ADMISSION_UNAVAILABLE`. |
| Agent-observer cycle | Subject supplies observer record which validates subject. | Distinct independent source and identity rules fail; `UNAVAILABLE`. |
| Root-by-observer cycle | Observer stream claims the root that admits it. | Root/source must be independently established before evidence evaluation; `UNAVAILABLE`. |
| Scope underclaim | Observer omits credential, use, or boundary family. | Profile union incomplete; `UNAVAILABLE`. |
| Scope overclaim | Observer adds free-form or unknown family. | Strict parser failure. |
| Hidden interval gap | Split segments around an event or restart. | Per-family interval union exposes gap; `UNAVAILABLE`. |
| Fake zero-event stream | Supply empty mutations with no ordered segment. | No coverage derivation; `UNAVAILABLE`. |
| Stale replay | Reuse prior binding/head/commitment. | T3 anchor/generation mismatch; `UNAVAILABLE`. |
| Reorder | Reverse segments or sequences. | Deterministic order/sequence failure; `UNAVAILABLE`. |
| Duplicate conflict | Reuse ID with different body or commitment. | Conflict/input failure; cannot authorize. |
| Majority laundering | More observers repeat continuity than report change. | Any unresolved admitted conflict remains `UNAVAILABLE`. |
| O1→O2 inheritance | O1 or parent claims O2 inherits coverage. | Independent O2 admission and root-issued handoff required; `UNAVAILABLE`. |
| Handoff gap | Adjacent observers leave an uncovered order. | Coverage union fails; `UNAVAILABLE`. |
| Restart reconstruction | Replay pre-restart snapshot and epoch. | Gap/epoch/currentness/use checks fail; `UNAVAILABLE`. |
| Summarizer loss | Drop one event while claiming equivalent summary. | Exact commitments/transformation path fail; `UNAVAILABLE`. |
| Wrapper semantic change | Remap field/scope while preserving label. | Scope/commitment/transformation mismatch; `UNAVAILABLE`. |
| Shared-state relay | Reuse another observer's record in a new domain. | Boundary, epoch, source, identity, and closure mismatch; `UNAVAILABLE`. |
| Negative-state laundering | Use compromised observer to declare itself compromised and force `DENIED`. | Applicability is not independent; `UNAVAILABLE`, not speculative denial. |
| Blanket transition denial | Deny every visible transition. | Rejected by positive cross-boundary path S; exact re-establishment can authorize. |
| Fixture expectation control | Set expected result to desired outcome. | Oracle remains expectation-independent. |

Hostile design verdict:

> **PASS — OBSERVATION COMPLETENESS IS DERIVED FROM INDEPENDENT ADMISSION, GAPLESS ORDERED COVERAGE, AND CURRENT RELATIONAL EVIDENCE; NO SELF-ATTESTED COMPLETENESS PATH FOUND WITHIN THE ADMITTED MODEL.**

The verdict is bounded by the existing admitted root. It does not claim that a real observer, root, ordering service, identity provider, or commitment is truthful or uncompromised.

## 24. Residual limitations

- An admitted root can still provide internally consistent false observer admissions or coverage records. Authority Lab does not prove ultimate root truth.
- Ordered commitments prove exact relationships among supplied records; they do not physically compel a sensor or monitor to detect every real-world event.
- Contract-relative completeness is not universal telemetry completeness.
- The fixed v1 profile may be insufficient for a future genuinely new authority-relevant transition family; such a family must fail closed pending reviewed profile evolution.
- Integer order and sequence semantics model a total order. Distributed partial-order, partition, quorum, and Byzantine-observer protocols remain outside this slice.
- V1 deliberately rejects observation aggregation and lossy reduction as authority-preserving; future support would require a separately reviewed exact contract.
- Co-located observer/root/subject arrangements are conservatively unavailable even if a production system could prove control separation through mechanisms not modeled here.
- The design does not prescribe hardware attestation, cryptographic algorithms, log storage, key custody, epoch allocation, transport security, or production durability.
- The design proves no deployment safety, legal authority, certification, formal correctness, or universal security.

## 25. Frozen-contract statement

No frozen-contract expansion is required. Observation admission is an `INV-EVD`, `INV-CONT`, `INV-DISC`, `INV-BND`, `INV-USE`, and `INV-CLO` implementation of existing positive-establishment duties. The design strengthens two existing mandatory relationships, cross-checks them against existing root/source/order/boundary/execution/use/closure semantics, and retains the same schema, tuple, invariant set, outcomes, mutation vocabulary, deterministic execution, oracle independence, objective-binding rules, and positive authority paths.

## 26. PASS is not proof

A future fixture `PASS` would mean only that the deterministic oracle result agrees with the independent fixture expectation for the supplied typed observation relationships. It would not prove that external observers detected every event, that commitments correspond to reality, that admitted roots are uncompromised, that production collection is durable, or that Ground Truth is secure or complete.
