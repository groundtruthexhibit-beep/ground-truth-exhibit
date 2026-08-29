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

## Independent verification

Agreement among multiple systems is useful only when their evidence is meaningfully independent. Numerical agreement alone does not prove independence.

## Alpha evidence posture

The completed Alpha includes adversarial and reproducible validation of the authorized scope. This public repository exposes the evidence model and earned claims at a high level while keeping private fixtures, internal enforcement logic, and sensitive operational details out of the exhibit.
