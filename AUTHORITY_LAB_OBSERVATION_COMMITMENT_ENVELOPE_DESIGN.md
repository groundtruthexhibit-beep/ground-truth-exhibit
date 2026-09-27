# Authority Lab v1 Observation Commitment Envelope and Anti-Equivocation Design

## 1. Baseline

This design is based on the exact reviewed Observation Commitment Authenticity frontier at commit `669a50c83322c39c451fd599e7ddfb5c50d540e3`.

It is design-only. It does not modify Authority Lab executable code, fixtures, the public contract, deployment authority, or merge authority. The reviewed executable baseline remains:

- schema `authority-lab-v1`;
- tuple `(subject, artifact, control_state, identity_basis, boundary_epoch, decision)` — exactly six coordinates;
- invariants `INV-CONT`, `INV-DISC`, `INV-BND`, `INV-EVD`, `INV-USE`, and `INV-CLO` — exactly six invariants;
- outcomes `AUTHORIZED`, `DENIED`, and `UNAVAILABLE` — exactly three outcomes;
- `167/167` public tests passing; and
- `88/88` Authority Lab fixtures passing.

The current observation implementation already establishes root-only observer admission, exact scope, gapless interval coverage, ordering, stream sequence, handoff, transformation continuity, lifecycle, freshness at the admitted T3 anchor, and co-present conflict handling. The shutdown/successor implementation retains admitted intermediate path effects and makes predecessor grants non-portable after terminal, identity, lineage, or incompatible use discontinuities.

This design preserves those results and adds no seventh coordinate, seventh invariant, fourth outcome, or schema version.

## 2. Exact counterexample

Two schema-valid `LAB-V1-068`-derived inputs use the same:

- observer identity and generation;
- observation-binding identity and generation;
- segment identity;
- stream identity and generation;
- T1/T3 interval;
- event and stream sequence ranges;
- semantic-family scope;
- boundary and epoch;
- authority root and objective binding; and
- freshness facts.

Only their opaque `stream_commitment` strings differ.

Evaluated separately, both return:

```text
AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED
```

Presented together, they correctly return:

```text
UNAVAILABLE / OBSERVATION_CONFLICTING
```

An unchanged valid input can also be replayed after an assumed but unreported later discontinuity and still return `AUTHORIZED` because its admitted freshness relation remains internally equal to its own T3 anchor.

The defect is not failure to compare records that are present together. It is that one isolated view is permitted to establish its own opaque commitment and currentness without positive evidence that it is the unique current head of an independently ordered, replay-resistant commitment lineage.

## 3. Defect statement

The current model proves local consistency of one admitted view. It does not prove commitment authenticity, unique logical position, append-only continuity with a previously trusted head, or cross-view consistency.

The authority error is:

```text
locally complete view
+ admitted observer
+ opaque non-empty commitment label
+ self-contained current anchor
=> AUTHORIZED
```

when the required rule is:

```text
locally complete view
+ admitted observer
+ exact authenticated commitment envelope
+ independently verified digest and issuer
+ unique current head selected by the admitted ordering source
+ verifier-bound freshness
+ durable predecessor-state continuity
+ no unresolved admitted branch conflict
=> AUTHORIZED remains possible
```

Two principles govern the repair:

> Observation authenticity is not enough. Authority requires a current, uniquely accountable, replay-resistant commitment to the relevant history.

> Absence of an observed discontinuity is not proof that no discontinuity occurred.

The second principle remains an external measurement limitation. A commitment can prove exactly what was committed and how that commitment relates to other admitted heads. It cannot prove that a compromised or blind instrument measured an event it never observed.

## 4. Normative authority requirement

The existing contract already requires this repair:

- `ARCHITECTURE.md` requires the exact current tuple, boundary, objective binding, evidence relationship, authority-relevant state, and consumption eligibility to remain established through T3.
- `SECURITY_MODEL.md` requires fail-closed behavior when required identity, proof, evidence binding, freshness, continuity, or current ordering cannot be established.
- `INV-CONT` rejects a T1 result or earlier head as sufficient proof of current T3 continuity.
- `INV-DISC` rejects stable labels, keys, handles, ABA restoration, restart, or copied state as identity continuity.
- `INV-BND` requires exact current root, source, boundary, non-restorable epoch, and ordering lineage.
- `INV-EVD` treats commitments, signatures, consistency proofs, verifier results, and witness statements as evidence rather than authority.
- `INV-USE` prevents replay, rollback, missing negative records, or old complete state from recreating current authority.
- `INV-CLO` prevents wrappers, summaries, relays, witnesses, and transformed commitments from inheriting authority implicitly.

Therefore `AUTHORIZED` requires positive establishment of the unique current admissible commitment head. Merely failing to receive a competing commitment is not positive establishment.

## 5. Typed commitment envelope

### 5.1 Location and role

The envelope is a strict typed relation inside the existing `evidence_binding` value. It strengthens observation evidence; it is not a tuple coordinate or independent authority source.

The existing `segments[].stream_commitment` string is retained only as a redundant digest reference during migration. It must exactly equal the selected envelope's `commitment_digest`; it can never authorize by itself.

`evidence_binding` gains four immutable arrays:

```text
commitment_envelopes
commitment_verifiers
commitment_links
commitment_checkpoints
```

It may additionally contain `commitment_witnesses` when an applicable policy requires cross-check evidence. Witness count never creates authority.

### 5.2 `ObservationCommitmentEnvelope`

Each envelope has exactly these fields:

```text
relationship = OBSERVATION_HISTORY_COMMITMENT
commitment_id
commitment_format = AUTHORITY-LAB-OBSERVATION-COMMITMENT-V1
commitment_digest_algorithm = SHA-256
commitment_digest
observer_id
observer_generation
observer_identity_basis
issuer_key_id
issuer_key_generation
stream_id
stream_generation
logical_position
segment_ids
start_anchor_id
start_event_order
end_anchor_id
end_event_order
start_sequence
end_sequence
scope_families
observation_binding_id
observation_binding_generation
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
freshness_challenge_id
predecessor_commitment_id
predecessor_commitment_digest
canonical_payload_digest
signature_evidence_id
```

Rules:

