# Frontier Delta: Durable Verifier-State Anchoring, Rollback Recovery, and Witness-Source Continuity

## 1. Exact baseline

This bounded research slice starts from the reviewed Authority Lab v1 Observation Commitment Envelope implementation:

- repository: `groundtruthexhibit-beep/ground-truth-exhibit`;
- starting branch: `fix/authority-lab-v1-observation-commitment-envelope`;
- starting HEAD: `3637fecc03e801b46188cd69d83bb87381590aca`;
- implementation commits: `369955a`, `c2fa255`, and `3637fec`;
- public tests: `183/183 PASS`;
- Authority Lab fixtures: `112/112 PASS`;
- schema: `authority-lab-v1`;
- frozen architecture: six tuple coordinates, six invariants, and three outcomes.

The reviewed implementation correctly rejects candidate-visible commitment forks, stale replay, missing checkpoints, verifier-state mismatch, and conflicting witnesses. This document attacks the next boundary: whether the separately supplied verifier-state snapshot is itself current, unique, and recoverable.

No executable Authority Lab code or fixture is changed by this research slice.

## 2. Durable-state trust boundary

The current implementation admits durable state through `cases/authority_lab/trusted_commitment_state.json`. `runner.load_fixture`:

1. rejects `_trusted_commitment_context` if it appears in candidate fixture JSON;
2. loads the separate manifest by caller-selected fixture filename; and
3. attaches the corresponding list as `_trusted_commitment_context` before constructing `OracleInput`.

Each manifest entry contains:

```text
exact_state_key_digest
stream_id
stream_generation
previous_verifier_state_digest
current_verifier_state_digest
head_logical_position
head_commitment_digest
checkpoint_id
freshness_challenge_id
```

The state key binds the observation binding, root generation and lineage, boundary epoch, observer generation, and stream generation. The oracle then compares the candidate checkpoint with this context.

The manifest is not self-authenticating and is not externally anchored. It has no manifest signature, global epoch, highest-ever generation, monotonic counter, replica identity, recovery provenance, anchor receipt, or authenticated predecessor store. It is a deterministic harness-owned input, not an implemented `compare_and_swap` store. The implementation has no state outside the manifest against which manifest rollback can be detected.

Therefore:

> Candidate control of durable state is blocked, but currency of the admitted durable-state root is assumed.

That is a meaningful boundary. It is also the exact boundary falsified here.

## 3. Current implementation semantics

### 3.1 Commitment history integrity

The canonical envelope digest binds fixed envelope fields and exact referenced observation segments. Exact verifier, predecessor-link, checkpoint, root, boundary, objective, freshness, and stream relations are required. Co-present same-position digest conflict yields `UNAVAILABLE / OBSERVATION_COMMITMENT_EQUIVOCATION`.

### 3.2 Verifier durable-state integrity

`verifier_state_digest` binds the previous state digest, current verifier-state identity and generation, head position and commitment, challenge, checkpoint identity, and checkpoint generation. This detects candidate-visible partial alteration.

### 3.3 Verifier durable-state freshness

Freshness is established only relative to the manifest entry supplied to the invocation. There is no independently retained higher generation, later head, or external anchor. A rolled-back manifest is internally current by definition.

### 3.4 Recovery provenance

No recovery relation exists. Missing context yields `UNAVAILABLE / OBSERVATION_VERIFIER_STATE_UNAVAILABLE`, but the oracle cannot distinguish an independently recovered context from a context reconstructed from candidate history if both mappings are identical.

### 3.5 Witness semantics

`CommitmentWitness` contains a witness ID/generation, checkpoint/head, root/boundary lineage, event order, and disposition. The oracle rejects a co-present witness that conflicts with the selected checkpoint.

The current record has no witness identity basis, admission relation, independence-domain identity, predecessor witness state, recovery interval, or witness-source handoff. Witnesses are optional. Multiple matching witnesses do not create authority, but neither their operational independence nor their process continuity can be established.

### 3.6 Restart and recovery

Observer/stream restart without matching durable state fails closed. Verifier-store restart and recovery are not separately modeled. Restoring the entire fixture-plus-manifest world restores the oracle's complete memory.

## 4. Required distinctions

The following are separate facts:

| Dimension | Meaning | Current representation |
|---|---|---|
| Commitment history integrity | Candidate history has exact canonical linkage | Envelopes, segments, links, digests |
| Durable-state integrity | Supplied checkpoint state is internally exact | State/checkpoint digests |
| Durable-state freshness | Supplied state is the latest state ever admitted | Not independently established |
| Recovery provenance | Rebuilt state came from an admitted recovery authority | Not represented |
| Anchor authenticity | The recovery anchor came from its admitted source | No anchor relation |
| Anchor freshness | No later anchor exists | No monotonic anchor |
| Witness identity | Exact witness authority and process lineage | Label/generation only; no admission model |
| Witness independence | Witnesses do not share controlling provenance | Not represented |
| Replica consistency | Replicas share one non-forked durable head | Not represented across invocations |
| Current authority | Exact T3 authority remains established | Derived after the preceding inputs are admitted |

An internally consistent commitment does not establish durable-state currency. An internally consistent durable-state snapshot does not establish that no later or competing snapshot exists.

## 5. A–Z hostile matrix

`AUTHORIZED*` below means authorization is reproducible when the assumed rolled-back, forked, or reconstructed harness context is supplied. That context is not candidate fixture data, but the oracle has no higher anchor with which to reject it.

| ID | Scenario / reproducer | Current outcome | Desired outcome | Reason class | Invariants | Classification | Fits v1? |
|---|---|---|---|---|---|---|---|
| A | Accept position 1, restore the same stream's position-0 candidate and context | `AUTHORIZED*` | `UNAVAILABLE` | durable-state currency unavailable | `CONT`, `DISC`, `EVD`, `USE` | executable defect at integrated boundary | Yes |
| B | Restore verifier runtime and manifest snapshot together | `AUTHORIZED*` | `UNAVAILABLE` | verifier epoch/anchor unavailable | `CONT`, `DISC`, `EVD`, `USE` | executable manifestation of A; external storage cause | Yes |
| C | Acceptance succeeds but stored state remains at the prior head | Prior head is again `AUTHORIZED*` | `UNAVAILABLE` | completed persistence unavailable | `CONT`, `EVD`, `USE` | executable manifestation of A | Yes |
| D | Head/digest/generation fields tear visibly | `UNAVAILABLE` (`ROLLBACK`, `REPLAY`, or uniqueness failure) | `UNAVAILABLE` | internal state mismatch | `CONT`, `EVD`, `USE` | already blocked when tear is visible | Yes |
| E | Remove state, then rebuild a matching context from candidate records | Missing state: `UNAVAILABLE`; rebuilt context: `AUTHORIZED*` | Rebuilt-from-candidate: `UNAVAILABLE` | recovery provenance unavailable | `CONT`, `DISC`, `EVD`, `USE`, `CLO` | executable recovery defect if reconstruction is admitted | Yes |
| F | Recover from an independently authenticated current anchor | No executable anchor/recovery relation | `AUTHORIZED` after exact proof | recovery anchor established | All six | implementation obligation / positive design path | Yes |
| G | Two stores retain different position-1 heads for the same state key/prior digest | Both separately `AUTHORIZED*` | `UNAVAILABLE` until reconciled | replica state conflicting | `CONT`, `BND`, `EVD`, `USE` | executable defect | Yes |
| H | Two verifier replicas advance one common predecessor to different heads | Both separately `AUTHORIZED*` | `UNAVAILABLE` | verifier split brain | `CONT`, `DISC`, `BND`, `EVD`, `USE` | executable defect | Yes |
| I | Roll back, then replay the exact complete chain | Head may `AUTHORIZED*`; completeness is not established | `AUTHORIZED` only with independent completeness proof | recovery completeness unavailable | `CONT`, `EVD`, `USE` | semantic/implementation obligation | Yes |
| J | Replay omits one accepted historical commitment | Final self-consistent head may `AUTHORIZED*` | `UNAVAILABLE` | recovery completeness unavailable | `CONT`, `EVD`, `USE`, `CLO` | executable input collapse; defect | Yes |
| K | Replay commitments in a different order but present a self-consistent final head | Final head may `AUTHORIZED*` | `UNAVAILABLE` | recovery ordering unavailable | `CONT`, `EVD`, `USE` | executable input collapse; defect | Yes |
| L | Reuse verifier-state generation/key after replacement with matching snapshot | `AUTHORIZED*` if all admitted labels roll back together | `UNAVAILABLE` | verifier lineage unavailable | `CONT`, `DISC`, `BND`, `EVD` | executable manifestation of A | Yes |
| M | Explicitly authorized verifier-state key rotation | No exact rotation relation is executable; `LAB-V1-102` is a control, not an actual rotation | `AUTHORIZED` with exact transition | key-rotation continuity established | `CONT`, `DISC`, `BND`, `EVD` | implementation obligation / positive path | Yes |
| N | Same witness label/key, replaced witness process/source | Matching witness does not affect `AUTHORIZED`; process change is invisible | `UNAVAILABLE` absent continuity | witness identity continuity unavailable | `DISC`, `BND`, `EVD` | observation/input-root limitation plus implementation gap | Yes |
| O | No witness covers the recovery interval | Witnesses are optional; candidate may `AUTHORIZED*` | `UNAVAILABLE` when recovery policy requires witness coverage | witness coverage unavailable | `CONT`, `BND`, `EVD`, `USE` | implementation obligation | Yes |
| P | Two witnesses or witness views support different heads | Co-present mismatch: `UNAVAILABLE`; separated views may each `AUTHORIZED*` | `UNAVAILABLE` | witness fork / checkpoint conflict | `CONT`, `BND`, `EVD`, `USE` | partially blocked; cross-view executable defect | Yes |
| Q | Multiple witness IDs share one source and confirm one head | `AUTHORIZED` | No added authority; `UNAVAILABLE` if independent recovery witnesses are required | independence unavailable | `BND`, `EVD`, `CLO` | executable representational gap | Yes |
| R | Replay a once-valid external anchor after a later head | No anchor exists; rolled manifest `AUTHORIZED*` | `UNAVAILABLE` | anchor freshness unavailable | `CONT`, `EVD`, `USE` | contract-compatible implementation gap | Yes |
| S | Anchor service itself reports an older state | No independent higher anchor; old world `AUTHORIZED*` | `UNAVAILABLE` | anchor rollback unavailable | `CONT`, `DISC`, `EVD`, `USE` | ultimate external trust boundary unless cross-anchored | Yes, within a stated root |
| T | Rollback crosses a recorded shutdown/successor transition | Fresh successor authorizes; restored predecessor world also `AUTHORIZED*` when terminal history is rolled back | `UNAVAILABLE` | terminal history/recovery unavailable | All six | executable composition defect | Yes |
| U | Valid correction at position 1, then restore pre-correction position 0 | Correction and old head each separately `AUTHORIZED*` | Old head: `UNAVAILABLE` | correction currency unavailable | `CONT`, `EVD`, `USE`, `CLO` | executable defect | Yes |
| V | Restore state predating a legitimate stream-generation change | Old generation with matching old context may `AUTHORIZED*` | `UNAVAILABLE` | stream-generation currency unavailable | `CONT`, `DISC`, `BND`, `EVD`, `USE` | executable manifestation of A | Yes |
| W | Empty store receives a non-genesis commitment | No context: `UNAVAILABLE`; candidate-derived context can make it `AUTHORIZED*` | `UNAVAILABLE` | recovery/genesis admission unavailable | `CONT`, `DISC`, `EVD`, `USE` | blocked inside intact runner boundary; unsafe reconstruction gap | Yes |
| X | Fresh stream with admitted genesis and current harness state | `AUTHORIZED` (`LAB-V1-032`) | `AUTHORIZED` | current genesis established | All six | positive control | Yes |
| Y | Compare verifier state with a local monotonic external anchor | Not represented | `AUTHORIZED` only on exact equality/advance | anchor relation established | `CONT`, `DISC`, `BND`, `EVD`, `USE` | viable design direction | Yes |
| Z | Trusted checkpoint recovery, exact complete continuation, witness/source continuity, then current head | Not executable end-to-end | `AUTHORIZED` | recovery chain established | All six | positive design obligation | Yes |

