# Authority Lab v1 Human Approval Continuity Design

## 1. Baseline and defect

This design follows `FRONTIER_DELTA_HUMAN_APPROVAL_CONTINUITY.md` at `498cce8`. Authority Lab v1 currently has no typed approval relation. A schema-valid arbitrary T3 fact can be added to `required_facts`, mirrored in candidate-controlled `required_values`, and treated as satisfied without consuming its meaning. `human_approval="yes"`, a model-attributed record, the wrong human, a stale context, and repeated one-shot use all permit an otherwise valid case to remain `AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED`.

The defect is not that every execution lacks approval. It is that an admitted policy which requires human approval cannot currently establish that requirement relationally. Human approval must remain optional when the independently selected policy says `NONE`.

## 2. Normative rule

> Human approval is evidence of authority only for the exact approved canonical effect, acting identity, execution path, and current authority context. It is neither transferable authority nor an override.

For an approval-required decision, `AUTHORIZED` requires all of:

1. an independently current root-issued approval policy;
2. independently admitted exact human/operator approval sources;
3. a strict approval envelope bound to an authority-established canonical effect;
4. exact source verification and authoritative ordering;
5. current lifecycle and freshness at use;
6. exact binding to subject, executor, delegation chain, tool/backend, boundary, objective, grant and execution context;
7. durable use/anti-replay state when policy limits use;
8. every unrelated Authority Lab requirement.

No approval value can establish any item above merely by containing a matching string, identity, signature, timestamp, count, or digest.

## 3. Frozen architecture

The repair is a composition of `INV-CONT`, `INV-DISC`, `INV-BND`, `INV-EVD`, `INV-USE`, and `INV-CLO`. It uses internal typed relational facts and harness-owned protected context. It does not change schema `authority-lab-v1`, the six tuple coordinates, the six invariant identifiers, or the three authority outcomes.

`human_approval` and `user_said_yes` become reserved approval-like names and cannot pass through generic required-fact equality. They are not new tuple coordinates. The only admitted candidate approval surface is the typed `human_approval_binding` relation.

## 4. Policy selection

Each harness-owned anchor context gains one immutable `human_approval_authority_context`. It contains exactly one current root-issued policy selected under the same boundary, epoch, objective, authority generation, ordering source, freshness challenge, and lineage as the decision.

Policy modes are closed:

- `NONE`: approval is not required. Existing authorization remains possible without approval evidence.
- `REQUIRED`: the exact policy requirements below must be established.

The candidate cannot select `NONE`, change required roles/count, or supply protected policy state. Missing, conflicting, stale, or non-applicable protected policy is `UNAVAILABLE / HUMAN_APPROVAL_POLICY_UNAVAILABLE`. Current root-issued policy revocation/prohibition is `DENIED / HUMAN_APPROVAL_POLICY_PROHIBITED`.

## 5. Protected approval policy

The immutable policy record binds:

- `policy_id`, `policy_generation`, `relationship=HUMAN_APPROVAL_POLICY`;
- `requirement` (`NONE` or `REQUIRED`);
- exact applicable objective and decision-contract identity/generation;
- canonical-effect profile and required semantic fields;
- required approval roles and exact required count;
- independence rule and required effective domains;
- permitted human/source identity classes;
- allowed action/effect and artifact/resource scope;
- permitted subject/executor classes;
- permitted tool/backend identities;
- boundary, epoch, execution-context and delegation requirements;
- use policy (`ONE_SHOT`, `BOUNDED`, or `CONTINUING`) and maximum uses;
- maximum issue-to-use interval and expiry requirements;
- transformation/reapproval rule;
- root/source authority, lineage, ordering, lifecycle and freshness.

`ALL_APPLICABLE` selection is mandatory. The oracle never shops among policies or approval subsets.

## 6. Protected human/operator admission

Every approver is joined to one exact harness-owned admission containing:

- human/operator principal ID and generation;
- identity basis and identity-basis generation;
- approval-source/key/device ID and generation;
- approval role(s), scoped approval authority and effective authority domain;
- controller/upstream source lineage;
- allowed objectives, effects, artifacts/resources, subjects/executors, tools and boundaries;
- start/end order, lifecycle, source authority and freshness;
- explicit replacement/handoff relation where applicable.

