# Ground Truth Frontier Delta — Semantic Evidence / Proposition Binding

## Status and scope

This document records a design- and research-only pressure test against the exact public Ground Truth state at `c5662312597b9afbb1b8a7b70b6665a598a39a4d` (`SEMANTIC_EVIDENCE_BASELINE`). Research and review are evidence, not authority.

This artifact does not authorize implementation, tests, fixtures, workflows, roadmap movement, deployment, publication, merge, or any authority-bearing transition. It does not modify the public contract or disclose private-core material. Human adoption and merge authority remain separate.

The exact frozen authority tuple remains:

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

`T1` is evaluation. `T2` is non-authoritative preparation, staging, or fencing. `T3` is the irreversible authority-consuming boundary. A valid `T1 AUTHORIZED` result is necessary but not sufficient for T3. Exact required current authority-relevant state unavailable yields `UNAVAILABLE`. An established applicable current prohibition yields `DENIED`. `AUTHORIZED` remains possible only when all exact required authority-relevant state and relationships are established and the applicable current decision contract permits the exact T3 effect.

The governing distinctions remain:

**Capability ≠ Evidence ≠ Authority ≠ Execution**

Verifier correctness ≠ semantic specification correctness.

Evidence provenance ≠ evidence truth.

Evidence truth ≠ authority.

## Research question

Can the frozen Ground Truth contract permit `AUTHORIZED` at T3 when every evidence object is authentic, fresh, correctly executed, and bound by identifier to the exact tuple and decision, but the evidence establishes the wrong semantic proposition?

The pressure combines two failure classes:

1. **Verdict-preserving unfaithfulness.** A formal representation encodes a proposition different from the natural-language or policy requirement, yet its solver executes correctly and produces the expected verdict.
2. **Perfect aliasing.** A probe, classifier, monitor, or evaluator performs perfectly where two properties coincide, but the evidence does not identify which property it tracks. When the properties later separate, the prior performance does not establish the required property.

The inquiry attacks the contract rather than assuming the answer. It does not treat a semantic difference as an automatic outcome.

## Frozen contract under pressure

The strongest existing text is `INV-EVD`: evidence is bound to the exact tuple and decision for which it was admitted; evidence is not authority; evidence from one tuple, state, boundary epoch, identity basis, or decision cannot be silently reused; and weaker evidence cannot be promoted into satisfying a stronger applicable decision contract.

That requirement blocks runtime promotion when the applicable decision contract actually requires `P` and evidence establishes only `P'`. Binding evidence identifier `E` to decision identifier `D` does not, in that case, establish that `E` satisfies `D`.

It does not follow that `INV-EVD` establishes the semantic fidelity of `D` itself to an authority objective expressed outside `D`. If `D` incorrectly formalizes required proposition `P` as proxy `P'`, evidence for `P'` is not weaker relative to the encoded contract: it satisfies exactly what `D` asks. All tuple, boundary, evidence, continuity, and consumption checks can therefore succeed while the external authority objective remains unsatisfied.

The frozen contract does not explicitly bind the encoded decision contract to the authority proposition it is intended to represent. Treating that missing fidelity relationship as already contained in `INV-EVD` would assume the conclusion under review. This is the candidate contract-level gap tested below.

## Semantic evidence model

Analytical notation:

- `P` = the authority-required proposition.
- `P'` = the proposition actually established by evidence.
- `E` = the evidence object or evidence relation.
- `D` = the applicable authority decision contract.
- `C` = semantic or environmental context where required.

`P`, `P'`, `E`, `D`, and `C` are notation only. They are not tuple coordinates, invariants, authority outcomes, or implementation fields mandated by this artifact.

For an exact T3 decision, it is insufficient to establish only:

1. the identity, provenance, freshness, and integrity of `E`;
2. correct execution of the producer or verifier of `E`; and
3. a stored association between `E` and `D`.

