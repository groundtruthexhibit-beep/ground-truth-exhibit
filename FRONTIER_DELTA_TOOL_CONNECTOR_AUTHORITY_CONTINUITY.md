# Frontier Delta: Tool / Connector Authority Continuity

## 1. Exact baseline

This research slice starts from `97bd9282da5f7b674009c78a080763de9bd16db4` (`fix: enforce Authority Lab human approval continuity`) on `fix/authority-lab-v1-human-approval-continuity`. At that exact head, 237/237 public tests and 342/342 Authority Lab fixtures pass. The schema remains `authority-lab-v1`; the public architecture remains six tuple coordinates, six invariants, and three outcomes. This document changes no executable file or maintained fixture.

The prior approval repair correctly rejects a direct edit to its protected `tool_backend_id`. The delegation evaluator likewise checks that its protected terminal use names a tool admitted by the terminal grant. Those local checks are not a general tool/connector authority model.

## 2. Current tool / connector model

The executable model has four relevant surfaces:

1. The immutable mutation registry recognizes scalar `tool_connector_identity` and legacy alias `connector_endpoint`. A recorded mutation has `CONTROL_REESTABLISHMENT` effect and requires `EXECUTION_CONTROL` observation scope.
2. Delegation scopes contain a set of `tools`; the selected protected terminal use must name one of them.
3. Human approval binds one scalar `tool_backend_id` plus `credential_generation` into its policy, effect digest, envelope, and use relation.
4. Generic T3 facts and `required_values` can contain `tool_connector_identity`, `credential_identity`, or arbitrary permission/backend facts, but no independently protected relation selects their authority source or joins them to the actual effect-capable target.

The registered mutation path fails closed. A `tool_connector_identity: TOOL-A -> TOOL-B` mutation, with T3 reporting `TOOL-B`, returns `UNAVAILABLE / T1_T3_RELATIONSHIP_UNAVAILABLE`. The defect lies beside that path: tool/backend identity is not mandatory protected state, and a stable scalar label has no typed internal decomposition.

## 3. Tool identity is not backend identity

The current scalar can name `payments`, but cannot establish which provider, endpoint, process generation, service account, credential generation, permission set, execution target, or operator actually implements `payments`. Consequently these two worlds can collapse into the same admitted input:

- world 1: `payments` continuously addresses backend A;
- world 2: `payments` is redirected to backend B while the label remains `payments`.

The oracle does not confuse two protected backend identities. It has no general protected backend identity to compare. Adding an explicit candidate fact does not cure that absence: candidate-controlled fact/value equality is not source authority.

## 4. Credential and permission model

`credential_identity` is a registered scalar mutation target. Human approval binds only a numeric `credential_generation`; delegation scopes bind allowed actions and tools, not the credential or the backend's effective permission set. There is no general protected record binding credential identity/generation to issuer, principal, tool, connector, backend, endpoint, exact permission scope, lifecycle, ordering, boundary, and current effect.

Therefore credential rotation and permission expansion are correctly blocked only when represented as a registered discontinuity or as a mismatch inside the repaired approval/delegation relation. A candidate-supplied `credential_identity=CREDENTIAL-GEN-2` or `permission_scope=READ,WRITE`, made a required fact with the same candidate-required value, still coexists with `AUTHORIZED`.

## 5. Hostile matrix A–BJ

`AUTHORIZED*` means the unchanged positive authority path still authorizes while the asserted external tool world differs or a candidate-only fact reports the difference. It is the demonstrated defect, not a claim that the changed world is truly admitted. `UNAVAILABLE` means an explicit registered/bound mismatch already fails closed. “Not representable” means the required positive protected transition does not yet exist.

