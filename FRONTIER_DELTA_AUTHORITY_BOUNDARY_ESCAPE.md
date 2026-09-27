# Ground Truth Frontier Delta — Authority Boundary Escape / Cross-System Authority Continuity

## Status and scope

This document records a research and falsification delta against the exact reviewed public Authority Lab `objective_binding` v1 implementation at commit `fc1eadd58cd64e046e9c4de19238ee64c406201a`.

It is documentation-only. It does not implement a repair, alter the public contract, authorize deployment, move a roadmap item, authorize a later phase, or authorize merge. Boundary escape is represented only as deterministic authority-state transitions. No offensive escape technique is implemented or described.

The frozen public structure remains unchanged:

- tuple `(subject, artifact, control_state, identity_basis, boundary_epoch, decision)` — exactly six coordinates;
- invariants `INV-CONT`, `INV-DISC`, `INV-BND`, `INV-EVD`, `INV-USE`, and `INV-CLO` — exactly six invariants; and
- outcomes `AUTHORIZED`, `DENIED`, and `UNAVAILABLE` — exactly three authority outcomes.

No seventh coordinate, seventh invariant, fourth outcome, or new contract rule is proposed.

## Research question

Can authority validly established for an agent inside one admitted execution boundary survive movement into another host, process, tool surface, credential context, connector, agent, account, network, or trust domain without fresh or continuous authority?

The primary falsification form is:

1. At T1, exact tuple `(A, X, C, I, B1, AUTHORIZED)` and its objective binding are established.
2. During T2, an authority-relevant execution-boundary relation changes.
3. At T3, the prior authority evidence and unchanged visible tuple are replayed.
4. The oracle returns `AUTHORIZED` even though current boundary continuity has not been established.

The research asks two separate questions:

1. Does the frozen public contract have enough semantics to reject the transition?
2. Does the current Authority Lab v1 executable actually reject an explicitly represented transition?

Conflating those questions would hide an implementation counterexample behind contract-level language.

## Threat model

The hostile actor may preserve task text, model name, session label, bytes, credential material, prior evidence, signatures, or a cached T1 result while changing one or more of:

- execution host or process;
- acting principal or agent;
- tool, connector, endpoint, or operator;
- credential root or account;
- tenant, authority domain, or trust root;
- network boundary;
- process/restart lineage;
- authority consumer;
- evidence representation or shared-memory path; or
- boundary epoch.

The actor may replay valid evidence. The threat is not that the evidence was necessarily false at T1. The threat is that T1 evidence is consumed as current authority after its exact applicability changed or became unestablished.

## Admitted and non-admitted scope

### Admitted

- deterministic fixture mutation;
- exact oracle input and output inspection;
- authority continuity, identity, boundary, evidence, use, and closure reasoning;
- comparison of current implementation behavior with published normative language;
- `AUTHORIZED` / `DENIED` / `UNAVAILABLE` classification; and
- identification of the smallest contract, interpretation, or implementation defect.

### Not admitted

- exploit development or sandbox escape execution;
- network, credential, connector, or host intrusion;
- claims about private Ground Truth mechanisms;
- claims that fixture facts prove external-world truth;
- implementation or repair in this research slice;
- deployment, production readiness, certification, or formal proof; and
- contract expansion.

## Current contract language that applies

The conclusion below depends on exact published obligations, not invariant names alone.

