# Ground Truth Objective Binding — Contract Adoption Design

## Status and scope

This document designs the narrow public-contract revision needed to adopt the reviewed `objective_binding` recommendation. It is design evidence only. It does not itself revise the public contract, authorize implementation, change tests or fixtures, move a roadmap, authorize deployment, or disclose private-core material. A later human-authorized contract-revision phase remains required.

The frozen authority tuple remains exactly:

`(subject, artifact, control_state, identity_basis, boundary_epoch, decision)`

It has exactly six coordinates. The invariant set remains exactly:

- `INV-CONT`
- `INV-DISC`
- `INV-BND`
- `INV-EVD`
- `INV-USE`
- `INV-CLO`

The authority outcomes remain exactly:

- `AUTHORIZED`
- `DENIED`
- `UNAVAILABLE`

`objective_binding` is an authority-relevant relationship required to admit a decision contract. It is not a tuple coordinate, invariant, outcome, grant, or item of operational evidence.

## Exact baseline

`OBJECTIVE_BINDING_ADOPTION_BASELINE=2d58df8da4ba15a7c261e78dfadfe307280c82c6`

The baseline is the human-merged result of PR #16. At this baseline:

- the public repository is `groundtruthexhibit-beep/ground-truth-exhibit`;
- the public branch is `main`;
- the PR #15 artifact `FRONTIER_DELTA_SEMANTIC_EVIDENCE_BINDING.md` is present;
- the PR #16 artifact `OBJECTIVE_DECISION_FIDELITY_REPAIR.md` is present;
- public tests pass 73/73;
- Authority Lab fixtures pass 12/12; and
- the baseline worktree is clean.

This artifact does not infer authority from either merged research document. Their review results are inputs to this adoption design, not contract adoption.

## Counterexample lineage

The PR #15 frontier distinguishes:

- `O`: the real authority objective;
- `P`: a proposition required by `O` before an exact T3 effect;
- `D`: the encoded authority decision contract; and
- `P'`: the proposition actually required and evaluated by `D`.

In the counterexample, `O` requires independent review and current release permission (`P`), while `D` requires only a passing test result (`P'`). Every frozen fact encoded by `D` is established and `D(P')` returns `AUTHORIZED`. Yet `P` is unavailable in the primary trace and explicitly false in the stronger trace. The objective therefore requires no T3 crossing even though the encoded contract authorizes it.

This is objective-to-decision-contract infidelity, not merely weak operational evidence inside a faithful contract. The existing evaluator can completely and correctly evaluate the wrong `D`.

## Reviewed repair recommendation

PR #16 recommends one mandatory relation:

> Before an encoded decision contract may participate in an authority decision, an exact current authoritative `objective_binding` must establish that the contract is an admitted realization of the applicable authority objective for the same decision context.

The reviewed result was:

`PASS — explicit authoritative objective binding closes the PR #15 counterexample within the existing six-invariant architecture`

and:

`NO REPRODUCIBLE PR #15 COUNTEREXAMPLE SURVIVES THE RECOMMENDED REPAIR`

This design determines how that recommendation could be adopted without changing tuple arity, invariant count, or outcome count.

## Adoption objective

The public contract must answer, before evaluating an encoded decision contract `D`:

> When is this exact `D` admissible as the authority-bearing decision semantics for this exact T3 effect?

The narrow adopted rule is:

> An exact encoded decision contract is admissible only when an explicit, current, authoritative `objective_binding` establishes that the exact applicable authority objective admits that exact contract for the exact relevant scope and current authority context.

This rule gates admission of `D`; it does not make a successful binding sufficient for `AUTHORIZED`. After admission, `D` must still evaluate its operational facts, and every other frozen T3 requirement must succeed.

## Objective-binding semantic model

For design analysis, write:

`objective_binding = B(O, D, S, A, Q, C, I, G, R, L, V, X, K)`

where the symbols denote, semantically:

- `O`: exact authority-objective identity and version;
- `D`: exact decision-contract identity and version;
- `S`: subject scope;
- `A`: artifact scope;
- `Q`: decision and authority-consuming effect scope;
- `C`: control-state scope;
- `I`: identity-basis scope;
- `G`: boundary epoch or authority-generation scope;
- `R`: issuing authority and any exact delegation relation;
- `L`: lineage and provenance of the authority act;
- `V`: validity interval and currentness conditions;
- `X`: revocation and supersession status; and
- `K`: transformation, derivation, and inheritance restrictions.

These symbols are analytical dimensions of one relationship. They are not new tuple coordinates and do not mandate one storage field per item. A conforming representation may normalize, reference, derive, or cryptographically cover them differently, but it must establish the same semantics without ambiguity.

The relationship states which admitted authority accepted which exact objective-to-contract mapping, for what exact use, under what live lineage and limitations. It does not state that the objective is morally ideal or that `D` is universally semantically true.

## Authority source requirements

An `objective_binding` may be established only by the applicable authority boundary or an exact currently authorized delegate acting within an established scope. The authority source must be independent of the requester's mere selection and must itself be established under the existing authority lineage and boundary rules.

Possible mechanisms include:

- a human policy authority whose role and act are currently authoritative;
- an organization policy authority acting through an admitted governance process;
- a signed policy registry whose signer, registry role, scope, ordering, and current authority are established;
- a delegated authority whose delegation is exact, current, in scope, and not revoked;
- a policy approval process whose result is authority-bearing under the applicable authority root; or
- a formally governed automated mechanism already admitted to issue that binding.

A formal verification process, compiler, formalizer, external reviewer, quorum, or AI model may contribute evidence. It may establish the binding only if a separate applicable authority rule already makes its exact act authority-bearing. Mechanism type never creates authority by itself.

The following are insufficient by themselves:

- `D` asserting that `D` is faithful;
- the generator of `D` asserting fidelity;
- verifier or test-suite `PASS`;
- a requester-uploaded mapping;
- a cryptographic signature from a signer not authoritative for this act;
- vote count, quorum, model diversity, or validator agreement;
- valid provenance or immutable storage; and
- strong identity without the authority-bearing relationship.

Thus `D` cannot authorize itself, evidence cannot authorize `D`, and a favorable interpreter cannot become applicable merely because the requester selected it.

## INV-EVD adoption semantics

Recommended replacement wording:

> **INV-EVD — exact evidence and objective binding; non-promotion.** Evidence is bound to the exact tuple and decision for which it was admitted. Evidence may satisfy an applicable authority decision only when (1) it satisfies the exact admitted decision contract and (2) an exact current authoritative `objective_binding` admits that exact decision contract as a realization of the applicable authority objective for the same decision context. Evidence is not authority and cannot establish the required `objective_binding` merely through assertion, provenance, signature, execution, repetition, aggregation, transformation, or consensus. Missing required evidence binding, objective binding, or evaluation yields `UNAVAILABLE`.

This wording avoids circularity by locating authority for the mapping outside `D` and its operational evidence. The binding is authority metadata: it makes `D` admissible. It is not evidence that the operational proposition required by `D` holds. Conversely, valid evidence for `P'` cannot repair a missing objective binding.

## INV-CONT adoption semantics

Recommended addition to `INV-CONT`:

> The exact live `objective_binding`, including its objective, contract, scope, authority source, lineage, validity, and status conditions, must remain continuous or be re-established through T3. A T1 binding does not survive a relevant change merely because its record or label remains available.

At T2, a change to the objective version, policy authority, `D` version, binding generation, revocation state, scope, authority root, boundary epoch, identity basis, or other defined validity condition invalidates cached continuity. At T3, unknown continuity yields `UNAVAILABLE`; an established applicable invalidation or prohibition yields `DENIED`.

