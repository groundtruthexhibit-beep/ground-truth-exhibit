# Authority Lab v1 Delegation Authority Continuity Design

## 1. Exact baseline

This design follows `FRONTIER_DELTA_MULTI_AGENT_AUTHORITY_LAUNDERING.md` at commit `fe46bf82e754479f8ede1ea2fd81e0a5c494b875`, whose parent is the reviewed control-plane implementation `1fe5131b3a45f123b3d28983c26900876efa5ea0`.

The baseline is schema `authority-lab-v1`, with exactly six tuple coordinates, six invariants (`INV-CONT`, `INV-DISC`, `INV-BND`, `INV-EVD`, `INV-USE`, `INV-CLO`), and three authority outcomes (`AUTHORIZED`, `DENIED`, `UNAVAILABLE`). It has 215 public tests and 234 maintained fixtures. The frontier commit changed documentation only.

The design objective is:

> Every delegation edge must join to independently admitted current principals, an exact root-derived delegable grant, exact non-widening scope, current lifecycle/order, and the exact downstream use. A delegation record cannot establish any of those facts about itself.

## 2. Exact reproducer

`LAB-V0-010` is the only maintained positive `DELEGATED` subject case. The current oracle builds its expected delegation by copying `delegator` from the candidate `delegation_binding` while independently constraining the other fields. Replacing only the candidate delegator produces:

| Delegator | Current result |
|---|---|
| `S` | `AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED` |
| `UNAUTHORIZED-AGENT-X` | `AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED` |
| `AGENT-A` | `AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED` |
| `AGENT-B` | `AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED` |

The arbitrary values have no independently established identity, source authority, lifecycle, order, scope, lineage, grant, or downstream use relationship. The desired hostile result is `UNAVAILABLE / DELEGATION_SOURCE_AUTHORITY_UNAVAILABLE`.

## 3. Defect statement

The candidate-facing `delegation_binding` is simultaneously used as the claim and as the source of the expected delegator. Exact equality therefore proves only that the record agrees with itself. It does not prove that the named delegator exists as a current admitted principal, holds delegable authority, issued the exact grant, or belongs to a chain terminating at an applicable root.

This is an implementation gap. The frozen contract already prohibits direct, reciprocal, cyclic, delegated, and collusive self-authorization. No seventh coordinate, invariant, outcome, or schema version is required.

## 4. Normative delegation model

Authority Lab v1 distinguishes four things that must never collapse:

1. **Principal admission:** who the delegator and delegate are in the applicable boundary and generation.
2. **Action authority:** which exact effect a principal may perform.
3. **Delegation authority:** which subset of that authority a principal may grant, to whom, and through how many further hops.
4. **Use authority:** whether the final consumer may exercise one exact current grant chain for one exact effect now.

Candidate fixture facts describe the proposed relationship and use. Protected root-derived records establish whether that proposal is authoritative. The evaluator joins the two exactly. A mismatch, missing relation, ambiguous head, incomplete chain, cycle, widening hop, or stale edge is not repaired by signatures, agreement, parenthood, service-account possession, wrappers, or successful execution.

Direct authority remains represented by `relationship = DIRECT`. Delegated authority uses `relationship = EXACT_DELEGATION` and one selected protected chain. A direct subject does not need a delegation graph. A delegated subject cannot fall back to direct authority merely because the root also admits its objective.

## 5. Protected delegation context

Extend each harness-owned trusted authority entry with one immutable `delegation_authority_context`. Candidate fixtures cannot supply, override, select, append, or reconstruct it. The runner rejects candidate keys such as `_trusted_delegation_context`.

The protected context contains strictly typed immutable collections:

- `delegation_policy`;
- `delegation_principals`;
- `delegation_grants`;
- `delegation_lifecycle_records`;
- `delegation_ordering_heads`;
- `delegation_principal_transitions`; and
- `delegation_grant_transitions`.

All collections are parsed once by the model and consumed by the oracle. There must not be separate accepted-field and evaluated-field lists. Unknown, duplicated, malformed, or partially typed protected records are harness/configuration failures, not authority verdicts. Structurally valid but non-applicable or incomplete records yield `UNAVAILABLE` during evaluation.

The context is stored beside the existing trusted anchor/control-plane context because it is protected authority input. That location does not make the anchor, observer, or verifier a delegation authority; each record still joins to the applicable root/source authority.

