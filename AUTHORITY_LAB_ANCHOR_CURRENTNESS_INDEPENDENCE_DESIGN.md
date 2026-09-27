# Authority Lab v1 Adapter Currentness, Source-Domain Independence, and Cross-Domain Checkpoint Reconciliation Design

## 1. Exact baseline

This design starts from reviewed frontier commit `e557887bed84e40f738e658afd11e15a8981575c` on `docs/frontier-delta-anchor-currentness-independence`, parent `74fa6ff9e121dfc9176d34fcfd2bce1cfd709fc2`, with subject `docs: record anchor currentness independence frontier`.

The executable baseline remains unchanged:

- schema `authority-lab-v1`;
- tuple `(subject, artifact, control_state, identity_basis, boundary_epoch, decision)` — exactly six coordinates;
- invariants `INV-CONT`, `INV-DISC`, `INV-BND`, `INV-EVD`, `INV-USE`, and `INV-CLO` — exactly six invariants;
- outcomes `AUTHORIZED`, `DENIED`, and `UNAVAILABLE` — exactly three outcomes;
- `195/195` public tests passing; and
- `146/146` Authority Lab fixtures passing.

This artifact is design-only. It changes no executable file, fixture, manifest, schema, tuple coordinate, invariant, or outcome.

## 2. Executable counterexamples

The reviewed frontier established three independent executable defects.

1. In a loaded `LAB-V1-032` case, replacing `adapter_source_id`, `adapter_source_generation`, `adapter_observation_id`, and `adapter_observation_generation` in harness-owned `_trusted_anchor_context` still returns `AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED`. Setting `adapter_event_order` to stale order `0` also authorizes.
2. `LAB-V1-133` correctly fails when two witnesses visibly share one control domain. Relabeling the second candidate-visible witness with distinct `witness_source_id`, `source_lineage`, and `control_domain` strings changes the result to `AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED` without independent appraisal of those distinctions.
3. Starting from `LAB-V1-134`, narrowing a witness interval to `3..3`, replacing its semantic scope with `UNRELATED`, or collapsing witness identity bases still returns `AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED`.

Existing controls remain meaningful: a duplicate matching trusted context fails closed; visible same-domain witnesses fail closed; a co-present anchor fork fails closed; a retained later anchor rejects stale replay; explicit current anchor revocation is `DENIED`; and authorized anchor rotation, genesis, and successor paths remain reachable.

## 3. Defect statement

The oracle joins the candidate anchor to selected harness state but does not establish the identity, continuity, scope, or currentness of the adapter that supplied that state. It also counts distinct candidate-visible witness labels as distinct source domains without an independently admitted mapping, and does not enforce witness scope, interval, identity, freshness, or handoff facts.

The common defect is authority from descriptive multiplicity:

> Candidate-visible or locally supplied names can describe different adapters, lineages, or domains without authoritative evidence that the underlying sources are different, current, applicable, and independently controlled.

This is one relational admission defect, not a reason to add a tuple coordinate or invariant.

## 4. Normative requirement

Multiplicity is not independence. A currentness statement may support `AUTHORIZED` only when the applicable root has selected the required source domains and every selected domain has an exact, current, lifecycle-valid adapter and checkpoint relation. Domain membership and independence must be established by an admitted appraisal relation whose issuer is neither the candidate nor any member whose independence it classifies.

The positive rule is:

```text
AUTHORIZED requires
  exact required-domain policy
+ exact current adapter admission for every selected domain
+ authoritative source-domain membership/appraisal
+ complete witness scope and interval where witnesses are required
+ one current checkpoint per required domain
+ agreement or explicit current reconciliation
+ all existing Authority Lab requirements.
```

Silence, label inequality, signature count, key inequality, endpoint diversity, or majority agreement does not establish any term in that conjunction.

## 5. Adapter admission

Add a strict internal typed `ANCHOR_ADAPTER_ADMISSION` relation under existing `evidence_binding`. It binds:

