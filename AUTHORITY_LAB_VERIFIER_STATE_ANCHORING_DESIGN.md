# Authority Lab v1 Verifier-State Anchoring and Recovery Design

## 1. Baseline

This design starts from the exact reviewed Durable Verifier-State frontier at commit `c4caf1dbda32bf6ac4a5668e4ba322b7a79ecef3`, whose parent is the reviewed Observation Commitment Envelope implementation at `3637fecc03e801b46188cd69d83bb87381590aca`.

The executable baseline remains:

- schema `authority-lab-v1`;
- tuple `(subject, artifact, control_state, identity_basis, boundary_epoch, decision)` — exactly six coordinates;
- invariants `INV-CONT`, `INV-DISC`, `INV-BND`, `INV-EVD`, `INV-USE`, and `INV-CLO` — exactly six invariants;
- outcomes `AUTHORIZED`, `DENIED`, and `UNAVAILABLE` — exactly three outcomes;
- `183/183` public tests passing; and
- `112/112` Authority Lab fixtures passing.

The current implementation has strict commitment envelopes, exact canonical SHA-256 encoding, verifier-bound authenticity and freshness, append-only predecessor links, unique-head checkpoints, and a harness-owned durable-state manifest. It correctly rejects a candidate that disagrees with the supplied manifest. This design addresses the next boundary: how the manifest itself is established as current, unique, and recoverable.

This is design-only. It changes no executable code, fixture, schema, public tuple coordinate, invariant, or outcome.

## 2. Exact rollback counterexample

`LAB-V1-032` and `LAB-V1-112` share the same exact state key and stream generation. `032` is commitment position 0 and `112` advances the stream to position 1.

The reviewed reproducer is:

```text
position 0 + position-0 trusted context
  -> AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED

position 1 + position-1 trusted context
  -> AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED

restore position 0 + restore position-0 trusted context
  -> AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED
```

The third result is wrong for a history in which position 1 was already accepted. The restored checkpoint and manifest are internally valid and mutually consistent, but nothing outside them establishes that they are current. The same collapse occurs when an entire verifier VM/container snapshot is restored, when a persisted update is lost, or when a pre-correction/pre-successor snapshot is reinstated.

The repair must make the third evaluation `UNAVAILABLE`, unless independently current recovery evidence establishes that position 0 is genuinely the current authorized state rather than a stale prefix.

## 3. Split-brain counterexample

The reviewed frontier constructed two canonical position-1 histories with:

- the same state key;
- the same stream generation;
- the same predecessor state and commitment;
- the same logical position; and
- different head commitment digests.

Each branch was paired with its own internally matching checkpoint and trusted context. Evaluated in isolation, both returned:

```text
AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED
```

Co-present branches already fail closed. The defect is cross-replica and cross-invocation: an isolated replica has no independently current fact selecting one head or declaring the heads unresolved. Arrival order, digest order, signature count, and “first writer wins” are not authority.

## 4. Defect statement

The harness-owned `trusted_commitment_state.json` prevents fixture JSON from supplying trusted verifier state, but it is a per-fixture mapping rather than an authenticated monotonic store. Each entry contains an exact state-key digest, stream identity/generation, previous and current verifier-state digests, head position/digest, checkpoint ID, and freshness challenge ID. It has no independently anchored position, anchor lineage, anchor predecessor, store generation, replica membership, installation receipt, or recovery provenance.

Therefore:

> Internally consistent verifier memory is not sufficient evidence that verifier memory is current.

And:

> Recovery can reconstruct state; it cannot manufacture authority continuity.

The defect is one missing relationship—independently anchored currentness—with rollback, snapshot restore, split brain, circular reconstruction, verifier replacement, correction loss, and successor-history loss as manifestations.

## 5. Normative authority requirement

Before a verifier checkpoint can support `AUTHORIZED`, the oracle must establish all of the following:

1. the checkpoint is internally exact and selects the commitment head, as today;
2. an independently admitted anchor source binds an exact anchor to the verifier-state key and head;
3. that anchor is current in a non-forked monotonic anchor lineage;
4. the verifier generation and durable-state identity are exact and not restored aliases;
5. any recovery or rotation is explicitly authorized, ordered, complete, and installed;
6. no unresolved current anchor, replica, recovery, or required-witness conflict exists; and
7. all existing observation, objective, boundary, identity, grant/use, shutdown/successor, freshness, and closure requirements remain established.

The candidate, observer, verifier, recovery process, or witness cannot authorize its own anchor. A hash, signature, counter, quorum, storage flag, or successful replay is evidence only. The applicable root may admit sources and policies; it does not turn self-produced currentness claims into independent currentness.

## 6. Typed anchor relation

### 6.1 Placement and trust separation

The design uses two complementary representations:

- strict candidate-visible relational evidence under the existing `evidence_binding` composition; and
- harness-owned trusted anchor context obtained from an external anchor adapter, never from fixture/candidate JSON.

The oracle requires an exact join between them. Candidate-visible evidence proves what an admitted source asserted. Harness-owned context supplies the independently retained current anchor observation. Neither side alone can authorize.

No top-level schema field is added. The implementation may extend the strict `evidence_binding` record with immutable internal arrays for anchor admissions, anchor statements, anchor links, recovery installations, verifier rotations, anchor rotations, replica observations, and witness-source admissions. This is an internal typed relation, not a seventh tuple coordinate or new public invariant.

### 6.2 `VerifierStateAnchor`

Each anchor statement has exactly these semantic members:

```text
relationship = VERIFIER_STATE_ANCHOR
anchor_id
anchor_generation
anchor_source_id
anchor_source_generation
anchor_source_identity_basis
anchor_key_id
anchor_key_generation
anchor_position
anchor_digest
predecessor_anchor_id
predecessor_anchor_generation
predecessor_anchor_position
predecessor_anchor_digest
verifier_id
verifier_generation
verifier_identity_basis
durable_state_id
durable_state_generation
exact_state_key_digest
stream_id
stream_generation
head_logical_position
head_commitment_id
head_commitment_digest
verifier_state_digest
checkpoint_id
checkpoint_generation
applicable_boundary
boundary_epoch
authority_root_id
authority_generation
lineage
ordering_source_id
anchor_event_order
freshness_challenge_id
recovery_eligibility
lifecycle_state
canonical_payload_digest
signature_evidence_id
```

Rules:

1. Every field is exact and strictly typed. Unknown or extra members are malformed; missing semantic evidence is `UNAVAILABLE`.
2. `anchor_digest` is a domain-separated canonical digest over every semantic member except the digest and signature reference themselves. It is evidence integrity, not authority.
3. The exact state key continues to bind observation binding, root generation/lineage, boundary epoch, observer generation, and stream generation. It additionally joins to the exact verifier and durable-state identities through the anchor.
4. `anchor_source_id` must have one exact current root-issued admission for `VERIFIER_STATE_CURRENTNESS`. It cannot equal the subject, observer, commitment issuer, commitment verifier, recovery actor, or a witness whose statement it is validating.
5. Source admission binds identity basis, key generation, scope, exact boundary/epoch, stream/state-key family, lifecycle, ordering source, and maximum authority. A source cannot widen its own scope.
6. `anchor_position` is monotonic only within the exact tuple `(anchor_source_id, anchor_source_generation, durable_state_id, durable_state_generation, exact_state_key_digest, stream_id, stream_generation)`.
7. A numeric position is never self-authenticating. The harness-owned adapter must return the current source observation for the exact anchor lineage, and it must match the typed statement.
8. Genesis is allowed only by an exact root-ordered anchor-source admission. Non-genesis anchors require one exact predecessor link at position `N-1`.
9. The selected anchor must exactly bind the candidate checkpoint and current verifier-state digest. A valid anchor for another head, stream generation, boundary epoch, or verifier generation is inapplicable.
10. `recovery_eligibility` is a constrained enum (`NORMAL`, `RECOVERY_CHECKPOINT`, or `NOT_RECOVERABLE`) issued by the admitted anchor authority. It is not a Boolean shortcut and does not itself authorize recovery.
11. Negative lifecycle states (`REVOKED`, `REJECTED`, `INVALID`, `SUPERSEDED`) are evaluated through existing lifecycle and source-authority ordering semantics.

### 6.3 Harness-owned `TrustedAnchorContext`

The external adapter supplies exactly one current observation per anchor lineage:

```text
exact_anchor_key_digest
anchor_id / anchor_generation / anchor_position / anchor_digest
predecessor_anchor_digest
exact_state_key_digest
stream_id / stream_generation
head_logical_position / head_commitment_digest
verifier_id / verifier_generation / verifier_state_digest
durable_state_id / durable_state_generation
adapter_source_id / adapter_source_generation
adapter_observation_id / adapter_observation_generation
adapter_event_order / freshness_challenge_id
```

Fixture data cannot provide or select this context. The adapter contract must be compare-and-advance or return a signed/current anchor observation from a protected source; simple file replacement is insufficient. Two incomparable current contexts for one anchor key are a conflict, not two valid choices.

The oracle can validate exact context. Protecting the adapter’s real persistence, keys, and currentness remains an explicit external trust precondition.

## 7. Monotonicity semantics

For one exact anchor key:

1. genesis position is `0` and has the reviewed genesis sentinel predecessor;
2. each ordinary anchor advances exactly by one and names the immediately preceding anchor digest;
3. the harness-owned current context selects one exact greatest admitted position/digest;
4. a candidate anchor lower than the selected position is replay and yields `UNAVAILABLE`;
5. the same position with a different digest is a fork and yields `UNAVAILABLE`;
6. a higher position without exact predecessor continuity and current adapter acknowledgement yields `UNAVAILABLE`;
7. position reuse after source, key, durable-store, verifier, or stream generation change is not continuity; the new lineage needs an authorized transition relation;
8. self-declared timestamps, reset counters, and larger integers do not outrank the current anchor context; and
9. an anchor cannot claim that no later anchor exists. Only the independently admitted current-context observation can establish that bounded currentness.

The required property is not “largest number seen in this invocation.” It is exact agreement with the independently retained current anchor lineage.

## 8. Rollback detection

Evaluation order is fail closed:

1. parse and validate exact typed relations;
2. establish applicable current root/source/lifecycle facts;
3. compute the candidate checkpoint and verifier-state key;
4. obtain the harness-owned current anchor context for that exact key;
5. require exactly one matching anchor statement and canonical digest;
6. compare anchor lineage, position, head, verifier generation, durable-state generation, and freshness;
7. evaluate recovery/rotation if the candidate was installed rather than normally advanced; and
8. only then allow the existing commitment and authority evaluation to continue.

For the reviewed rollback:

```text
anchor position 1 was independently retained
+ restored candidate/checkpoint position 0
+ restored ordinary verifier manifest position 0
=> UNAVAILABLE / VERIFIER_STATE_ANCHOR_REPLAY
```

Rolling back the candidate and ordinary manifest together no longer suffices because the separately supplied current anchor context still selects position 1. If the external anchor context is also rolled back without any surviving comparison source, that is the explicit residual trust-boundary failure in section 24.

## 9. Replica consistency

### 9.1 Identities and membership

