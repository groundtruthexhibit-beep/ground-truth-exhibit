# Frontier Delta: Independent Anchor Currentness and Total-Rollback Detection

## 1. Exact baseline

This research starts from reviewed commit `74fa6ff9e121dfc9176d34fcfd2bce1cfd709fc2` on `fix/authority-lab-v1-verifier-state-anchoring`, parent `85aba19e14272d20445a12565f0756a067c3abe2`, with commit subject `fix: enforce Authority Lab verifier state anchoring`.

The executable baseline is unchanged:

- schema `authority-lab-v1`;
- tuple `(subject, artifact, control_state, identity_basis, boundary_epoch, decision)` — six coordinates;
- invariants `INV-CONT`, `INV-DISC`, `INV-BND`, `INV-EVD`, `INV-USE`, and `INV-CLO` — six invariants;
- outcomes `AUTHORIZED`, `DENIED`, and `UNAVAILABLE` — three outcomes;
- `195/195` public tests passing; and
- `146/146` Authority Lab fixtures passing.

The implementation under attack has canonical verifier-state anchors, exact candidate-to-harness anchor joins, monotonic position checks, replay and same-position fork rejection, recovery receipts, verifier and anchor rotation relations, and witness-source records. This document changes no executable code, fixture, manifest, schema, tuple coordinate, invariant, or outcome.

## 2. Current trust boundary

The implementation proves currentness only relative to `trusted_anchor_state.json`. The runner owns that manifest and prevents fixture JSON from supplying `_trusted_anchor_context`. For one anchor key the oracle requires exactly one matching harness context and compares the selected anchor position, digest, state key, stream, head, verifier generation, durable-state generation, and freshness challenge.

That successfully blocks rollback when a later harness anchor survives. It does not prove that the adapter record supplying the harness context is itself current, continuously controlled, independent of the evaluated verifier, or outside the same rollback set. The context carries adapter identity, generation, observation identity, observation generation, and event order, but current evaluation does not consume those members.

The explicit residual boundary remains unavoidable in its strongest form:

> If every admitted comparison source and the candidate history are rolled back or compromised consistently, and no contrary fact survives outside that rollback set, a deterministic oracle receives the same input as a world that never advanced.

This frontier separates that external impossibility from executable omissions that occur even when adapter or witness continuity facts are present in the admitted input.

## 3. Anchor, adapter, and witness model

The current model has three layers:

1. Candidate-visible `anchor_source_admissions` and `verifier_state_anchors` inside `evidence_binding`.
2. Harness-owned anchor context containing `adapter_source_id`, adapter/source generations, observation identity/order, selected anchor/head, and recovery policy flags.
3. Candidate-visible `witness_source_admissions` containing witness identity basis, source lineage, control domain, scope, interval, lifecycle, and selected anchor/head.

The oracle currently establishes the anchor statement and its root-issued source admission exactly. It also rejects missing or duplicate matching contexts, stale anchor positions, same-position digest conflicts, explicit anchor revocation, and declared witness control-domain collapse when harness policy requests multiple domains.

The missing joins are narrower and reproducible:

- adapter identity, generation, observation generation, and event order are carried but not evaluated;
- adapter/source-role separation is not evaluated;
- witness identity basis, coverage interval, covered semantic families, freshness, and replacement/handoff are parsed but not evaluated;
- witness independence is inferred from distinct candidate-visible strings rather than joined to independently retained source/control-domain evidence; and
- no cross-domain anchor-set relation establishes which domains are required, independent, current, or reconciled.

## 4. Independence versus multiplicity

Multiplicity counts records. Independence is a causal and authority relationship: two records must not derive their currentness from the same rollback, control, storage, key-custody, process, upstream checkpoint, or recovery authority domain when policy relies on their disagreement surviving one failure.

Different IDs, keys, signatures, source-lineage labels, or `control_domain` strings do not establish independence by themselves. Conversely, one exact independently current source can be enough to reject a stale candidate; the contract does not require a quorum when a single authoritative surviving comparison source is sufficient.

Current Authority Lab correctly refuses to count two witnesses with the same declared control domain. It does not establish that two differently declared domains are genuinely distinct. A root-issued relational claim may describe independence, but it must itself be bound to current source identity, scope, lifecycle, and a non-circular appraisal source. Candidate-visible relabeling must not create the missing causal relationship.

## 5. Currentness model

The required distinctions are:

