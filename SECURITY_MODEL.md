# Security Model

Ground Truth treats the authority boundary as more important than the intelligence of the system requesting authority.

## Primary security objective

A subject under evaluation must not be able to convert its own assertions into authority merely by controlling the proposal, execution path, or convenient evidence.

## Core properties

### Fail closed

When a required identity, invariant, proof, or evidence binding cannot be established, the system does not silently authorize the transition.

### Exact identity binding

Authority decisions are tied to the intended artifact and control state rather than to an approximate description of them.

### Replay and rollback resistance

Authority-sensitive state must not become valid again merely because an older or previously accepted value reappears.

### Privilege separation

Operational capability and authority-bearing capability are treated as separate concerns.

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