## INV-DISC adoption semantics

Recommended addition to `INV-DISC`:

> Objective, decision-contract, binding, policy, schema, authority-source, and relevant transformation identities and versions must be established under the applicable identity basis. Stable names, selectors, labels, paths, tags, wrappers, schema similarity, or byte equality do not establish objective identity, contract fidelity, or binding identity.

Two contracts with the same label are not thereby the same contract. The same `D` bytes under different authority objectives are distinct binding contexts. Similar objective names across generations do not establish continuity. Exact identity is necessary but does not itself prove fidelity.

## INV-BND adoption semantics

Recommended addition to `INV-BND`:

> The source of an `objective_binding` and any delegation must be established within the applicable independent authority boundary and current authority lineage. A binding has no implicit authority across organizations, tenants, environments, domains, authority roots, or boundary epochs.

A sandbox approval does not authorize production. One organization cannot approve for another without an exact cross-boundary authority relation. The requester cannot route to a favorable signer, registry, verifier, or semantic interpreter. Boundary or authority-root rotation requires an exact currently authorized continuity, migration, or replacement relation.

## INV-USE adoption semantics

Recommended addition to `INV-USE`:

> An `objective_binding` is usable only while its exact current validity, scope, authority generation, delegation, revocation, supersession, and any consumption conditions remain established for the requested T3 effect. Cached, expired, revoked, superseded, consumed, wrong-scope, or wrong-generation bindings do not remain last-known-good authority.

Unknown current status yields `UNAVAILABLE`. Established expiry, revocation, supersession, scope failure, or prohibition yields `DENIED` when the applicable boundary and exact context are evaluable.

## INV-CLO adoption semantics

Recommended addition to `INV-CLO`:

> An `objective_binding` for `D` does not implicitly admit a transformed, wrapped, compiled, optimized, summarized, translated, migrated, composed, or derived contract `D2`. `D2` requires its own exact current authoritative binding unless an exact current authoritative closure relation expressly admits the identified transformation from `D` to `D2` for the same objective and exact scope.

Tool success, semantic-equivalence evidence, equal outputs, a shared source, or a signature over `D2` does not create that closure. The closure relation must itself identify the source and target contracts, transformation and versions, objective, scope, authority source, boundary lineage, validity, and revocation status.

## Outcome derivation

The adopted relation uses the existing outcomes:

| Established T3 facts | Derived outcome |
| --- | --- |
| A required binding, authority source, lineage, currentness, authoritative ordering, or scope relation cannot be established; or conflicting bindings cannot be ordered | `UNAVAILABLE` because admission of `D` cannot be established |
| The applicable boundary and exact context are established, and a current authoritative fact establishes invalidity, revocation, supersession, rejection, scope failure, or prohibition | `DENIED` because an established applicable condition prevents use of `D` or the transition |
| The exact current authoritative binding admits `D`, `D`'s operational requirements succeed, and every other frozen T3 requirement succeeds | `AUTHORIZED` remains possible for that exact effect |

The contract does not map every difference or context change to one hard-coded result. It asks whether required current facts are unavailable or whether an applicable failure or prohibition is established.

## PR #15 regression trace

Let the fixed objective `O` require `P`, while incorrect encoded `D` requires only `P'`. Evidence for `P'` is authentic, fresh, provenance-exact, correctly evaluated, and bound to the exact frozen tuple. There is no replay, stale operational state, grant reuse, consumption ambiguity, or encoded prohibition.

### Case U — binding unavailable

No current authoritative `objective_binding` admits `D` as a realization of `O`. `P` remains unestablished. Although `D(P')` would return `AUTHORIZED`, `INV-EVD` does not admit `D`; required T3 evaluation is incomplete. The frozen result is `UNAVAILABLE`, and T3 cannot be crossed.

### Case D — binding rejected

