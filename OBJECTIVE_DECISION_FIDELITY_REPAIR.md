# Ground Truth Objective-to-Decision Fidelity Repair

## Status and scope

This document is a design-review artifact against exact public baseline `e41ee92a6db590d36a651d0ce2acc9d9b7776ce8` (`OBJECTIVE_FIDELITY_BASELINE`). It evaluates the narrowest principled repair for the objective-to-decision-contract fidelity counterexample published through PR #15.

This artifact does not implement or authorize a contract change, test, fixture, workflow, validator, migration, roadmap transition, deployment, publication, or merge. It contains no private-core material. Any adoption remains a separate human authority decision.

The starting tuple remains exactly:

`(subject, artifact, control_state, identity_basis, boundary_epoch, decision)`

The starting invariants remain exactly:

- `INV-CONT`
- `INV-DISC`
- `INV-BND`
- `INV-EVD`
- `INV-USE`
- `INV-CLO`

The starting authority outcomes remain exactly:

- `AUTHORIZED`
- `DENIED`
- `UNAVAILABLE`

The review asks whether the demonstrated gap can be repaired inside that six-coordinate, six-invariant, three-outcome architecture. Analytical symbols introduced here are not tuple coordinates or outcomes.

## Exact counterexample being repaired

Let:

- `O` be the fixed real authority objective;
- `P` be the proposition required by `O`: artifact `A` has been independently reviewed and is currently permitted for release under policy `X`;
- `P'` be the proxy proposition: artifact `A` passes test suite `Y`;
- `D` be the encoded authority decision contract;
- `C` be the exact context in which an objective-to-contract relationship is claimed.

The counterexample gives the frozen evaluator an applicable `D` that incorrectly substitutes `P'` for `P`. At T3, exact tuple coordinates, boundary relations, provenance, freshness, verifier execution, grant/effect relations, consumption eligibility, and every fact required by encoded `D` are established. `D(P')` returns `AUTHORIZED`.

Under unchanged `O`, however:

- in the primary trace, `P` is required but unavailable, so the objective requires `UNAVAILABLE`; or
- in the stronger trace, `not P` is established, so the objective requires `DENIED`.

The defect is not weak evidence being relabeled inside a correct decision contract. It is complete and correct evaluation of the wrong decision contract. A sound repair must make `D` inadmissible unless the relationship from `O` to `D` is itself current and authoritative.

## Repair objective

The repair must enforce this property:

> An encoded authority decision contract may participate in `AUTHORIZED` only when an exact current authoritative relationship establishes that the contract is an admitted realization of the applicable authority objective for the same T3 context.

This property does not require Ground Truth to derive semantic truth from first principles. It requires the authority system to identify and bind the authority-bearing source that accepts responsibility for the objective-to-contract mapping.

The repair must preserve a positive path: proxy evidence remains usable when an authoritative current objective binding expressly admits it as sufficient for the exact objective, contract, context, and boundary epoch.

## Constraints

A viable repair must:

1. close both PR #15 traces;
2. preserve `DENIED` versus `UNAVAILABLE`;
3. preserve a practical `AUTHORIZED` path;
4. prevent `D`, its verifier, its evidence, its requester, and its formalizer from authorizing their own mapping;
5. avoid a universal semantic oracle or infinite regress claim;
6. remain current through T3;
7. bind exact objective, contract, context, identity basis, authority source, and boundary epoch;
8. fail closed under absence, conflict, staleness, substitution, replay, revocation, or transformation;
9. distinguish identity and provenance of a mapping from authoritative acceptance of its fidelity;
10. preserve exactly six tuple coordinates, six invariants, and three outcomes if the architecture can express the repair without evasion.

## Candidate A — INV-EVD strengthening

Candidate A would add an objective-fidelity clause directly to `INV-EVD`:

> Evidence may satisfy a decision only when the applicable decision contract is itself established as an authoritative faithful realization of the applicable authority objective for the exact current authority context.

This closes the counterexample only if “established” refers to an authority-bearing relationship external to `D`. If `D` can declare itself faithful, the wording is circular. If verifier success establishes fidelity, the candidate repeats the original error. If “faithful” means objectively true under an unspecified universal semantic oracle, the candidate is not implementable in principle.

`INV-EVD` is relevant because evidence admission must not proceed through an inadmissible `D`. It is not sufficient by itself because the new fact concerns contract applicability and authority lineage, not merely the strength of evidence evaluated within the contract.

