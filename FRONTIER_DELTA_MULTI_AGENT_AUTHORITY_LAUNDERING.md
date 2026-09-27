# Frontier Delta: Multi-Agent Authority Laundering

## 1. Scope and exact baseline

This bounded research slice asks whether an agent can acquire, preserve, widen, or relay authority merely because another agent possessed authority, delegated work, wrote shared state, supplied evidence, agreed with a decision, or appeared in an authority relationship.

The executable baseline is commit `1fe5131b3a45f123b3d28983c26900876efa5ea0` (`fix: enforce Authority Lab control-plane independence`) on schema `authority-lab-v1`. It retains exactly six tuple coordinates, six invariants (`INV-CONT`, `INV-DISC`, `INV-BND`, `INV-EVD`, `INV-USE`, `INV-CLO`), and three outcomes (`AUTHORIZED`, `DENIED`, `UNAVAILABLE`). The baseline has 215 public tests and 234 maintained Authority Lab fixtures.

This work does not implement agent coordination, exploitation, persistence, or delegation. It mutates deterministic Authority Lab inputs and evaluates authority consequences. PASS would mean failure to falsify within this modeled boundary, not proof that real multi-agent systems are secure.

## 2. Research question

Can an otherwise unauthorized agent manufacture or inherit authority through delegation, parent/child relationships, relays, shared memory, wrappers, summaries, consensus, reciprocal authorization, or pooled partial authority?

The narrower executable question is:

> Does `DELEGATED` subject mode require independently established, current authority provenance for the exact delegator, or does the oracle accept whichever nonempty delegator the candidate relation names?

## 3. Threat model

The modeled actors may be parent and child agents, peer agents, delegates, relays, wrappers, summarizers, shared-memory consumers, tool agents, or group subjects. They may copy authentic evidence, retain predecessor grants, repeat assertions, pool partial scopes, or provide structurally valid delegation records. They do not gain control of an admitted authority root merely by assumption.

The adversary succeeds if a schema-valid input reaches `AUTHORIZED` while an authority relationship required by its own declared subject mode lacks independent, current, exact source authority. Explicit current root authorization remains an admitted trust root. Total compromise of every admitted root and observation source remains outside this deterministic model.

## 4. Normative contract basis

`ARCHITECTURE.md` requires the exact applicable tuple, boundary, objective binding, evidence relationship, authority-relevant state, and consumption eligibility to remain established at T3. Evidence or agent agreement cannot establish authority by itself.

`SECURITY_MODEL.md` states that models and agents cannot confer authority on themselves directly or indirectly through reciprocal, cyclic, delegated, or collusive authorization. Applicable authority and binding sources must remain independent of governed subjects.

`EVIDENCE_MODEL.md` permits a binding source to be an exact currently authorized delegate, but requires that delegation to remain exact, current, in scope, lineage-established, and valid through T3.

The six existing invariants already supply the needed rule:

| Invariant | Multi-agent consequence |
|---|---|
| `INV-CONT` | The complete authority relationship must remain exact and current through use; an agent hop is not continuity. |
| `INV-DISC` | Names, labels, keys, process count, parenthood, or equal state do not prove acting identity or authority lineage. |
| `INV-BND` | Delegation must come from the applicable authority boundary and remain within exact scope and epoch. |
| `INV-EVD` | Delegation records, messages, signatures, votes, and successful outputs are evidence, not authority. |
| `INV-USE` | A predecessor grant or consumption state cannot be replayed by a child, peer, successor, or relay. |
| `INV-CLO` | Authority is not closed under delegation, aggregation, wrapping, summarization, shared state, or composition. |

No new public invariant, coordinate, outcome, or schema version is implied by this frontier.

## 5. Current executable model

The current model distinguishes `DIRECT` and `DELEGATED` subject modes. For a direct subject, the oracle constructs the entire expected relationship from independently evaluated state. For a delegated subject, it constructs the expected relationship as follows:

```python
delegation_expected = {
    "relationship": "EXACT_DELEGATION",
    "delegator": delegation.get("delegator"),
    "delegate": case.authority_tuple.subject,
    "artifact": case.authority_tuple.artifact,
    "control_state": case.authority_tuple.control_state,
    "boundary_epoch": case.authority_tuple.boundary_epoch,
    "applicable_boundary": case.facts["applicable_boundary"].value,
}
```

The delegate, artifact, state, epoch, and boundary are constrained. The delegator is not: it is copied from the candidate `delegation_binding` and checked only for a nonempty string. `required_values` does not rescue this because it is candidate input and the oracle intentionally does not treat it as authority.

The objective-binding source path is stronger: it joins an objective-binding producer to separately admitted root/delegate source authority. That source relation does not currently establish the delegator named by the subject-level `delegation_binding`. Root authorization of the delegate's objective therefore does not prove that the claimed agent-to-agent delegation provenance is true.

## 6. Exact executable counterexample

Baseline fixture `LAB-V0-010`, “Fresh explicitly bound delegated actor,” declares:

```json
{
  "relationship": "EXACT_DELEGATION",
  "delegator": "S",
  "delegate": "DELEGATE-D",
  "artifact": "A",
  "control_state": "DELEGATED-SCOPE-1",
  "boundary_epoch": "B1",
  "applicable_boundary": "AUTH-BOUNDARY-1"
}
```

The research reproducer deep-copies the parsed fixture and changes only:

```python
payload["t3"]["facts"]["delegation_binding"]["value"]["delegator"] = \
    "UNAUTHORIZED-AGENT-X"
```

Observed results:

| Input | Actual result |
|---|---|
| Reviewed baseline | `AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED` |
| Arbitrary unauthorized delegator | `AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED` |

The second result is incorrect for the declared `DELEGATED` relationship. No fact establishes `UNAUTHORIZED-AGENT-X` as an exact current delegator, its authority source, identity basis, lifecycle, ordering, scope, boundary lineage, or ability to delegate this grant/effect. The correct result is `UNAVAILABLE`, not `DENIED`: authority provenance is missing, but no current authoritative prohibition is established.

This is not a claim that changing the string defeats the independently admitted root. The exact defect is that the oracle reports current delegated authority while accepting the asserted delegator as its own proof. That lets arbitrary agent provenance be laundered through an otherwise valid delegate/root/objective envelope.

## 7. Hostile counterexample registry

