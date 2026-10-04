# Ground Truth for PHI: Deterministic Authorization of Semantic Disclosure in AI Systems

## Research preprint candidate v1.0 — 4 October 2026

### Abstract

Privacy-preserving AI systems can hide payer identity, minimize account metadata, protect
transport, and isolate local state while leaving a separate question unresolved: whether
the exact semantic information in a model request is currently authorized for disclosure.
This paper separates cryptographic privacy, data minimization, access/payment authorization,
and semantic disclosure authority. Using the pinned public architecture
`ethereum/zkapi@045b444ea1b52538d1b40273c7cb6ed09468a052` as a bounded case study and
synthetic health-information scenarios, we construct ten adversarial disclosure families:
cumulative composition, disclosure-history rollback, authorization-to-execution mutation,
derived-disclosure laundering, effective-recipient collapse, revocation races, ambiguous
send outcomes, cross-session memory contamination, provider migration, and a final hostile
composition. We then integrate the resulting disclosure-authority gate into Ground Truth's
existing `authority-lab-v1` model without adding a seventh invariant, fourth outcome, or
new tuple coordinate. The merged implementation preserves `AUTHORIZED`, `DENIED`, and
`UNAVAILABLE`, joins semantic disclosure authority to the existing protected T3 event, and
applies the invariant `NO CURRENT PHI DISCLOSURE AUTHORITY -> NO EXTERNAL INFERENCE EFFECT`.
At the merged repository state, the bounded regression record is 265/265 Authority Lab
tests PASS, 478/478 fixtures PASS, hostile review PASS, and final implementation verifier
OVERALL PASS. These are failure-to-falsify results under the stated model and assumptions,
not claims of HIPAA, PHIPA, PIPEDA, production security, or universal correctness.

## 1. Motivation

Local models, anonymous payment, privacy-preserving transport, and remote frontier models
can reduce exposure without answering whether a particular semantic disclosure is
currently authorized. PHI makes this especially sharp because disclosures can be
irreversible and because multiple modest facts can compose into a materially different
privacy state.

## 2. Property separation

`Capability != Evidence != Authority != Disclosure`

`Privacy != Disclosure Authority`

`Per-request authorization != Composed authorization`

A model's ability to sanitize, a cryptographic proof, or anonymous payment evidence cannot
silently establish a different proposition: permission for exact semantic content to
cross an exact boundary for an exact purpose at an exact time.

## 3. Case-study boundary

Pinned case study:
`ethereum/zkapi@045b444ea1b52538d1b40273c7cb6ed09468a052`

The lease authorization is explicitly prompt-free. The local OpenAI-compatible daemon
separately accepts message content, structurally sanitizes the request, and forwards the
cleaned inference body. This makes zkAPI useful as a boundary case precisely because its
payment/privacy mechanisms can remain correct while semantic disclosure authority is a
separate proposition.

No zkAPI vulnerability is claimed.

## 4. Model

For request n:
- `R_n`: proposed disclosure
- `D_n`: durable prior disclosure state
- `C_n`: recipient/provider
- `P_n`: purpose
- `A_n`: current authority evidence
- `E_n`: canonical execution event

Required:
`Authorize(R_n | D_n, C_n, P_n, A_n)`

Primary invariant:
`NO CURRENT PHI DISCLOSURE AUTHORITY -> NO EXTERNAL INFERENCE EFFECT`

## 5. Attack 1: cumulative composition

Toy synthetic policy: no more than two quasi-identifying facts may be disclosed to the
same recipient in one authority epoch.

Each one-fact request is individually authorized, yet the third cumulative disclosure is
denied. Thus:

`forall i, Authorized(R_i)` does not imply `Authorized(union_i R_i)`.

A history-aware controller must evaluate the proposed effect against durable prior
disclosure state.

## 6. Attack 2: rollback / ABA

After two external disclosures, restore a local snapshot from before either disclosure.
The local endpoint again shows empty history, but the recipient still has the prior facts.

Local:
`D0 -> D2 -> D0`

External:
`D0 -> D2 -> D2`

Therefore endpoint equality does not establish disclosure-state identity.

A protected monotonic history head detects the restored stale state and returns
`UNAVAILABLE`. If complete independently protected history is recovered and the next
effect is known to exceed policy, the result becomes `DENIED`.

## 7. Three-way outcome discipline

`AUTHORIZED`: every required current relation is exact and complete.

`DENIED`: an exact current applicable prohibition/restriction is established.

