# Authority Lab v1 Mutation-Registry Closure Design

Status: implementation design only

Scope: Authority Lab v1 mutation-registry closure and boundary-transition continuity

Schema: `authority-lab-v1` (unchanged)

This document specifies the smallest executable repair for the counterexample recorded in `FRONTIER_DELTA_AUTHORITY_BOUNDARY_ESCAPE.md`. It does not implement the repair, alter the public authority contract, authorize deployment, advance a roadmap phase, or authorize merge.

## 1. Defect summary

Authority Lab v1 parses `Mutation.field` as an arbitrary string, retains it in the fixture, and displays it in the trace. The oracle evaluates continuity only for names in finite canonical, relational, and objective-binding registries. A syntactically accepted field outside those registries is therefore semantically invisible.

Starting from the valid positive case `LAB-V1-032`, appending `execution_host: SANDBOX-S1 -> HOST-S2` without fresh T3 authority leaves the actual result incorrectly `AUTHORIZED`. Fourteen authority-relevant boundary-transition names reproduce that omission. By contrast, registered `boundary_epoch` and `execution_context` mutations fail closed. The defect is one registry-closure failure, not fourteen absent invariants:

> Open accepted mutation vocabulary + closed continuity-check registry permits explicit authority-relevant boundary transitions to disappear from authority evaluation.

## 2. Normative contract basis

The repair enforces existing obligations rather than adding authority semantics.

- `ARCHITECTURE.md` requires the exact applicable tuple, boundary, objective binding, evidence relationship, authority-relevant state, and consumption eligibility to remain established immediately before and at T3. A missing required fact is `UNAVAILABLE`; an established applicable prohibition is `DENIED`.
- `SECURITY_MODEL.md` requires exact identity continuity, makes boundary selection authority-sensitive, and says a binding from one organization, tenant, environment, authority domain, boundary epoch, or root does not silently authorize another.
- `EVIDENCE_MODEL.md` binds evidence to the exact decision and transition it supports. Evidence, verification success, repetition, quorum, and consensus do not confer authority.
- `INV-CONT`, `INV-DISC`, `INV-BND`, `INV-EVD`, `INV-USE`, and `INV-CLO` already cover exact transition continuity, discrimination, applicable boundary and lineage, evidence applicability, replay/consumption, and derived or inherited effects.
- Authority Lab v1 already requires exact current `objective_binding`, independently admitted source/root authority, lifecycle validity, current ordering, and transformation continuity.

The frozen contract remains exactly the six-coordinate tuple `(subject, artifact, control_state, identity_basis, boundary_epoch, decision)`, the six invariants above, and the three outcomes `AUTHORIZED`, `DENIED`, and `UNAVAILABLE`.

## 3. Current implementation gap

`authority_lab/model.py` accepts any exact string in `Mutation.field`. `authority_lab/oracle.py` separately enumerates the canonical state, relational, and objective-binding fields it knows how to check. Those two sets are not closed under one definition. The trace in `authority_lab/runner.py` makes the mutation visible but visibility has no authority effect.

The gap is not that every descriptive word must become a tuple coordinate. It is that an executable mutation record has authority semantics, yet its accepted name need not resolve to any evaluator-owned semantic target. The repair must make successful field admission imply deterministic evaluation.

## 4. Canonical mutation vocabulary

The implementation shall define one immutable registry in `authority_lab/model.py`. Both parsing and oracle evaluation shall consume that registry. No second list of accepted mutation names may exist.

Each entry contains:

1. one exact canonical field name;
2. zero or more exact, documented legacy aliases;
3. one target kind: `STATE`, `RELATION`, `BINDING`, or `FACT`;
4. one existing target name;
5. the exact value type or strict relation parser; and
6. its evaluation rule.

All admitted executable mutations are authority-relevant. There is no semantically ignored `diagnostic`, `comment`, `extension`, or free-form mutation class. Descriptive observations belong in fixture `notes`, titles, or explicit facts outside `t2.mutations` and cannot affect authority.

### 4.1 Canonical state fields

These names resolve to existing T1/T3 authority state and are checked as ordered chains:

`subject`, `artifact`, `control_state`, `identity_basis`, `boundary_epoch`, `decision`, `applicable_boundary`, `consumption_state`, `decision_binding`, `evidence_id`, `execution_context`, `grant_id`, and `subject_mode`.