The applicable current authority explicitly rejects or revokes the mapping from `O` to `D`. The boundary, exact context, and authoritative ordering are established. The rejected mapping is not uncertainty; it is an established applicable failure. The frozen result is `DENIED`, and T3 cannot be crossed.

### Case A — binding established

The applicable current authority explicitly admits exact `D` for exact `O` and the exact scope. `D`'s operational requirements succeed and every other T3 relationship remains established. `AUTHORIZED` remains possible.

The original attack no longer succeeds because a complete evaluation of `D(P')` is downstream of contract admission. An unbound or rejected `D` cannot supply authority, even when it executes correctly.

## Positive AUTHORIZED path

A legitimate policy authority `R1`, established within boundary lineage `G1`, adopts objective `O1`. `R1` approves exact contract `D1` for exact subject, artifact, decision/effect, control-state, identity-basis, and boundary-epoch scopes. The resulting binding `B1` has established lineage and currentness and is neither revoked nor superseded.

`D1` requires operational evidence `E1`. At T3:

- the exact six-coordinate tuple is established;
- the applicable independent boundary and authority source are established;
- `B1` exactly and currently admits `D1` for `O1` and this scope;
- any delegation and transformation relations are exact and current;
- `E1` satisfies `D1` without promotion;
- grant/effect and consumption eligibility are exact;
- continuity through T3 is established; and
- no applicable prohibition is established.

The result may be `AUTHORIZED` for the exact requested effect. The binding admits `D1`; it neither replaces `E1` nor authorizes a different effect. Adoption therefore does not collapse the model into permanent `UNAVAILABLE`.

## Revocation and supersession

An objective binding is revocable and supersedable authority state. It is not an immutable certificate of eternal permission.

Current status must be established from an authoritative ordering source within the applicable boundary lineage. A later authoritative revocation, rejection, scope reduction, authority rotation, or superseding binding defeats earlier positive state. Restoration, rollback, cached records, replica lag, offline operation, or absence of a locally observed revocation does not prove current validity.

If current ordering or status cannot be established, the outcome is `UNAVAILABLE`. If a current applicable revocation, rejection, invalidity, or prohibition is established, the outcome is `DENIED`. A replacement positive binding must be separately identifiable, lineage-linked, current, and exactly scoped.

A cryptographically valid signature may remain authentic after the signer loses authority. Authenticity of the old act does not make it currently usable.

## Transformation closure

No compilation or representation change is presumed semantic- or authority-preserving. For `D -> D2`, the contract requires either:

1. a new exact current authoritative `objective_binding` from the applicable objective to `D2`; or
2. an exact current authoritative closure relation that expressly admits this identified transformation, source, target, versions, scope, and boundary lineage.

The second option is not a generic transitive rule. It exists only if the authority root has authorized that exact closure. A proof that `D` and `D2` are equivalent relative to the wrong source objective remains evidence about the wrong proposition and does not create authority.

## T1/T2/T3 continuity

At T1, the applicable boundary establishes the exact tuple and exact current objective binding before admitting `D`. A T1 `AUTHORIZED` result is necessary but not sufficient for T3.

At T2, staging creates no authority. Changes to the objective, `D`, schema, policy, authority source, delegation, scope, environment, identity basis, boundary epoch, transformation, revocation state, or authoritative ordering can break the previously established relation.

At T3, the consumer re-establishes the exact applicable binding and all other authority-relevant relationships. A cached T1 label is not continuity. Missing or conflicting required current facts yield `UNAVAILABLE`; established applicable invalidity or prohibition yields `DENIED`; only an exact current valid binding followed by complete successful evaluation can preserve `AUTHORIZED`.

## Hostile adoption attacks

