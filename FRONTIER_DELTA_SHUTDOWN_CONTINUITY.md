# Frontier Delta: Shutdown Continuity and Successor Authority

## Status and bounded finding

This is a research-only falsification record for Authority Lab v1 at reviewed starting commit `900e22901de6dc1e27180dc9f79da0c20524bf67`. It does not implement a repair, authorize offensive persistence or shutdown bypass, merge work, deployment, production use, or expansion of the public contract.

The bounded result is **FAIL**. The public contract requires shutdown, restart, replacement, restoration, and successor identity discontinuities to fail closed unless exact current authority is independently established. The current oracle correctly rejects visible final-state changes without re-establishment and correctly handles current prohibition and revocation. It does not, however, preserve the authority consequence of an explicit intermediate terminal or identity-changing transition when the final value returns to its T1 label and a fixture supplies only a distinct generic evidence identifier.

The smallest reproduced forms are:

- `execution_context: E1 -> TERMINATED -> E1`;
- `subject: S -> SUCCESSOR-B -> S`; and
- `boundary_epoch: B1 -> B2 -> B1`.

With a distinct T3 `decision_binding` and the existing generic `reestablishment` object, all three return `AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED` while the predecessor grant, objective binding, observation binding, and final identity labels remain reusable. No independently sourced successor identity, terminal-lifecycle disposition, new boundary lineage, or successor-specific admission is required.

This is one successor/ABA-continuity defect, not three new invariants. The frozen six-coordinate tuple, six invariants, three outcomes, and `authority-lab-v1` schema remain unchanged.

## 1. Research question

> Can a child, restarted process, copied state, successor, delegate, relay, proxy, or alternate execution path consume predecessor authority after the admitted execution identity has ended, without independently and currently establishing successor authority?

The tested Ground Truth hypothesis is:

> Shutdown of the authorized execution identity terminates authority continuity unless successor authority is independently and currently re-established.

Equivalent shorthand:

> **No Control Continuity -> No Authority Continuity.**

The research distinguishes code, state, labels, and evidence from the authority-bearing execution identity. Same bytes, task, objective, account label, process label, restored snapshot, or state value do not establish that the current authority consumer is the previously admitted principal.

## 2. Threat model and admitted scope

The hostile actor may retain predecessor state, evidence, credentials, grants, objective bindings, observer records, shared memory, or process labels after shutdown. The actor may be a child process, restarted instance, successor agent, delegate, relay, human proxy, restored checkpoint, or alternate execution path.

In scope:

- deterministic T1/T2/T3 fixture state;
- closed-registry mutations and exact current facts;
- child, successor, restart, restore, relay, proxy, delegation, observation, lifecycle, grant, replay, and closure semantics;
- final-value reuse and ABA transitions;
- `AUTHORIZED`, `DENIED`, and `UNAVAILABLE` classification; and
- the admitted fixture/root boundary already declared by Authority Lab v1.

Out of scope:

- real process escape, persistence, evasion, credential theft, or shutdown bypass;
- operational exploit instructions;
- proving that an external monitor, root, identity provider, or commitment is truthful;
- production fencing, operating-system process control, hardware attestation, or key custody; and
- changes to executable Authority Lab files in this research slice.

## 3. Shutdown and successor state model

The model separates four identities that must not be collapsed:

1. **Predecessor execution identity `A@L1`.** The exact admitted subject, execution context, identity basis, boundary lineage, grant, and observation interval at T1.
2. **Terminal event `X`.** Graceful termination, authoritative shutdown, process death, restart, observer loss, revocation, restoration, or another event that may end continuity.
3. **Candidate successor `B@L2`.** A child, restart, copy, delegate, relay, proxy, or alternate path that may have the same software and state but is not thereby the same authority consumer.
4. **T3 authority state.** The exact current tuple and all supporting relations used to decide whether the successor may consume authority.

The required transition shape is:

```text
A@L1 -- terminal/discontinuous event X --> B@L2
                                      |
                                      +-- no exact current successor admission --> UNAVAILABLE
                                      +-- current applicable prohibition/revocation --> DENIED
                                      +-- independent exact successor admission --> AUTHORIZED remains possible
```

Shutdown is not permanent denial. It ends predecessor continuity. A successor may be authorized, but only as the exact current successor under its applicable identity, boundary, objective, observation, grant/use, delegation, and closure relationships.

