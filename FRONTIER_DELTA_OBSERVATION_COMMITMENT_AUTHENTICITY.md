# Ground Truth Frontier Delta — Observation Commitment Authenticity / Monitor Integrity

## 1. Scope

This document records a bounded research and falsification delta against the exact reviewed Authority Lab v1 shutdown/successor continuity implementation at commit `2fddffbc2a8cd953285c6776f5319975f535d681`.

It is research-only. It does not modify Authority Lab executable code, fixtures, the public contract, deployment authority, or merge authority. Assumed observation failures are represented only as deterministic differences between an external history and admitted records, or as schema-valid competing/replayed observation inputs. It contains no operational monitoring-evasion, shutdown-bypass, persistence, telemetry-suppression, or exploitation technique.

The frozen structure remains:

- schema `authority-lab-v1`;
- tuple `(subject, artifact, control_state, identity_basis, boundary_epoch, decision)` — exactly six coordinates;
- invariants `INV-CONT`, `INV-DISC`, `INV-BND`, `INV-EVD`, `INV-USE`, and `INV-CLO` — exactly six invariants; and
- outcomes `AUTHORIZED`, `DENIED`, and `UNAVAILABLE` — exactly three authority outcomes.

No seventh coordinate, seventh invariant, fourth outcome, or schema version is proposed.

## 2. Exact reviewed baseline

The baseline establishes all of the following inside its admitted fixture-input boundary:

- root-only observer admission;
- exact observer identity and generation;
- immutable observation scope families;
- gapless T1-through-T3 coverage;
- ordered event and stream sequence ranges;
- exact root-issued observer handoffs;
- exact one-to-one observation transformations with commitment continuity and no scope loss;
- root-issued observer/binding lifecycle state;
- an exact freshness head at the current T3 anchor;
- conflict rejection when incompatible records are co-present;
- mutation-registry closure;
- path-sensitive shutdown/successor continuity; and
- successor-specific grant/use non-portability after a terminal or lineage break.

The reviewed executable baseline is `167/167` public tests and `88/88` maintained fixtures passing. A current root-issued complete observation path can still reach `AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED`; explicit current observer revocation reaches `DENIED`; missing, stale, partial, conflicting, or incorrectly transformed admitted observation data reaches `UNAVAILABLE`.

## 3. Trust-boundary statement

Authority Lab already states its boundary exactly:

> Authority Lab v1 assumes fixture-provided root and cryptographic/event commitments as its admitted input model. `KNOWN` means the fixture supplies a value that passes these executable relational checks; it does not prove that a real external monitor emitted the underlying events or that the admitted root is ultimately truthful.

The lab therefore evaluates an admitted representation `F`, not the external history `W` directly:

```text
external history W
  -> acquisition / monitor
  -> delivery / reduction / commitment production
  -> admitted fixture F
  -> deterministic oracle E(F)
```

The shutdown repair correctly ensures that a terminal event retained in `F` cannot disappear through endpoint ABA restoration. It cannot establish that every real event entered `F`, that a `stream_commitment` was authentically issued, or that two separately presented views are globally consistent.

For any two worlds where the pre-admission layers produce identical input,

```text
F(W-continuous) = F(W-discontinuity-suppressed),
```

the deterministic result must also be identical. No local oracle can recover information absent from its input.

This research attacks a narrower adjacent question: whether the admitted model contains enough commitment identity, provenance, freshness, and cross-view consistency semantics to prevent an opaque, replayed, or equivocating commitment from supporting `AUTHORIZED`.

## 4. Current observation model

The executable model reasons about admitted typed records, not a cryptographically verified committed event history.