1. All identifiers are exact non-empty strings; generations, positions, event orders, and sequences are non-negative integers under existing strict integer rules.
2. `scope_families` is the exact immutable Authority Lab observation profile order, not an arbitrary set supplied by the observer.
3. `segment_ids` is non-empty, duplicate-free, and ordered by the segments' event/sequence position. Every named segment must exist, and every authority-relevant segment for the selected stream interval must be named exactly once.
4. Envelope observer, stream, interval, sequence, scope, binding, objective, contract, root, boundary, epoch, lineage, and ordering fields must exactly match independently admitted current records.
5. `logical_position` is monotonically increasing within `(observation_binding_id, observation_binding_generation, observer_id, observer_generation, stream_id, stream_generation)`.
6. A genesis envelope uses exact sentinel values `predecessor_commitment_id = GENESIS` and `predecessor_commitment_digest = GENESIS`, but genesis is permitted only by an exact root-ordering-source stream-generation admission.
7. Every non-genesis envelope identifies the immediately preceding accepted envelope. Skipping a predecessor is not append-only continuity.
8. `freshness_challenge_id` comes from the admitted verifier decision context. The observer cannot create its own freshness challenge.
9. `signature_evidence_id` identifies a separately appraised signature result. Its presence is not signature validity.
10. `commitment_digest` and `canonical_payload_digest` must agree with the verification relation. A digest never issues observer, root, objective, boundary, or execution authority.

### 5.3 Canonical committed body

The committed body is the strict envelope excluding `commitment_digest`, `signature_evidence_id`, and any verifier/checkpoint/witness result. It also commits to an ordered digest of the exact referenced segments, including every segment field and its ordered event representation.

The implementation design must use one domain-separated canonical encoding:

```text
AUTHORITY-LAB-OBSERVATION-COMMITMENT-V1\0
```

followed by each field in the fixed schema order, encoded as UTF-8 bytes with an unsigned decimal byte length and `:` delimiter. Arrays use their fixed order and encode their element count before their elements. Integers use minimal unsigned ASCII decimal form. No Unicode normalization, case folding, whitespace trimming, alternate key order, float coercion, or boolean-as-integer coercion is permitted.

This avoids treating visually similar or differently serialized bodies as identical. Cryptographic signature verification may remain an admitted external verifier operation in v1, but the deterministic oracle must recompute the canonical payload digest with the Python standard library and compare it with the exact verified digest.

### 5.4 Commitment verifier admission and verification

`CommitmentVerifierAdmission` is root-issued and contains:

```text
verifier_id
verifier_generation
verifier_identity_basis
role = OBSERVATION_COMMITMENT_APPRAISER
scope_families
boundary
boundary_epoch
source_id
authority_generation
lineage
ordering_source_id
lifecycle_state
```

The verifier must be distinct from the subject, observer, observer issuer key owner, wrapper, summarizer, relay, authority root, and commitment ordering source. Root admission authorizes the verifier role; the verifier does not authorize itself.

`CommitmentVerification` binds:

```text
verification_id
verifier_id
verifier_generation
commitment_id
commitment_digest
canonical_payload_digest
signature_evidence_id
issuer_key_id
issuer_key_generation
verification_method_id
freshness_challenge_id
verification_event_order
disposition = VERIFIED | INVALID | UNAVAILABLE
```

`VERIFIED` is not a naked boolean. It is accepted only when the verifier is independently current and admitted, all exact bindings match, the canonical digest is recomputed successfully, and verifier freshness/order is current. `INVALID` or `UNAVAILABLE` makes commitment authority unavailable unless an independent current authoritative prohibition/revocation separately establishes `DENIED`.

## 6. Uniqueness semantics

### 6.1 Logical position key

The unique logical position is:

```text
(
  observation_binding_id,
  observation_binding_generation,
  observer_id,
  observer_generation,
  stream_id,
  stream_generation,
  logical_position,
  start_event_order,
  end_event_order,
  start_sequence,
  end_sequence
)
```

Two different commitment digests for this same key are equivocation. Identical metadata is not required for conflict: overlapping envelopes in the same stream lineage conflict when their shared sequence/event positions commit to incompatible history.

### 6.2 Positive uniqueness evidence

Uniqueness is not inferred from the absence of a second envelope. Each selected envelope must have one exact `CommitmentCheckpoint` issued by the current root's existing `ordering_source_id`:

```text
relationship = UNIQUE_CURRENT_COMMITMENT_HEAD
checkpoint_id
checkpoint_generation
verifier_state_id
verifier_state_generation
previous_verifier_state_id
previous_verifier_state_generation
previous_verifier_state_digest
current_verifier_state_digest
observation_binding_id
observation_binding_generation
stream_id
stream_generation
head_logical_position
head_commitment_id
head_commitment_digest
freshness_challenge_id
checkpoint_event_order
source_id
authority_generation
boundary
boundary_epoch
lineage
ordering_source_id
lifecycle_state
```

The checkpoint ordering source is already selected by the current authority root. It must be distinct from the subject, observer, commitment verifier, wrapper, summarizer, and relay. The checkpoint is authoritative only for unique head selection, not for observer admission, objective binding, execution authority, or semantic truth.

The oracle requires exactly one current checkpoint for the applicable stream generation and decision. Missing, duplicate, incomparable, stale, or conflicting checkpoints yield `UNAVAILABLE`.

### 6.3 Same-position and overlap rules

- Same logical key plus same digest is one idempotent record; exact duplicate bodies do not create additional authority.
- Same logical key plus different digest is `UNAVAILABLE / OBSERVATION_COMMITMENT_EQUIVOCATION`.
- Same digest under incompatible metadata is `UNAVAILABLE / OBSERVATION_COMMITMENT_CONFLICTING`; digest equality cannot override scope or identity differences.
- Overlapping intervals in one lineage must commit to identical shared ordered event material and must have an exact verified consistency relation. Otherwise the result is `UNAVAILABLE`.
- Non-overlapping consecutive intervals may authorize only through exact predecessor continuity and the current checkpoint.
- Branch selection cannot be based on arrival order, lexical digest order, majority, first-seen state supplied by the observer, or fixture ordering.

## 7. Anti-equivocation semantics

The evaluator derives a conflict registry keyed by logical position and shared interval. Every envelope, link, checkpoint, verification, and witness record is retained before selection.

For the same observer/stream generation and logical interval:

```text
one digest + one current checkpoint + exact verification
  -> locally eligible

multiple incompatible digests
  -> UNAVAILABLE / OBSERVATION_COMMITMENT_EQUIVOCATION

no current independently ordered checkpoint
  -> UNAVAILABLE / OBSERVATION_COMMITMENT_UNIQUENESS_UNAVAILABLE
```

A checkpoint cannot erase a co-present conflict merely by selecting one branch. An explicit correction or supersession must preserve both prior identities, explain the relationship, advance logical position and durable state, and be current under the ordering source.

Cross-invocation equivocation is addressed by mandatory durable checkpoint continuity. An isolated view cannot authorize from its envelope alone. It must extend the verifier's previously trusted durable state and terminate at the independently ordered current checkpoint. If that state is absent, lost, rolled back, or incomparable, the result is `UNAVAILABLE`.

No deterministic oracle can detect a branch hidden from every admitted verifier, checkpoint source, and witness. Truthfulness and non-equivocation of the ultimate root/ordering infrastructure remain explicit trust preconditions.

## 8. Append-only and consistency model

Authority Lab v1 uses a strict linear commitment lineage, not a Certificate Transparency Merkle tree.

### 8.1 Link types

Every selected envelope has exactly one `CommitmentLink`:

```text
relationship = GENESIS | EXTENDS | CORRECTS | SUPERSEDES | REJECTS_BRANCH
link_id
stream_id
stream_generation
from_commitment_id
from_commitment_digest
from_logical_position
to_commitment_id
to_commitment_digest
to_logical_position
consistency_evidence_id
verifier_id
verifier_generation
ordering_source_id
link_event_order
source_id
authority_generation
boundary
boundary_epoch
lineage
```

Rules:

- `GENESIS` is valid only at logical position zero under a newly admitted stream generation.
- `EXTENDS` advances exactly one logical position and preserves the predecessor history.
- `CORRECTS` advances exactly one position, names the exact defective predecessor, retains it in history, and identifies an admitted correction reason/evidence. It does not rewrite the old position.
- `SUPERSEDES` advances the current head for an authority-relevant policy or representation change and preserves the prior head as non-current.
- `REJECTS_BRANCH` records an explicit current authoritative branch rejection. Rejection yields `DENIED` only if its source and applicability meet the existing exact authoritative prohibition/revocation standard; otherwise branch ambiguity is `UNAVAILABLE`.
- Any jump, cycle, fan-in, fan-out, missing predecessor, predecessor digest mismatch, position reuse, generation rollback, or cross-boundary link without exact re-establishment yields `UNAVAILABLE`.

### 8.2 Consistency evidence

`consistency_evidence_id` identifies a typed verifier result over the predecessor and successor canonical digests and committed segment material. The oracle recomputes all locally available digest relationships and checks the independent verifier relation. A proof label alone is insufficient.

The smallest v1 implementation needs a linear predecessor hash chain, not inclusion or Merkle proofs. A future tree representation may be considered only if scale demands it and must preserve these exact authority semantics.

## 9. Durable anti-replay state

### 9.1 State ownership

Durable anti-replay state belongs to the independently admitted commitment verifier/orderer boundary, not the observed subject or observer. The oracle consumes an exact candidate `CommitmentCheckpoint`, an independently loaded current `TrustedCommitmentState`, and the state store's `CheckpointReceipt` linking the immediately prior and current states.

The runner must not derive that anchor from the candidate fixture itself. The implementation introduces a caller-owned `CommitmentStateStore` boundary keyed by exact observation binding, root lineage, boundary epoch, observer generation, and stream generation. The store exposes:

```text
read_current(exact_state_key) -> TrustedCommitmentState
compare_and_swap(exact_state_key, expected_state_digest, next_checkpoint) -> CheckpointReceipt | conflict
```

The oracle receives a read-only `TrustedCommitmentState` snapshot and `CheckpointReceipt` as separate harness inputs; neither is a field under the candidate fixture's `t1`, `t2`, or `t3`. The snapshot and receipt are exact typed values bound to the candidate envelope and checkpoint. The oracle remains pure and has no access to storage, clocks, randomness, network state, or fixture expectations.

`TrustedCommitmentState` contains exactly:

```text
exact_state_key_digest
observation_binding_id
observation_binding_generation
source_id
authority_generation
boundary
boundary_epoch
lineage
ordering_source_id
observer_id
observer_generation
stream_id
stream_generation
verifier_state_id
verifier_state_generation
verifier_state_digest
head_logical_position
head_commitment_id
head_commitment_digest
checkpoint_id
checkpoint_generation
```

`CheckpointReceipt` contains exactly:

```text
transition_id
exact_state_key_digest
previous_verifier_state_id
previous_verifier_state_generation
previous_verifier_state_digest
current_verifier_state_id
current_verifier_state_generation
current_verifier_state_digest
checkpoint_id
checkpoint_generation
head_commitment_id
head_commitment_digest
freshness_challenge_id
ordering_source_id
receipt_event_order
receipt_digest
```

The in-memory or production store constructs the receipt from the completed atomic transition. Candidate fixture data cannot supply or override it. The oracle recomputes its domain-separated `receipt_digest` and requires exact equality with the independently loaded current state and candidate checkpoint. A receipt label or `COMMITTED=true` flag is never accepted.

Maintained single-case fixtures use deterministic harness-owned state snapshots stored separately from candidate payloads. Focused replay/equivocation tests use one deterministic in-memory store across multiple evaluations and prove that only one candidate can win a compare-and-swap. Fixture discovery resets a named test state namespace explicitly, so test order cannot create authority or change results. Production integration would implement the same interface over protected durable verifier storage.

Candidate-controlled paths, case IDs, namespace strings, or state keys cannot select another trusted state. The runner derives the exact state key from independently admitted root, boundary, observer, and stream relations and rejects a snapshot whose embedded key differs.

### 9.2 State transition rule

The ordering source creates a checkpoint only by an atomic compare-and-swap from the trusted previous verifier state to the exact candidate head. The checkpoint is the typed receipt of that completed state transition, not a request to perform it and not a fixture assertion that a future write will succeed.

The current checkpoint is eligible only when:

1. its `current_verifier_state_*` exactly matches the harness/verifier's independently loaded current durable state;
2. its transition receipt proves that the durable state exactly matched `previous_verifier_state_*` when the atomic compare-and-swap occurred;
3. `verifier_state_generation` advances exactly once;
4. `current_verifier_state_digest` commits to the complete new checkpoint body and previous state digest;
5. the selected commitment exactly extends, corrects, or supersedes the prior accepted head according to an admitted link; and
6. the current checkpoint is bound to the current freshness challenge and T3 anchor.

Checkpoint creation does not authorize the requested execution effect. It only commits the observation-ordering boundary to one current history head. Final authority evaluation remains pure and deterministic, and the later authority-consuming effect remains subject to existing atomic grant/use discipline under `INV-USE`.

Two competing candidates starting from the same previous state cannot both obtain valid current checkpoints: exactly one compare-and-swap may advance the durable state. The losing candidate has no current checkpoint and returns `UNAVAILABLE`. If two successful receipts for the same previous generation are admitted, the ordering source has equivocated and the result is `UNAVAILABLE / OBSERVATION_COMMITMENT_EQUIVOCATION`.

To prevent an invalid candidate from advancing the commitment head as a denial-of-service primitive, orchestration is two-phase without adding an authority outcome:

1. run all pure structural, root/source, observer, envelope, digest, signature-verification, scope, interval, link, objective, boundary, closure, and grant/use prechecks that do not require current-head selection;
2. if any precheck fails, return the existing `UNAVAILABLE` or `DENIED` result and do not call the state store;
3. atomically compare-and-swap the exact candidate checkpoint;
4. on conflict, return `UNAVAILABLE / OBSERVATION_COMMITMENT_UNIQUENESS_UNAVAILABLE`; and
5. perform final pure evaluation that repeats every authority check against the exact final input, returned receipt, and independently read current state before allowing the authority-consuming transition.

The precheck result is an internal implementation stage, not a fourth public outcome and not authority. Only the final oracle result can be `AUTHORIZED`.

### 9.3 Loss and rollback

- Missing durable prior state: `UNAVAILABLE / OBSERVATION_VERIFIER_STATE_UNAVAILABLE`.
- State generation lower than trusted generation: `UNAVAILABLE / OBSERVATION_VERIFIER_ROLLBACK`.
- Same generation with a different state digest: `UNAVAILABLE / OBSERVATION_COMMITMENT_EQUIVOCATION`.
- Same exact checkpoint replay for a new decision challenge: `UNAVAILABLE / OBSERVATION_COMMITMENT_REPLAY`.
- Authoritatively established verifier-state compromise or prohibited rollback: `DENIED` under the existing applicable prohibition/revocation rule.

A hidden rollback of the trusted storage itself cannot be detected by a value loaded from that same rolled-back storage. Protected monotonic persistence or independently anchored checkpoints remain an external trust requirement.

## 10. Verifier-bound freshness

The existing `freshness` relation is strengthened; no new top-level fact is added.

It must additionally bind:

```text
commitment_id
commitment_digest
stream_id
stream_generation
head_logical_position
checkpoint_id
checkpoint_generation
verifier_state_id
verifier_state_generation
verifier_state_digest
verifier_id
verifier_generation
freshness_challenge_id
challenge_issuer_id
challenge_generation
challenge_event_order
```

Freshness is established only when:

- the challenge issuer is the current admitted verifier/orderer boundary and is not the subject or observer;
- the challenge is exact to this decision, observation binding, boundary epoch, and T3 anchor;
- the envelope, verification, checkpoint, and freshness relation all contain the same challenge ID;
- the checkpoint advances the trusted durable verifier state;
- the challenge and checkpoint are ordered at or before the exact current T3 anchor and after the prior trusted state; and
- no current later checkpoint for the same stream lineage is admitted.

An observer timestamp is descriptive evidence only. Re-signing stale history with a new observer timestamp or self-issued challenge does not establish freshness.

## 11. Observer generation continuity

Observer identity, signing-key identity, process/runtime identity, and stream generation are distinct.

- Same observer ID or key after process restart does not prove observer-generation continuity.
- An observer restart requires a new root-issued observer generation and a new stream generation.
- New stream genesis must name the terminal checkpoint of the prior generation in an exact root/orderer-issued generation transition, but predecessor observation authority does not transfer automatically.
- A valid observer handoff preserves coverage only; it does not preserve process identity, stream generation, execution authority, or predecessor grant portability.
- Key rotation may preserve observer and stream continuity only through a current root-issued `AUTHORITY_PRESERVING_KEY_ROTATION` relationship binding old/new key IDs and generations, exact observer generation, stream generation, boundary epoch, position, and checkpoint.
- Reuse of an old stream generation or logical position after restart is rollback and yields `UNAVAILABLE`.
- Child agents, replacement observers, wrappers, relays, shared state, copied checkpoints, and identical code/hash never inherit observer or commitment authority by similarity.

## 12. Correction and supersession

Legitimate correction remains possible without rewriting history.

### 12.1 Valid correction

A valid correction:

1. creates a new envelope at the next logical position;
2. identifies the exact prior commitment ID and digest;
3. uses a `CORRECTS` link with independently verified consistency/correction evidence;
4. preserves the prior commitment in the lineage;
5. advances the durable verifier checkpoint;
6. receives a new verifier-bound freshness challenge;
7. is selected by the current ordering source; and
8. does not retroactively authorize an effect consumed under the defective commitment.

The corrected head may support a later `AUTHORIZED` decision if every other authority requirement is current. The old head becomes stale and cannot be replayed.

### 12.2 Supersession

`SUPERSEDES` is used when a current authoritative policy, representation, or stream transition replaces an earlier admissible head without claiming that the earlier signed body was erroneous. It has the same append-only, ordering, durable-state, and freshness requirements as correction.

### 12.3 Silent correction

Changing a digest at the same logical position, reusing an ID, replacing a body without a new link, or presenting a different branch as ordinary `EXTENDS` is equivocation and yields `UNAVAILABLE`. “First seen wins” and “latest timestamp wins” are prohibited.

## 13. Cross-view consistency

### 13.1 Required evidence

Every isolated view must carry positive evidence of a unique current head:

- the exact envelope and canonical digest;
- an independently admitted verifier result;
- an exact predecessor/correction/supersession link;
- the current root-ordering-source checkpoint;
- continuity from the verifier's trusted durable prior state; and
- verifier-bound freshness for the present decision.

