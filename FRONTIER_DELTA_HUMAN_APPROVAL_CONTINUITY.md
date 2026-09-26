# Frontier Delta: Human Approval Continuity

## 1. Exact baseline

Research began from `dd917bc24b36c6f61f4efa8ebda9fada98a0cf2c` on `fix/authority-lab-v1-delegation-authority-continuity`. That exact head had 225 public tests and 287 Authority Lab fixtures passing, schema `authority-lab-v1`, and the frozen six tuple coordinates, six invariants, and three outcomes. This slice changes no executable code or fixture.

## 2. Current human/operator authority representation

The public contract mentions an operator only as a capability-bearing actor. Authority Lab has no typed human, operator, approval, consent, approval policy, approval use, or approval revocation relation. It does have exact `subject` and `identity_basis`, objective binding, grants and consumption, protected delegation chains, lifecycle/order/freshness relations, boundary and execution context, observation, anchoring, and control-plane independence. Those relations can constrain an execution, but none establishes that a human approved its exact effect.

## 3. Approval model actually implemented today

`OracleInput.from_fixture` accepts arbitrary named T3 facts as generic `Fact` values. A name added to `required_facts` is checked for known/conflicting state and, unless it is one of the oracle-owned relational facts, exact equality with candidate-provided `required_values`. The evaluator does not assign semantics to an otherwise unknown required fact.

Consequently, a candidate can supply `human_approval = "yes"`, copy the same value into `required_values`, and satisfy the generic required-fact gate. This equality is not approval authority: both sides are candidate input. No human identity, source authority, canonical request/effect, lifecycle, freshness, ordering, use, or replay relationship is evaluated.

The mutation registry does fail closed on a visible unregistered `human_approval` mutation. That does not repair the defect: separately presented T3 inputs can reuse or replace the generic value without representing the approval change as a mutation.

## 4. Normative approval model

Human approval is evidence of authority only for the exact approved action in the exact approved context. Where an admitted decision contract requires approval, authorization requires a protected approval-source admission and an exact approval/use relationship binding the independently established human identity and identity basis to the canonical request/effect, artifact/resource, subject, executor/delegate, tool/backend, boundary/epoch, execution context, objective, delegation chain, session/generation, lifecycle, ordering, freshness, expiry, and use policy. Approval cannot establish its own source authority or repair unrelated missing authority.

Missing, stale, ambiguous, conflicting, replayed, transferred, widened, or not-provably-current approval is `UNAVAILABLE`. An exact current authoritative approval revocation, denial, or prohibition is `DENIED`. Exact current approval plus every other authority requirement may support `AUTHORIZED`.

## 5. Hostile matrix A–CO

`AUTH*` means the executable generic-required-fact reproducer can still return `AUTHORIZED` when the underlying C2 execution is otherwise independently authorized; it does not mean every malformed mutation bypasses existing checks. “Repair” means the case appears representable inside the current schema through typed internal relations.