The evaluated subject, model, agent, executor, observer, approval producer, or approver cannot admit itself. Stable display names, accounts, service roles, credentials, devices, signatures, and repeated assertions do not prove human identity continuity.

V1 uses root-issued approver admission. Ordinary action delegation and objective-binding delegation do not widen into approval authority. Any later approval-specific delegation would need a separately reviewed root-closed chain and is outside this repair.

## 7. Typed candidate approval relation

When policy mode is `REQUIRED`, T3 must contain one strict known `human_approval_binding` object. It has exact fields only and contains:

- one canonical request/effect record;
- one or more approval envelopes;
- exact approval verification receipts;
- one authoritative approval ordering head;
- one exact execution/use request;
- any exact correction/supersession links;
- any authority-preserving display/canonical transformation admission.

Unknown fields, duplicate identities, malformed arrays, booleans in integer fields, and omitted required members remain harness/schema failures. A structurally valid but semantically unmatched relation yields `UNAVAILABLE`.

Candidate injection of `_trusted_human_approval_context` is rejected by the loader, matching existing protected-context rules.

## 8. Canonical request/effect identity

The oracle computes a domain-separated SHA-256 digest over a strict canonical body containing at minimum:

- schema/domain separator and canonicalization profile;
- request/effect ID and generation;
- exact artifact/resource identity;
- semantic action/effect class;
- canonical parameter/target/destination/amount digest where applicable;
- tuple subject and identity basis;
- exact executor/delegate identity and generation;
- current execution context and control state;
- exact tool/connector/backend identity and generation;
- applicable boundary and epoch;
- objective binding and decision contract identity/generation/version;
- current grant/use identity;
- current protected delegation chain/head, or exact `DIRECT` marker;
- session/generation, queue/schedule/retry phase where applicable;
- transformation lineage and aggregate-effect identity where applicable.

The canonical action/effect is not accepted merely from the approval producer. It must join either existing exact execution semantics (artifact, tuple, objective, grant/use, tool, delegation and boundary) or an exact root/objective-authorized effect relationship. If the actual semantic effect or aggregate effect is not represented, approval-required authority is `UNAVAILABLE / HUMAN_APPROVAL_EFFECT_UNAVAILABLE`.

This is not natural-language semantic equivalence. A deployment must make the artifact/effect identity commit to every authority-relevant parameter. Unrepresented recipient, amount, destination, default, or downstream effect cannot be guessed by the oracle.

## 9. Approval envelope

Each strict envelope binds:

- approval ID/generation and policy ID/generation;
- independently admitted approver identity/basis/source generation;
- required approver role and effective authority domain;
- canonical request/effect digest and all exact context identities;
- approval disposition (`APPROVED`, `REJECTED`, or `PROHIBITED`);
- issuance order, expiry order and freshness challenge;
- session/generation and nonce;
- use policy/max uses;
- predecessor approval, correction or supersession identity;
- canonical payload digest and signature-evidence identity.

An opaque signature or digest is not authority. One exact verification receipt must bind the envelope digest, admitted approver source/key generation, current challenge, disposition and authoritative order.

## 10. Exact approval/use binding

The use request binds the selected current approval set to the exact current canonical effect, subject, executor/delegate, delegation head, execution grant, tool/backend, boundary/epoch, execution context, objective/contract, session/generation and use-event order. It also binds queue/schedule/retry/phase identity where policy declares those authority-relevant.

Approval at T1 is not sufficient. The join is reevaluated at T3 immediately before the authority-consuming transition. Any mismatch is `UNAVAILABLE / HUMAN_APPROVAL_USE_UNAVAILABLE`.

## 11. Lifecycle, ordering and currentness

Harness-owned lifecycle and ordering records select the complete current approval set. For each required approval:

- issuance precedes use;
- use does not exceed expiry or policy maximum interval;
- approval policy, human admission and source generation are current;
- no newer applicable supersession, correction, rejection or revocation is omitted;
- freshness is verifier/root-bound, not approver-declared;
- all required approvers and effective domains are covered;
- unresolved same-position or overlapping conflict fails closed.