| Property | Required meaning | Current executable status |
|---|---|---|
| Anchor identity | Exact anchor statement and lineage | Established |
| Adapter identity | Exact process/source producing current context | Carried, not evaluated |
| Anchor source lineage | Authorized anchor-source generation and key | Established for candidate statement |
| Control domain | Authority/control failure domain | Witness label parsed; anchor adapter domain absent |
| Independence domain | Failures not governed by one upstream source | Not independently established |
| Anchor freshness | Selected anchor is current | Established only relative to supplied harness context |
| Adapter freshness | Adapter observation is current | Fields carried, not evaluated |
| Currentness | No later applicable state survives | Relative, not absolute; requires outside comparison |
| Signature validity | Evidence integrity/authenticity | Never sufficient by itself |
| Witness source lineage | Exact source continuity across replacement | Parsed, not enforced end-to-end |
| Checkpoint consistency | Heads form one admitted history | Local conflicts blocked; cross-domain set absent |
| Rollback domain | Components that can roll back together | Not represented |
| Recovery authority | Independent authority installing recovered state | Represented for one anchor lineage |

## 6. A–AN hostile matrix

`AUTHORIZED*` means an executable authorization is reproducible under the stated admitted input, while the hostile world interpretation should withhold authority. Conceptual cases identify information that cannot be inferred from current admitted input.

