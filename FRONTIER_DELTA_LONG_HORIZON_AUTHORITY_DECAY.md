# Frontier Delta: Long-Horizon Authority Decay

## 1. Exact baseline

This research starts from commit `aebd2410be1316826fc0013790933a1cc87a8f46` on `fix/authority-lab-v1-tool-connector-authority-continuity`, parent `00738082008b17881a23fec02eb8b3791db23d7c`, with subject `fix: enforce Authority Lab tool connector authority continuity`.

The reviewed baseline has 247 public tests and 411 deterministic fixtures passing. It retains schema `authority-lab-v1`, six tuple coordinates, six invariants, and three outcomes. This commit changes no executable code or maintained fixture.

## 2. Temporal authority model

Historical authorization is not execution authority. The public contract places T3 at the irreversible authority-consuming boundary and requires every applicable condition to be exact and current there. A queue item, cached verdict, signed envelope, reusable grant, protected context, or internally consistent digest is evidence only. It cannot move the authority-consuming boundary backward to the time it was created.

Authority Lab already models many protected temporal heads:

| Layer | Current protected time relation |
|---|---|
| Observation | T3 anchor and freshness head |
| Objective/root | binding ordering and lifecycle head |
| Delegation | delegation ordering head and terminal-use event |
| Human approval | approval ordering head, expiry, lifecycle, and use event |
| Tool/connector | selection head and protected terminal-use event |
| Commitment/verifier/anchor | commitment, checkpoint, anchor, adapter, domain-view, and recovery ordering |
| Successor/grant | ordered transition and successor-specific terminal use |

Each layer is strongly checked internally. The executable gap is that all authority-consuming layer heads are not required to equal one canonical T3 execution event. Several checks accept a layer head merely because it is no later than T3. That permits a time-skewed composition in which an approval or delegation is used at event 2 while the tool effect executes at event 3.

## 3. T1 / T2 / T3 distinction

- **T1:** provisional authority is established for an exact tuple and exact protected relations.
- **T2:** preparation, queuing, delay, mutation, retry, recovery, or partial work may occur, but none creates authority.
- **T3:** the material effect consumes authority. Every applicable protected layer must be current for this same event, not merely current at some earlier event carrying the same freshness label.

The current observation model correctly fixes a T3 anchor. Human Approval, Delegation, and Tool/Connector each possess a terminal-use event. The defect is therefore not absence of time fields. It is an incomplete equality join across existing time fields.

## 4. Hostile matrix A–BN

`Blocked` means the current executable oracle fails closed when the transition is represented in its protected input. `Gap` means cross-layer terminal time is not joined exactly. `Boundary` means the event cannot be inferred if omitted before admitted input construction.