The current synonyms `consumption` and `consumption_state` resolve to the same canonical target. No other spelling synonym is implicit.

### 4.2 Canonical relational fields

These names retain their current strict typed parsers and chain checks:

`boundary_epoch_binding`, `closure_binding`, `consumption_binding`, `delegation_binding`, `evidence_binding`, `execution_control_binding`, and `freshness`.

### 4.3 Canonical objective-binding fields

These names retain their current strict typed parsers and binding evaluation:

`authority_root`, `binding_lifecycle`, `binding_ordering`, `binding_source_authority`, `contract_transformation_binding`, `decision_contract_identity`, `objective_binding`, and `objective_identity`.

### 4.4 Closed auxiliary fact fields

Three maintained cases need exact authority-relevant state that is not itself a tuple coordinate. They shall use these closed fact targets through the existing `Fact` model:

`commit_state`, `credential_identity`, and `tool_connector_identity`.

A `FACT` mutation's `before` is an explicit T1 observation, not authority evidence. Its accumulated final value must resolve against the independently supplied T3 fact of the registered target name. When the T3 fact is `KNOWN`, its value must equal the accumulated value. When it is `UNKNOWN`, the accumulated value may be the exact marker `UNKNOWN`, but the authority result remains `UNAVAILABLE`. `CONFLICTING`, absence, ambiguity, or a final mismatch is also `UNAVAILABLE`. A fact target is not authority merely because it is in the registry; it remains subject to the existing applicable contract and oracle checks.

## 5. Normalization rules

There is deliberately no lossy normalization. Field admission proceeds as follows:

1. `field` must be a JSON string and the mutation object must have exactly `field`, `before`, and `after` keys.
2. The string must already be ASCII lower snake case matching `^[a-z][a-z0-9_]*$`.
3. The parser performs no trimming, Unicode normalization, case folding, punctuation replacement, namespace removal, suffix removal, or last-component extraction.
4. The exact string is looked up in the canonical registry and the finite legacy-alias map.
5. A canonical name and all its aliases resolve to one canonical target before mutations are grouped or ordered.

Consequences are intentional:

- `execution_host`, if not canonical, is structurally valid but unknown and produces `UNAVAILABLE`.
- `Execution_Host`, ` execution_host`, `execution-host`, `execution.host`, `ns/execution_host`, bracketed paths, full-width characters, zero-width characters, and non-ASCII confusables are malformed field names and produce deterministic input failure.
- `wrapper_execution_host` and `vendor_execution_host_v2` are structurally valid but unknown and produce `UNAVAILABLE`; prefixes and suffixes do not create aliases.
- An object, array, number, or nested wrapper in place of the field string is malformed input.

This is a closed allowlist, not a blacklist of fourteen observed attack strings.

## 6. Semantic mapping

Boundary manifestations are encoded through existing authority state. Fixture authors do not gain new synonyms for the same concept; they select the existing canonical target whose authority relationship actually changed.