| ID | Hostile case | Reproducer | Current outcome | Desired outcome / reason | Invariants | Classification | Fits v1 |
|---|---|---|---|---|---|---|---|
| A | Two adapters, one shared store | Conceptual; no multi-adapter set | Each isolated valid context can authorize | `UNAVAILABLE / ANCHOR_INDEPENDENCE_UNAVAILABLE` when independence required | BND EVD CLO | contract-compatible implementation obligation | Yes |
| B | Two witnesses, one control domain | `LAB-V1-133` | `UNAVAILABLE / WITNESS_SOURCE_CONTINUITY_UNAVAILABLE` | Same | BND EVD CLO | already blocked when visible | Yes |
| C | Multiple signatures, one anchor service | Conceptual | Signature count has no selection role | No independence credit | EVD CLO | already sound; source truth external | Yes |
| D | Adapter replacement behind same identity | Executable reproducer 7.1 | `AUTHORIZED*` | `UNAVAILABLE / ANCHOR_ADAPTER_CONTINUITY_UNAVAILABLE` | CONT DISC EVD USE | executable defect | Yes |
| E | Adapter process replaced, same key | Same as D; process is not bound | `AUTHORIZED*` | `UNAVAILABLE` absent admitted rotation | CONT DISC EVD | executable defect plus input-root truth | Yes |
| F | Anchor key rotation without continuity | Existing unauthorized rotation path | `UNAVAILABLE / ANCHOR_ROTATION_UNAVAILABLE` | Same | DISC BND EVD CLO | already blocked for represented anchor rotation | Yes |
| G | Verifier and adapter rolled back together | Restore candidate plus harness context | `AUTHORIZED*` | `UNAVAILABLE` if any outside current source survives | CONT DISC EVD USE | executable manifestation; total case external | Yes |
| H | Verifier and witnesses rolled back together | Conceptual | Matching rolled context can authorize | `UNAVAILABLE` if current witness required | CONT EVD USE CLO | implementation obligation; total case external | Yes |
| I | Local verifier/anchor stale, remote checkpoint current | Existing higher retained context pattern | `UNAVAILABLE / VERIFIER_STATE_ANCHOR_REPLAY` | Same | CONT EVD USE | blocked when survivor is supplied | Yes |
| J | Remote stale, local independent source current | Conceptual cross-domain inverse | No cross-domain policy | Current source must reject stale domain | CONT BND EVD USE | implementation obligation | Yes |
| K | Every admitted source rolled back | Identical-input worlds | `AUTHORIZED*` | Cannot distinguish without surviving evidence | all six | external impossibility boundary | No local repair can remove boundary |
| L | Three anchors derive from one upstream | Conceptual | No anchor-domain set | No independence credit | BND EVD CLO | implementation obligation | Yes |
| M | 2-of-3 where two share one source | Conceptual | No quorum policy | Correlated pair counts as one domain | BND EVD CLO | contract gap only if quorum semantics claimed; otherwise implementation direction | Yes |
| N | 3-of-5 with hidden common-mode dependency | Conceptual | Hidden dependency absent | `UNAVAILABLE` when required independence unproved | BND EVD CLO | observation/input-root boundary plus obligation | Yes |
| O | Cross-domain checkpoints disagree | Conceptual; same-key duplicate context fails | Duplicate same key: `UNAVAILABLE` | `UNAVAILABLE / CROSS_DOMAIN_ANCHOR_CONFLICTING` | CONT BND EVD USE | partly blocked; set semantics missing | Yes |
| P | Domains agree but one is stale | Conceptual | Agreement can appear valid | Require domain-specific freshness | CONT EVD USE | implementation obligation | Yes |
| Q | One domain advances, another rolls back | Conceptual | No required-domain policy | `UNAVAILABLE` pending reconciliation | CONT BND EVD USE | implementation obligation | Yes |
| R | Anchor producer self-attests freshness | Adapter role-cycle reproducer | `AUTHORIZED*` | `UNAVAILABLE / ADAPTER_SOURCE_AUTHORITY_UNAVAILABLE` | BND EVD CLO | executable defect | Yes |
| S | Fresh adapter timestamp over stale head | Adapter order reproducer | `AUTHORIZED*` | `UNAVAILABLE / ANCHOR_ADAPTER_FRESHNESS_UNAVAILABLE` | CONT EVD USE | executable defect | Yes |
| T | Valid digest, adapter currentness unproved | Baseline with ignored adapter members | `AUTHORIZED*` | `UNAVAILABLE` absent verifier-bound adapter currentness | CONT EVD USE | executable defect | Yes |
| U | Adapter current, underlying anchor lineage changed | Conceptual replacement | Exact visible mismatch blocked; hidden change authorizes | `UNAVAILABLE` absent lineage transition | CONT DISC BND | implementation obligation plus external truth | Yes |
| V | Witness label stable, source lineage changed | Executable mutation of ignored lineage/identity | `AUTHORIZED*` | `UNAVAILABLE / WITNESS_SOURCE_CONTINUITY_UNAVAILABLE` | CONT DISC EVD | executable defect | Yes |
| W | Witness handoff gap | Remove witness interval coverage | `AUTHORIZED*` | `UNAVAILABLE / WITNESS_COVERAGE_UNAVAILABLE` | CONT BND EVD | executable defect | Yes |
| X | Witness handoff overlap conflict | Conceptual; no witness handoff relation | May authorize if conflict not surfaced | `UNAVAILABLE / WITNESS_CONFLICTING` | CONT BND EVD USE | implementation obligation | Yes |
| Y | Anchor generation reused after replacement | Rolled matching context | `AUTHORIZED*` if context also reused | `UNAVAILABLE` when outside lineage survives | CONT DISC EVD USE | external at total boundary; otherwise obligation | Yes |
| Z | Rollback hidden behind new generation label | Conceptual relabeling | Matching harness context can authorize | `UNAVAILABLE` absent authorized transition | CONT DISC EVD CLO | implementation obligation | Yes |
| AA | Recovery from inconsistent checkpoints | Current recovery relation names one source | No cross-domain comparison | `UNAVAILABLE / RECOVERY_CONFLICTING` | CONT BND EVD USE | implementation obligation | Yes |
| AB | Recovery from one stale and one current checkpoint | Conceptual | No multi-source selection | Select only independently current reconciled checkpoint | CONT EVD USE | implementation obligation | Yes |
| AC | Candidate chooses favorable anchor | Same-key duplicate is rejected | `UNAVAILABLE / VERIFIER_STATE_ANCHOR_UNAVAILABLE` when co-present | Same; required-domain selection must be external | BND EVD CLO | locally blocked, cross-key policy missing | Yes |
| AD | Verifier shops among anchors | Conceptual isolated invocations | Each isolated matching context can authorize | `UNAVAILABLE` until required anchor set selects head | BND EVD CLO | implementation obligation | Yes |
| AE | Majority over correlated anchors | Conceptual | No majority rule | Majority cannot replace independence | BND EVD CLO | current contract already forbids inference | Yes |
| AF | Independent domains agree | Positive conceptual control | No multi-domain positive path | `AUTHORIZED` after exact domain admissions/currentness | all six | positive implementation obligation | Yes |
| AG | Independent domains conflict | Conceptual | No cross-domain set | `UNAVAILABLE` pending authorized reconciliation | CONT BND EVD USE | implementation obligation | Yes |
| AH | Explicit anchor revocation | `LAB-V1-146` | `DENIED / VERIFIER_STATE_ANCHOR_PROHIBITED` | Same | BND EVD USE | already blocked correctly | Yes |
| AI | Authorized anchor replacement | `LAB-V1-132` | `AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED` | Same | all six | positive control passes | Yes |
| AJ | Authorized cross-domain reconciliation | Conceptual | Not represented | `AUTHORIZED` only after resolution names all heads/domains | all six | positive implementation obligation | Yes |
| AK | Total rollback, no surviving source | Identical-input worlds | `AUTHORIZED*` | Fundamentally undetectable locally | all six | external impossibility boundary | No local mechanism can prove missing fact |
| AL | Total local rollback, one independent survivor | Higher survivor context pattern | `UNAVAILABLE / VERIFIER_STATE_ANCHOR_REPLAY` | Same | CONT BND EVD USE | existing single-survivor mechanism sufficient if supplied | Yes |
| AM | Fresh genesis with independent anchor | `LAB-V1-143` | `AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED` | Same, independence admission still externally truthful | all six | positive control passes | Yes |
| AN | Fresh successor after cross-domain recovery | `LAB-V1-145` covers successor after recovery; cross-domain part absent | `AUTHORIZED` for single anchor | `AUTHORIZED` after reconciled independent-domain recovery | all six | partial positive; cross-domain obligation | Yes |