| Existing representation | What it establishes inside one oracle input | What it does not establish |
| --- | --- | --- |
| `evidence_binding` / `ObservationBinding` | Exact root/objective/contract/boundary linkage; anchors; observers; segments; handoffs; transformations; lifecycle | That an external root actually issued the object or that the object corresponds to the real event history |
| `ObserverAdmission` | Observer ID, generation, identity basis, immutable scope, lifecycle, binding generation | Runtime identity/key custody outside the fixture; that the observer process was not replaced behind reused labels |
| `ObservationSegment` | Stream ID/generation, event and sequence ranges, scope, boundary epoch, opaque `stream_commitment` string | Signature algorithm, signer, signed body, event-set digest, inclusion proof, challenge, receipt, or global uniqueness |
| `ObservationHandoff` | Exact root-context relationship between admitted segments | Authentic external handoff or absence of an unreported temporal gap |
| `ObservationTransformation` | Exact source/target commitment names and scope-preserving one-to-one lineage | Cryptographic verification that the named target is actually a lossless transform of the named source |
| observation lifecycle records | One current root-context lifecycle head per admitted binding/observer | Durable external revocation state or cross-evaluation lifecycle monotonicity |
| `freshness` / `ObservationFreshness` | Exact equality with the admitted T3 anchor, root generation, boundary, lineage, and ordering source | A nonce, trusted timestamp, durable monotonic checkpoint, or proof that the supplied head is the latest external head |
| oracle conflict checks | Conflicts among records co-present in one evaluation | Split views presented to different evaluations or an omitted conflicting observer |

`stream_commitment` is a strict non-empty identifier, and exact equality is enforced within a stream and through transformations. Its contents are not parsed or cryptographically verified. There is no signature, signer/key generation, committed event digest, commitment interval, nonce/challenge, monotonic log size, prior-head link, inclusion/consistency proof, witness receipt, or durable anti-replay/anti-equivocation state.

## 5. Authenticity, completeness, freshness, ordering, integrity, and independence

These properties are distinct and must not collapse into a `trusted_monitor` boolean.

1. **Authenticity** asks who issued the commitment and whether that issuer/key/generation is currently admitted for the exact boundary and purpose. A string named by a root-bound fixture is not cryptographic proof of issuance.
2. **Completeness** asks whether the commitment covers the full required interval and every required semantic family. An authentic signature over a partial record remains partial.
3. **Freshness** asks whether the commitment is current for this T3 decision. A valid old commitment can be authentic and complete for an earlier interval while being replayed now.
4. **Ordering** asks whether the commitment and its events occupy one sufficiently established sequence. Individually valid records may still be reordered, rolled back, or forked.
5. **Integrity** asks whether the committed body is exactly the body appraised and whether later transformations preserve it. An opaque identifier does not itself verify the body.
6. **Independence/source authority** asks whether the evaluated subject can create, select, replace, or control the issuer, key, witness, or appraisal path. A valid signature from a subject-controlled monitor does not create authority.

The current model strongly represents relational completeness, ordering, transformation, and freshness *claims inside one admitted input*. It does not independently authenticate a commitment body or compare separately admitted views.

## 6. Falsification method and exact executable reproducers

All executable probes are in-memory copies of maintained fixtures. No fixture expectation is read by the oracle, and no repository file is changed.

### 6.1 Control and externally suppressed event

Evaluate unchanged `LAB-V1-068`:

```text
AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED
```

The same exact bytes produce the same result for both:

- a continuous external history; and
- an external terminal/identity/boundary discontinuity suppressed before fixture construction.

The desired result for the second world is `UNAVAILABLE`, because current continuity cannot be established. This is an observation-boundary impossibility, not a defect in the deterministic mapping from admitted input to outcome.

### 6.2 Opaque commitment substitution

Starting from `LAB-V1-068`, replace the only segment's:

```json
"stream_commitment": "COMMITMENT-LAB-V1-032-1"
```

with:

```json
"stream_commitment": "COMMITMENT-EQUIVOCAL-VIEW-B"
```

No signer, signature, event body, digest, source lifecycle, freshness challenge, or root-issued commitment record must change because none exists in the admitted model. Results:

```text
original commitment   AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED
substituted commitment AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED
```

This proves that the current executable treats a non-empty commitment label plus surrounding admitted relations as sufficient. It does not authenticate the commitment.

### 6.3 Split-view equivocation

Evaluate the two payloads from 6.2 separately. They have the same:

- observer ID and generation;
- observation-binding ID and generation;
- segment ID;
- stream ID and generation;
- T1/T3 anchors and event interval;
- sequence range;
- semantic scope families;
- boundary epoch; and
- root/objective/freshness context.