| ID | Hostile case | Current result | Desired result | Classification / reason | Existing invariants | Repair inside v1? |
|---|---|---|---|---|---|---|
| A | Exact tool/backend unchanged | `AUTHORIZED` | `AUTHORIZED` | Positive control, but identity is only locally exact | CONT, BND, EVD, USE | Yes |
| B | Same tool name, different backend | `AUTHORIZED*` | `UNAVAILABLE` | Executable defect: stable label hides target | CONT, DISC, EVD | Yes |
| C | Same connector name, different provider | `AUTHORIZED*` | `UNAVAILABLE` | Executable defect | CONT, DISC, BND | Yes |
| D | Same endpoint label, different execution target | `AUTHORIZED*` | `UNAVAILABLE` | Executable defect | CONT, EVD, USE | Yes |
| E | Same API route, different authority context | `AUTHORIZED*` | `UNAVAILABLE` | Executable defect | CONT, BND, USE | Yes |
| F | Credential generation changes | Candidate fact: `AUTHORIZED`; registered mutation: `UNAVAILABLE` | `UNAVAILABLE` | Incomplete mandatory join | CONT, DISC, USE | Yes |
| G | Credential key changes | `AUTHORIZED*` unless registered | `UNAVAILABLE` | Executable defect | CONT, DISC, EVD | Yes |
| H | Permission scope expands | Candidate fact: `AUTHORIZED` | `UNAVAILABLE` | Executable defect | CONT, DISC, USE | Yes |
| I | Permission scope narrows | `AUTHORIZED*` | `UNAVAILABLE` if requested effect no longer covered | CONT, USE | Yes |
| J | OAuth/API scope changes | `AUTHORIZED*` | `UNAVAILABLE` | Executable defect | CONT, EVD, USE | Yes |
| K | Backend operator changes | `AUTHORIZED*` | `UNAVAILABLE` | Source-authority/currentness gap | CONT, DISC, BND | Yes |
| L | Tool process restarts | `AUTHORIZED*` | `UNAVAILABLE` absent continuity | CONT, DISC, USE | Yes |
| M | Tool identity reused after replacement | `AUTHORIZED*` | `UNAVAILABLE` | Label/ABA defect | CONT, DISC | Yes |
| N | Connector identity reused after replacement | `AUTHORIZED*` | `UNAVAILABLE` | Label/ABA defect | CONT, DISC | Yes |
| O | Cached identity survives rotation | `AUTHORIZED*` | `UNAVAILABLE` | Currentness/replay defect | CONT, EVD | Yes |
| P | Stale connector metadata | `AUTHORIZED*` | `UNAVAILABLE` | Freshness absent | CONT, EVD | Yes |
| Q | Stale backend generation | `AUTHORIZED*` | `UNAVAILABLE` | Generation absent | CONT, DISC | Yes |
| R | Stale credential binding | `AUTHORIZED*` | `UNAVAILABLE` | Credential relationship absent | CONT, EVD, USE | Yes |
| S | Proxy replaces direct tool | `AUTHORIZED*` | `UNAVAILABLE` absent admitted lineage | CONT, DISC, USE | Yes |
| T | Relay uses different backend | `AUTHORIZED*` | `UNAVAILABLE` | Relay cannot transfer authority | CONT, DISC, BND | Yes |
| U | Wrapper hides substitution | `AUTHORIZED*` | `UNAVAILABLE` | Wrapper laundering | CONT, EVD | Yes |
| V | Service account changes under label | `AUTHORIZED*` | `UNAVAILABLE` | Principal/credential gap | CONT, DISC, USE | Yes |
| W | Planner approves A, executor uses B | Hidden substitution: `AUTHORIZED*`; direct approval edit: `UNAVAILABLE` | `UNAVAILABLE` | Actual target not joined | CONT, EVD, USE | Yes |
| X | Delegation grants A, use on B | Direct protected-use edit: `UNAVAILABLE`; hidden backend: `AUTHORIZED*` | `UNAVAILABLE` | Delegation checks label, not backend identity | CONT, DISC, USE | Yes |
| Y | Approval binds A, execution on B | Direct binding edit: `UNAVAILABLE / HUMAN_APPROVAL_SCOPE_UNAVAILABLE`; hidden backend: `AUTHORIZED*` | `UNAVAILABLE` | Approval-local check is sound; execution join is missing | CONT, EVD, USE | Yes |
| Z | Approval/delegation bind connector label only | `AUTHORIZED*` | `UNAVAILABLE` | Exact shared label is not target continuity | CONT, EVD, USE | Yes |
| AA | Explicit authorized tool rotation | Not representable as a protected positive transition | `AUTHORIZED` | Implementation obligation | CONT, DISC, EVD | Yes |
| AB | Explicit authorized connector rotation | Not representable | `AUTHORIZED` | Implementation obligation | CONT, DISC, BND | Yes |
| AC | Explicit authorized credential rotation | Not representable generally | `AUTHORIZED` | Implementation obligation | CONT, DISC, USE | Yes |
| AD | Explicit authorized backend migration | Not representable | `AUTHORIZED` | Implementation obligation | CONT, BND, EVD | Yes |
| AE | Unauthorized backend migration | Hidden: `AUTHORIZED*`; explicit registered change: `UNAVAILABLE` | `UNAVAILABLE` | Executable defect on hidden/stable-label path | CONT, DISC | Yes |
| AF | Unauthorized connector replacement | Hidden: `AUTHORIZED*`; registered alias change: `UNAVAILABLE` | `UNAVAILABLE` | Executable defect | CONT, DISC | Yes |
| AG | Authorized permission expansion | Not representable as protected transition | `AUTHORIZED` after reauthorization | Implementation obligation | CONT, DISC, USE | Yes |
| AH | Unauthorized permission expansion | Candidate fact: `AUTHORIZED` | `UNAVAILABLE` | Executable defect | CONT, DISC, USE | Yes |
| AI | Endpoint redirect/rebinding | `AUTHORIZED*` | `UNAVAILABLE` | Executable defect | CONT, BND, EVD | Yes |
| AJ | Backend changes during queue | `AUTHORIZED*` | `UNAVAILABLE` | Execution-time currentness absent | CONT, EVD, USE | Yes |
| AK | Connector changes after approval | Hidden: `AUTHORIZED*`; direct approval mismatch: `UNAVAILABLE` | `UNAVAILABLE` | Missing actual-target join | CONT, EVD, USE | Yes |
| AL | Connector changes after delegation | Hidden: `AUTHORIZED*`; direct terminal-use mismatch: `UNAVAILABLE` | `UNAVAILABLE` | Missing actual-target join | CONT, DISC, USE | Yes |
| AM | Tool changes after verifier recovery | `AUTHORIZED*` | `UNAVAILABLE` | Recovery does not establish tool target | CONT, EVD | Yes |
| AN | Tool changes after successor transition | `AUTHORIZED*` | `UNAVAILABLE` | Successor chain lacks mandatory tool join | CONT, DISC, USE | Yes |
| AO | Predecessor tool authority reused by successor | `AUTHORIZED*` if label reused | `UNAVAILABLE` | Non-portability gap | CONT, DISC, USE | Yes |
| AP | Fresh successor/tool reauthorization | Successor may authorize; tool-specific proof absent | `AUTHORIZED` only with fresh tool chain | Positive path incomplete | CONT, DISC, BND, USE | Yes |
| AQ | Proxy with exact preserved lineage | No protected proxy lineage relation | `AUTHORIZED` with exact current lineage | Positive path not representable | CONT, EVD | Yes |
| AR | Exact protected connector handoff | No general connector handoff relation | `AUTHORIZED` | Positive path not representable | CONT, DISC, BND | Yes |
| AS | Tool unavailable | Baseline can remain `AUTHORIZED`; explicitly required `UNKNOWN` is `UNAVAILABLE` | `UNAVAILABLE` when tool is applicable | Mandatory-selection defect | CONT, EVD | Yes |
| AT | Backend identity unavailable | Baseline can remain `AUTHORIZED` | `UNAVAILABLE` | Mandatory-selection defect | CONT, EVD | Yes |
| AU | Conflicting backend identities | Unconsumed facts can coexist with `AUTHORIZED*` | `UNAVAILABLE` | Conflict not selected | CONT, EVD | Yes |
| AV | Conflicting connector generations | Unconsumed facts can coexist with `AUTHORIZED*` | `UNAVAILABLE` | Ordering/currentness absent | CONT, DISC, EVD | Yes |
| AW | Multiple candidates, favorable selection | Candidate-required favorable value: `AUTHORIZED` | `UNAVAILABLE` | Tool shopping | DISC, EVD, USE | Yes |
| AX | Tool shopping | `AUTHORIZED` in executable candidate-fact reproducer | `UNAVAILABLE` | Selection authority absent | DISC, EVD, USE | Yes |
| AY | Backend shopping | `AUTHORIZED*` | `UNAVAILABLE` | Selection authority absent | DISC, EVD, USE | Yes |
| AZ | Same effect, materially different backend | `AUTHORIZED*` | `UNAVAILABLE` absent admitted equivalence | CONT, EVD, USE | Yes |
| BA | Different effect, same tool label | Hidden: `AUTHORIZED*`; approval effect edit: `UNAVAILABLE` | `UNAVAILABLE` | Effect join incomplete outside approval | CONT, EVD, USE | Yes |
| BB | Tool reports its own identity | Candidate fact can coexist with `AUTHORIZED` | `UNAVAILABLE` | Self-attestation | DISC, EVD | Yes |
| BC | Connector reports own currentness | Candidate fact can coexist with `AUTHORIZED` | `UNAVAILABLE` | Self-attestation | DISC, EVD | Yes |
| BD | Candidate supplies tool/backend identity | `AUTHORIZED` | `UNAVAILABLE` | Exact executable counterexample | DISC, EVD, USE | Yes |
| BE | Candidate supplies permission scope | `AUTHORIZED` | `UNAVAILABLE` | Exact executable counterexample | DISC, EVD, USE | Yes |
| BF | Protected source supplies identity | No general protected source relation | `AUTHORIZED` when exact/current | Required positive model absent | CONT, BND, EVD | Yes |
| BG | Protected rotation + approval revalidation | No rotation relation; fresh exact approval alone does not prove backend transition | `AUTHORIZED` | Positive path not representable | CONT, EVD, USE | Yes |
| BH | Protected rotation + delegation revalidation | No rotation relation | `AUTHORIZED` | Positive path not representable | CONT, DISC, USE | Yes |
| BI | Fresh genesis tool context | General authority can authorize; tool genesis not established | `AUTHORIZED` with protected genesis | Positive path incomplete | CONT, BND, EVD | Yes |
| BJ | Fresh successor tool context | General successor can authorize; tool context not established | `AUTHORIZED` with successor-specific tool chain | Positive path incomplete | CONT, DISC, USE | Yes |

