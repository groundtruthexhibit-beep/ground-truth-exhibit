# Authority Lab objective_binding Implementation Design

## Status and scope

This is a design-only specification for the narrowest future Authority Lab change that can enforce the adopted public `objective_binding` rule. It does not implement the rule, modify the public contract, authorize implementation or deployment, move the roadmap, or describe private-core behavior.

The design preserves the public authority tuple, invariant set, and outcome set. Names such as `objective_id`, `decision_contract_id`, and `binding_id` below identify relational facts used to evaluate the existing tuple; they are not tuple coordinates.

## Exact public baseline

`OBJECTIVE_BINDING_IMPLEMENTATION_DESIGN_BASELINE=342b476d8d9f944bc914d394d52ab45bdedc384f`

That exact public `main` is the merge result of PR #18 and contains reviewed contract commit `548bf9592fadabbee4cfcf410bfa7af0f95c8690`. The baseline has:

- tuple `(subject, artifact, control_state, identity_basis, boundary_epoch, decision)` — exactly six coordinates;
- invariants `INV-CONT`, `INV-DISC`, `INV-BND`, `INV-EVD`, `INV-USE`, and `INV-CLO` — exactly six invariants; and
- outcomes `AUTHORIZED`, `DENIED`, and `UNAVAILABLE` — exactly three outcomes.

At design start the public test suite passed 73 of 73 tests, all 12 Authority Lab v0 fixtures passed, and the worktree was clean.

## Adopted public-contract requirement

Before encoded decision contract `D` may participate at T1 or T3, an exact current authoritative `objective_binding` must admit `D` for the exact applicable objective and decision context. The binding must originate at the applicable independent authority boundary or at an exact current delegate within scope. `D`, the requester, verifier, evidence producer, formalizer, compiler, model, agent, signature, proof, provenance record, quorum, repetition, or agreement cannot establish that admission merely by asserting or producing it.

Admission and operational satisfaction are separate:

1. objective-to-contract admission determines whether `D` is eligible to be evaluated; and
2. evidence-to-contract satisfaction determines whether admitted `D` succeeds.

An admitted contract does not manufacture its evidence. Successful evidence does not admit its contract.

## Current Authority Lab architecture

The following describes the implementation at the exact baseline, not an inferred production architecture.

### Input and fixture format

`authority_lab/runner.py` loads local JSON objects and accepts only `schema_version: "authority-lab-v0"`. Each fixture contains descriptive fields, the exact six-field `authority_tuple`, a T1 result/evidence/authority-state record, ordered T2 mutations, T3 facts and requirements, a prohibition, applicable invariant identifiers, and expected harness values. Twelve files exist under `cases/authority_lab/`.

`run_fixture` builds `OracleInput` before reading `expected_outcome`. `title`, `expected_outcome`, and `expected_reason` are not oracle inputs. Only after evaluation does the runner compare actual and expected outcomes and produce harness status `PASS` or `CASE_MISMATCH`. Those harness statuses are not authority outcomes.

### Oracle input and facts

`authority_lab/model.py` defines immutable dataclasses. `AuthorityTuple` accepts exactly the six public fields. `AuthorityStateBinding` records those fields plus evidence, execution context, boundary, grant, consumption, and subject-mode relationships. `OracleInput` holds T1, T2, T3, re-establishment, grant-transition, prohibition, and applicable-invariant data.

Facts use `FactState.KNOWN`, `UNKNOWN`, or `CONFLICTING`. A known fact carries one arbitrary JSON value; a conflicting fact carries at least two values. The current generic fact container does not type semantic relations. The oracle instead validates five mandatory relational facts—boundary/epoch, execution/control, consumption/grant/effect, delegation, and closure—against exact expected mappings with no missing or extra keys.

The oracle owns 16 mandatory T3 fact names. Fixture `required_facts` can add requirements but cannot remove oracle-owned requirements. For non-relational required facts, `required_values` must name an exact expected value. It is fixture input, not an oracle verdict, and cannot override the oracle's hard-coded authority-permitting values for freshness, evidence binding, or consumption.

### State mutation and time

T1 records an evaluated result, evidence identifiers, and one exact authority-state binding. T2 is represented by an ordered JSON array of `{field, before, after}` records and a Boolean `creates_authority` claim. The claim must be false; T2 cannot create authority. The oracle deterministically walks recognized mutation chains from T1 state to observed T3 state. A discontinuous chain or a mutation that disappears at T3 yields `UNAVAILABLE`.