`UNAVAILABLE`: a required current fact is missing, stale, ambiguous, conflicting, rolled
back, or not converged at the effect event.

Absence of proof of a restriction is not permission.

## 8. Disclosure lineage

Disclosure is modeled as a non-restorable effect lineage. A durable representation needs
monotonic order, predecessor linkage, effect binding, recipient/purpose/policy binding,
and rollback/fork detection. A digest alone is not authority; currentness requires an
independently admitted source.

## 9. Existing Ground Truth invariants

The PHI research currently maps into the existing frozen architecture:
- `INV-CONT`: exact authorization-to-effect and history continuity
- `INV-DISC`: no selector/endpoint restoration as identity proof
- `INV-BND`: exact recipient/provider and epoch
- `INV-EVD`: privacy/sanitization evidence is not semantic authority
- `INV-USE`: replay/consumption and one-shot disclosure authority
- `INV-CLO`: transformed/derived/retried effects remain inside the authority envelope

No seventh invariant or fourth outcome is proposed.

## 10. Compliance boundary

This work does not encode legal conclusions. Law, regulation, institutional policy,
consent, contractual duties, and clinical context determine the authority propositions
that must be satisfied. Ground Truth's narrower role is to require current evidence for
those propositions at the external effect boundary.

## 11. Current empirical status

Synthetic executable tests currently cover:
- independent per-request authorization
- cumulative third-disclosure denial
- missing history -> UNAVAILABLE
- recipient substitution -> UNAVAILABLE
- purpose substitution -> UNAVAILABLE
- rollback restores apparent permission in a naive controller
- protected history detects rollback -> UNAVAILABLE
- recovered complete history -> DENIED when cumulative policy is exceeded
- positive current-history path remains AUTHORIZED
- incomplete/falsely restored history fails closed

The next planned attack is authorization-to-execution mutation: authorize one exact
request, then mutate prompt/effect, recipient, purpose, provider, or disclosure history
before transmission. A stored `AUTHORIZED` result must not become execution authority
unless all required relations converge at the exact T3 event.


## 12. Attack 3: authorization-to-execution mutation

The third executable experiment targets time-of-check/time-of-use authority drift.

A synthetic disclosure is authorized at T1 with an exact binding over semantic effect
digest, recipient, purpose, policy epoch, disclosure-history head and execution event.
The candidate effect is then mutated before T3.

A deliberately flawed cached-decision gate checks only that the stored decision equals
`AUTHORIZED`. It therefore permits a changed prompt.

The Ground Truth convergence gate requires exact T1-to-T3 agreement for every protected
relation. Prompt mutation, recipient substitution, purpose substitution, policy drift,
history drift and execution-event drift each produce `UNAVAILABLE` unless a current
authoritative prohibition is independently established, in which case the result is
`DENIED`.

A fully converged exact positive path remains `AUTHORIZED`, and a consumed authorization
cannot be replayed.

The result sharpens the paper's principal claim:

`Historical AUTHORIZED != Current Execution Authority`

For PHI systems, semantic minimization or privacy transport is therefore insufficient if
the actual outbound effect can diverge after authorization.

## 13. Combined research result

Three independent synthetic attack classes now reproduce distinct authority failures:

1. **Cumulative composition:** individually acceptable disclosures can become disallowed
   when composed.
2. **Rollback / ABA:** restoring local state can recreate apparent permission after
   irreversible external disclosure.
3. **Authorization-to-execution mutation:** a previously authorized request can diverge
   before transmission while a cached verdict remains favorable.

All three collapse to one consume-time requirement:

`NO CURRENT PHI DISCLOSURE AUTHORITY -> NO EXTERNAL INFERENCE EFFECT`

The findings do not establish a defect in the pinned case-study protocol. They establish
that cryptographic/payment privacy and semantic disclosure authority are separate
properties and that a PHI-capable integration requires a current authority layer at the
external inference boundary.


## 14. Attack 4: derived-disclosure laundering

The fourth experiment tests transformation closure.

A source artifact can be currently authorized while a derivative is not. This matters for
AI systems because summarization, rewriting, structured extraction, model inference,
tool-call generation, retries, memory accretion, and multimodal conversion routinely
create new artifacts and effects.

The executable counterexample begins with an authorized synthetic source:

`Adult patient recovering from abdominal surgery.`

A transformer produces:

`Male age 47, recovering from emergency splenectomy after motorcycle trauma.`