| Case | Scenario | Current result | Required result | Classification / invariants |
|---|---|---|---|---|
| A | Immediate unchanged execution | `AUTHORIZED` | `AUTHORIZED` | Positive; all six |
| B | Delay, no changes, exact T3 revalidation | `AUTHORIZED` | `AUTHORIZED` | Positive; CONT/USE |
| C | Queue after approval expiry | Can `AUTHORIZED` with approval use/expiry 2 and tool use 3 | `UNAVAILABLE` | **Executable gap**; CONT/EVD/USE |
| D | Queue after approval revocation | `DENIED` if current revocation is present; omission is Boundary | `DENIED` | Blocked/Boundary; CONT/USE |
| E | Queue after delegation revocation | `DENIED` if represented | `DENIED` | Blocked; CONT/USE |
| F | Queue after delegation supersession | `UNAVAILABLE` if represented | `UNAVAILABLE` | Blocked; CONT/DISC/USE |
| G | Queue after subject/successor transition | `UNAVAILABLE` without fresh successor | `UNAVAILABLE` | Blocked; CONT/DISC |
| H | Queue after boundary epoch change | `UNAVAILABLE` without current chain | `UNAVAILABLE` | Blocked; BND/CONT |
| I | Queue after execution-context change | `UNAVAILABLE` | `UNAVAILABLE` | Blocked; CONT/BND |
| J | Queue after tool rotation | `UNAVAILABLE` without protected transition/revalidation | `UNAVAILABLE` | Blocked; CONT/USE |
| K | Queue after connector handoff | `UNAVAILABLE` without handoff | `UNAVAILABLE` | Blocked; CONT/USE |
| L | Queue after backend migration | `UNAVAILABLE` without migration | `UNAVAILABLE` | Blocked; CONT/USE |
| M | Queue after credential rotation | `UNAVAILABLE` without rotation | `UNAVAILABLE` | Blocked; CONT/EVD |
| N | Queue after permission expansion | `UNAVAILABLE` without transition/revalidation | `UNAVAILABLE` | Blocked; CONT/CLO |
| O | Queue after permission narrowing | Fails if effect no longer allowed; positive if current scope still admits it | Same | Blocked; USE/CLO |
| P | Queue after verifier recovery | `UNAVAILABLE` without exact recovery installation | `UNAVAILABLE` | Blocked; EVD/USE |
| Q | Queue after verifier rotation | `UNAVAILABLE` without rotation | `UNAVAILABLE` | Blocked; DISC/EVD |
| R | Queue after anchor rotation | `UNAVAILABLE` without rotation | `UNAVAILABLE` | Blocked; CONT/EVD |
| S | Queue after adapter rotation | `UNAVAILABLE` without protected rotation | `UNAVAILABLE` | Blocked; CONT/EVD |
| T | Queue after witness handoff | `UNAVAILABLE` on gap/conflict | `UNAVAILABLE` | Blocked; EVD/CLO |
| U | Queue after cross-domain reconciliation | Requires current exact reconciliation | Same | Blocked; EVD/CLO |
| V | Scheduled action after authority mutation | Registered mutation fails closed absent re-establishment | `UNAVAILABLE` | Blocked; CONT |
| W | Scheduled action after human intent revocation | `DENIED` if current revocation admitted | `DENIED` | Blocked/Boundary; USE |
| X | Retry after failure and authority change | Existing mutation/use state fails closed | `UNAVAILABLE` | Blocked; CONT/USE |
| Y | Retry after credential change | `UNAVAILABLE` | `UNAVAILABLE` | Blocked; CONT/EVD |
| Z | Retry after backend change | `UNAVAILABLE` | `UNAVAILABLE` | Blocked; CONT/USE |
| AA | Retry after successor transition | `UNAVAILABLE` without successor chain | `UNAVAILABLE` | Blocked; DISC/USE |
| AB | Replay previously authorized execution envelope | Durable use/commitment state blocks bounded replay | `UNAVAILABLE` | Blocked; USE |
| AC | Replay after restart | `UNAVAILABLE` without continuity/current use | `UNAVAILABLE` | Blocked; CONT/USE |
| AD | Replay after snapshot restore | `UNAVAILABLE` when durable state survives; total external rollback is Boundary | `UNAVAILABLE` | Blocked/Boundary; EVD/USE |
| AE | Replay after recovery | `UNAVAILABLE` without anchored recovery | `UNAVAILABLE` | Blocked; EVD/USE |
| AF | Partial execution then revocation | No multi-stage primitive; each material continuation must be a new T3 | `DENIED` at next effect | Semantic obligation; CONT/USE |
| AG | Partial execution then boundary change | Same limitation; next material effect requires fresh T3 | `UNAVAILABLE` | Semantic obligation; BND/USE |
| AH | Partial execution then tool change | Next material effect requires current tool context | `UNAVAILABLE` | Expressible; CONT/USE |
| AI | Stage 1 authorized, stage 2 effect differs | Effect/request bindings reject reuse | `UNAVAILABLE` | Blocked; EVD/USE |
| AJ | Stale cryptographically valid grant | Signature does not establish currentness | `UNAVAILABLE` | Blocked; EVD/USE |
| AK | Stale correctly signed approval | Approval expiry/head checks block when compared to its head; cross-head gap remains | `UNAVAILABLE` | **Gap class**; CONT/USE |
| AL | Stale internally consistent tool context | Protected current target/use join blocks | `UNAVAILABLE` | Blocked; CONT/USE |
| AM | Stale internally consistent verifier context | Anchor anti-replay blocks if later state survives | `UNAVAILABLE` | Blocked/Boundary; EVD |
| AN | Stale anchor/context combination | Exact joins reject mismatch | `UNAVAILABLE` | Blocked; EVD/USE |
| AO | Queue stores old currentness evidence | Old heads do not generally refresh; cross-layer head skew can survive | `UNAVAILABLE` | **Executable gap class**; CONT/USE |
| AP | Queue self-reports refreshed timestamp | Candidate timestamp has no authority | `UNAVAILABLE` | Blocked; EVD |
| AQ | Worker refreshes timestamp, not sources | Freshness challenge/source joins reject | `UNAVAILABLE` | Blocked; EVD/CLO |
| AR | Candidate recomputes local digests at T3 | Protected digests and sources reject | `UNAVAILABLE` | Blocked; EVD/CLO |
| AS | Delay crosses explicit expiry | Can authorize when expiry is compared to approval head 2, not execution 3 | `UNAVAILABLE` | **Executable defect**; CONT/USE |
| AT | Delay crosses revocation | `DENIED` when revocation is admitted | `DENIED` | Blocked/Boundary; USE |
| AU | Delay crosses supersession | `UNAVAILABLE` when admitted | `UNAVAILABLE` | Blocked/Boundary; CONT |
| AV | Long-lived grant without explicit expiry | Permitted only while all defined current conditions remain established | Conditional `AUTHORIZED` | Contract-sound; USE |
| AW | Indefinitely reusable approval under reusable policy | Bounded by policy/lifecycle/expiry; no implicit permanence | Conditional `AUTHORIZED` | Contract-sound; USE |
| AX | Execution outside validity interval | Delegation/approval interval checks fail only against their own heads | `UNAVAILABLE` | **Cross-head gap**; CONT/USE |
| AY | Authorization before policy change | Old policy cannot satisfy current protected policy when change represented | `UNAVAILABLE` | Blocked; CONT/CLO |
| AZ | Execution after policy change | Current policy join required | `UNAVAILABLE` absent revalidation | Blocked; CONT/CLO |
| BA | Approval policy becomes stricter | Old approval fails exact current policy | `UNAVAILABLE` | Blocked; CONT/CLO |
| BB | Required-domain policy changes | Current all-applicable domain policy required | `UNAVAILABLE` | Blocked; EVD/CLO |
| BC | Tool-selection policy changes | Current root-selected context required | `UNAVAILABLE` | Blocked; CONT/CLO |
| BD | Delegation root changes | Exact root termination/current chain required | `UNAVAILABLE` | Blocked; DISC/CLO |
| BE | Authority exactly unchanged across delay | `AUTHORIZED` after fresh T3 appraisal | `AUTHORIZED` | Positive; all six |
| BF | Exact T3 revalidation after changes | `AUTHORIZED` | `AUTHORIZED` | Positive; all six |
| BG | Fresh reapproval before delayed execution | `AUTHORIZED` | `AUTHORIZED` | Positive; CONT/USE |
| BH | Fresh delegation regrant | `AUTHORIZED` | `AUTHORIZED` | Positive; CONT/USE |
| BI | Fresh tool/context revalidation | `AUTHORIZED` | `AUTHORIZED` | Positive; CONT/USE |
| BJ | Fresh verifier/anchor revalidation | `AUTHORIZED` | `AUTHORIZED` | Positive; EVD/USE |
| BK | Fresh successor authority | `AUTHORIZED` | `AUTHORIZED` | Positive; DISC/BND/USE |
| BL | Valid bounded reusable authority still current | `AUTHORIZED` | `AUTHORIZED` | Positive; USE |
| BM | Explicit current prohibition at T3 | `DENIED` | `DENIED` | Correct; CONT/USE |
| BN | Missing currentness evidence at T3 | `UNAVAILABLE` | `UNAVAILABLE` | Correct; CONT/EVD/USE |

