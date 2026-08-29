# Disclosure Boundary

[Overview](README.md) · [Architecture](ARCHITECTURE.md) · [Security model](SECURITY_MODEL.md) · [Evidence model](EVIDENCE_MODEL.md) · [Alpha completion](ALPHA_COMPLETION.md)

This repository is intentionally narrower than the private Ground Truth engineering repository.

## Suitable for public disclosure

The public exhibit may include:

- project thesis and terminology;
- high-level authority architecture;
- threat-model categories;
- lifecycle concepts;
- evidence philosophy;
- demonstrated properties stated at their earned scope;
- explicit limitations and non-claims;
- public diagrams and explanatory material.

## Kept private by default

The following are not published automatically:

- authority-store migrations;
- guarded canonicalizer implementation;
- phase-gate validator implementation;
- exact enforcement routing;
- adversarial fixtures and hidden negative-case mechanics;
- operational scripts;
- deployment-specific authority mechanisms;
- secrets, credentials, keys, endpoints, or environment data;
- unpublished future-phase implementation;
- private repository history.

## Publication rule

Public disclosure is a deliberate export, not a mirror.

Every proposed public artifact should be reviewed for claim accuracy, provenance, security impact, and accidental leakage before publication.