Stale, expired, superseded, unordered, ambiguous, or incompletely observed state is `UNAVAILABLE`. Exact current authoritative rejection, revocation or prohibition is `DENIED`.

## 12. Replay and durable use state

A harness-owned approval-use manifest records the current use position/count for `(policy, approval, request/effect, session/generation)`. Candidate fixtures cannot supply or reconstruct it.

- `ONE_SHOT`: only the exact next unused use position can authorize; any accepted prior use makes replay unavailable.
- `BOUNDED`: the protected count must be below the exact maximum and advance atomically with use.
- `CONTINUING`: reuse is permitted only while the exact policy, effect, context, lifecycle, freshness and authority relationships remain current.

Rollback, snapshot restore, restart, recovery, cross-session copy, successor transfer and candidate-only reconstruction do not reset consumption. Missing protected use state is `UNAVAILABLE / HUMAN_APPROVAL_USE_STATE_UNAVAILABLE`.

The lab models the pre-transition authority decision and an exact protected current-use position; production atomic consumption remains an external implementation obligation.

## 13. Identity and successor rules

Approval is non-portable across a human/operator identity transition, evaluated-subject transition, executor/delegate transition, successor/restart, changed execution context, or changed session generation unless the current policy explicitly defines a continuing scope and every identity relationship remains exact. V1 positive successor cases use fresh approval.

Same label, account, credential, device, code, checkpoint, or restored state does not prove the same approval identity. Human/operator replacement requires root-issued admission continuity; execution successor authority still requires its independent existing successor chain.

## 14. Delegation interaction

Protected delegation authority establishes who may execute; protected human approval establishes who may approve. Neither implies the other. The approval binds the exact selected delegation chain/head and terminal executor. Regrant, delegate replacement, planner/executor split, service-account change, chain splice, or scope change requires fresh approval unless an exact policy-authorized transformation says the approved canonical effect and executor relationship are unchanged.

An operator with action authority but no approval role is unavailable. A human with approval authority cannot execute unless ordinary execution authority independently permits it.

## 15. Tool/backend and boundary interaction

Approval binds exact tool/connector/backend identity and generation whenever the policy's canonical-effect profile requires it. Tool substitution, backend redirect, credential/source replacement, cross-domain reconciliation, adapter rotation and boundary-epoch change require fresh approval or one exact root-authorized identity-preserving transition admitted by policy.

An observer/verifier/anchor/witness handoff establishes only its own continuity. It never transfers approval or execution authority.

## 16. Transformation and representation

A human may view representation `R`, while the executor consumes canonical effect `E`. Authorization requires an exact admitted `R -> E` relationship binding display digest, canonical effect digest, renderer/canonicalizer identity and generation, transformation profile, preserved constraints, lifecycle, source authority and ordering.

Planner rewrite, wrapper reformat, default insertion, summarization, retry reconstruction and payload transformation are accepted only if this relation proves exact authority-preserving continuity. Scope expansion, dropped constraints, changed recipient/amount/destination/time/tool/backend, or changed aggregate effect requires reapproval. Unknown semantic equivalence yields `UNAVAILABLE`, never guessed authorization.

## 17. Multi-human policy and independence

The protected policy selects exact required roles, count and effective authority domains. The oracle evaluates all applicable approvals and uses protected human admissions to derive effective domains. Approval count, signatures, aliases, credentials, devices or processes do not establish independence.

Several approvals from one effective human/control domain count once. A missing, stale, revoked or conflicting required approver fails closed. Majority vote does not resolve conflict. Exact current root-authorized resolution/supersession may select a corrected set.

## 18. Approval cannot override authority

Approval evaluation is conjunctive and occurs only after earlier schema/observation/anchor/control-plane checks have established their own requirements. Approval cannot repair `UNAVAILABLE`, override `DENIED`, create an objective binding, select an authority root, establish execution delegation, cure tool identity, or manufacture observation/anchor state.

An explicit separate root-authorized supersession relation would be evaluated under its own semantics; a human approval alone is never that relation.

## 19. Outcome discipline

