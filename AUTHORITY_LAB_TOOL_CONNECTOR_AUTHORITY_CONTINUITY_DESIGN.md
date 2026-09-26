# Authority Lab v1 Tool / Connector Authority Continuity Design

## 1. Exact baseline

This design starts from `2f68e33aafc78bd1a51b97ca380cfd8d9925f588`, `docs: record tool connector authority continuity frontier`. At that exact head, 237/237 public tests and 342/342 maintained fixtures pass. The schema is `authority-lab-v1`; the public contract remains six tuple coordinates, six invariants, and three outcomes. The frontier commit changed only `FRONTIER_DELTA_TOOL_CONNECTOR_AUTHORITY_CONTINUITY.md`.

This is a design artifact. It changes no executable code, fixture, schema, tuple coordinate, invariant, or outcome.

## 2. Research counterexample

The minimal executable counterexample adds a schema-valid candidate-required fact to positive fixture `LAB-V1-337`:

```text
tool_connector_identity = payments@BACKEND-B
```

Candidate `required_values` repeats the same value. The current oracle returns:

```text
AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED
```

The same addition preserves `AUTHORIZED` in `LAB-V1-338`, which has exact human approval, and `LAB-V1-253`, which has protected delegation. Candidate credential rotation, permission expansion, and favorable tool selection also coexist with `AUTHORIZED`. Registered `tool_connector_identity` and `credential_identity` mutations correctly return `UNAVAILABLE`, and a direct edit to approval's `tool_backend_id` correctly returns `UNAVAILABLE / HUMAN_APPROVAL_SCOPE_UNAVAILABLE`.

## 3. Defect statement

Mutation-registry closure is not defective. Approval and delegation are not ignoring their own exact scalar tool fields. The missing relationship is the independently protected join from those scalar names to the actual current effect-capable execution target.

Current authority can bind the label `payments` while remaining unable to establish:

- which logical-tool generation is applicable;
- which connector generation resolves it;
- which backend generation receives the effect;
- which concrete target is effect-capable;
- which operator/source lineage controls that target;
- which credential generation is used;
- which exact effective permission set applies;
- whether any of those relations changed after authority was established.

The design adopts:

> A stable label is not continuity. Authority requires one exact, current, independently selected execution-target lineage at use time.

## 4. Normative execution-target model

Authority Lab v1 adds one internal protected `tool_connector_authority_context` to each harness-owned trusted-anchor entry and one strict candidate-visible `tool_connector_use_binding` T3 fact. These are relational authority state, not a seventh tuple coordinate or invariant.

The protected context has exactly these collections:

1. `tool_connector_policy`
2. `logical_tool_admissions`
3. `connector_admissions`
4. `backend_admissions`
5. `execution_target_admissions`
6. `credential_admissions`
7. `permission_scope_records`
8. `component_lifecycle_records`
9. `component_ordering_heads`
10. `component_transitions`
11. `execution_target_selection`
12. `protected_terminal_uses`

Every record is strict, immutable after parsing, exact-field-only, generation-bearing, lifecycle-bearing, ordered, boundary-scoped, freshness-bound, and source-authority-bound. Candidate fixtures cannot supply `_trusted_tool_connector_context`, replace `tool_connector_authority_context`, select a protected record, or manufacture protected currentness.

The policy mode is closed:

- `NONE`: no effect-capable tool is applicable to this decision. Existing non-tool authorization remains reachable.
- `REQUIRED`: one exact protected execution-target lineage and terminal use are mandatory.

`ALL_APPLICABLE` is the only v1 selection rule. Candidate strings, generic facts, self-reports, successful authentication, endpoint reachability, signatures, or digest agreement cannot select `NONE` or a favorable target.

The oracle computes a domain-separated canonical execution-context digest over the exact selected logical tool, connector, backend, target, credential, permission scope, operator lineage, boundary, execution context, subject/executor, objective/contract, effect, grant/use identity, and current generations. The protected selection head commits to that digest. Candidate recomputation cannot change the protected head.

## 5. Logical tool identity

Each `LOGICAL_TOOL_ADMISSION` binds:

- `tool_id`, `tool_generation`, and identity basis;
- permitted effect classes and artifact/resource classes;
- applicable subject/executor classes;
- applicable boundary and execution-context class;
- source authority, lineage, lifecycle, ordering, and freshness;
- the exact selected connector identity/generation.

A candidate string or tool self-report is evidence only. The protected policy and ordering head determine the applicable tool. Same `tool_id` with a different generation is a transition, not continuity.

## 6. Connector identity

Each `CONNECTOR_ADMISSION` binds:

- connector identity, generation, identity basis and provider/source lineage;
- exact upstream tool identity/generation;
- exact downstream backend identity/generation;
- connector implementation/profile identity;
- boundary, execution context, lifecycle, ordering, freshness and source authority;
- any proxy, relay, wrapper, broker or service-account lineage required to reach the backend.

A connector may not authorize itself, declare itself current, choose its backend, or infer continuity from a stable label. Connector restart with generation reuse is unavailable unless an exact authorized continuity relation establishes that it remains the same admitted authority identity.

## 7. Backend identity

Each `BACKEND_ADMISSION` binds:

- backend identity, generation and identity basis;
- operator identity, operator generation and source/control lineage;
- exact connector identity/generation;
- exact effect-capable target identity/generation;
- supported effect and artifact/resource classes;
- boundary, lifecycle, ordering, freshness and source authority.

Backend label equality does not imply operator equality or target equality. A changed operator, provider, process authority, tenant, control source or backend generation requires an explicit transition.

## 8. Effect-capable target

Each `EXECUTION_TARGET_ADMISSION` identifies the terminal system that can create the authority-consuming effect. It binds:

- target identity, generation and target type;
- backend identity/generation and operator lineage;
- endpoint/service-resolution identity and generation;
- canonical effect and parameter/target/destination scope;
- applicable artifact/resource, subject, executor, boundary and execution context;
- lifecycle, ordering, freshness and source authority.

An endpoint alias, URI, route, service name, browser target, computer-use surface, or proxy label is not the target identity. Resolution to a materially different target changes this record and its canonical digest.

## 9. Credential continuity

Each `CREDENTIAL_ADMISSION` binds:

- credential identity, generation and identity basis;
- issuing authority identity/generation;
- principal/subject and actual executor;
- logical tool, connector, backend and target applicability;
- exact permission-scope record identity/generation;
- boundary and execution context;
- lifecycle, revocation/supersession state, ordering and freshness;
- source authority independent of the candidate and effect-capable target.

Credential ID equality does not hide generation change. Credential validity does not establish target identity or unchanged permissions. Replacement, key rotation and service-account change require an authorized credential transition and current permission join.

## 10. Permission-scope continuity

Each immutable `PERMISSION_SCOPE` record carries an exact sorted, duplicate-free set of semantic actions and resource constraints, not an opaque display string. It binds its identity/generation to the credential, backend, target, principal, boundary, lifecycle, ordering, freshness and source authority.

- Expansion requires an exact current authoritative `PERMISSION_EXPANSION` transition. Existing approval and delegation do not widen automatically. If either policy binds the old scope or requires revalidation, fresh approval/regrant is mandatory.
- Narrowing may preserve authority only when an exact authorized `PERMISSION_NARROWING` transition exists, the requested effect remains a subset of the new scope, and no approval/delegation/tool policy requires reauthorization.
- A scope that no longer covers the requested effect yields `UNAVAILABLE`; an exact current prohibition yields `DENIED`.

Counts, strings, successful API calls, or credentials containing scope claims do not establish effective permissions.

## 11. Operator / source lineage

Operator identity is separate from backend identity. Protected admissions bind controller, upstream dependency, provider/operator and rollback/control domain using the existing source-domain/control-plane independence vocabulary. A stable backend label under a different operator is a source-authority transition.

The target, connector, backend, credential issuer, verifier, candidate, subject, executor, approver, or delegate cannot issue its own protected admission or close a circular source chain. Authorized source change requires a root-issued transition whose predecessor and successor lineages are exact and current.

## 12. Lifecycle and currentness