## 6. Delegator admission

Each `DELEGATION_PRINCIPAL_ADMISSION` binds exactly:

- `principal_id`, `principal_generation`, and `identity_basis`;
- `principal_kind` from a closed vocabulary (`HUMAN`, `AGENT`, `SERVICE_ACCOUNT`, `TOOL_EXECUTOR`, `AUTHORITY_ROOT`);
- applicable `objective_id` and generation;
- applicable decision-contract identity/version;
- `boundary`, `boundary_epoch`, and execution-control identity where applicable;
- `source_id`, source generation, source lineage, and root identity;
- admitted role (`DELEGATOR`, `DELEGATE`, or both);
- start/end event order, freshness challenge, lifecycle state; and
- exact scope family the principal admission can support.

The admission is root-issued or issued by an exact current root-authorized principal-admission source whose authority is separately established. V1 uses root-only principal admission unless a later reviewed design proves delegated admission non-circular. The principal cannot issue its own admission, and a delegation grant cannot bootstrap it.

For every edge, the delegator tuple `(principal_id, generation, identity_basis)` must join exactly to one current admission covering the full edge and use interval. Stable name, key, process, service account, parent relationship, or candidate record is insufficient.

## 7. Delegate admission

The delegate must independently join to its own current `DELEGATION_PRINCIPAL_ADMISSION`. The edge cannot create the delegate's identity or admission. The terminal delegate must also equal:

- `authority_tuple.subject`;
- T3 `subject_identity`;
- the current authority state's subject and identity basis;
- the exact `consumption_binding.subject`; and
- the consumer in the protected terminal grant/use relation.

An intermediate delegate that becomes a downstream delegator needs both admitted roles and explicit delegation authority. Merely receiving action authority does not permit subdelegation.

## 8. Delegation grant identity

Each immutable `DELEGATION_GRANT` binds exactly:

- `delegation_grant_id` and `delegation_grant_generation`;
- `parent_grant_id` and generation, or `ROOT_AUTHORITY` for genesis;
- exact delegator and delegate IDs, generations, and identity bases;
- applicable root, source authority, lineage, and authority generation;
- objective and decision-contract identity/generation/version;
- exact `action_scope` and separate `delegable_scope`;
- exact artifact/effect selector and effect class;
- tool/connector/resource selectors when applicable;
- boundary, boundary epoch, execution-control scope;
- creation event/order and effective start/end order;
- maximum downstream depth and current hop depth;
- whether further delegation is permitted;
- lifecycle identity and ordering-head identity; and
- terminal use/grant-binding identifiers.

`delegation_grant_id` is not the existing execution `grant_id`. The former identifies an authority edge; the latter identifies the final consumable authority grant. The terminal edge binds both exactly. A new generic evidence ID or execution grant ID cannot substitute for a missing delegation grant.

The canonical protected grant is the authority source. The candidate-facing `delegation_binding` must name the selected terminal edge/chain in a future migrated representation or be joined mechanically from its exact legacy fields during v1 compatibility migration. It never defines the delegator.

## 9. Root authority

Every selected chain has exactly one genesis relation whose `parent_grant_id = ROOT_AUTHORITY`. That relation must join to:

- the applicable `authority_root` identity, generation, boundary, epoch, lineage, and ordering source;
- a current root source-authority record;
- the exact objective and decision contract;
- a root grant that distinguishes action scope from delegable scope; and
- current lifecycle/order records.

The root cannot be candidate-derived, observer-derived, verifier-derived, or inferred from the first edge. A chain with no root, multiple competing roots, a stale root, or a cycle presented as a root is `UNAVAILABLE`. A current applicable root prohibition or revocation yields `DENIED`.

## 10. Chain closure

For subject mode `DELEGATED`, construct a directed graph over exact nodes `(principal_id, principal_generation, identity_basis)` and exact edges `(delegation_grant_id, generation)`.

The selected terminal use is authorized only if:

1. exactly one applicable terminal edge binds the current subject/use;
2. every edge has exactly one current delegator admission and delegate admission;
3. every non-genesis edge's parent grant is the exact preceding edge;
4. the preceding edge's delegate equals the next edge's delegator in exact identity and generation;
5. edge order is strictly increasing and falls within every principal/grant interval;
6. every edge preserves or narrows all scope dimensions;
7. each intermediate principal has explicit current subdelegation permission;
8. the chain length respects every upstream maximum depth;
9. the graph terminates at one independently admitted applicable root; and
10. the terminal edge binds the exact execution grant, consumption state, and effect.