| ID | Case | Current | Desired | Class / existing invariant mapping | Repair |
|---|---|---|---|---|---|
| A | Exact approval/action/immediate use | AUTH* | AUTHORIZED | Positive; INV-EVD/USE | Yes |
| B | Different artifact | AUTH* | UNAVAILABLE | Unconsumed binding; INV-CONT/EVD | Yes |
| C | Different resource | AUTH* | UNAVAILABLE | Unconsumed scope; INV-EVD/USE | Yes |
| D | Different effect | AUTH* | UNAVAILABLE | Effect mismatch; INV-EVD/USE/CLO | Yes |
| E | READ reused for WRITE | AUTH* | UNAVAILABLE | Scope widening; INV-EVD/USE | Yes |
| F | WRITE reused for DELETE | AUTH* | UNAVAILABLE | Scope widening; INV-EVD/USE | Yes |
| G | Different agent | AUTH* | UNAVAILABLE | Subject transfer; INV-CONT/DISC | Yes |
| H | Different delegate | AUTH* | UNAVAILABLE | Delegation transfer; INV-DISC/USE | Yes |
| I | Different executor | AUTH* | UNAVAILABLE | Use mismatch; INV-CONT/USE | Yes |
| J | Successor agent | AUTH* | UNAVAILABLE | Successor portability; INV-CONT/DISC | Yes |
| K | Restart with predecessor approval | AUTH* | UNAVAILABLE | Replay; INV-CONT/USE | Yes |
| L | Execution-context change | AUTH* | UNAVAILABLE | Control discontinuity; INV-CONT/BND | Yes |
| M | Boundary-epoch change | AUTH* | UNAVAILABLE | Boundary mismatch; INV-BND | Yes |
| N | Subject transition | AUTH* | UNAVAILABLE | Identity discontinuity; INV-CONT/DISC | Yes |
| O | Artifact mutates after approval | AUTH* | UNAVAILABLE | Stale binding; INV-CONT/EVD | Yes |
| P | Payload mutates after approval | AUTH* | UNAVAILABLE | Canonical effect mismatch; INV-EVD/CLO | Yes |
| Q | Objective changes | AUTH* | UNAVAILABLE | Objective mismatch; INV-EVD/CLO | Yes |
| R | Execution parameters change | AUTH* | UNAVAILABLE | Effect mismatch; INV-EVD/USE | Yes |
| S | Tool substitution | AUTH* | UNAVAILABLE | Control/effect mismatch; INV-CONT/USE | Yes |
| T | Connector/backend substitution | AUTH* | UNAVAILABLE | Boundary/control mismatch; INV-BND/USE | Yes |
| U | Credential change | AUTH* | UNAVAILABLE | Identity discontinuity; INV-CONT/DISC | Yes |
| V | Permission/scope expansion | AUTH* | UNAVAILABLE | Widening; INV-DISC/USE | Yes |
| W | Delegation chain changes | AUTH* | UNAVAILABLE | Chain mismatch; INV-DISC/USE | Yes |
| X | Delegate changes | AUTH* | UNAVAILABLE | Principal mismatch; INV-CONT/DISC | Yes |
| Y | Planner/executor split changes | AUTH* | UNAVAILABLE | Effect/principal mismatch; INV-DISC/USE | Yes |
| Z | Service-account identity changes | AUTH* | UNAVAILABLE | Identity mismatch; INV-CONT/DISC | Yes |
| AA | Same-session second use | AUTH* | UNAVAILABLE if one-shot | Replay; INV-USE | Yes |
| AB | Different-session replay | AUTH* | UNAVAILABLE | Replay/session mismatch; INV-USE | Yes |
| AC | Another agent replays | AUTH* | UNAVAILABLE | Transfer/replay; INV-CONT/USE | Yes |
| AD | Replay after restart | AUTH* | UNAVAILABLE | Restart replay; INV-CONT/USE | Yes |
| AE | Replay after snapshot restore | AUTH* | UNAVAILABLE | Rollback; INV-CONT/USE | Yes |
| AF | Replay after recovery | AUTH* | UNAVAILABLE | Recovery replay; INV-CONT/USE | Yes |
| AG | Conversation/session copy | AUTH* | UNAVAILABLE | Session transfer; INV-CONT/USE | Yes |
| AH | Generic `yes` | AUTH* | UNAVAILABLE | No exact content; INV-EVD | Yes |
| AI | Text without human source | AUTH* | UNAVAILABLE | Source unavailable; INV-EVD/DISC | Yes |
| AJ | Model-generated `yes` | AUTH* | UNAVAILABLE | Self-authority; INV-DISC | Yes |
| AK | Agent attributes record to human | AUTH* | UNAVAILABLE | Self-asserted provenance; INV-DISC/EVD | Yes |
| AL | Proxy claims approval | AUTH* | UNAVAILABLE | Source authority missing; INV-DISC | Yes |
| AM | Wrong human | AUTH* | UNAVAILABLE | Identity mismatch; INV-CONT | Yes |
| AN | Stale human identity basis | AUTH* | UNAVAILABLE | Identity stale; INV-CONT | Yes |
| AO | Account/operator transition | AUTH* | UNAVAILABLE | Successor identity; INV-CONT/DISC | Yes |
| AP | Undelegated operator approval | AUTH* | UNAVAILABLE | Approval authority absent; INV-DISC | Yes |
| AQ | Action authority but no approval authority | AUTH* | UNAVAILABLE | Privilege confusion; INV-DISC | Yes |
| AR | Effect outside approval scope | AUTH* | UNAVAILABLE | Scope mismatch; INV-EVD/USE | Yes |
| AS | Expired approval | AUTH* | UNAVAILABLE | Lifecycle stale; INV-CONT/USE | Yes |
| AT | Freshness unavailable | AUTH* | UNAVAILABLE | Currentness missing; INV-CONT/EVD | Yes |
| AU | Superseded approval | AUTH* | UNAVAILABLE | Ordering missing; INV-CONT | Yes |
| AV | Approval revoked | AUTH* | DENIED | Revocation ignored; INV-CONT/DISC | Yes |
| AW | Approval denied/prohibited | AUTH* | DENIED | Prohibition ignored; INV-DISC | Yes |
| AX | Positive then current negative | AUTH* | DENIED | Later lifecycle ignored; INV-CONT/DISC | Yes |
| AY | Same authority conflicts | AUTH* | UNAVAILABLE | Conflict ignored; INV-EVD | Yes |
| AZ | Authorized humans conflict | AUTH* | UNAVAILABLE absent resolution | Conflict ignored; INV-EVD/DISC | Yes |
| BA | Policy requires one approver | AUTH* | AUTHORIZED only if exact | Policy/source not evaluated; INV-DISC | Yes |
| BB | Policy requires independent quorum | AUTH* | UNAVAILABLE unless complete | Required set absent; INV-DISC/EVD | Yes |
| BC | One effective human masquerades as quorum | AUTH* | UNAVAILABLE | Multiplicity != independence; INV-DISC | Yes |
| BD | Required approver set changes | AUTH* | UNAVAILABLE | Policy stale; INV-CONT | Yes |
| BE | Approval policy changes | AUTH* | UNAVAILABLE | Policy generation stale; INV-CONT | Yes |
| BF | Approval predates shutdown | AUTH* | UNAVAILABLE | Terminal discontinuity; INV-CONT/USE | Yes |
| BG | Approval after shutdown, before successor admission | AUTH* | UNAVAILABLE | Principal unavailable; INV-CONT/DISC | Yes |
| BH | Predecessor approval used by successor | AUTH* | UNAVAILABLE | Non-portability; INV-CONT/USE | Yes |
| BI | Fresh successor reapproval | AUTH* | AUTHORIZED | Positive; INV-CONT/USE | Yes |
| BJ | Approval predates verifier recovery | AUTH* | UNAVAILABLE absent exact continuity | Recovery currentness; INV-CONT/EVD | Yes |
| BK | Approval predates anchor recovery | AUTH* | UNAVAILABLE absent exact continuity | Anchor currentness; INV-CONT/EVD | Yes |
| BL | Approval predates adapter rotation | AUTH* | UNAVAILABLE absent exact continuity | Source transition; INV-CONT/EVD | Yes |
| BM | Approval predates witness handoff | AUTH* | UNAVAILABLE absent exact continuity | Evidence transition; INV-CONT/EVD | Yes |
| BN | Approval predates reconciliation | AUTH* | UNAVAILABLE absent exact continuity | Domain transition; INV-CONT/BND | Yes |
| BO | Approval predates role rotation | AUTH* | UNAVAILABLE absent exact continuity | Authority transition; INV-CONT/DISC | Yes |
| BP | Approval predates delegation regrant | AUTH* | UNAVAILABLE | Chain changed; INV-DISC/USE | Yes |
| BQ | Approval while other facts unresolved | UNAVAILABLE | UNAVAILABLE | Already blocked; all applicable | Existing |
| BR | Approval attempts to override UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | Already blocked | Existing |
| BS | Approval attempts to override DENIED | DENIED | DENIED | Already blocked | Existing |
| BT | Plan approval used for execution | AUTH* | UNAVAILABLE | Effect mismatch; INV-EVD/USE | Yes |
| BU | Preview/draft used for send/commit | AUTH* | UNAVAILABLE | Effect widening; INV-EVD/USE | Yes |
| BV | Calculate used for transact | AUTH* | UNAVAILABLE | Effect widening; INV-EVD/USE | Yes |
| BW | Navigate used for state mutation | AUTH* | UNAVAILABLE | Effect widening; INV-EVD/USE | Yes |
| BX | One tool through another tool | AUTH* | UNAVAILABLE | Tool mismatch; INV-CONT/USE | Yes |
| BY | API approval after backend redirect | AUTH* | UNAVAILABLE | Backend mismatch; INV-BND/USE | Yes |
| BZ | Queued, executed much later | AUTH* | UNAVAILABLE unless current | Freshness absent; INV-CONT/USE | Yes |
| CA | Scheduled action after authority change | AUTH* | UNAVAILABLE | Ordering/currentness; INV-CONT/USE | Yes |
| CB | Retry after state change | AUTH* | UNAVAILABLE | Retry is new use/context; INV-CONT/USE | Yes |
| CC | Second phase changes effect | AUTH* | UNAVAILABLE | Compound effect mismatch; INV-EVD/USE | Yes |
| CD | Larger amount | AUTH* | UNAVAILABLE | Bounded parameter widening; INV-EVD/USE | Yes |
| CE | Different recipient | AUTH* | UNAVAILABLE | Effect target mismatch; INV-EVD/USE | Yes |
| CF | Different destination | AUTH* | UNAVAILABLE | Boundary/effect mismatch; INV-BND/USE | Yes |
| CG | Decomposition changes aggregate effect | AUTH* | UNAVAILABLE | Aggregate effect absent; INV-EVD/CLO | Partial |
| CH | Exact immutable digest and unchanged use | AUTH* | AUTHORIZED | Positive; INV-EVD/USE | Yes |
| CI | Fresh approval after mutation | AUTH* | AUTHORIZED | Positive reapproval | Yes |
| CJ | Fresh approval after tool rotation | AUTH* | AUTHORIZED | Positive reapproval | Yes |
| CK | Fresh approval after delegation change | AUTH* | AUTHORIZED | Positive reapproval | Yes |
| CL | Fresh approval after successor | AUTH* | AUTHORIZED | Positive reapproval | Yes |
| CM | Explicit approval revocation | AUTH* | DENIED | Approval lifecycle absent; INV-DISC | Yes |
| CN | Missing required approval | UNAVAILABLE | UNAVAILABLE | Generic required gate blocks | Existing |
| CO | Policy does not require approval | AUTHORIZED | AUTHORIZED | Valid non-approval control | Existing |