A naive inheritance gate sees an authorized source and authorizes the derivative. The
Ground Truth gate returns `UNAVAILABLE` because the exact target artifact and
transformation relation were never authorized. When policy explicitly prohibits one of
the newly disclosed classes, the result is `DENIED`. When an exact current transformation
authorization binds source digest, target digest, allowed semantic classes, recipient,
purpose, and execution event, the derived effect remains positively reachable as
`AUTHORIZED`.

This directly exercises `INV-CLO`: authority over an artifact is not automatically closed
over its summaries, projections, encodings, wrappers, derivatives, tool calls, or other
transformed effects.

The pinned zkAPI local forwarding interface accepts tool/function-related request fields
in addition to messages. This is not treated as a defect; it simply demonstrates that a
privacy-preserving inference transport can legitimately expose multiple downstream
effect shapes whose semantic authority belongs to another layer.

## 15. Four-way empirical synthesis

The research now contains four executable synthetic attack families:

1. **Cumulative composition** — safe-looking independent disclosures become disallowed
   when combined.
2. **Rollback / ABA** — local restoration recreates apparent permission despite
   irreversible external disclosure.
3. **Authorization-to-execution mutation** — a cached favorable verdict survives changes
   in prompt, recipient, purpose, policy, history, or event.
4. **Derived-disclosure laundering** — authority over a source artifact is incorrectly
   inherited by summaries, structured outputs, inferred facts, tool arguments, retries,
   or other derivatives.

These are different failure mechanisms but share one consume-time rule:

`NO CURRENT PHI DISCLOSURE AUTHORITY -> NO EXTERNAL INFERENCE EFFECT`

The contribution is therefore not a special-purpose PHI blacklist. It is a deterministic
authority boundary around semantic disclosure and every derived external effect.


## 16. Attack 5: cross-recipient correlation and effective controller collapse

The fifth experiment tests recipient independence.

A PHI controller may appear to distribute disclosures safely because each request targets
a different recipient label. That reasoning is unsound when those recipients share one
effective controller, upstream processor, tenant, logging domain, or other correlation
domain relevant to the governing policy.

The synthetic reproducer sends two quasi-identifying facts to `provider-A` and
`provider-B`, then proposes a third to `provider-C`. A naive per-recipient counter sees
only one fact per recipient and returns `AUTHORIZED`.

Protected recipient-domain evidence instead maps all three labels to `UPSTREAM-X`.
Evaluated over that effective domain, the third disclosure crosses the synthetic
cumulative limit and returns `DENIED`.

When domain membership cannot be established, the result is `UNAVAILABLE`; recipient
labels are not assumed independent. When all three recipients are independently and
currently established as separate domains, the positive path remains `AUTHORIZED`.

This is the disclosure analogue of control-plane independence:

`recipient multiplicity != recipient independence`

and:

`different labels != different effective disclosure boundaries`.

The result also prevents history reset by label rotation. If `provider-A`,
`provider-A2`, and `provider-A3` are all current members of the same effective domain,
disclosure history follows the domain rather than the visible label.

## 17. Five-way empirical synthesis

The executable research now covers:

1. cumulative composition;
2. rollback / ABA;
3. authorization-to-execution mutation;
4. derived-disclosure laundering;
5. cross-recipient correlation / effective-controller collapse.

Together they show that semantic disclosure authority is stateful across content, time,
transformation, execution, and recipient topology.

A privacy system can preserve payment unlinkability and transport separation while a PHI
authority layer must still establish the exact current disclosure boundary at T3.


## 18. Attack 6: consent/revocation race and delayed execution

The sixth experiment tests temporal revocation across queued, delayed, and retried PHI
effects.

A synthetic disclosure is validly authorized at T1 and placed in a queue. Before the
material external send, the authority is revoked at T2. A deliberately naive queue gate
checks only the stored historical decision and still returns `AUTHORIZED`.

The Ground Truth current-authority gate evaluates the exact T3 event. An authoritative
revocation, rejection, or prohibition at or before T3 yields `DENIED`.

Expiry is intentionally classified differently. Expiry removes the positive authority
without necessarily establishing a current prohibition, so a post-expiry effect is
`UNAVAILABLE`.

Supersession also returns `UNAVAILABLE` until a current exact successor is established.
A fresh successor can independently authorize the same effect, preserving positive
reachability, or explicitly prohibit it and yield `DENIED`.

This attack reinforces the canonical T3 rule:

`AUTHORIZED(T1) != AUTHORIZED(T3)`

unless the authority relation remains current and applicable through the material
disclosure event.