| Transition family | Required canonical representation | Existing authority semantics | Absent fresh/current T3 establishment |
|---|---|---|---|
| Execution host or sandbox | `control_state` plus `execution_context`; `applicable_boundary`/`boundary_epoch` when containment lineage changes | `INV-CONT`, `INV-BND`, `execution_control_binding`, `boundary_epoch_binding` | `UNAVAILABLE` |
| Process identity | `identity_basis` and `execution_context`; `boundary_epoch` for restart lineage | `INV-CONT`, `INV-DISC`, `INV-USE` | `UNAVAILABLE` |
| Parent to child/sub-agent | `subject`, `subject_mode`, and `delegation_binding`; `closure_binding` for derived effect | `INV-DISC`, `INV-CLO` | `UNAVAILABLE` |
| Tool substitution | `control_state`, `execution_context`, and exact `execution_control_binding` | `INV-CONT`, `INV-DISC`, `INV-CLO` | `UNAVAILABLE` |
| Connector substitution | `tool_connector_identity`, plus `control_state`/`execution_context` when the authority context changes | `INV-CONT`, `INV-EVD`, `INV-CLO` | `UNAVAILABLE` |
| Credential context | `identity_basis`, `credential_identity`, and, when applicable, `subject` | `INV-DISC`, `INV-BND` | `UNAVAILABLE` |
| Trust or authority domain | `applicable_boundary` and `boundary_epoch` | `INV-BND` | `UNAVAILABLE` |
| Tenant or account | `applicable_boundary`, `identity_basis`, and `boundary_epoch` | `INV-BND`, `INV-DISC` | `UNAVAILABLE` |
| Network boundary | `control_state`, `execution_context`, and, when authority scope changes, `applicable_boundary` | `INV-CONT`, `INV-BND` | `UNAVAILABLE` |
| Restart or re-entry | `boundary_epoch`, `execution_context`, `consumption_state`, and the grant/evidence relations | `INV-CONT`, `INV-USE` | `UNAVAILABLE` |
| Raw to summarized/compressed/transformed state | `artifact`, `evidence_binding`, and `closure_binding`; `contract_transformation_binding` when the decision contract changes | `INV-EVD`, `INV-CLO`, transformation continuity | `UNAVAILABLE` |
| Shared-state consumer | `subject`, `evidence_binding`, `delegation_binding`, and `closure_binding` as applicable | `INV-DISC`, `INV-EVD`, `INV-CLO` | `UNAVAILABLE` |
| Relay actor | `subject`, `identity_basis`, and exact delegation/evidence relations | `INV-DISC`, `INV-EVD`, `INV-CLO` | `UNAVAILABLE` |
| Execution principal | `subject`, `identity_basis`, and applicable delegation | `INV-DISC`, `INV-BND`, `INV-CLO` | `UNAVAILABLE` |

The observed strings `execution_host`, `process_identity`, `child_agent`, `tool`, `connector`, `credential_context`, `trust_domain`, `tenant_account`, `network_boundary`, `restart_instance`, `authority_state_representation`, `authority_consumer`, `relay_actor`, and `execution_principal` are not added as loosely interchangeable aliases. In a v1 fixture they either use the canonical representation above or fail closed as unknown. This prevents a growing synonym surface from becoming a second open vocabulary.

## 7. Unknown-field and malformed-input behavior

A structurally valid field name absent from the registry and legacy-alias map is retained for traceability, classified `UNKNOWN`, and causes an early authority result:

- outcome: `UNAVAILABLE`;
- reason: `UNKNOWN_MUTATION_FIELD`;
- detail: the exact unknown field names, sorted by their UTF-8 byte representation for deterministic output;
- precedence: after schema/version validity is established and after the v0 non-authorization gate, but before any T1 or T3 authority conclusion, including an otherwise established denial.

The early precedence is necessary because the evaluator cannot prove that the unknown transition is irrelevant or that another condition applies to the same current tuple. It must not speculate `DENIED`, and it must not preserve `AUTHORIZED`.

Malformed input does not receive an authority outcome. Wrong keys, wrong types, malformed field names, malformed typed values, nested/wrapped mutation records, and semantically empty no-op mutations (`before == after`) raise the existing deterministic `ValueError`-class input/schema failure. Harness status and authority outcome are not applicable to a fixture that did not load.

## 8. Boundary-continuity rules

After alias resolution, the oracle groups mutations by canonical target while preserving their original array order.

1. A chain begins at the exact corresponding T1 state or typed relation where one exists. A registered auxiliary fact chain begins at its first explicit `before` value and must terminate in the exact T3 fact.
2. For every mutation, `before` must type-exactly equal the accumulated current value. Its `after` becomes the next value.
3. Two aliases resolving to the same target participate in one chain; aliases cannot establish parallel histories.
4. A duplicate whose `before` does not equal the accumulated value, an omitted intermediate value, an order-dependent discontinuity, an absent final T3 value, or a final mismatch is `UNAVAILABLE`.
5. A recognized boundary change invalidates cached T1 applicability. T3 must establish the exact current tuple, applicable boundary and epoch, identity, execution-to-control relation, evidence applicability, grant/effect and use state, objective binding, and any delegation or closure required for the new state.
6. A mutation record is never authority evidence. It describes a change; it cannot attest to the legitimacy of its own `after` value.
7. Re-establishment must use distinct current evidence and an exact lineage-linked `reestablishment` when authority state changed. A changed grant must satisfy the existing new-grant or authority-preserving transition rules.
8. Source/root authority for boundary and objective-binding facts must remain independent of the requester, changed subject, child agent, relay, wrapper, shared memory, evidence producer, model, or verifier.

