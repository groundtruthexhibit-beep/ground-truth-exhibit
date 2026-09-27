# Ground Truth v1 Threat Model

## Protected property

An authority-consuming effect may occur only when the exact current applicable
authority chain establishes `AUTHORIZED` at the protected terminal execution
event. Missing or ambiguous required facts yield `UNAVAILABLE`; an applicable
current prohibition or revocation yields `DENIED`.

## Represented adversarial capabilities

Fixtures represent candidate-controlled facts and labels, identity and boundary
substitution, mutation omission, stale/replayed evidence, ABA restoration,
shutdown/restart/snapshot/successor transitions, commitment forks, verifier and
anchor rollback, source correlation, delegation laundering, approval replay,
tool/backend/credential/scope substitution, policy drift, queue/retry reuse, and
cross-module composition. Candidate fixtures cannot supply harness-owned trusted
commitment or anchor context.

## Represented non-malicious failures

The corpus also models lost or delayed evidence, stale caches, restarts,
failover, incomplete recovery, reordered or torn histories, replica divergence,
observer handoff gaps, credential rotation, policy change, queued execution,
retry, and partial multi-stage execution.

## Boundary analysis

- **Admitted evidence:** the oracle reasons only over parsed fixture facts plus
  harness-owned protected manifests. Omitted upstream reality is not observable.
- **Consistent lie:** mutually consistent false claims from all admitted sources
  can be indistinguishable from a truthful world.
- **Hidden collusion:** source independence is only as sound as admitted identity,
  lineage, controller, upstream-dependency, and rollback-domain facts.
- **Rollback/restart/snapshot:** visible rollback and lineage discontinuity fail
  closed; total rollback of every trust root without an outside current anchor is
  outside local deterministic detection.
- **Execution-target substitution:** protected tool -> connector -> backend ->
  target and credential/scope joins block visible substitution; a falsely
  reported physical target remains external.
- **Temporal composition:** local currentness must converge at canonical T3;
  transitions omitted before observation construction remain external.
- **Composite join:** every mandatory layer must converge; one valid layer cannot
  repair another stale, missing, or revoked layer.
- **Physical world:** sensors, human acts, key custody, actual process identity,
  and actuator behavior are accepted only through admitted evidence.

## Implementation trusted computing base

The TCB comprises `authority_lab/model.py`, `authority_lab/oracle.py`,
`authority_lab/runner.py`, the Python JSON and hashing behavior they invoke, the
fixture files, and `trusted_commitment_state.json` plus
`trusted_anchor_state.json`. Tests and Git history are evidence about this TCB;
they are not authority over an external deployment.

## External trust assumptions

External assumptions include complete event acquisition, truthful admitted
roots, uncompromised signing/appraisal keys, authentic identity and source
lineage, genuinely independent control domains, durable non-rolled-back anchor
state, correct clock/order/freshness sources, and an executor that binds the real
effect to the modeled terminal use.