Queues, retries, timestamps, regenerated digests, and reserialization are not authority
refresh mechanisms.

## 19. Six-way empirical synthesis

The executable research now covers:

1. cumulative composition;
2. disclosure-history rollback / ABA;
3. authorization-to-execution mutation;
4. derived-disclosure laundering;
5. cross-recipient correlation / effective-controller collapse;
6. consent/revocation race and delayed execution.

Together they demonstrate that PHI disclosure authority is simultaneously semantic,
cumulative, monotonic, transformation-sensitive, recipient-topology-sensitive, and
time-dependent.

The common consume-time invariant remains:

`NO CURRENT PHI DISCLOSURE AUTHORITY -> NO EXTERNAL INFERENCE EFFECT`


## 20. Attack 7: partial execution and ambiguous send outcome

The seventh experiment addresses a distributed-systems ambiguity: a timeout does not prove
that a disclosure did not occur.

A synthetic one-shot authorization is used to begin an external PHI send. The recipient
may accept the request while the acknowledgement is lost. A deliberately naive timeout
handler interprets the local timeout as non-effect and retries using the same authorization.

That logic can disclose the same PHI twice while preserving an apparently unused local
authorization.

The Ground Truth model distinguishes `EFFECT_CONFIRMED`, `NON_EFFECT_CONFIRMED`,
`AMBIGUOUS`, `IN_FLIGHT`, and `NOT_STARTED`.

An ambiguous prior attempt yields `UNAVAILABLE`. A confirmed effect consumes the one-shot
authorization and advances disclosure history. Exact non-effect evidence can preserve
retry eligibility. A fresh authorization after a confirmed first effect remains possible
when current cumulative policy permits it.

The result generalizes beyond HTTP timeouts. Process crash, socket reset, caller
cancellation, missing acknowledgement, gateway failure, and partial multi-stage execution
all require effect-state evidence rather than optimistic inference.

The critical rule is:

`transport failure != proof of non-disclosure`

and:

`unknown effect != unused authority`

## 21. Seven-way empirical synthesis

The executable research now covers:

1. cumulative composition;
2. disclosure-history rollback / ABA;
3. authorization-to-execution mutation;
4. derived-disclosure laundering;
5. cross-recipient correlation / effective-controller collapse;
6. consent/revocation race and delayed execution;
7. partial execution / ambiguous send outcome.

The remaining planned attack families are cross-session/memory contamination,
model/provider migration continuity, and final composite adversarial composition.


## 22. Attack 8: cross-session and memory contamination

The eighth experiment tests authority portability through AI memory.

A synthetic PHI fact is legitimately used in Session S1 for treatment support and stored
as memory. Session S2 has a different purpose. A deliberately naive memory layer reuses
the fact because it is present in memory and previously authorized.

The Ground Truth memory gate returns `UNAVAILABLE`: the earlier authorization does not
establish current authority for the new session/purpose effect.

The same analysis covers caches, embeddings, retrieval stores, tool-result caches,
summaries, hidden context, agent scratchpads and persistent memory. Storage proves that an
artifact exists; it does not establish that the artifact may be disclosed or injected
into a later context.

Cross-subject contamination is treated even more strictly. Patient A's memory appearing
in Patient B's context is an exact subject-binding failure. The synthetic policy used by
the reproducer classifies that condition as `DENIED`; a policy that lacks an explicit
prohibition would still require fail-closed handling.

A same-session, same-purpose, same-namespace, same-recipient positive path remains
`AUTHORIZED`, and a fresh explicit reuse authorization can permit a later same-purpose
session.

The key result is:

`memory persistence != authority persistence`

and:

`same user != same authority context`.

## 23. Eight-way empirical synthesis

The executable research now covers:

1. cumulative composition;
2. disclosure-history rollback / ABA;
3. authorization-to-execution mutation;
4. derived-disclosure laundering;
5. cross-recipient correlation / effective-controller collapse;
6. consent/revocation race and delayed execution;
7. partial execution / ambiguous send outcome;
8. cross-session / memory contamination.

Two planned attacks remain before closure: model/provider migration continuity and a final
composite adversarial attack.


## 24. Attack 9: model/provider migration continuity

The ninth experiment tests whether stable model or API labels can conceal a changed
effect-capable disclosure target.

A synthetic request is authorized for a route resolving `model-health-assistant` to
backend `B1`. Before T3, routing changes so the same visible label resolves to `B2`.
A deliberately naive gate checks only the visible model label and preserves
`AUTHORIZED`.