An optional `CommitmentWitness` may cross-check a checkpoint:

```text
witness_id
witness_generation
independence_domain_id
checkpoint_id
checkpoint_generation
head_commitment_digest
verifier_state_digest
witness_event_order
source_id
authority_generation
boundary
boundary_epoch
lineage
lifecycle_state
```

Witnesses must be independently root-admitted for the exact purpose and boundary. Multiple witnesses with the same `independence_domain_id`, source root, shared mutable state, or delegated authority are not independent and cannot be counted as separate support. Majority agreement, repetition, aggregation, or consensus does not create authority.

### 13.2 Conflicts

- Conflicting current checkpoints: `UNAVAILABLE / OBSERVATION_COMMITMENT_EQUIVOCATION`.
- Conflicting current witnesses: `UNAVAILABLE / OBSERVATION_WITNESS_CONFLICTING`.
- Witness/checkpoint mismatch: `UNAVAILABLE`.
- Missing required witness under the applicable root policy: `UNAVAILABLE`.
- Current authoritative witness/verifier/ordering-source revocation: `DENIED` only when exact applicability is independently established.

The mandatory ordering checkpoint, not witness plurality, supplies unique-head admission. Witnesses improve detection and external accountability; they do not replace source authority.

## 14. `DENIED` versus `UNAVAILABLE`

Use `UNAVAILABLE` for:

- missing or unverifiable commitment envelope;
- commitment uniqueness not positively established;
- detected equivocation without an independently applicable prohibition;
- missing, invalid, ambiguous, stale, replayed, or incomparable predecessor/consistency evidence;
- durable verifier state unavailable, lost, rolled back, or conflicting;
- self-issued or stale freshness;
- observer/key/stream generation continuity unresolved;
- hidden/incomparable branch history;
- conflicting verifier, checkpoint, or witness evidence;
- incomplete semantic-family coverage; or
- correction/supersession applicability not established.

Use `DENIED` only when a current authoritative fact exactly establishes an applicable revocation, rejection, invalidity, compromise, or prohibition for the observer, verifier, ordering source, witness, commitment lineage, stream, execution identity, or requested authority-consuming transition.

Use `AUTHORIZED` only after the commitment composition succeeds and all existing objective, identity, boundary, observation, execution-control, transformation, grant/use, closure, lifecycle, and shutdown/successor requirements also succeed.

## 15. Hostile matrix A–X

“Reusable” refers to the predecessor commitment as current authority, not whether its digest remains retained in append-only history. “Durable” means the trusted verifier checkpoint is required. Every repair below fits typed subrelations in existing `evidence_binding`/`freshness` under `authority-lab-v1`.

| ID | Case | Current behavior | Desired outcome / reason class | Required facts | Invariants | Reusable? | Durable? |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A | Identical metadata, different digest | Separate views each `AUTHORIZED`; co-present conflict is `UNAVAILABLE` | `UNAVAILABLE / OBSERVATION_COMMITMENT_EQUIVOCATION` | Canonical envelopes, logical key, unique head checkpoint, prior state | `CONT`, `EVD`, `BND` | No | Yes |
| B | Two commitments at same sequence | Separate views may authorize | `UNAVAILABLE / OBSERVATION_COMMITMENT_EQUIVOCATION` | One checkpointed digest for exact position; both bodies retained for conflict | `CONT`, `EVD`, `USE` | No | Yes |
| C | Same commitment replay after later sequence | Old self-contained view authorizes | `UNAVAILABLE / OBSERVATION_COMMITMENT_REPLAY` | Trusted newer checkpoint, challenge, monotonic state | `CONT`, `EVD`, `USE` | No | Yes |
| D | Replay after stream-generation change | Old generation can authorize if change omitted | `UNAVAILABLE / OBSERVATION_STREAM_GENERATION_STALE` | Current root-issued generation transition and checkpoint | `DISC`, `BND`, `EVD`, `USE` | No | Yes |
| E | Replay after observer restart | Same labels/key may authorize | `UNAVAILABLE / OBSERVER_GENERATION_UNAVAILABLE` | New observer/stream generations and root-issued admission | `DISC`, `BND`, `EVD` | No | Yes |
| F | Stale commitment with self-updated timestamp | Opaque commitment plus current-looking fixture may authorize | `UNAVAILABLE / OBSERVATION_FRESHNESS_UNAVAILABLE` | Verifier challenge, current checkpoint, durable state | `CONT`, `EVD`, `USE` | No | Yes |
| G | Later commitment without predecessor relation | Locally complete isolated head may authorize | `UNAVAILABLE / OBSERVATION_CONSISTENCY_UNAVAILABLE` | Exact immediate predecessor link and consistency verification | `CONT`, `EVD`, `CLO` | No | Yes |
| H | Forked histories | Each branch may separately authorize | `UNAVAILABLE / OBSERVATION_COMMITMENT_EQUIVOCATION` | One ordering checkpoint; durable prior state; branch evidence | `CONT`, `EVD`, `BND`, `USE` | No | Yes |
| I | Overlapping intervals with conflicting history | Co-present conflict blocked; split views may authorize | `UNAVAILABLE / OBSERVATION_COMMITMENT_CONFLICTING` | Shared-range digest consistency and unique head | `CONT`, `EVD`, `CLO` | No | Yes |
| J | Non-overlapping valid append-only continuation | Current local model lacks predecessor proof | `AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED` remains possible | `EXTENDS`, exact next position, verification, checkpoint, freshness | All six | Prior retained, not current | Yes |
| K | Valid explicit correction | Same-position changed digest is conflict | Later corrected decision may `AUTHORIZED` | New position, `CORRECTS`, correction evidence, new checkpoint/challenge | `CONT`, `EVD`, `USE`, `CLO` | Old retained only | Yes |
| L | Silent correction | Separate replacement may authorize | `UNAVAILABLE / OBSERVATION_COMMITMENT_EQUIVOCATION` | Missing `CORRECTS`/checkpoint advancement causes failure | `CONT`, `EVD`, `USE` | No | Yes |
| M | Key unchanged, process/generation replaced | Hidden replacement may authorize | `UNAVAILABLE / OBSERVER_GENERATION_UNAVAILABLE` | Root-issued observer generation and runtime identity continuity | `DISC`, `BND`, `EVD` | No | Yes |
| N | Key rotation with authorized continuity | Key change is not modeled as commitment lineage | `AUTHORIZED` remains possible | Exact root-issued key rotation, same current observer/stream lineage, next checkpoint | `CONT`, `DISC`, `BND`, `EVD` | Prior retained | Yes |
| O | Verifier durable state lost after restart | Candidate fixture can recreate current-looking state | `UNAVAILABLE / OBSERVATION_VERIFIER_STATE_UNAVAILABLE` | Protected prior state or independently anchored recovery checkpoint | `CONT`, `DISC`, `EVD`, `USE` | No | Yes |
| P | Verifier durable state rollback | Old state can make old view appear current | `UNAVAILABLE / OBSERVATION_VERIFIER_ROLLBACK` | Monotonic generation/digest anchored outside candidate input | `CONT`, `DISC`, `EVD`, `USE` | No | Yes |
| Q | Witness agreement over shared compromised source | Repetition may look persuasive outside oracle | `UNAVAILABLE` if witness policy requires independence | Root-issued witness identities and distinct admitted independence domains; no voting | `BND`, `EVD`, `CLO` | No | Yes |
| R | Conflicting witnesses | Only co-present observer conflicts are currently checked | `UNAVAILABLE / OBSERVATION_WITNESS_CONFLICTING` | Exact witness/checkpoint relations and authoritative resolution | `CONT`, `BND`, `EVD` | No | Yes |
| S | Authentic commitment, incomplete scope | Explicit scope loss already fails; opaque body may hide loss | `UNAVAILABLE / OBSERVATION_SCOPE_UNAVAILABLE` | Canonical body binds immutable profile and exact segments | `CONT`, `EVD`, `CLO` | No | Yes |
| T | Complete scope, unverifiable authenticity | Arbitrary non-empty commitment can authorize | `UNAVAILABLE / OBSERVATION_COMMITMENT_UNAVAILABLE` | Admitted verifier, issuer key generation, verification relation, digest recomputation | `DISC`, `BND`, `EVD` | No | Yes |
| U | Current authentic commitment, no anti-replay evidence | Current-looking admitted relation may authorize | `UNAVAILABLE / OBSERVATION_COMMITMENT_UNIQUENESS_UNAVAILABLE` | Durable unique-head checkpoint and challenge | `CONT`, `EVD`, `USE` | No | Yes |
| V | Old commitment after shutdown/successor transition | Omitted transition permits replay; visible path fails closed | `UNAVAILABLE`; applicable current prohibition is `DENIED` | Terminal checkpoint, fresh successor generation/epoch/stream, new grant/use | All six | No | Yes |
| W | Fresh successor with fresh observation stream | Existing fresh successor path authorizes | `AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED` | New identity, epoch, stream genesis, verifier/checkpoint, objective, grant/use | All six | No | Yes |
| X | Positive append-only normal progression | Current view can authorize without predecessor proof | `AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED` | Exact `EXTENDS`, next position, verified digest, unique checkpoint, durable state, fresh challenge | All six | Prior retained | Yes |