Consequences:

- unknown objective fidelity must make required evaluation unavailable;
- explicit authoritative invalidity, revocation, or prohibition must prevent authorization and may yield `DENIED` when applicability is established;
- exact current authoritative fidelity preserves the positive path;
- context-sensitive fidelity must remain current through T3;
- transformed decision contracts cannot inherit fidelity without an explicit closure rule.

Classification: contract repair requirement when paired with an explicit binding relation; otherwise residual counterexample or model limitation.

## Candidate B — existing tuple-state encoding

Candidate B places objective identity, policy version, contract version, semantic-map version, compiler/schema identity, and approval generation inside existing `control_state` and `identity_basis` representations.

This is useful but insufficient alone. Exact identity can establish which mapping was used; it cannot establish that the mapping was accepted by the applicable authority or is semantically adequate for `O`. An exactly identified incorrect mapping reproduces PR #15.

Existing tuple coordinates can carry the authority-relevant identities and versions needed to discriminate the binding. They need not gain a seventh coordinate. The validity of the relationship must still arrive as a separately established authority-relevant fact.

Benefits:

- policy, contract, compiler, schema, and mapping changes become visible control-state changes;
- `INV-CONT` naturally requires re-establishment at T3;
- `INV-DISC` rejects aliases as proof of identity;
- boundary-epoch changes fence stale approvals.

Limitations:

- hashes, names, and versions prove identity, not fidelity;
- provenance proves lineage, not correctness;
- exact state cannot make a self-attested mapping authoritative.

Classification: implementation obligation supporting the repair; not a complete contract repair.

## Candidate C — explicit objective binding

Candidate C requires an explicit authority-bearing relational fact, written analytically as:

`objective_binding(O, D, C, identity_basis, boundary_epoch, authority_source, version, status)`

This notation is not a tuple coordinate. It is a required external relationship of the same general architectural kind as boundary-to-epoch, evidence-to-artifact, delegation, grant/effect, and consumption relations already required at T3.

The relationship means that an applicable authority source has accepted `D` as an authorized realization of `O` for exactly the identified scope. It does not mean that Ground Truth independently proved the natural-language semantics correct.

Admissibility rules:

1. `O` and `D` identities must be exact, not names or selectors alone.
2. Scope `C` must cover the exact subject, artifact class or artifact, relevant control state, decision, identity basis, and boundary epoch.
3. The establishing source must be the applicable authority boundary or an explicitly authorized delegate whose delegation is exact and current.
4. `D`, the requester, the verifier, the evidence producer, a compiler, a model, or an agent cannot establish its own binding merely by assertion or agreement.
5. The binding must have durable provenance, authoritative ordering, version, lineage, and current status.
6. Any objective, contract, schema, formalizer, authority-source, context, or boundary change outside the binding scope requires re-establishment.
7. Revocation or supersession must dominate older positive bindings according to authoritative ordering.
8. A derived, wrapped, translated, compiled, or otherwise transformed `D2` does not inherit the binding of `D` without an explicit authority-preserving closure relation.

Outcome derivation:

- if the required binding is missing, conflicting, stale, or cannot be established at T3, required authority-relevant evaluation is incomplete and yields `UNAVAILABLE`;
- if the applicable binding is established as invalid, revoked, superseded, out of scope, or prohibited, the established condition prevents the transition and yields `DENIED`;
- if the exact current authoritative binding is established and every other applicable requirement succeeds, `AUTHORIZED` remains possible.

These results use the existing outcome meanings. They are not a fourth outcome and are not hard-coded from semantic difference alone.

Candidate C closes PR #15 because the incorrect `D(P')` lacks an authoritative current binding to `O(P)`. Correct execution of `D` cannot replace the missing relationship.

Classification: recommended contract repair requirement; implementation obligation; test requirement; trust precondition at the admitted authority root.

## Candidate D — authority-bearing formalization

Candidate D treats creation or adoption of `D` from `O` as an authority-bearing transition. The formalization output is evidence until an applicable authority act admits it through an objective binding.

Compiler identity is necessary for reproducibility but insufficient for fidelity. A proof of equivalence can be evidence for the mapping, but proof validity covers the encoded theorem and trusted translation chain; it does not authorize itself. Human approval can be authoritative only when the human role, act, scope, objective, contract, and boundary are all within the applicable authority contract.

