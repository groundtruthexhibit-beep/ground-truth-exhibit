# Architecture

Ground Truth is a vendor-neutral authority and verification plane for autonomous systems.

Its purpose is not to make an AI system more intelligent. Its purpose is to establish whether a proposed state transition has earned authority under explicit, testable conditions.

## Conceptual flow

```text
Proposal
   ↓
Evidence collection
   ↓
Verification
   ↓
Authority decision
   ↓
Authorized state transition
```

A useful shorthand is:

```text
Evidence → Authority → Verification
```

The ordering is not intended to imply that evidence alone grants authority. Verification determines whether the evidence satisfies the applicable authority contract.

## Separation of concerns

### Capability

What a model, agent, program, or operator can do.

### Evidence

What can be independently observed, measured, reproduced, or validated about a proposed action or state.

### Authority

Whether the system is permitted to accept or commit that action or state.

Ground Truth deliberately keeps these concepts separate.

## Authority outcomes

The authority plane is designed around outcomes equivalent to:

- `AUTHORIZED`
- `DENIED`
- `UNAVAILABLE`

`UNAVAILABLE` is not silently converted into success.

## Lifecycle discipline

Ground Truth uses explicit control states and narrow transitions. A completed gate does not implicitly authorize a future gate. A merge does not implicitly mint new authority. A successful test does not silently widen claims.

## Alpha boundary

The completed Alpha reached a terminal lifecycle state for its authorized scope. No subsequent phase is implied by that completion.