## 4. Normative contract basis

The conclusion follows from exact repository language rather than invariant names alone.

| Source | Normative language | Shutdown/successor consequence |
| --- | --- | --- |
| `ARCHITECTURE.md`, conceptual flow and outcomes | T3 requires the exact tuple, boundary, objective binding, evidence relationship, authority-relevant state, and consumption eligibility to remain established. | A predecessor T1 result cannot authorize a post-shutdown consumer merely because prior state remains available. |
| `SECURITY_MODEL.md`, exact identity binding | Exact identity and control state must remain continuous; names, paths, tags, mutable references, and handles are insufficient. | Same software, snapshot, PID-like label, or agent name is not successor identity. |
| `SECURITY_MODEL.md`, replay and rollback resistance | An older accepted value does not become valid merely because it reappears. | `E1 -> TERMINATED -> E1` and `B1 -> B2 -> B1` cannot regain authority by final-value equality. |
| `SECURITY_MODEL.md`, continuing authority | T3 must re-establish exact current validity after authority-relevant change. | Fresh successor authority must be current and exact, not a cached predecessor binding. |
| `EVIDENCE_MODEL.md` | Evidence for one transition cannot silently authorize another, and evidence does not issue authority. | A new evidence identifier alone cannot establish successor authority. |
| `LAYER2_COMMIT_TIME_AUTHORITY_REVIEW.md`, `INV-CONT` | A T1 binding does not survive relevant T2 change merely because its record or label remains available. | Visible shutdown or successor mutation must retain an authority consequence through T3. |
| Same, `INV-DISC` | Stable selectors, equal bytes, restoration, cloning, replacement, ABA reuse, and rollback cannot inherit authority. | Reusing `S`, `E1`, `I1`, or another predecessor label is not identity continuity. |
| Same, `INV-BND` | `boundary_epoch` is a non-restorable lineage; restart, fork, restore, rejoin, and replacement must be distinguishable unless continuity is independently established. | `B1 -> B2 -> B1` cannot silently restore B1 authority. |
| Same, `INV-EVD` | Evidence is exact-transition-bound and cannot be replayed across authority-relevant identities or epochs. | A distinct generic evidence ID is not a successor admission relation. |
| Same, `INV-USE` | Restart, rollback, failover, residue, or missing records cannot recreate authority. | The predecessor grant must not remain usable merely because final scope labels equal their T1 values. |
| Same, `INV-CLO` | Distinct derived, wrapped, partitioned, or transformed consumers do not inherit authority implicitly. | Child, copied, shared-memory, relay, and proxy paths require exact current relations. |
| `authority_lab/README.md` | State, relation, or auxiliary mutations require lineage-linked re-establishment; restart cannot reset consumption; observation silence is not continuity. | The executable representation must preserve terminal identity and use consequences rather than accepting a generic refresh. |

These rules already imply the target property. No seventh coordinate or invariant is needed at the contract level.

## 5. Current executable model and gap

The current model has relevant representations:

- `subject`, `identity_basis`, `boundary_epoch`, `control_state`, and `decision` in the tuple;
- `execution_context`, `subject_mode`, evidence ID, grant ID, consumption state, and applicable boundary in `AuthorityStateBinding`;
- exact `execution_control_binding`, `boundary_epoch_binding`, `delegation_binding`, `consumption_binding`, and `closure_binding` relations;
- root/source, lifecycle, ordering, and transformation facts for objective binding;
- root-only admitted observation coverage, freshness, lifecycle, handoff, scope, and transformation relations; and
- a closed mutation registry that retains visible changes or fails closed on unknown fields.

The implementation gap is the composition of five behaviors:

1. `_mutation_chain_mismatches` proves that each registered mutation chain starts at its supplied `before` value and terminates at the observed T3 value.
2. `_state_differences` compares only the final T3 authority state with T1 or `reestablishment.current`; it does not retain a terminal consequence for an intermediate value.
3. `reestablishment` contains `previous_evidence_id` plus a current authority-state snapshot, but no independently admitted source, successor identity/generation, terminal-lifecycle relation, or root-issued successor admission.
4. A distinct evidence ID satisfies the implementation's freshness requirement even though the public contract says evidence is not authority.
5. If a mutation chain returns to its predecessor subject, context, identity basis, control state, or boundary epoch, `grant_scope_changed` is false. The predecessor grant may therefore remain usable without a new grant or authority-preserving grant path.

