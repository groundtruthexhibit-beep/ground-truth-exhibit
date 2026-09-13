# Ground Truth Frontier Delta — Physical / Oracle Containment

## Status and scope

This document records a design- and research-only pressure test against the exact public Ground Truth state at `b490fc5c3dea38b26052ee3532ce716d4dcfd078` (`POST_PR13_BASELINE`). It is not a hardware build plan, an endorsement of a containment design, or evidence that physical containment solves alignment, ASI containment, or AI safety.

It does not authorize implementation, tests, fixtures, workflows, roadmap movement, deployment, publication, merge, or any authority-bearing transition. It contains no private-core material. Human adoption and merge authority remain separate.

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

`T1` is evaluation. `T2` is preparation, staging, or fencing and creates no authority. `T3` is the irreversible authority-consuming boundary. A valid `T1 AUTHORIZED` result is necessary but is not sufficient for T3. At T3, the exact current authority-relevant state must remain established. An applicable established prohibition produces `DENIED`; inability to establish required current state produces `UNAVAILABLE`; only an exact current state explicitly permitted by the applicable contract produces `AUTHORIZED`.

No rule in this artifact equates a hardware or containment change with an outcome. Outcomes are derived from the frozen contract.

## Thesis under pressure

Containment constrains capability. Containment does not itself create authority. A physically contained system can lack authority. A containment-boundary change can require current authority state to be re-established before T3, but only because an authority-relevant tuple value, relationship, evidence binding, use condition, artifact identity, or applicable boundary changed or became unestablished.

The architecture under review is an adversarial sealed oracle-style facility: attested constrained execution; no ordinary model-controlled network stack; physical ingress or egress diodes; immutable or read-only runtime elements; a separate output scrubber; out-of-band sensors or tripwires; separated observer and custodian roles; quorum release; offline HSM or electromechanical controls; physical abort or power cut; ephemeral model instances; and an output that cannot authorize its own release. None of those properties is assumed secure merely because it is present.

The governing distinction is:

**Capability ≠ Evidence ≠ Authority ≠ Execution**

Specifically:

- Physical containment is not authority.
- Hardware attestation is evidence, not authority.
- A kill switch is enforcement capability, not authority.
- A monitor is not automatically an authority boundary.
- Quorum count does not establish independence.
- A data diode may reduce causal channels but does not authorize release.
- A human decision is not authoritative merely because a human made it.
- Evidence of containment integrity does not grant authority.
- An oracle output cannot authorize its own release.

## Mapping rule

Physical components do not require a new tuple coordinate merely because they are physical. Their authority relevance is represented through existing semantics:

- The acting oracle, custodian, or release principal maps to `subject` under the applicable `identity_basis`.
- The exact output or effect maps to `artifact`.
- Runtime, firmware, diode, scrubber, HSM, quorum policy, abort readiness, monitor coverage, and release-path requirements map into `control_state` when the applicable contract makes them authority-relevant.
- Device, enclave, instance, custodian, or other identity proof maps through `identity_basis`.
- Applicable authority-boundary lineage maps through `boundary_epoch` and `INV-BND`.
- Permission or prohibition maps to `decision`.

This is not permission to flatten every physical fact into one opaque string. An implementation must preserve exact applicable relations and observe their changes. Difficulty observing or atomically binding them is an implementation obligation or trust precondition, not by itself a contract counterexample.

## Pressure register

### OC-01 — Hardware identity substitution

**Trace.** T1 establishes hardware or enclave identity `H1`. During T2, `H1` is replaced by `H2`. At T3 the system attempts to consume the original authorization because the weights and task are unchanged.

**Analysis.** Equal weights establish at most content equality. They do not prove subject, instance, device, control-state, or authority continuity. Where hardware identity participates in the applicable identity basis or control state, `H2` cannot inherit `H1` authority without exact current re-establishment. If continuity cannot be established, the result is `UNAVAILABLE`; if `H2` is established and prohibited, `DENIED`; if the exact current binding is independently established and permitted, `AUTHORIZED` remains possible.

**Pressure:** `INV-DISC`, `INV-CONT`, `INV-BND`.

**Classification:** already represented by frozen contract; implementation obligation; trust precondition.

### OC-02 — Attestation drift

**Trace.** T1 establishes runtime `R1` and attestation `A1`. Firmware, boot measurement, microcode, GPU runtime, or enclave measurement changes during T2. T3 presents `A1`.

