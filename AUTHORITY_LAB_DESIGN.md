# Ground Truth Authority Lab Design

## Status and Scope

This document designs a minimal public, deterministic, non-production Ground Truth Authority Lab. The lab is a falsification harness: it allows engineers to replay explicit adversarial authority-boundary scenarios and attempt to falsify the current public authority model.

The lab is not a product, policy engine, production authorization service, AI safety certification system, or copy of the private Ground Truth core. This document does not implement the lab, create executable code, or claim that any implementation passes the cases. It creates no implementation, deployment, roadmap, later-phase, certification, merge, or authority-bearing authorization. Human adoption and merge authority remain separate.

The core public question is:

> Given exact authority-relevant state at T1, changes during T2, and exact observable state at T3, what authority outcome follows under the current public contract?

The authority outcomes remain exactly:

- `AUTHORIZED`
- `DENIED`
- `UNAVAILABLE`

The exact authority tuple remains:

`(subject, artifact, control_state, identity_basis, boundary_epoch, decision)`

It has exactly six coordinates.

The invariant identifiers remain exactly:

- `INV-CONT`
- `INV-DISC`
- `INV-BND`
- `INV-EVD`
- `INV-USE`
- `INV-CLO`

The lab introduces no new authority outcome, tuple coordinate, invariant, or semantic stage.

## 1. Lab Thesis

The Authority Lab is a deterministic public falsification harness.

It does not prove the Ground Truth model correct. Its purpose is to make counterexamples reproducible.

A successful falsification is a case where:

1. all applicable public contract requirements are represented faithfully;
2. the lab establishes the exact relevant facts required by the case;
3. the six-invariant public model returns or permits `AUTHORIZED` at T3; and
4. the authority-consuming transition should nevertheless be impermissible under the stated contract objective.

That result is a candidate contract-level counterexample requiring separate human hostile review. A lab bug, incomplete fixture, missing state representation, implementation error, or incorrect oracle does not automatically constitute a contract counterexample.

The lab must be capable of disagreeing with the expectation written into a fixture. A harness that simply returns the fixture's expected result is not falsifiable and fails this design.

## 2. Execution Model

The lab models three observable phases only:

| Phase | Meaning | Authority consequence |
| --- | --- | --- |
| T1 | Evaluation of the exact applicable tuple and evidence | Produces an evaluation result; it does not execute the effect. |
| T2 | Non-authoritative preparation and adversarial mutation | May change authority-relevant facts; it never creates authority. |
| T3 | Authority check at the modeled irreversible boundary | Permits the exact modeled transition only when current `AUTHORIZED` is established. |

A T1 `AUTHORIZED` result is necessary but insufficient for T3. T2 never creates authority.

Immediately before and at T3, all facts required by the applicable contract must be established. If required facts cannot be established, the outcome is `UNAVAILABLE`. If the applicable boundary and exact tuple are established and an established applicable condition prohibits the transition, the outcome is `DENIED`. Only current `AUTHORIZED` at T3 permits the modeled transition.

Capability ≠ Evidence ≠ Authority ≠ Execution

No fixture step, explanation, expected result, model output, or harness status may itself execute or authorize an effect.

## 3. State Model

The future lab fixture needs an explicit state envelope. Its fields are observations and contract inputs, not additions to the authority tuple.