At T3 all mandatory and fixture-required facts must be established. Changed authority state requires a distinct evidence identifier and an exact `Reestablishment` linked to T1 evidence. Re-establishment must target the observed current state, and relevant changes must be represented by T2 mutations. The current implementation has no objective, contract, binding, policy, schema, or authority-source identity in this continuity record.

### Identity, versions, grants, and effects

Identity-bearing tuple and authority-state values are exact, non-empty strings. Parsing does not trim, normalize, or coerce numeric identities. The current schema has no general version or generation type and no authoritative ordering record; version-like values appear only where a fixture models them as ordinary strings.

Consumption is bound to the active grant, subject, artifact, and boundary epoch. A consumed grant cannot be reset to unused. Scope changes cannot retarget an old grant unless there is a distinct current grant or an exact `AUTHORITY_PRESERVING` transition whose complete grant path and previous/current authority states match. Delegation and artifact closure are separately exact. Generic provenance, aggregate agreement, and transformation do not inherit authority.

### Outcome derivation, uncertainty, and ordering

The current oracle first accumulates missing or conflicting required facts and an unknown or conflicting prohibition state; any such uncertainty returns `UNAVAILABLE`. It then checks tuple/value/boundary relationships, T1 and current decision outcomes, an applicable prohibition, authority-permitting core values, T1/T2/T3 continuity, grants, execution, consumption, delegation, and closure. Established T1 or current `DENIED`, or an established applicable prohibition, returns `DENIED`. Only complete success returns `AUTHORIZED`.

Iteration is deterministic: mandatory fact and invariant orders are constants, fixture-required order is preserved with duplicate removal, T2 mutations retain array order, and fixture discovery sorts paths. There is no network, wall-clock query, model judgment, majority vote, or external service. There is currently no objective-binding candidate ordering to resolve.

### Current trust assumptions

The lab treats fixture-provided `KNOWN` observations as admitted inputs. It tests deterministic consequences of those inputs but does not prove that a real observer established them. Observer identity, integrity, provenance, freshness, independence, and resistance to false fixture assertions are explicit trust preconditions. No current public implementation identifies an authoritative objective source; inventing one would be unsound.

## Representation options

| Option | Merits | Failure or cost | Assessment |
|---|---|---|---|
| A. Dedicated `objective_binding` relation record | Strong typing, readable scope, explicit identity and lifecycle references | A record alone can self-certify if it also declares its own authority/currentness; parallel candidates and ordering still need support | Necessary component, insufficient alone |
| B. Generic facts plus a new relation kind | Reuses `Fact`, `KNOWN/UNKNOWN/CONFLICTING`, trace rendering, and mutation machinery | Untyped nested dictionaries are easy to under-specify; one `CONFLICTING` bag cannot by itself resolve ordered candidates | Useful carrier, insufficient without validation |
| C. Encode binding in `control_state` | Few parser changes | Hides a mandatory relationship in one tuple value, conflates operational and admission state, weakens exact scope and hostile mutation testing | Reject |
| D. Put binding identity in `identity_basis` plus an authority relation | Reuses identity comparison | Conflates the tuple's identity basis with objective/contract admission and becomes a hidden tuple overload | Reject |
| E. Minimal composite | Typed binding records carried by generic facts, independent typed source/lifecycle/ordering relations, and continuity references | Requires a schema bump and focused model/oracle work | Recommend |

Option E is the narrowest representation that supports exact scope, source independence, multiple candidates, revocation, supersession, deterministic ordering, T1/T2/T3 mutation, and transformation closure without public structural expansion.

## Recommended representation

Retain `Fact` as the state envelope, but parse known relation values into strict immutable records before evaluation. Add these oracle-owned facts:

- `objective_identity`: the exact applicable objective and its generation/version identity;
- `decision_contract_identity`: the exact encoded `D` and its schema/version identity;
- `authority_root`: the independently admitted root identity, boundary, epoch, lineage, and authority generation;
- `objective_binding`: one candidate or an ordered tuple of candidate records, never a Boolean validity assertion;
- `binding_source_authority`: an independent root-membership or exact delegate relation;
- `binding_lifecycle`: authoritative current validity/revocation/rejection facts for candidate identities; and
- `binding_ordering`: the authoritative lineage and ordering facts needed to select the currently applicable candidate.