Objective-preserving authorization would require the proposition supported by `E` to be semantically sufficient for the authority proposition the decision contract is intended to represent in the exact current context. Symbolically, the required relationship is not `E -> D` by identifier alone, but an established current relationship of the form:

`E establishes P'` and `D in C accepts P' as sufficient for P`.

No universal logical calculus is implied. When `D` correctly states that it requires `P`, an unestablished `P' -> P` relationship makes the required evaluation unavailable; an established failure yields denial; and established sufficiency preserves an authorization path. The hostile case is different: `D` itself encodes `P'` as the requirement while the actual authority objective remains `P`. The frozen checks can then see a complete evaluation even though the objective-to-contract mapping is unfaithful.

## Why authentic evidence can still be insufficient

Authenticity answers questions such as who signed, which key was used, which bytes were covered, and whether the object was altered. Provenance can establish source and lineage. Freshness can establish timing relative to an authoritative ordering source. Correct execution can establish that a verifier accurately evaluated its encoded input.

None of these properties silently changes the proposition encoded or measured. Authentic evidence for `P'` remains authentic evidence for `P'`. Relabeling it as evidence for `P`, repeating it, aggregating it, signing it again, or obtaining consensus about its verdict cannot create an unestablished entailment.

## Flagship verdict-preserving-unfaithfulness case

### Required and observed propositions

Required authority proposition:

`P = "Artifact A has been independently reviewed and permitted for release under policy X."`

Observed verifier proposition:

`P' = "Artifact A passes test suite Y."`

Established facts:

- artifact identity is exact;
- evidence is authentic and fresh;
- verifier identity and execution are established;
- test result is `PASS`;
- provenance is intact;
- there is no replay or stale evidence;
- there is no boundary substitution;
- no compromised cryptographic primitive is assumed;
- no explicit prohibition has yet been established.

At T1, the applicable encoded decision contract `D` incorrectly formalizes policy `X`: it treats passing suite `Y` as the complete release condition. Evidence for `P'` therefore satisfies `D`, which emits `AUTHORIZED`. The intended authority objective remains `P`. At T3, the system attempts release with unchanged current state and no missing frozen-contract fact.

### Attack result

Solver or test success establishes only the proposition actually encoded and evaluated. Passing suite `Y` does not establish independent review and release permission under policy `X`.

Nevertheless, the encoded `D` requires only `P'`. There is no runtime relabeling of weak evidence into a stronger condition inside `D`; the stronger condition was lost when the authority objective was formalized. `INV-EVD` evaluates evidence against the encoded decision contract, and the other frozen invariants preserve exact identity, boundary, continuity, use, and closure without testing whether `D` faithfully represents `P`.

The frozen contract therefore permits `AUTHORIZED` in this construction while the stated authority objective makes release impermissible. This is a reproducible in-scope contract counterexample at the design level. It does not prove that every semantic mismatch authorizes, and it does not authorize a contract repair in this artifact.

## Flagship perfect-aliasing case

### T1 context

In context `C1`, truthfulness and compliance happen to coincide. A probe is trained and evaluated in `C1`; it achieves perfect predictive performance. Its output is positive for an artifact. The applicable decision requires truthfulness.

Perfect performance in `C1` establishes predictive agreement over the observed distribution. It does not by itself identify whether the probe represents truthfulness, compliance, a shared correlate, or another feature.

### T2 context change

Context changes from `C1` to `C2`. In `C2`, truthfulness and compliance separate. The probe continues to output positive because the artifact is compliant but untruthful.

### T3 attack

Historical correlation cannot silently define evidence semantics. If the probe's measurement relationship to truthfulness in `C2` is unestablished, required semantic sufficiency is unavailable. The probe identifier and model bytes may remain unchanged while its authority-relevant measurement validity changes.

Depending on the applicable contract, this can engage:

- `INV-EVD`, because positive proxy evidence cannot be promoted into evidence of truthfulness;
- `INV-CONT`, because the semantic relationship established in `C1` does not remain established in `C2`;
- `INV-DISC`, because stable property labels or probe names do not prove identity of the measured property;
- `INV-USE`, because a prior interpretation cannot remain usable after its validity conditions change.

If the applicable current contract independently establishes that the probe remains a sufficient truthfulness measure in `C2`, and all other exact T3 relationships hold, `AUTHORIZED` remains possible. Context change alone is not hard-coded as failure.

## Three-way outcome derivation

### Variant U — semantic relationship unestablished

`P'` is established, but whether `P'` satisfies or entails required `P` under the current `D` and `C` cannot be established.

The decision contract's required evidence evaluation cannot be completed. The result is `UNAVAILABLE`. This is not a new rule named `semantic_difference = UNAVAILABLE`; it follows from `INV-EVD`'s prohibition on evidence promotion and from the requirement that the applicable evaluation be established.

### Variant D — semantic relationship explicitly fails

`P'` is established. The applicable boundary, exact tuple, current contract, and interpretation relationship are all established. `D` explicitly says that `P'` does not satisfy the required condition `P`, or an applicable current rule prohibits release on `P'` alone.

The result is `DENIED`: evaluation is available and an established applicable condition fails. It would be incorrect to call this `UNAVAILABLE`, because the semantic relationship is known rather than missing or conflicting.

### Variant A — semantic relationship established

`P'` is established. The applicable current decision contract explicitly establishes that `P'` is sufficient evidence for `P` for the exact subject, artifact, control state, identity basis, boundary epoch, and decision. Source, provenance, freshness, boundary, grant/effect, consumption eligibility, and T3 continuity are exact.

The result may be `AUTHORIZED`. Proxy evidence is not permanently unusable; it is usable when its exact current semantic sufficiency is itself established by the applicable contract.

## Temporal alias break between T1 and T3

At T1 in `C1`, the applicable contract validly establishes equivalence or sufficiency between `P'` and `P`. Evidence `E` establishes `P'`, and the exact T1 decision is `AUTHORIZED`.

During T2, `C1 -> C2`. The context change may be a policy version, deployment environment, test profile, formalization map, monitor coverage, world-model domain, reviewer role, ontology, or evidence-interpretation contract change. T2 creates no authority.

At T3:

- If current semantic sufficiency in `C2` cannot be established, the outcome is `UNAVAILABLE`.
- If the current relationship is established and `D` prohibits or fails release under `C2`, the outcome is `DENIED`.
- If the current relationship is re-established as sufficient and all exact T3 conditions remain satisfied, `AUTHORIZED` remains possible.

This result follows from verification-to-use continuity and continuing-grant validity. Cached T1 success cannot preserve an evidence interpretation after its defined context changes.

## Pressure matrix