They differ only in `stream_commitment`. Both return:

```text
AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED
```

When the second segment body is appended to the first payload so both conflicting bodies are co-present under the same segment/stream identity, the result is correctly:

```text
UNAVAILABLE / OBSERVATION_CONFLICTING
```

The discrepancy is the reproducible counterexample: conflict handling is local to one evaluation. The same admitted observer can present incompatible commitments for the same identity and interval to separate evaluations, and each view can authorize. The lab has no durable uniqueness rule, external witness, consistency proof, or cross-evaluation checkpoint with which to discover the equivocation.

### 6.4 Replay of an old complete view

Evaluate the unchanged valid payload once, assume an external discontinuity occurs but is not delivered, and evaluate the same bytes again. Both evaluations return:

```text
AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED
```

The typed `freshness` relation is equal to the fixture's T3 anchor in both evaluations, but there is no verifier challenge, trusted-time bound, durable later head, or anti-replay state. If a stale head or earlier anchor is visibly supplied, existing fixtures `LAB-V1-056` and `LAB-V1-079` correctly return `UNAVAILABLE / OBSERVATION_FRESHNESS_UNAVAILABLE`. The bypass exists only when old data is replayed as the complete current admitted view.

## 7. A–T hostile matrix

`Current outcome` names the observed executable result for the stated representation. `Boundary` means the adverse fact is absent before input construction and therefore cannot be distinguished locally. `Paired executable defect` means two or more schema-valid evaluations reproduce a failure of global uniqueness/freshness even though each local input passes.