The matrix adds relational proof obligations. It does not create new outcome semantics.

## 16. Positive `AUTHORIZED` path

A normal positive progression is:

1. The current root admits observer `O@1`, commitment verifier `V@1`, ordering source `Q@1`, observation binding `OB@1`, and stream `S@1` for the exact boundary epoch and objective binding.
2. Durable verifier state `VS@7` identifies commitment `C7/D7` at logical position 7 as the previously trusted head.
3. The verifier issues decision-specific challenge `CH8` under its current admitted generation.
4. Observer `O@1` produces envelope `C8/D8` at position 8, names `C7/D7` as immediate predecessor, binds `CH8`, commits to exact complete segments and immutable semantic-family scope, and uses its current admitted key generation.
5. The deterministic oracle recomputes the canonical payload digest. `V@1` supplies an exact current verification relation for the same envelope, digest, key generation, and challenge.
6. An `EXTENDS` link proves exact predecessor continuity. The root's existing ordering source atomically advances `VS@7` to `VS@8` and issues checkpoint receipt `CP8`, selecting `C8/D8` as the unique current head. A competing branch cannot obtain another valid transition from `VS@7`.
7. The harness independently loads current durable state `VS@8`; strengthened `freshness` binds `C8`, `CP8`, `VS@8`, `CH8`, and the exact T3 anchor.
8. Observation coverage, transformation, lifecycle, identity, boundary, objective binding, execution control, grant/use, closure, and all other current requirements succeed.

Expected result:

```text
AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED
```

The checkpoint transition to `VS@8` precedes final evaluation and commits only the observation head; it does not consume execution authority. Evaluation alone does not mutate state. The requested authority-consuming effect remains separately atomic under existing grant/use rules.

A fresh successor follows the same path under a newly admitted identity basis, boundary epoch, observer/stream generation as applicable, current objective/observation chain, and successor-specific grant/use binding. It does not reuse the predecessor's commitment as current authority.

## 17. Existing-field and invariant mapping

| Existing surface | Design use |
| --- | --- |
| `evidence_binding` | Owns commitment envelopes, verifier admissions/results, links, unique-head checkpoints, and optional witnesses. |
| `freshness` | Binds the selected commitment/checkpoint/verifier state and decision challenge to exact T3. |
| `authority_root` | Independently admits observer, verifier, ordering source, boundary, epoch, and lifecycle authority. |
| `binding_source_authority` | Continues to establish objective-binding source only; it does not widen into observation or commitment authority. |
| `binding_ordering` | Supplies the already admitted root ordering-source identity/generation against which commitment checkpoints are cross-checked; it does not select a head by itself. |
| `binding_lifecycle` | Continues objective-binding lifecycle; observation lifecycle records expand to cover commitment verifier, stream generation, checkpoint, and witness admissions. |
| observation admission/completeness | Supplies exact observer identity, immutable scope, anchors, segments, handoffs, transformations, and coverage to which the envelope binds. |
| mutation registry | Existing canonical `evidence_binding` and `freshness` targets already require re-establishment. No new mutation field is needed. |
| `boundary_epoch` / `applicable_boundary` | Bind envelope, verifier, stream, checkpoint, witness, freshness, and successor continuity to the exact non-restorable boundary lineage. |
| `identity_basis` | Separates subject, observer, verifier, issuer key, ordering source, and successor identities; label/key equality is insufficient. |
| closure/transformation semantics | Prevent wrappers, summaries, relays, derived commitments, and transformed streams from inheriting authenticity or completeness. |
| grant/use and shutdown path semantics | Prevent a valid observation commitment from transferring execution authority or making predecessor grants portable. |