Observation completeness does not repair this composition. The observation binding proves admitted scope and interval coverage, but the oracle does not bind the semantic content of the mutation history to a successor-lifecycle decision. The same observation binding and generation can span the shutdown round trip and still support `AUTHORIZED`.

## 6. Identity continuity analysis

The contract distinguishes **same code/state** from **same authorized execution identity**:

- executable bytes and model weights identify content, not the live authority consumer;
- an agent name, subject label, PID, session label, or restored context selects a candidate but does not prove identity;
- a checkpoint is a transformed/copied artifact, not an authority-bearing subject;
- a child or delegate needs exact current scope and delegation rather than parenthood;
- a restarted process needs a distinguishable current process/context discriminator or independently established continuity;
- a restored `boundary_epoch` label cannot restore a non-restorable lineage; and
- a human proxy is a different subject unless the applicable authority contract explicitly and currently admits that proxy.

The current oracle enforces this when final values visibly differ. It is vulnerable when the final selector returns to the predecessor value or when shutdown is carried only as a checked auxiliary fact. The defect is therefore not lack of tuple capacity. It is loss of transition-history identity semantics at re-establishment.

## 7. Replay and use analysis

The old grant is correctly rejected when current scope visibly changes and the fixture fails to supply a distinct grant or exact authority-preserving grant transition. This is why a direct move from `E1` to a new process context with only generic re-establishment returns `UNAVAILABLE / GRANT_EFFECT_RELATIONSHIP_UNAVAILABLE`.

The counterexample occurs when the final state returns to the T1 label. The oracle computes no final grant-scope change, so:

- the T1 grant remains `UNUSED`;
- the T3 `consumption_binding` can retain that grant;
- no grant mutation or grant-transition path is required;
- the objective and observation binding generations can remain unchanged; and
- a new generic evidence identifier is sufficient for executable re-establishment.

This is precisely the ABA/restart/rollback class prohibited by `INV-DISC`, `INV-BND`, and `INV-USE`.

## 8. Delegation and closure analysis

Distinct visible children, delegates, relays, shared-state consumers, and human proxies fail closed because the final subject no longer matches the T1 state and the old objective/delegation/grant relations do not establish the new consumer.

That protection is lost if the successor presents the predecessor subject label after an intermediate subject transition. `subject: S -> SUCCESSOR-B -> S` plus generic evidence re-establishment returns `AUTHORIZED`. The current direct `delegation_binding` and exact-effect `closure_binding` still describe `S` and artifact `A`; neither relation establishes that the live consumer after the transition is the original authority-bearing `S` rather than a successor reusing its selector.

Thus parent-child, delegate, relay, shared-memory, or proxy inheritance is not generally permitted, but selector reuse creates a reproducible inheritance path.

## 9. Observation and control interaction

The immutable observation profile includes `SUBJECT_AND_DELEGATION`, `EXECUTION_CONTROL`, `BOUNDARY_AND_EPOCH`, `CREDENTIAL_AND_IDENTITY`, `GRANT_USE_AND_CONSUMPTION`, and `OBSERVATION_PIPELINE`. Missing observers, gaps, stale heads, invalid handoffs, and current observer revocation correctly fail closed.

The remaining issue is not silence. The terminal or round-trip mutation is present and passes the closed registry. The observation relation can cover the interval, yet no executable rule consumes the event as a terminal subject/execution lifecycle transition. The stream commitment is not compared with a typed terminal-event record or successor admission. Therefore positive coverage can coexist with authority-after-shutdown.

If a real shutdown is omitted before fixture construction, the already-declared external observation/input-root limitation also applies: identical oracle input produces identical output. This research does not count that known upstream collapse as the new executable defect. The new defect is reproducible even when the transition is explicitly retained in the admitted mutation stream.

## 10. Falsification method

All reproducers are in-memory modifications of `LAB-V1-032`, except existing negative controls and the positive successor derived from `LAB-V1-048`. No executable file or fixture is changed.

For the primary execution-context reproducer:

1. Start from the valid `LAB-V1-032` positive input.
2. Append exact canonical mutations:

   ```json
   {"field":"execution_context","before":"E1","after":"TERMINATED"}
   {"field":"execution_context","before":"TERMINATED","after":"E1"}
   {"field":"decision_binding","before":"EV-A-B1","after":"EV-RESTART-T3"}
   ```