| Attack | Required fail-closed treatment |
| --- | --- |
| `D` self-signs, or its generator model signs | Signature is evidence; neither actor becomes the applicable authority source |
| Requester uploads a favorable binding | Requester selection does not establish boundary applicability or issuing authority |
| Verifier/test `PASS`, model agreement, majority, or quorum | Output and count do not establish authority or independence |
| Valid provenance, copied approval, immutable storage | Source history does not establish current authority, scope, or fidelity |
| Stale approved `D` or stale objective | `INV-CONT` and `INV-USE` require exact current versions and validity at T3 |
| Revoked authority root or delegation | Current revocation defeats earlier approval; unknown status is unavailable |
| Signer key valid but role no longer authorized | Cryptographic validity is not current authority |
| Compromised signer | Outside the guarantee when the accepted authority boundary is compromised; no claim of automatic detection |
| Policy fork or two valid-looking bindings | Authoritative ordering and applicable lineage must be established; unresolved conflict is unavailable |
| Quorum split | Count does not select the applicable authority source; unresolved ordering is unavailable |
| Rollback, restored snapshot, cached approval | Old state cannot establish current lineage or status |
| Offline revocation or missing currentness source | Absence of observed revocation is not validity; required state is unavailable |
| Transformed or wrapped `D2` | No inherited binding without new binding or exact authoritative closure |
| Same bytes, different objective | Exact objective identity and scope differ; byte equality is not binding identity |
| Same objective name, different generation | Stable label is not exact identity or continuity |
| Cross-tenant, environment, domain, or boundary use | `INV-BND` blocks implicit transfer; exact separate authority relation required |
| Delegated approval after delegation revocation | Established revocation yields denial; unknown ordering yields unavailable |
| Approval before authority rotation | Prior generation does not silently cross the new authority lineage |
| AI-generated equivalence proof | Evidence only; cannot establish its own authority-bearing mapping |
| Formal equivalence to wrong objective | Valid proof does not bind `D` to the applicable objective |
| Missing objective or unavailable authority source | Required contract admission cannot be established; result is unavailable |

Semantic-interpreter shopping is blocked by requiring the applicable boundary to establish the objective, `D`, binding, and authority source. A requester cannot turn a preferred parser, verifier, registry, or policy fork into the applicable one by selecting it.

## Trust boundary

Ground Truth cannot derive ultimate normative or semantic correctness from nothing. This adoption can establish:

- which authority root is accepted;
- which exact objective that authority root states;
- which exact `D` that authority root admits;
- exact scope, lineage, and delegation;
- currentness and authoritative ordering;
- revocation and supersession state; and
- continuity of those relationships through T3.

It does not prove that the admitted authority root chose a morally, legally, safely, or semantically ideal objective. It does not prove natural-language meaning, ontology quality, formalization completeness, parser/compiler correctness, cryptographic soundness, clock correctness, or uncompromised authority from first principles.

Those are explicit trust preconditions or bounded model limitations. Naming the accepted authority act prevents hidden authorization; it does not turn acceptance into universal truth.

## Proposed exact contract revision shape

The narrow revision consists of one new relational admission rule plus clarifications to all six existing invariants.

### New relational admission rule

> Before an encoded decision contract may participate in an authority decision at T1 or T3, an exact current authoritative `objective_binding` must establish that the exact applicable authority objective admits that exact decision contract for the same subject, artifact, decision/effect, control-state, identity-basis, boundary-epoch or authority-generation, and authority-boundary scope. The requester, contract, verifier, evidence producer, formalizer, compiler, model, or other participant cannot establish the binding merely by assertion, execution, provenance, signature, proof, repetition, or agreement. Missing or conflicting required binding yields `UNAVAILABLE`; established applicable invalidity, revocation, supersession, rejection, scope failure, or prohibition yields `DENIED`; a valid binding makes the contract admissible but does not itself guarantee `AUTHORIZED`.

### Exact invariant changes