Invariant effects:

- `INV-CONT`: exact predecessor-to-head path and T3 checkpoint/freshness.
- `INV-DISC`: observer, key, verifier, stream generation, restart, and rollback distinction.
- `INV-BND`: root/orderer/source/boundary/epoch applicability.
- `INV-EVD`: commitment, verification, proof, checkpoint, and witness evidence exactness without authority promotion.
- `INV-USE`: durable anti-replay state and separation of evaluation from state consumption.
- `INV-CLO`: no authority through summaries, wrappers, witness aggregation, relays, or transformed histories.

## 18. Expected implementation surface

The smallest expected implementation slice changes:

- `authority_lab/model.py`
  - strict frozen dataclasses for envelope, verifier admission/result, link, checkpoint, witness, and strengthened freshness;
  - fixed canonical encoding and SHA-256 payload/segment digest calculation;
  - exact-field, exact-enum, duplicate, integer, canonical-encoding/domain-separator, array-order, and legacy-shape validation;
- `authority_lab/oracle.py`
  - envelope-to-segment matching;
  - canonical digest recomputation;
  - verifier/root/orderer independence and lifecycle checks;
  - logical-key conflict registry;
  - predecessor/link/position/generation checks;
  - durable prior-state and unique-head checkpoint admission;
  - replay, rollback, correction, supersession, branch, witness, and freshness evaluation;
  - fail-closed reason codes without a new outcome;
- `authority_lab/commitment_state.py`
  - immutable `TrustedCommitmentState` and `CheckpointReceipt` values;
  - the exact state-key derivation;
  - a deterministic in-memory compare-and-swap implementation for tests;
  - a storage protocol for production adapters, without shipping or claiming a production durable store;
- `authority_lab/runner.py`
  - two-phase precheck/checkpoint/final-evaluation orchestration;
  - harness-owned state injection that is never read from fixture expectations or candidate T1/T2/T3 facts;
  - deterministic trace of commitment logical key, digest, predecessor, verification, checkpoint, durable state transition, challenge, witnesses, and derived conflict/replay status;
- `authority_lab/README.md`
  - commitment trust boundary, same-schema migration, external durable-state/key/root limitations, and positive progression;
- `tests/test_authority_lab.py`
  - expectation-independent tests for canonicalization, exact parsing, all A–X cases, cross-evaluation trusted-state behavior, oracle independence, and positive paths;
- all 88 maintained fixtures
  - atomic migration to exact envelope, verification, checkpoint, trusted-state, and strengthened freshness relationships; and
- a separate harness-owned trusted-state manifest
  - exact state snapshots keyed by immutable root/boundary/observer/stream context for isolated maintained fixture evaluation; never consulted by the oracle through `case_id` alone; and
- 24 new hostile fixtures `LAB-V1-089` through `LAB-V1-112`
  - one independently expected maintained case for each A–X scenario.

No architecture, security, evidence, tuple, invariant, outcome, or schema-version file requires semantic expansion.

## 19. Fixture implications

All existing fixtures must migrate atomically because every current observation binding contains the opaque commitment form.

- Existing `AUTHORIZED` fixtures gain the minimum exact positive commitment chain and durable verifier-state input appropriate to their current T3 head.
- Existing `UNAVAILABLE` and `DENIED` fixtures receive commitment data only where necessary to ensure their reviewed earlier failure/denial remains the controlling reason. A missing commitment must not accidentally mask a stronger established current prohibition expected to produce `DENIED`.
- Existing shutdown/successor fixtures retain path-sensitive semantics. Commitment migration cannot make a predecessor grant, observer stream, or boundary lineage portable.
- Fixture expectations remain independent. The oracle never reads expected outcome/reason while evaluating.
- The test harness owns the trusted verifier-state snapshot and checkpoint receipt through the separate state interface/manifest. A fixture cannot replace either with a self-selected anchor, path, namespace, or case ID.

Required new fixture outcomes include:

- `UNAVAILABLE` for A–I;
- `AUTHORIZED` for J;
- later `AUTHORIZED` remains possible for K after exact correction;
- `UNAVAILABLE` for L–M, O–U, and V absent a separately applicable prohibition;
- `AUTHORIZED` for N, W, and X when every exact continuity requirement succeeds; and
- `DENIED` controls for exact current observer/verifier/orderer/lineage revocation or prohibition.

## 20. Backward compatibility

- Schema string remains `authority-lab-v1`.
- The six tuple fields, six invariant identifiers, and three outcome strings are unchanged.
- Existing mutation vocabulary remains closed and unchanged; `evidence_binding` and `freshness` are already canonical authority-relevant targets.
- The old typed observation binding with only an opaque segment commitment may remain structurally loadable for deterministic diagnostics, but it can never authorize. It returns `UNAVAILABLE / OBSERVATION_COMMITMENT_UNAVAILABLE`.
- Maintained fixtures migrate together; there is no half-v1 state where opaque and envelope commitments can independently authorize.
- Legacy v0 remains unable to authorize.
- Determinism, standard-library execution, and oracle independence remain required.
- No runtime network, clock, randomness, storage access, or external log query occurs inside the oracle. Challenges, checkpoint receipts, and durable state snapshots are explicit inputs from independent harness-owned boundaries.

## 21. Prior-art relationship

### Certificate Transparency