## 7. Executable reproducers

All reproducers start from `runner.load_fixture`, so trusted contexts remain harness-loaded rather than fixture-file fields. They mutate the in-memory admitted input only to determine which semantic members the oracle consumes. Expected strings never participate in evaluation.

### 7.1 Adapter replacement and stale adapter observation

Starting from `LAB-V1-032`, change only harness-owned adapter metadata:

```python
case = fixture("LAB-V1-032")
context = case["_trusted_anchor_context"][0]
context["adapter_source_id"] = "REPLACED-ADAPTER"
context["adapter_source_generation"] = 99
context["adapter_observation_id"] = "REPLACED-OBSERVATION"
context["adapter_observation_generation"] = 99
```

Observed result:

```text
AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED
```

Changing `adapter_event_order` to `0` also preserves the same result. Changing `adapter_source_id` to a role-cyclic value representing the anchor producer itself likewise preserves authorization. The context fields are schema-valid and retained, but they do not constrain authority evaluation.

### 7.2 Correlated witnesses relabeled as independent

`LAB-V1-133` correctly returns `UNAVAILABLE / WITNESS_SOURCE_CONTINUITY_UNAVAILABLE` when both witnesses declare one control domain. Change only the second candidate-visible witness admission:

```python
witness["witness_source_id"] = "CLAIMED-INDEPENDENT-SOURCE"
witness["source_lineage"] = "CLAIMED-INDEPENDENT-LINEAGE"
witness["control_domain"] = "CLAIMED-INDEPENDENT-DOMAIN"
```

Observed result:

```text
AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED
```

This does not prove the real sources are correlated. It proves that current execution treats distinct strings as sufficient evidence of the required independence domains. No harness-owned or separately appraised source-domain relation closes that claim.

### 7.3 Witness coverage and identity discontinuity are not consumed

Starting from authorized `LAB-V1-134`:

- narrow one witness interval to event `3..3`;
- replace its covered scope with `UNRELATED`; or
- make both witnesses use the same `witness_identity_basis`.

Each mutation still returns:

```text
AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED
```

The records are parsed and retained, but the oracle currently counts valid-looking control domains without enforcing exact interval coverage, semantic-family scope, identity separation, freshness, or handoff continuity.

### 7.4 Existing correct controls

- Duplicating the matching trusted context produces `UNAVAILABLE / VERIFIER_STATE_ANCHOR_UNAVAILABLE`; candidate shopping within one anchor key is blocked.
- `LAB-V1-133` blocks visibly shared witness domains.
- `LAB-V1-119` blocks an admitted anchor fork.
- `LAB-V1-139` blocks a stale anchor when a later independently retained anchor survives.
- `LAB-V1-146` maps explicit current anchor revocation to `DENIED`.
- `LAB-V1-132`, `143`, and `145` preserve authorized anchor rotation, fresh genesis, and fresh successor paths.

## 8. Reproducible counterexample

The smallest executable counterexample is adapter replacement:

```text
valid candidate anchor + exact selected head
+ harness context whose adapter identity/generation/observation lineage is replaced
+ unchanged anchor/head comparison members
-> AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED
```

The stated authority objective requires the currentness source itself to be independently current and continuity-bound. The oracle cannot presently distinguish the reviewed adapter from an unadmitted replacement because it ignores the adapter members already carried in trusted context.

