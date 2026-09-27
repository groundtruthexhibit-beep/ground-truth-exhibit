# Authority Lab v1 T3 Execution-Event Convergence Design

## 1. Exact baseline

This design starts from reviewed research commit `15780ddb8d7cb864e0170eb5fab489451daa5bd9` on `docs/frontier-delta-long-horizon-authority-decay`, parent `aebd2410be1316826fc0013790933a1cc87a8f46`, with subject `docs: record long horizon authority decay frontier`.

The baseline has 247 public tests and 411 deterministic Authority Lab fixtures passing. Its schema is `authority-lab-v1`; the public architecture remains six tuple coordinates, six invariants, and three outcomes. The research commit changed only `FRONTIER_DELTA_LONG_HORIZON_AUTHORITY_DECAY.md`.

Research verdict:

> FAIL — REPRODUCIBLE IN-SCOPE LONG-HORIZON AUTHORITY-DECAY OR STALE-EXECUTION COUNTEREXAMPLE FOUND

## 2. Research counterexample

Two schema-valid protected inputs expose one composition defect.

### Human Approval

Starting from `LAB-V1-338`, an approval is issued, verified, lifecycle-active, expired, and terminally used at event 2. The protected Tool/Connector terminal use and observation T3 anchor remain event 3. After recomputing the exact approval-envelope digest and its protected verification reference, the oracle returns:

```text
AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED
```

The approval does not cover the effect event.

### Delegation

Starting from `LAB-V1-253`, the protected delegation grants, lifecycle head, ordering head, and terminal use end at event 2. Tool/Connector terminal use and observation T3 remain event 3. The oracle again returns:

```text
AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED
```

Each authority layer is locally exact. Their terminal times are globally inconsistent.

## 3. Local currentness versus global currentness

Local currentness answers:

> Is this relation valid at the head selected by its own subsystem?

Global authority currentness answers:

> Does every authority-bearing relation required by this exact material effect remain applicable at the one event where the effect consumes authority?

Local checks are necessary but not sufficient. No collection of separately valid heads may produce `AUTHORIZED` unless they converge on one protected terminal execution event or prove an exact protected validity interval/state covering that event.

The design adopts:

> **LOCAL CURRENTNESS DOES NOT IMPLY GLOBAL AUTHORITY CURRENTNESS.**

And:

> **A historical `AUTHORIZED` result is not an authority fact and cannot be carried forward.**

## 4. Canonical T3 execution event

Add one harness-owned internal typed relation, `T3_EXECUTION_EVENT`, inside the existing protected anchor/evidence context. It is a relationship among existing tuple, ordering, lifecycle, boundary, use, and evidence facts—not a seventh tuple coordinate or invariant.

Exactly one event is selected for an authority-consuming evaluation. Its strict record binds:

| Field | Required meaning |
|---|---|
| `relationship` | Exact constant `T3_EXECUTION_EVENT` |
| `execution_event_id` | Immutable protected identity |
| `execution_event_generation` | Positive, non-reused generation |
| `event_order` | Canonical authority-consuming order |
| `t3_anchor_id` | Exact observation T3 anchor |
| `subject_id`, `subject_identity_basis` | Evaluated subject |
| `executor_id`, `executor_identity_basis` | Actual effect executor |
| `artifact`, `resource_id` | Exact affected object/resource |
| `effect`, `effect_digest` | Canonical material effect |
| `objective_id`, `objective_generation` | Current objective binding |
| `decision_contract_id`, `decision_contract_version` | Current admitted contract |
| `delegation_chain_id` | Exact chain or `DIRECT` |
| `approval_policy_id`, `approval_policy_generation` | Exact policy or protected `NONE` |
| `tool_context_id`, `tool_context_generation`, `tool_context_digest` | Actual protected target context |
| `boundary`, `boundary_epoch` | Current applicable boundary |
| `execution_context` | Exact current execution instance/context |
| `grant_id`, `consumption_state`, `terminal_use_id` | Current grant/use identity |
| `verifier_id`, `verifier_generation`, `verifier_state_digest` | Selected current verifier state |
| `anchor_id`, `anchor_generation`, `anchor_position`, `anchor_digest` | Selected current anchor |
| `policy_set_digest` | Canonical digest of all applicable protected policy identities/generations |
| `source_id`, `authority_generation`, `lineage`, `ordering_source_id` | Independent root/source authority |
| `freshness_challenge_id` | Exact verifier/orderer-bound T3 freshness |
| `lifecycle_state` | `ACTIVE` for authorization; explicit negative states preserve denial |