Probabilistic or ML formalizers may propose `D` and produce evidence. Their confidence, agreement, or performance cannot create authority. A separately authorized source must admit the result. Each policy, compiler, schema, or material formalization revision requires a binding whose scope covers that revision.

Existing `INV-CLO` can prevent authority from flowing implicitly from `O` to transformed `D`; `INV-BND` constrains who may authorize the transformation; `INV-CONT` and `INV-USE` require its continuing validity.

Candidate D is a sound production pattern when it produces Candidate C’s binding. Without that binding, merely labeling compilation “authority-bearing” does not specify an enforceable T3 fact.

Classification: implementation architecture and authority workflow; viable support for Candidate C; not the narrowest independent repair.

## Candidate E — independent witness

Candidate E requires one or more witnesses to assert that `D` is faithful to `O`.

Independence can improve evidence quality, but witness count is not semantic fidelity. Two models trained on the same data, two agents using the same formalizer, two reviewers relying on the same mistaken source, or unanimous agreement can reproduce one error. Consensus is not evidence of independence.

A witness statement is evidence. It becomes relevant only through an authority rule that identifies the proposition witnessed, the witness role, source lineage, scope, independence requirements where applicable, and the authority source that admits the result. A witness cannot authorize itself.

Candidate E therefore cannot replace objective binding. It can supply evidence to the authority source that establishes Candidate C. Shared provenance and correlated derivation must remain visible, and repetition cannot strengthen semantics by itself.

Classification: optional evidence mechanism; trust precondition and test requirement; residual counterexample if treated as authority by count alone.

## Candidate F — explicit trust/model boundary

Candidate F states that objective-to-contract fidelity is external and `AUTHORIZED` is valid only relative to an externally established applicable binding.

The boundary is principled: no finite authority system can prove natural-language meaning, normative correctness, or semantic truth from first principles. Some trusted authority root must define or accept the objective and its operational realization.

Scope language alone does not close PR #15. If the evaluator can still accept `D(P')` with no required current binding fact, the same trace remains reproducible and has merely been renamed out of scope. Candidate F becomes a repair only when the external trust act is represented inside the decision process as Candidate C’s required relational fact.

The remaining trust claim is narrow: the admitted authority source is trusted to accept the mapping. Ground Truth establishes the identity, scope, lineage, freshness, applicability, and status of that act; it does not prove the source made a semantically correct or wise decision.

Classification: necessary trust/model boundary; insufficient alone; sound when paired with Candidate C.

## Comparative matrix

| # / criterion | A: strengthen EVD | B: tuple state | C: objective binding | D: formalization authority | E: witness | F: trust boundary |
|---|---|---|---|---|---|---|
| 1. Closes PR #15 | only with C | no | yes | only through C | no | only with C |
| 2. Preserves positive path | yes | yes | yes | yes | yes | yes |
| 3. Preserves outcome distinction | if specified | neutral | yes | through C | neutral | through C |
| 4. Prevents `D` self-authorization | only with C | no | yes | if external | no | only with C |
| 5. Prevents evidence self-authorization | only with C | no | yes | if external | no | only with C |
| 6. Verifier success is not fidelity | stated | neutral | enforced | stated | not enforced | stated |
| 7. Avoids universal semantic oracle | if authority-relative | yes | yes | yes | yes | yes |
| 8. Survives T1/T2/T3 change | with `INV-CONT` | helps | yes | through C | no | only with C |
| 9. Survives policy/version drift | with exact scope | identifies | yes | through C | no | only with C |
| 10. Survives objective substitution | only with C | identifies | yes | through C | no | only with C |
| 11. Survives contract substitution | only with C | identifies | yes | through C | no | only with C |
| 12. Rejects requester interpretation | only with C | no | yes | if external | no | only with C |
| 13. Survives replay | only with current binding | helps | yes | through C | no | only with C |
| 14. Survives revocation | with status relation | helps | yes | through C | no | only with C |
| 15. Blocks derived-contract reuse | with `INV-CLO` | identifies | yes | yes through C | no | only with C |
| 16. Preserves fail-closed behavior | with concrete relation | neutral | yes | through C | no | through C |
| 17. Fits six-coordinate tuple | yes | yes | yes | yes | yes | yes |
| 18. Fits six invariants | with clarification | yes | yes | yes | yes | yes |
| 19. Avoids circularity | only with C | no | yes | if external | no | only with C |
| 20. Makes trust explicit | partly | no | yes | partly | no | yes |
| 21. Avoids private-core disclosure | yes | yes | yes | yes | yes | yes |
| 22. Implementable in principle | with C | yes | yes | yes | yes | yes |
| 23. Rejects consensus-as-authority | neutral | neutral | yes | yes | no alone | neutral |
| 24. Provenance is not correctness | stated | no | enforced | stated | ambiguous | stated |
| 25. Identity is not fidelity | stated | no | enforced | stated | ambiguous | stated |