| State field | Minimum representation | Contract role |
| --- | --- | --- |
| Subject identity | Identity-bearing value plus fact state and provenance | Establishes `subject` and supports `INV-DISC`. |
| Artifact identity | Exact artifact/effect identity plus fact state | Establishes `artifact` and supports `INV-EVD` and `INV-CLO`. |
| Control state | Authority-relevant environment, privilege, ordering, policy, and lifecycle facts | Supplies the existing `control_state`. |
| Identity basis | Discriminator, binding method, scope, and fact state | Supplies the existing `identity_basis`. |
| Boundary epoch | Exact lineage-bearing epoch and observation source | Supplies the existing `boundary_epoch`. |
| Decision | Exact decision value and binding | Supplies the existing `decision`. |
| Evidence objects | Stable identifiers, content commitments, and admission facts | Evaluated under `INV-EVD`; evidence does not issue authority. |
| Evidence provenance | Produced-by, transformed-from, subject-influenced, and shared-origin relations | Establishes causal relationships required by the case. |
| Authority-boundary identity | Applicable boundary, trust root, selector, and epoch binding | Evaluated under `INV-BND` and `INV-DISC`. |
| Execution-context identity | Environment, process, session, host, sandbox, or runtime identity | Evaluated as authority-relevant state under existing semantics. |
| Principal or credential identity | Acting principal, credential, scope, and custody facts where relevant | Supports subject, identity, boundary, and control-state establishment. |
| Tool or connector identity | Name, implementation, endpoint, operator, version, and trust lineage where relevant | Prevents interface or name equality from substituting for identity. |
| Consumption state | Unused, consumed, or unresolved, with authoritative ordering | Evaluated under `INV-USE`. |
| Commit state | Not attempted, committed, not committed, partial, or unresolved, with provenance | Supports T3 and retry reasoning. |
| Freshness or supersession state | Relevant version, revocation, replacement, and ordering facts | Evaluated under `INV-CONT`, `INV-EVD`, and `INV-USE`. |
| Delegation relationship | Delegator, delegate, scope, effect, boundary, and current binding | Evaluated under `INV-DISC`, `INV-BND`, and `INV-CLO`. |
| Derived or aggregate relationship | Constituents, transformation, aggregation rule, scope, and output identity | Treats authority-relevant derived output as a distinct artifact under `INV-CLO`. |
| Fact-state marker | `KNOWN(value)`, `UNKNOWN`, or `CONFLICTING(values)` | Prevents missing or contradictory facts from defaulting safe. |

Fixture state is not the authority tuple. Additional fixture fields represent facts used to evaluate existing tuple coordinates, `control_state`, evidence relationships, continuity, and invariant obligations. They do not create a seventh coordinate.

The fixture must distinguish an absent inapplicable field from a required field whose value is unknown. Applicability is determined by the stated public contract for the case, not by whether a fixture author supplied a convenient value.

## 4. Unknown and Unavailable Model

Every authority-relevant fact is represented in one of three bounded fact states:

- `KNOWN(value)`: the value and its required binding or provenance are established;
- `UNKNOWN`: the required value or relationship cannot be established; or
- `CONFLICTING(values)`: multiple relevant claims exist and the applicable contract cannot establish which controls.

Unknown is never encoded as false, denied, zero, a safe default, an optional omission, a stale prior value, or a previous `AUTHORIZED` result. Conflicting facts are not resolved by majority vote, source count, model output, or fixture expectation.

For each case, the oracle first determines which facts the applicable contract requires. If any required fact is `UNKNOWN`, or is `CONFLICTING` without an authoritative resolution established by that contract, uncertainty propagates to `UNAVAILABLE`.

`DENIED` is appropriate only when the applicable boundary and exact tuple are established and an established applicable condition decisively prohibits the requested transition. It must not be used to hide missing establishment needed to identify the tuple, boundary, prohibition, or its applicability.

## 5. Case Format

Each future machine-readable case derives from a case in `ADVERSARIAL_AUTHORITY_BOUNDARY_CASEBOOK.md` and contains at least:

| Case field | Required content |
| --- | --- |
| Case ID | Stable lab ID and public casebook source ID. |
| Title | Concise attack or control name. |
| Objective | Exact contract proposition being tested. |
| Initial T1 state | Explicit tuple, boundary, context, freshness, and consumption facts before evaluation. |
| T1 evidence | Exact evidence objects, provenance, and admission relationships. |
| Expected T1 result | One of the three authority outcomes, used for comparison only. |
| T2 mutations | Ordered, explicit state changes between evaluation and commit. |
| T2 non-authority assertion | Assertion that preparation and mutation produce no authority. |
| T3 observed state | Exact observations presented independently to the oracle. |
| T3 missing, unknown, or conflicting facts | Required facts marked with the explicit fact-state mechanism. |
| Applicable invariants | Subset of the frozen six identifiers engaged by the case. |
| Precise authority question | Exact authority-consuming transition the oracle must decide. |
| Expected final outcome | Comparison value only; it cannot control evaluation. |
| Expected reason | Public contract interpretation supporting the expected value. |
| Counterexample condition | Exact mismatch that would pressure or falsify contract semantics. |
| Notes and provenance | Public casebook source, schema version, authorship, and bounded explanatory context. |

The case format must preserve the casebook's distinctions. It may normalize syntax, but it must not silently discard identity, evidence-lineage, boundary, freshness, consumption, delegation, closure, or uncertainty semantics.

## 6. First Runnable Case Set

The proposed v0 set contains twelve deterministic fixtures. It includes positive and negative controls and covers the highest-value boundary transitions without attempting the full 30-case catalog.

| Lab ID | Casebook source | Expected category | Why it belongs in v0 |
| --- | --- | --- | --- |
| LAB-V0-001 | Control projection of GT-CASE-009 | Fresh unchanged positive authorization | Establishes a baseline where the exact tuple, execution context, evidence, boundary, freshness, and unused state remain `KNOWN` and unchanged through T3. It detects an oracle that always fails closed. |
| LAB-V0-002 | GT-CASE-002 | Established explicit prohibition | Separates a known, prohibited privilege escalation (`DENIED`) from missing state (`UNAVAILABLE`). |
| LAB-V0-003 | GT-CASE-001 | Sandbox escape after T1 | Tests whether an S1-bound result is replayed after unestablished host execution. |
| LAB-V0-004 | GT-CASE-004 | Connector or tool substitution | Tests stable interface/name with a different endpoint, operator, credential, or trust lineage. |
| LAB-V0-005 | GT-CASE-006 | Principal or credential substitution | Tests an exact, established substitution that the applicable contract prohibits. |
| LAB-V0-006 | GT-CASE-012 | Monitor remains in old context | Tests a locally valid monitor report after the acting lineage leaves its observation boundary. |
| LAB-V0-007 | GT-CASE-011 | Cached historical `AUTHORIZED` | Tests replay after an authority-relevant environment or epoch change. |
| LAB-V0-008 | GT-CASE-020 | Lost acknowledgment with known consumption | Negative control: authoritative consumption is `KNOWN`, so one-shot replay is prohibited rather than uncertain. |
| LAB-V0-009 | GT-CASE-021 | Ambiguous T3 and one-shot uncertainty | Paired with LAB-V0-008 to require `UNAVAILABLE` when commitment and consumption cannot be established. |
| LAB-V0-010 | GT-CASE-014 | Explicitly bound delegated actor | Positive control: permits `AUTHORIZED` only after the delegate, effect, boundary, evidence, epoch, and unused state are freshly established. |
| LAB-V0-011 | GT-CASE-016 | Aggregate artifact authority | Tests whether constituent judgments improperly authorize a distinct aggregate result. |
| LAB-V0-012 | GT-CASE-029 | Derived artifact authority | Tests whether a transformed, summarized, scored, or signed report inherits authority from its source. |

The control projection in LAB-V0-001 changes no casebook semantics: it is the no-transition baseline paired with GT-CASE-009's identity/context pressure. GT-CASE-009 and GT-CASE-014 establish that v0 must not preserve a preferred failure result; fresh exact establishment can produce `AUTHORIZED` when the applicable contract genuinely permits the transition.

## 7. Flagship Escape Case

### Scenario