## 6. Executable reproducers

The smallest reproducer starts from policy-`NONE` positive fixture `LAB-V1-337` and adds a schema-valid canonical registry fact as a candidate-required equality:

```python
payload = load_fixture("cases/authority_lab/LAB-V1-337.json")
payload["t3"]["facts"]["tool_connector_identity"] = {
    "state": "KNOWN", "value": "payments@BACKEND-B"
}
payload["t3"]["required_facts"].append("tool_connector_identity")
payload["t3"]["required_values"]["tool_connector_identity"] = "payments@BACKEND-B"
evaluate(OracleInput.from_fixture(payload))
```

Actual result:

```text
AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED
```

The same fact added to exact-approval positive `LAB-V1-338` and delegated positive `LAB-V1-253` also returns `AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED`. Candidate facts `credential_identity=CREDENTIAL-GEN-2` and `permission_scope=READ,WRITE` produce the same result. A favorable `tool_connector_identity=TOOL-A` plus a second visible `backend_candidate=TOOL-B` also remains `AUTHORIZED`.

Controls:

- a registered `tool_connector_identity: TOOL-A -> TOOL-B` mutation returns `UNAVAILABLE / T1_T3_RELATIONSHIP_UNAVAILABLE`;
- a registered credential mutation returns the same fail-closed result;
- changing repaired human approval `tool_backend_id` returns `UNAVAILABLE / HUMAN_APPROVAL_SCOPE_UNAVAILABLE`;
- the delegated baseline is authorized only while its protected terminal-use tool stays inside its grant scope.

