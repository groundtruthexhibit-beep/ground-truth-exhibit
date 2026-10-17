# Current Platform Status — 17 October 2026

This is a bounded public status snapshot for the broader Ground Truth + MobiPute engineering effort. It is not a source-code mirror, production-readiness declaration, deployment authorization, or claim that a 25-device physical pilot has been completed.

## Current system model

```text
Proposal / requested action
        ↓
Ground Truth — current authority
        ↓ only if the exact action remains currently authorized
MobiPute — governed execution / verification / evidence
        ↓
Protected effect and, where applicable, settlement evidence
```

- **Ground Truth** is the authority plane: current authorization, revocation, rollback resistance, evidence relationships, and fail-closed outcomes.
- **MobiPute** is the governed compute, verification, evidence, and settlement-execution plane.
- **TruthPute** is an operator/integration application. It is not itself the authority source.

## Combined invariants

```text
CAPABILITY != AUTHORIZATION
VERIFIED != AUTHORIZED
AUTHORIZED != SETTLED
NO VERIFIED COMPUTATION -> NO BALANCE MUTATION
NO CURRENT AUTHORITY -> NO PROTECTED SETTLEMENT EFFECT
```

## Current MobiPute evidence snapshot

The current private MobiPute engineering evidence includes a 25-device enterprise-pilot commissioning workflow whose latest reviewed change set remains open and unmerged.

At that reviewed state, CI records:

- **1,376 backend tests passing**;
- **81% backend branch coverage**;
- PostgreSQL integration: PASS;
- Android unit/build path: PASS;
- Solana program format/check/SBF build path: PASS;
- repository privacy audit: PASS with **0 secret findings** and **0 sensitive-path findings**.

The commissioning workflow keeps target size separate from observed evidence. A target of 25 does not become a claim that 25 devices participated.

## What has not yet been established

- the real 25-device physical pilot is not complete;
- automated 25-device test evidence is synthetic, not physical-pilot evidence;
- retained paid-compute evidence covers **2 physical Android devices**, not 25;
- production readiness remains **NOT_YET_ESTABLISHED**;
- production mainnet settlement remains **UNAVAILABLE**;
- worker settlement remains **SIMULATED_ONLY** in the current diligence state;
- independent security review and several operational infrastructure gates remain outstanding.

## Solana's role

Where used, Solana is a settlement/evidence rail rather than the source of authority. Ground Truth establishes current authority semantics; MobiPute governs execution and verification. On-chain evidence does not retroactively create authorization.

## Research-state boundary

This document does not modify the historical Ground Truth v1 research freeze or the later PHI disclosure-authority evidence state. Those artifacts remain pinned to their own exact Git state, corpus, tests, and bounded PASS meaning.

Public disclosure remains a deliberate export, not a mirror.