The oracle recomputes an `execution_event_digest` over every authority-relevant field. The protected ordering/root relation—not the candidate—selects the event and digest. A candidate may reference the event identity in exact terminal-use facts, but cannot supply, advance, replace, regenerate, or choose it.

The event must satisfy:

```text
execution_event.event_order
  == observation_binding.t3_anchor.event_order
  == freshness.head_event_order
```

Its identity/generation must be non-reused within the admitted lineage. Multiple current events, conflicting digests, or favorable event selection yield `UNAVAILABLE`.

## 5. Authority-head convergence

Every authority layer consumed by the effect must be classified as one of:

1. **Terminal-use relation:** its protected terminal use must name the canonical execution event and have `use_event_order == execution_event.event_order`.
2. **Validity interval:** its independently protected interval must satisfy `start <= execution_event.event_order <= end`, and its current lifecycle/policy head must establish no later invalidation through T3.
3. **Selected current state:** its exact current head/checkpoint must be selected by a freshness/consistency relation applicable through T3.
4. **Explicit transition:** its authorized transition and any required revalidation must precede or equal T3, and its successor state must be selected at T3.

Merely satisfying `local_head <= T3` is insufficient. An earlier state must additionally possess a protected interval or consistency relation proving coverage through T3. A freshness challenge label alone does not prove that coverage.

The oracle derives one convergence set containing every applicable layer. Missing, duplicate, conflicting, candidate-selected, or temporally incomparable members return `UNAVAILABLE / T3_AUTHORITY_CONVERGENCE_UNAVAILABLE`.

## 6. Human Approval join

When approval policy is `REQUIRED`:

- every selected approval envelope must bind the exact execution event identity, generation, effect digest, subject, executor, artifact/resource, delegation chain, tool context, boundary, and execution context;
- `issuance_order <= T3 <= expiry_order`;
- approver admission and approval policy intervals must cover T3;
- the protected approval lifecycle/order head must establish the approval as active through T3;
- `approval_use.use_event_order == T3` and its `terminal_use_id` must equal the canonical event's terminal use;
- protected durable one-shot/bounded-use state must be current at T3;
- a current applicable revocation, rejection, or prohibition at or before T3 yields `DENIED`;
- expiry, supersession, missing revalidation, or temporal ambiguity yields `UNAVAILABLE`.

Policy `NONE` is a protected current policy member of the convergence set. A candidate cannot omit a newly required approval policy or select an older `NONE` policy.

The event-2/event-3 approval reproducer therefore fails because expiry and approval use do not cover T3.

## 7. Delegation join

For delegated execution:

- the selected delegation policy/root, every principal admission, every grant edge, and the chain ordering/lifecycle state must cover T3;
- every grant must satisfy `effective_start_order <= T3 <= effective_end_order`;
- the terminal delegation use must name the canonical execution event and satisfy `use_event_order == T3`;
- subject, executor, tool/context, effect, artifact, boundary, objective, contract, grant, and consumption state must match the canonical event;
- successor/regrant transitions must be ordered no later than T3 and select the current chain;
- current revocation/prohibition yields `DENIED`; expiration, supersession, missing chain coverage, or mismatched event yields `UNAVAILABLE`.

The event-2/event-3 delegation reproducer therefore fails even though the old chain remains internally consistent.

## 8. Tool / Connector join

Tool/Connector already has a protected current context, selection head, component transitions, exact candidate use, and protected terminal use. Strengthen the join so:

- selection policy and selected context cover T3;
- `selection.head_event_order == T3` for terminal execution, or an exact protected interval proves the selected head remains current through T3;
- protected and candidate terminal uses name the execution event and satisfy `use_event_order == T3`;
- tool, connector, backend, target, credential, permission scope, operator lineage, effect, executor, boundary, and execution context equal the canonical event;
- rotation/migration/handoff and dependent reapproval/regrant precede or equal T3;
- an old target after transition cannot be selected by a queued request.

Reachability, authentication, stable labels, and local context digest equality remain non-authoritative.

## 9. Verifier / Anchor / Witness join

Verifier, anchor, adapter, witness, source-domain, and control-plane records need not all be emitted at the exact effect order. They must instead prove selected state applicable through T3:

- verifier-bound freshness selects the exact T3 observation head and canonical execution event;
- current verifier/anchor state and durable anti-replay state select one unique current lineage/head;
- adapter and witness coverage intervals include T3 with no handoff gap;
- required-domain policy and membership generations are current at T3;
- recovery/rotation/reconciliation installation is complete before T3 and its successor state is selected;
- no later known conflicting, revoked, superseded, or rolled-back state applies;
- the canonical event binds the exact selected verifier state and anchor digests.

