# Ground Truth PHI Disclosure Authority Contract v1 — Candidate

## Status

Design candidate for integration into Authority Lab v1.

This artifact does not modify the frozen public contract. It preserves:

- tuple `(subject, artifact, control_state, identity_basis, boundary_epoch, decision)`
- invariants `INV-CONT`, `INV-DISC`, `INV-BND`, `INV-EVD`, `INV-USE`, `INV-CLO`
- outcomes `AUTHORIZED`, `DENIED`, `UNAVAILABLE`
- schema `authority-lab-v1`

Ground Truth public main is pinned for this design at:

`74cd883736c7acde1ff0d0d2ad765f6e8771def0`

At that exact public head, `tests/test_authority_lab.py` expects 466 maintained deterministic
fixtures. This candidate is additive research design; it does not claim those fixtures have
been migrated or that the repository test suite has been run with this integration.

## 1. Primary invariant

`NO CURRENT PHI DISCLOSURE AUTHORITY -> NO EXTERNAL INFERENCE EFFECT`

The term PHI is used for the health-data research domain. Applicable legal classifications
and lawful bases remain external policy inputs.

## 2. Authority object

PHI disclosure authority is represented as protected relational context, not as a new tuple
coordinate.

A current disclosure decision binds, directly or by exact protected reference:

- `subject_scope`
- `information_classes`
- `recipient_id`
- `effective_recipient_domain`
- `purpose_id`
- `authority_basis_id`
- `authority_basis_generation`
- `policy_id`
- `policy_generation`
- `disclosure_history_head`
- `memory_scope_id`
- `transformation_id`
- `tool_context_id`
- `execution_event_id`
- `effect_digest`
- `use_id`

No single field is independently sufficient.

## 3. Protected versus candidate-controlled state

Protected/harness-owned:
- applicable PHI disclosure policy;
- authority-basis lifecycle/currentness;
- recipient-domain membership;
- disclosure-history current head;
- subject/memory namespace admission;
- allowed transformation relations;
- current route/tool execution context;
- T3 execution event;
- durable use/effect state.

Candidate-visible:
- exact proposed disclosure effect;
- exact requested recipient/purpose;
- exact asserted source/derived artifact relation;
- exact terminal use request.

Candidate data cannot select the protected policy, current history head, recipient-domain
membership, authority lifecycle, or T3 event.

## 4. Three-way result discipline

Return `DENIED` only when an exact current authoritative negative applies to the exact T3
effect, including current revocation, rejection, explicit prohibited purpose/recipient,
cross-subject prohibition, or a proven cumulative disclosure limit violation.

Return `UNAVAILABLE` when a required positive relation cannot be established, including
missing/ambiguous history, recipient-domain membership, transformation authority, memory
scope, provider migration, effect outcome, authority currentness, or T3 convergence.

Return `AUTHORIZED` only when every mandatory current relation is established and no
applicable current negative exists.

Unknown never becomes permission.

## 5. Cumulative disclosure

Disclosure history is monotonic with respect to confirmed external effects.

`H_(n+1) = Commit(H_n, Effect_n)`

A restored local snapshot does not restore the external privacy state.

The current history head must be independently protected and current at T3.

## 6. Recipient-domain semantics

Disclosure history is evaluated over the effective correlation/control domain required by
policy, not merely the visible recipient label.

`recipient multiplicity != recipient independence`

If domain membership is required but unavailable, result is `UNAVAILABLE`.

## 7. Transformation closure

Authority over source artifact `A` does not imply authority over derivative `T(A)`.

Exact transformation authority must bind source digest, target digest, allowed semantic
classes, recipient, purpose and T3 effect.

This is an `INV-CLO` application, not a new invariant.

## 8. Memory/session continuity

Storage or retrieval does not preserve disclosure authority automatically.

A memory artifact requires exact current subject, namespace, purpose, recipient, source
provenance, lifecycle and use binding at retrieval T3.

`memory persistence != authority persistence`

## 9. Route/provider continuity

Stable model/API labels are selectors only.

The current PHI effect must bind the exact protected tool/connector/backend/target/operator
lineage already represented by Tool / Connector Authority Continuity.

A backend/provider/tenant/relay migration requires exact current transition/revalidation.

## 10. Authority-basis continuity

Consent, approval, policy grant, contract, or other authority basis is treated as a typed
current source relation.

Historical `AUTHORIZED` is not a current authority fact.

Current applicable revocation/rejection/prohibition -> `DENIED`.
Expiry/supersession/missing successor -> `UNAVAILABLE`.

## 11. Effect ambiguity

Timeout, cancellation, crash, or missing acknowledgement does not prove non-disclosure.

Ambiguous prior effect/use state -> `UNAVAILABLE`.
Confirmed effect advances history and consumes applicable one-shot use.
Exact non-effect proof can preserve retry eligibility.

## 12. Canonical T3 convergence

All mandatory PHI disclosure relations must name the protected canonical T3 event or prove
exact applicability through it.

The PHI layer must not maintain a parallel notion of terminal time.

## 13. Positive reachability

The candidate contract explicitly preserves `AUTHORIZED` when:

- current authority basis covers T3;
- exact effect is within policy;
- current history is complete;
- recipient/effective domain is exact;
- memory/transform relations are exact when applicable;
- current execution route is exact;
- prior effect/use state is resolved;
- terminal use is current;
- no applicable prohibition exists.

Fail-closed behavior is not a permanent denial model.

## 14. Residual trust boundary

The oracle cannot independently prove:
- truth of omitted real-world events;
- correctness of external legal/policy interpretation;
- source honesty when all admitted sources collude;
- actual data deletion at external recipients;
- real provider internal topology absent admitted evidence;
- complete instrumentation before evidence construction.

Those remain explicit external preconditions.

### Implementation note — exact T3 digest binding

At the reviewed Ground Truth baseline, the protected T3 record exposes `execution_event_digest`, not a separate `effect_digest`. The PHI contract's `effect_digest` member is therefore populated from and compared to the protected `t3_execution_event.execution_event_digest`. This reuses the existing canonical T3 commitment and does not create an independent effect-digest authority path.