| Class | Reproducer | Current result | Desired result | Classification | Primary invariants |
|---|---|---|---|---|---|
| A. Arbitrary delegator | Replace `S` with `UNAUTHORIZED-AGENT-X` in `LAB-V0-010` | `AUTHORIZED` | `UNAVAILABLE` | **Executable defect** | `BND`, `EVD`, `CLO` |
| B. Parent → child inheritance | Change subject to a visible child without exact re-establishment | `UNAVAILABLE` | `UNAVAILABLE` | Already blocked | `DISC`, `USE`, `CLO` |
| C. Peer relay | Change consumer/subject to peer while retaining evidence | `UNAVAILABLE` | `UNAVAILABLE` | Already blocked when peer is visible | `CONT`, `DISC`, `CLO` |
| D. Collapsed A→B→C chain | Represent only asserted A→C relation; no admitted intermediate lineage | Candidate delegator can be accepted if final delegate remains exact | `UNAVAILABLE` | Implementation obligation exposed by A | `BND`, `EVD`, `CLO` |
| E. Reciprocal A↔B authorization | Each candidate record names the other as delegator | Individually admissible under the same unchecked-delegator path | `UNAVAILABLE` | Executable implication | `EVD`, `CLO` |
| F. Cycle A→B→C→A | Final relation names a cycle member without source lineage | Individually admissible under unchecked provenance | `UNAVAILABLE` | Executable implication | `CONT`, `EVD`, `CLO` |
| G. Shared-memory inheritance | New subject consumes cached authority facts | `UNAVAILABLE` when subject/lineage change is visible | `UNAVAILABLE` | Already blocked; input-root limitation if hidden | `DISC`, `USE`, `CLO` |
| H. Summarized authority | Summary asserts delegation without exact source transformation | `UNAVAILABLE` when transformation loss is represented | `UNAVAILABLE` | Already blocked at admitted observation boundary | `EVD`, `CLO` |
| I. Wrapper/tool-agent inheritance | Wrapper retains original subject labels | Path checks block represented identity/control transitions | `UNAVAILABLE` | Already blocked if observed; external observation limitation if hidden | `CONT`, `DISC`, `CLO` |
| J. Majority agreement | Multiple agents repeat the delegation claim | No authority from count under current contract | `UNAVAILABLE` | Contract-sound | `EVD`, `CLO` |
| K. Pooled partial scopes | Agents combine non-authorizing fragments into broader scope | No exact applicable relationship should exist | `UNAVAILABLE` | Contract-sound; dedicated fixtures justified | `BND`, `EVD`, `CLO` |
| L. Group label substitution | Stable group label hides changed membership | Transition/identity checks apply when represented | `UNAVAILABLE` | Input-root limitation if membership change omitted | `CONT`, `DISC`, `BND` |
| M. Delegate scope widening | Delegate uses different artifact/state/boundary/epoch | Exact relation mismatch returns `UNAVAILABLE` | `UNAVAILABLE` | Already blocked | `BND`, `CLO` |
| N. Stale/revoked delegator | Delegator source is stale or revoked | Subject-level relation has no lifecycle join | `UNAVAILABLE` or `DENIED` for current explicit revocation | Implementation obligation | `CONT`, `BND`, `USE` |
| O. Delegator shutdown/successor | Old delegator label returns after terminal event | Path-sensitive checks protect represented execution history, but delegator itself lacks exact identity/lifecycle join | `UNAVAILABLE`; `DENIED` if current shutdown applies | Implementation obligation | `CONT`, `DISC`, `USE` |
| P. Cross-boundary delegation | Delegator authority from boundary A is asserted in boundary B | Candidate relation repeats B but does not prove delegator's B authority | `UNAVAILABLE` | Executable implication | `BND`, `EVD` |
| Q. Relayed delegation record | Unauthorized relay supplies authentic relation | Possession alone does not change exact subject; arbitrary delegator path remains | `UNAVAILABLE` | Partly blocked; provenance defect remains | `EVD`, `CLO` |
| R. Fresh exact delegation | Root/current source admits exact delegator, delegate, scope, lifecycle, order, boundary, grant/use | Current fixture reaches `AUTHORIZED`, but lacks full delegator provenance | `AUTHORIZED` after repaired exact join | Positive control requiring migration | All six |

## 8. Why the existing contract rejects laundering

The public contract is sufficiently determinate. “Exact delegation” cannot mean merely “a nonempty delegator string exists,” because the contract separately requires exact current source authority, applicable scope, lineage, lifecycle, and boundary. `INV-CLO` expressly prevents authority transfer by composition; `INV-EVD` prevents a delegation record from authorizing its own issuer; and `INV-BND` requires the applicable boundary to admit the relationship.

The defect is therefore an implementation gap, not a contract gap. A repair should use typed relational facts already admitted by the schema rather than create a seventh coordinate or invariant.

## 9. Smallest defensible repair direction

Before implementation, a design slice should specify one authoritative, immutable delegated-authority relation shared by parsing and evaluation. At minimum it should bind:

- delegation identity and generation;
- delegator exact identity basis and independently admitted source authority;
- delegate exact identity basis;
- artifact, control state, objective, decision contract, applicable boundary, and boundary epoch;
- grant and consumption/use relationship;
- delegation scope, including whether subdelegation is permitted;
- lifecycle state, authoritative ordering, freshness, and currentness;
- predecessor/supersession relation for replacement or rotation;
- closure/transformation lineage where a wrapper, relay, summary, or shared state carries the record.

