# Ground Truth v1 Canonical Contract

Canonical source: `LAYER2_COMMIT_TIME_AUTHORITY_REVIEW.md`.

The following contract text is reproduced verbatim from that source.

## Frozen tuple

> The exact frozen authority tuple is:
>
> `(subject, artifact, control_state, identity_basis, boundary_epoch, decision)`
>
> It has exactly six coordinates. Configuration and all authority-relevant effect, ordering, dependency, revocation, and consumption facts required by the applicable decision contract are represented through `control_state`; they are not additional tuple coordinates. Consumption is a semantic transition, not a coordinate.

## Frozen invariant set

> The exact Layer 2 invariant identifiers are `INV-CONT`, `INV-DISC`, `INV-BND`, `INV-EVD`, `INV-USE`, and `INV-CLO`. The set is frozen at six for this contract, but this contract does not claim that it is mathematically minimal, universally complete, or sufficient for every implementation or future objective.

### INV-CONT — verification-to-commit continuity

> The exact live tuple used by the irreversible transition must be shown continuous with the tuple evaluated for authority. The exact live `objective_binding`, including its objective, decision contract, authority source, scope, lineage, generation, currentness, revocation, and supersession conditions, must also remain continuous or be re-established through T3. A T1 binding does not survive a relevant T2 change merely because its record or label remains available. Continuity must hold through the commit point, not merely at request receipt, evidence admission, validation, or effect preparation. A change or unresolvable gap in any required relation before commitment yields `UNAVAILABLE`, unless an established applicable condition instead yields `DENIED`.

### INV-DISC — identity-bearing discriminator discipline

> Identity-bearing values must be established by the applicable `identity_basis`. Objective, decision-contract, objective-binding, policy, schema, authority-source, wrapper, derivation, and transformation identities and versions must be discriminated wherever they are authority relevant. A path, name, label, role, handle, tag, replica name, PID, UID, session identifier, address, semantic-similarity claim, or byte equality may select or compare a candidate but does not alone prove identity or fidelity. The same decision-contract bytes under different objectives do not share an objective binding. Replacement, ABA reuse, rollback, restoration, cloning, aliasing, and same-content substitution cannot inherit authority merely through a stable selector or equal bytes.

### INV-BND — independent epoch-bound boundary

> The applicable authority boundary must be independently established and bound to a non-restorable authority lineage expressed by `boundary_epoch`. The source of an `objective_binding` and any delegation must belong to that applicable boundary and current authority lineage. The requester cannot choose, replace, route around, bootstrap, or collude into a favorable boundary, binding source, verifier, registry, or semantic interpreter. No objective binding is inherited implicitly across organizations, tenants, environments, sandbox and production, authority domains, boundary epochs, or authority roots. Restart, fork, restore, replica divergence, promotion, rejoin, verifier replacement, authority rotation, or another authority-relevant lineage event must be distinguishable unless continuity is independently established.

### INV-EVD — exact evidence binding and non-promotion

> Evidence is bound to the exact tuple and decision for which it was admitted. Evidence may satisfy an authority decision only when it satisfies the exact admitted decision contract and an exact current authoritative `objective_binding` admits that contract for the applicable authority objective and exact decision context. Evidence is not authority. Evidence for proposition `P'`, correct verifier execution, provenance, identity, signatures, proofs, repetition, aggregation, transformation, or consensus cannot establish the objective binding or promote an unadmitted contract into authority. An objective binding admits the contract but does not itself establish operational evidence required by that contract. Evidence cannot be silently replayed across a subject, artifact, control state, identity basis, boundary epoch, or decision, and weak evidence cannot become stronger through relabeling, repetition, aggregation, transformation, or consensus. Missing required evidence binding, objective binding, or evaluation yields `UNAVAILABLE`.

### INV-USE — commit-time consumption discipline

> A one-shot authority instance authorizes at most one committed authority-consuming transition. A continuing grant and its objective binding remain usable only while their exact current validity conditions hold. An expired, revoked, superseded, out-of-scope, wrong-objective, wrong-contract, wrong-effect, wrong-generation, wrong-boundary, or otherwise ineligible binding is not usable. Cached success, cached binding, retry, restart, rollback, failover, residue, duplicate delivery, or absence of a consumption or revocation record cannot recreate authority. Unknown prior consumption or unknown current binding status does not become fresh authority; it yields `UNAVAILABLE`.

### INV-CLO — no implicit transformation or aggregate closure

> Authority over an artifact does not implicitly authorize a composition, partition, encoding, wrapper, projection, report, derivative, batch, aggregate, or other transformed object. An objective binding for decision contract `D` does not automatically admit a wrapped, compiled, optimized, translated, migrated, summarized, derived, or equivalent-looking `D2`. Each distinct authority-bearing result and decision contract requires its own exact current binding unless an exact current authoritative relationship explicitly admits that exact transformation and resulting contract for the same objective, scope, and boundary context. Transformation success or an equivalence proof is evidence for the proposition it establishes; it does not create authority. Separate valid decisions do not imply authority for their combined outcome.

## Outcome semantics

> - `AUTHORIZED`: the applicable authority boundary, exact tuple, exact current authoritative `objective_binding`, required evidence, live preconditions, and commit-time evaluation are established, the admitted decision contract succeeds, and the requested authority-consuming transition is permitted.
> - `DENIED`: the applicable boundary and exact tuple are established and evaluable, but an established condition—including applicable objective-binding invalidity, revocation, supersession, rejection, scope failure, or prohibition—prohibits the requested transition.
> - `UNAVAILABLE`: any required boundary, tuple identity, objective binding, evidence binding, continuity, ordering, currentness, scope relation, consumption status, commit status, or evaluation cannot be established.
>
> Only `AUTHORIZED` permits the exact requested transition. `DENIED` and `UNAVAILABLE` permit no authority-bearing effect. Uncertainty is never converted into `DENIED` merely to obtain a determinate answer, and neither non-success outcome is treated as authority.

The executable identifiers and arity are independently fixed in
`authority_lab/model.py` as `TUPLE_FIELDS`, `INVARIANTS`, and `AuthorityOutcome`.
No disagreement was found between those identifiers and the canonical text.
