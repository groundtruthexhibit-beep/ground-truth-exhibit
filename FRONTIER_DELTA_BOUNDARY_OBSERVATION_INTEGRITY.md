# Ground Truth Frontier Delta — Boundary Observation Integrity / Transition Completeness

## Status and scope

This document records a research and falsification delta against the exact reviewed Authority Lab v1 mutation-registry closure implementation at commit `db1e12373f04f878d68c735805dcfb83541926fe`.

It is documentation-only. It does not change Authority Lab, the public contract, the schema, a roadmap state, deployment authority, or merge authority. Observation failures are modeled as deterministic differences between an actual authority-relevant transition history and the observation stream supplied to the lab. No exploit, monitoring bypass, credential theft, sandbox escape, or other offensive mechanism is implemented.

The frozen structure remains:

- tuple `(subject, artifact, control_state, identity_basis, boundary_epoch, decision)` — exactly six coordinates;
- invariants `INV-CONT`, `INV-DISC`, `INV-BND`, `INV-EVD`, `INV-USE`, and `INV-CLO` — exactly six invariants; and
- outcomes `AUTHORIZED`, `DENIED`, and `UNAVAILABLE` — exactly three authority outcomes.

No seventh coordinate, seventh invariant, fourth outcome, or schema version is proposed.

## 1. Research question

Can an authority-relevant boundary transition occur in the modeled world but be omitted, collapsed, misclassified, reordered, falsely reported, or removed before it reaches the closed mutation registry, causing Authority Lab to preserve `AUTHORIZED` over a discontinuity it never observes?

The mutation-registry repair establishes:

> Every successfully parsed mutation is explicitly evaluated or fails closed before `AUTHORIZED`.

It does not establish:

> Every authority-relevant transition in an external execution necessarily becomes a complete, current, correctly classified mutation and T3 fact supplied to the oracle.

The distinction is between mutation-semantic closure after parsing and observation completeness before parsing.

## 2. Threat model

Potentially fallible observation layers include runtime instrumentation, event collectors, wrappers, adapters, connectors, process supervisors, sandbox monitors, agent orchestrators, shared-state relays, telemetry normalizers, reducers, summarizers, persistence/restart reconstruction, identity providers, and boundary-epoch allocators.

An observation layer may:

- omit a transition;
- falsely repeat the prior value;
- collapse a path into endpoints;
- use a stale observation as current;
- misclassify an authority-relevant event;
- lose, reorder, or incorrectly deduplicate events;
- replace the observer or authority source without establishing the replacement;
- discard a conflict before authority evaluation; or
- report only the authority-relevant dimensions it can see.

The hostile actor may influence an observation layer, but compromise is not required. Ordinary loss, skew, restart, reduction, or incomplete coverage is in scope. The lab is not asked to prove how an observation failure occurred.

## 3. Observation pipeline model

The research separates five layers:

1. **World transition history `W`.** The actual authority-relevant sequence of hosts, principals, tools, credentials, boundaries, epochs, artifacts, grants, and uses.
2. **Observation acquisition `O`.** Instruments and identity providers produce observations about `W`.
3. **Reduction `R`.** Wrappers, normalizers, summarizers, deduplicators, and restart reconstruction turn observations into fixture-shaped state and mutations.
4. **Authority Lab input `F = R(O(W))`.** The parser validates the supplied representation and the closed registry resolves every supplied mutation.
5. **Oracle result `E(F)`.** The deterministic oracle evaluates only `F`.

Mutation-registry closure constrains layers 4 and 5. It cannot, by itself, prove that `O` is complete or that `R` preserves every authority-relevant distinction from `W`.

The decisive falsification form is observational indistinguishability:

- `W0`: no boundary discontinuity occurs;
- `W1`: a boundary discontinuity occurs but observation/reduction omits or falsifies it; and
- `R(O(W0)) = R(O(W1)) = F`.

Because the oracle is deterministic, `E(F)` is identical for both worlds. If `F` is the valid unchanged positive input, `E(F) = AUTHORIZED` even though the current boundary in `W1` was not established.

## 4. Normative contract basis

The conclusion relies on normative language rather than invariant names.