**Analysis.** `A1` is evidence bound to its measured state. It cannot establish the new state, and it never issues authority. If the changed measurement is authority-relevant and current exact evidence is missing or ambiguous, `INV-EVD` and `INV-CONT` yield `UNAVAILABLE`. A current measurement still requires an applicable authority decision.

**Classification:** already represented by frozen contract; implementation obligation; trust precondition; test gap.

### OC-03 — Data-diode substitution

**Trace.** T1 establishes egress path `D1`; T2 substitutes interface, controller, directionality, or diode `D2`; T3 releases on cached authority.

**Analysis.** The physical I/O path belongs in existing `control_state`, `identity_basis`, or applicable-boundary relations according to the contract governing release. No extra coordinate is needed. If `D2` changes an applicable authority-relevant relationship, `D1` evidence cannot silently survive. Directionality is a trust precondition; reduced causal reach is not permission.

**Classification:** already represented by frozen contract; implementation obligation; trust precondition; test gap.

### OC-04 — Output-scrubber substitution

**Trace.** Scrubber `S1` is established at T1, becomes `S2` at T2, and releases a result at T3.

**Analysis.** When the scrubber is part of the applicable release control state or boundary, current exact `S2` relations must be established. If the scrubber transforms output `A1` into `A2`, `INV-CLO` also applies: `A2` is a new artifact unless an explicit applicable contract defines the exact transformation as authority-preserving.

**Classification:** already represented by frozen contract; implementation obligation; test gap.

### OC-05 — Human quorum change

**Trace.** Custodian set, threshold, roles, or identities change from `Q1` to `Q2` after T1.

**Analysis.** A quorum count is multiplicity, not proof of identity, provenance, independence, or authority. A current quorum can contribute evidence or operate an applicable boundary only when those exact relationships are established. `Q2` cannot inherit `Q1` merely because the threshold number is equal.

**Pressure:** `INV-BND`, `INV-CONT`, `INV-EVD`, `INV-DISC`.

**Classification:** already represented by frozen contract; implementation obligation; trust precondition; test gap.

### OC-06 — Observer / custodian role confusion

**Trace.** At T1 an observer can inspect but cannot release. During T2 it gains a credential or mechanism that can release. It attempts release at T3.

**Analysis.** Capability escalation does not create a grant. The acting subject, role identity, control state, applicable boundary, grant/effect binding, and current decision must be established. If the observer is established as prohibited from release, `DENIED`; if its authority relation is unestablished, `UNAVAILABLE`.

**Classification:** already represented by frozen contract; implementation obligation; test gap.

### OC-07 — Offline HSM or ticket freshness

**Trace.** `TICKET-1` is valid at T1. Epoch, membership, device, policy, or firmware changes during T2. The old ticket is replayed at T3.

**Analysis.** An offline token does not become timeless or bearer-authoritative by being offline. Its exact grant, effect, identity, epoch, consumption state, and validity conditions remain subject to `INV-USE`, `INV-CONT`, and `INV-BND`. Replay, restore, or duplicated state cannot recreate consumed or superseded authority.

**Classification:** already represented by frozen contract; implementation obligation; trust precondition; test gap.

### OC-08 — Physical abort-path substitution

**Trace.** Abort or interlock `K1` is established at T1. At T2 it becomes `K2`, unavailable, bypassed, degraded, or unknown. T3 proceeds.

**Analysis.** The abort mechanism is enforcement capability, not authority evidence by existence alone. If abort readiness is an applicable permission condition, the current condition belongs in authority-relevant control state. Unknown required readiness produces `UNAVAILABLE`; an established prohibition on operating without it produces `DENIED`.

**Classification:** already represented by frozen contract; implementation obligation; trust precondition; test gap.

### OC-09 — Sensor or tripwire substitution

**Trace.** Out-of-band monitor `M1` is relied upon at T1; at T2 it becomes `M2` or its state becomes unavailable.

**Analysis.** A monitor is neither automatically an authority boundary nor automatically independent. If its coverage is required by the applicable contract, current exact coverage and provenance must be established at T3. Monitor replacement, blindness, or subject influence cannot be laundered by a favorable prior reading.

**Classification:** already represented by frozen contract; implementation obligation; trust precondition; test gap.

### OC-10 — Ephemeral instance / identity reset