Each verifier replica has an exact replica identity, generation, identity basis, verifier generation, durable-store identity/generation, boundary/epoch, membership epoch, and lifecycle record. Root-issued membership does not give a replica authority to choose the current head.

### 9.2 Unique current head

For one anchor/state key, `AUTHORIZED` requires one anchor-selected current head. Two heads from one predecessor are incomparable until an admitted resolution exists. Each isolated branch lacks authority unless its digest is selected by the independently current anchor context. Thus a hidden branch cannot authorize solely from its local manifest.

### 9.3 Conflict and reconciliation

- Co-present or externally reported forks yield `UNAVAILABLE / VERIFIER_STATE_REPLICA_CONFLICTING`.
- A branch cannot win by arrival order, signature count, lexical digest order, or local sequence.
- Reconciliation requires an exact root-ordered resolution or correction relation that names all known competing anchor/head digests, selects the continuing lineage, records the disposition of rejected branches, advances the anchor, and is independently current.
- Explicit current prohibition or revocation of a branch/source may yield `DENIED`; mere divergence remains `UNAVAILABLE`.
- A general Byzantine consensus protocol is not required by this design. If deployment policy uses one, its membership epoch and committed result must still enter as exact admitted evidence rather than an unchecked quorum Boolean.

## 10. Recovery installation

### 10.1 `VerifierStateRecoveryInstallation`

A recovery installation is a strict typed relation with at least:

```text
relationship = VERIFIER_STATE_RECOVERY_INSTALLATION
recovery_id / recovery_generation
recovery_authority_id / recovery_authority_generation / identity_basis
source_anchor_id / generation / position / digest
source_checkpoint_id / generation
source_head_position / commitment_id / digest / verifier_state_digest
target_verifier_id / generation / identity_basis
target_durable_state_id / generation
target_stream_id / generation
replay_start_position / replay_end_position
replay_commitment_ids / replay_commitment_digests
replay_link_ids
replay_correction_ids
replay_terminal_event_ids
replay_completeness_evidence_id
final_head_position / commitment_id / digest
final_verifier_state_digest
installation_receipt_id / digest
installation_event_order
applicable_boundary / boundary_epoch
authority_root_id / authority_generation / lineage / ordering_source_id
freshness_challenge_id
lifecycle_state
```

The recovery authority is independently root-admitted for an exact verifier/store/state-key/boundary scope. It cannot be the subject, candidate, observer, commitment issuer, recovered verifier, or anchor source whose currentness it is asserting.

### 10.2 Installation rules

1. The source anchor must be the exact current anchor or an explicitly retained recovery checkpoint selected by the current anchor.
2. `NOT_RECOVERABLE` anchors cannot seed recovery.
3. The target verifier and durable store use fresh generations. Reusing a rolled-back generation is not installation.
4. Replay is verified before installation; installation is represented by a separate receipt bound to the final bytes/digest and target identity.
5. The receipt must be ordered after replay verification and before the fresh T3 checkpoint/challenge.
6. The anchor must advance to select the installed target state. An installation receipt not reflected in the independently current anchor is provisional and yields `UNAVAILABLE`.
7. Old verifier/store generations are superseded or revoked by exact lifecycle/order records. Observer handoff, verifier key possession, or store copy does not imply recovery authority.
8. A crash between preparation and anchor advancement leaves recovery incomplete and `UNAVAILABLE`; it cannot expose two authoritative heads.

## 11. Replay completeness

Local append-only linkage proves that supplied records form a chain; it does not prove that the chain is the whole required history. Complete recovery requires:

1. a current anchor that fixes the expected source checkpoint and required terminal head/position (or fixes a source checkpoint plus an independently current later target anchor);
2. exact inclusive replay bounds;
3. every commitment and predecessor link in position order with no position gap, duplicate, reorder, or unexplained branch;
4. all correction/supersession relations and dispositions in the interval;
5. all authority-relevant terminal, shutdown, successor, generation, boundary, grant/use, observation-handoff, and lifecycle records in the interval;
6. observation completeness over the recovery interval and semantic families;
7. a completeness appraisal from the independently admitted recovery authority, bound to the exact ordered replay digest and anchor endpoints; and
8. an installation receipt and post-installation current anchor.

Exact replay of an old prefix is not complete if the current anchor requires a later end. A locally contiguous chain from a stale anchor is not complete. Reordered records fail even if their set is identical. A summary or candidate assertion cannot stand in for the exact ordered replay digest.

If independent evidence establishes only a checkpoint, replay may advance beyond it only when each new anchor is installed through normal monotonic progression. Recovery data do not get to predict their own terminal head.

## 12. Circular recovery prevention

The following cycle is forbidden:

```text
candidate history
  -> reconstruct trusted verifier state
  -> reconstructed state validates candidate history
  -> AUTHORIZED
```

The exact controls are:

- candidate JSON cannot supply trusted verifier or anchor context;
- no anchor is admitted unless it matches the separately obtained harness-owned current anchor context;
- recovery authority is independent of candidate, subject, observer, verifier, and anchor producer roles;
- the source anchor predates and scopes the recovery operation;
- completeness is checked against independently fixed endpoints, not a candidate-chosen last record;
- installation needs a separate receipt and post-installation anchor advancement; and
- derived manifests, copied stores, wrappers, summaries, witness aggregates, and replay tools cannot inherit source authority through `INV-CLO`.

Missing trusted anchor context remains `UNAVAILABLE`. Rebuilding every old manifest field from a candidate cannot change that result.

## 13. Verifier rotation

Verifier replacement uses an exact `VerifierRotation` relation:

1. V1 is currently admitted and bound to the current anchor/head.
2. The applicable root/orderer authorizes a rotation naming V1 identity/generation and V2 identity basis/generation, exact scope, boundary/epoch, stream/state key, effective event order, and rotation challenge.
3. The recovery/installation process installs the current anchored head into a fresh V2 durable-state generation.
4. An installation receipt binds V2 to that exact state.
5. The current anchor advances and selects V2 and the installed head.
6. V1 is explicitly superseded/revoked at the ordered cutover; overlap policy is exact and cannot create two current writers.
7. Verifier-bound freshness is reissued for V2 after cutover.

Same key, label, copied state, or process restart is not rotation. Rotation without exact authority or anchor continuity yields `UNAVAILABLE`; explicit current prohibition yields `DENIED`. A completed authorized rotation remains capable of `AUTHORIZED`.

## 14. Anchor rotation

Anchor-source/key replacement is more privileged and cannot be inferred from verifier rotation.

An `AnchorRotation` relation binds old and new source identities, generations, identity bases, keys, independence/control domains, exact anchor/state scope, final old anchor, first new anchor, boundary/epoch, ordering, effective cutover, and lifecycle dispositions. It must be authorized by the applicable root/orderer and cross-confirmed by an admitted currentness source that is not solely the new anchor self-asserting its legitimacy.

The first new-source anchor commits to the final old-source anchor and uses a fresh source generation. The old source becomes superseded/revoked at the cutover. Silent key change, reused generation, or a new source claiming `GENESIS` for an existing state key yields `UNAVAILABLE`. Explicitly authorized rotation preserves normal authorization.

If the old anchor is irretrievably unavailable, emergency rotation requires an independently defined recovery authority and enough current external anchor/witness evidence to establish the cutover. Otherwise the safe result is `UNAVAILABLE`, not an invented genesis.

## 15. Witness-source continuity

Witness statements remain optional for normal single-anchor progression unless policy requires them, but they are mandatory where the recovery/replica policy uses witnesses to establish cross-view currentness or source transition.

Each usable witness needs:

- exact witness identity, generation, identity basis, and key generation;
- one root-issued admission for exact anchor/state-key/stream/boundary scope;
- witness source-lineage and control/independence-domain identities;
- predecessor witness statement and covered anchor interval;
- exact head/anchor statement, event order, freshness, lifecycle, and disposition;
- handoff/rotation relation for witness replacement; and
- no role collision with subject, observer, commitment issuer, verifier, recovery authority, anchor source, or another supposedly independent witness control domain.

Rules:

1. Count and signature diversity do not establish independence.
2. Two witnesses with the same upstream source/control domain are one corroboration domain and cannot satisfy a policy requiring two independent domains.
3. Independence is positively established by exact root-issued admissions and disjoint admitted control domains; it is never inferred from different labels.
4. A witness label/key surviving process replacement does not prove source continuity. Fresh generation and exact handoff are required.
5. A coverage gap at recovery or cutover yields `UNAVAILABLE`.
6. Conflicting current witness statements yield `UNAVAILABLE / VERIFIER_STATE_WITNESS_CONFLICTING`; majority vote does not resolve them.
7. An exact current root-ordered resolution may supersede a witness statement, but it must name the conflict and advance the anchor lineage.
8. Witnesses corroborate an anchor/head relation; they cannot create root, anchor, recovery, verifier, observer, or execution authority.

Real organizational or hardware independence remains an external truth claim admitted through these exact source relations.

## 16. DENIED versus UNAVAILABLE

`UNAVAILABLE` applies when required positive establishment is missing or ambiguous, including:

- current anchor absent, stale, replayed, forked, or unmatched;
- verifier and candidate rolled back together;
- replica heads incomparable or a fork is hidden from the selected local state but reported by an admitted source;
- durable-store/verifier generation ambiguous or reused;
- recovery source, provenance, endpoint, replay order, completeness, or installation unavailable;
- circular candidate-derived reconstruction;
- verifier or anchor rotation incomplete;
- anchor freshness unavailable;
- required witness independence/coverage unavailable;
- witness or anchor conflicts unresolved; or
- external anchor adapter unavailable.

Suggested precise reason families are `VERIFIER_STATE_ANCHOR_UNAVAILABLE`, `VERIFIER_STATE_ANCHOR_REPLAY`, `VERIFIER_STATE_ANCHOR_FORK`, `VERIFIER_STATE_REPLICA_CONFLICTING`, `VERIFIER_STATE_RECOVERY_UNAVAILABLE`, `VERIFIER_STATE_RECOVERY_INCOMPLETE`, `VERIFIER_STATE_ROTATION_UNAVAILABLE`, `VERIFIER_STATE_WITNESS_UNAVAILABLE`, and `VERIFIER_STATE_WITNESS_CONFLICTING`.

`DENIED` applies only when exact current authoritative evidence explicitly revokes, rejects, invalidates, or prohibits the applicable anchor source, verifier, durable-state lineage, recovery authority, recovery operation, successor, or execution authority. Uncertainty is never converted into denial.

`AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED` remains possible only after exact anchored currentness plus all existing authority requirements are established.

## 17. Hostile matrix A–AJ

`Current` describes the reviewed implementation boundary. `External?` means whether some fact must ultimately be supplied by protected state outside the deterministic oracle; it does not mean the case is exempt from fail-closed modeling.