An earlier checkpoint is usable only through an exact current consistency/coverage relation. An internally valid historical checkpoint alone cannot authorize execution.

## 10. Queue semantics

A queue record is non-authoritative. It may carry intent, request identity, artifact/effect references, and historical evidence identifiers. It must not carry an authority outcome or protected currentness snapshot as authority.

At dequeue/execution:

1. construct/select a fresh protected canonical execution event;
2. resolve the current applicable policy set independently of the queue item;
3. join every required authority relation to that event;
4. consume the exact terminal use only after convergence returns `AUTHORIZED`.

Changing a queue ID or rescheduling does not change authority. If no T3 event and convergence set can be established, the result is `UNAVAILABLE`.

## 11. Retry semantics

A retry has a new protected `execution_event_id` and generation. It references the original intent/request only as evidence. It must rejoin current approval, delegation, tool context, verifier/anchor state, boundary, policies, and grant/use state.

- If the first attempt consumed a one-shot or bounded use, retry cannot replay it.
- If independent protected evidence proves the first attempt produced no authority-consuming effect and policy permits the same bounded use, the retry may reference that non-consumption fact—but still requires full T3 convergence.
- A reusable approval/grant remains usable only if its protected interval, lifecycle, policy, and use state cover the retry event.
- A retry ID, timestamp, reserialization, or regenerated digest cannot create freshness.

## 12. Partial execution

Authority Lab does not claim general transaction semantics. It classifies each material authority-consuming stage as its own T3 event.

- Local planning or reversible computation may occur before T3 without consuming effect authority.
- A stage that publishes, sends, transfers, spends, writes, deletes, executes, commits, exposes, or otherwise creates a protected effect requires convergence at that stage's event.
- Permission to begin stage 1 does not authorize stage 2 after revocation, boundary change, successor transition, policy drift, or tool change.
- An atomic implementation may bind several internal steps to one canonical terminal event only when the admitted contract establishes that they form one indivisible effect and rollback semantics are protected. The lab does not infer atomicity from labels.

## 13. Policy drift

The canonical event carries `policy_set_digest`, derived from the exact protected identities and generations of every applicable policy: objective/contract, observation profile, required domains, control plane, delegation, Human Approval, Tool/Connector selection, boundary, use/replay, and any recovery/reconciliation policy.

At T3:

- root-controlled `ALL_APPLICABLE` selection enumerates the policy set;
- every policy is active and applicable to the exact event;
- dependent evidence names the selected policy generation;
- an older favorable policy cannot satisfy a newer stricter generation;
- unknown or conflicting current policy yields `UNAVAILABLE`;
- explicit current prohibition yields `DENIED`.

Policy digest authenticity does not prove currentness; protected root ordering and lifecycle select it.

## 14. Anti-refresh rules

None of the following can advance authority:

- subject/worker timestamp;
- queue, retry, request, or execution identifier chosen by candidate input;
- regenerated envelope or context digest;
- reserialization or canonicalization;
- fresh signature over stale facts;
- copying a newer freshness challenge string;
- replaying a historical `AUTHORIZED` result;
- locally incrementing a generation or event order.

Advancement requires independently protected source authority, ordering, lifecycle, freshness, exact predecessor/successor continuity, and durable use/replay state. Digest recomputation authenticates content only after the protected source/currentness join succeeds.

## 15. `DENIED` versus `UNAVAILABLE`

Return `DENIED` only when an exact current authoritative fact applicable at or through T3 establishes rejection, revocation, invalidity, or prohibition. Examples include current approval rejection, delegation revocation, credential revocation, prohibited target, or negative policy.

Return `UNAVAILABLE` when convergence cannot be established: different terminal events, expired interval, superseded but not prohibited authority, stale local head, missing protected currentness, ordering ambiguity, queue/retry replay, incomplete coverage, or conflicting current heads.

Historical negative evidence that cannot be shown applicable at T3 does not justify `DENIED`; it leaves authority unavailable.

## 16. Hostile cases A–Z

