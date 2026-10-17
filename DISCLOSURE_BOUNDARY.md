# Disclosure Boundary

[Overview](README.md) · [Architecture](ARCHITECTURE.md) · [Security model](SECURITY_MODEL.md) · [Evidence model](EVIDENCE_MODEL.md) · [Alpha completion](ALPHA_COMPLETION.md) · [Current platform status](CURRENT_PLATFORM_STATUS.md)

This repository is intentionally narrower than the private Ground Truth and MobiPute engineering repositories.

## Suitable for public disclosure

The public exhibit may include:

- project thesis and terminology;
- high-level authority architecture;
- high-level Ground Truth + MobiPute integration boundaries;
- threat-model categories;
- lifecycle concepts;
- evidence philosophy;
- demonstrated properties stated at their earned scope;
- bounded aggregate engineering status and test evidence;
- explicit limitations and non-claims;
- public diagrams and explanatory material.

## Kept private by default

The following are not published automatically:

- authority-store migrations;
- guarded canonicalizer implementation;
- phase-gate validator implementation;
- exact enforcement routing;
- MobiPute private runtime source;
- adversarial fixtures and hidden negative-case mechanics;
- operational scripts;
- deployment-specific authority mechanisms;
- credentials, keys, endpoints, or environment data;
- protected operational evidence;
- unpublished future-phase implementation;
- private repository history.

## Publication rule

Public disclosure is a deliberate export, not a mirror.

Every proposed public artifact should be reviewed for claim accuracy, provenance, security impact, and accidental leakage before publication. Cross-system status must preserve the distinction between research evidence, implementation evidence, physical evidence, and production readiness rather than allowing one category to stand in for another.