| ID | Scenario | Current behavior | Designed outcome / reason | Required facts | Invariants | Durable external state? | Fits v1? | Outside deterministic trust boundary? |
|---|---|---|---|---|---|---|---|---|
| A | Verifier and candidate roll back together | Restored head can `AUTHORIZED` | `UNAVAILABLE / ANCHOR_REPLAY` | retained later anchor selecting H1 | `CONT DISC EVD USE` | Yes | Yes | Only if the anchor also rolls back unseen |
| B | Manifest-only rollback | Visible mismatch usually `UNAVAILABLE` | `UNAVAILABLE / ANCHOR_REPLAY` | exact current anchor/context | `CONT EVD USE` | Yes | Yes | No |
| C | Candidate-only rollback | `UNAVAILABLE / COMMITMENT_REPLAY` | same `UNAVAILABLE` | current manifest and anchor | `CONT EVD USE` | Yes | Yes | No |
| D | VM snapshot rollback | Whole restored view can `AUTHORIZED` | `UNAVAILABLE / ANCHOR_REPLAY` | external current anchor and fresh adapter observation | `CONT DISC BND EVD USE` | Yes | Yes | Anchor rollback remains external |
| E | State-key reuse after rollback | Matching old labels can `AUTHORIZED` | `UNAVAILABLE / ANCHOR_REPLAY` | exact store/verifier generations and anchor key | `DISC BND EVD USE` | Yes | Yes | No |
| F | Old anchor replay | No anchor model | `UNAVAILABLE / ANCHOR_REPLAY` | selected greater current anchor position/digest | `CONT EVD USE` | Yes | Yes | No |
| G | Anchor position reuse | No anchor model | `UNAVAILABLE / ANCHOR_FORK` | one digest per exact position; resolution if forked | `CONT DISC EVD USE` | Yes | Yes | Hidden global fork remains external |
| H | Split-brain verifier replicas | Each branch can `AUTHORIZED` | `UNAVAILABLE / REPLICA_CONFLICTING` | replica membership plus unique anchor-selected head | `CONT BND EVD USE` | Yes | Yes | Undisclosed fork outside all sources remains external |
| I | Two heads from same predecessor | Separately `AUTHORIZED` | `UNAVAILABLE / ANCHOR_FORK` | one current anchor or explicit resolution naming both | `CONT EVD USE` | Yes | Yes | Same qualification as H |
| J | Replica fork hidden from isolated invocation | Local branch can `AUTHORIZED` | `UNAVAILABLE` unless external anchor selects it | fresh anchor adapter observation/cross-view evidence | `CONT EVD USE` | Yes | Yes | A fork hidden from every admitted source is external |
| K | Candidate-data state reconstruction | Rebuilt matching context can `AUTHORIZED` | `UNAVAILABLE / RECOVERY_UNAVAILABLE` | non-candidate current anchor, recovery admission, receipt | `CONT EVD USE CLO` | Yes | Yes | No |
| L | Incomplete recovery replay | Locally contiguous prefix may `AUTHORIZED` | `UNAVAILABLE / RECOVERY_INCOMPLETE` | anchored endpoints and exact interval digest | `CONT EVD USE CLO` | Yes | Yes | Completeness source truth remains external |
| M | Reordered recovery replay | Self-consistent rebuilt end may `AUTHORIZED` | `UNAVAILABLE / RECOVERY_INCOMPLETE` | ordered replay, event/position continuity | `CONT EVD USE` | Yes | Yes | No |
| N | Replay missing a correction | Pre-correction state can reappear | `UNAVAILABLE / RECOVERY_INCOMPLETE` | correction inventory bound between anchor endpoints | `CONT EVD USE CLO` | Yes | Yes | No |
| O | Replay crosses shutdown/successor boundary | Predecessor world can reappear | `UNAVAILABLE` absent successor-specific chain | terminal records, fresh identity/epoch/grant and anchors | all six | Yes | Yes | Omitted real terminal event remains external |
| P | Recovery from stale anchor | No exact recovery relation | `UNAVAILABLE / ANCHOR_REPLAY` | current anchor selecting eligible checkpoint | `CONT EVD USE` | Yes | Yes | No |
| Q | Legitimate recovery from current anchor | Not executable end-to-end | `AUTHORIZED` | exact current anchor, complete replay, fresh generation, receipt, new anchor | all six | Yes | Yes | Protected anchor/storage mechanics remain external |
| R | Verifier replacement without rotation authority | Same labels/generation may pass if context matches | `UNAVAILABLE / ROTATION_UNAVAILABLE` | root-issued rotation and fresh V2 installation | `DISC BND EVD CLO` | Yes | Yes | No |
| S | Authorized verifier rotation | Not executable | `AUTHORIZED` | V1 final anchor, rotation, V2 receipt, anchor advance, V1 supersession | all six | Yes | Yes | Key custody remains external |
| T | Verifier generation rollback | Matching rolled context can `AUTHORIZED` | `UNAVAILABLE / ANCHOR_REPLAY` | anchor-bound highest current generation | `CONT DISC EVD USE` | Yes | Yes | No |
| U | Anchor-key rotation without authority | No anchor model | `UNAVAILABLE / ROTATION_UNAVAILABLE` | exact source/key transition | `DISC BND EVD CLO` | Yes | Yes | No |
| V | Authorized anchor rotation | No anchor model | `AUTHORIZED` | root-ordered old/new link, cross-confirmation, cutover | all six | Yes | Yes | Root/cross-source truth remains external |
| W | Multiple witnesses from shared source | Compatible with `AUTHORIZED` | no independence credit; `UNAVAILABLE` if policy requires it | exact source/control domains and admissions | `BND EVD CLO` | Sometimes | Yes | Real independence remains external |
| X | Independent witnesses agree | Labels cannot establish independence | `AUTHORIZED` only with all ordinary facts and exact admitted independence | admissions, scope, interval, freshness, matching anchor | `CONT BND EVD` | Sometimes | Yes | Independence truth remains external |
| Y | Conflicting witnesses | Co-present mismatch `UNAVAILABLE` | `UNAVAILABLE / WITNESS_CONFLICTING` | explicit current resolution to proceed | `CONT BND EVD USE` | Sometimes | Yes | Hidden conflict remains external |
| Z | Witness source replaced behind same identity | Process change invisible | `UNAVAILABLE / WITNESS_UNAVAILABLE` | fresh generation and exact source handoff | `DISC BND EVD CLO` | Sometimes | Yes | Source identity truth remains external |
| AA | Witness continuity gap | Coverage not represented | `UNAVAILABLE / WITNESS_UNAVAILABLE` | gapless anchor/recovery interval coverage | `CONT BND EVD` | Sometimes | Yes | Event delivery remains external |
| AB | External anchor unavailable | No anchor requirement | `UNAVAILABLE / ANCHOR_UNAVAILABLE` | one fresh exact context observation | `CONT EVD USE` | Yes | Yes | Availability itself is external |
| AC | Anchor reports older state | No anchor model | `UNAVAILABLE / ANCHOR_REPLAY` when later state survives elsewhere | greater retained anchor/cross-source evidence | `CONT EVD USE` | Yes | Yes | Universal anchor rollback is external |
| AD | Anchor fork | No anchor model | `UNAVAILABLE / ANCHOR_FORK` | resolution naming all known branches and advancing lineage | `CONT BND EVD USE` | Yes | Yes | Globally hidden branch is external |
| AE | Anchor and verifier collude | Matching context can `AUTHORIZED` | `UNAVAILABLE` if admitted witness/cross-anchor contradicts; otherwise trust failure | independent current comparison source | `BND EVD CLO` | Yes | Yes | Total collusion beyond all independent roots is external |
| AF | Recovery layer manufactures state without anchor | Can recreate matching context | `UNAVAILABLE / RECOVERY_UNAVAILABLE` | independently current anchor and installation receipt | `CONT EVD USE CLO` | Yes | Yes | No |
| AG | Exact complete forward replay | Not executable as recovery | `AUTHORIZED` | anchored endpoints, complete ordered replay, receipt, anchor advance | all six | Yes | Yes | Completeness/currentness source remains external |
| AH | Fresh genesis | Manifest-backed genesis `AUTHORIZED` | `AUTHORIZED` with root-admitted anchor genesis and fresh context | genesis admission, position 0 anchor, exact checkpoint | all six | Yes | Yes | Genesis source truth remains external |
| AI | Non-genesis bootstrap without anchor | Candidate-derived context may authorize | `UNAVAILABLE / RECOVERY_UNAVAILABLE` | eligible current source anchor and complete replay | `CONT DISC EVD USE CLO` | Yes | Yes | No |
| AJ | Fresh successor after recovery | Current successor control can authorize | `AUTHORIZED` with successor-specific identity/boundary/grant plus recovered verifier chain | fresh successor chain, recovery receipt, current anchor | all six | Yes | Yes | Real observation/input truth remains external |