If the current applicable state is missing, stale, ambiguous, conflicting, incomparable, or not provably continuous, the result is `UNAVAILABLE`. If exact current authoritative state establishes rejection, invalidity, revocation, supersession, or prohibition for the applicable tuple, the result is `DENIED`. Exact current re-establishment can still reach `AUTHORIZED`.

## 9. Migration strategy

The migration is atomic with the implementation and does not change case IDs, expected outcomes, or the schema string.

| Existing field | Classification | Migration or compatibility mapping |
|---|---|---|
| Registered state, relation, and binding names | Normative authority-relevant | Retain; resolve through the single registry |
| `privilege` | Legacy authority-relevant | Alias to `control_state`; migrate `LAB-V0-002` to the canonical name |
| `connector_endpoint` | Legacy authority-relevant | Alias to `tool_connector_identity`; migrate `LAB-V0-004` |
| `principal` | Legacy authority-relevant | Alias to `subject`; migrate `LAB-V0-005` |
| `credential` | Legacy authority-relevant | Alias to `credential_identity`; migrate `LAB-V0-005` |
| `actor_context` | Legacy authority-relevant | Alias to `execution_context`; migrate `LAB-V0-006` |
| `monitor_context` | Descriptive no-op in the maintained corpus | Remove the no-op mutation from `LAB-V0-006`; retain observation in notes/facts, not executable mutation state |
| `acknowledgment` | Descriptive carryover in the maintained corpus | Remove it from `LAB-V0-008`; exact consumption and commit state already carry the authority consequence |
| `commit_state` | Normative auxiliary fact | Retain as canonical `FACT`; ensure exact T3 fact termination in `LAB-V0-009` |
| `acting_subject` | Redundant pre-T1 description in the maintained corpus | Remove it from `LAB-V0-010`; exact T1/T3 subject plus typed delegation already carry the authority relation |

Retained legacy aliases are finite, explicit, target-checked, and documented. They never bypass continuity. Canonical names are emitted in maintained fixtures and traces. The three removed descriptive/redundant names are not aliases: an unmigrated fixture using one fails closed as an unknown field. Adding or removing an alias requires a later separately reviewed compatibility decision.

No other descriptive mutation remains permitted. A third-party v1 fixture using an arbitrary descriptive field now gets `UNAVAILABLE`, which is the intended fail-closed security hardening. A malformed third-party fixture remains a load failure. V0 inputs retain the existing diagnostic-only path and cannot authorize.

## 10. Hostile fixture matrix

The implementation slice adds `LAB-V1-033` through `LAB-V1-048`. Every loadable case below has expected harness status `PASS`; malformed representation tests are unit-level load failures with no harness status or authority outcome.

| Case | Hostile condition | Representation | Expected authority | Expected reason class |
|---|---|---|---|---|
| 033 | Unknown mutation field | `execution_host_v2` | `UNAVAILABLE` | `UNKNOWN_MUTATION_FIELD` |
| 034 | Execution-host change | canonical `control_state` + `execution_context` without T3 continuity | `UNAVAILABLE` | continuity mismatch |
| 035 | Process change | canonical `identity_basis` + `execution_context` without re-establishment | `UNAVAILABLE` | identity/continuity unavailable |
| 036 | Child-agent inheritance | `subject` + `subject_mode`, no delegation | `UNAVAILABLE` | delegation/closure unavailable |
| 037 | Tool substitution | `control_state`/`execution_context`, stale execution binding | `UNAVAILABLE` | execution binding unavailable |
| 038 | Connector substitution | `tool_connector_identity`, no current connector fact | `UNAVAILABLE` | fact/evidence applicability unavailable |
| 039 | Credential-context change | `identity_basis` + `credential_identity`, stale prior evidence | `UNAVAILABLE` | identity/evidence unavailable |
| 040 | Trust-domain change | `applicable_boundary` + `boundary_epoch`, old root/binding replayed | `UNAVAILABLE` | boundary unavailable |
| 041 | Restart/re-entry | `boundary_epoch` + `execution_context`, old grant/consumption replayed | `UNAVAILABLE` | use/continuity unavailable |
| 042 | Summarized-state carryover | `artifact`, no admitted transformation/closure | `UNAVAILABLE` | evidence/closure unavailable |
| 043 | Shared-state relay | `subject`, no delegation/evidence binding to consumer | `UNAVAILABLE` | delegation/evidence unavailable |
| 044 | Alias/spelling injection | structurally valid `executionhost` | `UNAVAILABLE` | `UNKNOWN_MUTATION_FIELD` |
| 045 | Wrapper/namespaced injection | structurally valid `wrapper_execution_host` | `UNAVAILABLE` | `UNKNOWN_MUTATION_FIELD` |
| 046 | Explicit prohibited transition | exact canonical transition plus current applicable prohibition | `DENIED` | established prohibition |
| 047 | Missing continuity control | exact recognized transition, no current lineage | `UNAVAILABLE` | continuity unavailable |
| 048 | Correctly re-established transition | exact canonical transition and complete independent T3 establishment | `AUTHORIZED` | current authority established |