Across the full criteria, Candidate C is the only independently complete repair. A supplies its evidence-admission hook; B supplies exact state and identity; D supplies a disciplined way to create a proposed binding; E may supply evidence; and F states the bounded trust root.

## Flagship repair trace

### T1

The real objective `O` requires `P`. Encoded `D` requires only `P'`. Identities for `O`, `D`, policy, schema, compiler, context, and boundary epoch are exact. Evidence for `P'` is valid. `P` is unavailable.

The evaluator requests the exact current `objective_binding(O, D, C, ...)` as a prerequisite to admitting `D`.

- If no such authoritative binding can be established, `D` is not admissible. Required evaluation is incomplete, so the result is `UNAVAILABLE`.
- If an applicable authority has established the binding invalid or prohibited, the result is `DENIED`.
- The fact that `D(P')` would return `AUTHORIZED` is irrelevant because an inadmissible `D` cannot supply authority.

### T2

T2 creates no authority. Changes to the objective, contract, policy source, formalizer, compiler, schema, reviewer role, context, or boundary may invalidate the binding’s scope. Preparation, cached labels, signatures, proof results, or unanimous agents do not preserve authority.

### T3

The system re-establishes the exact live binding and every other required relationship.

- missing, stale, conflicting, or unobservable binding yields `UNAVAILABLE`;
- established revocation, supersession, invalidity, scope failure, or prohibition yields `DENIED`;
- exact current valid binding permits `D` to be evaluated, after which `AUTHORIZED` remains possible only if all other frozen requirements succeed.

Thus the repair closes both PR #15 traces without defining `P`, `P'`, `O`, `D`, or `C` as new tuple coordinates.

## Positive AUTHORIZED trace

Objective `O` requires `P`. Contract `D` encodes `P` directly, or an applicable authority expressly accepts evidence proposition `P'` as sufficient for `P` within exact context `C`.

At T3 the system establishes:

- exact objective and decision-contract identities;
- exact current objective binding;
- authority source and any delegation;
- binding provenance and authoritative ordering;
- policy, schema, compiler, and mapping versions where applicable;
- subject, artifact, control state, identity basis, boundary epoch, and decision;
- evidence semantics, provenance, freshness, and applicability;
- grant/effect, closure, consumption eligibility, and continuity;
- no applicable prohibition.

The binding status is valid and current. `D` succeeds. `AUTHORIZED` remains possible. The repair does not make proxy evidence permanently unusable and does not require a universal proof of meaning.

## T1/T2/T3 continuity

Objective fidelity is not a one-time publication property. Its validity conditions must remain established through T3.

An objective version change can alter what `D` must represent. A contract, schema, compiler, or formalizer change can alter what is evaluated. An environment change can invalidate a context-bounded mapping. A reviewer-role or authority-boundary change can invalidate who was permitted to establish the binding.

`INV-CONT` requires the live relationship to match the verified relationship. `INV-DISC` requires exact identities rather than stable aliases. `INV-BND` binds the establishing authority and epoch. `INV-USE` prevents a last-known-good binding from surviving invalidation. No new temporal invariant is required.

## Revocation and supersession

An objective binding is revocable and supersedable authority state, not immutable evidence of eternal permission.

The implementation must preserve authoritative ordering, monotonic invalidation where applicable, durable lineage, and conflict visibility. Absence of a locally observed revocation is not proof of current validity. Cached, restored, replicated, delegated, or transferred bindings cannot outrank a current authoritative revocation.

If current status cannot be established, the binding is unavailable. If a current applicable revocation or prohibition is established, the transition is denied. A new positive binding must be distinct, lineage-linked, and scoped to the current objective, contract, context, and epoch.

Emergency override is a distinct authority act. It must be expressly permitted, scoped, bound, ordered, and consumed; urgency cannot create an implicit objective binding.

## Transformation and closure

Compilation, translation, optimization, wrapping, schema migration, partial evaluation, composition, and derivation can change contract semantics even when a tool reports success.