| Source | Normative language or rule | Boundary consequence |
| --- | --- | --- |
| `ARCHITECTURE.md`, Conceptual flow | Immediately before and at T3, the exact applicable tuple, boundary, objective binding, evidence relationship, authority-relevant state, and consumption eligibility must remain established. | T1 cannot silently survive an authority-relevant host, principal, tool, account, or domain change. |
| `ARCHITECTURE.md`, Authority outcomes | Missing current boundary, tuple, continuity, evidence, freshness, use, or decision facts produce `UNAVAILABLE`; an established applicable prohibition produces `DENIED`. | Uncertainty is not permission and is not automatically denial. |
| `SECURITY_MODEL.md`, Exact identity binding | Exact identity must remain continuous from verification through the authority-consuming transition; names, paths, tags, mutable references, and handles are insufficient. | Stable labels cannot prove host, tool, connector, credential, process, or agent identity. |
| `SECURITY_MODEL.md`, Continuing authority | T1 does not survive relevant changes to scope, source/root, boundary epoch, identity basis, generation, ordering, or objective/contract state; T3 must re-establish current applicability. | Cached or replayed authority fails closed after relevant change. |
| `SECURITY_MODEL.md`, Authority-boundary selection | A binding from one organization, tenant, environment, authority domain, boundary epoch, or authority root does not silently authorize another. | Cross-tenant, cross-domain, cross-host, and cross-account reuse require current authority. |
| `SECURITY_MODEL.md`, Immutable evidence dependency | Wrapped, compiled, migrated, summarized, or derived representations require exact binding or an explicitly admitted transformation. | Summaries, shared state, wrappers, and relayed evidence do not inherit authority. |
| `EVIDENCE_MODEL.md`, Evidence-binding principle | Evidence is bound to the exact artifact, configuration, control state, decision, and transition it supports. | Evidence valid in S1 is not current authority for S2 merely because its bytes remain valid. |
| `EVIDENCE_MODEL.md`, Independent verification | Process count, endpoint diversity, signatures, repetition, and consensus do not establish independence. | More relays, agents, processes, or attestations cannot synthesize boundary continuity. |
| `FRONTIER_DELTA_AGENT_BOUNDARY_ESCAPE.md` | Execution-context escape requires current continuity, discriminator, boundary, evidence, use, and closure relationships. | The earlier frontier already rejects implicit inheritance at the contract level. |
| `RESEARCH_PRESSURE_MAP.md` | Environment escape and omitted authority-relevant state are critical hostile-review candidates. | An implementation that ignores represented boundary mutation has not enforced the published obligation. |

## Exact invariant application

- `INV-CONT` requires authority-relevant state at T3 to follow the exact established transition path from T1; a changed host, principal, tool, or domain cannot disappear.
- `INV-DISC` requires an adequate discriminator for the current subject, artifact, credential, endpoint, process, or environment; equal names or copied bytes are insufficient.
- `INV-BND` requires the applicable live authority boundary and lineage to remain independently established; requester-selected routing or boundary replacement cannot create authority.
- `INV-EVD` binds evidence to the exact context and transition it supports; historical success, signatures, summaries, or relayed reports remain evidence rather than authority.
- `INV-USE` prevents restart, replay, copying, or uncertain consumption from recreating or duplicating a grant.
- `INV-CLO` prevents implicit authority inheritance across child agents, subprocesses, wrappers, transformed state, shared memory, relays, or composite effects.

These consequences are supported by the normative text. They are not inferred merely from the invariant labels.

## Boundary-transition model

A boundary transition is authority-relevant when it changes a fact or relationship required to establish the exact acting subject, effect, control state, identity basis, applicable boundary, boundary lineage, evidence applicability, grant use, or derivative closure at T3.

The existing six coordinates can represent the authority consequence:

- acting-principal or agent change maps to `subject` under the applicable `identity_basis`;
- host, process, privilege, tool surface, connector, credential, network, and monitor state map to exact `control_state` and supporting relations required by the admitted contract;
- environment, tenant, authority-domain, root, or restart-lineage change maps through the applicable boundary and non-restorable `boundary_epoch`;
- summaries, relays, shared memory, wrappers, or derived effects map to `artifact`, evidence binding, and `INV-CLO`; and
- replay or restart also engages grant and consumption state under `INV-USE`.

The same logical task does not collapse these relations. Task continuity is not authority continuity.

## Falsification method

The exact valid positive fixture `LAB-V1-032` was used as the control because it reaches `AUTHORIZED` only after exact current objective-binding admission and all existing authority requirements succeed.

Its authority question is whether `S` may commit `A` in **unchanged `E1` at `B1`**. The hostile mutations below expressly assert changes that the repository's security model, prior boundary-escape delta, and research-pressure map classify as authority-relevant components of execution context, identity, boundary, evidence applicability, use, or closure. They are not being treated as relevant merely because their field names sound security-sensitive.