## 6. Executable reproducers

### 6.1 Rollback to a formerly valid head

`LAB-V1-032` and `LAB-V1-112` use the same exact state-key digest and stream generation. `032` is position 0; `112` is an `EXTENDS` head at position 1.

Observed sequence:

```text
position 0 + position-0 trusted context
  -> AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED

position 1 + position-1 trusted context
  -> AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED

restore position 0 + restore position-0 trusted context
  -> AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED
```

The third result is the counterexample. A later accepted head existed in the modeled history, but the oracle receives no fact outside the restored state with which to establish that history.

### 6.2 Split-brain heads

Starting from the valid position-1 input, the reproducer created a second canonical envelope with a different issuer key and therefore a different commitment digest. It exactly updated its verifier result, link, checkpoint, freshness relation, and forked trusted context.

Both branches had:

- the same exact state-key digest;
- the same previous verifier-state digest;
- logical position 1; and
- different head commitment digests.

Evaluated separately:

```text
branch A -> AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED
branch B -> AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED
```

Presented together, current equivocation checks would fail closed. The defect is cross-replica and cross-invocation currency: neither isolated replica knows the other successful head exists.

### 6.3 Lost state and candidate-derived reconstruction

For the positive position-1 input:

```text
trusted context absent
  -> UNAVAILABLE / OBSERVATION_VERIFIER_STATE_UNAVAILABLE

context reconstructed to match candidate records
  -> AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED
```

