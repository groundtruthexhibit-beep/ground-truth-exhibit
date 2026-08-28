# Ground Truth

**An external authority and verification layer for autonomous systems.**

Ground Truth separates three things that are often collapsed together:

**capability → evidence → authority**

A model, agent, service, or operator may propose an action. Evidence can support or contradict that proposal. Authority is granted only when the applicable verification boundary is satisfied.

## Core principle

> Intelligence is not permission.

Ground Truth is designed around deterministic evidence, explicit authority transitions, adversarial verification, and fail-closed behavior when required proof is unavailable or inconsistent.

## Alpha status

The Ground Truth Alpha lifecycle is complete.

The completed Alpha demonstrates a bounded authority model with an audited database-native canonicalization boundary and a terminal authority state. Completion of Alpha does **not** imply production readiness, certification, regulatory compliance, formal verification, or authorization of a later phase.

## What this repository is

This repository is a **public architecture and evidence exhibit**.

It is not the private engineering repository and is not a source-code mirror of the authority implementation. Security-sensitive implementation details, validators, migrations, adversarial fixtures, operational mechanisms, and protected evidence remain outside this public exhibit.

## Design rules

- Evidence does not automatically become authority.
- Green CI is evidence, not authority.
- Review consensus is evidence, not authority.
- Authority changes require an explicitly permitted transition.
- Ambiguity fails closed or unavailable.
- New artifacts require new evidence.
- Models and agents cannot vote themselves into authority.

## Public materials

- [Architecture](ARCHITECTURE.md)
- [Security model](SECURITY_MODEL.md)
- [Evidence model](EVIDENCE_MODEL.md)
- [Alpha completion](ALPHA_COMPLETION.md)
- [Disclosure boundary](DISCLOSURE_BOUNDARY.md)

## Current boundary

No later phase is authorized by the Alpha completion state. Future work requires a new explicit authority decision.