| Class | Proposition actually established | Invalid promotion | Engaged invariants | Classification |
|---|---|---|---|---|
| Verdict-preserving formalization | Solver verdict for encoded `F(P')` | `F(P')` faithfully represents `P` | existing invariants do not establish objective-to-contract fidelity | candidate contract counterexample; trust precondition; test gap |
| Perfect aliasing | Predictive agreement in `C1` | Probe measures required property in rival `C2` | `INV-EVD`, `INV-CONT`, `INV-DISC`, `INV-USE` | already represented by frozen contract; implementation obligation; trust precondition; test gap |
| Test suite | Tests in suite `Y` pass | Functional correctness, safety, policy compliance, permission, or deployment authority | `INV-EVD`, `INV-CLO` | already represented by frozen contract; test gap |
| Attestation overreach | Signed measurement or quoted state | Uncompromised hardware, semantic correctness, safety, or permission | `INV-EVD`, `INV-DISC` | already represented by frozen contract; trust precondition |
| Monitor silence | No violation observed through covered channel | No violation exists, system is safe, or release is authorized | `INV-EVD`, `INV-CONT` | already represented by frozen contract; trust precondition; test gap |
| Human review mismatch | Identified human performed stated review act | Human authorized release | `INV-EVD`, `INV-DISC`, `INV-BND` | already represented by frozen contract; implementation obligation; test gap |
| Provenance overreach | Source, time, key, and lineage | Proposition truth or authority | `INV-EVD` | already represented by frozen contract; trust precondition |
| Cryptographic proof mismatch | Encoded statement is validly proven | Different authority proposition is true or permitted | `INV-EVD`, `INV-DISC`, `INV-CLO` | already represented by frozen contract; trust precondition; test gap |
| World model / simulation | Prediction or simulated state | External state actually holds | `INV-EVD`, `INV-CONT`, `INV-CLO` | already represented by frozen contract; trust precondition; model limitation; test gap |
| Agent verifier optimization | Verifier `V` accepts behavior | Intended authority proposition is satisfied | `INV-EVD`, `INV-BND`, `INV-CLO` | already represented by frozen contract; implementation obligation; test gap |
| Derived summary / memory | Summary or memory record states an interpretation | Source record carries the summarized authority | `INV-EVD`, `INV-DISC`, `INV-CLO` | already represented by frozen contract; implementation obligation; test gap |
| Positive exact semantic path | `P'` and its exact current sufficiency for `P` | None | all applicable existing invariants | already represented by frozen contract |

## Detailed pressure classes

### A. Verdict-preserving unfaithful formalization

A sound and complete solver for an encoded formula establishes its result for that formula. Solver correctness does not establish that the formula faithfully represents a natural-language requirement. Formalization-fidelity evidence must bind to the exact requirement, formal object, schema and parser versions, context, decision contract, and relevant epoch. Unknown fidelity yields `UNAVAILABLE`; explicitly false fidelity makes an otherwise evaluable condition fail and yields `DENIED`; exact independently established equivalence permits the evidence to participate in `AUTHORIZED`.

### B. Perfect aliasing

A positive probe establishes only what its measurement validation supports. Historical coincidence cannot silently define the measured property. The property identity and context-sensitive measurement relationship are authority-relevant within the applicable evidence contract. Stable labels such as `truth_probe` are selectors, not semantic proof.

### C. Test suite is not authority

“All tests pass” establishes that the executed tests produced their defined passing results under the observed configuration. It does not automatically establish complete functional correctness, safety, policy compliance, release permission, or deployment authority. Each is a distinct proposition requiring its own admitted evidence relationship and applicable decision rule.

### D. Attestation semantic overreach

A valid TPM quote, signature, HSM statement, or enclave report proves only its precisely specified cryptographic and measurement claim under stated assumptions. It does not automatically establish uncompromised hardware, correct runtime semantics, current permission, safe state, or authorized release. Cryptographic authenticity cannot repair a statement-selection error.

### E. Monitor or tripwire negative result

“No violation observed” is bounded by sensor, coverage, time, detection, and reporting assumptions. It is not equivalent to “no violation occurred,” “safe,” or “authorized.” Absence of observation becomes evidence of absence only under an established applicable observation model.

### F. Human review semantic mismatch

An authentic signature over “content reviewed” establishes the signed review act under relevant identity and cryptographic assumptions. It does not establish “release authorized” unless the human, role, act, scope, and current decision contract make that exact act authoritative. Human origin does not create authority.

### G. Provenance is not truth or authority

Perfect provenance may establish who produced evidence, when, under which key, and through which lineage. It can remain exact while the asserted proposition is false or irrelevant to the authority decision. Provenance is a property of evidence and its history, not a substitute for semantic sufficiency or authority.

### H. Cryptographic proof semantic mismatch

A proof can be mathematically valid for the encoded statement while the encoded statement is not the proposition required by the authority decision. This attack assumes no cryptographic defect. It targets statement selection, parsing, schema, formalization, and decision-contract binding.

### I. World-model or simulation evidence