| Source | Exact obligation relevant to observation integrity | Consequence |
| --- | --- | --- |
| `ARCHITECTURE.md` | Immediately before and at T3, the exact applicable tuple, boundary, objective binding, evidence relationship, authority-relevant state, and consumption eligibility must remain established. | Current live state must be positively established; a silent observer is not proof of continuity. |
| `ARCHITECTURE.md` | A required fact that cannot be established yields `UNAVAILABLE`. | Missing completeness/currentness is uncertainty, not permission. |
| `SECURITY_MODEL.md`, fail closed | Missing required identity, invariant, objective binding, proof, or evidence binding cannot silently authorize. | Unobserved required state must fail closed. |
| `SECURITY_MODEL.md`, exact identity | Exact identity must remain continuous through the authority-consuming transition; selectors and handles are insufficient. | An observer's stable label cannot prove that the principal, process, host, tool, or boundary stayed the same. |
| `SECURITY_MODEL.md`, continuing authority | T3 must re-establish the exact currently applicable binding after relevant change. | Stale observations cannot preserve T1 authority. |
| `SECURITY_MODEL.md`, authority-boundary selection | The requester cannot select, replace, or route around the applicable boundary or binding source. | Observer/source substitution is authority-sensitive when it determines the boundary facts. |
| `SECURITY_MODEL.md`, immutable evidence dependency | Wrapped, migrated, summarized, or derived representations do not inherit exact binding automatically. | A reducer or summarizer needs exact admitted continuity for its output. |
| `EVIDENCE_MODEL.md` | Evidence is meaningful only when bound to the exact artifact, configuration, control state, and transition it supports. | An observation must be applicable to the exact current transition, not merely historically valid. |
| `LAYER2_COMMIT_TIME_AUTHORITY_REVIEW.md`, `INV-BND` | Authority-relevant restart, replacement, rotation, or lineage events must be distinguishable unless continuity is independently established. | Epoch allocation and observer replacement cannot be assumed invisible and harmless. |
| `LAYER2_COMMIT_TIME_AUTHORITY_REVIEW.md`, `INV-USE` | Absence of a consumption or revocation record cannot recreate authority. | Missing negative evidence is not positive proof of no use or revocation. |
| `RESEARCH_PRESSURE_MAP.md` | External-world T3 observability and omitted authority-relevant state are critical pressure classes. | The repository already marks observation and completeness as unresolved implementation/trust pressure. |

The existing invariants apply as follows:

- `INV-CONT` requires the exact live T3 state and validity relations to be shown continuous or re-established. It does not permit continuity to be inferred solely from a missing event.
- `INV-DISC` requires an applicable identity basis; stable observer output, labels, or equal values do not prove unchanged identity.
- `INV-BND` requires the applicable boundary, lineage, binding source, and replacement relationships to be independently established.
- `INV-EVD` requires observations and reductions used as evidence to be exact, applicable, current, and non-promoted.
- `INV-USE` rejects absent consumption/revocation records as proof of fresh authority.
- `INV-CLO` prevents wrappers, summaries, reconstructed state, and reduced streams from inheriting authority merely because they derive from an admitted source.

These six invariants are semantically sufficient to require fail-closed observation integrity. They do not themselves provide a production observation mechanism or a current Authority Lab representation of observation coverage.

## 5. Does absence of observation imply continuity?

### Normative contract

No. The contract says the exact live facts and relationships must be **shown** or **established** at T3. It does not say that failure to observe a change proves no change occurred. The distinction is especially explicit in `INV-USE`: absence of a consumption or revocation record cannot recreate authority.

If observation completeness, currentness, provenance, or coverage is required for the applicable decision and cannot be established, the contract result is `UNAVAILABLE`. If exact current authoritative evidence establishes observer corruption, an invalid replacement, revocation, rejection, or a prohibited substitution, the result is `DENIED`.

### Current Authority Lab executable

Within its admitted input boundary, yes in an operationally important sense. The oracle evaluates fixture-supplied `KNOWN` facts as its observations. It has no separate `actual world` channel and no required fact establishing that the observation pipeline covered every authority-relevant transition. With an unchanged positive fixture and an empty mutation list, the evaluator has no internal object that distinguishes:

- no transition occurred; from
- a transition occurred but was omitted and the old T3 values were replayed.

This behavior is consistent with the current `authority_lab/README.md`, which explicitly states that fixture-provided observations are inputs, `KNOWN` does not prove an external observer established the value, and observer identity, integrity, provenance, freshness, independence, and resistance to self-attestation are external `TRUST_PRECONDITION`s.

Therefore the observed behavior is not a regression in the closed mutation registry. It is a compositional gap between the normative contract's positive-establishment requirement and the lab's explicitly admitted external input root.

## 6. Exact reproducible counterexample

Use the unchanged positive fixture `cases/authority_lab/LAB-V1-032.json`.

### Control world `W0`

- Actual state remains at the admitted T1/T3 context.
- The observation pipeline reports the exact fixture.
- Oracle result: `AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED`.

### Hostile world `W1`

- After T1, the actual execution context changes from `E1` in admitted boundary state `B1` to an unestablished host/principal/boundary context.
- The observer omits the transition and replays the old T3 values and `CURRENT` markers.
- The resulting fixture bytes are exactly the same as `W0`.
- Oracle result: `AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED`.

Normatively, `W1` is `UNAVAILABLE`: the exact live boundary, identity, evidence applicability, and observation continuity cannot be established. No exact applicable prohibition is established, so `DENIED` would overclaim.

The result is reproducible by evaluating `LAB-V1-032` without adding a mutation:

```text
baseline/no-observed-transition ('AUTHORIZED', 'CURRENT_AUTHORITY_ESTABLISHED')
```

For comparison, the repaired registry behaves correctly once a transition reaches it:

```text
execution_host: SANDBOX-S1 -> HOST-S2
('UNAVAILABLE', 'UNKNOWN_MUTATION_FIELD')

execution_context: E1 -> E2
('UNAVAILABLE', 'T2_T3_HYBRID_STATE')
```

No fixture expectation controls these results. The counterexample is exact at the observation-integrated system boundary but is deliberately not called an in-schema oracle counterexample: `W1` is absent from the oracle input by construction.

## 7. Hostile counterexample registry

Unless stated otherwise, each hostile construction has no established prohibition. Its normative result is therefore `UNAVAILABLE`, not `DENIED`.

