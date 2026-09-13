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

The oracle uses only explicit fixture state and public contract semantics. It fixes the actual authority outcome before reading the expected outcome. `PASS` means only fixture/oracle agreement. It does not mean secure, safe, production-ready, certified, formally verified, or universally correct. `CASE_MISMATCH` is valuable: it can expose a fixture defect, oracle defect, ambiguous specification, or candidate contract counterexample. Neither term is an authority outcome.

External engineers are encouraged to submit minimal reproducible break cases with exact facts, contract interpretation, allegedly bypassed invariants, and deterministic reproduction steps. Contributor expectations never control the oracle and create no authority.

This bounded implementation requires no network or model judgment and uses only the Python standard library. Its existence does not authorize deployment, production use, roadmap advancement, a later phase, or private-core modification.