## 6. Executable reproducers

The minimal reproducer starts from positive `LAB-V1-032`, adds a schema-valid fact, and makes it required using candidate-controlled equality:

```python
payload["t3"]["facts"]["human_approval"] = {"state": "KNOWN", "value": "yes"}
payload["t3"]["required_facts"].append("human_approval")
payload["t3"]["required_values"]["human_approval"] = "yes"
```

Current result: `AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED`.

Replacing `"yes"` with a structured but self-asserted record naming `MODEL-SELF`, `OTHER-HUMAN`, an expired approval, a revoked approval, or `use_policy=ONE_SHOT` produces the same result when `required_values` repeats it. Evaluating the same one-shot record twice independently produces `AUTHORIZED` twice.

The same stale record, claiming artifact `A1`, subject `S`, boundary epoch `B1`, execution context `E1`, and no delegation chain, was attached to independently valid positive cases for cross-boundary re-establishment (`LAB-V1-048`), successor admission (`LAB-V1-084`), verifier rotation (`LAB-V1-129`), and changed delegation chain (`LAB-V1-253`). Every case remained `AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED`.

Negative controls remained correct: attaching the same approval to missing-anchor `LAB-V1-138` returned `UNAVAILABLE / VERIFIER_STATE_ANCHOR_UNAVAILABLE`; arbitrary-delegator `LAB-V1-235` returned `UNAVAILABLE / DELEGATION_SOURCE_AUTHORITY_UNAVAILABLE`; and revoked-delegation `LAB-V1-247` returned `DENIED / DELEGATION_REVOKED`.