Every selected component has one authoritative lifecycle record and one unique ordering head. The selected context is current only if:

- all generations and identities join exactly;
- lifecycle is `ACTIVE`;
- no applicable later revocation, rejection, prohibition, supersession or conflicting head exists;
- source authority and boundary match the current root;
- ordering precedes or equals the exact T3 terminal-use event;
- freshness binds the current observation challenge and interval;
- observation coverage includes every affected tool/connector/backend/credential/permission family;
- component transitions form one ordered predecessor-to-successor path.

Alive, reachable, authenticated, healthy and credential-valid are operational facts, not authority currentness.

## 13. Exact use binding

The candidate-visible `tool_connector_use_binding` is a strict typed relation with:

- policy identity/generation;
- selected context identity/generation and protected context digest;
- logical tool, connector, backend, target, credential and permission-scope identities/generations;
- operator/source lineage;
- exact subject, executor, delegation-chain head and approval identity where applicable;
- objective, contract, artifact/resource, effect and canonical effect digest;
- execution context, boundary/epoch, grant/use, session and event order;
- queue/schedule/retry phase identity where applicable;
- source verification receipt identity.

The protected `TOOL_CONNECTOR_TERMINAL_USE` repeats the exact context digest and terminal identities under root/current ordering. Both must join the selected protected head. Candidate-local recomputation, required-value equality or an unconsumed generic fact cannot replace the protected digest.

## 14. Human approval interaction

Human Approval Continuity remains the sole approval model. Its canonical effect gains the protected tool-context identity/generation and context digest as authoritative inputs. Existing `tool_backend_id` and `credential_generation` become exact projections that must equal the selected protected context; they cannot select it.

If backend, connector, credential, permission scope or target changes after approval, the selected context digest changes. Old approval then fails exact request/effect/head binding. Fresh approval is required unless both tool policy and approval policy explicitly admit the exact authority-preserving transition. Permission expansion and backend/operator change require reapproval in v1.

Approval never authorizes tool rotation or backend selection.

## 15. Delegation interaction

Delegation remains the sole execution-delegation model. Tool names in delegation scope constrain which protected logical tools may be selected; they do not identify a backend. The protected terminal delegation use gains the exact selected tool-context identity/generation and context digest.

A hidden backend change therefore invalidates the terminal join even while the grant's tool label remains unchanged. Backend/operator migration, connector replacement, permission expansion, or successor transition requires a fresh exact delegation grant/use whenever the delegation policy binds the replaced context. Delegation never authorizes its own tool transition.

## 16. Authorized rotations

One strict `TOOL_COMPONENT_TRANSITION` shape covers tool, connector, backend, target and credential transitions. It binds:

- component kind;
- old identity/generation and old current-head digest;
- new identity/generation and new current-head digest;
- transition class (`ROTATION`, `HANDOFF`, `MIGRATION`, `REPLACEMENT`, `NARROWING`, `EXPANSION`);
- preserved and changed authority dimensions;
- old/new operator lineage, boundary and permission scope;
- required approval/delegation revalidation disposition;
- transition event order and observation coverage;
- root/source authority, lifecycle and freshness.

The old component is superseded at the transition order; the successor becomes usable only after its admission and unique new ordering head are current. A transition cannot be issued by either endpoint, candidate, tool, connector, backend, credential, approval or delegation relation.

Positive paths include T1→T2 tool rotation, C1→C2 connector handoff, credential key rotation and target replacement when every exact transition condition and required revalidation is established.

## 17. Backend migration

An authorized B1→B2 migration requires:

- exact old and new backend/operator/target admissions;
- a root-issued migration transition;
- exact connector handoff or new connector admission;
- current credential and permission applicability to B2;
- B1 supersession and one unique selected B2 head;
- complete ordered observation of the transition;
- fresh approval and delegation regrant when their policies require it;
- a T3 terminal use bound only to B2's new context digest.

Returning later to label B1 is a new lineage/generation; it does not revive the predecessor context.

## 18. Proxy / relay / wrapper lineage

Every effect-capable path is an ordered lineage:

```text
logical tool → connector → optional intermediaries → backend → target
```