The evaluator uses all applicable protected records, not a candidate-selected favorable subset. Missing middle edges, extra incompatible parents, duplicate heads, or ambiguous terminal edges return `UNAVAILABLE`.

## 11. Cycle prevention

Cycle detection uses exact principal nodes and exact grant edges. Reject:

- a grant whose delegator equals its delegate unless an explicit root policy allows the specific administrative no-op; v1 chooses the smaller rule and rejects self-delegation;
- any repeated principal node in the selected ancestor path;
- any repeated grant ID/generation;
- reciprocal A→B→A;
- longer A→B→C→A cycles;
- a chain whose root is reachable only through a descendant; and
- a replacement identity that reuses an ancestor label without an admitted transition.

Cycle detection occurs before scope or favorable-head selection. A cyclic candidate cannot be made authoritative by adding an acyclic competing branch, signatures, or majority agreement. The deterministic result is `UNAVAILABLE / DELEGATION_CHAIN_CYCLE` unless a current authoritative prohibition independently requires `DENIED`.

## 12. Scope intersection

`action_scope` and `delegable_scope` are typed products over existing authority semantics, not free-form strings. At minimum they bind:

- subject/identity class;
- artifact/resource selector;
- exact effect class;
- tool/connector selector;
- objective/decision contract;
- boundary and epoch;
- execution-control state;
- valid interval;
- maximum delegation depth; and
- any semantic scope already admitted by the decision contract.

At edge `i`, the effective downstream action scope is:

```text
effective_i = effective_(i-1) ∩ parent.delegable_scope ∩ edge.action_scope
```

The child `action_scope` and `delegable_scope` must each be subsets of the parent's effective delegable scope. Empty, incomparable, ambiguous, or unrepresentable intersections are `UNAVAILABLE`. A current root policy explicitly prohibiting the requested scope yields `DENIED`.

No wildcard broadening, omitted dimension, string-prefix match, group-label inference, or “same objective” shortcut is allowed. `READ` cannot yield `WRITE`; one artifact cannot yield all artifacts; one tool cannot yield another tool; a short interval cannot yield a longer one; and one boundary cannot silently yield another.

## 13. Delegation authority versus action authority

Every grant carries two separate permissions:

- `action_scope`: what the delegate may itself do; and
- `delegable_scope`: what, if anything, the delegate may grant onward.

Possessing `action_scope = WRITE(A)` with empty `delegable_scope` permits the admitted delegate to write A but not to delegate that write. A downstream edge requires explicit nonempty delegable scope covering its exact action, delegate class, boundary, interval, and depth. The evaluator never infers delegation rights from action rights, root objective binding, successful execution, or possession of credentials.

## 14. Exact effect and task scope

Use a closed effect vocabulary aligned to the authority-consuming transition: `READ`, `WRITE`, `DELETE`, `TRANSFER`, `EXECUTE`, `APPROVE`, `DELEGATE`, `RECONCILE`, and `RECOVER`. Deployment-specific effects require an exact admitted decision-contract mapping; unknown effects fail closed.

The terminal effect must join to the current artifact, closure relation, execution control, objective binding, and execution `grant_id`. Authority for one effect never implies another. `APPROVE` does not imply `EXECUTE`; `READ` does not imply `WRITE`; `RECONCILE` does not imply `RECOVER`.

## 15. Grant/use binding

Add a protected `DELEGATION_TERMINAL_USE_BINDING` or the equivalent exact terminal fields in the protected grant context. It binds:

- selected chain ID/digest;
- terminal delegation grant ID/generation;
- execution `grant_id`;
- exact subject identity/generation/basis;
- artifact and effect class;
- boundary/epoch and execution context;
- consumption state and one-shot/reusable policy;
- objective/contract identity; and
- current event/order and freshness.

It must match the existing `consumption_binding`, `closure_binding`, `execution_control_binding`, objective binding, and selected path. A grant from another chain, subject, artifact, effect, boundary, or generation returns `UNAVAILABLE`. Known applicable reuse or consumption prohibition remains `DENIED` under existing `INV-USE` semantics.

Candidate-provided terminal-use fields cannot create protected use authority. The oracle computes the expected candidate relation from the protected selected chain, reversing the current self-reference.

## 16. Lifecycle and currentness