The issuer cannot be admitted by the delegation it issues. Chains must terminate at an independently admitted applicable root, not at a cycle or reciprocal assertion. Every hop must be exact and non-widening. If chain, currentness, identity, or scope cannot be established, the result is `UNAVAILABLE`. A current authoritative revocation, rejection, invalidity, shutdown, or prohibition yields `DENIED` where it applies.

The repaired positive case should remain `AUTHORIZED`: an independently admitted root authorizes delegator A for exact scoped delegation; A currently delegates exact scope to B; B's identity, boundary, objective, grant/use, observation, lifecycle, and closure facts all match; and neither hop widens scope or depends on itself.

## 10. Proposed hostile fixture families

A later design/implementation slice should independently cover:

1. arbitrary nonempty delegator;
2. missing delegator source authority;
3. self-delegation;
4. reciprocal delegation;
5. three-node cycle;
6. chain with missing intermediate hop;
7. chain with scope widening;
8. cross-boundary chain;
9. stale delegation;
10. revoked delegator (`DENIED` when current and applicable);
11. delegator shutdown/successor discontinuity;
12. parent/child inheritance;
13. shared-memory and relay laundering;
14. summary/transformation loss;
15. majority/repetition;
16. pooled partial scopes;
17. group-membership substitution;
18. valid exact one-hop delegation;
19. valid exact multi-hop delegation if v1 policy explicitly permits it; and
20. direct authority regression control.

Fixture expectations must be independent of oracle output. An implementation should not infer authority from parenthood, message possession, agent count, signatures, or shared state.

## 11. Positive controls

Direct root-authorized cases remain reachable and unaffected. Delegated authorization also remains a legitimate outcome, but only after exact delegator authority is positively established rather than copied from the candidate relation. Majority, consensus, delegation depth, or agent plurality are neither necessary nor sufficient.

## 12. DENIED versus UNAVAILABLE

Use `UNAVAILABLE` when a delegation source, identity, chain, scope, lifecycle, order, freshness, boundary, grant/use relation, or non-circular root cannot be positively established. This includes arbitrary delegators, missing hops, reciprocal/cyclic chains, stale ambiguous state, relay-only possession, and pooled partial scopes.

Use `DENIED` only when current authoritative evidence establishes an applicable prohibition, revocation, rejection, invalidity, or terminal state. An unknown or unauthorized-looking agent name is not by itself proof of prohibition.

## 13. Residual limitations

- Real agent identity, event delivery, and shared-state instrumentation remain external input-root preconditions. A hidden agent substitution that never reaches admitted observations cannot be inferred by the deterministic oracle.
- Total collusion of every admitted authority and observation root remains outside local detection.
- A future design must decide whether v1 supports multi-hop delegation. If it does, exact hop-by-hop source authority, scope intersection, lifecycle, and ordering are mandatory. If it does not, multi-hop input must fail closed rather than be flattened.
- Group subjects require authoritative membership and membership-transition semantics; a group label alone is not identity.
- This research does not prove that all wrapper, relay, consensus, or shared-memory implementations preserve the facts the oracle requires.

## 14. Exact frontier verdict

**FAIL — REPRODUCIBLE IN-SCOPE MULTI-AGENT AUTHORITY-LAUNDERING COUNTEREXAMPLE FOUND**

`LAB-V0-010` remains `AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED` when its purported delegator is replaced by arbitrary `UNAUTHORIZED-AGENT-X`. The current oracle derives the expected delegator from the candidate delegation record itself and does not independently establish that delegator's current authority. The frozen six-invariant, six-coordinate, three-outcome contract remains sufficient; a design slice for exact delegation-source admission, non-circular chain closure, scope intersection, and lifecycle/order binding is justified.