The first two are ordinary mandatory value facts. The root, binding, source-authority, lifecycle, and ordering facts are mandatory relational T3 facts validated by the oracle. A conditional `contract_transformation_binding` relation is required only when the current contract is derived from another contract. Adding fact names to `MANDATORY_T3_FACTS` and `RELATIONAL_T3_FACTS` extends executable obligations, not the public tuple or invariant set.

Extend the non-tuple T1 authority-state snapshot, re-establishment target, and grant-transition snapshots with references to the admitted objective, contract, binding, binding generation, authority generation, and policy/schema identities. This lets existing exact continuity machinery detect a changed binding rather than trusting a cached T1 outcome.

Do not serialize `binding_valid`, `source_authoritative`, `current`, or `wins_conflict` as verdict shortcuts. Serialize atomic identities, scopes, lineage, events, and order facts from which the oracle derives those conclusions.

## Semantic data requirements

The executable semantics require the following information, but not necessarily one field for every item:

| Required semantic fact | Minimal representation or reference |
|---|---|
| Applicable objective | Exact objective identity plus objective generation/version |
| Encoded decision contract | Exact contract identity plus schema/version; identity must discriminate transformed bytes/semantics as the admitted authority defines |
| Binding | Exact binding identity, disposition (`ADMIT` or `REJECT`), objective, contract, source, lineage, generation, and scope references |
| Source authority | Exact root or delegation relation to applicable boundary, epoch, authority generation, and permitted binding scope |
| Scope | Exact subject, artifact/effect, control state, identity basis, boundary epoch, decision, applicable boundary, and any narrower policy scope |
| Policy/schema | Exact identifiers and versions wherever applicable to objective, contract, or binding interpretation |
| Authority root | Exact root identity, applicable boundary, epoch, lineage, and authority generation |
| Lifecycle | Independently sourced active, invalid, revoked, rejected, or superseded event for exact binding and generation |
| Ordering | Exact authority lineage, monotonically comparable generation/order token, current head/event, and ordering source authority |
| Lineage | Root/delegate lineage and binding predecessor/supersession relationship where applicable |
| Transformation | Exact source `D`, target `D2`, objective, scope, boundary, relation identity, source authority, generation, and lifecycle |

`subject_scope`, `artifact_scope`, and decision/effect scope are required semantic relationships even when their serialized values duplicate tuple values. Duplicate comparison is deliberate: it proves exact binding rather than creating more tuple coordinates. Validity and currentness are conclusions derived from lifecycle and ordering records, not trusted flags. If no policy, schema, delegate, or transformation is applicable, that non-applicability must be represented unambiguously rather than silently omitted.

Use exact non-empty strings for opaque identities and non-negative integers for generations/order positions. Reject Booleans as integers. Generations are comparable only within the same authoritative lineage and ordering domain; a larger number from another source or fork does not win.

## Authoritative source model

The current lab lacks an objective-binding authority model. Add an explicit admitted `authority_root` fact for the applicable boundary and epoch, then derive binding-source authority as follows:

1. A direct source is authoritative only when its exact identity and authority generation match that root fact and its binding scope covers the exact context.
2. A delegated source is authoritative only through a separate exact current delegation record from that root (or a fully established delegation chain), with source, delegate, scope, lineage, authority generation, boundary, epoch, validity, and ordering all established.
3. The binding candidate cannot be used as evidence for either root membership or delegation.
4. The source must be independent of the governed requester/subject roles represented by the case; a role coincidence is not accepted merely because identifiers or signatures match.
5. A signature or provenance fact may authenticate the bytes attributed to a source, but authority still derives only from the root/delegation relation.

This makes self-authorization impossible within the modeled relations: `D`, its verifier, or a requester-supplied candidate has no path to admitted source authority unless the independent root/delegation facts establish one. As in v0, the ultimate correctness of the fixture's admitted root and observer facts is a trust precondition; the lab cannot prove its root from first principles.

## Admission algorithm

The oracle should run a deterministic `admit_objective_contract` phase before `D` or its evidence can influence an `AUTHORIZED` result:

1. Establish the exact applicable boundary, epoch, authority root, objective identity/generation, and contract identity/version. Unknown or conflicting applicability is `UNAVAILABLE`.
2. Parse candidate records strictly. Reject malformed schema as fixture/input error; treat an absent required candidate set as `UNAVAILABLE`.
3. Filter candidates by exact objective, `D`, policy/schema, tuple/effect scope, boundary, epoch, and lineage. An unknown required match is `UNAVAILABLE`; a current authoritative explicit scope rejection is a denial candidate.
4. For each surviving candidate, resolve source authority only from the independent root/delegation relation. Candidate assertion, signature, evidence, or expected outcome contributes nothing.
5. Validate candidate and source generations within their exact ordering domains. Never compare unrelated lineages.
6. Apply authoritative lifecycle events in deterministic order. Establish invalidity, rejection, revocation, and supersession for the exact identity/generation rather than inferring them from absence.
7. Resolve multiple current-looking candidates using the exact authoritative ordering head. Do not use input order, lexical ID order, timestamps not represented as admitted state, vote count, or majority.
8. If current `D` is derived, require its own admitted binding or validate an exact current authoritative transformation relation from the admitted source contract to `D`.
9. Produce an internal admission result containing the selected binding/reference and reason data. Its internal classification maps only to existing public outcomes and is not a fourth outcome.
10. Only an admitted result permits existing evidence-to-contract evaluation and remaining tuple, boundary, continuity, grant, consumption, delegation, and closure checks to continue toward `AUTHORIZED`.

Candidate selection uses semantic equality over strict parsed records, never labels or descriptive fixture text. Duplicate identical records are duplicates, not votes; contradictory duplicates remain a conflict unless authoritative ordering resolves them.

## Outcome derivation

Use a scoped precedence rule rather than a global “missing fact always wins” shortcut:

1. If the applicable boundary, tuple, objective, `D`, or facts needed to decide whether a negative binding event applies cannot be established, return `UNAVAILABLE`.
2. Once exact applicability is established, an authoritative current rejection, invalidity, revocation, superseding rejection/prohibition, or prohibited scope/use returns `DENIED`. Missing unrelated positive evidence must not downgrade that established denial to `UNAVAILABLE`.
3. If no applicable denial is established but admission source, scope, lineage, currentness, ordering, transformation, or conflict resolution is missing or unresolved, return `UNAVAILABLE`.
4. If an exact current authoritative binding admits `D`, evaluate `D` and all existing T3 requirements. Their existing denial/unavailability distinctions remain in force.
5. Return `AUTHORIZED` only after admission, contract/evidence success, and every other applicable current requirement succeeds.

Thus an unauthorized or self-declared candidate normally yields `UNAVAILABLE` when source authority is unestablished. It yields `DENIED` only when current authoritative state explicitly rejects or prohibits that candidate/use.

## T1/T2/T3 continuity

At T1 the oracle must perform the same admission algorithm and record the exact admitted objective, `D`, binding, source, source authority generation, binding generation, policy/schema, boundary/epoch, and scope in the evaluated authority state. T1 admission is provisional evidence about T1 only.

T2 continues to create no authority. Extend recognized ordered mutation fields to cover objective, `D`, binding identity, binding lifecycle, source/root, delegation, policy/schema version, authority generation, binding generation, scope, ordering head, and transformation relation. Revocation, supersession, rotation, narrowing, or unavailability is represented as an exact before/after transition.

At T3 recompute admission from current atomic facts. The mutation chain must reach those facts, and a changed admission state requires a distinct lineage-linked re-establishment. A cached T1 binding, result, record, or identical label is never sufficient. An objective/contract/binding change that lacks exact continuity returns `UNAVAILABLE`; an exact current revocation or rejection returns `DENIED`.

## Revocation and supersession

- A current authoritative revocation of the applicable binding is `DENIED`.
- Revocation of its source or required delegation is `DENIED` when exact current applicability is established; unknown source/delegation state is `UNAVAILABLE`.
- Supersession is valid only when the authoritative ordering relation identifies the successor in the same lineage and domain. A current superseding rejection/prohibition is `DENIED`; an admitted successor replaces the older candidate for further evaluation.
- A numerically newer record from an unauthorized source, another lineage, or another policy fork does not supersede anything.
- Rollback, restart, restore, cache, or reappearance of an older binding cannot erase a later revocation or supersession. The current authoritative ordering head must still select it; otherwise it is not usable.
- Conflicting generations or a missing/unavailable ordering source are `UNAVAILABLE` unless an independently established current prohibition already resolves the exact use as `DENIED`.
- Offline revocation is not guessed. If the required current revocation/ordering view cannot be established at T3, the outcome is `UNAVAILABLE`.