| ID | Hostile case and reproducer | Current outcome | Desired outcome | Reason class / invariants | Determination | Repair inside 6/6/3? |
| --- | --- | --- | --- | --- | --- | --- |
| A | Omitted terminal event; unchanged `LAB-V1-068` represents both continuous and suppressed-shutdown worlds | `AUTHORIZED` | `UNAVAILABLE` for suppressed world | Missing current continuity; `INV-CONT`, `INV-DISC`, `INV-BND` | Observation-boundary impossibility; identical input | Contract yes; requires trusted acquisition outside oracle |
| B | Selectively omit one terminal/identity family while supplying a complete-looking profile | `AUTHORIZED`; explicit missing family in `LAB-V1-053` is `UNAVAILABLE / OBSERVATION_SCOPE_UNAVAILABLE` | `UNAVAILABLE` | Semantic-family completeness; all six, especially `INV-EVD` | Boundary when omission precedes input; correctly blocked when visible | Yes, but independent coverage evidence is required |
| C | Evaluate before delayed terminal event arrives; current-looking prefix supplied | `AUTHORIZED`; an admitted head before T3 is `UNAVAILABLE` (`LAB-V1-056`, `079`) | `UNAVAILABLE` until delivery/currentness is established | Freshness and delivery; `INV-CONT`, `INV-EVD`, `INV-USE` | Delivery race is boundary; visible staleness blocked | Yes with verifier-bound current head; delivery truth remains external |
| D | Prefix begins after a hidden discontinuity and claims T1-to-T3 coverage | `AUTHORIZED`; explicit start gap is `UNAVAILABLE` (`LAB-V1-054`, `055`) | `UNAVAILABLE` | Interval origin/lineage; `INV-CONT`, `INV-DISC`, `INV-BND` | Boundary if the claimed anchor is false | Yes relationally; authentic anchor source required |
| E | Suffix ends before shutdown but is supplied as current T3 | `AUTHORIZED`; explicit stale head is `UNAVAILABLE` | `UNAVAILABLE` | Freshness/delivery; `INV-CONT`, `INV-EVD`, `INV-USE` | Boundary if the false current head is admitted | Yes with freshness challenge/checkpoint |
| F | Summary gives correct endpoint but omits intermediate break | `AUTHORIZED` if summary is the only admitted complete-looking view; explicit loss is `UNAVAILABLE` (`LAB-V1-061`, `080`) | `UNAVAILABLE` | Integrity/transformation; `INV-CONT`, `INV-EVD`, `INV-CLO` | Boundary if raw history is withheld; visible transformation loss blocked | Yes with body-bound transform proof; source truth external |
| G | Observer root/runtime replaced behind identical labels/configuration | `AUTHORIZED`; visible substitution without handoff is `UNAVAILABLE` (`LAB-V1-057`) | `UNAVAILABLE` | Observer identity continuity; `INV-DISC`, `INV-BND`, `INV-EVD` | Identity/input-root limitation | Yes if runtime/key generation is independently attested |
| H | Same root key signs after root-process replacement | `AUTHORIZED` when root/process generation is replayed unchanged | `UNAVAILABLE` absent current root-runtime continuity | Key possession is not process continuity; `INV-DISC`, `INV-BND`, `INV-EVD` | Identity/key-custody limitation | 6/6/3 yes; external attestation/fencing needed |
| I | Two authorized observers provide incompatible histories; co-present versus separately presented | Co-present: `UNAVAILABLE / OBSERVATION_CONFLICTING` (`LAB-V1-059`, `083`); split: each can `AUTHORIZED` | `UNAVAILABLE` until authoritative resolution | Split view; `INV-CONT`, `INV-EVD`, `INV-BND` | Paired executable defect plus delivery boundary | Yes; needs comparable commitments/witness state |
| J | Same observer/stream/generation/interval emits two commitment values in separate evaluations | Both views `AUTHORIZED`; co-present duplicate is `UNAVAILABLE / OBSERVATION_CONFLICTING` | `UNAVAILABLE` | Equivocation; `INV-EVD`, `INV-CONT`, `INV-BND` | **Reproducible paired executable counterexample** | Yes; needs commitment uniqueness/consistency evidence |
| K | Replay unchanged old valid commitment after later hidden discontinuity | Both evaluations `AUTHORIZED`; visibly stale fixture is `UNAVAILABLE` | `UNAVAILABLE` | Replay/freshness; `INV-CONT`, `INV-EVD`, `INV-USE` | Paired temporal counterexample; depends on external later event | Yes; nonce/time/epoch plus durable latest-head state |
| L | Commitment interval is absent/ambiguous, or a falsely broad segment is supplied | Strict malformed input fails; explicit gap is `UNAVAILABLE`; falsely broad valid record can `AUTHORIZED` | `UNAVAILABLE` | Coverage applicability; `INV-CONT`, `INV-EVD`, `INV-BND` | Boundary authenticity of interval claim | Yes with signed exact interval/anchor claims |
| M | Observer covers subject/context but not boundary epoch | Explicit missing scope: `UNAVAILABLE / OBSERVATION_SCOPE_UNAVAILABLE`; falsely claimed scope: `AUTHORIZED` | `UNAVAILABLE` | Boundary-family coverage; `INV-BND`, `INV-EVD` | Correctly blocked when visible; boundary if false | Yes; independent family capability/coverage evidence |
| N | Completeness claim omits one semantic family | Explicit omission: `UNAVAILABLE`; a complete-looking false profile: `AUTHORIZED` | `UNAVAILABLE` | Semantic-family completeness; all six | Correctly blocked when visible; boundary if false | Yes; no naked completeness assertion |
| O | Individually authorized observer handoff has a hidden temporal gap | Explicit gap/no handoff: `UNAVAILABLE / OBSERVER_HANDOFF_UNAVAILABLE` or coverage unavailable; concealed gap: `AUTHORIZED` | `UNAVAILABLE` | Handoff interval continuity; `INV-CONT`, `INV-EVD`, `INV-BND` | Correctly blocked when visible; boundary if concealed | Yes with exact signed overlap/boundary receipts |
| P | Handoff overlap contains disagreeing histories | Co-present conflict: `UNAVAILABLE`; separate non-compared views can each `AUTHORIZED` | `UNAVAILABLE` | Overlap conflict; `INV-CONT`, `INV-EVD`, `INV-BND` | Paired split-view defect | Yes with comparable commitments and resolution source |
| Q | Observer restarts and reuses the same ID, generation, key, and admission | `AUTHORIZED` if restart omitted; visible generation change without handoff is `UNAVAILABLE` | `UNAVAILABLE` absent fresh root-issued admission/handoff | Observer ABA; `INV-DISC`, `INV-BND`, `INV-EVD` | Identity/input-root limitation | Yes with non-restorable observer generation and attestation |
| R | Durable log and live monitor disagree | Co-present: `UNAVAILABLE / OBSERVATION_CONFLICTING`; only one delivered view may `AUTHORIZED` | `UNAVAILABLE` | Source conflict; `INV-CONT`, `INV-EVD`, `INV-BND` | Local conflict blocked; delivery/split-view remains | Yes with joint checkpoint/witness policy; no majority vote |
| S | Commitment label/authentic signature is valid but coverage is incomplete | Explicit incomplete coverage: `UNAVAILABLE`; incomplete body hidden behind a complete-looking opaque label: `AUTHORIZED` | `UNAVAILABLE` | Authenticity does not imply completeness; `INV-EVD`, `INV-CONT` | Current commitment body is not appraised | Yes, with exact signed body/manifest and coverage derivation |
| T | Coverage looks complete but commitment provenance/authority is unestablished | Missing/root-mismatched admitted source: `UNAVAILABLE`; fixture-provided exact root fields plus arbitrary commitment string: `AUTHORIZED` | `UNAVAILABLE` unless issuer/key/current authority are independently established | Authenticity/source authority; `INV-EVD`, `INV-BND`, `INV-DISC` | **Executable commitment-authenticity gap inside admitted representation** | Yes; source-bound signed commitment relation needed |