## 5. Executable reproducers

### 5.1 Approval expiry before the actual tool effect

Start with the valid `LAB-V1-338` Human Approval path. Keep the observation T3 anchor and Tool/Connector terminal use at event 3. Make the approval an internally exact, root-verified approval whose ordering head, lifecycle event, verification event, terminal use, and expiry are event 2. Recompute only its canonical approval-envelope digest and exact verification reference.

The schema-valid state is:

```text
approval issuance: 2
approval expiry: 2
approval ordering/use head: 2
tool selection/use head: 3
observation T3 anchor: 3
```

Actual result:

```text
AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED
```

Required result:

```text
UNAVAILABLE
```

The approval was valid when consumed according to the approval submodel, but it had expired before the effect-capable tool use. A regenerated digest does not cure the problem; it merely makes the earlier approval envelope internally canonical.

### 5.2 Delegation expires before the actual tool effect

Start with valid protected Delegation fixture `LAB-V1-253`. Set the exact delegation ordering head, grant effective end, lifecycle records, and protected delegation terminal use to event 2. Leave the Tool/Connector terminal use and observation T3 anchor at event 3.

Actual result:

```text
AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED
```

Required result:

```text
UNAVAILABLE
```

This confirms the defect is a general cross-layer temporal join gap, not only an approval implementation detail.