A second counterexample affects policies that require independent witnesses:

```text
two correlated witness records
+ candidate-visible distinct source-lineage/control-domain labels
+ harness policy requires two domains
-> AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED
```

The implementation establishes multiplicity of declared domains, not independently appraised source-domain separation. These are implementation gaps inside the deterministic boundary. They are distinct from AK, where every source and all contrary evidence are rolled back and no input distinction exists.

## 9. Quorum and correlation analysis

No value of `N-of-M` proves independence. A quorum can establish a decision only relative to admitted membership, epoch, source lineage, control-domain mapping, fault assumptions, and a current commit/certificate relation. Two signatures controlled by one service remain one failure domain. Three cloud replicas sharing one rollback-capable database remain one rollback domain.

Authority Lab should not implement generic Byzantine consensus. If a deployment relies on a quorum certificate, the lab can treat it as typed evidence whose membership epoch, distinct admitted source domains, checkpoint, ordering, freshness, and resolution are exact. `INV-EVD` still prevents the quorum from manufacturing execution authority.

## 10. Adapter replacement analysis

Adapter and anchor source are different roles. The anchor source produces or retains the anchored history; the adapter supplies a current observation of that source to the verifier. Current trusted context carries adapter fields but does not join them to:

- a root-issued adapter admission;
- adapter identity basis and control domain;
- lifecycle and supersession;
- exact scope and anchor lineage;
- a verifier-bound freshness challenge;
- predecessor adapter observation;
- authorized handoff/rotation; or
- a prohibition against subject/verifier/anchor-producer role cycles.

The smallest repair direction is an exact typed adapter-admission/currentness relation composed under existing `evidence_binding`, source authority, lifecycle, ordering, freshness, boundary, and identity semantics. It must join to harness context and reject ignored adapter members. A naked `adapter_current=true` is insufficient.

## 11. Cross-domain checkpoint analysis

The present oracle selects one exact anchor context per anchor key. This is sufficient when the policy admits one comparison source. It does not model a required set of independent anchor domains, domain-specific current heads, or reconciliation across domains.

A bounded cross-domain model would need:

1. root-issued anchor-domain membership and independence-source admissions;
2. exact per-domain adapter identity/currentness;
3. a required-domain policy bound to the state key, boundary, and interval;
4. one current checkpoint per required domain;
5. conflict semantics that do not use arrival order or majority;
6. authorized reconciliation naming every known incompatible head; and
7. a positive rule permitting consistent current domains to support authorization.

Candidate or verifier selection cannot choose which required domains participate. Missing or conflicting required domains yield `UNAVAILABLE`; explicit current revocation remains `DENIED`.

## 12. Total-rollback analysis

Total rollback has two materially different forms.

**With a survivor:** if any independently admitted source retains a later position or incompatible head and its evidence reaches the oracle, the current anchor replay/fork checks can fail closed. One survivor is sufficient when it has authority for the exact state key and interval; numerical majority is unnecessary.

**Without a survivor:** if candidate history, verifier state, every required anchor, every adapter, every witness, every comparison source, and every recovery record are restored to one earlier mutually consistent world, then the oracle input is identical to a world that never advanced. No deterministic rule over that input can recover the absent fact. Hardware counters, remote checkpoints, gossip, witnesses, or external logs help only by placing at least one relevant fact outside the rollback set.

The correct claim is therefore conditional rollback resistance, not absolute detection: authority can fail closed relative to at least one independently current surviving comparison source.

## 13. Positive controls

The repair direction must preserve:

- two admitted independent anchor domains agreeing on one current head;
- authorized adapter handoff/rotation with no coverage gap;
- authorized anchor replacement (`LAB-V1-132` remains reachable);
- current cross-domain reconciliation naming all competing heads;
- independent witness support with exact scope and interval;
- recovery from one surviving independent current anchor;
- fresh anchored genesis (`LAB-V1-143`); and
- fresh successor after reconciled recovery (`LAB-V1-145` plus cross-domain evidence).

Each may reach `AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED` only after every ordinary objective, identity, boundary, observation, grant/use, closure, commitment, successor, anchor, and recovery requirement succeeds.

## 14. Invariant mapping