A prediction that external state `X` holds is not an observation that `X` actually holds. Simulated completion is not real execution. Confidence is not authority. If T3 requires current external state, the applicable evidence relationship must establish external state through an admitted observation path rather than silently promoting a forecast or simulation.

### J. Agent verifier optimization

An agent rewarded for satisfying verifier `V` may find behavior accepted by `V` while violating the intended proposition. The authority question is not merely whether the behavior is “reward hacking”; it is which proposition `V` actually establishes, whether that proposition satisfies `D`, and whether the verifier or requester can select a favorable semantic interpreter. Verifier acceptance cannot authorize itself.

### K. Derived summary or memory

An authentic memory saying “approved by Alice” can be a faithful record of its own bytes while misrepresenting a source that said “Alice reviewed formatting.” Semantic compression creates a new artifact and asserted proposition. It requires exact provenance and evidence binding and cannot inherit source authority through implicit closure.

### L. Positive exact semantic path

The required proposition `P` and observed proposition `P'` are explicit. Evidence `E` currently establishes `P'`. The applicable contract `D`, under exact current context `C`, explicitly establishes the sufficiency relationship from `P'` to `P`. The source and provenance are current; tuple, boundary, grant/effect, consumption eligibility, and T3 continuity are exact. No applicable prohibition is established. `AUTHORIZED` remains possible.

## Existing invariant analysis

### INV-CONT — Verification-to-use continuity

The live consume-time tuple and all required relationships must match what is established at verification. When semantic sufficiency depends on context, policy, schema, reviewer role, monitor coverage, or interpretation version, its validity conditions must remain established at T3. A semantic relationship that was valid only in `C1` cannot be cached into `C2`.

### INV-DISC — Identity-bearing discriminator discipline

Proposition names, field names, labels, ontology terms, test-suite names, probe names, and schema handles are selectors. Stable selectors do not prove identity or meaning of the measured or encoded proposition. Exact identity bases and versioned interpretation relations are implementation and trust obligations where the applicable decision depends on them.

### INV-BND — Boundary identity and epoch binding

A requester cannot select, replace, route around, or bootstrap a favorable semantic interpreter to obtain the desired meaning. A model, agent, verifier, evaluator, or reviewer cannot become an independent authority boundary merely by agreeing with its own output. Interpreter or policy-boundary replacement may require a distinguishable epoch unless continuity is independently established.

### INV-EVD — Evidence binding and non-promotion

`INV-EVD` blocks authentic evidence of `P'` from satisfying an encoded decision contract that actually requires `P` unless the applicable sufficiency relationship is established. Identifier binding, repetition, agreement, transformation, consensus, and cryptographic wrapping do not strengthen the proposition established.

`INV-EVD` does not, as currently written, establish that the encoded decision contract faithfully represents an authority objective defined outside that contract. When `D` itself substitutes `P'` for `P`, evidence of `P'` satisfies the encoded requirement without runtime evidence promotion. Treating objective-to-contract fidelity as implicit in `INV-EVD` would silently strengthen the frozen invariant.

### INV-USE — Consumption is not last-known-good

A prior semantically valid interpretation remains usable only while its defined validity conditions remain satisfied for the same exact tuple. A policy, ontology, context, domain, schema, role, or measurement-validity change cannot leave a continuing or cached grant silently usable. Re-evaluation yielding `DENIED` or `UNAVAILABLE` does not preserve permission.

### INV-CLO — No implicit transformation closure

Formalization, classification, probing, summarization, simulation, translation, compilation, parsing, aggregation, and memory compression all create derived artifacts or relationships. Authority over or evidence about a source does not automatically close over its semantic transformation. Exact authority-preserving transformation must be explicitly defined by the applicable contract.

## Semantic interpreter and recursion boundary

If verifier `V` establishes `P'`, the relationship from `P'` to `P` can be established by an applicable decision contract, versioned semantic mapping, human policy act, formal equivalence proof, schema binding, or meta-verifier. None is automatically authoritative merely by existing.