No uncertainty case should be mapped to `DENIED`. `DENIED` remains appropriate only when a current authoritative fact establishes an applicable observer/execution revocation, rejection, invalidity, prohibition, or compromise. `LAB-V1-067` remains the exact positive control for this distinction: `DENIED / OBSERVATION_SOURCE_REVOKED`.

## 8. Positive controls

The frontier does not make authority impossible.

| Positive control | Current result | Required meaning |
| --- | --- | --- |
| `LAB-V1-066` complete root-admitted coverage | `AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED` | One locally consistent admitted view with all current relational requirements |
| `LAB-V1-058` exact root-issued observer handoff | `AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED` | Gapless, scoped, ordered, non-conflicting handoff preserves observation coverage only |
| `LAB-V1-084` fresh independently admitted successor | `AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED` | Terminal path is visible; successor has fresh identity/epoch/root/objective/observation/grant/use chain |
| `LAB-V1-085` legitimate boundary re-entry | `AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED` | Named boundary may recur only under a fresh lineage and authority chain |

A future commitment-authenticity repair must preserve these paths after adding exact current commitment provenance and consistency evidence. It must not turn every monitor restart, handoff, or successor into permanent denial.

## 9. Direct answers to the research questions

1. **Committed history or admitted event records?** Authority Lab reasons over admitted typed segment, scope, interval, sequence, lifecycle, transformation, and commitment-label records. It does not verify a cryptographic commitment to event contents.
2. **Is observer authorization enough?** No normatively, and not even in the current local evaluator: scope, coverage, order, lifecycle, handoff, transformation, and freshness are also required. But current observer admission plus relationally complete records accepts any exact non-empty commitment label; an authenticated commitment object/relationship is missing.
3. **Can an authorized observer equivocate and still cause `AUTHORIZED`?** Yes across separate evaluations. Two incompatible commitment values for the same observer/stream/generation/segment/interval each authorize when not co-present. Co-present equivocation correctly fails closed.
4. **Can a stale complete history be replayed after a discontinuity?** Yes if the discontinuity and later head are not admitted and the old fixture is replayed as current. Explicitly stale admitted heads correctly fail closed.
5. **Is event delivery represented?** No independent delivery receipt or obligation exists. Segments assert coverage; they do not prove that the external collector delivered every event before the decision.
6. **Can a signature establish authenticity but not completeness?** Yes conceptually. Signature validity authenticates a signed body and signer; it does not prove that the signed body contains every required event or family. Current v1 does not model or verify the signature either.
7. **Can completeness be claimed without proving semantic-family coverage?** A visible narrow profile cannot; the immutable family set and interval algorithm reject it. A false complete-looking claim can because external capability and emission truth are admitted preconditions.
8. **Does root-issued observer admission survive runtime replacement too easily?** Yes when observer ID, generation, key/root fields, and records are replayed unchanged. Visible replacement is blocked; hidden runtime replacement is indistinguishable.
9. **Can existing relations express a repair?** The authority meaning fits existing `evidence_binding`, `freshness`, lifecycle, ordering, root/source authority, observation coverage, and transformation semantics. The executable representation needs an exact commitment envelope and consistency/freshness evidence, but no new tuple coordinate, invariant, or outcome.
10. **Is 6/6/3 sufficient?** Yes at the public-contract level. The defect is incomplete executable evidence representation and cross-evaluation state, not a missing authority dimension.