- `adapter_id`, `adapter_generation`, and `adapter_identity_basis`;
- `adapter_observation_id` and `adapter_observation_generation`;
- `anchor_source_id`, `anchor_source_generation`, and `source_lineage`;
- `control_domain_id` and `independence_domain_id`;
- exact `anchor_key_id`/generation and `stream_id`/generation;
- covered checkpoint family and semantic scope `VERIFIER_STATE_CURRENTNESS`;
- applicable boundary and boundary epoch;
- root/source authority, ordering source, lifecycle, and event order;
- verifier-bound freshness challenge;
- predecessor adapter admission/observation; and
- supersession/rotation identifier when generation changes.

The relation must be root-issued or issued by an exact root-admitted classification authority whose delegation scope explicitly includes adapter admission for the same boundary and source family. The adapter, candidate subject, observer, verifier, anchor producer, witness, recovery installer, wrapper, or transformed record cannot admit itself.

The harness manifest remains the protected carrier of the selected context. Its adapter members must join exactly to one active admission. Extra, missing, duplicate, conflicting, or unjoined adapter context fails before `AUTHORIZED` with `ANCHOR_ADAPTER_ADMISSION_UNAVAILABLE` or `ANCHOR_ADAPTER_CONFLICTING`.

## 6. Adapter currentness

Add a typed `ANCHOR_ADAPTER_CURRENTNESS` relation, also under existing evidence/freshness semantics. It binds the exact adapter admission and observation to:

- selected anchor digest and position;
- selected commitment head/checkpoint;
- exact state key and source domain;
- freshness challenge issued by the admitted verifier/orderer rather than the adapter;
- observation event order within the T1–T3 interval;
- predecessor adapter observation or genesis;
- lifecycle head; and
- independently retained domain checkpoint context.

An adapter timestamp, sequence, signature, reused key, stable name, stable endpoint, or same process label is evidence only. It cannot make the relation current. Currentness requires exact verifier-bound challenge response plus authoritative ordering no later than T3 and no later active/superseding adapter observation omitted from the admitted domain context.

The oracle must consume every adapter field carried by trusted context. An unknown or semantically unused successfully parsed adapter member is not permitted to influence authorization. Stale order, generation reuse, unadmitted replacement, scope mismatch, or role cycle returns `UNAVAILABLE / ANCHOR_ADAPTER_CURRENTNESS_UNAVAILABLE`. Explicit current prohibition or revocation returns `DENIED / ANCHOR_ADAPTER_PROHIBITED`.

## 7. Adapter rotation

Add a typed `ANCHOR_ADAPTER_ROTATION` relation with exact old-to-new continuity:

- old and new adapter identity, generation, identity basis, and source domain;
- old last observation and new first observation;
- anchor/source lineage and stream family;
- handoff interval with overlap or an exact boundary and no gap;
- current root/classification authority and ordering;
- new freshness challenge;
- old admission supersession and new admission activation; and
- cross-confirmation/installation receipt where the protected adapter context changes.

An authorized rotation preserves observation/currentness coverage only. It does not transfer execution, verifier, anchor-source, witness, or recovery authority. A changed adapter without exactly one current rotation is `UNAVAILABLE / ANCHOR_ADAPTER_ROTATION_UNAVAILABLE`. A current authoritative prohibition of the new adapter is `DENIED`. The old adapter cannot remain concurrently current unless an explicit policy admits a bounded overlap and both observations reconcile to one head.

## 8. Source-domain membership

Add a root-selected typed `SOURCE_DOMAIN_MEMBERSHIP` relation. Each record binds:

- exact member kind (`ANCHOR_SOURCE`, `ADAPTER`, or `WITNESS_SOURCE`);
- member identity/generation/identity basis and source lineage;
- `control_domain_id`, `independence_domain_id`, and membership epoch;
- upstream dependency identifier and rollback-domain identifier;
- applicable anchor/stream/checkpoint family, boundary, and interval;
- classification authority identity and generation;
- root/source authority, lifecycle, ordering, and freshness; and
- predecessor membership or authorized transition.