## 7. Minimal counterexample

The smallest counterexample is `human_approval="yes"` as a required generic fact in an otherwise positive input. Candidate equality is accepted as satisfaction of an authority-relevant approval requirement, so no independently admitted human, source, content, context, lifecycle, ordering, or use relationship is necessary. A second invocation reuses the same purported one-shot approval and authorizes again.

This is an executable implementation gap, not proof that every action needs human approval. It applies only when an authority objective or admitted decision contract requires human approval. `CO` remains valid: an objective that does not require human approval must not acquire a new universal gate.

## 8. Human identity analysis

`subject` and `identity_basis` can represent the executing subject, but they do not identify an approving human separately from that subject. Generic fact content self-identifies its alleged approver. Existing protected principal admission and source-authority patterns can represent a separately admitted human/operator identity without adding a tuple coordinate. Stable display names, account labels, credentials, service roles, and self-reported identities are insufficient; transitions require exact identity-basis and generation continuity.

## 9. Artifact/effect binding analysis

Current evidence, consumption, closure, and delegation relations strongly bind the execution itself, but an arbitrary `human_approval` fact is not joined to any of them. Approval needs a canonical request/effect digest whose domain-separated body includes the exact artifact/resource, semantic action, bounded parameters and targets, subject, executor, tool/backend, boundary/epoch, objective and contract, delegation-chain head, and execution context. An opaque display label or digest without a typed canonical body is insufficient.

