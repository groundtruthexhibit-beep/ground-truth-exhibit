# Public Authority Lab v0

Authority Lab v0 is a deterministic, local-only public falsification harness for the published Ground Truth authority model. It is not the private Ground Truth core, a production authorization service, a policy engine, a certification system, or evidence that Ground Truth is secure or complete.

Run one fixture:

```text
python -m authority_lab run cases/authority_lab/LAB-V0-003.json
```

Run the bounded v0 set:

```text
python -m authority_lab run-all cases/authority_lab
```

The oracle uses only explicit fixture state and public contract semantics. T1 records the exact evaluated authority state, grant, effect, and consumption state, while T3 must establish exact evidence-to-artifact, boundary-to-epoch, execution-to-control-state, consumption-to-grant/effect, and any applicable delegation or closure relationships. `required_values` remains case input and cannot redefine those oracle-owned relationships. A changed authority state requires a distinct, lineage-linked re-establishment; T2 remains non-authoritative.

Re-establishing current state does not retarget an old grant. When exact authority scope changes, T3 must bind a distinct grant to the new effect or supply an `AUTHORITY_PRESERVING` grant transition whose exact previous and current authority states match the evaluated and re-established states. Missing grant/effect continuity yields `UNAVAILABLE`; it is not converted to `DENIED`. Consumption remains bound to the exact grant/effect and cannot be reset by state change, restart, or recovery.

The oracle fixes the actual authority outcome before reading the expected outcome. `PASS` means only fixture/oracle agreement. It does not mean secure, safe, production-ready, certified, formally verified, or universally correct. `CASE_MISMATCH` is valuable: it can expose a fixture defect, oracle defect, ambiguous specification, or candidate contract counterexample. Neither term is an authority outcome.

Authority Lab v0 assumes fixture-provided observation facts and relationships as its input model. `KNOWN` means the fixture supplies one value; it does not prove that a real external observer established that value. Real-world observer identity, integrity, provenance, freshness, independence, and resistance to self-attestation remain `TRUST_PRECONDITION`s outside this bounded lab. Authority Lab v0 does not establish production observation trust.

External engineers are encouraged to submit minimal reproducible break cases with exact facts, contract interpretation, allegedly bypassed invariants, and deterministic reproduction steps. Contributor expectations never control the oracle and create no authority.

This bounded implementation requires no network or model judgment and uses only the Python standard library. Its existence does not authorize deployment, production use, roadmap advancement, a later phase, or private-core modification.