Thus mutation-registry closure is working. The reproducer establishes a different gap: no protected mandatory tool/backend selection and actual-target join exists.

## 7. Minimal counterexample

At T1, the ordinary tuple, grant, objective, observation, anchor, control-plane, delegation (if applicable), and approval (if applicable) chain is valid for the displayed service `payments` backed by A.

At T2, `payments` is rebound to effect-capable backend B, or its credential permission expands from `READ` to `WRITE`. The scalar label visible to the existing approval/delegation relationships remains unchanged. Candidate-visible facts may even state B or the expanded scope.

At T3, no independently protected source selects B, establishes its identity/generation, authorizes the transition, or binds it to the exact use. Nevertheless the unchanged positive fixture plus those facts returns `AUTHORIZED`.

Expected result is `UNAVAILABLE`. If a current authoritative fact explicitly prohibited or revoked B, the result should be `DENIED`.

## 8. Human approval interaction

The Human Approval Continuity repair is locally sound: changing `tool_backend_id`, credential generation, effect, request digest, or protected request head fails closed. It does not prove that the scalar named by `tool_backend_id` is the actual current effect-capable backend. An exact approval for label A therefore survives a hidden A-to-B rebinding. Approval must join a separately protected current tool/backend selection; it must not become that selection authority.

## 9. Delegation interaction