## 10. Approval replay analysis

The evaluator has no approval-use ledger. Generic equality cannot distinguish first use from same-session, cross-session, restart, snapshot, recovery, or successor replay. Existing consumption and protected durable-state patterns can carry approval-specific one-shot or bounded-use state. Reusable approval, if policy expressly permits it, still requires current scope, lifecycle, and exact use binding.

## 11. Lifecycle/currentness analysis

Approval issuance, expiry, revocation, supersession, conflict, and authoritative order are not modeled. Candidate timestamps cannot establish freshness. A repair can compose existing lifecycle, ordering, freshness, source-authority, and durable anti-replay semantics. Current authoritative negative lifecycle must yield `DENIED`; inability to prove current approval yields `UNAVAILABLE`.

## 12. Successor/restart analysis

The shutdown/successor repair prevents predecessor execution grants from porting, but it does not consume an approval relation. A generic approval can therefore accompany a fresh successor authority chain even when it names the predecessor context. Approval must be successor-specific whenever the policy binds approval to the acting identity, executor, session, generation, or execution context.

## 13. Delegation interaction

The protected delegation chain correctly establishes execution delegation. It does not establish approval authority. Action authority and approval authority must be separate scoped roles. An operator may approve only under an exact protected approval-source admission or approval-specific delegation that is root-closed, current, non-widening, and distinct from ordinary action delegation. The current root-only principal-admission discipline is the smallest safe v1 choice.

## 14. Tool/backend interaction

`tool_connector_identity` is observed execution state, and terminal delegated use names a tool, but generic approval is not bound to either. Approval must name the exact admitted tool/backend identity and generation when that dimension affects the approved effect. Redirects, connector substitutions, default-filled parameters, and backend rotations require an admitted identity-preserving transformation or fresh approval.

## 15. Approval-as-override analysis

No override defect was reproduced. Existing evaluation failures occur before final authorization and are not repaired by the extra generic fact. Missing anchors and invalid delegation stay `UNAVAILABLE`; explicit delegation revocation stays `DENIED`. A repair must preserve this conjunction: approval is one required relation, never a bypass for another.

## 16. Representation-versus-effect analysis

Today no relationship joins displayed representation to canonical request and real effect. A repair should bind approval to a typed canonical request/effect digest and require exact display-to-canonical and canonical-to-execution transformation continuity where display is authority-relevant. The lab cannot decide arbitrary semantic equivalence; absent an admitted exact transformation relation, changed representation or effect fails closed.