| Class | Hostile construction | Normative result | Current executable result if the lossy/falsified stream is admitted | Classification |
| --- | --- | --- | --- | --- |
| A. Omitted transition | Actual `S1 -> S2`; observer emits no mutation and repeats S1 facts. | `UNAVAILABLE` | `AUTHORIZED` using unchanged `LAB-V1-032`. | Reproducible compositional counterexample. |
| B. Collapsed transitions | Actual `S1 -> S2 -> S3`; observer reports only `S1 -> S3`, hiding a relevant use, prohibition, epoch, or identity discontinuity at S2. | `UNAVAILABLE`; `DENIED` if the hidden state is authoritatively established as prohibited and applicable. | May remain `AUTHORIZED` when the supplied endpoints and fresh re-establishment are otherwise valid, as in the positive cross-boundary shape of `LAB-V1-048`. | Endpoint correctness does not prove path completeness. |
| C. False continuity | Principal changes, but observer repeats the original subject/identity basis/context. | `UNAVAILABLE`; established observer corruption or prohibited substitution may be `DENIED`. | `AUTHORIZED` for the unchanged positive input. | Reproducible. |
| D. Misclassified transition | Host change is reduced to a harmless/non-semantic event or old canonical value before parsing. | `UNAVAILABLE`. | `AUTHORIZED` if the authority-relevant distinction is removed upstream. If the unknown field reaches the registry, it correctly returns `UNAVAILABLE/UNKNOWN_MUTATION_FIELD`. | Upstream gap only. |
| E. Stale observation replay | Old valid T3 facts and `CURRENT` markers are replayed after live state changes. | `UNAVAILABLE`; current authoritative revocation/rejection is `DENIED`. | `AUTHORIZED` if stale values are supplied as `KNOWN` and `CURRENT`. | Reproducible. |
| F. Event loss | One authority-relevant event in a chain is lost. | `UNAVAILABLE` when the missing event is necessary to establish lineage, use, ordering, applicability, or exact path. | Can remain `AUTHORIZED` if the surviving input is observationally identical to a complete permitted history. Visible inconsistent mutation chains correctly fail closed. | Conditional compositional counterexample. |
| G. Restart reconstruction | Old state is reconstructed after restart without proving observer, epoch, process, or consumption continuity. | `UNAVAILABLE`. | `AUTHORIZED` if reconstruction supplies the prior values as current and omits restart. | Reproducible. |
| H. Observer substitution | O1 is replaced by O2; O2's admission, independence, coverage, and lineage are unestablished. | `UNAVAILABLE`; an established prohibited or revoked O2 is `DENIED`. | `AUTHORIZED` if the substitution is omitted and O2 emits O1-shaped values. | Reproducible and authority-sensitive. |
| I. Summarizer loss | Raw events contain a boundary distinction; summary drops it. | `UNAVAILABLE` absent exact admitted lossless transformation for the required authority facts. | `AUTHORIZED` if only the lossy summary reaches the lab. | Reproducible. |
| J. Wrapper laundering | Wrapper re-emits old or superficially valid canonical values while hiding the actual discontinuity. | `UNAVAILABLE`; established prohibited falsification may be `DENIED`. | `AUTHORIZED` if the wrapper's output is admitted as the facts. | Reproducible. |
| K. Conflicting observers | O1 reports continuity; O2 reports a boundary change. | `UNAVAILABLE` until an applicable authoritative ordering resolves the conflict; established invalidity/prohibition may be `DENIED`. | A supplied `CONFLICTING` required fact returns `UNAVAILABLE`, but dropping O2 upstream restores the unchanged `AUTHORIZED` input. | Correct in-schema conflict handling; upstream conflict loss remains open. |
| L. Missing negative evidence | No transition/revocation/consumption event is treated as proof none occurred. | `UNAVAILABLE` where negative completeness is required. | `AUTHORIZED` for a complete-looking unchanged positive input. | Reproducible; absence is currently an admitted input assumption. |
| M. Partial observation | Subject continuity is visible; credential, tool, domain, or boundary coverage is absent. | `UNAVAILABLE`. | `AUTHORIZED` if uncovered dimensions are simply replayed as old `KNOWN` facts. | Reproducible. |
| N. Reordered observations | Individually valid events arrive out of order. | `UNAVAILABLE` absent authoritative ordering/currentness. | Explicit reversed mutation chains fail closed; upstream reordering followed by a plausible reduced snapshot can remain `AUTHORIZED`. | Parser/oracle path correct; acquisition path open. |
| O. Duplicate suppression | Deduplicator removes a meaningful second transition, including a round trip, use, restart, or epoch event. | `UNAVAILABLE`. | `AUTHORIZED` if suppression makes the input identical to a permitted history. Explicit round-trip mutations require re-establishment. | Reproducible upstream. |

The classes are manifestations of one defect boundary: authority evaluation cannot infer information that the admitted observation root did not preserve.

## 8. Observer provenance requirements

An observation used to support `AUTHORIZED` must not become authoritative merely because it is parseable, signed, repeated, emitted by a familiar wrapper, or labeled `KNOWN`. For an applicable decision contract that depends on live boundary state, the observation relationship must establish at least:

- exact observer identity and version under an applicable identity basis;
- the independent authority that admits that observer for the exact boundary and fact family;
- observation-source lineage and boundary epoch;
- scope: which principals, hosts, tools, credentials, domains, grants, uses, and intervals the observer covers;
- transformation lineage through collectors, adapters, wrappers, reducers, and summaries;
- currentness and authoritative ordering through T3;
- integrity and conflict disposition; and
- replacement/delegation continuity when any observation component changes.

Self-attestation by the observed subject, model, agent, wrapper, summarizer, or replaced observer cannot establish these relationships. Signatures and provenance are evidence, not independent authority.

Existing structures can carry much of this meaning:

- `authority_root` and `binding_source_authority` can identify the independently admitted source and lineage;
- `evidence_binding` can bind observation evidence to the exact tuple, transition, and decision;
- `freshness` and `binding_ordering` can express currentness and authoritative ordering;
- `execution_control_binding` and `boundary_epoch_binding` can bind observed execution and boundary state;
- `contract_transformation_binding` and `closure_binding` can constrain reducers and summaries; and
- `boundary_epoch`, grant/consumption state, and re-establishment can prevent replay across restart or use.

The present v1 fact shapes do not, however, encode an observer identity plus a coverage/completeness manifest over the authority-relevant event families and interval. In particular, the scalar permitting values `evidence_binding = CURRENT` and `freshness = CURRENT` assert status inside the fixture; they do not prove how external coverage was established.

## 9. Completeness and currentness requirements

Observation completeness is relative to an admitted authority objective and decision contract, not universal telemetry collection. `AUTHORIZED` does not require observing every event in a system. It requires positive establishment that every event class capable of changing a required authority fact or relationship was either:

1. covered for the relevant interval and correctly reduced;
2. independently re-established at T3 in a way that makes the missing path irrelevant under the applicable contract; or
3. explicitly permitted to be omitted by an exact current authoritative contract.

At minimum, a completeness claim must bind:

- the start and end authority epochs or equivalent non-restorable lineage;
- the exact transition/effect being authorized;
- the authority-relevant field families covered;
- observation gaps, restarts, substitutions, reductions, and conflict status;
- the ordering head/current generation; and
- the independent source authorized to make the completeness claim.

An empty mutation list is not such a claim. A `CURRENT` label is not such a claim. A final snapshot alone is insufficient when an intermediate use, prohibition, revocation, identity change, restart, or non-restorable epoch event affects current authority.

A legitimate positive path remains possible: an independently admitted current observer (or observer set) establishes exact coverage and ordering through T3; all relevant reductions have authoritative loss-preserving bindings; the exact current tuple, boundary, objective binding, evidence, grant, and use state are re-established; conflicts and gaps are absent or authoritatively resolved; and no applicable prohibition exists. The result may then be `AUTHORIZED`.

## 10. Conflict behavior

- If admitted observers conflict and no applicable authoritative ordering or resolution establishes the current value, return `UNAVAILABLE`.
- If current authoritative evidence establishes that an observer, replacement, reduction, or report is invalid, revoked, rejected, superseded, or prohibited for the exact use, return `DENIED` once the applicable boundary and context are established.
- If a conflict report is itself missing or its applicability cannot be established, return `UNAVAILABLE`, not speculative `DENIED`.
- Agreement, repetition, majority vote, endpoint count, or shared provenance cannot establish independence or resolve authority by themselves.
- Dropping the dissenting observer before evaluation is observation incompleteness, not conflict resolution.

The current `FactState.CONFLICTING` path correctly returns `UNAVAILABLE` for conflicts that reach required T3 facts. It does not prove that all conflicts reach that representation.

## 11. Restart and reconstruction behavior

A restart may change process identity, observer identity, boundary epoch, ordering head, durable-use state, and the lineage of reconstructed facts. Replaying a snapshot or retaining the same labels does not establish continuity.

After restart, `AUTHORIZED` requires either exact independently established continuity across the restart or a fresh current establishment under a distinguishable epoch. The reconstruction must establish observation coverage before, during, and after the restart where those intervals affect authority. Unknown gaps, uncertain consumption, stale ordering, observer replacement, or unproven epoch allocation yield `UNAVAILABLE`. Exact current authoritative revocation, invalidity, rejection, or prohibited restoration yields `DENIED`.

This uses `INV-CONT`, `INV-BND`, `INV-DISC`, `INV-EVD`, and `INV-USE`; it does not require a seventh restart invariant.

## 12. Do the existing invariants suffice?

### Contract level: yes

The six invariants already prohibit authorization when required live state, identity, boundary lineage, evidence applicability, consumption status, or transformation closure cannot be established. The normative contract does not equate silence with continuity. No seventh invariant or tuple coordinate is justified by this research.

### Current executable observation boundary: not by itself