Every repair in the matrix composes existing authority relations. No row needs a seventh coordinate, invariant, outcome, or schema version.

## 18. Positive paths

### 18.1 Normal progression

```text
admitted anchor genesis A0 selects H0
-> verifier advances commitment/checkpoint to H1
-> anchor A1 links A0 and selects H1
-> verifier advances to H2
-> anchor A2 links A1 and selects H2
-> fresh adapter observation selects A2
-> AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED
```

Each transition is exact, root/source authorized, current, non-forked, and bound to the existing observation and objective chain.

### 18.2 Disaster recovery

1. Current adapter context selects recovery-eligible anchor A2/checkpoint C2.
2. Independently admitted recovery authority verifies the exact ordered replay from C2 to the required current anchor A5.
3. Replay includes corrections, terminal events, lifecycle facts, and all semantic families.
4. A fresh verifier/store generation is installed and produces receipt R5.
5. Anchor A6 binds the new verifier generation, R5, and recovered H5; old verifier state is superseded.
6. Freshness is reissued and all ordinary authority facts remain current.

Result: `AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED`.

### 18.3 Verifier rotation

V1 is current at A5. The root/orderer authorizes exact rotation to V2. V2 receives a fresh identity basis and durable-state generation, is installed from H5, obtains a bound receipt, and is selected by A6. V1 is superseded at the cutover. Result: `AUTHORIZED` remains possible.

### 18.4 Fresh successor after recovery

Recovery does not port predecessor execution authority. After recovery, successor B still needs its own exact identity basis, fresh boundary epoch, root-authorized complete observation, current objective binding, and successor-specific grant/use chain. When all are established and the recovered verifier head is anchored, B may return `AUTHORIZED`.

## 19. Existing-field and invariant mapping

| Design requirement | Existing relational home | Invariants |
|---|---|---|
| Anchor/source admission and statement | typed records composed under `evidence_binding`, `binding_source_authority`, `binding_lifecycle`, `binding_ordering` | `BND`, `EVD`, `CLO` |
| Anchor and adapter freshness | existing `freshness` composition plus exact anchor challenge/context | `CONT`, `EVD`, `USE` |
| Verifier/store/replica identity | `identity_basis`, `execution_control_binding`, boundary and lifecycle relations | `DISC`, `BND`, `EVD` |
| Monotonic position and predecessor | commitment ordering/link semantics extended to anchor lineage | `CONT`, `EVD`, `USE` |
| Recovery provenance/completeness | typed `evidence_binding` recovery relation, observation completeness, ordering | `CONT`, `EVD`, `USE`, `CLO` |
| Rotation/supersession | lifecycle, ordering, source authority, identity and boundary relations | all six |
| Witness identity/source/coverage | typed witness admission and evidence under existing observation/evidence semantics | `CONT`, `DISC`, `BND`, `EVD`, `CLO` |
| Replica conflict/resolution | evidence conflict, ordering, lifecycle and unique current anchor | `CONT`, `BND`, `EVD`, `USE` |