- `INV-EVD`: require both evidence-to-contract satisfaction and authoritative objective-to-contract admission; prohibit evidence from promoting itself into the binding.
- `INV-CONT`: require the binding and all validity conditions to remain established or be re-established through T3.
- `INV-DISC`: require exact objective, contract, binding, policy, schema, authority-source, and transformation identities and versions; reject selector or byte equality as fidelity.
- `INV-BND`: bind the issuer and any delegate to the applicable independent boundary and lineage; prohibit implicit cross-boundary inheritance or requester selection.
- `INV-USE`: require current scope, delegation, generation, revocation, supersession, and consumption eligibility; prohibit last-known-good binding use.
- `INV-CLO`: prohibit transformed or derived contracts from inheriting admission without a new binding or exact authoritative closure relation.

Tuple wording does not change. `objective_binding` remains relational authority state associated with the exact decision context. Outcome names and count do not change. Outcome definitions should be clarified only to include missing objective binding among unavailable required relationships and established binding invalidity among prohibiting conditions.

T1/T2/T3 wording must explicitly place contract admission before evaluation at T1, preserve T2 as non-authoritative, and require live re-establishment immediately before and at T3.

`objective_binding` should become named public contract vocabulary because conformance cannot depend on an unnamed assumed mapping. Its storage representation remains an implementation choice.

## Required later contract files

A separately authorized adoption revision would need to amend this exact public set:

- `LAYER2_COMMIT_TIME_AUTHORITY_REVIEW.md`: normative Layer 2 vocabulary, all six invariant definitions, contract admission, T1/T2/T3 semantics, and outcomes;
- `ARCHITECTURE.md`: conceptual flow and authority-outcome language so verification cannot begin from an unadmitted decision contract;
- `EVIDENCE_MODEL.md`: evidence-binding principle, making evidence-to-contract satisfaction distinct from objective-to-contract admission;
- `SECURITY_MODEL.md`: fail-closed, privilege-separation, boundary-selection, and continuing-authority treatment for objective bindings;
- `README.md`: core-model and design-rule summary after, and only after, adoption; and
- `PUBLICATION_MANIFEST.md`: public exhibit inventory and claim boundary if the adopted contract revision is included in the published exhibit.

`ALPHA_COMPLETION.md`, historical candidate documents, completed frontier artifacts, and the PR #16 design record should remain historical and should not be rewritten to simulate prior adoption. Any link-only or publication-index change must occur in the same separately authorized publication phase, not here.

## Implementation obligations

This design does not authorize implementation. A later implementation phase would need, at minimum, to represent exact objective, contract, binding, authority-source, scope, version, lineage, delegation, ordering, currentness, revocation, supersession, and closure facts; distinguish binding authority from operational evidence; prevent self-attestation and requester routing; re-establish state at T3; and preserve durable ambiguity rather than guessing.

Representation remains open. These semantics do not require a new tuple field, one database column per analytical dimension, a particular signature format, a central registry, or a disclosed private mechanism.

## Test/fixture obligations

No test or fixture changes are authorized here. A later authorized validation phase should add:

- PR #15 primary and stronger regression traces;
- exact valid-binding positive control;
- missing, conflicting, stale, expired, revoked, superseded, wrong-scope, and wrong-generation bindings;
- objective, policy, contract, schema, signer-role, authority-root, and boundary changes between T1 and T3;
- self-signed, generator-signed, requester-supplied, model-generated, quorum, copied, and provenance-only bindings;
- policy forks, ordering loss, rollback, restored snapshot, offline revocation, and replica lag;
- transformed, wrapped, compiled, translated, migrated, and cross-boundary contracts; and
- signatures or formal proofs for the wrong objective.

Expected outcomes must be derived from current established facts, not assigned solely from an attack label.

## Migration/versioning obligations

Contract adoption is a semantic version event because previously admissible `D` instances may lack the newly required relation. Migration must not backfill authority by assumption.

A later revision must:

- give the adopted contract version an exact identity;
- identify the authority act that adopts it and its effective boundary generation;
- distinguish pre-adoption decisions and bindings from post-adoption ones;
- require explicit authoritative migration or replacement bindings where continued use is intended;
- define ordering against revocations, supersessions, policy forks, and authority rotation;
- prevent rollback to the pre-adoption semantics from recreating authority; and
- fail `UNAVAILABLE` when the applicable contract version or migration relation cannot be established.

Historical records may remain authentic evidence of what occurred under an older contract. They do not silently become current objective bindings.

## Residual model limitations

An admitted authority root can deliberately or mistakenly approve a poor mapping. If it authoritatively binds `O` to a deficient `D`, this model can faithfully represent bad authority. That is a trust-root or policy-quality limitation, not a missing-binding authorization.

The model cannot guarantee unique natural-language meaning, complete formalization, uncompromised keys or sensors, perfect clocks, total observer coverage, or universal semantic equivalence. It can require exact responsibility, scope, lineage, currentness, and fail-closed handling of missing authority.

Compromise of the accepted authority boundary may defeat the guarantee. Cryptographic and observer integrity remain preconditions; this design does not claim to detect every compromise.

## Residual counterexample search

The adoption was pressured against self-authorization, evidence promotion, identity/fidelity confusion, semantic-interpreter shopping, stale and revoked state, authority rotation, policy forks, ordering loss, transformation inheritance, cross-boundary reuse, and permanent unavailability.

The PR #15 trace does not survive: without exact current authoritative admission, `D(P')` is ineligible to produce authority; with an explicit current rejection, it is denied; with a valid admission, the authority root has accepted the mapping and the original missing-binding premise no longer holds.

No residual case was found in which all adopted relational requirements and all frozen requirements are established, the contract returns `AUTHORIZED`, and the same fixed authority objective nonetheless forbids the exact transition solely because objective-to-contract admission is absent. Cases involving a legitimately authoritative but bad mapping remain within the stated trust/model limitation. Cases involving compromise, missing observers, or implementation failure do not show the adopted contract itself permitting the transition.

No narrower adoption closes the gap. Identity-only language does not establish fidelity. An `INV-EVD` sentence without an external authority-bearing relation is circular. Scope language without current authoritative admission renames the gap. A signature, proof, witness, or quorum supplies evidence unless independently made authoritative.

## Adoption recommendation

Recommend a later human-authorized contract revision that adopts the new relational admission rule and the six exact invariant clarifications above.

Authority source requirements are narrow: the applicable independent authority boundary, or an exact current authorized delegate, must issue the binding within scope. Identity, provenance, signatures, proofs, verifier success, and agreement are insufficient without that authority role.

Revocation and supersession are live ordered authority state. Unknown status fails `UNAVAILABLE`; established applicable invalidity or prohibition yields `DENIED`. T1 admission must be re-established at T3 after any relevant T2 change. Transformed contracts require a new binding or exact authoritative closure relation.

The tuple remains six coordinates. The invariant set remains six. The outcome set remains three. The recommended change is a semantic tightening of how the existing contract admits `D`, not architectural expansion.

## Authorization boundary

This artifact performs contract-adoption design only.

- Design recommendation: contained here.
- Contract adoption: not performed; requires a later explicit human-authorized public-contract revision.
- Implementation: not authorized.
- Tests and fixtures: not authorized to change.
- Workflows and validators: not authorized to change.
- Deployment and roadmap movement: not authorized.
- Publication and merge: remain human-controlled separate decisions.

Review, test success, commit creation, publication, or merge would be evidence about this artifact, not authority for the later phases.

## Final determination

The narrow relational admission rule is expressible through the existing six invariants. It closes the omitted objective-to-contract mapping exposed by PR #15, preserves exact failure-closed outcome derivation, and retains a positive authorization path without adding a tuple coordinate, invariant, or outcome.

**ADOPTION DESIGN COMPLETE — EXISTING SIX-INVARIANT CONTRACT CAN INCORPORATE OBJECTIVE_BINDING**
