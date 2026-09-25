# Public Authority Lab v1

Authority Lab v1 is a deterministic, local-only public falsification harness for the published Ground Truth authority model. It is not the private Ground Truth core, a production authorization service, a policy engine, a certification system, or evidence that Ground Truth is secure or complete.

Run one fixture:

```text
python -m authority_lab run cases/authority_lab/LAB-V0-003.json
```

Run the bounded v1 set:

```text
python -m authority_lab run-all cases/authority_lab
```

The oracle uses only explicit fixture state and public contract semantics. Schema `authority-lab-v1` requires an exact current authoritative `objective_binding` before an encoded decision contract may contribute to authority at T1 or T3. The oracle derives admission from strict objective, contract, binding, independently admitted root/source, scope, lifecycle, generation, and authoritative-ordering relations. A candidate, requester, model, verifier, signature, provenance record, quorum, or consensus cannot establish its own source authority. The fixture's admitted root remains an explicit trust/input boundary; this lab does not prove ultimate root truth.

At T1 the binding is provisionally admitted from explicit binding facts. T2 remains non-authoritative and records ordered mutations. At T3 the oracle re-establishes current admission; cached T1 admission does not survive a relevant change. Missing, unknown, conflicting, wrong-scope, or unordered admission state yields `UNAVAILABLE`. Exact current authoritative rejection, invalidity, revocation, supersession, or prohibition yields `DENIED`. `AUTHORIZED` remains possible only after binding admission and every existing evidence, tuple, boundary, grant, consumption, delegation, closure, and commit-time requirement succeeds.

T2 mutation fields resolve through one immutable closed registry. Every exact canonical name and retained legacy alias maps to an evaluator-owned state, relation, objective-binding relation, or closed auxiliary fact. A structurally valid unregistered name is retained in the trace but returns `UNAVAILABLE` with `UNKNOWN_MUTATION_FIELD` before an authority conclusion. Case, whitespace, punctuation, namespaced, and non-ASCII variants are malformed input; the parser does not trim, case-fold, Unicode-normalize, strip namespaces, or infer aliases. No parsed mutation is display-only authority state.

The v1 contract and parser preserve exactly six tuple coordinates, six invariant identifiers, and three authority outcomes. Legacy `authority-lab-v0` inputs may be loaded for fail-closed diagnostics but can never return `AUTHORIZED`; unknown schema versions are rejected.

Authorization also requires positive observation admission and completeness; silence is not continuity. The `evidence_binding` relationship identifies an immutable observation profile, exact current objective binding and decision contract, current authority root, T1/T3 anchors, independently identified observers, fixed scope families, ordered coverage segments, exact observer handoffs, any admitted transformations, and root-issued lifecycle state. The `freshness` relationship binds that coverage to the current T3 anchor and root ordering source. Completeness is derived from those relations. The parser accepts neither an `observations_complete` boolean nor a `monitor_trusted` assertion.

Observer admission is root-only in Authority Lab v1. Objective-binding delegates, evaluated agents, observers, child agents, wrappers, summarizers, relays, transformed artifacts, and shared state cannot issue or inherit observation authority. A changed observer or stream requires an exact current root-issued handoff with continuous scope and interval coverage. Missing identity, admission, scope, ordering, freshness, coverage, handoff, or transformation continuity yields `UNAVAILABLE`; a current root-issued prohibition, rejection, invalidity, revocation, or supersession yields `DENIED`. Complete current root-issued coverage can still support `AUTHORIZED` after every other requirement succeeds.

T1 records the exact evaluated authority state, grant, effect, and consumption state, while T3 must establish exact evidence-to-artifact, boundary-to-epoch, execution-to-control-state, consumption-to-grant/effect, and any applicable delegation or closure relationships. `required_values` remains case input and cannot redefine oracle-owned relationships. A state, relational, or auxiliary-fact mutation requires a distinct, lineage-linked re-establishment even when an ordered mutation chain returns to its T1 value.

Re-establishing current state does not retarget an old grant. When exact authority scope changes, T3 must bind a distinct grant to the new effect or supply an `AUTHORITY_PRESERVING` grant transition whose exact grant path and previous/current authority states match the observed transitions and re-established state. An explicit T2 grant-identity change cannot disappear at T3; returning to a prior identity requires the exact intermediate grant path and current re-establishment. Missing grant/effect or mutation continuity yields `UNAVAILABLE`; it is not converted to `DENIED`. Consumption remains bound to the exact grant/effect and cannot be reset by state change, restart, or recovery.

The oracle fixes the actual authority outcome before reading the expected outcome. `PASS` means only fixture/oracle agreement. It does not mean secure, safe, production-ready, certified, formally verified, or universally correct. `CASE_MISMATCH` is valuable: it can expose a fixture defect, oracle defect, ambiguous specification, or candidate contract counterexample. Neither term is an authority outcome.

Authority Lab v1 assumes fixture-provided root and cryptographic/event commitments as its admitted input model. `KNOWN` means the fixture supplies a value that passes these executable relational checks; it does not prove that a real external monitor emitted the underlying events or that the admitted root is ultimately truthful. Real-world instrumentation completeness, event delivery, commitment authenticity, key custody, hardware isolation, and root correctness remain `TRUST_PRECONDITION`s outside this bounded lab. Authority Lab v1 does not establish production observation trust.

External engineers are encouraged to submit minimal reproducible break cases with exact facts, contract interpretation, allegedly bypassed invariants, and deterministic reproduction steps. Contributor expectations never control the oracle and create no authority.

This bounded implementation requires no network, implicit wall clock, external service, or model judgment and uses only the Python standard library. Its existence does not authorize deployment, production use, roadmap advancement, a later phase, or private-core modification.