Each proxy, relay, wrapper, broker or service account is represented by a strict lineage hop with identity/generation, upstream/downstream identities, preserved effect constraints, operator/control lineage, boundary, lifecycle, ordering, freshness and source authority. The canonical context digest commits to the entire ordered path. Dropped, inserted, reordered, self-asserted or target-changing hops yield `UNAVAILABLE`.

V1 does not infer semantic equivalence between direct and proxied execution. Exact protected lineage is required.

## 19. Tool / backend selection policy

`TOOL_CONNECTOR_POLICY` is harness-owned and root-issued. It binds objective/contract/effect/artifact applicability, allowed components, required layers, boundary, selection rule, transition rules, revalidation rules, lifecycle, ordering and freshness.

`ALL_APPLICABLE` requires the evaluator to consider every protected applicable current record. One unique selected context is required. Multiple current candidates, same-position heads, conflicting backends, ambiguous aliases or incomplete applicability yield `UNAVAILABLE`. There is no first-match, first-writer, majority, cheapest, fastest or verifier-favorable selection.

The candidate, verifier, planner, approval, delegation chain and tool cannot choose which protected policy or target applies.

## 20. Successor continuity

Tool context is successor-specific. Subject, executor, execution-context, backend, connector or target successor events invalidate predecessor terminal-use binding. Identical labels, code, checkpoint, credentials or restored state do not transfer it.

A fresh successor path requires the existing successor authority chain plus a current successor-specific tool context, credential/permission applicability, approval/regrant where required, observation coverage and a new protected terminal use. Fresh successor authorization remains reachable.

## 21. Queued execution implications

The selected context is evaluated at the authority-consuming T3 event, not only at request, approval, delegation or queue time. Queue delay, schedule release, retry, partial execution, recovery or resumed work triggers exact revalidation.

Any intervening tool, connector, backend, target, credential, permission, source or policy transition changes the protected context head/digest. Old queued authorization becomes `UNAVAILABLE` unless the exact new context and all policy-required reapproval/regrant relations are established. This supplies the execution-target input needed by the later Long-Horizon Authority Decay frontier without defining time-decay semantics here.

## 22. `DENIED` versus `UNAVAILABLE`

`UNAVAILABLE` applies to missing, unknown, stale, ambiguous, conflicting, candidate-controlled, self-reported, unselected or incompletely observed tool identity, connector identity, backend identity, target, credential, permission scope, operator lineage, lifecycle, ordering, transition, policy, context digest or terminal-use binding.

`DENIED` applies only when an exact current authoritative record explicitly revokes, rejects or prohibits the applicable tool, connector, backend, target, credential, permission, transition or requested effect.

An unavailable component never degrades into permission, and an explicit prohibition is not weakened into uncertainty.

## 23. Hostile matrix A–BO