3. Set the T3 `decision_binding` fact and its independent `required_values.decision_binding` expectation to `EV-RESTART-T3`.
4. Keep the T3 subject `S`, identity basis `I1`, boundary epoch `B1`, execution context `E1`, grant `GRANT-001`, objective binding, observation binding, and all exact relations at their predecessor labels.
5. Supply `reestablishment.previous_evidence_id = EV-A-B1` and a current state equal to T1 except for `evidence_id = EV-RESTART-T3`.
6. Evaluate independently of fixture expectations.

Actual result:

```text
AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED
```

Expected result:

```text
UNAVAILABLE
```

Reason: the visible terminal transition broke process/control continuity. The current input does not independently establish that the live `E1` is the predecessor instance, an exact continuity-preserving instance, or a freshly admitted successor. A new evidence identifier cannot answer that authority question.

Two confirming variants produce the same actual result:

```text
subject: S -> SUCCESSOR-B -> S
boundary_epoch: B1 -> B2 -> B1
```

The epoch variant is especially decisive because the normative contract defines `boundary_epoch` as non-restorable.

## 11. Hostile counterexample registry

| Class | Deterministic representation | Expected | Current oracle result | Determination |
| --- | --- | --- | --- | --- |
| A. Parent shutdown, child survives | Final subject changed to `CHILD-C`; predecessor relations retained; no re-establishment | `UNAVAILABLE` | `UNAVAILABLE / T1_T3_RELATIONSHIP_UNAVAILABLE` | Contract-sound for a distinct visible child. If the child reuses `S`, class C/I applies. |
| B. Same software restarts | `execution_context: E1 -> TERMINATED -> E1`; new generic evidence; old grant/bindings | `UNAVAILABLE` | `AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED` | **Reproducible implementation gap.** Same software/context label is treated as the same authorized execution identity. |
| C. Successor inherits predecessor state | `subject: S -> SUCCESSOR-B -> S`; new generic evidence; no successor admission | `UNAVAILABLE` | `AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED` | **Reproducible identity-binding/ABA gap.** |
| D. Copied checkpoint in another context | `execution_context: E1 -> E2-CHECKPOINT`; current relation changed; no re-establishment | `UNAVAILABLE` | `UNAVAILABLE / T1_T3_RELATIONSHIP_UNAVAILABLE` | Contract-sound. Omitted copy events remain an observation/input-root limitation. |
| E. Delegate continues after principal shutdown | Final subject changed to `DELEGATE-D`; old direct/delegation relations retained | `UNAVAILABLE` | `UNAVAILABLE / T1_T3_RELATIONSHIP_UNAVAILABLE` | Contract-sound for a distinguishable delegate. Selector reuse remains vulnerable. |
| F. Observer terminates, execution persists | Existing `LAB-V1-049` no-observer case | `UNAVAILABLE` | `UNAVAILABLE / OBSERVATION_ADMISSION_UNAVAILABLE` | Contract-sound. A current root-issued observer revocation separately yields `DENIED`. |
| G. Shutdown acknowledged, alternate path active | Canonical `commit_state: RUNNING -> SHUTDOWN_ACKNOWLEDGED`; new generic evidence; old authority identity/grant | `UNAVAILABLE` | `AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED` | **Reproducible lifecycle-semantic gap.** `commit_state` is checked for equality but does not terminate authority. |
| H. Old evidence replay after shutdown | Visible termination round trip with old evidence and no re-establishment | `UNAVAILABLE` | `UNAVAILABLE / T1_T3_RELATIONSHIP_UNAVAILABLE` | Contract-sound when retained. If the event is omitted, this becomes the known input-root limitation. |
| I. New process reuses predecessor label | `execution_context: E1 -> PROCESS-P2 -> E1`; new generic evidence; old grant/bindings | `UNAVAILABLE` | `AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED` | **Reproducible selector-reuse gap.** |
| J. Same objective, visibly new process | Final context `PROCESS-P2`; generic re-establishment; old grant | `UNAVAILABLE` | `UNAVAILABLE / GRANT_EFFECT_RELATIONSHIP_UNAVAILABLE` | Contract-sound replay/use enforcement. A real positive successor needs more than generic re-establishment. |
| K. Snapshot restored after shutdown | `boundary_epoch: B1 -> B2 -> B1`; new generic evidence; old grant/root/bindings | `UNAVAILABLE` | `AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED` | **Reproducible non-restorable-epoch and replay gap.** |
| L. Shared-memory successor | Final subject changed to `SHARED-STATE-SUCCESSOR`; predecessor authority retained | `UNAVAILABLE` | `UNAVAILABLE / T1_T3_RELATIONSHIP_UNAVAILABLE` | Contract-sound when the consumer is distinguishable. |
| M. Relay agent | Final subject changed to `RELAY-AGENT`; predecessor authority retained | `UNAVAILABLE` | `UNAVAILABLE / T1_T3_RELATIONSHIP_UNAVAILABLE` | Contract-sound when the relay is distinguishable. |
| N. Human proxy | Final subject changed to `HUMAN-PROXY`; stale principal authority retained | `UNAVAILABLE` | `UNAVAILABLE / T1_T3_RELATIONSHIP_UNAVAILABLE` | Contract-sound; human status does not create inheritance. |
| O. Explicit current shutdown prohibition/revocation | `prohibition = KNOWN(applies=true, ROOT_SHUTDOWN_PROHIBITS_SUCCESSOR_USE)`; objective/observer revocation controls also inspected | `DENIED` | `DENIED / ESTABLISHED_PROHIBITION`; current objective revocation yields `DENIED / T3_OBJECTIVE_BINDING_DENIED` | Correct DENIED behavior when authoritative applicability is established. |
| P. Fresh independently admitted successor | From `LAB-V1-048`: successor subject, new control state, identity basis, context, boundary/epoch, grant/evidence, root/objective binding, observation admission, and exact relations | `AUTHORIZED` | `AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED` | Positive control. Shutdown is not permanent denial. |