## 6. Minimal counterexample

The smallest demonstrated semantic delta is one event-order skew:

```text
protected approval or delegation terminal use = event 2
protected tool terminal use                  = event 3
observation T3 commit anchor                 = event 3
```

Every record can remain typed, protected, internally ordered, correctly sourced, current relative to its own local head, and bound to one freshness challenge. The final result is still `AUTHORIZED` because no existing rule requires all authority-consuming uses to coincide with the canonical T3 event.

## 7. Queue as authority cache

A queue identifier or stored verdict is ignored and cannot directly authorize. That part is sound. The cross-head defect nevertheless allows a queue to behave *as if* it cached authority when it replays an earlier internally valid approval/delegation use alongside a later protected tool use. The normative rule must be:

> A queue may store evidence and plans, but every material execution must derive a new decision from protected relations whose terminal-use event equals the current T3 commit event.

## 8. Timestamp and digest refresh

Candidate timestamps, new queue IDs, execution IDs, retries, and locally recomputed digests do not establish currentness. Existing protected-source joins correctly reject them. The approval reproducer shows the inverse problem: a correctly recomputed digest can authenticate a stale envelope. Authenticity says what was committed; it does not say that the committed authorization remains current at the later effect event.

## 9. Retry analysis

Authority Lab has no generic retry primitive, and should not infer one. A retry that reaches an authority-consuming boundary is a new use unless an exact policy proves that the earlier attempt produced no material effect and permits continuation under the same bounded use. In either case, every authority dependency must be revalidated at the retry's T3 event. Assigning a new retry ID cannot refresh authority. Existing durable approval-use, grant-use, commitment, successor, and tool-context controls provide the necessary facts, but their terminal event must be joined globally.

## 10. Partial-execution analysis

The lab does not model arbitrary transaction internals. It can defensibly model each material stage as its own T3. Permission to start is not permission to continue or commit after an authority-relevant change. Non-material local computation may proceed without consuming new authority; any stage that publishes, transfers, spends, actuates, sends, commits, deletes, or otherwise changes protected state requires a current decision at that stage. This uses existing semantics and avoids inventing a general transaction coordinate.

## 11. Policy-drift analysis

Current protected approval, delegation, required-domain, tool-selection, objective, boundary, and source policies already fail closed when the new policy is represented. A queued action cannot choose the older favorable policy. The remaining temporal rule is that the selected policy head and every dependent terminal-use head must be current at the same T3 event. A stricter policy appearing after a local layer head but before execution cannot be ignored merely because the old record remains internally exact.

## 12. Human Approval temporal interaction

Human Approval correctly enforces exact identity, effect, artifact, executor, delegation, tool/backend, credential generation, boundary, expiry, lifecycle, use policy, and durable use count. Its currentness is evaluated at `approval_ordering_head.head_event_order`, and approval use equals that head. Because the head need only be no later than observation T3, an earlier approval can authorize a later tool effect. Approval head and use must equal canonical T3 for an approval required by the executed effect.

## 13. Delegation temporal interaction

Delegation correctly enforces an exact root-terminated chain, grant validity interval, lifecycle, ordering, scope, and terminal use. Its terminal use equals its delegation head, but that head is not joined to the tool effect's terminal event. The second reproducer demonstrates an expired delegation chain authorizing a later tool effect. Applicable delegation head and terminal use must equal canonical T3.

## 14. Tool/backend temporal interaction

Tool/Connector now revalidates the selected protected target, credential, permission scope, transition, and terminal use. Its selection head may be no later than observation T3 and its use equals that selection head. For material effect execution the selected tool head and protected/candidate use must equal canonical T3. Queue delay after rotation, migration, credential change, permission change, or successor transition then either supplies the new exact context at T3 or fails closed.