Unit tests additionally cover malformed case/whitespace/Unicode/punctuation/nested names, duplicate conflicting chains, chain order, stale re-establishment, self-declared boundary authority, relay laundering, and transformed-state laundering. At least one fixture deliberately carries the wrong expected outcome to prove oracle independence after the new gate.

## 11. Positive cross-boundary re-establishment

`LAB-V1-048` demonstrates that a boundary change is not an automatic denial.

At T1, subject `S` has exact authority for artifact `A`, control state `C1`, identity basis `I1`, boundary epoch `B1`, execution context `E1`, applicable boundary `AB1`, grant `G1`, evidence `EV1`, and the currently admitted objective/decision binding.

At T2, ordered canonical mutations explicitly move the relevant state to `C2`, `I2`, `B2`, `E2`, and `AB2`, together with the exact typed boundary, execution, evidence, grant, consumption, delegation/closure (if applicable), and objective-binding relations required by those changes.

At T3:

- the applicable independent authority root admits `AB2` and the exact current boundary epoch;
- identity continuity for `S` into `I2` is established rather than inferred from a name or credential copy;
- `E2` is exactly bound to `C2`;
- distinct current evidence `EV2` is bound to the exact current artifact, decision, and transition;
- an exact lineage-linked re-establishment replaces the changed authority state;
- a distinct current grant `G2`, or a valid authority-preserving grant transition, binds the current effect and consumption state;
- objective binding remains exact, current, in scope, independently sourced, and transformation-continuous; and
- no applicable prohibition exists.

Only after every existing check succeeds may the outcome be `AUTHORIZED`. The mutation list itself, copied credentials, a parent agent, shared state, or old evidence cannot supply any of those facts.

## 12. `DENIED` versus `UNAVAILABLE`

The repair preserves the existing distinction.

| Condition | Result |
|---|---|
| Unknown but structurally valid mutation field | `UNAVAILABLE` |
| Recognized change with missing, stale, ambiguous, conflicting, incomparable, or not-provably-current continuity | `UNAVAILABLE` |
| Recognized change whose exact current applicable boundary and tuple are established, with an established applicable rejection, invalidity, revocation, supersession, or prohibition | `DENIED` |
| Recognized change with exact current independent re-establishment and all other requirements satisfied | `AUTHORIZED` |
| Malformed mutation representation or typed value | input/schema failure; no authority outcome |

An unknown transition cannot be converted to `DENIED` merely because another fixture field appears prohibitive: applicability to the post-mutation tuple has not been established. Conversely, established current prohibition must not be weakened to `UNAVAILABLE` once exact applicability is proven.

## 13. Implementation surface

The implementation is intentionally narrow:

1. `model.py` owns the immutable registry, exact alias map, name-shape validation, target kinds, and parsed mutation classification.
2. `oracle.py` performs the early unknown-field gate and evaluates every admitted mutation by iterating the registry-resolved targets. Existing state, relation, binding, and fact evaluators remain the semantic engines.
3. `runner.py` renders original field, canonical target, and unknown-field reason deterministically without consulting expected outcomes.
4. Maintained fixtures are atomically canonicalized and the hostile matrix is added.
5. Tests freeze closure: every registry entry must have an evaluator, every evaluator-owned mutation target must have a registry entry, aliases must resolve to exactly one target, and there must be no ignored parsed class.

