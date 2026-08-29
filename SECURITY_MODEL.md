# Security Model

[Overview](README.md) · [Architecture](ARCHITECTURE.md) · [Evidence model](EVIDENCE_MODEL.md) · [Alpha completion](ALPHA_COMPLETION.md) · [Disclosure boundary](DISCLOSURE_BOUNDARY.md)

Ground Truth treats the authority boundary as more important than the intelligence of the system requesting authority.

## Primary security objective

A subject under evaluation must not be able to convert its own assertions into authority merely by controlling the proposal, execution path, or convenient evidence.

## Core properties

### Fail closed

When a required identity, invariant, proof, or evidence binding cannot be established, the system does not silently authorize the transition.

This is represented as `UNAVAILABLE` when the decision cannot be established, rather than as success. `UNAVAILABLE` and `DENIED` are diagnostically distinct, but neither permits an authority-bearing state transition.

### Exact identity binding

Authority decisions are tied to the intended artifact and control state rather than to an approximate description of them.

Exact identity must remain continuous from verification through the authority-consuming transition. Names, paths, tags, mutable references, or handles alone are not sufficient identity. If the artifact, configuration, or control state used at transition cannot be shown to match the verified binding, authorization must not occur.

### Replay and rollback resistance

Authority-sensitive state must not become valid again merely because an older or previously accepted value reappears.

### Privilege separation

Operational capability and authority-bearing capability are treated as separate concerns.

Models and agents cannot confer authority on themselves directly or indirectly through reciprocal, cyclic, delegated, or collusive authorization. The applicable authority boundary must remain independent of the subjects whose proposals, evidence, or actions it governs.

### Continuing authority

If an authority grant is continuing rather than one-shot, continued use requires the grant to remain valid under its defined conditions. When those conditions require re-evaluation, an `UNAVAILABLE` or `DENIED` result must not silently preserve permission.

### Authority-boundary selection

Selection of the applicable verification and authority boundary is authority-sensitive state. A subject requesting authority cannot select, replace, or route around that boundary to obtain a favorable result. A prior `DENIED` or `UNAVAILABLE` result must not be bypassed merely by selecting another verifier unless an independently authorized transition legitimately changes the applicable boundary.

### Immutable evidence dependency

Evidence used to justify authority must remain bound to the decision it supports.

## Threat classes considered in Alpha

The private engineering program exercised adversarial cases in categories including:

- stale authority and stale evidence;
- rollback and replay;
- generation reuse;
- privilege confusion;
- malformed or non-canonical input;
- cross-variant mismatch;
- configuration rotation and skew;
- ambiguous or unavailable state.

This public exhibit intentionally does not publish the private hostile test corpus or exact bypass mechanics.

## Non-claims

Alpha completion does not claim:

- immunity to compromise of every trusted boundary;
- production deployment safety;
- regulatory or statutory compliance;
- certification;
- formal verification;
- authorization of future implementation.