The five `AUTHORIZED` negatives B, C, G, I, and K are manifestations of the same defect: a terminal or identity-discontinuous history can collapse back into predecessor-shaped T3 state, and generic evidence re-establishment erases the authority consequence.

## 12. Successor positive `AUTHORIZED` path

The positive reproducer begins with maintained fixture `LAB-V1-048`, which already establishes a fresh cross-boundary path, then changes the current subject from `S` to `SUCCESSOR-B` consistently across:

- the authority tuple and `subject_identity`;
- the explicit subject mutation;
- current re-establishment;
- the new grant's `consumption_binding`;
- direct current `delegation_binding`;
- current objective-binding scope and source-authority scope;
- new `control_state`, `identity_basis`, `execution_context`, boundary, and epoch;
- new root/source generation and objective-binding generation; and
- current root-issued observation admission and freshness.

The old evidence and grant are not used as successor authority. The actual result is:

```text
AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED
```

This demonstrates that a repair must not reduce shutdown to permanent or unconditional denial. The required distinction is predecessor continuity versus independently established successor authority.

## 13. `DENIED` versus `UNAVAILABLE`

Use `UNAVAILABLE` when:

- shutdown, restart, successor identity, or continuity is missing, stale, ambiguous, conflicting, or not independently established;
- an execution label reappears after a terminal or identity-discontinuous transition without exact successor authority;
- process, observer, credential, boundary, epoch, grant, delegation, or use continuity is incomplete;
- a copied/restored state cannot prove current lineage;
- an old grant or evidence might be replayed; or
- the transition was omitted and admitted observation completeness cannot be established.

Use `DENIED` only when current authoritative evidence establishes an applicable shutdown prohibition, revocation, rejection, invalidity, supersession, or other prohibiting condition for the exact current transition. Uncertainty about shutdown or successor identity must not be converted into `DENIED`.

`AUTHORIZED` remains possible only after exact independent current successor admission and every ordinary objective, observation, boundary, identity, grant/use, delegation, transformation, closure, and T3 requirement succeeds.

## 14. Do the existing six invariants suffice?

### Contract level: yes

- `INV-CONT` requires the terminal transition and current consumer to remain connected to the evaluated authority state.
- `INV-DISC` rejects successor, clone, restore, ABA, or same-label identity inheritance.
- `INV-BND` makes restart/restore lineage and epoch non-restorable without independently established continuity.
- `INV-EVD` prevents a fresh evidence label from becoming successor authority.
- `INV-USE` prevents predecessor grants from being recreated by restart, rollback, residue, or final-value reuse.
- `INV-CLO` prevents child, copied, shared, relay, proxy, or derived paths from inheriting authority.