The registry must be immutable at evaluation time. Runtime plugin registration, environment-driven aliases, fixture-defined namespaces, wildcard prefixes, and caller-supplied mapping tables are forbidden.

## 14. Exact files expected to change in implementation

- `authority_lab/model.py`
- `authority_lab/oracle.py`
- `authority_lab/runner.py`
- `authority_lab/README.md`
- `tests/test_authority_lab.py`
- `cases/authority_lab/LAB-V0-002.json`
- `cases/authority_lab/LAB-V0-004.json`
- `cases/authority_lab/LAB-V0-005.json`
- `cases/authority_lab/LAB-V0-006.json`
- `cases/authority_lab/LAB-V0-008.json`
- `cases/authority_lab/LAB-V0-010.json`
- new fixtures `cases/authority_lab/LAB-V1-033.json` through `LAB-V1-048.json`

No architecture, security-model, evidence-model, public tuple, invariant, or outcome file requires semantic change. Documentation references may be updated only to describe implemented behavior.

## 15. Exact tests expected to be added

`tests/test_authority_lab.py` shall add assertions for:

1. the registry contains each accepted canonical name exactly once;
2. every registry target kind has an oracle evaluator and no evaluator accepts an unregistered name;
3. every retained legacy alias resolves to exactly one checked canonical target;
4. a structurally valid unknown name returns `UNAVAILABLE/UNKNOWN_MUTATION_FIELD`;
5. unknown-name ordering and trace details are deterministic;
6. case, whitespace, punctuation, namespace syntax, non-ASCII, zero-width, and confusable names fail loading;
7. nested/wrapped mutation representations and extra/missing keys fail loading;
8. `before == after` fails loading after the maintained no-op is migrated;
9. canonical and alias mutations for the same target share one ordered chain;
10. duplicate conflict and reversed order return `UNAVAILABLE`;
11. the fourteen demonstrated boundary aliases can no longer preserve `AUTHORIZED`—they are unknown unless re-expressed canonically;
12. host, process, child-agent, tool, connector, credential, domain, restart, summary, shared-state, and relay cases fail closed;
13. stale or self-declared re-establishment cannot authorize;
14. copied credentials, majority agreement, repeated evidence, shared memory, relays, and transformed state cannot synthesize continuity;
15. an exact current prohibited transition returns `DENIED`;
16. complete independent cross-boundary re-establishment returns `AUTHORIZED`;
17. a normal no-boundary-change positive case remains `AUTHORIZED`;
18. v0 can never authorize;
19. expected outcomes remain oracle-independent; and
20. exactly six tuple coordinates, six invariant identifiers, and three authority outcomes remain frozen.

## 16. Backward-compatibility constraints

- The schema remains `authority-lab-v1`; the existing mutation object already has the required structure, so no schema-version change is necessary.
- The tuple, invariant set, authority outcomes, objective-binding semantics, deterministic local-only execution, and expectation independence remain unchanged.
- Existing maintained fixture IDs and expected authority outcomes remain stable after atomic canonicalization.
- Exact retained legacy aliases remain loadable but are now evaluated; they are never ignored. Removed descriptive/redundant names fail closed as unknown.
- Old v0 inputs remain diagnostic and cannot authorize.
- Third-party v1 fixtures relying on unregistered mutation names intentionally change from possible silent acceptance to fail-closed `UNAVAILABLE` or malformed-input failure. Preserving silent omission is not compatible behavior.
- Existing positive paths remain reachable, including ordinary unchanged-boundary authorization and the new exact cross-boundary re-establishment case.

## 17. Hostile design review