The classification authority cannot be the classified member, candidate subject, evaluated verifier, or a source whose independence it is used to prove. If delegated classification is supported, the delegation must be exact, current, boundary-scoped, non-circular, and unable to widen domain membership beyond root policy. V1 may choose the smaller root-only implementation if delegated classification cannot be proven non-circular.

Domain IDs are references into admitted membership, never evidence by themselves. Distinct labels with the same admitted rollback domain count once. Different keys or identities with one upstream/control domain count once. One source represented through multiple adapters counts once. Missing, stale, conflicting, self-issued, or candidate-only membership is `UNAVAILABLE / SOURCE_DOMAIN_MEMBERSHIP_UNAVAILABLE`.

## 9. Witness independence

A witness counts toward a required independence policy only when its `WITNESS_SOURCE_ADMISSION` joins exactly to one current `SOURCE_DOMAIN_MEMBERSHIP` and, where the witness uses an adapter, one current adapter admission/currentness chain.

The join must establish:

- exact witness identity, generation, and identity basis;
- exact witness-source identity/generation and source lineage;
- control, independence, upstream-dependency, and rollback domains;
- selected anchor digest and commitment head;
- boundary, membership epoch, and required-domain policy;
- semantic scope and interval coverage;
- freshness and lifecycle;
- predecessor/handoff continuity; and
- root or exact admitted source authority.

Two signatures, keys, witness IDs, or domain strings count as one effective source whenever authoritative membership maps them to one independence domain or shared upstream dependency. A witness cannot classify itself as independent. Independence is not transitive through relays, summaries, wrappers, shared state, or common recovery authority.

## 10. Witness coverage and currentness

Every required witness must cover the exact semantic families and interval selected by policy. At minimum, coverage must include the selected anchor/checkpoint, adapter-currentness family, verifier state, boundary/epoch, and any terminal/successor or recovery events relevant to T1–T3.

The oracle must validate:

- `covered_scope_families` contains every policy-required family;
- `start_event_order <= T1` and `end_event_order >= T3` for continuous coverage, or exact gap-free handoffs compose that interval;
- the witness selects the exact anchor digest and commitment head;
- freshness is verifier/orderer-bound and current at T3;
- lifecycle is active and not superseded;
- identity/source lineage matches admitted membership; and
- overlapping witnesses do not report incompatible heads or histories.

Missing scope, shortened interval, stale freshness, handoff gap, unresolved overlap conflict, transformed loss, or stable-label source replacement yields `UNAVAILABLE`. Explicit current witness prohibition/revocation yields `DENIED`.

## 11. Required-domain selection

Add a typed `REQUIRED_SOURCE_DOMAIN_POLICY` relation selected by the applicable root. It binds:

- policy ID/generation and membership epoch;
- exact state key, stream/generation, boundary/epoch, and T1–T3 interval;
- required domain IDs and required roles per domain;
- selection rule (`ALL_LISTED` or an exact named subset fixed by root policy);
- witness/adapter semantic-family requirements;
- behavior for unavailable domains;
- reconciliation authority and policy version;
- source authority, lifecycle, ordering, and freshness.

The candidate, verifier, adapter, witness, fixture ordering, or oracle arrival order cannot select participating domains. The v1 implementation should avoid generic numeric quorum selection. If a deployment needs a subset, the root policy must name the eligible membership epoch and exact accepted combinations before candidate evaluation; distinct domain membership is still mandatory.

Policy may explicitly require only domain A, in which case unavailable optional domain B does not block A. If both A and B are required, omission or unavailability of either is `UNAVAILABLE`. Candidate-provided extra favorable domains cannot replace a missing required domain.

## 12. Cross-domain checkpoint reconciliation