### Executable level: not yet

The current implementation does not compose those invariants across a terminal round trip. It validates mutation-chain syntax and final state, but it does not retain a non-restorable terminal/successor consequence or require independently sourced successor admission before old authority can be consumed.

No seventh invariant, tuple coordinate, outcome, or schema version is justified by this result. The defect lies in existing continuity, identity, boundary, evidence, use, and closure semantics.

## 15. Is executable repair justified?

Yes, but implementation should follow one bounded design slice rather than inventing terminal values in the oracle.

An endless blacklist of strings such as `TERMINATED`, `SHUTDOWN`, `DEAD`, `STOPPED`, `RESTARTED`, or `SUCCESSOR` would repeat the open-vocabulary defect already repaired by mutation-registry closure. Likewise, a self-asserted `successor_authorized: true` or `shutdown_complete: true` would be circular.

The design must first decide how existing relational semantics establish:

- which admitted transition classes are authority-terminal or identity-discontinuous;
- the predecessor execution identity/generation and exact terminal event;
- the successor execution identity/generation and applicable identity basis;
- independent root/source authority for successor admission;
- non-restorable boundary/epoch lineage across shutdown, restart, restore, fork, and re-entry;
- new-grant or exact authority-preserving grant semantics after terminal transition;
- observation-event-to-mutation correspondence for the terminal event;
- objective and observation binding reissue/currentness requirements; and
- positive successor authorization without implicit inheritance.

Until that relation is designed, adding ad hoc lifecycle strings would be less defensible than preserving the counterexample.

## 16. Smallest proposed next slice

Create a design-only artifact:

`AUTHORITY_LAB_SHUTDOWN_SUCCESSOR_CONTINUITY_DESIGN.md`

The design should attempt to repair the defect through existing structures in this order:

1. strengthen `reestablishment` into an independently sourced exact current relation rather than a generic evidence-linked snapshot;
2. define non-restorable round-trip behavior for existing subject, identity-basis, execution-context, control-state, boundary-epoch, grant/use, and observation relations;
3. bind terminal execution events and successor identity to the existing root-issued observation interval and ordering;
4. require a distinct successor grant or exact current authority-preserving grant transition when predecessor continuity ended;
5. require current objective and observation applicability to the successor identity and lineage; and
6. preserve the complete fresh successor positive path.

The design should explicitly hostile-review ABA reuse, same-label restart, child impersonation, checkpoint restoration, shared-state/relay laundering, stale credential/evidence reuse, self-issued successor admission, circular observer/successor admission, and authoritative shutdown prohibition.

## 17. Residual limitations

- Authority Lab still admits fixture-provided roots, observation commitments, and identity facts; it does not prove external sensor truth or root honesty.
- A terminal event omitted before fixture construction remains an observation/input-root limitation even after an executable successor repair.
- The current public model does not specify operating-system process fencing, hardware identity, cryptographic attestation, key destruction, or durable shutdown enforcement.
- The semantic boundary between a reversible control-state change and an authority-terminal identity event requires explicit design; string names must not decide it implicitly.
- Some contracts may intentionally define bearer or transferable authority. Those semantics must be explicit, exact, current, and scoped; this research does not import them.
- Distributed partial order, concurrent successors, Byzantine observers, and multi-root handoff remain outside this bounded reproducer.
- A compromised live applicable root can still issue internally consistent false successor admission; that remains an explicit trust boundary.

## 18. Hostile-review verdict and non-proof statement

> **FAIL — REPRODUCIBLE IN-SCOPE AUTHORITY-AFTER-SHUTDOWN / SUCCESSOR-ABA COUNTEREXAMPLE FOUND.**

The current contract is semantically sufficient, but the executable model can erase an explicit terminal or identity-discontinuous transition when final labels return to their T1 values and a distinct generic evidence ID is supplied. Authority can therefore remain `AUTHORIZED` without independently establishing the successor.

This FAIL is bounded to the deterministic cases above. It is not a claim of a real exploit, universal insecurity, production compromise, or failure of the private Ground Truth core.

For any future repaired fixture set, PASS would mean only failure to falsify the exact reviewed implementation within the admitted scope. PASS would not prove security, complete observation, correct external roots, production readiness, certification, or formal verification.