The runner prevents a fixture file from embedding this context. That is correct. No implemented recovery boundary, however, proves that a replacement context came from an independent current anchor rather than the supplied history.

### 6.4 Shared witness source

Two matching witness records with different witness IDs but the same source/root were added to a valid input. The result remained:

```text
AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED
```

This does not mean witness multiplicity currently grants authority; it does not. It proves that witness independence and witness-source continuity are not representable or enforceable today and therefore cannot safely establish rollback recovery.

## 7. Reproducible counterexample

The exact counterexample class is:

> A verifier-state snapshot and candidate commitment view are each internally exact and mutually consistent, but a later or competing accepted snapshot exists outside the supplied invocation. Because the oracle retains no independently anchored monotonic fact, the stale or forked view returns `AUTHORIZED`.

This is one semantic defect with several manifestations:

- rollback after position advancement;
- VM/container snapshot restoration;
- persistence loss;
- split-brain stores/replicas;
- correction or successor history disappearance;
- incomplete/reordered recovery replay; and
- old stream-generation restoration.

It is not a failure of the existing local digest checks. Those checks correctly reject visible mismatch. It is a failure to establish durable-state currency across the admitted recovery boundary.

## 8. Replica and fork analysis

The current logical key prevents a single invocation from accepting two different digests at one position. The separate manifest also prevents a candidate branch from replacing an intact current head.

Neither mechanism coordinates replicas. If replicas fork the trusted state itself, each branch has a matching checkpoint and context. Arrival order, digest order, witness count, or majority must not choose a winner. Recovery requires an independently authoritative anchor or a replication protocol whose authority, membership, epochs, and commit evidence are themselves admitted.

Byzantine agreement concepts clarify why two internally valid replicas do not establish one current state. Ground Truth does not need to implement a general Byzantine state-machine replication protocol merely to close this lab defect. It must, however, refuse authority when the required unique durable head or recovery provenance cannot be established.

## 9. Rollback and recovery analysis

### 9.1 Exact replay is not enough

Replaying the complete chain in order can reconstruct bytes, but it does not prove completeness. The verifier needs an independently current terminal anchor or equivalent evidence establishing the expected final position/digest. Otherwise a valid prefix is indistinguishable from the full history.

### 9.2 Candidate history cannot bootstrap recovery

Candidate commitments can prove local hash/link consistency. They cannot establish which accepted history is latest. Reconstruction from candidate data alone is circular:

```text
candidate history selects recovery head
-> recovered state declares candidate history current
-> recovered currentness authorizes candidate
```

This cycle must yield `UNAVAILABLE`.

### 9.3 Positive recovery

A defensible positive recovery needs, at minimum:

1. an independently admitted recovery authority and exact verifier/store identity;
2. a current authenticated anchor for the exact state key and boundary epoch;
3. anchor generation/currentness that is not derived from the recovering candidate;
4. exact ordered continuation from the anchor;
5. proof that the replay reaches the anchor's required terminal head or a later authorized head;
6. no unresolved replica, witness, correction, shutdown, or generation conflict;
7. atomic installation of the recovered state; and
8. a fresh T3 checkpoint/challenge after recovery.

Only then may the ordinary observation/objective/grant/use requirements permit `AUTHORIZED`.

## 10. Witness-source continuity analysis

Witness statements are evidence, not authority. Witness count does not establish independence.

For rollback recovery, a usable witness relation would need exact root-issued admission for:

- witness identity basis and generation;
- witness source/control/independence domain;
- scope: exact state key, stream generation, checkpoint family, and boundary;
- covered interval and predecessor witness head;
- lifecycle, ordering, freshness, revocation, and handoff;
- the exact anchor/checkpoint attested; and
- conflict behavior across views.

A witness process replacement under the same label or key is not continuity. A handoff must preserve only the exact admitted witness evidence relationship; it cannot transfer verifier, observer, execution, or root authority.

Current witness semantics are sufficient to reject a visible mismatch with one checkpoint. They are not sufficient to prove witness independence, witness currency, recovery-interval coverage, or cross-view consistency.

## 11. Anchor analysis

An anchor is useful only if both authenticity and freshness are established.

- A signed old anchor remains authentic but stale.
- A monotonic number supplied by the recovering verifier is self-attestation.
- A hardware-backed counter can strengthen rollback resistance, but its device identity, reset/replacement lifecycle, scope, and binding to the exact verifier state remain authority-relevant.
- A transparency checkpoint can establish append-only relation to another checkpoint, but split-view detection still depends on comparison, witness, or gossip boundaries.
- Cross-anchoring moves the trust root; it does not eliminate it.

The smallest repair direction is not `durable_state_valid=true`. It is a typed relational composition binding an independently admitted anchor source, anchor identity/generation, exact state key, head digest/position, predecessor anchor, lifecycle/order/freshness, recovery event, and verifier installation receipt.

## 12. Positive controls

Current executable controls:

| Control | Result | Qualification |
|---|---|---|
| Fresh admitted genesis (`LAB-V1-032`) | `AUTHORIZED` | Positive within supplied manifest boundary |
| Append-only progression (`098`, `112`) | `AUTHORIZED` | Does not prove manifest currency outside invocation |
| Explicit correction (`099`) | `AUTHORIZED` | Correction can disappear if state and input both roll back |
| Fresh successor (`111`) | `AUTHORIZED` | Old predecessor world can reappear if terminal history also rolls back |
| Visible lost verifier state (`103`) | `UNAVAILABLE` | Correct fail-closed behavior |
| Visible verifier rollback (`104`) | `UNAVAILABLE` | Correct when manifest and candidate disagree |
| Co-present witness conflict (`106`) | `UNAVAILABLE` | Correct local conflict behavior |

Not yet executable as true positive controls:

- authorized verifier key rotation (`102` is labeled as a control but performs genesis with the unchanged key);
- recovery from an independently authenticated current anchor;
- independently proven complete forward replay; and
- correction/supersession continuity across recovery.

Those are requirements for the next design slice, not claims of current implementation coverage.

## 13. Invariant mapping

- `INV-CONT`: accepted head, recovery anchor, replay interval, and T3 state must form one exact current lineage.
- `INV-DISC`: snapshot restore, replica replacement, verifier generation reuse, key reuse, and witness replacement do not prove continuity.
- `INV-BND`: anchor, recovery authority, replicas, witnesses, state key, and stream generation must remain in the exact applicable boundary/epoch.
- `INV-EVD`: digests, signatures, checkpoints, counters, logs, witnesses, and replayed records remain evidence; none may self-establish current authority.
- `INV-USE`: a previously accepted state cannot regain current authority through rollback, replay, prefix recovery, or reused generation.
- `INV-CLO`: snapshots, reconstructed manifests, replicated stores, summaries, witness aggregates, and recovery wrappers cannot inherit authority implicitly.

All six already speak directly to the defect. No seventh invariant is needed.

## 14. Contract sufficiency

The public contract already requires current authority-relevant state, continuity, evidence relationship, freshness, and replay/rollback resistance to be established. A rolled-back verifier state does not satisfy those requirements merely because its internal hashes are valid.

The repair appears representable as typed subrelations under existing `evidence_binding`, `freshness`, lifecycle, ordering, source-authority, boundary, identity, closure, and commitment semantics. A protected anchor/store interface remains an external implementation boundary, but its admitted evidence can be modeled without changing:

- `authority-lab-v1`;
- the six tuple coordinates;
- the six invariants; or
- the three outcomes.

A new public primitive is not presently justified. New internal typed records may be required to make recovery/anchor facts exact; that is not a public architecture expansion.

## 15. Possible design directions

The next design slice should specify:

1. an immutable `VerifierStateAnchor` relation with source authority, exact state key, anchor generation, head position/digest, predecessor anchor, lifecycle, ordering, boundary, and freshness;
2. a `VerifierStateRecovery` relation binding the selected anchor, replay range, exact ordered commitment/link set, completeness evidence, recovered head, and fresh installation receipt;
3. replica identity/membership and a fail-closed rule for incomparable current heads;
4. verifier key/generation rotation and replacement continuity;
5. witness admission, source/control identity, independence domain, interval coverage, and handoff;
6. explicit full-prefix versus complete-history semantics;
7. atomic durable installation with crash/torn-write behavior; and
8. positive genesis, rotation, recovery, correction, successor, and disaster-recovery paths.

Preferred outcomes:

- missing, stale, ambiguous, incomparable, rolled-back, forked, or incompletely recovered state: `UNAVAILABLE`;
- an exact current authoritative revocation/prohibition/compromise that applies: `DENIED`;
- exact independently anchored recovery plus every ordinary authority requirement: `AUTHORIZED`.

## 16. Prior-art notes

These are conceptual comparisons, not implementation or equivalence claims.

- [TPM technology](https://trustedcomputinggroup.org/resource/trusted-platform-module-tpm-summary/) illustrates protected key/measurement storage. Monotonic or secure-counter designs can make rollback more detectable, but device replacement, reset, ownership, and scope still need explicit authority semantics.
- [RFC 9162, Certificate Transparency Version 2.0](https://www.rfc-editor.org/rfc/rfc9162.html) distinguishes signed log heads and append-only consistency proofs. Ground Truth does not implement CT, a Merkle tree, or public gossip.
- [CT Gossip](https://datatracker.ietf.org/doc/draft-ietf-trans-gossip/) studies detection of split views through cross-view exchange. Ground Truth's witness/source continuity must be defined under its own authority model.
- [RFC 9334, RATS Architecture](https://www.rfc-editor.org/rfc/rfc9334.html) separates verifier appraisal from relying-party decisions and treats freshness as policy-bound. Ground Truth does not claim remote-attestation equivalence.
- Lamport, Shostak, and Pease, [The Byzantine Generals Problem](https://www.microsoft.com/en-us/research/publication/byzantine-generals-problem/), clarifies that agreement under faulty participants is not implied by individually valid replica state. Ground Truth need not adopt general Byzantine consensus to recognize incomparable heads as unavailable.
- [CoSi](https://www.usenix.org/system/files/conference/usenixsecurity16/sec16_paper_kokoris-kogias.pdf) explores witness cosigning of authoritative statements. Ground Truth does not infer independence or authority from signature count.
- [SQLite write-ahead logging](https://sqlite.org/wal.html) illustrates crash recovery and atomic persistence mechanics. Journaling can address torn writes; it does not by itself provide adversarial rollback resistance or authority.

## 17. Residual trust boundary

Even a repaired deterministic lab cannot establish physical truth by computation alone. Residual preconditions include:

- truthful and current root/orderer/anchor inputs;
- correct isolation and key custody for verifier, anchor, and witness sources;
- protected monotonic persistence or independently comparable anchors;
- truthful replica membership and failure detection;
- event delivery and observation completeness before commitment construction;
- no branch hidden from every admitted anchor/witness/comparison path; and
- correct hardware, storage, clock, and signature-verifier behavior where relied upon.

Hidden rollback of every admitted anchor and all independent comparison sources remains an ultimate external trust failure. The contract must state this boundary rather than pretend a local hash can detect it.

## 18. Exact hostile-research verdict

**FAIL — REPRODUCIBLE IN-SCOPE DURABLE VERIFIER-STATE ROLLBACK/RECOVERY COUNTEREXAMPLE FOUND**

The current implementation passes within the admitted-current-manifest boundary. It fails at the durable-state-integrated boundary because rollback or fork of that admitted manifest collapses distinct histories into separately valid oracle inputs.

The smallest next slice is design-only: specify a verifier-state anchor, recovery provenance/completeness, replica conflict, and witness-source continuity contract using the existing 6/6/3 architecture. Executable repair should follow only after that design survives hostile review.

This failure is bounded. It does not prove that all durable stores, anchors, or witness systems are insecure. Conversely, a later PASS would mean failure to falsify within the modeled boundary, not proof of security.