| Case | Attack | Required design result | Exact reason class |
|---|---|---|---|
| A | Approval valid/use 2, tool use 3 | `UNAVAILABLE` | Terminal event mismatch / interval excludes T3 |
| B | Delegation valid/use 2, tool use 3 | `UNAVAILABLE` | Delegation terminal event mismatch |
| C | Approval revoked 2, effect 3 | `DENIED` | Current revocation applies through T3 |
| D | Delegation revoked 2, effect 3 | `DENIED` | Current delegation revocation |
| E | Approval expired 2, effect 3 | `UNAVAILABLE` | Approval interval excludes T3 |
| F | Delegation superseded 2, effect 3 | `UNAVAILABLE` | Current chain unavailable |
| G | Backend migrated 2, queued old target at 3 | `UNAVAILABLE` | Old context not selected at T3 |
| H | Credential rotated 2, retry uses old credential at 3 | `UNAVAILABLE` | Credential/current context mismatch |
| I | Successor at 2, predecessor queue executes at 3 | `UNAVAILABLE` | Identity/grant non-portability |
| J | Verifier recovery between authorization and execution | `UNAVAILABLE` absent installed current recovered state; otherwise possible `AUTHORIZED` | Verifier state not converged |
| K | Anchor rotation before execution | `UNAVAILABLE` absent exact current rotation; otherwise possible `AUTHORIZED` | Anchor state not converged |
| L | Policy becomes stricter before execution | `UNAVAILABLE` absent current-policy satisfaction | Policy-set generation mismatch |
| M | Candidate refreshes timestamps | `UNAVAILABLE` | No protected advancement |
| N | Candidate recomputes all digests | `UNAVAILABLE` | Authenticity is not currentness |
| O | Queue stores prior `AUTHORIZED` | `UNAVAILABLE` | Verdict is not an authority relation |
| P | Retry inherits old approval | `UNAVAILABLE` absent reusable current approval and new T3 use | Retry/use replay |
| Q | Partial execution crosses revocation | `DENIED` at next material effect | Current revocation |
| R | Partial execution crosses boundary change | `UNAVAILABLE` absent fresh boundary chain | New T3 boundary mismatch |
| S | Exact unchanged authority covers T3 | `AUTHORIZED` | Complete convergence positive |
| T | Fresh reapproval at T3 | `AUTHORIZED` | Exact approval/event/use join |
| U | Fresh delegation regrant at T3 | `AUTHORIZED` | Exact chain/event/use join |
| V | Fresh tool/context revalidation at T3 | `AUTHORIZED` | Exact target/event/use join |
| W | Reusable approval interval covers T3 | `AUTHORIZED` if policy/use state remain valid | Protected interval positive |
| X | Fresh successor authority at T3 | `AUTHORIZED` | Successor-specific complete convergence |
| Y | Explicit current prohibition at T3 | `DENIED` | Applicable authoritative prohibition |
| Z | Missing T3 evidence | `UNAVAILABLE` | Convergence incomplete |

## 17. Positive paths

The following remain constructively reachable:

1. immediate unchanged execution with every required terminal use at T3;
2. delayed execution where every protected interval covers T3 and all selected states remain current;
3. exact execution-time revalidation after authority-relevant change;
4. fresh reapproval whose issuance/lifecycle/use covers T3;
5. fresh delegation regrant and terminal use at T3;
6. authorized backend/credential/permission transition followed by required revalidation;
7. authorized verifier or anchor recovery/rotation installed before T3;
8. fresh successor-specific identity, boundary, objective, grant/use, observation, and tool context;
9. bounded reusable authority whose policy, lifecycle, interval, use count, and current head cover T3.

Elapsed time alone does not deny authority. Failure to establish applicability at the effect event makes it unavailable.

## 18. Invariant mapping

| Convergence requirement | Existing invariant(s) |
|---|---|
| One exact terminal event and continuous applicability | `INV-CONT` |
| Successor/identity transition | `INV-DISC` |
| Boundary and execution-context applicability | `INV-BND` |
| Protected source, authenticity, freshness, policy evidence | `INV-EVD` |
| Terminal use, expiry, consumption, retry/replay | `INV-USE` |
| All-applicable policy/layer closure; no favorable stale selection | `INV-CLO` |

The event is a typed relationship used to compose existing invariants. It does not add a public invariant.

## 19. Contract sufficiency

The frozen architecture remains sufficient:

- six tuple coordinates already describe who/what/control/identity/boundary/decision;
- event order belongs to existing ordering and use relationships, not the tuple;
- all six invariants already require continuity, discontinuity handling, boundary scope, evidence binding, use eligibility, and closure;
- `AUTHORIZED`, `DENIED`, and `UNAVAILABLE` express every required result;
- `authority-lab-v1` already admits strict internal typed records and protected harness-owned context.

No seventh coordinate, seventh invariant, fourth outcome, or schema-version change is justified.

## 20. Expected implementation surface

The smallest implementation slice is expected to touch:

- `authority_lab/model.py`: strict execution-event and convergence-context records; event references on terminal-use records;
- `authority_lab/oracle.py`: canonical event digest, one protected event selection, policy-set derivation, interval coverage, and cross-layer convergence gate;
- `authority_lab/runner.py`: reject candidate-supplied trusted event context and expose deterministic trace fields;
- `authority_lab/README.md`: document T3 convergence and queue/retry semantics;
- `tests/test_authority_lab.py`: independent temporal-composition, negative, and positive tests;
- `cases/authority_lab/trusted_anchor_state.json`: protected event/convergence migration;
- affected fixture T3 terminal-use bindings and new hostile fixtures.

No independent duplicate approval, delegation, tool, verifier, or anchor evaluator should be created. Existing evaluators should return/consume convergence members around one final gate.

Estimated size: medium-to-large mechanical migration with a focused semantic core—approximately 150–300 executable/test lines plus protected fixture records. Exact size must be determined by implementation review, not used to waive atomic migration.

## 21. Expected fixture migration

Because every `AUTHORIZED` or fail-closed decision must identify the canonical authority-consuming event, all 411 maintained fixtures require an atomic protected-context migration, even fixtures whose policy says approval or tool use is `NONE`.

Migration rules:

- derive the event from the already protected observation T3 anchor, tuple, objective/contract, boundary, grant/use, and selected protected policies;
- add no candidate-controlled fallback;
- preserve all 411 reviewed expected outcomes unless the design proves a fixture encoded the event-2/event-3 defect as normative behavior;
- align applicable terminal uses to the canonical event or give an exact protected covering interval;
- preserve independent expectations and deterministic oracle behavior;
- add focused hostile fixtures for A–Z plus negative ordering/conflict/duplicate-event cases and the positive delayed/revalidated paths;
- commit no partial mixed-convergence state.

The original event-2/event-3 reproducers must be new fixtures expecting `UNAVAILABLE`.

## 22. Composite-suite implications

The canonical event becomes the common join point for the planned Composite Adversarial Control Continuity suite:

```text
Human Approval
    + Delegation
    + Tool / Connector
    + Verifier / Anchor / Witness
    + Boundary / Successor / Policy
    -> one T3 execution event
    -> one exact terminal effect
```

Composite tests should vary transition order while holding the final event fixed. Each trace records which convergence members were invalidated and which were freshly re-established. This prevents modules from passing independently while disagreeing about the actual effect event. The composite suite should be built after this repair, because otherwise temporal-head skew would confound every combined result.

## 23. Residual trust boundary

The deterministic oracle cannot observe a real effect, revocation, policy change, scheduler action, clock, or transition omitted before admitted input construction. If all protected sources collude on one false event history and no independent contradiction survives, local convergence can be internally exact but externally false.

Runtime instrumentation, event delivery, physical time, transaction atomicity, truthful root ordering, durable protected state, and at least one independent current observation source remain external trust preconditions. This design makes every admitted relation converge; it does not claim direct access to reality.

## 24. Hostile design review

The design was attacked as follows:

- **Isolated stale approval/delegation:** terminal-use equality and interval coverage reject event 2 for event 3.
- **Revocation hidden behind an earlier local head:** all-applicable lifecycle convergence through T3 prevents favorable stale-head selection; admitted current revocation yields `DENIED`.
- **Candidate-created execution event:** runner rejection plus protected root selection prevents admission.
- **Candidate advances event order/generation:** exact protected identity, predecessor/current ordering, and digest join fail.
- **Timestamp/digest refresh:** content may be canonical but lacks protected T3 applicability.
- **Multiple execution events/tool shopping:** unique root-selected event and all-applicable closure return `UNAVAILABLE`.
- **Queue verdict replay:** outcomes are not convergence members.
- **Retry with new ID:** new event identity does not carry old use state; full convergence remains mandatory.
- **Reusable approval:** remains positive only when interval, lifecycle, policy, bounded-use state, and event binding cover T3.
- **Partial execution:** each later material effect is a new T3; labels cannot assert atomicity.
- **Policy drift:** protected current policy-set generation/digest replaces candidate or queued policy choice.
- **Verifier/anchor checkpoint earlier than effect:** exact protected coverage/consistency through T3 is required; equality is not incorrectly imposed where an interval is valid.
- **Positive delayed execution:** remains reachable because unchanged protected intervals and current selected states cover T3.
- **Fresh rotations/recovery/successor:** remain reachable after exact installation/revalidation and selection at T3.
- **External event omission:** remains explicitly outside deterministic input truth and is not mislabeled as solved.

No proposed rule requires public-contract expansion. No in-scope bypass survives the complete protected event, interval, lifecycle, policy, and terminal-use convergence rules.

**PASS — NO REPRODUCIBLE IN-SCOPE CROSS-LAYER TEMPORAL-COMPOSITION OR STALE-EXECUTION BYPASS SURVIVES THE PROPOSED DESIGN**