- `INV-CONT`: adapter observations, witness coverage, required anchor domains, and reconciled checkpoints must form one continuous current history.
- `INV-DISC`: stable IDs, keys, labels, processes, generations, and domain names do not prove adapter, anchor-source, or witness continuity.
- `INV-BND`: adapter, anchor domain, witness, reconciliation, and recovery authority remain scoped to the exact applicable boundary and epoch.
- `INV-EVD`: signatures, timestamps, counters, quorum certificates, domain labels, and witness records are evidence; none self-establishes independence or current authority.
- `INV-USE`: stale anchors, adapter observations, witness heads, generations, and reconciliation records cannot be replayed as current.
- `INV-CLO`: aggregates, quorums, shared stores, common upstream services, wrappers, and relabeled domains cannot inherit or synthesize independence.

The executable failures are failures to enforce existing invariants, not evidence that a seventh invariant is needed.

## 15. Contract sufficiency

The frozen 6/6/3 architecture remains sufficient. The missing semantics are relational facts about existing evidence, identity, boundary, continuity, currentness, ordering, use/replay, and closure—not a new authority outcome or tuple dimension.

Expected behavior remains:

- `UNAVAILABLE` for unproved adapter continuity/currentness, correlated or unappraised source domains, missing domain coverage, conflicting checkpoints, unresolved reconciliation, and rollback without a trusted survivor;
- `DENIED` only for explicit current authoritative prohibition, revocation, rejection, or invalidity; and
- `AUTHORIZED` when required independent domains and adapters are exactly current, consistent or authoritatively reconciled, and every other authority requirement holds.

## 16. Possible design directions

A design slice is justified. It should remain design-only first and specify:

1. strict adapter admission, identity, scope, lifecycle, freshness, predecessor, handoff, and rotation relations;
2. an immutable required anchor-domain policy selected by the applicable root, not candidate/verifier choice;
3. harness-owned domain/source mappings sufficient to prevent candidate relabeling from proving independence;
4. exact witness identity/source/coverage/freshness evaluation rather than domain-counting alone;
5. cross-domain checkpoint-set and conflict/reconciliation relations;
6. verifier-bound adapter challenges and durable per-domain currentness;
7. explicit rollback-domain assumptions and the minimum surviving-source rule; and
8. positive adapter rotation, independent agreement, reconciliation, recovery, genesis, and successor paths.

No generic `trusted_adapter`, `independent`, `quorum_valid`, or `current` Boolean should be admitted.

## 17. Prior-art notes

These are bounded analogies, not equivalence or superiority claims.

- Certificate Transparency gossip illustrates that a valid signed checkpoint does not prevent a split view; comparison across parties is what exposes inconsistency.
- Witness cosigning illustrates binding multiple parties to a checkpoint, while also showing that signer count alone says nothing about common control.
- Byzantine quorum models make fault-domain and membership assumptions explicit. Ground Truth does not implement Byzantine consensus.
- Reliability engineering's common-mode failure analysis explains why replicas sharing storage, control, deployment, or recovery mechanisms are not independent failures.
- Remote-attestation appraisal separates evidence producers, verifiers, freshness, and relying-party decisions; verifier independence remains a separate assumption.
- Multi-party checkpointing and external anchoring can place state outside one rollback domain, but move rather than eliminate trust roots.
- Distributed monotonic counters can expose rollback only while at least one relevant counter/anchor remains current and authentic.

## 18. Residual trust boundary

After any future repair, truthful real-world control-domain separation, key custody, process identity, adapter behavior, checkpoint delivery, clock/counter behavior, and at least one surviving non-colluding current source remain external preconditions. The lab can require and join admitted evidence; it cannot observe hidden common ownership or resurrect evidence erased from every admitted source.

PASS for a future fixture set would mean failure to falsify the implementation inside that explicit boundary. It would not prove production anchor independence, Byzantine safety, hardware integrity, or universal rollback detection.

## 19. Exact hostile-research verdict

**FAIL — REPRODUCIBLE IN-SCOPE ANCHOR-CURRENTNESS OR INDEPENDENCE COUNTEREXAMPLE FOUND**

The exact executable failures are:

1. replacing or staling adapter identity/currentness members in harness-owned trusted context does not change `AUTHORIZED`;
2. candidate-visible source-lineage/control-domain relabeling can convert a visibly shared witness source from `UNAVAILABLE` to `AUTHORIZED`; and
3. witness identity, semantic scope, and interval coverage can be removed while `AUTHORIZED` remains.

Total rollback with no surviving contradictory source remains separately and fundamentally undetectable from identical oracle input. The next slice should design adapter admission/currentness, independently appraised source-domain membership, witness coverage/currentness enforcement, and cross-domain checkpoint reconciliation within the existing 6/6/3 contract.