Delegation correctly checks action, artifact, tool label, boundary, subject, and use against the protected grant chain. It does not bind the named tool to a protected backend/connector/credential identity. A tool label admitted by the grant can therefore resolve to an unadmitted backend. Delegation revalidation should consume the same independently selected tool/backend head as approval and execution, without allowing either relation to select a favorable tool.

## 10. Lifecycle and currentness

Process liveness, endpoint reachability, successful authentication, credential validity, or a stable label does not establish current authority applicability. A repair would need exact protected lifecycle and ordering for:

- tool, connector, backend, endpoint and service-account identity/generation;
- credential identity/generation and exact effective permission scope;
- source authority, boundary and objective applicability;
- current selected target and any rotation/handoff/supersession;
- execution-time use after queue, retry, recovery, restart, or successor events.

Missing or ambiguous currentness should be `UNAVAILABLE`; exact current prohibition/revocation should be `DENIED`.

## 11. Tool shopping

The candidate currently controls which optional facts and required-value comparisons appear. It can describe the favorable tool while an alternative backend fact remains unconsumed. Selection must instead be `ALL_APPLICABLE` or one exact root/objective-authorized target head. Multiple same-position heads, conflicting generations, or unresolved aliases must fail closed. Neither the requester, planner, verifier, tool, connector, wrapper, approval, nor delegation chain may select its own favorable backend.

## 12. Authorized rotation positive controls

The current lab has no general protected tool/connector rotation relation, so the required positive controls cannot yet prove tool-specific continuity. A smallest repair must preserve these paths:

1. exact unchanged current tool/backend;
2. root-authorized A-to-B tool or connector rotation with exact old/new identities, generations, scope, lifecycle, ordering and execution-time target selection;
3. credential rotation with non-widening or explicitly authorized changed permissions;
4. backend migration followed by exact approval and delegation revalidation;
5. fresh genesis and fresh successor-specific tool context;
6. exact proxy/handoff lineage where the protected policy permits it.