`INV-CONT` requires one continuous current history; `INV-DISC` prevents stable labels from proving verifier/store/witness identity; `INV-BND` scopes every source and recovery operation; `INV-EVD` prevents counters, signatures, receipts, and witnesses from becoming authority; `INV-USE` rejects replay and rollback; `INV-CLO` blocks state-copy, wrapper, aggregate, and recovery inheritance. The existing six are sufficient.

## 20. Expected implementation surface

The smallest executable slice is expected to change:

- `authority_lab/model.py`: strict immutable anchor, source-admission, recovery, rotation, replica, and witness-source records; no new top-level schema;
- `authority_lab/commitment.py`: domain-separated canonical anchor, ordered replay, and installation-receipt digests;
- `authority_lab/runner.py`: reject candidate-supplied trusted anchor state and load a harness-owned trusted anchor manifest/adapter result;
- `authority_lab/oracle.py`: exact anchor join, monotonic/replay/fork checks, recovery/rotation validation, replica conflict, and witness-source rules;
- `authority_lab/README.md`: admitted anchor/recovery trust boundary and outcome rules;
- `tests/test_authority_lab.py`: independent direct tests of all new semantics; and
- `cases/authority_lab/`: atomic fixture migration, trusted anchor manifest, and hostile/positive fixtures.

One immutable specification must define every strict relation field and lifecycle value. Parsing, digesting, trace output, and oracle evaluation must consume that specification or mechanically derived constants; uncoordinated accepted and checked field lists are forbidden.

The external anchor adapter is modeled deterministically in the public lab by a harness-owned manifest. Production protected storage, counter, transparency, cosigning, or replication mechanics are not implemented by the lab.

## 21. Fixture implications

All 112 maintained fixtures currently depend on harness-owned commitment context. They must migrate atomically so no `AUTHORIZED` fixture relies on the old unanchored manifest.

Migration requirements:

1. each current trusted context receives one exact root-admitted anchor source, canonical anchor statement, and matching harness-owned current anchor context;
2. negative fixtures keep their normative outcome; migration must not mask their earlier intended failure behind a generic missing anchor;
3. positive genesis/progression/correction/successor fixtures receive the minimum exact anchor lineage needed for their existing intent;
4. fixture expectations remain independent of oracle output;
5. candidate fixtures remain unable to provide `_trusted_commitment_context` or the new trusted anchor context; and
6. migration validation reports every changed fixture and any intentional reason-code precedence change.

New hostile fixtures should continue at `LAB-V1-113` and cover at least A–AJ, with cases combined only when one fixture proves the same semantic rule without losing independent expected outcomes. Required positive fixtures include fresh anchored genesis, normal A0→A1→A2 progression, exact recovery, verifier rotation, anchor rotation, independent witness continuity, correction surviving recovery, and fresh successor after recovery.

## 22. Migration implications and compatibility constraints

- Schema stays `authority-lab-v1`; old unmigrated inputs cannot authorize.
- All six tuple coordinates and six invariant identifiers remain byte-for-byte unchanged.
- `AuthorityOutcome` remains exactly `AUTHORIZED`, `DENIED`, and `UNAVAILABLE`.
- Objective binding, mutation-registry closure, observation admission/completeness, commitment-envelope, shutdown/successor, grant/use, and v0 fail-closed semantics remain intact.
- The old harness manifest may be read only during a one-shot atomic fixture migration tool; runtime authorization cannot fall back to it.
- Missing anchors are `UNAVAILABLE`, not silently grandfathered.
- A legitimate genesis, correction, normal progression, disaster recovery, rotation, and fresh successor remain reachable.
- Determinism is preserved: all adapter observations used by the lab are immutable harness inputs and all canonical digests are reproducible.
- Oracle independence is preserved: expected outcome/reason strings never enter evaluation or trusted context selection.

No half-migrated compatibility state may produce `AUTHORIZED`.

## 23. Prior-art relationship

These comparisons clarify the design space; they are not claims that Ground Truth implements or improves the cited systems.

- TPM monotonic counters and anti-rollback secure storage illustrate protected state that survives ordinary software rollback. Device identity, reset, replacement, ownership, counter scope, and binding to the exact verifier state still need explicit authority semantics.
- Transparency-log checkpoints illustrate authenticated heads and append-only consistency. Split-view detection still needs comparison, gossip, witnesses, or another currentness boundary. Ground Truth does not implement Certificate Transparency or a Merkle log.
- Witness cosigning and gossip illustrate cross-view corroboration. Signature count is not independence, and witness authority remains scoped evidence in Ground Truth.
- Byzantine replicated state machines illustrate why individually valid replicas do not imply one committed state. This design requires exact admitted membership/current-head evidence but does not require Authority Lab to implement general Byzantine consensus.
- Write-ahead logging and crash-consistent journaling illustrate atomic recovery from partial/torn writes. They do not by themselves prevent adversarial rollback or establish authority.
- Remote-attestation verifier/appraisal models distinguish evidence production, appraisal, freshness, and relying-party decisions. Ground Truth retains its own authority semantics and makes no attestation-equivalence claim.

The borrowed concepts are monotonic external comparison, authenticated checkpoints, explicit recovery provenance, crash-consistent installation, and source-aware corroboration. The Ground Truth-specific requirement is that none of those evidence mechanisms independently creates execution authority.

## 24. Residual trust boundary

This design closes rollback only relative to at least one independently current anchor/comparison source. It cannot deterministically detect a world in which every admitted anchor, its protected state, all required witnesses, all comparison sources, and the candidate history are rolled back or compromised consistently and no contrary evidence survives.