The lab should use explicit fixture order tokens and mutation sequences, never wall-clock time. It models reordered events by their authoritative order relation, not JSON array position alone.

## Conflict semantics

Two current-looking admissions, an admit/reject pair, authority-source forks, delegation forks, policy forks, and conflicting transformation relations are candidate conflicts. The oracle groups candidates by exact ordering domain and resolves them only when a current authoritative ordering fact selects a unique applicable head or establishes a total applicable sequence.

If no authoritative order exists, its source is unknown, or two incomparable authoritative lineages both claim applicability, return `UNAVAILABLE`. If the established applicable head rejects, revokes, invalidates, or prohibits the exact use, return `DENIED`. If it uniquely admits, continue evaluation. Neither record count, signature count, consensus, fixture order, nor lexical sorting creates authority.

## Transformation closure

For `D -> D2`, do not copy `D`'s binding identifier into `D2`. Admission succeeds only when either:

- `D2` has its own exact current authoritative objective binding; or
- an exact current authoritative transformation relation names source `D`, target `D2`, transformation identity/version, objective, policy/schema, scope, boundary/epoch, authority source, lineage, generation, and an admission-preserving disposition.

The transformation relation receives the same source-authority, lifecycle, currentness, ordering, conflict, and T3 continuity checks as a direct binding. Wrapping, compilation, optimization, normalization, migration, summarization, translation, schema transformation, byte similarity, provenance, a semantic-equivalence assertion, or a proof output alone does not establish admission.

## PR #15 executable regression design

Use three fixtures with identical exact tuple and operational evidence wherever the intended outcome permits:

| Case | Atomic facts | Derived result |
|---|---|---|
| U | Objective `O` requires `P`; incorrect `D` requires only `P'`; evidence establishes `P'`; `objective_binding` candidate/source relation for `O -> D` is absent or `UNKNOWN`; no independent evidence establishes `P` | `UNAVAILABLE`; unadmitted `D` is never evaluated as authority-permitting |
| D | Same objective, `D`, and `P'` evidence; exact current root, scope, and order select an authoritative rejection or revocation of `O -> D` | `DENIED`; the applicable admission is explicitly prohibited |
| A | Exact current root or in-scope delegate admits `D` for `O`; source, scope, lineage, versions, generations, lifecycle, ordering, and T3 continuity are exact; `D` and all existing requirements succeed | `AUTHORIZED`; binding admits evaluation but does not supply `D`'s evidence |

Case U directly closes the original executable gap: verifier `PASS` for `P'` has no code path around missing objective-to-contract admission.

## Positive AUTHORIZED path

A minimal legitimate fixture establishes exact objective `O1`, exact contract `D1`, applicable root `R1` at boundary `AUTH-BOUNDARY-1/B1`, exact admission `OB1` at the selected binding and authority generations, exact tuple/effect scope, active lifecycle, unique authoritative order head, and no transformation. T1 records that admission. T2 makes no relevant mutation. T3 independently re-establishes the same current facts, required operational evidence satisfies `D1`, grant and consumption are exact and unused, delegation/closure requirements succeed, and no applicable prohibition exists. The oracle may return `AUTHORIZED`.

If deleting any one mandatory binding relation still permits this case, or if the fully established case cannot authorize, the implementation is defective.

## Hostile fixture matrix

Design the future fixtures as atomic-fact variations, not embedded verdicts:

| # | Pressure | Expected executable result |
|---:|---|---|
| 1 | No applicable binding candidate | `UNAVAILABLE` |
| 2 | Candidate exists; source authority unknown | `UNAVAILABLE` |
| 3 | Conflicting admissions; authoritative ordering absent | `UNAVAILABLE` |
| 4 | Exact current authoritative binding revoked | `DENIED` |
| 5 | Exact current binding superseded by authoritative prohibition | `DENIED` |
| 6 | T1 admitted; exact T2 revocation; current T3 revocation established | `DENIED` |
| 7 | `D` names itself as binding/source without root relation | `UNAVAILABLE`; `DENIED` only if explicit rejection also exists; never `AUTHORIZED` |
| 8 | Requester supplies candidate without source authority | Same derivation as #7; never `AUTHORIZED` |
| 9 | Model produces candidate without source authority | Same derivation as #7; never `AUTHORIZED` |
| 10 | Verifier `PASS`; objective binding absent | `UNAVAILABLE` |
| 11 | Signature valid; signer not established as source | `UNAVAILABLE`, or `DENIED` if current authority explicitly rejects signer/use; never `AUTHORIZED` |
| 12 | Exact `D`, binding names a different objective | `UNAVAILABLE`, or `DENIED` only on explicit applicable rejection; never `AUTHORIZED` |
| 13 | Same objective label, wrong objective generation | Same derivation as #12; never `AUTHORIZED` |
| 14 | Binding root/boundary differs from applicable boundary | `UNAVAILABLE`, or `DENIED` on explicit cross-boundary prohibition; never `AUTHORIZED` |
| 15 | Delegate's authority is currently revoked | `DENIED` when exact applicability is established; never `AUTHORIZED` |
| 16 | `D2` derived from bound `D`; no direct or transformation admission | `UNAVAILABLE` |
| 17 | Exact current authoritative transformation relation admits `D2`; all else succeeds | `AUTHORIZED` remains possible |
| 18 | Restore older binding after authoritative revocation/supersession | `DENIED` when current ordering selects the negative event; otherwise `UNAVAILABLE`; never `AUTHORIZED` |
| 19 | Candidate conflict requires ordering; ordering source unavailable | `UNAVAILABLE` |
| 20 | Exact current authoritative binding and every existing condition succeed | `AUTHORIZED` |

Cases 1–20 should be separate JSON fixtures so trace output and expectation mismatches remain inspectable. Cases 7–9 must vary producer identity without changing source-authority facts, proving that labels and origin claims confer nothing.

## Oracle independence

The future oracle must continue to construct and evaluate `OracleInput` without `title`, `objective` prose, `expected_outcome`, or `expected_reason`. Objective prose is descriptive only; `objective_identity` is an atomic oracle input. The runner reads expected outcome only after actual evaluation.

Strict relation parsers must reject `binding_valid`, `source_authoritative`, or equivalent shortcut fields as unknown keys. Candidate disposition is not validity: an `ADMIT` record is merely a candidate until source authority, exact scope, lifecycle, order, continuity, and transformation checks derive admission. A deliberately wrong expected outcome must still yield `CASE_MISMATCH` with an unchanged actual authority outcome.

## Determinism

- Preserve sorted fixture discovery and fixed invariant/fact traversal order.
- Preserve T2 array order and validate each `before -> after` chain.
- Parse candidate sets into immutable records, reject duplicate identities with unequal bodies, and group by exact lineage/order domain.
- Compare non-negative integer generations only inside one established domain; reject type ambiguity and do not parse numeric strings.
- Select only the unique head named or derived by an authoritative ordering relation.
- Apply lifecycle events by the same authoritative order; a later current revocation cannot be erased by JSON ordering.
- Match transformation relations by exact source/target/objective/scope keys.
- Treat absent, unknown, conflicting, incomparable, or malformed authority facts deterministically as input error or `UNAVAILABLE` according to whether syntax or authority establishment failed.
- Use no network, implicit wall clock, randomness, external service, runtime ML, or dictionary insertion order as authority.

## Trust preconditions

Authority Lab admits fixture facts for the accepted root identity, applicable boundary and epoch, authoritative ordering source, policy/objective source, delegation source, and observer results. It can test whether the oracle correctly derives authority from those roots; it cannot prove that a real-world root is legitimate, that the fixture is truthful, or that an observer was uncompromised.

Parser/compiler correctness, JSON integrity, exact identity construction, generation assignment, ordering-source integrity, external clock/order mapping, signature primitives, provenance recorder integrity, and the semantic/normative quality of a root-approved objective mapping remain trust preconditions or model limitations. None is silently treated as evidence that `D` is correct. An admitted authority root can approve a bad mapping; the public contract explicitly stops at that admitted authority boundary.

## Backward compatibility

Evaluate the options as follows:

- A, silently treating every old fixture as missing binding and accepting widespread mismatches, is fail-closed but leaves the maintained suite unusable.
- B, retaining v0 authorization semantics for v0 inputs, would let old inputs bypass the adopted public contract and is rejected for current authority evaluation.
- C, explicitly migrating each maintained fixture with atomic objective/binding/source/lifecycle/ordering facts, preserves each case's original pressure while enforcing the new rule and is recommended.
- D, a compatibility adapter that synthesizes a valid binding, silently grandfathers authority and is rejected. A fail-closed adapter that represents absent binding as unknown is acceptable only for diagnostic loading.
- E, deleting historical fixtures, would lose regressions and is unnecessary.

Therefore migrate all 12 maintained fixtures atomically. Their expected outcomes should remain unchanged only when the added current binding facts independently justify that result. An unmigrated v0 input must never produce `AUTHORIZED` under current semantics; diagnostic compatibility maps its absent admission to `UNAVAILABLE` without inventing a binding.

## Schema versioning

The current version is `authority-lab-v0`. The proposed version is `authority-lab-v1`. A version bump is required because mandatory facts, strict relation shapes, T1 authority-state content, and authorization behavior change.

`load_fixture` should accept v1 for current evaluation. It may accept v0 only through an explicit legacy diagnostic path that injects no facts and therefore yields `UNAVAILABLE` for missing objective admission; it must not preserve v0 `AUTHORIZED`. Unknown versions and structurally malformed records must raise a deterministic input/schema error before authority evaluation. All 12 maintained fixture files migrate to v1 in the same implementation commit, while case IDs may retain their historical source identity because case labels do not drive the oracle.

## Proposed implementation surface

| File | Why it changes | Narrow future change | Surface |
|---|---|---|---|
| `authority_lab/model.py` | v0 has no objective/binding/source/order types | Add strict immutable relation records, v1 parsing, new mandatory facts, and T1/T3 admission references; keep six tuple fields and three outcomes | Data model/parser |
| `authority_lab/oracle.py` | `D` can currently reach success without objective admission | Add deterministic admission phase, source/lifecycle/order/transform checks, mutation continuity, and scoped outcome precedence | Logic |
| `authority_lab/runner.py` | Loader accepts only v0 and trace omits admission | Route v1 and fail-closed v0 diagnostics; render atomic binding facts without reading expected values early | Parser/fixture handling/trace |
| `authority_lab/README.md` | Public usage describes v0 semantics | Document v1 schema, admission behavior, trust boundary, migration, and nonclaims | Documentation |
| `tests/test_authority_lab.py` | Existing tests freeze 16 facts and v0 count/behavior | Preserve regressions; add binding, schema, independence, continuity, conflict, and transformation assertions | Tests |
| `cases/authority_lab/LAB-V0-001.json` through `LAB-V0-012.json` | Maintained cases lack mandatory admission facts | Migrate schema and add explicit atomic objective-binding state without laundering prior outcomes | Fixtures |
| `cases/authority_lab/LAB-V1-013.json` through `LAB-V1-032.json` | Required hostile matrix has no executable cases | Add the 20 cases enumerated above, with U/D/A regression represented among them | New fixtures |

No new Python module, database, policy engine, service, cryptographic system, or runtime dependency is necessary. If implementation makes the oracle unwieldy, private helper functions within `oracle.py` remain narrower than a speculative subsystem.

## Proposed test surface

Retain every current regression: exact tuple and invariant sets, three outcomes, expectation independence, local-only execution, mandatory facts, tuple/value exactness, T1/T2/T3 mutation chains, re-establishment, grant/effect continuity, consumption, delegation, boundary/epoch, closure, and CLI traces.

Add tests in `tests/test_authority_lab.py` for:

- exact v1 typed parsing and rejection of extra/shortcut fields;
- v0 input never authorizing and unknown versions failing deterministically;
- each mandatory binding fact missing, unknown, conflicting, or wrong;
- root and delegate authority, revoked delegate, unauthorized signer/requester/model/verifier;
- objective, contract, policy/schema, scope, boundary, epoch, identity, and generation mismatch;
- T1 admission plus every listed T2 mutation re-evaluated at T3;
- revocation, supersession, rollback, restart, restore, cache, and reordered-event resistance;
- unique ordering, missing order, incomparable forks, admit/reject conflict, and no majority resolution;
- direct `D2` binding, exact transformation admission, and implicit inheritance rejection;
- all PR #15 U/D/A cases and the minimal positive `AUTHORIZED` case;
- wrong expected answers still producing `CASE_MISMATCH`; and
- exact counts of six tuple fields, six invariant identifiers, and three authority outcomes.