| ID | Scenario | Required result | Design disposition |
|---|---|---|---|
| A | Same tool/backend unchanged | `AUTHORIZED` | Exact selected context/head/use remain current |
| B | Same tool label, new backend | `UNAVAILABLE` | Backend/context digest mismatch |
| C | Same connector label, new generation | `UNAVAILABLE` | Generation mismatch; transition required |
| D | Same endpoint, new target | `UNAVAILABLE` | Target identity is independent of alias |
| E | Backend operator changes | `UNAVAILABLE` | Operator/source lineage transition missing |
| F | Credential generation changes | `UNAVAILABLE` | Exact credential generation mismatch |
| G | Credential key changes | `UNAVAILABLE` | Authorized credential transition required |
| H | Permission expands | `UNAVAILABLE` | Expansion and required revalidation absent |
| I | Permission narrows | `AUTHORIZED` only if effect remains covered and transition exact | Subset and policy check |
| J | Stale connector metadata | `UNAVAILABLE` | Freshness/head mismatch |
| K | Stale backend generation | `UNAVAILABLE` | Current selected generation differs |
| L | Stale credential binding | `UNAVAILABLE` | Credential head/currentness mismatch |
| M | Tool restart | `UNAVAILABLE` absent continuity | Restart/generation transition required |
| N | Connector restart | `UNAVAILABLE` absent continuity | Connector transition required |
| O | Backend replacement | `UNAVAILABLE` absent migration | New admission/migration required |
| P | Cached tool identity | `UNAVAILABLE` | Protected current head is authoritative |
| Q | Candidate tool identity | `UNAVAILABLE` | Candidate cannot supply protected context |
| R | Candidate backend identity | `UNAVAILABLE` | Candidate cannot select backend |
| S | Candidate credential identity | `UNAVAILABLE` | Candidate cannot supply admission |
| T | Candidate permission scope | `UNAVAILABLE` | Candidate scope is non-authoritative |
| U | Tool self-reports identity | `UNAVAILABLE` | Self-attestation rejected |
| V | Connector self-reports currentness | `UNAVAILABLE` | Protected lifecycle/order required |
| W | Backend self-reports currentness | `UNAVAILABLE` | Protected lifecycle/order required |
| X | Proxy substitution | `UNAVAILABLE` | Ordered lineage digest changes |
| Y | Relay substitution | `UNAVAILABLE` | Ordered lineage digest changes |
| Z | Wrapper hides backend | `UNAVAILABLE` | Terminal target must join protected path |
| AA | Approval A, hidden backend B | `UNAVAILABLE` | Approval context digest differs from use |
| AB | Delegation A, hidden backend B | `UNAVAILABLE` | Delegation terminal context digest differs |
| AC | Exact approval + exact backend | `AUTHORIZED` | Exact protected join succeeds |
| AD | Exact delegation + exact backend | `AUTHORIZED` | Exact protected join succeeds |
| AE | Approval before authorized rotation | `UNAVAILABLE` until revalidated | Rotation changes context digest |
| AF | Delegation before authorized rotation | `UNAVAILABLE` until regranted if required | Policy-controlled revalidation |
| AG | Explicit reapproval after rotation | `AUTHORIZED` | New approval binds new protected digest |
| AH | Explicit regrant after rotation | `AUTHORIZED` | New delegation use binds new digest |
| AI | Authorized tool rotation | `AUTHORIZED` | Exact transition, supersession and head |
| AJ | Unauthorized tool rotation | `UNAVAILABLE` | Transition authority missing |
| AK | Authorized connector rotation | `AUTHORIZED` | Exact handoff and downstream joins |
| AL | Unauthorized connector rotation | `UNAVAILABLE` | Handoff unavailable |
| AM | Authorized backend migration | `AUTHORIZED` | Migration and revalidation complete |
| AN | Unauthorized backend migration | `UNAVAILABLE` | Migration authority missing |
| AO | Authorized credential rotation | `AUTHORIZED` | Issuer/current transition exact |
| AP | Unauthorized credential replacement | `UNAVAILABLE` | Credential transition missing |
| AQ | Authorized permission expansion | `AUTHORIZED` after explicit expansion and required revalidation | No implicit widening |
| AR | Unauthorized permission expansion | `UNAVAILABLE` | Protected scope/head mismatch |
| AS | Narrowing still covers effect | `AUTHORIZED` if policy permits continuity | Exact subset proof |
| AT | Narrowing excludes effect | `UNAVAILABLE` | Terminal effect outside current scope |
| AU | Tool shopping | `UNAVAILABLE` | Unique protected selection required |
| AV | Backend shopping | `UNAVAILABLE` | All-applicable policy detects candidates |
| AW | Favorable connector selection | `UNAVAILABLE` | Candidate/verifier cannot select head |
| AX | Conflicting backend records | `UNAVAILABLE` | Unique current head unavailable |
| AY | Conflicting connector generations | `UNAVAILABLE` | Ordering/currentness conflict |
| AZ | Backend unavailable | `UNAVAILABLE` | Required protected layer missing |
| BA | Credential unavailable | `UNAVAILABLE` | Required credential admission missing |
| BB | Permission scope unavailable | `UNAVAILABLE` | Effective scope cannot be established |
| BC | Tool available, backend stale | `UNAVAILABLE` | Every layer must be current |
| BD | Backend current, connector stale | `UNAVAILABLE` | Every layer must be current |
| BE | Connector current, credential stale | `UNAVAILABLE` | Every layer must be current |
| BF | Old backend after migration | `UNAVAILABLE` | Superseded head cannot be reused |
| BG | Old connector after rotation | `UNAVAILABLE` | Superseded generation rejected |
| BH | Old credential after rotation | `UNAVAILABLE` | Superseded credential rejected |
| BI | Successor reuses predecessor context | `UNAVAILABLE` | Terminal use is successor-specific |
| BJ | Fresh successor authorization | `AUTHORIZED` | Fresh context and authority chain exact |
| BK | Queue resumes after backend migration | `UNAVAILABLE` until revalidated | T3 selected head changed |
| BL | Queue resumes after credential rotation | `UNAVAILABLE` until revalidated | Credential/context digest changed |
| BM | Queue resumes after scope expansion | `UNAVAILABLE` until explicitly revalidated | No implicit widening |
| BN | Exact fresh execution-time revalidation | `AUTHORIZED` | Current head/use and dependencies exact |
| BO | Fresh genesis tool context | `AUTHORIZED` | Root-issued genesis and current use exact |