`UNAVAILABLE` includes missing required approval, generic yes, arbitrary or self-attributed approver, missing source admission, stale identity, effect/context mismatch, replay, expiry, supersession ambiguity, conflict, missing required approver/domain, unresolved transformation, unrepresented aggregate effect, and unavailable durable use state.

`DENIED` is reserved for exact current authoritative policy/approval rejection, revocation or prohibition that applies to the exact request/effect.

`AUTHORIZED` remains possible for policy `NONE`, or for an exact current complete approval set and use relation after every existing authority requirement succeeds.

## 20. Hostile matrix disposition

The research matrix A–CO is closed by five non-overlapping checks:

| Cases | Required design check |
|---|---|
| A, CH, CI–CL, CO | Explicit positive paths for unchanged use, fresh reapproval, and policy `NONE`. |
| B–Z, BT–CG | Canonical effect/context digest plus exact approval/use and transformation binding. |
| AA–AG, AS–AU, BF–BP, BZ–CB | Lifecycle, authoritative ordering, freshness, successor non-portability and durable anti-replay. |
| AH–AR, BA–BE | Protected root-issued policy, exact human/source admission, approval roles and effective-domain independence. |
| AV–AZ, CM | Current authoritative negative lifecycle; `DENIED` or unresolved conflict as specified. |
| BQ–BS | Conjunctive evaluation preserves unrelated `UNAVAILABLE` and `DENIED`. |
| CN | Required policy with missing relation is `UNAVAILABLE`. |

The full implementation fixture plan must retain a named case for every research class even where cases share an evaluator branch.

## 21. Positive paths

1. `NONE`: an otherwise valid action remains `AUTHORIZED` without approval evidence.
2. Exact one-shot approval: root-issued policy, independently admitted human, exact canonical effect, current envelope/verification/head, unused protected position and exact use reach `AUTHORIZED`.
3. Fresh reapproval: material mutation creates a new canonical effect and approval generation; exact fresh use reaches `AUTHORIZED`.
4. Successor: fresh successor authority plus successor-specific approval reaches `AUTHORIZED`.
5. Tool/backend rotation: current admitted rotation plus fresh approval of the new exact tool/backend reaches `AUTHORIZED`.
6. Multi-human: all required independently admitted effective domains approve the same canonical effect and exact use reaches `AUTHORIZED`.

## 22. Compatibility and migration

Implementation must atomically add protected approval policy/context to every one of the 287 maintained fixture entries. Existing fixtures receive exact current `NONE` policies and preserve every reviewed outcome. Their fixture payloads need not gain approval envelopes if the parser permits absence only under protected `NONE` policy.

Approval-required hostile fixtures begin at `LAB-V1-288`. A bounded first implementation should cover at least generic yes, arbitrary/model approver, wrong/stale identity, artifact/effect/context mismatch, agent/executor/delegate substitution, boundary/tool/delegation/successor change, replay/session/restart/recovery, expiry/supersession/revocation/conflict, override attempts, representation mismatch, queued/retry use, multi-human false independence, exact positive use, fresh reapproval and policy `NONE`.

No prior expected outcome changes. Any fixture with unavailable earlier anchor context remains unavailable for that earlier reason; approval policy is not allowed to mask established upstream diagnostics.

## 23. Expected implementation surface

- `authority_lab/model.py`: strict typed approval records, reserved names, immutable protected context parser.
- `authority_lab/oracle.py`: canonical effect digest, protected policy/source join, lifecycle/order/freshness, independence, exact use and anti-replay evaluation.
- `authority_lab/runner.py`: reject candidate protected-context injection and expose bounded trace metadata.
- `authority_lab/README.md`: approval authority and residual trust boundary.
- `cases/authority_lab/trusted_anchor_state.json`: atomic 287-case policy/context migration.
- A separate harness-owned approval-use manifest if durable state cannot safely share the anchor manifest.
- `tests/test_authority_lab.py`: expectation-independent focused tests.
- New fixtures beginning `LAB-V1-288`.

No contract, architecture, invariant, outcome or schema-version file changes are required.

## 24. Independent test obligations

Tests must prove independently of fixture expectations:

- generic and model-generated yes cannot authorize an approval-required policy;
- candidate cannot supply protected policy/source/use state;
- approval records are strict and immutable;
- canonical digest changes for every material bound dimension;
- approval source and execution subject are distinct roles;
- arbitrary/wrong/stale approver fails closed;
- replay does not reset across session, restart, snapshot, recovery or successor;
- artifact/effect/parameter/recipient/tool/backend/boundary/delegation changes require reapproval;
- one-shot use is consumed and continuing use remains policy-bounded;
- expiry/supersession/conflict are unavailable and current revocation/prohibition is denied;
- approval cannot override anchor/delegation unavailable or current denial;
- multi-signature aliases from one domain do not satisfy independent approvers;
- exact unchanged approval, fresh reapproval, fresh successor, valid rotation, independent quorum and `NONE` policy positives remain reachable.

## 25. Hostile design review

| Attack | Why it does not survive |
|---|---|
| Candidate chooses approval requirement | Requirement comes only from protected all-applicable policy. |
| Candidate repeats policy values | Protected context and exact root/currentness join remain unavailable. |
| Generic `yes` or unknown approval fact | Reserved names cannot use generic equality; required typed relation is absent. |
| Approver self-identification | Exact protected human/source admission is independently required. |
| Model/agent/proxy attribution | Producer identity does not equal admitted approval authority. |
| Same label after identity rotation | Principal, basis, source and generation must all match current admission. |
| Stale approval with fresh self-timestamp | Root/verifier-bound freshness and authoritative order ignore self-time. |
| Artifact/effect substitution | Recomputed canonical digest and exact use no longer match. |
| Stable display, changed payload | Display-to-canonical relation and canonical digest fail. |
| Wrapper/default/summarizer widening | No exact authority-preserving transformation; reapproval required. |
| One-shot replay | Protected durable use position/count rejects reuse. |
| Durable-state rollback | Approval use joins existing independently anchored currentness; candidate reconstruction cannot close the loop. |
| Successor/restart reuse | Subject/executor/session generations and successor-specific approval mismatch. |
| Delegation regrant | Bound protected chain/head changes; fresh approval required. |
| Tool/backend redirect | Bound tool/backend identity/generation changes. |
| Approval shopping | All-applicable head/policy selects the complete current set. |
| Same person signs twice | Effective human/control domain counts once. |
| Approval conflict | Conflict is unavailable absent authoritative resolution; no voting. |
| Approval revocation hidden by older positive | Current protected lifecycle/order selects revocation and returns denied. |
| Approval overrides missing anchor | Anchor evaluation remains an independent prerequisite. |
| Approval overrides prohibition | Current authoritative denial remains denial. |
| Positive action becomes impossible | `NONE`, unchanged exact use, fresh reapproval, successor and quorum positive paths are explicit. |

No in-scope bypass survives the proposed relational composition. The design does not claim to prove human intent or arbitrary semantic equivalence.

## 26. Residual trust boundary

The oracle still trusts admitted external facts about real human identity, intentional interaction, comprehension, freedom from coercion, device/key custody, UI rendering, signature appraisal, canonicalization correctness, protected use-state durability, event delivery and ultimate root truth. If every admitted source colludes to fabricate one exact history and no independent contrary state survives, the deterministic oracle cannot recover the real world.

General semantic task decomposition is enforceable only when the aggregate effect is explicitly represented by the admitted canonical-effect profile. Unknown equivalence fails closed.

## 27. Determination and exact hostile-design verdict

The repair is representable through internal typed relational facts plus existing source-authority, identity, lifecycle, ordering, freshness, boundary, objective, delegation, control-plane, anchoring, consumption and closure semantics. It requires no seventh coordinate, seventh invariant, fourth outcome or new schema version.

Implementation is justified, but it entails an atomic protected-state migration of all 287 fixtures and a substantial hostile fixture set. It should proceed only as one complete implementation slice; partial policy migration is unauthorized.

**PASS — NO REPRODUCIBLE IN-SCOPE HUMAN-APPROVAL CONTINUITY, REPLAY, TRANSFER, OR EFFECT-BINDING BYPASS SURVIVES THE PROPOSED DESIGN**