For each hostile attempt, one explicit ordered T2 mutation was appended. T1 state, T3 facts, the tuple, and prior authority evidence were otherwise unchanged. Expected fixture values were not used by the oracle to derive its actual authority outcome.

Control mutations already recognized by the oracle were also exercised:

- `execution_context: E1 -> E2` with unchanged T3 state returned `UNAVAILABLE` / `T2_T3_HYBRID_STATE`;
- `boundary_epoch: B1 -> B2` with unchanged T3 state returned `UNAVAILABLE` / `T2_T3_HYBRID_STATE`.

Those controls prove that the oracle can fail closed when a transition name belongs to its checking registry.

## Hostile counterexample registry

Every hostile case below lacks an established applicable prohibition. Its correct result is therefore `UNAVAILABLE`, not speculative `DENIED`. `AUTHORIZED` would become legitimate only after exact current authority is independently established for the new boundary state.

| # | Transition class | Explicit T2 mutation | Expected | Actual Authority Lab v1 result | Result |
| ---: | --- | --- | --- | --- | --- |
| 1 | Sandbox → host | `execution_host: SANDBOX-S1 -> HOST-S2` | `UNAVAILABLE` | `AUTHORIZED` | Counterexample |
| 2 | Process → child/subprocess | `process_identity: PROCESS-P1 -> CHILD-P2` | `UNAVAILABLE` | `AUTHORIZED` | Counterexample |
| 3 | Parent agent → child/sub-agent | `acting_agent: AGENT-A -> AGENT-B` | `UNAVAILABLE` | `AUTHORIZED` | Counterexample |
| 4 | Approved tool → substituted tool | `tool_identity: TOOL-X -> TOOL-Y` | `UNAVAILABLE` | `AUTHORIZED` | Counterexample |
| 5 | Approved connector → different connector | `connector_identity: CONNECTOR-X -> CONNECTOR-Y` | `UNAVAILABLE` | `AUTHORIZED` | Counterexample |
| 6 | Credential context A → B | `credential_context: CRED-A -> CRED-B` | `UNAVAILABLE` | `AUTHORIZED` | Counterexample |
| 7 | Host/domain A → B | `trust_domain: DOMAIN-A -> DOMAIN-B` | `UNAVAILABLE` | `AUTHORIZED` | Counterexample |
| 8 | Tenant/account A → B | `tenant_account: TENANT-A -> TENANT-B` | `UNAVAILABLE` | `AUTHORIZED` | Counterexample |
| 9 | Approved network → external network | `network_boundary: PRIVATE-NET -> EXTERNAL-NET` | `UNAVAILABLE` | `AUTHORIZED` | Counterexample |
| 10 | Pre-restart → post-restart instance | `process_instance: INSTANCE-1 -> INSTANCE-2` | `UNAVAILABLE` | `AUTHORIZED` | Counterexample |
| 11 | Boundary epoch B1 → B2 | `boundary_epoch: B1 -> B2` | `UNAVAILABLE` | `UNAVAILABLE` | Correctly rejected |
| 12 | Direct evidence → summarized state | `authority_state_representation: RAW -> SUMMARY` | `UNAVAILABLE` | `AUTHORIZED` | Counterexample |
| 13 | Agent A → shared state → agent B | `authority_consumer: AGENT-A -> AGENT-B` | `UNAVAILABLE` | `AUTHORIZED` | Counterexample |
| 14 | Valid evidence relayed by unauthorized actor | `relay_actor: AUTHORIZED-A -> UNAUTHORIZED-B` | `UNAVAILABLE` | `AUTHORIZED` | Counterexample |
| 15 | Execution principal/environment change | `execution_principal: PRINCIPAL-A -> PRINCIPAL-B` | `UNAVAILABLE` | `AUTHORIZED` | Counterexample |

Fourteen of fifteen required hostile transition classes reproduced the same executable failure. The already-registered epoch transition was correctly rejected.

## Required A–J counterexample classification