| Attack | Attempt against this design | Disposition |
|---|---|---|
| Unknown-field injection | Add `execution_host_v2` to an otherwise positive fixture | Exact lookup misses; early `UNAVAILABLE` |
| Alias injection | Use an undocumented synonym such as `host`, `runtime_host`, or `executionhost` | No implicit aliases; `UNAVAILABLE` |
| Case/whitespace variant | Use `Execution_Host` or padded text | Fails ASCII lower-snake validation; input failure |
| Unicode/confusable | Use full-width, combining, or zero-width characters | Non-ASCII or pattern failure; input failure |
| Nested/wrapped representation | Put `field` under `wrapper`, use an object value, or add namespace keys | Exact-key/type failure; input failure |
| Wrapper/namespaced name | Use `wrapper_execution_host` | Valid shape but absent registry; `UNAVAILABLE` |
| Duplicate conflict | Apply `C1->C2` and then `C1->C3` to one canonical target | Second `before` mismatches accumulated `C2`; `UNAVAILABLE` |
| Order dependence | Reverse a valid `C1->C2->C3` chain | First `before` mismatches T1; `UNAVAILABLE` |
| Alias/canonical split | Mutate an alias and canonical name as if they were independent | Both resolve to one target chain; discontinuity is `UNAVAILABLE` |
| Stale re-establishment | Reuse T1 evidence/grant/root ordering after B1→B2 | Current lineage/evidence/grant/binding checks fail; `UNAVAILABLE` |
| Self-declared authority | Let changed subject, requester, model, verifier, or mutation assert admission | A mutation only describes a change and is not authority evidence; independent root/source checks fail; `UNAVAILABLE` or established `DENIED` |
| Child-agent inheritance | Change `subject` without exact current delegation and closure | `UNAVAILABLE` |
| Shared-memory laundering | Change artifact/consumer while replaying summarized state | Exact evidence/closure/subject relations fail; `UNAVAILABLE` |
| Relay laundering | A valid holder relays evidence to an unbound subject/domain | Possession is not authority; delegation/evidence/boundary checks fail; `UNAVAILABLE` |
| Transformed-state laundering | Wrap, compress, summarize, or derive state without admitted transformation | Artifact/evidence/closure or contract transformation fails; `UNAVAILABLE` |
| Blanket boundary denial | Treat every boundary mutation as forbidden | Rejected by `LAB-V1-048`; complete current re-establishment reaches `AUTHORIZED` |
| Denial laundering | Add unknown mutation beside a denial to claim exact applicability | Unknown gate returns `UNAVAILABLE` until current tuple is established; no speculative `DENIED` |

Hostile verdict for the design: **PASS within the modeled input boundary**. Successful parsing can no longer create a semantically ignored mutation, exact and legacy names converge on checked targets, and the demonstrated `execution_host` counterexample fails closed. PASS means failure to falsify this design within the attempted scope, not proof of security, completeness, parser correctness, production observation, or universal boundary continuity.

## 18. Residual limitations

- The lab only evaluates transitions represented in its fixture. It cannot prove that a real host, runtime, connector, credential system, monitor, or agent detected and reported a boundary change.
- The fixture remains able to assert false admitted roots or facts. Production acquisition and protection of those roots are outside the lab's authority objective.
- The closed vocabulary is complete only for the modeled v1 contract. A genuinely new authority relation requires a separately reviewed registry addition and semantic mapping; it must fail closed until then.
- Auxiliary fact values are deterministic fixture inputs, not proof that their external referents are genuine.
- ASCII exactness prevents parser aliases but does not prevent misleading human prose in notes; notes never affect authority.
- The design does not prove rollback-resistant epoch allocation, credential custody, process attestation, external ordering integrity, or persistence detection.
- A cross-boundary `AUTHORIZED` result proves only that the supplied deterministic facts satisfy the modeled contract. It does not prove the transition safe, lawful, wise, or correctly observed.
- Registry closure cannot repair an omitted mutation that was never represented. That is an observation/instrumentation problem outside this slice.

## 19. Frozen-contract statement and next step

No frozen-contract expansion is required. The repair adds no tuple coordinate, invariant, authority outcome, schema version, or self-authorizing evidence path. Boundary details map into the existing six coordinates, typed relational facts, objective-binding facts, lifecycle/order/transform logic, evidence applicability, and use/replay state.

The smallest next slice is one implementation commit from this design: introduce the single immutable registry and early unknown-field gate, atomically migrate the six maintained fixtures listed above, add cases 033–048 and the enumerated unit tests, then run the full public suite, every Authority Lab fixture, diff checks, and an exact-head hostile review. Implementation remains separately authorized; this design does not authorize merge or deployment.