Ground Truth does not require an infinite chain of meta-verifiers. The applicable authority boundary defines a trust base: which contract, interpreter, schema, observer, and identity basis are admitted; which relationships must be evidenced; and where assumptions stop. The live applicability, identity, provenance, version, and boundary lineage of that trust base must be established at T3.

The unresolved issue is one level earlier: the frozen contract does not expressly require evidence that the admitted decision contract faithfully represents the stated authority objective. A future design may place that mapping at a bounded human policy root, formal equivalence relation, or other explicitly trusted boundary without claiming infinite regress. Choosing that repair is outside this research artifact.

Whether a selected trust base is ultimately truthful or normatively correct still remains a trust or model boundary. The counterexample here is narrower: the authority objective is held fixed as `P`, `D` incorrectly encodes `P'`, and the frozen contract has no explicit fidelity check between them.

Classification:

- Binding evidence to the proposition explicitly required inside `D` is already represented by the frozen contract.
- Binding `D` to the external authority objective it is intended to formalize is a candidate contract counterexample.
- Recording and enforcing either relationship is an implementation obligation once separately authorized.
- Correctness of the admitted semantic root remains a trust precondition.
- Truth from first principles and universal semantic grounding are model limitations or out of scope.

## Trust preconditions

The frozen contract does not itself prove:

- fidelity of a natural-language requirement;
- fidelity of a formalization;
- correctness and completeness of a semantic schema;
- parser, compiler, runtime, or solver correctness;
- probe training-distribution assumptions;
- validity and causal specificity of a probe measurement;
- stability and identity of labels and ontology terms;
- integrity and adequacy of policy definitions;
- evaluator identity, scope, competence, or independence;
- reviewer identity, role, scope, or authority;
- correctness of cryptographic primitives and key custody;
- completeness and integrity of provenance recording;
- clock and authoritative ordering integrity;
- external-world observer or sensor integrity;
- world-model calibration or domain applicability;
- correctness of context classification;
- identity, applicability, integrity, and lineage of the active contract version.

Where any such assumption is required by `D` and cannot be established at T3, the result is `UNAVAILABLE`. Where the exact current contract is evaluable and establishes that a required condition fails, the result is `DENIED`.

## Implementation obligations

Without authorizing implementation, this analysis identifies obligations for any conforming realization where applicable:

- represent the proposition actually established by each evidence source rather than only an evidence identifier;
- bind evidence semantics to the exact applicable decision contract, context, schema, policy, and boundary epoch;
- prevent weak propositions from being relabeled as stronger propositions;
- distinguish verifier execution success from formalization fidelity;
- discriminate property, ontology, schema, probe, policy, and interpreter versions;
- preserve semantic transformation provenance through parsing, compilation, formalization, summarization, simulation, and memory;
- re-establish context-dependent semantic sufficiency at T3;
- distinguish unknown entailment from an established failed or prohibited condition;
- prevent requester-selected semantic interpreters and self-attesting verifiers from bootstrapping authority;
- bind human signatures to exact acts, roles, scopes, artifacts, and decision contracts;
- state exactly what tests, monitors, attestations, proofs, probes, and models establish;
- fail closed on missing, conflicting, stale, or inapplicable semantic relationships.

These obligations do not add an invariant or authorize implementation.

## Test gaps

No tests or fixtures are added here. Candidate future tests, subject to separate authority, include:

- valid solver verdict over an unfaithful formalization;
- unknown, explicitly false, and independently proven formalization fidelity;
- a perfect proxy in `C1` that diverges from the required property in `C2`;
- a passing test suite presented as safety, compliance, permission, and deployment authority;
- authentic attestation for a measurement irrelevant to the required proposition;
- monitor silence with incomplete coverage and with established complete coverage;
- authentic “reviewed” signature interpreted as “release authorized”;
- exact provenance attached to a false or authority-irrelevant proposition;
- valid cryptographic proof for a statement different from the required authority proposition;
- simulation success substituted for current external-world state;
- an optimizing agent selecting or shaping verifier semantics;
- an authentic derived memory that expands a source review into approval;
- context changes between T1 and T3 across policy, schema, role, ontology, monitor, and domain;
- a positive exact path with current explicit semantic sufficiency and all T3 relations established.