For every required domain, evaluation derives exactly one `DOMAIN_CHECKPOINT_VIEW` by joining its membership, adapter currentness, and selected anchor. Then:

1. **Agreement:** all required current views select the same exact state key, stream generation, anchor/head position, commitment digest, and applicable boundary. Continue evaluation.
2. **Different positions on one proven append-only lineage:** the later position may be selected only if every required domain either currently observes it or has an authorized, gap-free handoff/supersession explaining its older view. Otherwise `UNAVAILABLE`.
3. **Incompatible heads, same position, branches, or ambiguous ordering:** `UNAVAILABLE / CROSS_DOMAIN_CHECKPOINT_CONFLICTING`.
4. **One stale and one current required domain:** `UNAVAILABLE` until the stale domain advances or an authorized reconciliation/supersession relation removes it from the current required set.
5. **One unavailable required domain:** `UNAVAILABLE`. An optional domain is ignored only because the pre-existing root policy says it is optional, never because the candidate omits it.
6. **Explicit reconciliation:** one current typed `CROSS_DOMAIN_CHECKPOINT_RECONCILIATION` must name every required domain, every competing digest/position, the selected history, consistency/correction evidence, resolution authority, membership epoch, freshness challenge, and superseded views. It must be root-issued or issued by the policy's exact non-member reconciliation authority. Unknown branches cannot be silently discarded.

Authorized reconciliation permits later `AUTHORIZED`; unresolved disagreement never does. Arrival order, first writer, majority, largest position alone, or candidate preference cannot select a branch.

## 13. Anti-shopping rules

The implementation must enforce these selection rules before evaluating whether evidence is favorable:

- derive required domains exclusively from one exact current root policy;
- enumerate all current admissions for each required domain;
- reject duplicate/conflicting memberships and adapter observations;
- require exactly one reconciled view per required domain;
- reject candidate omission of required evidence;
- reject extra candidate records that conflict with required-domain state;
- count authoritative independence domains, not records/signatures/keys;
- prohibit the candidate, verifier, adapter, or witness from choosing the policy, membership epoch, or reconciliation; and
- make evaluation invariant under candidate array order.

No “best available,” “first valid,” “highest count,” or “majority wins” fallback may produce `AUTHORIZED`.

## 14. DENIED versus UNAVAILABLE

Use `UNAVAILABLE` when required positive establishment is missing or ambiguous, including:

- adapter admission/currentness/rotation unavailable;
- source-domain membership or independence unestablished;
- witness identity, scope, interval, freshness, lifecycle, or handoff unavailable;
- required-domain policy absent, stale, conflicting, or candidate-selected;
- a required domain missing, stale, unavailable, or conflicting;
- checkpoint reconciliation absent or incomplete;
- domain shopping or favorable subset selection cannot be excluded; or
- the surviving comparison source is not independently current.

Use `DENIED` only when a current authoritative relation explicitly revokes, rejects, invalidates, or prohibits the applicable adapter, source, witness, anchor lineage, reconciliation, or execution authority. Do not convert uncertainty, correlation, or missing proof into denial.

## 15. Hostile matrix A–AM

`Current` describes the reviewed executable baseline. “External” means the real distinction is absent from deterministic input, not that the oracle may assume it.