## 10. Invariant mapping

| Invariant | Commitment-authenticity obligation |
| --- | --- |
| `INV-CONT` | The committed history must cover the full continuity-sensitive interval through the exact T3 head; silence, delayed delivery, or a truncated view is not continuity. |
| `INV-DISC` | Reused observer/root labels, keys, process names, generations, or commitment IDs do not prove the same live observation identity after replacement or restart. |
| `INV-BND` | Commitment issuer, scope, anchors, ordering source, and root lineage must apply to the exact current boundary and non-restorable epoch. |
| `INV-EVD` | A commitment, signature, receipt, witness statement, or transparency proof is evidence, not authority; it must be authentic, applicable, current, exact, and non-promoted. |
| `INV-USE` | Replay, rollback, delayed delivery, missing negative events, or an old complete view cannot recreate current unused authority. |
| `INV-CLO` | Wrappers, summaries, relays, durable logs, live monitors, and transformed streams do not inherit authenticity or completeness without exact current relationships. |

All six are engaged. None requires a seventh invariant.

## 11. Contract sufficiency and frontier classification

The public contract is sufficient to demand the desired outcomes:

- missing, stale, ambiguous, replayed, unauthenticated, partially covered, or conflicting commitment evidence yields `UNAVAILABLE`;
- a current authoritative and exactly applicable revocation/prohibition yields `DENIED`; and
- a current authentic, complete, ordered, fresh, integrity-protected, independently sourced commitment plus every other authority requirement may support `AUTHORIZED`.

The current implementation is locally sound for facts co-present in one admitted input. It is not sufficient for commitment authenticity or global consistency because:

1. `stream_commitment` is opaque and unauthenticated;
2. no exact signed body binds issuer, observer generation, stream generation, interval, scope manifest, event/sequence digest, prior head, objective binding, boundary epoch, and T3 decision;
3. freshness is an admitted equality relation, not verifier-bound anti-replay evidence;
4. conflict detection has no memory or external consistency witness across evaluations; and
5. event delivery and external history truth remain outside the lab.

The split-view reproducer is an executable counterexample at the observation-commitment boundary. The omitted-event reproducer is an observation-boundary impossibility. They must not be conflated: a better commitment protocol can make equivocation, rollback, and replay detectable, but it cannot prove that a compromised or blind measurement root observed an event it never measured.

## 12. Design and implementation implications

A design-only slice is justified before executable work. It should determine the smallest extension of the existing `evidence_binding`/`freshness` relationships that can represent, without self-attestation:

- a canonical commitment envelope binding exact issuer/root, observer and stream generations, decision/objective binding, boundary/epoch, T1/T3 anchors, event and sequence range, immutable semantic-family manifest, committed event-set/root digest, and prior commitment/head;
- exact current signer/key generation and lifecycle under root authority;
- verifier-bound freshness through nonce, trusted time, monotonic epoch/head, or an explicitly chosen composition;
- durable anti-replay state and an ordering rule for later heads;
- same-identity/same-interval commitment uniqueness;
- cross-view consistency evidence, witness/checkpoint policy, or another deterministic anti-equivocation relationship;
- exact transformation proofs over committed bodies rather than label equality alone;
- handoff commitments with no gap and no conflicting overlap; and
- fail-closed behavior when required commitment, signature, inclusion/consistency evidence, witness state, or current head is missing.

This likely requires a new **typed relational object inside the existing observation evidence model**. It does not presently justify a new public primitive, tuple coordinate, invariant, outcome, or schema version. Whether same-schema migration is sufficiently strict must be decided in the design slice; the current research does not authorize implementation.