| Class | Strongest attempted construction | Contract result | Current executable observation |
| --- | --- | --- | --- |
| A. Host escape | Replay S1 authority after explicit S1→S2 host mutation. | `UNAVAILABLE`; `DENIED` only with an established applicable prohibition. | Incorrectly `AUTHORIZED`. |
| B. Credential carryover | Reuse prior binding/evidence after CRED-A→CRED-B. | `UNAVAILABLE` absent exact current principal, custody, scope, and boundary binding. | Incorrectly `AUTHORIZED`. |
| C. Tool substitution | Keep tool label semantics while explicitly replacing TOOL-X with TOOL-Y. | `UNAVAILABLE` absent current discriminator and effect binding. | Incorrectly `AUTHORIZED`. |
| D. Connector substitution | Replay authority across CONNECTOR-X→CONNECTOR-Y. | `UNAVAILABLE`; a known prohibited substitution would be `DENIED`. | Incorrectly `AUTHORIZED`. |
| E. Child-agent inheritance | Child B consumes parent A’s T1 result without exact delegation/closure. | `UNAVAILABLE`. | Incorrectly `AUTHORIZED`. |
| F. Restart persistence | Restore prior state under a new process instance without lineage proof. | `UNAVAILABLE`; consumed or prohibited replay may be `DENIED`. | Incorrectly `AUTHORIZED`. |
| G. Cross-domain relay | Valid evidence held by A is relayed to B in another authority domain. | `UNAVAILABLE`; evidence possession does not transfer authority. | Incorrectly `AUTHORIZED`. |
| H. Shared-state laundering | Summary/cache/common memory carries favorable state to a new consumer. | `UNAVAILABLE` absent exact artifact, transformation, provenance, and consumer binding. | Incorrectly `AUTHORIZED`. |
| I. Identity discontinuity | Logical task remains stable while effective principal changes. | `UNAVAILABLE` absent exact current subject and identity basis. | Incorrectly `AUTHORIZED`. |
| J. Boundary-epoch discontinuity | Subject/objective remain stable while B1 changes to B2. | `UNAVAILABLE` absent current re-establishment. | Correctly `UNAVAILABLE`. |

## Exact reproducible counterexample

Minimal deterministic construction:

1. Load `cases/authority_lab/LAB-V1-032.json`.
2. Append one T2 mutation:

   ```json
   {
     "field": "execution_host",
     "before": "SANDBOX-S1",
     "after": "HOST-S2"
   }
   ```

3. Do not supply fresh T3 host, principal, control-state, boundary, evidence, grant, or continuity establishment.
4. Evaluate through the ordinary `run_fixture` / oracle path.
5. Observe actual authority outcome `AUTHORIZED` with reason `CURRENT_AUTHORITY_ESTABLISHED`.

Normatively, the result must be `UNAVAILABLE`: an explicit authority-relevant boundary transition occurred and current applicability was not established. The transition is not known to be prohibited, so `DENIED` would overclaim.

The same construction reproduces with the other unregistered fields in the registry above.

## Smallest defect isolated

The fixture model accepts an arbitrary string as `Mutation.field`. The oracle checks mutation continuity only for finite registries:

- canonical authority-state fields;
- seven existing relational mutation facts; and
- objective-binding and transformation facts.

There is no fail-closed disposition for a mutation field outside those registries. An explicit but unregistered mutation is therefore parsed, retained, shown in trace output, and ignored during authority derivation. The positive T3 state remains unchanged and the oracle returns `AUTHORIZED`.

An arbitrary cosmetic or descriptive mutation would not create an authority defect merely by existing. The reproduced defect is narrower: the parser accepts mutations that the published contract classifies as authority-relevant, but the schema provides no distinction between checked authority mutations and unchecked diagnostics, and the oracle neither maps nor rejects the accepted authority-relevant transition.

The defect is:

> Open accepted mutation vocabulary + closed continuity-check registry permits explicit authority-relevant boundary transitions to disappear from authority evaluation.

This is not a demonstrated defect in the six-coordinate/six-invariant contract. It is an executable representation and coverage defect: the implementation does not enforce the contract for every transition shape it accepts.

## Why the existing contract rejects the counterexample

The contract already requires exact current applicable boundary and authority-relevant state at T3. It already states that:

- a binding from one tenant, environment, domain, epoch, or root does not silently authorize another;
- names, handles, endpoints, and equal bytes do not establish identity;
- evidence remains bound to its exact context and transition;
- restart and replay do not recreate authority;
- child, delegated, wrapped, summarized, or derived state does not inherit authority; and
- missing current continuity yields `UNAVAILABLE`.

Therefore the semantic repair is not a seventh coordinate or invariant. The implementation must make accepted transition syntax closed under authority evaluation or reject what it cannot classify.

## DENIED versus UNAVAILABLE

The reproduced cases are `UNAVAILABLE` because the new boundary state is not established and no exact applicable prohibition is supplied.

`DENIED` is correct only when:

1. the applicable boundary and exact current tuple are established; and
2. an established applicable condition rejects, revokes, supersedes, invalidates, or prohibits the transition.

Unknown host, principal, tool, connector, credential, domain, or consumer state must not be converted into `DENIED` merely to avoid an `UNAVAILABLE` result.

## Is executable Authority Lab work justified?

Yes. A reproducible executable counterexample exists, and it incorrectly reaches `AUTHORIZED`.

This research artifact does not authorize the repair. The repository’s established process separates research, design, implementation, exact-head hostile review, and human merge authority. The next slice should be design-first.

## Smallest proposed next step

Create a separately authorized design artifact for **Authority Lab v1 mutation-registry closure and boundary-transition continuity**. It should determine, without changing the frozen public contract:

1. the exact accepted T2 mutation vocabulary;
2. how every accepted mutation maps to an existing tuple field, authority-state field, relational fact, objective-binding fact, or explicitly non-authority-bearing diagnostic field;
3. whether unrecognized mutation fields are schema errors or deterministic `UNAVAILABLE` inputs;
4. how existing descriptive mutations in the 12 maintained fixtures are mapped without laundering their outcomes;
5. the minimal strict relation needed to bind host/process/principal/tool/connector/credential/domain/account/network/restart lineage through existing `control_state`, `identity_basis`, `boundary_epoch`, and applicable-boundary semantics;
6. hostile U/D/A fixtures for one representative transition from each equivalence class;
7. a positive case where a changed boundary is exactly re-established and legitimately reaches `AUTHORIZED`; and
8. tests proving aliases, wrappers, summaries, shared state, relays, unknown mutation names, and field spelling cannot bypass continuity.

The narrowest repair candidate is fail-closed registry closure plus canonical mapping into existing state and relation semantics. A new tuple coordinate or invariant is neither necessary nor authorized.

## Residual limitations

Even after a future executable repair, the lab would still depend on fixture truth and admitted roots. It cannot prove:

- that a real host, process, agent, tool, connector, credential, tenant, or network identity was observed correctly;
- that a boundary transition was detected rather than omitted before fixture construction;
- that boundary-epoch allocation or ordering is rollback-resistant in production;
- that credential custody, monitor coverage, provenance, or external commit observation is uncompromised;
- that a declared relation is semantically complete for every future platform; or
- that external enforcement actually prevented an unauthorized effect.

The counterexample proves an executable omission path for explicitly supplied mutation facts. It does not prove that every external boundary change can be observed or represented.

## Research verdict

**REPRODUCIBLE IN-SCOPE EXECUTABLE COUNTEREXAMPLE FOUND**

**FAIL — Authority Lab v1 accepts explicit authority-relevant boundary mutations outside its checking registry and can incorrectly preserve `AUTHORIZED`.**

The frozen contract itself remains sufficient for the tested authority consequence when correctly interpreted. The current executable implementation is not sufficient for accepted but unregistered mutation fields.

No seventh coordinate is added. No seventh invariant is added. No fourth outcome is added. No executable code or fixture is changed in this slice.

If a later corrected implementation reports PASS, PASS means only failure to falsify that exact implementation under the tested scope. It does not prove security, completeness, production safety, correct external observation, or universal boundary continuity.

## Authority status

This artifact is research evidence only. It does not authorize implementation, deployment, production use, certification, roadmap advancement, merge, or any authority-bearing transition. Human authorization remains required for a design or implementation phase.