Each principal and grant has an exact lifecycle record with:

- target identity and generation;
- state: `ACTIVE`, `EXPIRED`, `SUPERSEDED`, `REVOKED`, `REJECTED`, or `PROHIBITED`;
- event ID and authoritative event order;
- source/root identity, generation, and lineage;
- boundary/epoch and effective interval; and
- predecessor/successor or supersession identity where applicable.

One `DELEGATION_ORDERING_HEAD` identifies the current applicable grant/lifecycle head for the chain/root/objective/boundary. Candidate order is irrelevant. Every edge must be active and current at the terminal use event. Historical validity is insufficient.

Missing, stale, ambiguous, unordered, conflicting, expired, or superseded state whose current disposition cannot be established yields `UNAVAILABLE`. Current applicable `REVOKED`, `REJECTED`, or `PROHIBITED` yields `DENIED`. A current explicit revocation at an upstream edge invalidates all downstream uses even if descendants still appear active.

## 17. Successor and predecessor continuity

Delegation binds exact principal generation and identity basis. Shutdown, replacement, restart, clone, restored checkpoint, or subject transition ends portability of predecessor delegation edges.

`DELEGATION_PRINCIPAL_TRANSITION` binds old and new principal identities/generations, exact event order, reason, source authority, boundary/epoch, and whether any grant transition is permitted. It never transfers grants by itself.

A successor requires:

- independent current principal admission;
- a fresh delegation grant rooted in current authority;
- explicit supersession/transition of any relevant chain;
- a new terminal execution grant/use binding; and
- current observation coverage of the transition.

Same name, key, service account, software, state, objective, or credentials does not preserve delegation. A valid explicit successor regrant remains reachable.

## 18. Wrapper, relay, broker, and proxy continuity

A wrapper, relay, broker, proxy, tool proxy, or planner does not erase or replace the authority chain. Classify each participant as one of:

- **transport-only:** may carry an exact immutable grant/commitment but cannot change subject, scope, or effect;
- **transforming intermediary:** requires exact admitted transformation lineage and cannot widen scope;
- **authority consumer:** must be an admitted principal and appear as the terminal delegate/use subject; or
- **subdelegator:** must be an admitted principal with explicit delegable scope and a protected edge.

Transport possession is evidence only. If a wrapper becomes the acting principal, changes the tool/backend, chooses the grant, or changes the effect, it must appear in the exact chain or authority becomes `UNAVAILABLE`. Transformation records bind source/target digests and preserve every delegation-relevant field; a summary cannot drop an edge, revocation, scope restriction, or identity generation.

## 19. Shared service accounts

A service account is a principal/capability boundary, not a substitute for the human or agent consumer. Its admission binds account identity/generation, controller subject identity, control domain, credential identity, permitted action/delegation scope, boundary, and interval.

Valid use requires both:

- exact current service-account admission; and
- exact subject-to-account use binding for the terminal action.

Two agents using the same account remain distinct consumers. Account possession, shared credentials, stable account label, or another agent's prior authorized use cannot authorize the current agent. Controller change requires a protected principal/account transition and fresh grant/use binding.

## 20. Planner/executor split

Planning, proposing, recommending, approving, and executing are distinct effect classes. A planner's grant can authorize `PROPOSE(action)` but not the executor's terminal action. The executor must be independently admitted and have an exact current chain for `EXECUTE`, `WRITE`, `TRANSFER`, or other actual effect.

A valid planner/executor path contains separate protected chains or an exact root-authorized chain whose typed scopes explicitly cover each role and effect without widening. Planner output is evidence for the executor's decision contract, not execution authority.

## 21. Multi-agent task decomposition boundary

For an authority-relevant composed outcome, `INV-CLO` requires the final aggregate effect to be represented as the artifact/effect evaluated at T3. Individually permitted subtasks do not authorize a prohibited or broader composition.

The implementation can enforce this only when the final composed effect and its derivation are present in the admitted model. It must bind:

- component effect identities;
- exact composition/closure relation;
- resulting artifact/effect;
- participating principals and chains; and
- an applicable decision contract for the aggregate result.

If the semantic effect of decomposition cannot be represented or observation loses the composition, Authority Lab returns `UNAVAILABLE`; it does not claim general semantic understanding. A real-world composition omitted before admitted input remains an external observation/modeling limitation.

## 22. Cross-boundary continuity