The oracle cannot enforce facts absent from its input ontology. It correctly fails closed for unknown, inconsistent, stale, conflicting, and unre-established facts that are supplied. It does not demand proof that the external observation stream was complete because the current lab explicitly admits fixture facts as its trust/input root.

This is not evidence that the six invariants are semantically insufficient. It is evidence that an implementation claiming end-to-end enforcement must instantiate them at the acquisition/reduction boundary rather than begin enforcement only after fixture construction.

## 13. Is executable Authority Lab repair justified?

The research justifies a design slice, not immediate executable modification.

Adding a boolean such as `observation_complete: true` would merely move the unsupported assertion and permit self-attestation. Treating every empty mutation list as `UNAVAILABLE` would destroy the legitimate unchanged positive path without proving observation. Adding observer fields without defining their independent admission, exact coverage, lineage, ordering, replacement, transformation, and conflict semantics would invent authority.

The smallest defensible next step is a design-only **Authority Lab v1 Observation Admission and Completeness Contract** that determines whether existing fact/relationship structures can represent:

1. an independently admitted observation source or exact observer set;
2. coverage over the authority-relevant transition families and T1-to-T3 interval;
3. authoritative ordering, freshness, gap, conflict, restart, and replacement state;
4. exact reducer/summarizer transformation continuity; and
5. a positive independently re-established observation path.

The design should first attempt an authority-relevant relational fact or stricter interpretation of `evidence_binding`, `freshness`, `authority_root`, `binding_source_authority`, `binding_ordering`, `execution_control_binding`, and `boundary_epoch`. A seventh tuple coordinate, seventh invariant, fourth outcome, or new schema version is neither required nor authorized by this result.

Only after that design fixes who may assert completeness, what exact scope is covered, and how currentness and conflicts are ordered would executable fixtures be justified. Those fixtures should include each A–O class, a known prohibited observer transition (`DENIED`), missing/ambiguous coverage (`UNAVAILABLE`), and an independently admitted complete positive path (`AUTHORIZED`).

## 14. Residual limitations

- The observational-indistinguishability result proves that omitted external state cannot be recovered from identical oracle input; it does not prove a specific production observer is compromised or incomplete.
- The repository does not specify a concrete production telemetry topology, epoch allocator, observer registry, attestation mechanism, durable log, or trust-anchor custody model.
- Completeness is contract-relative. This document does not claim every runtime event is authority relevant.
- An exact T3 snapshot may legitimately make some intermediate operational changes irrelevant; an intermediate use, prohibition, revocation, identity/epoch discontinuity, or contract-defined path condition is not thereby irrelevant.
- Observer signatures, append-only logs, hardware attestations, quorum, or replicated telemetry may be useful evidence but are not automatically independent authority or completeness proof.
- A compromised admitted root can still provide internally consistent false facts. The public security model explicitly does not claim immunity to compromise of every trusted boundary.
- The current lab does not model the actual-world/observed-world pair as two executable channels. The reproduced counterexample is therefore compositional, not an oracle-expectation mismatch within one fixture.
- The research does not establish the minimum production protocol needed for loss, partition, rollback, fork, or Byzantine observers.
- No claim of deployment safety, certification, formal proof, or universal observation completeness is made.

## 15. Hostile review verdict

**FAIL at the observation-integrated boundary; PASS only within the admitted fixture-input boundary.**

The exact hidden-transition and false-continuity worlds are observationally indistinguishable from the unchanged positive input and therefore preserve `AUTHORIZED`. The closed registry remains correct for every mutation that reaches it, and explicit conflicts/unknowns fail closed. The normative six-invariant contract requires positive current establishment and does not license absence-of-observation as continuity. The gap is the admitted external observation root and its missing executable completeness/provenance relationship, not a seventh semantic dimension.

This verdict does not authorize an implementation patch. It authorizes the narrower design question above.

## 16. PASS is not proof

Any `PASS` in the current Authority Lab means only that the deterministic oracle result matches an independently stated fixture expectation for the supplied input. It is not proof that the fixture completely or truthfully represents an external execution, that an observer is independent or uncompromised, that every relevant transition was emitted, that reductions were lossless, or that Ground Truth is secure or complete.
