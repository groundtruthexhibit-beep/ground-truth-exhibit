# Architecture

[Overview](README.md) · [Security model](SECURITY_MODEL.md) · [Evidence model](EVIDENCE_MODEL.md) · [Alpha completion](ALPHA_COMPLETION.md) · [Disclosure boundary](DISCLOSURE_BOUNDARY.md)

Ground Truth is a vendor-neutral authority and verification plane for autonomous systems.

Its purpose is not to make an AI system more intelligent. Its purpose is to establish whether a proposed state transition has earned authority under explicit, testable conditions.

## Conceptual flow

```text
Proposal
   ↓
Evidence collection
   ↓
T1 — evaluation: AUTHORIZED | DENIED | UNAVAILABLE
   ↓ only if T1 is AUTHORIZED
T2 — non-authoritative preparation
   ↓
T3 — commit-time authority establishment at the irreversible boundary
   ↓ only if current AUTHORIZED remains established
Exact authority-consuming transition
```

A useful shorthand is:

```text
Evidence → Verification → Authority
```

The ordering is not intended to imply that evidence alone grants authority. Verification determines whether the evidence satisfies the applicable authority contract. A T1 `AUTHORIZED` result is necessary but not sufficient for T3. T2 preparation does not publish, apply, transfer, spend, actuate, expose, or otherwise make an effect authoritative. Immediately before and at T3, the exact applicable tuple, boundary, evidence relationship, authority-relevant state, and consumption eligibility required by the applicable contract must remain established. If a required fact cannot be established, the result is `UNAVAILABLE`. If the applicable boundary and tuple are established and an established condition prohibits the transition, the result is `DENIED`. Only current `AUTHORIZED` at the applicable irreversible boundary permits the exact authority-consuming transition.

## Separation of concerns

### Capability

What a model, agent, program, or operator can do.

### Evidence

Information that can be observed, measured, reproduced, or validated about a proposed action or state. Where independence matters to an applicable contract, causal, provenance, control, and authority independence must be established rather than inferred from multiplicity. Evidence remains evidence; it does not issue authority.

### Authority

Whether the system is permitted to accept or commit that action or state.

Ground Truth deliberately keeps these concepts separate.

## Authority outcomes

The authority plane uses exactly these authority outcomes:

- `AUTHORIZED`
- `DENIED`
- `UNAVAILABLE`

`UNAVAILABLE` is not silently converted into success.

`AUTHORIZED`: The applicable boundary, exact tuple, and every authority-relevant condition required by the applicable contract are established, and the contract permits the exact requested authority-consuming transition.

`DENIED`: The applicable boundary and exact tuple are established, and an established applicable condition prohibits the requested transition.

`UNAVAILABLE`: A fact required to establish the applicable boundary, exact tuple, authority-relevant state, continuity, evidence relationship, freshness, consumption state, or decision cannot be established.

All outcomes preserve the separation between a decision and execution. `DENIED` and `UNAVAILABLE` result in no authority-consuming transition; uncertainty does not degrade into permission.

## Lifecycle discipline

Ground Truth uses explicit control states and narrow transitions. A completed gate does not implicitly authorize a future gate. A merge does not implicitly mint new authority. A successful test does not silently widen claims.

## Alpha boundary

The completed Alpha reached a terminal lifecycle state for its authorized scope. No subsequent phase is implied by that completion.