These are test gaps, not claims that current Authority Lab fixtures already establish semantic truth.

## Model limitations and out-of-scope boundaries

This authority model does not establish:

- semantic truth or natural-language meaning from first principles;
- that a policy or authority objective is wise, safe, complete, or morally correct;
- universal ontology alignment across people, systems, languages, domains, or time;
- that an admitted semantic interpreter, reviewer, observer, solver, parser, compiler, sensor, or cryptographic root is uncompromised;
- that statistical probes have unique causal interpretations;
- that finite tests establish universal functional correctness or safety;
- that monitor silence proves absence of harmful behavior;
- that simulations or predictions establish external reality;
- that agreement proves semantic equivalence or independence;
- semantic truth beyond a separately established objective-to-contract fidelity boundary;
- protection after a legitimately authorized effect exceeds the stated authority objective.

Those are trust preconditions, model limitations, out-of-scope objectives, or reasons to improve the applicable decision contract. They do not create a new authority outcome.

## Candidate contract counterexample analysis

The strongest attempted counterexample fixes all referential checks:

- tuple exact;
- boundary exact;
- evidence authentic and fresh;
- provenance exact;
- evidence identifier bound to the tuple and decision;
- decision contract nominally evaluable;
- no stale state, replay, grant reuse, or consumption ambiguity;
- no established prohibition;
- all explicit identifier and cryptographic checks pass.

The first construction sets `E` to establish `P'` while encoded `D` explicitly requires `P`, with no established relationship from `P'` to `P`. Existing `INV-EVD` blocks this case because the applicable evidence evaluation is not established. It is not the surviving counterexample.

The surviving construction holds the stated authority objective fixed as `P` but gives the frozen contract an applicable encoded `D` that incorrectly formalizes the objective as `P'`. Evidence `E` authentically and freshly establishes `P'`. `D` is current and evaluable; all exact tuple, boundary, provenance, continuity, grant/effect, and consumption relationships hold; no prohibition is established; and no runtime transformation or relabeling occurs. The frozen checks permit `AUTHORIZED`, yet release remains impermissible under the fixed objective `P` because `P'` does not entail `P`.

This is not merely an implementation bug in enforcing the existing invariants. The missing relationship is the semantic fidelity of the applicable decision contract to the authority objective it purports to encode, and the frozen contract does not expressly require that relationship. The counterexample therefore satisfies the stated strict standard.

This finding does not determine the repair. A separate design review must decide whether the narrowest correction is a tightening of an existing invariant, an explicit decision-contract applicability rule, or another bounded mechanism. This artifact does not create a new tuple coordinate, invariant, outcome, or implementation authority.

## Public/private boundary

This artifact contains only abstract public research pressure. It includes no private validators, fixtures, migrations, operational mechanisms, credentials, protected evidence, exploit payloads, or private-core material. Detailed future adversarial fixtures and implementation mechanisms remain outside this document and require separate authority.

## Final determination

**REPRODUCIBLE IN-SCOPE CONTRACT COUNTEREXAMPLE FOUND**

The frozen contract prevents evidence for `P'` from satisfying an encoded decision contract that explicitly requires stronger proposition `P`. It does not expressly establish that the encoded decision contract itself faithfully represents the fixed authority objective. When `D` incorrectly substitutes `P'` for `P`, all frozen checks can pass and yield `AUTHORIZED` while the exact transition remains impermissible under the stated objective.

This is a bounded design finding, not proof of universal semantic failure, an implementation defect, authorization to change the contract, implementation authority, certification, safety, or roadmap authority.