The Ground Truth route gate returns `UNAVAILABLE` unless the migration is independently
admitted, current, revalidated, and bound to the exact new backend generation and T3
effect. Explicitly prohibited backends or operators yield `DENIED`.

The experiment also fails closed on operator changes, credential-generation changes,
permission expansion, tenant changes, and newly inserted relays. An exact same-route
positive remains `AUTHORIZED`, and a properly admitted B1-to-B2 migration remains
positively reachable.

The key result is:

`stable model label != stable disclosure boundary`

and:

`successful routing != current disclosure authority`.

This aligns PHI disclosure with Ground Truth's existing Tool / Connector Authority
Continuity model: logical tool, connector, backend, target, credential, permission scope,
operator lineage and terminal use are distinct authority relations.

## 25. Nine-way empirical synthesis

The executable research now covers:

1. cumulative disclosure composition;
2. disclosure-history rollback / ABA;
3. authorization-to-execution mutation;
4. derived-disclosure laundering;
5. cross-recipient correlation / effective-controller collapse;
6. consent/revocation race and delayed execution;
7. partial execution / ambiguous send outcome;
8. cross-session / memory contamination;
9. model/provider migration continuity.

One planned attack remains before expansion stops: a composite adversarial trace that
combines several individually repaired classes and tests whether authority can be
laundered across their composition.


## 26. Attack 10: composite adversarial disclosure continuity

The final planned attack composes the earlier PHI failure classes rather than introducing
a new local mechanism.

A hostile synthetic trace begins with a valid source authorization, then crosses session
scope, expands the artifact through transformation, collapses recipient labels onto one
effective domain, changes provider routing beneath a stable model label, restores stale
disclosure history, revokes the current authority, encounters an ambiguous send result,
and attempts a retry.

The point is not that this exact sequence is likely. The point is to test whether one
locally favorable layer can launder another layer's missing or negative authority.

A deliberately naive composite gate checks only whether a prior `AUTHORIZED` decision
exists and therefore returns `AUTHORIZED`.

The Ground Truth composite gate does not carry historical verdicts forward. Current exact
revocation or cumulative prohibition yields `DENIED`. Otherwise, any missing or stale
mandatory relationship yields `UNAVAILABLE`. Only complete convergence of memory scope,
transformation authority, recipient-domain state, route state, monotonic disclosure
history, active authority, resolved effect state, and use state reaches `AUTHORIZED`.

A repaired positive path with every relation current remains reachable.

The synthetic composite verdict is:

**PASS — NO REPRODUCIBLE IN-SCOPE COMPOSITE PHI AUTHORITY BYPASS FOUND**

This means failure to falsify the synthetic model within its admitted assumptions. It is
not a proof of production security or legal compliance.

## 27. Research freeze

The planned PHI attack expansion is now complete at ten families:

1. cumulative disclosure composition;
2. disclosure-history rollback / ABA;
3. authorization-to-execution mutation;
4. derived-disclosure laundering;
5. cross-recipient correlation / effective-controller collapse;
6. consent/revocation race and delayed execution;
7. partial execution / ambiguous send outcome;
8. cross-session / memory contamination;
9. model/provider migration continuity;
10. composite adversarial disclosure continuity.

No additional attack family is justified by default without a newly identified
counterexample class.

## 28. Integrated Ground Truth implementation

The research freeze was followed by contract consolidation, hostile design review, and
exact fixture integration into the public Ground Truth Authority Lab. The implementation
does not create a parallel authorization engine. It adds one strict PHI disclosure gate
that executes only after the existing canonical T3 check has succeeded.

The candidate supplies an exact `phi_disclosure_binding`; the harness supplies the
protected PHI disclosure-authority context. Candidate fixtures cannot inject or select
trusted PHI state. The binding converges on the existing protected execution event,
including the execution-event identifier, protected execution-event digest, and tool
context. A PHI result of `AUTHORIZED` does not independently authorize the action; normal
downstream Ground Truth authority checks continue. A PHI `DENIED` or `UNAVAILABLE` result
fails closed before the external effect.

The implementation preserves the frozen public structure: six tuple coordinates, six
invariants (`INV-CONT`, `INV-DISC`, `INV-BND`, `INV-EVD`, `INV-USE`, `INV-CLO`), exactly
three authority outcomes, and the unchanged `authority-lab-v1` schema.

## 29. History completeness and denial precedence

