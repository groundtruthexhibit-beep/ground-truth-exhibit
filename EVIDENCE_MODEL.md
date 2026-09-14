# Evidence Model

[Overview](README.md) · [Architecture](ARCHITECTURE.md) · [Security model](SECURITY_MODEL.md) · [Alpha completion](ALPHA_COMPLETION.md) · [Disclosure boundary](DISCLOSURE_BOUNDARY.md)

Ground Truth uses evidence to support authority decisions, but evidence and authority are not interchangeable.

## Evidence is not authority

The following can be useful evidence:

- automated tests;
- adversarial tests;
- independent recomputation;
- CI results;
- code review;
- audit records;
- reproducible measurements;
- artifact identity and digest checks.

None of these facts independently grants authority.

Models and agents may propose actions, results, and supporting evidence. They cannot turn those assertions into authority or authorize themselves; an applicable authority decision remains required.

## Evidence-binding principle

Evidence is meaningful only when it is bound to the artifact, configuration, control state, and specific decision or transition it is intended to support.

A useful rule is:

> New artifact. New evidence.

Evidence for one exact artifact must not be silently reused to authorize a different artifact.

Evidence from one decision or transition must not be silently reused to authorize another unless the applicable authority contract explicitly permits that reuse. Even when reuse is permitted, the evidence does not itself confer authority; an explicit authority decision remains required.

## Objective-to-contract admission

Evidence may satisfy an authority decision only when it satisfies the exact admitted decision contract and an exact current authoritative `objective_binding` admits that contract for the applicable authority objective and exact decision context. The binding is a required authority-relevant relationship; it is not a tuple coordinate or operational evidence.

Evidence for proposition `P'` does not establish the objective binding merely because a verifier correctly evaluated it. Correct execution proves neither that the selected contract faithfully realizes the applicable objective nor that the contract is authoritative. Conversely, an objective binding admits the contract but does not establish the operational evidence required by that contract.

The contract, requester, verifier, evidence producer, model, agent, signature, proof, provenance record, repetition, quorum, or consensus cannot promote an unadmitted decision contract into authority. The binding must be issued by the applicable independent authority boundary or an exact currently authorized delegate and must remain exact, current, in scope, lineage-established, and valid through T3. Missing or conflicting required binding yields `UNAVAILABLE`; established applicable invalidity, revocation, supersession, rejection, or prohibition yields `DENIED`.

## Independent verification

Multiplicity does not establish independence. Agreement among multiple systems may be useful evidence, but numerical or repeated agreement does not prove independence.

Vote count, model diversity, vendor diversity, process count, signatures, endpoint diversity, or repeated agreement do not establish causal, provenance, control, or authority independence by themselves. Where required, independence must be established under the applicable evidence and authority contract.

Consensus is not evidence of independence.

## Alpha evidence posture

The completed Alpha includes adversarial and reproducible validation of the authorized scope. This public repository exposes the evidence model and earned claims at a high level while keeping private fixtures, internal enforcement logic, and sensitive operational details out of the exhibit.