`INV-CLO` must apply to objective bindings: approval of `D` does not automatically authorize `D2`. A transformation may preserve authority only when an explicit current closure relation identifies the source and target contracts, transformation, versions, scope, authority source, and boundary epoch.

A formal equivalence proof is evidence for the proposition it actually proves. A signature authenticates covered bytes and signer identity under stated assumptions. Neither automatically proves fidelity to the correct source objective or creates the authority-preserving closure rule.

Cross-domain transfer and delegation require their own exact authority relationships. A source-domain binding does not silently become a target-domain binding.

## Trust preconditions

The repair does not prove:

- that the authority objective is wise, safe, complete, moral, or correctly expressed;
- natural-language meaning or formalization fidelity from first principles;
- integrity or competence of the admitted human or institutional authority source;
- correctness of semantic schemas, parsers, compilers, formalizers, solvers, or runtimes;
- correctness of cryptographic primitives, key custody, clocks, or authoritative ordering sources;
- completeness of observers, sensors, provenance recorders, or revocation channels;
- independence merely from witness count or agreement;
- universal equivalence across languages, ontologies, domains, or time.

These are explicit trust preconditions or model limitations. The repair establishes which authority accepted which mapping, under which exact scope and current state. It does not convert that acceptance into proof of semantic truth.

## Implementation obligations

Without authorizing implementation, a conforming realization would need to:

- represent exact objective, contract, binding, authority-source, version, and context identities;
- record an authority-bearing objective-binding act distinct from evidence and verifier output;
- require that binding before admitting `D` at T1 and T3;
- prevent self-attestation by `D`, requesters, agents, verifiers, formalizers, and evidence producers;
- bind the relationship to exact tuple state and boundary epoch without adding a tuple coordinate;
- retain durable provenance, authoritative ordering, revocation, supersession, and lineage;
- re-establish current applicability at T3;
- expose missing or conflicting state as unavailable rather than guessing;
- enforce explicit closure for transformed contracts;
- preserve the existing outcome distinction and positive path;
- keep diagnostic detail from becoming an unintended authority or side channel where applicable.

## Test requirements

Future tests, subject to separate authority, should include:

- the exact PR #15 primary trace with `P` unavailable and `D(P')` otherwise passing;
- the stronger trace with `not P` established and omitted by `D`;
- exact valid binding positive control;
- missing, conflicting, stale, revoked, and superseded bindings;
- objective replacement after T1;
- contract replacement after T1;
- identical contract bytes under a different objective or policy;
- objective, policy, schema, and contract alias collisions;
- compiler, formalizer, and reviewer-role changes;
- requester-supplied and self-attested mappings;
- model-generated and unanimous correlated mappings;
- transformed, wrapped, delegated, transferred, and cross-domain contracts;
- cached binding, rollback, replica lag, partial observation, and unknown current policy;
- conflicting objective sources and conflicting approved mappings;
- emergency override without explicit authority;
- signatures over semantically wrong contracts;
- formal equivalence proofs relative to the wrong source proposition.

Expected outcomes must be derived from exact current facts, not assigned by attack name.

## Residual model limitations

Even with the repair, an authorized objective source can approve a bad mapping. If the applicable boundary itself is compromised, incompetent, deceptive, or normatively wrong, the authority model may faithfully represent bad authority. Ground Truth does not establish correctness beyond its admitted trust root.

The design also cannot guarantee that natural-language objectives have unique meanings or that a finite formal contract is complete. It can require explicit responsibility, exact scope, current applicability, and fail-closed handling of missing authority. It cannot manufacture an oracle for objective truth.

These limitations do not reopen PR #15: that trace lacks the required authoritative relationship entirely. A forged or compromised binding is a different trust-boundary or cryptographic attack. A legitimately authoritative but unwise binding is a policy-quality limitation, not the same omitted-binding counterexample.

## Residual counterexample search

The recommended repair was attacked with the mandatory hostile cases:

- A malicious or accidentally incorrect `D` is inadmissible without an external authoritative binding.
- A stale approved mapping fails T3 continuity.
- Revocation and supersession defeat earlier positive bindings under authoritative ordering.
- Objective, contract, policy, schema, compiler, formalizer, reviewer, context, or boundary substitution falls outside the exact binding or requires re-establishment.
- Identical `D` bytes cannot replay across a different objective or policy because both identities and scope are bound.
- Alias collisions do not establish identity under `INV-DISC`.
- Requester-supplied, self-attested, model-generated, or unanimous mappings remain evidence without authority.
- Correlated witnesses do not become independent through count or presentation.
- Derived and wrapped contracts lack closure unless an exact authority-preserving transformation is established.
- Cached or rolled-back bindings cannot establish current status.
- Partial observation, unknown policy, and conflicting sources yield unavailable evaluation.
- Cross-domain transfer and delegation require exact separate relations.
- Boundary-epoch change fences the prior binding.
- Human verbal approval without durable binding cannot satisfy the T3 relation.
- A signature on a semantically wrong `D` proves authenticity, not fidelity.
- A proof relative to the wrong source proposition does not bind `D` to the real objective.

No residual reproduction of the PR #15 counterexample survives when the exact current authoritative objective binding is treated as a mandatory T3 relational fact. A different case can still challenge the trustworthiness or completeness of the admitted authority root, but that does not show the repaired contract authorizing without its newly required relation.

No narrower candidate closes the gap. Identity-only encoding leaves fidelity unestablished; an `INV-EVD` sentence without a concrete relation is circular; witnesses supply evidence rather than authority; and scope language alone merely moves the defect outside the model.

## Recommended narrow repair

Adopt Candidate C, supported by narrow clarifications to the existing invariants and an explicit trust boundary.

Exact semantic rule:

> Before an encoded decision contract may participate in an authority decision, an exact current authoritative objective binding must establish that the contract is an admitted realization of the applicable authority objective for the same decision context. The contract, requester, verifier, evidence producer, and formalizer cannot establish that binding merely through their own assertion, execution, output, or agreement. Missing or conflicting required binding yields `UNAVAILABLE`; established applicable invalidity, revocation, supersession, scope failure, or prohibition yields `DENIED`; exact current valid binding makes the contract admissible but does not itself guarantee `AUTHORIZED`.

Invariant impact:

- clarify `INV-EVD` so evidence cannot satisfy or activate a decision through a contract whose objective binding is unestablished;
- apply `INV-CONT` to the binding’s validity conditions through T3;
- apply `INV-DISC` to objective, contract, mapping, schema, and policy identities;
- apply `INV-BND` to the source and epoch of the authority-bearing binding;
- apply `INV-USE` to revocation, supersession, and continuing eligibility;
- apply `INV-CLO` to transformed or derived decision contracts.

This is a semantic tightening of the existing six-invariant architecture, not a seventh invariant. The tuple remains six coordinates. The outcomes remain three. `objective_binding` is a required relational fact, not a tuple coordinate.

Who may establish it: the applicable authority boundary or an exact currently authorized delegate acting within scope. Humans, institutional policy processes, or formally governed mechanisms may serve in that role only when the existing authority contract establishes their identity, role, act, scope, and delegation. Verifiers, models, agents, proofs, signatures, and witnesses may supply evidence but do not authorize themselves.

At T1 the binding gates admission of `D`. At T2 no authority is created and relevant changes invalidate or supersede the verified relation. At T3 the binding and all other required facts are re-established. Revocation and supersession follow authoritative ordering and fail closed.

Remaining trust assumption: the admitted authority root is trusted to define or accept the objective-to-contract relationship. Ground Truth proves neither semantic truth nor normative quality beyond that boundary.

## Frozen-contract impact

The recommended design changes contract semantics by making objective binding an explicit required T3 relational fact and by clarifying the reach of the existing invariants. Adoption would therefore require a separate authorized contract revision and corresponding implementation and tests.

It does not require:

- a seventh tuple coordinate;
- a seventh invariant;
- a fourth authority outcome;
- a universal semantic oracle;
- consensus as authority;
- objective binding to become evidence that authorizes itself.

Until separately adopted, the public contract at `OBJECTIVE_FIDELITY_BASELINE` remains unchanged.

## Final determination

**NARROW REPAIR FOUND WITHIN EXISTING SIX-INVARIANT ARCHITECTURE**

An explicit current authoritative objective-to-decision-contract binding, enforced as a mandatory T3 relational fact through the existing invariants, closes the PR #15 counterexample while preserving the positive authorization path and the existing `AUTHORIZED`, `DENIED`, and `UNAVAILABLE` distinction.

This determination is design evidence only. It is not implementation authority, proof of semantic truth, certification, roadmap authority, publication authority, or merge authority.