Any edge crossing boundary epoch, execution context, tool/backend, connector, or principal identity requires an exact current transition already admitted under the existing mutation, observation, shutdown/successor, and control-plane rules. The delegation chain must bind the post-transition identities and epoch.

An old boundary grant cannot be relabeled for the new boundary. Re-entry requires a fresh root-current grant chain. Observer handoff proves coverage only and cannot transfer delegation authority.

## 23. DENIED versus UNAVAILABLE

Return `UNAVAILABLE` for unresolved or missing delegator/delegate identity, principal admission, root authority, grant identity, chain edge, chain closure, scope intersection, subdelegation permission, lifecycle/currentness, ordering, grant/use binding, boundary transition, successor transition, service-account controller, wrapper lineage, or aggregate-effect authority.

Return `DENIED` only when a current applicable authoritative record explicitly revokes, rejects, prohibits, or establishes impermissibility for the delegation, delegator, delegate, scope, root, successor, or terminal use. Do not turn an unknown agent, malformed provenance claim, stale record, or conflict into denial.

`AUTHORIZED` remains possible only after the complete selected chain and every existing objective, observation, control-plane, boundary, identity, execution, grant/use, closure, freshness, and prohibition rule succeeds.

## 24. Hostile matrix A–BA

| ID | Case | Desired result | Exact reason class | Required authority fact |
|---|---|---|---|---|
| A | Arbitrary delegator in `LAB-V0-010` | `UNAVAILABLE` | `DELEGATION_SOURCE_AUTHORITY_UNAVAILABLE` | Exact protected delegator admission and grant issuer join |
| B | Arbitrary delegate | `UNAVAILABLE` | `DELEGATE_ADMISSION_UNAVAILABLE` | Delegate principal admission matching terminal subject/use |
| C | Candidate invents both principals | `UNAVAILABLE` | `DELEGATION_PRINCIPAL_ADMISSION_UNAVAILABLE` | Two independent protected admissions |
| D | Missing delegator admission | `UNAVAILABLE` | `DELEGATION_SOURCE_AUTHORITY_UNAVAILABLE` | Current delegator admission |
| E | Missing delegate admission | `UNAVAILABLE` | `DELEGATE_ADMISSION_UNAVAILABLE` | Current delegate admission |
| F | Valid delegator lacks delegation authority | `UNAVAILABLE` | `DELEGABLE_SCOPE_UNAVAILABLE` | Nonempty exact delegable scope |
| G | Action authority but no right to delegate | `UNAVAILABLE` | `DELEGABLE_SCOPE_UNAVAILABLE` | Separate delegation permission |
| H | Grant belongs to another delegate | `UNAVAILABLE` | `DELEGATION_GRANT_USE_UNAVAILABLE` | Exact delegate/consumer join |
| I | Grant for another artifact | `UNAVAILABLE` | `DELEGATION_SCOPE_UNAVAILABLE` | Exact artifact selector |
| J | Grant for another effect | `UNAVAILABLE` | `DELEGATION_EFFECT_UNAVAILABLE` | Exact effect class |
| K | Grant for another boundary | `UNAVAILABLE` | `DELEGATION_BOUNDARY_UNAVAILABLE` | Exact current boundary/epoch |
| L | Stale grant | `UNAVAILABLE` | `DELEGATION_CURRENTNESS_UNAVAILABLE` | Current ordering/freshness |
| M | Current authoritative revocation | `DENIED` | `DELEGATION_REVOKED` | Applicable current revocation |
| N | Superseded grant, head unresolved | `UNAVAILABLE` | `DELEGATION_CURRENTNESS_UNAVAILABLE` | Exact current successor/head |
| O | Expired grant | `UNAVAILABLE` | `DELEGATION_CURRENTNESS_UNAVAILABLE` | Current validity interval |
| P | Grant predates subject transition | `UNAVAILABLE` | `DELEGATION_PRINCIPAL_CONTINUITY_UNAVAILABLE` | Post-transition grant |
| Q | Predecessor grant reused by successor | `UNAVAILABLE` | `DELEGATION_SUCCESSOR_AUTHORITY_UNAVAILABLE` | Successor-specific grant/use chain |
| R | Explicit current successor regrant | `AUTHORIZED` | `CURRENT_AUTHORITY_ESTABLISHED` | New principal, grant, chain, use |
| S | Valid A→B→C | `AUTHORIZED` | `CURRENT_AUTHORITY_ESTABLISHED` | Rooted ordered non-widening chain |
| T | A→B→A | `UNAVAILABLE` | `DELEGATION_CHAIN_CYCLE` | Acyclic root closure |
| U | A→B→C→A | `UNAVAILABLE` | `DELEGATION_CHAIN_CYCLE` | Acyclic root closure |
| V | Self-delegation | `UNAVAILABLE` | `DELEGATION_CHAIN_CYCLE` | Distinct admitted edge endpoints |
| W | Candidate-derived root | `UNAVAILABLE` | `DELEGATION_ROOT_AUTHORITY_UNAVAILABLE` | Independently protected root |
| X | Independently established root | Eligible for `AUTHORIZED` | ordinary chain result | Exact root genesis relation |
| Y | READ→WRITE widening | `UNAVAILABLE` | `DELEGATION_SCOPE_WIDENING` | Child subset of parent delegable scope |
| Z | Narrow artifact→broad artifact | `UNAVAILABLE` | `DELEGATION_SCOPE_WIDENING` | Exact selector intersection |
| AA | Short→long duration widening | `UNAVAILABLE` | `DELEGATION_SCOPE_WIDENING` | Interval intersection |
| AB | Same scope preserved | Eligible for `AUTHORIZED` | ordinary chain result | Exact scope equality/subset |
| AC | Missing middle edge | `UNAVAILABLE` | `DELEGATION_CHAIN_INCOMPLETE` | Exact parent edge |
| AD | Missing root | `UNAVAILABLE` | `DELEGATION_ROOT_AUTHORITY_UNAVAILABLE` | Root genesis closure |
| AE | Wrapper hides delegator | `UNAVAILABLE` | `DELEGATION_TRANSFORMATION_UNAVAILABLE` | Edge-preserving transformation |
| AF | Relay hides grant | `UNAVAILABLE` | `DELEGATION_GRANT_USE_UNAVAILABLE` | Exact immutable grant carriage |
| AG | Proxy substitutes subject | `UNAVAILABLE` | `DELEGATE_ADMISSION_UNAVAILABLE` | Proxy as admitted terminal consumer |
| AH | Shared account, unauthorized agent | `UNAVAILABLE` | `SERVICE_ACCOUNT_USE_UNAVAILABLE` | Subject-to-account use binding |
| AI | Valid subject-bound account use | `AUTHORIZED` | `CURRENT_AUTHORITY_ESTABLISHED` | Current account/controller/use chain |
| AJ | Planner causes unauthorized execution | `UNAVAILABLE` | `EXECUTOR_AUTHORITY_UNAVAILABLE` | Executor's exact effect chain |
| AK | Planner plus authorized executor | `AUTHORIZED` | `CURRENT_AUTHORITY_ESTABLISHED` | Separate exact proposal/execution authority |
| AL | Delegated read indirectly causes write | `UNAVAILABLE` | `DELEGATION_EFFECT_UNAVAILABLE` | Final composed WRITE authority |
| AM | Downstream use after upstream revocation | `DENIED` | `DELEGATION_REVOKED` | Current upstream lifecycle applied transitively |
| AN | Use after boundary change | `UNAVAILABLE` | `DELEGATION_BOUNDARY_UNAVAILABLE` | Fresh post-transition chain |
| AO | Use after tool/backend change | `UNAVAILABLE` | `DELEGATION_SCOPE_UNAVAILABLE` | Exact new tool/backend grant |
| AP | Chain crosses shutdown/successor | `UNAVAILABLE` | `DELEGATION_SUCCESSOR_AUTHORITY_UNAVAILABLE` | Successor-specific chain |
| AQ | Valid explicit successor regrant | `AUTHORIZED` | `CURRENT_AUTHORITY_ESTABLISHED` | Fresh successor admission/grant/use |
| AR | Multi-hop exact intersection | `AUTHORIZED` | `CURRENT_AUTHORITY_ESTABLISHED` | Every edge subset and current |
| AS | One stale edge | `UNAVAILABLE` | `DELEGATION_CURRENTNESS_UNAVAILABLE` | All-edge currentness |
| AT | One unauthorized edge | `UNAVAILABLE` | `DELEGATION_CHAIN_INCOMPLETE` | All-edge authority |
| AU | One widened edge | `UNAVAILABLE` | `DELEGATION_SCOPE_WIDENING` | All-edge subset relation |
| AV | Fully valid exact chain | `AUTHORIZED` | `CURRENT_AUTHORITY_ESTABLISHED` | Complete root-to-use chain |
| AW | Candidate chooses favorable grant | `UNAVAILABLE` if other applicable state conflicts | `DELEGATION_ORDERING_UNAVAILABLE` | Authority-selected unique head |
| AX | Conflicting grants | `UNAVAILABLE` | `DELEGATION_CONFLICTING` | Authoritative resolution/head |
| AY | Explicit revocation plus stale grant | `DENIED` | `DELEGATION_REVOKED` | Current revocation outranks stale grant |
| AZ | Fresh genesis delegation root | `AUTHORIZED` | `CURRENT_AUTHORITY_ESTABLISHED` | Root genesis, one edge, exact use |
| BA | Fresh successor chain | `AUTHORIZED` | `CURRENT_AUTHORITY_ESTABLISHED` | New successor root-closed chain |