## 24. Positive paths

The following remain reachable and must have independent fixture expectations:

1. Policy `NONE` where no tool is applicable.
2. Exact unchanged tool→connector→backend→target context.
3. Current connector and credential with exact permission scope.
4. Authorized tool rotation and connector handoff.
5. Authorized backend/operator migration.
6. Authorized credential rotation.
7. Scope narrowing that still covers the exact effect.
8. Explicitly authorized expansion followed by required approval/delegation revalidation.
9. Fresh approval and regrant after backend transition.
10. Exact proxy/relay/wrapper lineage.
11. Fresh genesis.
12. Fresh successor-specific context.
13. Fresh T3 revalidation after queue delay.

Each reaches `AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED` only after every pre-existing authority requirement also succeeds.

## 25. Existing invariant and field mapping

- `INV-CONT`: exact component generations, context digest, ordered transitions and T1/T3 use continuity.
- `INV-DISC`: protected policy/source selection; no candidate, tool, connector, verifier, approval or delegation self-selection.
- `INV-BND`: exact boundary/epoch and execution-context applicability for every layer.
- `INV-EVD`: identity claims, authentication, reachability, signatures and self-reports remain evidence rather than authority.
- `INV-USE`: exact credential/permission/effect and protected terminal-use binding.
- `INV-CLO`: complete ordered proxy/relay/wrapper lineage and aggregate effect closure.

Existing structures are reused:

- `evidence_binding` and observation coverage establish ordered visibility of transitions;
- `binding_source_authority`, lifecycle, ordering and freshness establish protected currentness;
- `identity_basis`, `boundary_epoch` and execution context constrain applicability;
- the mutation registry routes observed tool/credential discontinuities into revalidation;
- verifier-state anchoring and protected manifests prevent candidate reconstruction;
- source-domain/control-plane relations establish source independence;
- delegation and Human Approval consume, but cannot create, the protected context;
- terminal consumption/use binds the exact effect-capable target.

## 26. Fixture migration implications

Implementation requires one atomic migration of all 342 maintained fixtures because protected target applicability must be decided independently for every decision:

- fixtures with no applicable effect-capable tool receive an exact root-issued `NONE` policy;
- fixtures exercising execution receive a complete current protected context matching their existing normative intent;
- the 55 Human Approval fixtures retain their outcomes while approval gains an exact protected-context join;
- delegated fixtures retain their outcomes while terminal delegation use gains the same context digest;
- no candidate-controlled compatibility fallback is permitted;
- no committed intermediate state may mix protected and unprotected tool semantics.

The hostile implementation plan should allocate `LAB-V1-343` through at least `LAB-V1-409` for one independent A–BO matrix case each, consolidating only where a single fixture unambiguously tests multiple aliases without weakening coverage. Existing expectations do not change merely to satisfy implementation.

## 27. Expected implementation surface and size

Expected executable surfaces:

- `authority_lab/model.py`: strict protected records, candidate use relation and immutable parsers;
- `authority_lab/oracle.py`: canonical context digest, protected joins, transitions, selection and exact terminal use;
- `authority_lab/runner.py`: reject candidate protected-context injection and load the harness-owned context;
- `authority_lab/README.md`: public executable semantics and trust boundary;
- `tests/test_authority_lab.py`: independent hostile and positive tests;
- `cases/authority_lab/trusted_anchor_state.json`: atomic 342-fixture policy/context migration;
- maintained fixtures only if their candidate use relation is required;
- new fixtures beginning at `LAB-V1-343`.

Estimated implementation size is medium-to-large: approximately 600–1,000 executable/test lines plus protected manifest and fixture expansion. The fixture JSON diff will be much larger mechanically. Expected focused tests: 18–30. Expected new fixtures: approximately 67 (`LAB-V1-343`–`LAB-V1-409`) if every A–BO row receives one fixture. This estimate must be reported before implementation; it is not authorization to implement.

## 28. Residual trust boundary

The deterministic oracle cannot directly observe external execution. It trusts admitted facts concerning runtime routing, DNS/service discovery, provider/operator identity, endpoint measurement, connector implementation, service-account control, credential/key custody, effective remote permissions, remote policy enforcement, event delivery, canonical effect construction, protected-state durability and ultimate root correctness.

If every admitted source falsely reports the same tool/backend/credential/permission history and no independently anchored contradiction survives, deterministic local detection may be impossible. The design closes authority disappearance inside admitted input; it does not manufacture trustworthy instrumentation.

## 29. Hostile design review

The proposed design was attacked as follows:

| Attack | Why it does not survive the proposed design |
|---|---|
| Candidate recomputes every local digest | Protected selection and terminal-use heads retain the authoritative context digest |
| Stable tool label hides backend change | Backend and target identities/generations are independently protected digest members |
| Stable connector label hides generation | Connector generation and ordering head must match exactly |
| Same credential ID hides generation | Credential generation is independently selected and digest-bound |
| Same credential generation hides expanded scope | Permission record has its own identity/generation/head and transition |
| Proxy preserves label but changes target | Entire ordered intermediary lineage and terminal target are digest-bound |
| Approval remains structurally exact | Approval must equal the current protected context digest at use time |
| Delegation remains structurally exact | Delegation terminal use must equal that same protected digest |
| Tool shopping chooses favorable backend | Root-issued all-applicable policy requires one unique head |
| Rotation self-authorizes | Neither endpoint nor consumer can issue the protected transition |
| Backend declares itself current | Currentness comes from protected lifecycle/order/source relations |
| Connector declares continuity | Exact root-issued transition and successor admission are required |
| Registered mutation bypasses target head | Mutation revalidation must culminate in the protected selected head/use |
| Authorized rotation is blocked | Explicit transition, admission, supersession and new use form a positive path |
| Fresh reapproval/regrant is blocked | Both may bind the new context digest after independent transition authority succeeds |
| Unchanged positive is blocked | Exact existing head/digest/use remains valid without artificial rotation |

No in-scope bypass survives the proposed relational checks. This is a hostile design result, not executable proof. Parser defects, implementation omissions and external-source compromise remain possible until separately tested.

## 30. Frozen-contract sufficiency and verdict

Tool/connector continuity is authority-relevant relational state. It does not describe a new public decision coordinate. Existing invariants already require continuity, non-self-authorization, exact boundary applicability, evidence/authority separation, exact use and closed execution lineage. Existing outcomes already distinguish uncertainty from prohibition.

Therefore `authority-lab-v1`, six tuple coordinates, six invariants and three outcomes remain sufficient. No seventh coordinate, seventh invariant, fourth outcome or schema version is justified.

**PASS — NO REPRODUCIBLE IN-SCOPE TOOL-LABEL, CONNECTOR, BACKEND, CREDENTIAL, PERMISSION, OR EXECUTION-TARGET CONTINUITY BYPASS SURVIVES THE PROPOSED DESIGN**

PASS means the proposed design resisted the bounded attacks above. It is not proof of implementation correctness, production observability, physical-world truth or universal security.