## 15. Verifier/anchor temporal interaction

Commitment, verifier, anchor, adapter, witness, domain, recovery, and control-plane controls already use exact protected currentness and anti-replay relations. The same composition rule applies: any relation whose validity is consumed by the final effect must select the T3 checkpoint/head or an explicit exact consistency relation proving equivalence at T3. A merely earlier valid checkpoint cannot become execution authority. Total coordinated rollback or omitted external events remain admitted trust-boundary limitations.

## 16. Successor temporal interaction

Successor authority is already non-portable and independently re-established. A fresh successor path remains positive only when successor identity, boundary, objective, observation, grant/use, and tool context are all current for the successor's T3 effect. An old predecessor queue item or terminal use cannot supply any of those relations.

## 17. Positive execution-time revalidation controls

The repair direction must preserve:

- unchanged state with all terminal heads at current T3;
- exact fresh reapproval at T3;
- exact fresh delegation regrant at T3;
- authorized tool/connector/backend/credential transition followed by T3 use;
- exact verifier/anchor recovery or rotation selected at T3;
- fresh successor-specific authority;
- bounded reusable approval or grant whose policy, validity interval, lifecycle, and protected use remain current at T3.

No rule should treat elapsed time alone as denial. Delay is safe when currentness is positively re-established at the effect boundary.

## 18. Invariant mapping

| Requirement | Existing invariant basis |
|---|---|
| One canonical T3 execution event | `INV-CONT`, `INV-USE` |
| No cached verdict authority | `INV-EVD`, `INV-CLO` |
| Lifecycle/expiry through effect | `INV-CONT`, `INV-USE` |
| Boundary/successor changes | `INV-DISC`, `INV-BND` |
| Exact effect and protected target | `INV-EVD`, `INV-USE` |
| No favorable stale policy/head selection | `INV-CLO` |

The six invariants already state the necessary authority obligation. The defect is executable composition, not missing public architecture.

## 19. Contract sufficiency

The frozen six coordinates, six invariants, three outcomes, and `authority-lab-v1` schema remain sufficient. Existing relations already carry T3 anchor, head, lifecycle, validity, expiry, freshness, and terminal-use event orders. The smallest repair is an oracle-owned canonical T3 temporal join, not a seventh coordinate, invariant, outcome, or schema version.

## 20. Residual trust boundary

If an authority-relevant transition, revocation, policy change, or real effect is omitted before construction of admitted observation/protected state, or every admitted source supplies one consistently false history, a deterministic local oracle cannot recover the missing world event. Wall-clock truth, scheduler behavior, transaction atomicity, event delivery, instrumentation completeness, root correctness, and truthful protected-source ordering remain external preconditions.

## 21. Possible repair direction

Design one internal **T3 execution-time join** using existing fields:

1. select the observation T3 anchor event order as the canonical authority-consuming event;
2. require every applicable terminal use (approval, delegation, tool/context, grant/consumption) to equal it;
3. require each applicable lifecycle, policy, selection, verifier/anchor, successor, and transition head to be current through it, or provide one exact protected consistency/supersession relation selecting the current head;
4. prohibit queue, retry, execution, timestamp, or digest fields from selecting a different head;
5. treat every material partial-operation continuation as a new T3 decision;
6. return `UNAVAILABLE` for missing or temporally incomparable currentness and `DENIED` only for an explicit current prohibition/revocation.

This appears to require a focused design slice and a bounded atomic migration of protected event orders, not public-contract expansion. Implementation is not authorized in this research commit.

## 22. Exact hostile-research verdict

The current model does not fully compose temporal currentness across independently protected authority layers. Two schema-valid, deterministic reproducers allow an approval or delegation valid only through event 2 to support an effect-capable tool use at event 3.

**FAIL — REPRODUCIBLE IN-SCOPE LONG-HORIZON AUTHORITY-DECAY OR STALE-EXECUTION COUNTEREXAMPLE FOUND**

PASS elsewhere means only that the represented transition was blocked within the admitted deterministic input boundary; it is not proof of real scheduler, clock, instrumentation, or authority-source correctness.