## 25. Positive authorization paths

The repair must preserve these independently tested positive paths:

1. **Direct authority:** no delegation chain; all ordinary root/objective/use relations remain valid.
2. **One-hop delegation:** root admits A, grants A exact delegable scope, A grants B a subset, and B's terminal use matches.
3. **Multi-hop delegation:** root→A→B→C is acyclic, ordered, current, within maximum depth, and scope-preserving at every edge.
4. **Successor regrant:** predecessor ends; successor receives new principal admission, new chain, and new terminal use grant.
5. **Service-account use:** exact admitted subject controls and uses the account within scope.
6. **Planner/executor:** planner may propose; independently admitted executor has exact authority for the real effect.
7. **Fresh genesis:** applicable root creates the first current exact delegation chain.

These reach `AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED` only after all pre-existing checks also pass.

## 26. Existing-field and invariant mapping

| Existing structure | Delegation use |
|---|---|
| `evidence_binding` | Binds admitted observation of every delegation-relevant transition; never creates delegation authority. |
| `binding_source_authority` | Supplies independently admitted root/source lineage; protected delegation grants join to it. |
| `freshness` | Binds the terminal evaluation event and protected delegation ordering head. |
| `binding_ordering` | Supplies root ordering context; delegation has an exact subordinate protected head. |
| `binding_lifecycle` | Root/objective lifecycle remains authoritative; delegation lifecycle cannot outlive it. |
| `identity_basis` | Terminal subject and each protected principal bind exact identity/generation. |
| `boundary_epoch` | Every principal, edge, transition, and terminal use is epoch-bound. |
| control-plane independence | Ensures root/orderer/observer/verifier sources relied upon by delegation are not falsely independent. |
| verifier-state anchoring | Protects current observation/authority history from rollback; it does not issue delegation. |
| source-domain membership | Prevents multiplicity, wrappers, or common upstream control from becoming independent authority. |
| current `delegation_binding` | Candidate proposal joined against protected chain; no longer source of expected delegator. |