## 17. Transformation analysis

Planner rewrites, formatting, wrappers, default insertion, summarization, retries, and successor reconstruction are safe only when an existing exact authority-preserving transformation proves that the canonical approved effect is unchanged. Scope expansion, dropped constraints, changed targets/nonces/times, changed tool/backend, or a new aggregate effect requires reapproval. General natural-language equivalence remains outside deterministic scope.

## 18. Multi-human approval analysis

No approval policy, required approver set, or approval independence relation exists. Count or signatures cannot establish independence. A repair can reuse protected control-plane membership/appraisal concepts: exact human identity and generation, effective control/authority domain, required role, required set, all-applicable selection, lifecycle, scope, and ordering. Several aliases, credentials, or approvals from one effective human/domain count once. Conflict fails closed absent authoritative resolution.

## 19. Positive controls

An exact unchanged approval/use and fresh reapproval after mutation, rotation, delegation change, or successor transition must remain reachable. A non-approval objective remains reachable without an approval relation. Approval policy selection must therefore be independently admitted and exact; it cannot be inferred from the candidate's presence or absence of an approval record.

## 20. Invariant mapping

- `INV-CONT`: approval identity, policy, context, lifecycle, ordering, freshness, successor, and transformation continuity.
- `INV-DISC`: human source authority, approval-specific delegation, role separation, quorum independence, revocation, and prohibition.
- `INV-BND`: boundary, epoch, tool/backend domain, destination, and cross-domain applicability.
- `INV-EVD`: canonical request/effect digest, display/canonical relationship, approval authenticity, and conflict.
- `INV-USE`: approval/use identity, execution binding, one-shot/bounded consumption, replay, queue/retry timing.
- `INV-CLO`: planner/wrapper/transformation closure and aggregate effect.

No case requires a seventh invariant or tuple coordinate. Approval is an authority-relevant relational fact, like objective binding, observation admission, anchoring, control-plane independence, and delegation continuity.

## 21. Contract sufficiency

The normative public language already requires exact current authority, exact identity/evidence binding, replay resistance, privilege separation, continuing authority, immutable evidence dependency, and fail-closed handling. The six invariants cover the defect. The gap is executable: generic required-fact equality is not a typed approval authority relation. The frozen 6/6/3 contract remains sufficient.

## 22. Possible repair direction

A bounded design is justified. It should add harness-owned protected approval policy/source context and strict candidate-visible typed approval envelope/use records inside existing relational structures. The policy selects whether approval is required, required roles/independence, scope, use policy, and canonicalization profile. The protected context admits exact human identities and approval authority. The envelope binds canonical effect and full context; lifecycle/order/freshness and durable consumption establish currentness and anti-replay. Exact negative lifecycle yields `DENIED`. Candidate-supplied protected state is rejected. Existing 287 fixtures require atomic policy migration, primarily explicit `approval_requirement=NONE`, while positive approval fixtures exercise the required path.

## 23. Residual external trust boundary

The deterministic oracle cannot prove that a real human intentionally acted, understood a display, controlled an independently admitted identity, or was free from coercion. UI integrity, device/key custody, biometric/account truth, accessibility, comprehension, canonical-effect rendering correctness, event delivery, and ultimate approval-root truth remain external trust preconditions. If every admitted source falsely presents an internally exact approval history and no contrary evidence survives, the oracle cannot infer the omitted world.

## 24. Exact hostile-research verdict

**FAIL — REPRODUCIBLE IN-SCOPE HUMAN-APPROVAL CONTINUITY OR REPLAY COUNTEREXAMPLE FOUND**

The executable counterexample is candidate-controlled generic required-fact equality: arbitrary, stale, transferred, revoked-looking, or replayed approval content is semantically invisible while an otherwise valid execution remains `AUTHORIZED`. Existing unrelated authority failures remain fail-closed. A design slice is justified inside the frozen `authority-lab-v1` architecture.