[RFC 9162, Certificate Transparency Version 2.0](https://www.rfc-editor.org/rfc/rfc9162.html) provides the conceptual distinction between signed log heads, append-only history, inclusion/consistency evidence, and the split-view problem. This design borrows:

- commitment to ordered history rather than an opaque label;
- explicit predecessor/consistency evidence;
- monotonic head progression; and
- the recognition that locally valid signed views do not by themselves prevent equivocation.

Ground Truth does **not** implement Certificate Transparency. Authority Lab v1 uses a bounded linear predecessor chain and root-ordered checkpoints, not a public certificate log, Merkle tree, SCT, STH, or CT gossip protocol. Its semantic families, objective binding, boundary epochs, grant/use state, observer admission, and three authority outcomes are Ground Truth-specific.

### RATS / remote attestation freshness

[RFC 9334, Remote ATtestation procedureS Architecture](https://www.rfc-editor.org/rfc/rfc9334.html) separates evidence appraisal by a verifier from the relying party's authorization decision and describes timestamps, nonces, and epoch identifiers as freshness mechanisms with explicit replay, delay, key, and root-of-trust assumptions. This design borrows:

- an independently admitted verifier role;
- verifier-issued decision freshness challenges;
- separation of evidence authenticity/appraisal from authority; and
- explicit replay and root/key trust boundaries.

Ground Truth does **not** claim remote-attestation equivalence. The envelope is an Authority Lab evidence relationship, not a hardware attestation token, and it does not prove measurement completeness, secure key custody, or a truthful attesting environment.

## 22. Residual trust boundary

The design cannot prove:

- that instrumentation observed every real authority-relevant event;
- that a compromised observation root did not produce a false but internally consistent history;
- that observer, verifier, ordering-source, or witness keys and processes are correctly isolated;
- that protected durable state cannot be secretly rolled back;
- that independently named witnesses are operationally independent;
- that external event delivery completed before the real authority-consuming effect;
- that hardware, firmware, operating-system, hypervisor, connector, identity-provider, clock, nonce source, or root policy is truthful; or
- that a branch hidden from every admitted verifier/orderer/witness exists.

Those are external trust and production assurance preconditions. The repair ensures that missing required commitment evidence fails closed and that an admitted commitment lineage cannot authorize through opaque labels, self-freshness, visible forks, or candidate-controlled rollback. It cannot manufacture truthful measurement.

## 23. Hostile design review

| Attack | Attempt | Designed result |
| --- | --- | --- |
| 1. Isolated equivocated commitment | Supply one of two same-position digests without the competing body. | Envelope alone is insufficient. It must extend harness-owned durable state and match the independently ordered unique checkpoint. Missing/mismatched uniqueness evidence is `UNAVAILABLE`. |
| 2. Replay after newer commitment | Replay old envelope, checkpoint, and freshness. | Trusted durable generation/head is newer; replay is `UNAVAILABLE / OBSERVATION_COMMITMENT_REPLAY`. |
| 3. Verifier rollback | Supply older prior-state anchor inside candidate input. | Candidate cannot select prior anchor. Harness-owned trusted state mismatch is `UNAVAILABLE`; hidden rollback of protected storage remains an explicit external limit. |
| 4. Observer restart with same key | Reuse observer/key/stream generation and old checkpoint. | Key equality is not process identity. Missing new root-issued observer/stream generation yields `UNAVAILABLE`. |
| 5. Branch hidden from invocation | Present one branch plus no conflict. | Positive unique-head checkpoint and prior-state continuity are mandatory. If the admitted ordering infrastructure itself hides a branch, that is the stated root/orderer trust limit, not inferred safety. |
| 6. Correction disguised as continuation | Change prior content and use `EXTENDS`. | Canonical predecessor digest and shared history mismatch; `UNAVAILABLE`. Valid correction needs `CORRECTS` at a new position. |
| 7. Stale body with fresh self-timestamp | Observer changes timestamp/challenge-like text. | Observer timestamp has no freshness authority. Exact verifier challenge/checkpoint/durable advancement is missing; `UNAVAILABLE`. |
| 8. Stream-generation rollback | Reuse an earlier generation after a newer admitted generation. | Root lifecycle, checkpoint generation, and durable state disagree; `UNAVAILABLE`. |
| 9. Witness multiplicity without independence | Duplicate attestations or several witnesses sharing one source/domain. | No voting or aggregation. Witnesses do not select the head, and shared-domain multiplicity creates no additional authority. |
| 10. Positive progression blocked | Supply exact next envelope, verifier result, `EXTENDS`, current checkpoint, durable transition, challenge, and all ordinary authority facts. | `AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED` remains reachable. |

Additional review results:

- Digest equality cannot override metadata, identity, scope, or boundary conflict.
- A unique checkpoint cannot erase a co-present fork.
- A verifier cannot verify its own admission or become the ordering source.
- The subject, observer, wrapper, summarizer, relay, child, successor, or objective-binding delegate cannot issue commitment admission, checkpoint uniqueness, or verifier freshness.
- A new generic evidence ID, signature label, timestamp, key, witness count, or restored checkpoint cannot independently establish currentness.
- Correction and supersession remain append-only and cannot retroactively authorize a consumed effect.
- Valid observer handoff and key rotation preserve only their exact reviewed relationships; neither transfers execution authority.
- A fresh successor and normal append-only progression remain reachable.

Hostile design verdict:

> **PASS — NO REPRODUCIBLE IN-SCOPE OBSERVATION-COMMITMENT EQUIVOCATION OR REPLAY BYPASS SURVIVES THE PROPOSED DESIGN**

This verdict is bounded by the admitted root, ordering source, independent verifier, trusted durable-state anchor, and measurement inputs. `PASS` means failure to falsify the proposed semantic composition within that boundary, not proof of security or truthful external observation.

## 24. Frozen-architecture determination

The existing 6/6/3 architecture remains sufficient.

The repair is an `INV-CONT`/`INV-DISC`/`INV-BND`/`INV-EVD`/`INV-USE`/`INV-CLO` strengthening of two existing mandatory relationships: `evidence_binding` and `freshness`. Existing root, ordering, lifecycle, boundary, identity, observation, mutation, closure, shutdown, and grant/use semantics supply the required authority vocabulary.

The design adds strict typed **relational evidence objects**, reason codes, deterministic digest computation, and a harness-owned durable prior-state input. None is a new public authority dimension. No seventh tuple coordinate, seventh invariant, fourth outcome, or schema version is justified.

Executable implementation is justified in one atomic slice after review of this design. The implementation must migrate all maintained fixtures, add A–X hostile fixtures, preserve positive paths, and repeat the split-view and replay attacks using trusted cross-evaluation state rather than relying only on co-present conflict detection.
