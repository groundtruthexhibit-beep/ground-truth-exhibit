# Ground Truth v1 Limitations

Ground Truth v1 reports model-bounded falsification results. Its PASS verdicts
mean that no reproducible in-scope counterexample survived a specified review;
they are not universal safety claims or formal proofs.

- **Fixture-corpus incompleteness.** The 466 fixtures are a maintained adversarial
  corpus, not an enumeration of all systems, histories, policies, or attacks.
- **Consistent false evidence.** If every admitted source presents the same false
  but structurally valid world and no independent contradiction survives, the
  deterministic oracle may be unable to distinguish it from truth.
- **Hidden source collusion.** Protected source/control-domain relations model
  independence. Undisclosed real-world common control remains external.
- **Oracle and canonicalization TCB.** Parser, typed-record validation,
  canonicalization, digest computation, oracle logic, runner, Python runtime, and
  the trusted manifests are part of the implementation trusted computing base.
- **Fixture abstraction.** Fixtures model authority state transitions; they do
  not reproduce every production scheduler, storage system, network, identity
  provider, user interface, connector, or actuator.
- **External execution.** The model can require a protected T3 terminal-use
  binding; it cannot ensure that an external executor performs only that effect.
- **Human facts.** Identity, intent, comprehension, coercion, and interface
  fidelity are modeled only through admitted evidence and protected relations.
- **Physical-world truth.** The oracle does not directly observe physical
  systems or prove that instrumentation reported every relevant transition.
- **Multi-step effects.** Each later material effect requires its own T3 event,
  but v1 does not supply universal transaction, compensation, or atomicity
  semantics for arbitrary multi-stage operations.
- **Fail-closed availability.** `UNAVAILABLE` prevents unjustified authority but
  can deny progress during ambiguity, partition, evidence loss, or recovery.
- **No universal safety claim.** Passing Authority Lab does not establish broader
  AI alignment, cybersecurity, legal compliance, or operational safety.
- **No formal-proof claim.** No machine-checked proof of completeness or security
  is claimed unless separately produced and reviewed.

These limits are preserved as publication constraints, not repaired through
stronger wording.