| ID | Case | Current behavior | Designed outcome / reason | Required authoritative facts | Invariants | Fits v1 | External? |
|---|---|---|---|---|---|---|---|
| A | Adapter relabeled, same source | Can authorize | `UNAVAILABLE / ANCHOR_ADAPTER_ADMISSION_UNAVAILABLE` | Exact adapter admission + membership join | DISC EVD CLO | Yes | Hidden source truth only |
| B | Adapter stale, candidate marks current | Can authorize | `UNAVAILABLE / ANCHOR_ADAPTER_CURRENTNESS_UNAVAILABLE` | Verifier-bound freshness + ordering | CONT EVD USE | Yes | No |
| C | Adapter replaced behind same key/name | Can authorize | `UNAVAILABLE / ANCHOR_ADAPTER_ROTATION_UNAVAILABLE` | New identity basis + exact rotation | CONT DISC EVD | Yes | Hidden replacement truth only |
| D | Unauthorized adapter rotation | Not modeled | `UNAVAILABLE` | Root-issued old→new rotation | DISC BND EVD | Yes | No |
| E | Authorized adapter rotation | Not modeled | `AUTHORIZED` if all requirements hold | Exact handoff, activation, supersession | all six | Yes | No |
| F | Two witness labels, one source | Relabeling can authorize | `UNAVAILABLE / SOURCE_DOMAIN_MEMBERSHIP_UNAVAILABLE` | Shared authoritative domain mapping | BND EVD CLO | Yes | Hidden correlation truth only |
| G | Two keys, one control domain | Can count if labels differ | `UNAVAILABLE` | Control/rollback-domain appraisal | DISC EVD CLO | Yes | Hidden control truth only |
| H | Distinct authoritative source domains | No exact positive model | `AUTHORIZED` if required and agreeing | Current memberships + exact views | all six | Yes | Appraisal truth remains external |
| I | Missing witness scope | Can authorize | `UNAVAILABLE / WITNESS_COVERAGE_UNAVAILABLE` | Exact semantic scope | CONT BND EVD | Yes | No |
| J | Missing interval coverage | Can authorize | `UNAVAILABLE / WITNESS_COVERAGE_UNAVAILABLE` | Full interval or gap-free handoff | CONT EVD USE | Yes | No |
| K | Stale witness currentness | Not enforced exactly | `UNAVAILABLE / WITNESS_CURRENTNESS_UNAVAILABLE` | Verifier-bound freshness | CONT EVD USE | Yes | No |
| L | Witness handoff gap | Not enforced | `UNAVAILABLE` | Ordered gap-free handoff | CONT DISC EVD | Yes | No |
| M | Witness overlap conflict | Partly conflict-checked | `UNAVAILABLE / OBSERVATION_WITNESS_CONFLICTING` | Exact overlap reconciliation | CONT EVD USE | Yes | No |
| N | Candidate invents independence labels | Can authorize | `UNAVAILABLE / SOURCE_DOMAIN_MEMBERSHIP_UNAVAILABLE` | Protected membership relation | BND EVD CLO | Yes | No |
| O | Candidate invents source lineage | Can authorize | `UNAVAILABLE` | Exact authoritative lineage | CONT DISC EVD | Yes | No |
| P | Source-domain authority missing | Not modeled | `UNAVAILABLE` | Root/classifier source authority | BND EVD CLO | Yes | No |
| Q | Source-domain authority stale | Not modeled | `UNAVAILABLE` | Current lifecycle/order/freshness | CONT EVD USE | Yes | No |
| R | Source-domain authority conflicting | Not modeled | `UNAVAILABLE / SOURCE_DOMAIN_MEMBERSHIP_CONFLICTING` | Unique current membership epoch | CONT BND EVD | Yes | No |
| S | Anchor shopping | Same-key co-presence blocked; cross-domain absent | `UNAVAILABLE` | Root-selected required-domain policy | BND EVD CLO | Yes | No |
| T | Witness shopping | Favorable relabel/subset possible | `UNAVAILABLE` | Policy-selected exact witnesses/domains | BND EVD CLO | Yes | No |
| U | Favorable quorum subset | Generic quorum absent | `UNAVAILABLE` | Preselected combinations + membership | BND EVD CLO | Yes | No |
| V | Required domain omitted | Not representable | `UNAVAILABLE / REQUIRED_SOURCE_DOMAIN_UNAVAILABLE` | Complete root policy domain set | CONT BND EVD | Yes | No |
| W | Cross-domain agreement | Not modeled | `AUTHORIZED` when exact/current | Per-domain views + agreement | all six | Yes | No |
| X | Cross-domain disagreement | Not modeled | `UNAVAILABLE / CROSS_DOMAIN_CHECKPOINT_CONFLICTING` | Reconciliation or convergence | CONT BND EVD USE | Yes | No |
| Y | One stale, one current required domain | Not modeled | `UNAVAILABLE` | Both current or superseded policy | CONT EVD USE | Yes | No |
| Z | One unavailable, one current domain | Not modeled | `UNAVAILABLE` if both required; otherwise possible `AUTHORIZED` | Exact policy optionality | BND EVD CLO | Yes | No |
| AA | Reconciled conflict | Not modeled | `AUTHORIZED` after exact resolution | All heads + current resolution authority | all six | Yes | No |
| AB | Unauthorized reconciliation | Not modeled | `UNAVAILABLE` | Exact reconciliation source authority | BND EVD CLO | Yes | No |
| AC | Adapter/source mismatch | Ignored adapter members can authorize | `UNAVAILABLE / ANCHOR_ADAPTER_CONFLICTING` | Exact source/admission join | CONT DISC EVD | Yes | No |
| AD | Same source via two adapters | May appear multiple | Count one domain; `UNAVAILABLE` if two required | Membership/rollback-domain mapping | BND EVD CLO | Yes | Hidden common source only |
| AE | Same witness via two identities | May appear multiple | Count one admitted identity/domain | Identity basis + membership | DISC EVD CLO | Yes | Hidden alias truth only |
| AF | Same key under two domain labels | Can appear independent | Count one; `UNAVAILABLE` if two required | Key/source/domain mapping | DISC EVD CLO | Yes | No when admitted |
| AG | Fresh key, same source lineage | Can appear independent | Count one domain | Source-lineage membership | CONT DISC CLO | Yes | Hidden lineage truth only |
| AH | Lineage changes without authority | Not enforced | `UNAVAILABLE` | Authorized lineage transition | CONT DISC EVD | Yes | No |
| AI | Authorized lineage transition | Not modeled | `AUTHORIZED` if gap-free/current | Exact predecessor/supersession | all six | Yes | No |
| AJ | Total rollback of all domains | Identical old input can authorize | Externally undecidable without survivor | No local fact can restore erased history | all six | N/A | Yes, fundamentally |
| AK | Total local rollback, one survivor | Later retained anchor rejects replay | `UNAVAILABLE / VERIFIER_STATE_ANCHOR_REPLAY` | One independently current survivor | CONT BND EVD USE | Yes | No if supplied |
| AL | Fresh genesis, independent domain | Single-anchor positive exists | `AUTHORIZED` after membership/admission | Genesis policy + current domain chain | all six | Yes | No |
| AM | Fresh successor after cross-domain recovery | Single-anchor successor positive exists | `AUTHORIZED` after reconciled recovery | Current domains + successor-specific chain | all six | Yes | No |