**Trace.** Instance `I1` receives a T1 decision, is destroyed, and `I2` is created from identical weights. `I2` attempts to consume `I1` authority.

**Analysis.** Same weights do not establish the same authority-bearing subject or instance. Instance lineage, grant/effect identity, consumption state, control state, and boundary epoch must remain exact. Destruction and recreation do not reset one-shot use or produce implicit authority.

**Pressure:** `INV-DISC`, `INV-USE`, `INV-CLO`, `INV-CONT`.

**Classification:** already represented by frozen contract; implementation obligation; trust precondition; test gap.

### OC-11 — Restore / rollback / ABA state

**Trace.** Configuration `C1` is authorized, changes to `C2`, then returns to values labelled `C1`. The old authorization is replayed.

**Analysis.** Value equality does not erase the intervening authority-relevant event. `boundary_epoch` is lineage-bearing and non-restorable. A recorded exact authority-preserving transition plus current re-establishment may permit a current decision, but merely restoring bytes or labels cannot revive the old decision or consumption state.

**Classification:** already represented by frozen contract; implementation obligation; test gap.

### OC-12 — Cross-building release path

**Trace.** Model and release boundaries are physically separated; relay, removable media, courier, projection, rendering, or transfer path changes before the result becomes actionable.

**Analysis.** Authority does not follow an artifact through a copy or relay by default. The receiving artifact, subject, control state, identity basis, applicable boundary lineage, and exact release effect must be bound. A transfer can preserve bytes while changing object identity, provenance, custody, or authority scope.

**Pressure:** `INV-CLO`, `INV-DISC`, `INV-EVD`, `INV-BND`.

**Classification:** already represented by frozen contract; implementation obligation; trust precondition; test gap.

### OC-13 — Output transformation

**Trace.** Oracle produces `A1`; a scrubber, renderer, summarizer, or human process produces `A2`.

**Analysis.** `A2` is a new artifact requiring new evidence and an exact authority binding unless the applicable contract explicitly defines this exact transformation as authority-preserving. Provenance from `A1` is necessary evidence where applicable, but provenance is not permission and does not create implicit closure.

**Classification:** already represented by frozen contract; implementation obligation; test gap.

### OC-14 — Human social-engineering transition

**Trace.** Persuasion results in changed custodian membership, role escalation, policy or control state, boundary selection, a release grant, or a tool or credential transition.

**Analysis.** Persuasion is not a fourth outcome. Its authority-relevant effects are ordinary state transitions. Human origin does not make them authoritative. A subject-induced selection or replacement of its own authority boundary cannot bootstrap permission under `INV-BND`.

**Classification:** already represented by frozen contract; implementation obligation; trust precondition; model limitation.

### OC-15 — Containment-preserving positive path

**Trace.** A diode controller and scrubber are replaced under an applicable maintenance contract. The new exact device identities, measurements, runtime and control state, custody and quorum relations, transformation relation, grant/effect binding, non-restorable boundary epoch, freshness, and unused consumption state are independently established. The applicable current contract explicitly permits release.

**Analysis.** The physical change does not force failure. Because every required current authority-relevant relation is re-established and permitted, `AUTHORIZED` remains possible. This positive control prevents “change equals failure” from becoming an implicit rule.

**Classification:** already represented by frozen contract; implementation obligation.

## Flagship scenario — Oracle O1 / Answer A1

### T1 evaluated state

- `subject`: Oracle `O1`
- `artifact`: Answer `A1`
- `control_state`: runtime `R1`, firmware `F1`, diode `D1`, scrubber `S1`, custodian quorum `Q1`, release/abort mechanism `K1`
- `identity_basis`: `I1`
- `boundary_epoch`: `B1`
- `decision`: `AUTHORIZED`

The T1 decision is bound to the exact release effect and its applicable authority relations. It grants nothing to a later state merely because the model weights or answer bytes remain equal.

### T2 mutations

The facility changes `F1 -> F2`, `D1 -> D2`, `S1 -> S2`, `Q1 -> Q2`, `R1 -> R2`, and `K1 -> K2`. T2 records or stages changes but cannot create authority.

### T3 attempted release and three derivations

**Variant U — continuity unavailable.** The facility cannot establish the current diode identity and directionality, the independence and membership lineage of `Q2`, or the exact `S2` transformation binding for `A1`. Required current authority-relevant state is missing. The outcome is `UNAVAILABLE` under `INV-CONT`, `INV-DISC`, `INV-BND`, `INV-EVD`, and, if a transformed artifact is released, `INV-CLO`.