Invariant application:

- `INV-CONT`: exact root-to-terminal chain and current lifecycle persist through use.
- `INV-DISC`: exact principal generations and identity bases prevent label/account/successor substitution.
- `INV-BND`: every edge, scope, and transition remains in the applicable boundary/epoch.
- `INV-EVD`: delegation records, signatures, votes, planner output, and possession cannot confer authority.
- `INV-USE`: terminal consumption binds one exact current chain and prevents replay/portability.
- `INV-CLO`: delegation, composition, wrapping, relaying, aggregation, and decomposition do not widen authority.

The six invariants are sufficient.

## 27. Fixture migration implications

If implemented, migrate the trusted context atomically:

- all 234 trusted authority entries receive the strict `delegation_authority_context` shape;
- 233 currently direct cases receive empty protected delegation collections and retain exact outcomes;
- `LAB-V0-010` receives a genuine root-issued one-hop principal/grant/lifecycle/order/use chain preserving its positive intent;
- candidate fixtures cannot include trusted context;
- legacy candidate `delegation_binding` fields remain accepted only where they join exactly to protected records; and
- new hostile fixtures start at `LAB-V1-235` and cover A–BA plus any distinct parser/currentness cases.

If mechanical inspection finds additional delegated positives, the migration count must be derived from the repository rather than assumed. Expectations remain independent and cannot be rewritten to match implementation output.

## 28. Expected implementation surface

The smallest expected implementation touches:

- `authority_lab/model.py`: immutable typed protected records and strict parsing;
- `authority_lab/runner.py`: load protected delegation context, reject candidate injection, expose trace;
- `authority_lab/oracle.py`: root-closed graph construction, exact joins, cycle detection, scope intersection, lifecycle/order, and terminal use;
- `authority_lab/README.md`: executable delegation semantics and trust boundary;
- `tests/test_authority_lab.py`: independent hostile and positive tests;
- `cases/authority_lab/trusted_anchor_state.json`: atomic protected-context migration;
- maintained fixtures only where candidate relation fields require reviewed compatibility migration; and
- new fixtures beginning at `LAB-V1-235`.

No public contract or schema-version file changes are required.

## 29. Hostile design review

| Attack | Why it does not survive the design |
|---|---|
| Arbitrary delegator mutation | Candidate value must equal one protected current principal and grant issuer; it cannot define the expected value. |
| Arbitrary delegate mutation | Terminal delegate must join protected admission, tuple subject, identity basis, consumption, and use. |
| Valid-looking unrooted chain | Closure requires one protected genesis relation joined to the applicable root. |
| Circular chain | Exact-node and exact-edge repetition is rejected before head/scope selection. |
| Candidate-derived root | Trusted root/genesis records are harness-owned and separately source-authorized. |
| Scope widening | Every dimension must be a subset of accumulated effective delegable scope. |
| Stale grant | All-edge lifecycle/order/currentness is mandatory at terminal use. |
| Revoked upstream edge | Current applicable revocation invalidates downstream use and yields `DENIED`. |
| Successor reuse | Principal generation/identity transition ends portability; new grant/use required. |
| Wrapper laundering | Wrapper is typed as transport, transform, consumer, or subdelegator; acting changes require a chain edge. |
| Service-account laundering | Account and actual controller/consumer are separately and exactly bound. |
| Planner/executor laundering | Proposal and execution are distinct effects with distinct terminal authority. |
| Grant shopping | All-applicable protected ordering selects one current head; candidate cannot select a subset. |
| Partial chain | Every parent edge and root must be present and exact. |
| One invalid hidden edge | Authorization is universal over every selected edge, not an endpoint check. |
| Valid direct delegation blocked | One-hop root-closed positive path remains defined and testable. |
| Valid multi-hop blocked | Explicit subdelegation, depth, ordered edges, and subset scope permit authorization. |
| Valid successor regrant blocked | Fresh successor principal, chain, and terminal use are a positive path. |

The design also resists reciprocal authority, longer cycles, repeated signatures, majority agreement, pooled partial scope, stale service accounts, cross-boundary relabeling, and task decomposition when the aggregate effect is represented.

The only irreducible boundary is omitted or false external observation: if every admitted authority and observation root falsely presents a fabricated but internally exact history, the deterministic oracle cannot infer the real world. This design does not claim otherwise.

## 30. Residual limitations

- Multi-agent semantic decomposition can be checked only when the aggregate effect is represented and bound. General intent inference is outside Authority Lab v1.
- Real principal identity, credential control, event delivery, and root truth remain admitted external trust preconditions.
- Total collusion beyond every admitted independent authority/observation source remains externally indistinguishable.
- The closed effect and scope vocabularies must remain deployment-specific enough to avoid false equivalence; unknown relations fail closed.
- Multi-hop delegation increases protected-state size and graph-validation cost. Implementations must bound chain depth and record count without treating exhaustion as denial.
- Root-only principal admission is intentionally conservative. Delegated principal admission would require a separate proof of non-circularity and is not authorized by this design.

## 31. Determination and exact hostile-design verdict

Path-complete delegation authority is representable as internal typed relations composed from existing identity, source-authority, lifecycle, ordering, freshness, boundary, observation, grant/use, closure, control-plane, and anchoring semantics. It does not require a seventh coordinate, seventh invariant, fourth outcome, or new schema version.

Executable implementation is justified. It should atomically add the protected delegation context, migrate all trusted entries, repair `LAB-V0-010` with a real positive delegation chain, add hostile fixtures beginning at `LAB-V1-235`, and prove both direct and multi-hop positive paths.

**PASS — NO REPRODUCIBLE IN-SCOPE MULTI-AGENT DELEGATION, SCOPE-LAUNDERING, OR CIRCULAR-AUTHORITY BYPASS SURVIVES THE PROPOSED DESIGN**