## 16. Positive AUTHORIZED paths

The design preserves these positive cases:

1. **Two independent domains agree:** root policy requires domains A and B; both memberships and adapters are current; exact views select one checkpoint; all ordinary authority facts hold.
2. **Authorized adapter rotation:** old adapter is superseded through an exact gap-free rotation; the new adapter responds to a current verifier challenge and observes the selected head.
3. **Authorized witness handoff:** exact old/new identity, source lineage, interval boundary, selected head, and current root authority establish uninterrupted coverage.
4. **Optional domain unavailable:** root policy explicitly requires only A and marks B optional before evaluation; A is independently current and exact. This is not candidate fallback.
5. **Authorized reconciliation:** all known competing domain views are named; current reconciliation authority selects a consistency/correction-supported lineage and supersedes incompatible views.
6. **Recovery from one survivor:** policy admits one independently current recovery anchor sufficient for the exact state key; complete ordered replay and installation remain required.
7. **Fresh successor after recovery:** cross-domain recovery is reconciled, then the existing successor model independently establishes identity, boundary, observation, objective, and successor-specific grant/use authority.

Each reaches `AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED`; no rule makes multiple domains mandatory where exact root policy legitimately requires one.

## 17. Existing-field and invariant mapping

| Design relation | Existing placement/composition | Primary invariants |
|---|---|---|
| Adapter admission/currentness | `evidence_binding` + `freshness` + source authority + ordering/lifecycle | CONT, DISC, BND, EVD, USE |
| Adapter rotation | `evidence_binding` predecessor/supersession relation | CONT, DISC, BND, USE |
| Source-domain membership | `evidence_binding` + `binding_source_authority` + identity/boundary/lifecycle | DISC, BND, EVD, CLO |
| Witness coverage/currentness | Existing witness-source records joined to observation interval/freshness | CONT, BND, EVD, USE |
| Required-domain policy | Root-issued relational fact under existing evidence/source-authority model | BND, EVD, CLO |
| Domain checkpoint view | Derived exact join, not candidate-supplied authority | CONT, EVD, USE |
| Reconciliation | Typed correction/supersession relation with ordering/lifecycle | CONT, BND, EVD, USE, CLO |