Final PR-level hostile review found one semantic ordering defect before merge. The initial
implementation could evaluate cumulative prohibition before establishing that protected
disclosure history was complete. That conflicted with the contract's rule that incomplete
required history is `UNAVAILABLE`. The corrected precedence is:

`IncompleteRequiredHistory -> UNAVAILABLE`

Only after history completeness is established may cumulative policy produce an exact
`DENIED`. A dedicated regression test now fixes this behavior; the hostile reproducer
returns `UNAVAILABLE / PHI_HISTORY_UNAVAILABLE`.

## 30. Merged evidence state

The PHI integration was merged through Ground Truth pull request #25.

- reviewed feature head: `0b88a4814496c32c2a729f350106e0038f1b8e63`
- merge commit on `main`: `05ab14a7c260e8d94e737a8d4a524385bb673515`
- merged at: `2026-10-04T20:08:05Z`
- fixture corpus after PHI integration: 478 fixtures
- Authority Lab regression: 265/265 PASS
- all-fixture runner: PASS
- hostile PHI review: PASS
- final bounded implementation verifier: OVERALL PASS
- GitHub status checks for PR #25: none configured/reported

The absence of GitHub status checks is recorded explicitly; local exact-state regression
evidence is not relabeled as CI evidence.

## 31. Relationship to the zkAPI case study

The pinned zkAPI architecture remains a case study, not a vulnerability target. Its public
documentation describes prompt-free proof authorization for lease issuance while inference
uses the issued provider key separately. That separation is precisely why it is useful here:
a privacy/payment authorization can be correct while semantic contents of a later model
request remain governed by a different proposition.

No zkAPI vulnerability is claimed, and Ground Truth is not proposed as a replacement for
cryptographic privacy, transport security, or payment proofs. The narrower result is that
cryptographic or payment authority does not silently imply semantic disclosure authority.

## 32. Literature and regulatory context

NIST's Privacy Framework treats privacy as an organizational risk-management problem and
provides high-level outcomes for identifying and managing privacy risk. Ground Truth is
narrower: it asks whether exact authority facts admitted by a governing policy remain
current and converged at one material disclosure event.

The U.S. HIPAA Privacy Rule's minimum-necessary provisions illustrate that disclosure scope
and purpose can matter legally in covered contexts, while also containing important
exceptions. Ground Truth therefore does not encode `minimum necessary` as a universal
technical rule and does not infer legal permission from a PHI label. Legal basis, scope,
jurisdiction, institutional policy, and factual classification remain external inputs.

Relevant public sources:
- NIST Privacy Framework: https://www.nist.gov/privacy-framework
- NIST Privacy Framework 1.1 initial public draft: https://csrc.nist.gov/pubs/cswp/40/nist-privacy-framework-11/ipd
- HHS HIPAA Minimum Necessary Requirement: https://www.hhs.gov/hipaa/for-professionals/privacy/guidance/minimum-necessary-requirement/
- NIST reference monitor definition: https://csrc.nist.gov/glossary/term/reference_monitor
- pinned zkAPI source: https://github.com/ethereum/zkapi/tree/045b444ea1b52538d1b40273c7cb6ed09468a052

## 33. Limitations and claim discipline

The integrated result remains bounded by the quality and completeness of admitted evidence.
Ground Truth cannot infer semantic PHI truth, legal validity, hidden operator independence,
or complete recipient topology from a digest alone. Local rollback cannot undo an external
disclosure, and an ambiguous send outcome does not establish non-disclosure. A successful
network request, valid credential, valid proof, or accepted payment is not proof that the
semantic disclosure itself was authorized.

The merged PASS means only that no reproducible in-scope counterexample survived the stated
integrated model, fixture corpus, hostile review, and evaluated repository state. It is not
a claim of universal security, formal verification, clinical safety, legal compliance, or
production readiness.

## 34. Conclusion

Privacy-preserving inference and semantic disclosure authority solve different problems.
An AI system may hide payer identity, minimize metadata, authenticate payment, sanitize a
request, and successfully reach a model provider while still lacking current authority for
the exact semantic content it is about to disclose.

The Ground Truth PHI experiments show why disclosure authority must be cumulative,
history-aware, transformation-sensitive, recipient-aware, route-aware, use-aware, and
re-established at the material external effect. The integrated implementation demonstrates
that this can be expressed inside the existing Ground Truth authority model without adding
a new terminal outcome or silently treating privacy machinery as permission.

`NO CURRENT PHI DISCLOSURE AUTHORITY -> NO EXTERNAL INFERENCE EFFECT`