Each remains conjunctive with every existing authority requirement and may reach `AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED`.

## 13. Invariant mapping

- `INV-CONT`: the effect-capable target and credential/permission relationship must remain continuous through T3; a stable name is insufficient.
- `INV-DISC`: the candidate, tool, connector, wrapper, verifier, approval, or delegate cannot select or self-assert its own authority-bearing target.
- `INV-BND`: connector/backend identity and credential scope are applicable only inside the exact admitted boundary and epoch.
- `INV-EVD`: labels, reachability, authentication success, signatures, and self-reported metadata are evidence, not source authority.
- `INV-USE`: the selected tool/backend, credential and effective permissions must bind the exact authority-consuming use at execution time.
- `INV-CLO`: composite/proxy/wrapper execution must preserve a closed exact lineage; omitted downstream effects cannot inherit authority.

No seventh invariant is needed. The defect is a missing typed relation and mandatory join under existing invariants.

## 14. Contract sufficiency

The six-coordinate tuple need not gain a tool coordinate. Tool/backend state is authority-relevant relational state, like objective binding, observation, delegation, approval and verifier anchoring. `UNAVAILABLE` already represents missing or ambiguous continuity, and `DENIED` already represents an exact current prohibition. The frozen 6/6/3 architecture remains sufficient.

## 15. Smallest possible repair direction

Design one harness-owned, strictly typed tool/connector authority context and one exact candidate use relation. Reuse existing `evidence_binding`, freshness, lifecycle, ordering, source-authority, boundary, delegation, approval and consumption semantics. The protected context should bind:

- root-selected policy and `ALL_APPLICABLE` target selection;
- tool, connector, backend, endpoint and service-account identities/generations;
- credential identity/generation and exact effective permissions;
- canonical effect-capable target digest;
- source authority, boundary/epoch, objective/contract, lifecycle, ordering and freshness;
- rotation/handoff/supersession edges and a unique current head;
- exact T3 execution/use relation shared by delegation and approval.

Unknown, missing, stale, conflicting, candidate-supplied, self-reported, or shopping-prone target state should be `UNAVAILABLE`. Current authoritative revocation/prohibition should be `DENIED`. Explicit current rotations and fresh genesis/successor contexts should keep `AUTHORIZED` reachable.

Implementation would be medium-to-large rather than architectural: approximately four executable surfaces (`model.py`, `oracle.py`, `runner.py`, README/tests), one protected manifest extension, an atomic migration of all 342 maintained fixtures to an exact `NONE` or current tool policy, and roughly 40–60 focused hostile/positive fixtures. No schema version, coordinate, invariant, or outcome expansion appears necessary.

## 16. Residual external trust boundary

Even after such a repair, the deterministic lab would trust admitted external truth about runtime routing, DNS/service discovery, connector implementation, provider/operator identity, endpoint measurement, credential/key custody, effective remote permissions, policy enforcement by the backend, event delivery, canonical target construction, and ultimate root correctness. If every admitted source reports one fabricated but internally exact target history and no contrary state survives, the oracle cannot infer the hidden physical world.

## 17. Exact hostile-research verdict

**FAIL — REPRODUCIBLE IN-SCOPE TOOL OR CONNECTOR AUTHORITY-CONTINUITY COUNTEREXAMPLE FOUND**

The failure is specific: a registered observed mutation fails closed, and direct edits to repaired approval/delegation tool bindings fail closed, but no mandatory independently protected relation binds their stable tool label to the actual current effect-capable backend, connector, credential and permission scope. Candidate-controlled equality and stable labels can therefore coexist with `AUTHORIZED` across a materially different execution target.

`FAIL` records a bounded reproducible counterexample. It does not prove exploitability in a production system or exhaust the frontier.