At T1, subject S is evaluated inside environment E1 and receives `AUTHORIZED` for exact artifact A under boundary epoch B1. The decision is bound to the stated `control_state`, `identity_basis`, evidence, applicable boundary, and unused consumption state.

During T2, non-authoritative preparation begins. Before T3, the acting process crosses into environment E2 or acquires a different privilege, principal, credential, connector, or tool path. The model bytes and task text may remain identical. The cached T1 decision remains present. The original monitor may still observe E1 while the acting process approaches commit from E2.

At T3 the precise question is:

> Does the original authority still bind the exact acting subject, artifact, control state, identity basis, boundary epoch, and decision at the applicable irreversible boundary?

### Required Inputs

The fixture must state, independently of its expected result:

- whether E1-to-E2 execution continuity is `KNOWN`, `UNKNOWN`, or `CONFLICTING`;
- whether the current acting subject and principal are exactly established;
- whether privilege, credential, tool, connector, and endpoint changes are authority-relevant under the applicable contract;
- whether artifact A and its exact effect remain unchanged;
- whether monitor and evidence coverage still bind the actual T3 path;
- whether the applicable boundary and B1 continuity remain established; and
- whether the decision remains fresh, unrevoked, unsuperseded, and unused.

### Derived Outcomes

| Established T3 facts | Derived authority outcome |
| --- | --- |
| A required continuity, identity, boundary, evidence, freshness, or consumption fact is `UNKNOWN` or unresolved `CONFLICTING` | `UNAVAILABLE` |
| The applicable boundary and exact tuple are established, and an established applicable condition prohibits the E2 transition | `DENIED` |
| Every required current fact is `KNOWN`, the exact tuple and applicable boundary remain established, authority is unused, and the applicable contract permits the exact E2 transition | `AUTHORIZED` |

The design does not hard-code “sandbox escape equals `UNAVAILABLE`.” It derives the outcome from current facts and the applicable public contract. Stable model bytes, task text, cached decisions, or monitor output do not establish continuity by themselves. Conversely, a context change does not force `UNAVAILABLE` when every required current relationship is genuinely established and the applicable contract permits the exact transition.

## 8. Oracle Design

The future oracle is a deterministic boundary over explicit fixture state. It evaluates only public contract semantics and has no access to the fixture's expected outcome while computing its actual outcome.

The oracle design follows this order:

1. Validate that the fixture can identify its applicable public contract, requested transition, and required fact set. Schema validity is not authority.
2. Resolve the applicable authority boundary without accepting requester-selected substitution.
3. Establish the exact six-coordinate tuple from explicit current facts.
4. Evaluate evidence identity, provenance, freshness, continuity, consumption, delegation, and derived-artifact relationships required by the case.
5. If a required establishment is `UNKNOWN` or unresolved `CONFLICTING`, return `UNAVAILABLE` with structured reasons.
6. If the applicable boundary and exact tuple are established and a decisive established applicable condition prohibits the transition, return `DENIED` with that condition.
7. Return `AUTHORIZED` only when every required current condition is established, authority is eligible for consumption, and the applicable contract permits the exact transition.

The result record contains exactly one authority outcome, structured reason codes, the engaged invariant identifiers, and the exact authority question. Explanatory text describes the decision but is not authority evidence.

The expected result stored in the fixture is read only after the actual result is fixed. If actual and expected differ, the harness emits `CASE_MISMATCH`. `CASE_MISMATCH` is a test-harness comparison status, not a fourth authority outcome. The mismatch must remain visible and must not be rewritten into agreement.

The oracle never infers authority from consensus, model output, previous success, case title, expected result, source reputation, signature count, process count, or vendor multiplicity.

## 9. Counterexample Handling

When actual authority outcome differs from expected authority outcome, the lab preserves the fixture, inputs, actual result, expected result, structured reasons, and deterministic trace. It assigns no automatic semantic conclusion.

Separate review classifies the mismatch as one of:

- **Fixture defect:** the fixture is incomplete, internally inconsistent, or does not represent the stated case faithfully.
- **Oracle implementation defect:** the implementation does not follow the published deterministic oracle design.
- **Ambiguous specification:** two defensible public-contract interpretations produce different results from the same established facts.
- **Candidate contract counterexample:** faithful representation and a conforming oracle permit `AUTHORIZED` at T3 even though the stated contract objective makes the exact transition impermissible.

There is no automatic contract modification, invariant creation, roadmap advancement, or authority transition. Candidate counterexamples require separate human hostile review before any contract response is considered.

## 10. Trace and Explanation

A future human-readable flagship trace should have this form:

```text
T1:
AUTHORIZATION EVALUATED
result = AUTHORIZED

T2:
execution_context changed E1 -> E2
connector changed C1 -> C2
cached T1 evidence retained
no authority consumed

T3:
execution_context identity = UNKNOWN
connector binding = CHANGED
boundary continuity = NOT ESTABLISHED

FINAL:
UNAVAILABLE

ENGAGED:
INV-CONT
INV-DISC
INV-BND
INV-EVD
```

The structured fixture and deterministic oracle result control the trace. The prose explanation is a derived diagnostic artifact under `INV-CLO`; it cannot supply missing evidence, cure unknown state, or issue authority.

## 11. Public CLI and Interface Concept

A possible future non-production interface is:

```text
authority-lab run cases/escape-after-t1.json
```

A possible comparison display is:

```text
CASE: LAB-V0-003
EXPECTED: UNAVAILABLE
ACTUAL: UNAVAILABLE
STATUS: PASS
```

In that display, PASS means only that the independently computed oracle outcome equals the fixture expectation. PASS never means secure, safe, formally verified, production ready, certified, complete, or universally correct. A mismatch is displayed as `CASE_MISMATCH` without changing the actual authority outcome.

This interface is a design sketch, not executable code or implementation authorization.

## 12. Reproducibility

A future separately authorized implementation would require:

- deterministic fixtures with explicit ordered mutations;
- deterministic oracle behavior over identical fixture bytes and schema versions;
- no network dependency for core case execution;
- machine-readable fixtures and results;
- stable case IDs;
- stable, explicit schema versioning and migration rules;
- explicit provenance to the public source case;
- exact recording of actual and expected outcomes without expectation leakage;
- complete structured reason and invariant output; and
- no hidden model judgment in the authority oracle.

Reproducibility establishes repeatable harness behavior. It does not establish that the oracle is correct, that the contract is complete, or that an external system is safe.

## 13. Attacker Contribution Model

An external engineer proposing a break case should provide:

- a minimal machine-readable fixture;
- claimed expected result;
- claimed actual result;
- exact public-contract interpretation;
- invariant identifiers allegedly bypassed;
- deterministic reproduction steps;
- the source case or reason a new case is necessary; and
- an explanation of why the result is contract-level rather than fixture- or implementation-level.

Contributor-supplied expected outcomes, explanations, votes, signatures, or reputations do not become authority and do not control the oracle. Consensus is not evidence of independence. Multiplicity does not establish independence.

Contributions should remain public and abstract enough to avoid credentials, operational exploit details, private topology, hidden fixtures, validators, schemas, enforcement internals, recovery mechanisms, or unpublished private implementation.

## 14. Non-Goals

The v0 lab is not:

- the private Ground Truth implementation;
- an AI model evaluator;
- a sandbox;
- an agent runtime;
- an MCP security product;
- a policy engine;
- a production authorization server;
- a formal proof system;
- a certification framework;
- a deployment control plane; or
- evidence that Ground Truth solves AI safety generally.

It also does not validate implementation behavior, promise containment, prevent privilege escalation, certify an agent, or convert case coverage into authority.

## 15. Implementation Authority

This design artifact creates no implementation authority.

Implementation of the Authority Lab requires a separate explicit authorization decision after this design survives hostile exact-head review.