Run all migrated and new JSON fixtures through the existing discovery/CLI path, including malformed data in unit-test payloads rather than the passing fixture directory.

## Implementation obligations

- Define exact record key sets and types; reject ambiguity and Boolean verdict shortcuts.
- Keep objective-binding admission before any contract success can contribute to authorization.
- Validate source authority independently from candidate content.
- Preserve denial only for established applicable negative conditions; preserve unavailability for missing evaluation.
- Re-evaluate current binding state at T3 and integrate every authority-relevant T2 mutation.
- Make ordering lineage-scoped, deterministic, and rollback-resistant.
- Require explicit transformation admission.
- Keep expected fixture values out of oracle input and keep all evaluation local and standard-library-only.
- Keep `objective_binding` relational, with no tuple, invariant, or outcome expansion.

## Test/fixture obligations

- Migrate all 12 maintained fixtures without silently granting admission.
- Add all 20 hostile fixtures, including the three PR #15 paths and one reachable positive path.
- Test each atomic omission and mismatch rather than only end-to-end labels.
- Prove negative precedence with exact applicable revocation plus irrelevant missing operational evidence.
- Prove unknown applicability remains `UNAVAILABLE` rather than speculative `DENIED`.
- Prove duplicate assertions, signatures, proofs, provenance, quorum, consensus, and fixture order cannot select a binding.
- Prove cached T1 admission and restored old generations cannot authorize T3.
- Preserve a wrong-expectation mismatch test for every authority outcome.

## Residual model limitations

The lab remains a bounded falsification harness, not an authority source. It cannot establish the ultimate legitimacy, semantic wisdom, morality, legality, or safety of an admitted root's objective-to-contract choice. It does not prove observer truth, parser/compiler correctness, cryptographic soundness, production ordering durability, or external-world execution. The design models exact deterministic facts and relationships; production acquisition and protection of those facts remain outside this slice.

The fixture format can syntactically claim a false root fact. That is not modeled self-authorization when the candidate is evaluated separately from the admitted root relation, but it is an input-trust limitation. A production system must obtain roots and ordering state from an independently protected boundary rather than requester-controlled JSON.

## Residual counterexample search

The strongest near-counterexample is a fixture containing both a malicious `D` and a fabricated fact naming its producer as the authority root. If the oracle accepted the candidate record itself as root evidence, the design would fail. The recommended split blocks that circular path: root membership and any delegation are separate admitted relations, candidate data cannot create them, and exact boundary/epoch/scope/order checks still apply. A dishonest fixture can falsify those admitted relations, but v0 already treats observation truth as a trust precondition; proving external facts is outside the lab's authority objective.

No PR #15-style counterexample survives the proposed semantics: absent or unestablished admission is `UNAVAILABLE`, established applicable rejection is `DENIED`, and only independently admitted exact `D` can proceed. This is a design result, not evidence that unimplemented code is correct. Hostile implementation testing remains required.

## Recommended implementation slice

Implement one v1 vertical slice in a later separately authorized phase:

1. Add strict objective, contract, binding, root/delegation, lifecycle, ordering, and transformation records to `model.py`.
2. Add their v1 parsing and T1/T2/T3 state references without changing `AuthorityTuple`.
3. Add one admission function in `oracle.py` before contract/evidence success, then extend existing mutation and re-establishment checks.
4. Update runner tracing and fail-closed schema routing.
5. Atomically migrate the 12 fixtures and add the 20-case hostile matrix.
6. Extend the single existing test module, preserve no-network determinism, and rerun all old and new regressions.

The slice uses standard-library dataclasses, enums for internal record dispositions only, tuples, mappings, and deterministic comparisons. It requires no new public outcome and no external system.

## Authorization boundary

This artifact authorizes nothing beyond publication of the design itself. It does not adopt another contract revision, implement `objective_binding`, change fixture expectations, authorize runtime use, deploy code, merge a branch, or move a roadmap item. Any implementation, contract interpretation change, migration, deployment, or private-core work requires a separate human-authorized phase and exact-head review.

## Final determination

IMPLEMENTATION DESIGN COMPLETE — OBJECTIVE_BINDING CAN BE ADDED WITHOUT STRUCTURAL EXPANSION