Residual external preconditions include:

- truthful anchor-source identity, key custody, and currentness;
- protected monotonic persistence or independently comparable current checkpoints;
- truthful root/orderer admissions and lifecycle records;
- correct external adapter behavior and atomicity;
- truthful replica membership and conflict delivery;
- real witness source/control independence where policy relies on it;
- correct signature, digest, hardware counter, clock, and storage behavior;
- observation/event delivery before commitment construction; and
- at least one non-colluding, non-rolled-back source for recovery currentness.

Anchor/verifier collusion that is contradicted by an admitted independent source fails closed. Total collusion or simultaneous rollback beyond every admitted comparison root is an external trust failure, not something a local deterministic oracle can infer. The design must state this limitation rather than replace it with `anchor_valid=true`.

## 25. Hostile design review

### 25.1 Verifier and candidate rollback together

The rolled ordinary manifest is insufficient. The separately obtained current anchor context selects the later anchor/head, so the restored position returns `UNAVAILABLE / VERIFIER_STATE_ANCHOR_REPLAY`. Bypass survives only if the independent anchor boundary is also rolled back invisibly, which is the declared external limit.

### 25.2 Old but valid anchor replay

Authenticity does not imply currentness. Exact comparison with the adapter-selected current anchor rejects a lower position or stale digest. A fresh self-timestamp and larger candidate counter have no effect.

### 25.3 Split brain hidden from one replica

Neither local head authorizes without an anchor-selected digest. If the anchor or admitted witness evidence reports both heads, the result is `UNAVAILABLE`. If a fork is hidden from every admitted comparison source, detection is outside the deterministic input boundary; the design does not claim otherwise.

### 25.4 Recovery reconstructed entirely from candidate history

Candidate data cannot create trusted anchor context, recovery-source admission, independently fixed replay endpoints, installation receipt, or post-installation anchor advancement. The cycle stops at `UNAVAILABLE / VERIFIER_STATE_RECOVERY_UNAVAILABLE`.

### 25.5 Incomplete replay that looks locally contiguous

The current anchor fixes the required endpoint, and the ordered replay digest binds the entire inclusive interval plus corrections and terminal facts. A valid prefix cannot meet the endpoint; an omitted interior position creates a gap or digest mismatch.

### 25.6 Reordered replay

Replay digest and per-position predecessor ordering are sequence-sensitive. Set equality is insufficient. Reordering yields `UNAVAILABLE / VERIFIER_STATE_RECOVERY_INCOMPLETE`.

### 25.7 Verifier generation reuse

The anchor binds exact verifier identity basis, generation, durable-store generation, and state digest. Replacement requires explicit rotation and fresh generations. Same key/label or copied bytes do not bridge `INV-DISC`.

### 25.8 Witness multiplicity from one source

Admissions expose source/control domains. Multiple signatures in one domain count as one corroboration domain and cannot satisfy an independence requirement. Witness count never selects authority.

### 25.9 Conflicting witnesses

Conflict is `UNAVAILABLE`, not majority resolution. Proceeding requires a current root-ordered resolution naming the conflict and an anchor advance; silent omission of the losing witness is not resolution.

### 25.10 Positive disaster recovery

The design does not require permanent continuity of the failed verifier. A current recovery-eligible anchor, exact complete replay, fresh verifier/store generation, independent recovery admission, installation receipt, post-installation anchor, and ordinary authority chain are sufficient. Therefore disaster recovery remains reachable.

### 25.11 Additional attacks

- **Anchor position reuse:** same-position different digest is a fork; same digest under replaced source/generation is a new lineage needing rotation.
- **Anchor/key self-rotation:** rejected without exact old/new root-ordered continuity and cross-confirmation.
- **Recovery after shutdown:** recovered verifier state does not port predecessor execution grants; successor rules still apply.
- **Correction loss:** required endpoint and correction inventory prevent a pre-correction prefix from installing as current.
- **Replica resolution laundering:** “first,” “majority,” or lexically smallest head cannot replace explicit current resolution.
- **Torn installation:** no post-installation anchor means `UNAVAILABLE`.
- **Candidate-supplied adapter record:** parser/runner rejects it before oracle authority evaluation.
- **Positive progression regression:** A0→A1→A2 with exact links and current adapter context remains `AUTHORIZED`.

Hostile-design verdict:

**PASS — NO REPRODUCIBLE IN-SCOPE VERIFIER-STATE ROLLBACK, SPLIT-BRAIN, OR CIRCULAR-RECOVERY BYPASS SURVIVES THE PROPOSED DESIGN**

This PASS means failure to falsify the proposed design within its explicit deterministic boundary. It is not proof that an implementation, protected store, hardware anchor, witness network, or real deployment is secure.

## 26. Frozen-architecture determination

The repair is representable as typed relational evidence and harness-owned current anchor context composed through existing `evidence_binding`, `freshness`, ordering, lifecycle, source-authority, identity, boundary, observation, use/replay, and closure semantics.

Therefore the frozen architecture remains sufficient:

- schema remains `authority-lab-v1`;
- tuple coordinates remain exactly six;
- invariants remain exactly six;
- outcomes remain exactly three; and
- no unchecked Boolean, self-attested counter, candidate-controlled recovery authority, or new public semantic dimension is required.

Executable implementation is justified as the next bounded slice. It should first implement the strict anchor/source/context join and the exact rollback/split-brain/circular-recovery negative cases, then add recovery and rotation positive paths. It must migrate all 112 fixtures atomically and undergo exact-head hostile testing against adapter rollback, hidden forks, incomplete replay, role cycles, and positive-path reachability.