`INV-CLO` prohibits aggregation or relabeling from synthesizing independence. `INV-EVD` prevents signatures, labels, counters, and quorum certificates from self-authorizing. `INV-DISC` requires explicit identity/lineage transitions. `INV-CONT`, `INV-BND`, and `INV-USE` provide continuity, scope, currentness, and replay rules. No seventh invariant or tuple coordinate is needed.

## 18. Expected implementation surface

The smallest implementation slice is expected to change:

- `authority_lab/model.py`: strict immutable field sets and typed records for adapter admission/currentness/rotation, source-domain membership, required-domain policy, and reconciliation;
- `authority_lab/oracle.py`: exact joins, adapter consumption, witness scope/interval/currentness, required-domain derivation, anti-shopping, and reconciliation;
- `authority_lab/runner.py`: load protected domain/adapter context from a harness-owned manifest and expose deterministic reporting without accepting fixture-owned trusted context;
- `authority_lab/README.md`: bounded semantics and external trust statement;
- `tests/test_authority_lab.py`: expectation-independent unit/hostile tests;
- `cases/authority_lab/trusted_anchor_state.json` or one separate harness-owned typed domain manifest: authoritative adapter/domain policy contexts; and
- new hostile fixtures after `LAB-V1-146`.

Do not maintain separate accepted and evaluated relation registries. Every parsed relation capable of affecting authorization must be consumed exactly or fail closed. Canonical digests should cover every field whose alteration changes authority semantics.

## 19. Fixture migration implications

If adapter admission/currentness and domain policy become mandatory, all 146 maintained fixtures require an atomic mechanical migration because each current trusted anchor context carries adapter fields that are presently descriptive. The migration must:

- add exact harness-owned adapter/domain policy context for every fixture;
- add candidate-visible typed relations only where the candidate must present them;
- preserve all reviewed outcomes and reasons unless the design explicitly requires a more precise `UNAVAILABLE` reason;
- keep v0 unable to authorize;
- preserve current positive rotation, genesis, disaster recovery, correction, and successor cases; and
- never let fixture expectation strings or candidate fields supply protected membership/currentness.

New hostile fixtures should cover A–AM, with separate positive fixtures for adapter rotation, authoritative independent agreement, optional-domain policy, reconciliation, survivor recovery, genesis, and successor recovery. Exact fixture count is an implementation decision; migration and hostile expansion must land atomically.

## 20. Prior-art relationship

These are bounded conceptual precedents, not claims of equivalence:

- **Fault-domain modeling** distinguishes replicated records from failures that can occur independently; it motivates explicit control/upstream/rollback domains.
- **Byzantine quorum assumptions** require admitted membership and fault bounds; they show why numerical quorum does not prove independence. Authority Lab does not implement consensus.
- **Certificate Transparency gossip** compares checkpoints across parties to expose split views; it motivates cross-domain view comparison without claiming CT semantics.
- **Witness cosigning** binds parties to checkpoints but does not make signers independent by count alone.
- **Multi-party checkpointing** places state in multiple domains, while retaining membership, currentness, and reconciliation assumptions.
- **Remote-attestation trust domains** separate evidence production, verification, and appraisal; this design similarly keeps adapter/witness evidence from establishing its own authority.
- **Redundancy engineering** distinguishes diversity from independence: different implementations, keys, or labels may still share one common-mode failure.

## 21. Total-rollback limitation

The design provides conditional rollback resistance. If at least one required, independently admitted, current source survives and its evidence reaches the oracle, it can expose a stale or conflicting local history. One such source may be sufficient when root policy says so; majority is not required.

If candidate history, verifier state, every anchor, adapter, witness, domain membership record, reconciliation record, and every comparison source are rolled back or compromised into one mutually consistent old world, and no contrary evidence survives, the deterministic input is identical to a world that never advanced. No internal relation can infer the missing event. Hardware monotonic state, remote checkpoints, gossip, or external logs help only by leaving at least one applicable fact outside the rollback set.

Truthful real-world domain separation, source identity, key custody, adapter behavior, delivery, and at least one surviving current comparison source remain external trust preconditions.

## 22. Hostile design review

The proposed design was attacked as follows:

- **Relabeled adapter:** fails the exact protected admission/currentness join; labels do not select a new admission.
- **Relabeled witness domains:** fail authoritative membership; candidate strings never enter the counted domain set.
- **Same source behind multiple identities/adapters:** authoritative rollback/upstream-domain mapping collapses them to one effective domain.
- **Stale currentness:** verifier-bound challenge, exact ordering, lifecycle head, and protected per-domain context are mandatory.
- **Favorable subset selection:** root policy fixes required domains and combinations before candidate evaluation; array order and omission cannot select them.
- **Cross-domain disagreement:** produces `UNAVAILABLE` unless one current reconciliation names all known views and exact consistency/correction evidence.
- **Source-lineage replacement:** requires an authorized predecessor/supersession transition; stable keys or labels do not bridge it.
- **Adapter or classifier self-authorization:** forbidden role cycles and exact source authority prevent the evidence producer from establishing its own admission or independence.
- **Shared recovery authority:** sources mapped to one upstream/rollback domain count once; recovery does not manufacture independence.
- **Total rollback:** remains explicitly outside deterministic detection when no source survives; the design makes no absolute claim.
- **Positive-path regression:** single-domain policy, optional domains, authorized rotations/handoffs, reconciliation, survivor recovery, genesis, and fresh successor paths remain constructively reachable.

No in-scope bypass survives the proposed relational rules. The residual ways to defeat them require falsifying the admitted external classification/currentness roots or erasing every comparison source, which are stated trust boundaries rather than hidden authorization assumptions.

**PASS — NO REPRODUCIBLE IN-SCOPE ADAPTER-CURRENTNESS, SOURCE-INDEPENDENCE, OR CROSS-DOMAIN RECONCILIATION BYPASS SURVIVES THE PROPOSED DESIGN**

PASS means failure to falsify this design within its admitted input boundary, not proof of production independence, Byzantine safety, instrumentation truth, or universal rollback detection.

## 23. Frozen-contract sufficiency

The frozen 6/6/3 architecture remains sufficient. Adapter admission/currentness, source-domain membership, required-domain selection, witness coverage, and reconciliation are typed relationships among existing identity, evidence, boundary, ordering, lifecycle, freshness, use/replay, and closure semantics. They are not a seventh coordinate or invariant.

No schema-version change, fourth outcome, generic `trusted_adapter=true`, `independent=true`, `different_domain=true`, or candidate-controlled quorum primitive is required. Executable implementation is justified as one atomic slice after review of this design.