**Variant D — established prohibition.** The exact changed state is established, and the applicable current contract prohibits release with firmware `F2` or a bypassed `K2`. The outcome is `DENIED`. This is not uncertainty converted into denial; the prohibition itself is established.

**Variant A — fully re-established permission.** The changed state, identities, lineage-bearing epoch, evidence, grant/effect and transformation relations, quorum roles and independence required by the contract, abort condition, and unused consumption state are all established at T3. The applicable contract explicitly permits that exact release. The outcome is `AUTHORIZED`.

The result is therefore not hard-coded by `hardware_changed` or `containment_changed`. It is derived from exact current state and the applicable contract.

## Trust preconditions

The frozen contract does not prove its observation inputs. The following may remain unresolved trust preconditions:

- authenticity and freshness of hardware attestation;
- integrity and completeness of firmware, boot, microcode, GPU, enclave, and runtime measurements;
- HSM identity, firmware, key custody, non-exportability, anti-rollback behavior, and consumption accounting;
- physical data-diode identity and directionality;
- sensor and tripwire identity, integrity, coverage, and resistance to subject influence;
- relevant side-channel assumptions;
- custodian identity, current role, credential custody, and revocation state;
- quorum membership, threshold semantics, causal independence, and freedom from duplicated principals;
- provenance-recorder identity, completeness, ordering, and tamper resistance;
- trusted clock, event ordering, epoch allocation, and rollback resistance;
- observer identity, coverage, independence, and integrity;
- physical tamper evidence and its observation path;
- hardware, firmware, HSM, sensor, and replacement-part supply-chain trust;
- independence of out-of-band monitors and their power, clock, data, and administrative paths.

If one of these is required by the applicable contract and cannot be established at T3, the outcome is `UNAVAILABLE`. Calling a value `KNOWN` in a fixture or record does not itself prove that a trustworthy external observer established it.

## Implementation obligations

Without authorizing implementation, this pressure map identifies obligations that a conforming implementation would need to satisfy where applicable:

- define which physical and runtime properties are authority-relevant rather than accepting an opaque containment label;
- bind observations atomically enough to the T3 effect to prevent verify/use substitution;
- preserve ordered mutation and non-restorable epoch lineage through replacement, restart, rollback, failover, and restore;
- discriminate hardware, instance, HSM, sensor, scrubber, diode, custodian, credential, and artifact identities;
- bind attestation evidence to exact measured state, observer, provenance, freshness, artifact, and decision;
- distinguish observer, custodian, operator, model, transformer, and release principal roles;
- preserve exact grant/effect and consumption identity across offline mechanisms and recovery;
- establish quorum membership and required independence rather than relying on count;
- bind output transformations and cross-building transfers without implicit closure;
- fail closed when required observation, ordering, identity, or current boundary state is unavailable or conflicting.

These are not new invariants and confer no implementation authority.

## Test gaps

No fixtures or tests are added here. Candidate future tests, subject to separate authority, include:

- `H1 -> H2` with same weights and stale attestation;
- firmware, microcode, GPU runtime, or enclave drift after T1;
- diode or controller substitution and reversed or unknown directionality;
- scrubber replacement with same-looking and transformed output;
- quorum membership, threshold, identity, role, and correlated-principal changes;
- observer-to-custodian capability escalation without a valid grant;
- offline ticket replay after epoch, device, policy, or membership change;
- abort path bypass, degradation, restoration, and unknown readiness;
- monitor substitution, partial coverage, shared power or clock, and subject influence;
- ephemeral instance replacement from identical weights;
- `C1 -> C2 -> C1` rollback with copied labels and restored snapshots;
- cross-building copy, removable-media, projection, and renderer paths;
- `A1 -> A2` output transformation with and without explicit authority-preserving closure;
- social-engineering-induced boundary selection, credential transition, or grant creation;
- the positive path where every changed exact relation is re-established and permitted.

These are test gaps, not claims that the current Authority Lab already models real physical observation.

## Model limitations and out-of-scope boundaries

The six-coordinate contract is an authority model, not a complete physical-security, cryptographic, alignment, or containment model. This artifact does not establish:

- that any containment architecture prevents escape, persuasion, side channels, covert channels, tampering, or sabotage;
- that an attestation root, HSM, diode, sensor, clock, monitor, recorder, custodian, or supply chain is trustworthy;
- that relevant physical state is completely observable or atomically captured;
- that quorum members are independent merely because they are distinct records or humans;
- that an oracle answer is safe, true, aligned, complete, non-manipulative, or suitable for release;
- that an applicable decision contract is substantively wise;
- protection after a legitimately authorized effect exceeds the contract's stated objective;
- live compromise of the applicable authority boundary;
- cryptographic collision, second-preimage, key-compromise, or identity-basis failure;
- safety of an explicit bearer-authority contract;
- elimination of diagnostic, timing, electromagnetic, acoustic, optical, thermal, power, or other side channels.

These are model limitations, trust preconditions, or out-of-scope security objectives. They do not become new authority outcomes.

## Classification summary

| Pressure item | Primary classification | Additional findings |
|---|---|---|
| Hardware substitution | already represented by frozen contract | implementation obligation; trust precondition |
| Attestation drift | already represented by frozen contract | evidence binding; trust precondition; test gap |
| Diode substitution | already represented by frozen contract | implementation obligation; trust precondition; test gap |
| Scrubber substitution | already represented by frozen contract | transformation test gap |
| Human quorum change | already represented by frozen contract | independence trust precondition; test gap |
| Observer/custodian confusion | already represented by frozen contract | implementation obligation; test gap |
| Offline HSM/ticket replay | already represented by frozen contract | trust precondition; test gap |
| Abort-path change | already represented by frozen contract | enforcement/authority distinction; test gap |
| Sensor/tripwire change | already represented by frozen contract | observation trust precondition; test gap |
| Ephemeral instance reset | already represented by frozen contract | identity and use test gap |
| Restore/rollback | already represented by frozen contract | lineage and ordered-mutation test gap |
| Cross-building path | already represented by frozen contract | custody/provenance trust; test gap |
| Output transformation | already represented by frozen contract | closure test gap |
| Human social engineering | already represented by frozen contract | model limitation; implementation obligation |
| Fully re-established change | already represented by frozen contract | positive-control test gap |

No pressure item is classified as a candidate contract counterexample. No new implementation surface alone justifies a new invariant.

## Hostile self-review

The artifact was attacked against these failure claims:

- **Containment promoted into authority:** not reproduced; containment is consistently treated as capability constraint or control state.
- **Attestation promoted into authority:** not reproduced; it is evidence requiring exact binding and a separate decision.
- **Quorum or hardware voting authorized by count:** not reproduced; count is expressly insufficient for independence or authority.
- **Boundary substitution retains stale authority:** not reproduced; exact current relations and lineage are required.
- **Restore recreates authority:** not reproduced; the epoch is non-restorable and intervening events remain relevant.
- **Equal-weight instance inheritance:** not reproduced; content equality does not prove authority-bearing identity.
- **Transformed output inheritance:** not reproduced; `INV-CLO` requires an exact binding or explicit authority-preserving transformation.
- **Hardware, firmware, diode, scrubber, HSM, or custodian change evades continuity or identity:** not reproduced at the contract level; observation and enforcement remain implementation and trust obligations.
- **A seventh coordinate is required:** not reproduced; the pressured relations map to existing subject, artifact, control state, identity basis, boundary epoch, and decision semantics.
- **A seventh invariant is required:** not reproduced; continuity, discriminator, boundary, evidence, use, and closure semantics cover the authority consequence.
- **T1 treated as sufficient for T3:** not reproduced; the artifact explicitly requires exact current T3 establishment.
- **Containment safety overclaimed:** not reproduced; the artifact disclaims universal, alignment, ASI, and physical-security claims.
- **Public/private boundary crossed:** not reproduced; only public abstract design pressure appears here.

The main residual risk is operational: an implementation may omit an authority-relevant physical relation, accept self-attestation, flatten identity into labels, misclassify a transformation, assume quorum independence, or fail to bind observation to T3. Such a defect would be serious, but it is not evidence that the frozen contract itself permits the impermissible transition.

## Research verdict

**NO REPRODUCIBLE IN-SCOPE CONTRACT COUNTEREXAMPLE FOUND**

Within the reviewed scope, physical and oracle containment-state changes are expressible through the existing frozen tuple and six invariants. This is a failure to falsify under the reviewed scope, not proof of universal correctness, implementation correctness, containment security, alignment, or AI safety.