The design must also specify state ownership. A stateless oracle cannot discover two views never presented together. Anti-equivocation therefore requires either:

- a supplied independently authenticated consistency/witness relation that the deterministic oracle can appraise; or
- durable verifier state outside a single fixture, represented to the oracle as admitted current evidence.

Neither mechanism may be issued solely by the observer or subject whose behavior it is intended to constrain.

## 13. Residual physical/runtime trust assumptions

Even a complete commitment design would not prove:

- that runtime instrumentation measured every authority-relevant event;
- that a compromised measurement root did not sign a false but internally consistent history;
- that keys were generated, stored, rotated, destroyed, or isolated correctly;
- that hardware, firmware, operating-system, hypervisor, connector, or identity-provider roots are truthful;
- that event delivery cannot be delayed beyond an operational authorization race;
- that independent witnesses are actually independent;
- that physical process identity, shutdown, fencing, or credential destruction occurred; or
- that external root policy and appraisal configuration are correct.

Those remain production trust and assurance obligations. Ground Truth can require exact evidence and fail closed when it is unavailable; it cannot manufacture truthful measurement from a compromised or absent observation root.

## 14. Literature and prior-art notes

These references inform the design space without being imported as Ground Truth authority:

- [RFC 9162, Certificate Transparency Version 2.0](https://www.rfc-editor.org/rfc/rfc9162.html) uses signed tree heads plus Merkle inclusion and consistency proofs to make append-only log evolution verifiable. It also notes that detecting inconsistent views requires clients to compare heads (gossip); a signature alone does not make split views globally visible.
- [RFC 9334, Remote ATtestation procedureS Architecture](https://www.rfc-editor.org/rfc/rfc9334.html) separates Attester, Verifier, and Relying Party roles; treats authentic appraisal results as inputs to relying-party policy; describes timestamp, nonce, and epoch-ID freshness; and requires end-to-end integrity and replay protection while retaining explicit root/key-strength assumptions.
- [The Update Framework Specification](https://theupdateframework.github.io/specification/latest/) uses signed role metadata, version monotonicity, expiration, persistent trusted state, and consistent snapshots to address rollback, freeze, and mixed-version views. These mechanisms illustrate why a valid old signature is not sufficient currentness.
- [in-toto specification](https://in-toto.io/docs/specs/) models signed supply-chain step metadata and ordered provenance. Its published [2023 security-audit summary](https://in-toto.io/blog/2023/security-audit/) discusses layout replay, link-file reuse, configuration that filters recorded artifacts, and the need for non-forgeable provenance generation—close analogues to stale commitments and incomplete observation.

The common lesson is compositional: authenticity, append-only consistency, freshness, provenance, and measurement completeness are separate claims. No one signature or `trusted` flag supplies all of them.

## 15. Exact frontier verdict

> **FAIL — REPRODUCIBLE IN-SCOPE OBSERVATION-COMMITMENT AUTHENTICITY COUNTEREXAMPLE FOUND**

Exact counterexample: two schema-valid `LAB-V1-068`-derived inputs with identical observer, observation-binding, segment, stream identity/generation, interval, sequence, scope, boundary, root, objective, and freshness facts but different opaque `stream_commitment` values each return `AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED` when evaluated separately. The same bodies co-present correctly return `UNAVAILABLE / OBSERVATION_CONFLICTING`. Therefore local conflict handling does not establish commitment authenticity, uniqueness, cross-view consistency, or anti-equivocation.

The associated old-view replay reproducer also returns `AUTHORIZED` when the complete prior input is replayed after an unreported external discontinuity. Visible stale heads fail closed; replay presented as current does not.

The frozen 6/6/3 contract remains sufficient. A design slice for an exact root-authorized commitment envelope, verifier-bound freshness, durable anti-replay head, and cross-view consistency/witness relationship is justified. No executable repair is made here.

`FAIL` identifies a bounded executable/compositional counterexample. It does not prove that every deployment is vulnerable, prescribe operational monitoring mechanisms, or prove that any future commitment scheme makes external observation truthful.
