# Hostile Review Catalog

## Status

This document is a public design-review catalog for the frozen candidate next-layer authority-binding contract.

It records the hostile design-review campaign covering reviews #3 through #14. It is a documentation artifact only.

It does **not** prove security, establish universal correctness, constitute certification/compliance/formal verification, authorize implementation, authorize a later phase, change roadmap state, convert review PASS results into authority, or convert human merge into implementation authority.

The frozen candidate authority-binding tuple is:

`(subject, artifact, control_state, identity_basis, boundary_epoch, decision)`

Configuration is part of `control_state`. Consumption is a rule, not a tuple field.

## Frozen invariant set

The frozen candidate contract contains exactly six invariants.

### INV-CONT — verification-to-use continuity

The live consume-time authority tuple must match the tuple that was verified. If equality between the verified tuple and the live consume-time tuple cannot be established, the result is `UNAVAILABLE`. Detection after consumption is forensic evidence, not authorization.

### INV-DISC — identity-bearing discriminator discipline

Selectors and content alone are not identity. Names, roles, labels, handles, pathnames, replica names, process identifiers, user identifiers, session identifiers, and similar selectors do not by themselves prove identity continuity. This discipline applies at minimum to `subject`, `artifact`, and `boundary_epoch`.

### INV-BND — independent, epoch-bound authority boundary

The applicable authority boundary is independently established and epoch-bound. The requester cannot select, route around, or manufacture its own applicable boundary. Reciprocal, cyclic, delegated, or collusive agents do not create authority merely by agreeing with each other.

### INV-EVD — evidence is tuple-bound and non-promotable

Evidence is bound to the exact applicable tuple and decision. Evidence is not authority. Evidence for one decision, artifact, control state, identity basis, or boundary epoch cannot be silently promoted to another. Weaker evidence cannot be promoted into stronger evidence by relabeling, aggregation, transformation, repetition, or agreement alone.

### INV-USE — consumption and continuing-use discipline

A one-shot authorization may be consumed at most once. Continuing grants remain usable only while their current authority conditions remain satisfied. `DENIED` and `UNAVAILABLE` do not preserve residual permission. Restart, cache recovery, replay, retry, or replica promotion do not recreate consumed or no-longer-current authority.

### INV-CLO — no implicit transformation closure

Authority over one object does not automatically authorize a composition, partition, wrapper, projection, report, transformed object, derived object, hybrid result, or translated cross-domain object. Authority extends only where the exact applicable contract explicitly preserves it.

## Category discipline

### Security invariant

A semantic rule that the candidate contract requires to remain true.

### Trust assumption

A property the contract depends on but does not itself prove.

### Implementation obligation

A mechanism that an implementation would need in order to preserve the contract. An implementation obligation is not automatically a new invariant.

### Hostile-review evidence

A review result showing that an attempted counterexample did or did not survive the stated contract and trust boundary. Review evidence is not authority.

### Authority decision

The result produced by the applicable authority evaluation: `AUTHORIZED | DENIED | UNAVAILABLE`.

`DENIED` means the applicable boundary and current tuple were established and the evaluated contract failed.

`UNAVAILABLE` means the applicable boundary, tuple continuity, discriminator, evidence, ordering, freshness, or evaluation required for a valid decision could not be established.

Neither `DENIED` nor `UNAVAILABLE` authorizes the requested transition.

---

## Review #3 — Unresolved trust-boundary edges

### Objective

Attack the frozen candidate contract at its explicit trust boundary rather than only at ordinary state transitions.

### Attack styles

- compromise of the live applicable authority boundary;
- identity-basis collision, corruption, or second-preimage failure;
- explicitly bearer-style authority contracts;
- diagnostic or timing distinctions between `DENIED` and `UNAVAILABLE`;
- combinations of these edge conditions with continuity and evidence attacks.

### Strongest near-counterexample

A live applicable authority boundary that is itself compromised can produce apparently valid decisions while violating the intended security objective. That is not resolved by adding another invariant inside the same trust boundary; it is an explicit boundary assumption.

### Principal invariants engaged

`INV-CONT`, `INV-DISC`, `INV-BND`, `INV-EVD`.

### Surviving in-scope counterexample

None found within the stated objective and trust boundary.

### Seventh invariant required

No.

### Tightening required

No.

### Trust assumptions and obligations exposed

- the live applicable authority boundary must itself remain trustworthy;
- the active identity basis must retain its assumed collision and integrity properties;
- bearer-style semantics must be explicitly modeled rather than inferred;
- confidentiality or indistinguishability of `DENIED` versus `UNAVAILABLE` is outside the current authority objective.

### Verdict

The frozen six-invariant design survived the assigned review within its declared boundary. This is design evidence, not proof.

---

## Review #4 — Composition

### Objective

Determine whether independently valid authority decisions can compose into an unauthorized aggregate outcome.

### Attack styles

- nested decisions;
- delegation chains;
- partial failure;
- concurrent consumers;
- overlapping artifacts and subjects;
- one-shot plus continuing grants;
- cross-boundary composition;
- derived objects;
- stale-parent/fresh-child and fresh-parent/stale-child combinations;
- cycles and replica disagreement;
- ordering attacks;
- revocation races;
- retries;
- decision-set replay;
- identity-basis mismatch.

### Strongest near-counterexample

Two independently issued decisions attempt to consume the same scarce pre-state concurrently. If both external effects commit as though each had exclusive authority, the implementation has failed to preserve live-state linearization. The semantic blocker is already represented by `INV-CONT` and `INV-USE`.

### Principal invariants engaged

`INV-CONT`, `INV-EVD`, `INV-USE`, `INV-CLO`.

### Surviving in-scope counterexample

None found.

### Seventh invariant required

No.

### Tightening required

No.

### Implementation obligations exposed

- atomic authority consumption or equivalent fencing;
- complete representation of authority-relevant control state;
- explicit dependency semantics;
- authoritative ordering;
- faithful replica lineage.

### Verdict

Composition does not create implicit authority. Composite or derived outcomes require an exact applicable authority contract.

---

## Review #5 — Authority-graph lifecycle drift

### Objective

Attack decisions whose dependency graph changes between issuance and consumption. The review modeled an evolving authority graph `G_t = (V_t, E_t)`.

### Attack styles

- revocation after downstream issuance;
- partial refresh;
- stale subgraphs;
- fresh child with stale parent;
- replacement and rebinding;
- partial control-state drift;
- identity migration;
- boundary-epoch change;
- continuing and one-shot interactions;
- graph forks and rejoins;
- replica promotion;
- graph truncation;
- orphaning and reparenting;
- delayed revocation or epoch propagation;
- lifecycle cycles;
- rollback of graph segments;
- restoration of historical subgraphs;
- compaction and recovery;
- identifier resurrection;
- partial policy rotation and reevaluation.

### Strongest near-counterexample

A parent dependency is revoked. A restart loses the consume-time dependency edge or its classification. A cached child decision then appears independent. The child cannot establish the current dependency relation and must therefore be `UNAVAILABLE`.

### Principal invariants engaged

`INV-CONT`, `INV-EVD`, `INV-USE`, `INV-CLO`.

### Surviving in-scope counterexample

None found.

### Seventh invariant required

No.

### Tightening required

No.

### Trust assumptions and implementation obligations exposed

- dependencies must classify issuance-time-only versus consume-time-required semantics;
- consume-time dependencies must be re-established from authoritative state;
- graph provenance must survive lifecycle transitions;
- invalidation visibility must be monotonic enough for the stated contract;
- graph reevaluation must not assume transitive freshness;
- orphan semantics must be explicit;
- selectors must not reconstruct lost identity.

### Verdict

Lifecycle drift exposed implementation and provenance obligations, not a new semantic invariant.

---

## Review #6 — Crash/recovery/disaster state

### Objective

Attack authority semantics across crashes, torn persistence, recovery, replay, and ambiguous external effects.

### Attack styles

- crash before or after validation;
- crash before consumption persistence;
- crash after external effect;
- torn persistence;
- partial control-state, dependency, or epoch persistence;
- stale checkpoints;
- database/world mismatch;
- journal replay, duplication, omission, and reorder;
- snapshot replay;
- failover missing consumption state;
- crash during revocation, rotation, or rebind;
- compensation;
- ambiguous commit;
- operator restore;
- unavailable clocks and ordering reconstruction;
- selector-based recovery.

### Strongest near-counterexample

An external effect commits. The process crashes before the consumption record is durably known. Recovery sees an apparently unused one-shot authorization and retries. The recovered system cannot prove whether the authority was already consumed. The correct result is `UNAVAILABLE`, not optimistic retry.

### Principal invariants engaged

`INV-CONT`, `INV-DISC`, `INV-USE`.

### Surviving in-scope counterexample

None found.

### Seventh invariant required

No.

### Tightening required

No.

### Implementation obligations exposed

- durable preservation of ambiguity;
- atomic consumption/effect fencing or an equivalent recovery protocol;
- stable effect identity;
- authoritative recovery ordering;
- complete provenance;
- failover uncertainty discipline;
- reconciliation between authority store and external world;
- separately authorized compensation;
- no operator-created lineage.

### Verdict

Absence of a consumption record is not proof of non-consumption. Absence of an observed effect is not proof that the effect never happened. Ambiguous commit state fails unavailable.

---

## Review #7 — Authority re-entry/restart

### Objective

Determine whether a previously valid authority participant can re-enter after restart, failover, fencing, or restoration and incorrectly treat historical validity as current authority.

### Core principle

**Historically valid is not the same as provably current.**

### Attack styles

- clean and unclean restart;
- failover overlap and dual primary;
- fenced-node return;
- old graph or superseded epoch restoration;
- backup replay;
- authority metadata/world mismatch;
- process or session identifier reuse;
- identity and key rotation;
- subject or artifact replacement while offline;
- dependency mutation while offline;
- revocation, one-shot consumption, expiry, or policy change while offline;
- parent epoch advance;
- partitioned startup;
- cached healthy state;
- operator forced-online behavior;
- stale quorum;
- old-leader resurrection;
- replica conflict;
- startup ordering;
- unavailable ordering sources;
- degraded startup.

### Strongest near-counterexample

An old leader returns with internally consistent historical state after a replacement leader has consumed authority under a newer epoch. The returning leader cannot prove that its epoch, use state, and ordering are current. Its authority result must therefore be `UNAVAILABLE`.

### Principal invariants engaged

`INV-CONT`, `INV-DISC`, `INV-BND`, `INV-USE`.

### Surviving in-scope counterexample

None found.

### Seventh invariant required

No.

### Tightening required

No.

### Trust assumptions and implementation obligations exposed

- authoritative freshness source;
- exclusive participation proof;
- durable fencing;
- quorum intersection across authority lineage where used;
- coverage of authority-relevant offline events;
- reconstruction of current dependencies;
- binding between world state and authority-store generation;
- startup readiness must not imply authority readiness;
- authoritative ordering;
- no forced-online override that manufactures currentness.

### Verdict

Restart and re-entry do not restore authority merely because historical bytes or local state are valid.

---

## Review #8 — Multi-domain authority transfer/handoff

### Objective

Attack authority transfer between independently governed domains. A conceptual translation was modeled as `F_A→B(T_A, H) = T_B`, where `H` binds the source and destination domains, tuples, identities, evidence compatibility, epochs, ordering, revocation/use state, and relinquish/accept semantics required by the transfer contract.

### Safe exclusive states

For an exclusive handoff:

- before transfer: A active, B inactive;
- completed transfer: A inactive, B active;
- authority gap: A inactive, B inactive — safe but unavailable;
- A active and B active — unsafe unless explicitly permitted by a non-exclusive contract.

### Attack styles

- ordinary, simultaneous, partial, duplicate, and replayed handoff;
- stale source or destination domain;
- subject, artifact, control-state, identity-basis, and epoch translation;
- decision-semantics mismatch;
- `DENIED` or `UNAVAILABLE` laundering;
- evidence promotion;
- one-shot/continuing widening or mismatch;
- delegation widening;
- revocation and epoch races;
- failover during handoff;
- brokered and multi-hop handoff.

### Strongest near-counterexample

Domain B accepts an exclusive handoff, but domain A's relinquishment was not durably established. Both domains can then appear authorized. If exclusivity requires source relinquishment or fencing, B cannot establish the required transfer state and must remain `UNAVAILABLE`.

### Principal invariants engaged

`INV-CONT`, `INV-BND`, `INV-EVD`, `INV-USE`, `INV-CLO`.

### Surviving in-scope counterexample

None found.

### Seventh invariant required

No.

### Tightening required

No.

### Trust assumptions and implementation obligations exposed

- authoritative translation schema;
- relinquish/accept observability;
- globally unique handoff identity;
- cross-domain fencing;
- semantic and evidence-strength compatibility;
- end-to-end provenance;
- revocation ordering;
- durable failure state;
- destination uniqueness where exclusivity requires it.

### Verdict

Cross-domain transfer does not create implicit authority. A destination domain must establish the exact transfer contract required for its own applicable authority decision.

---

## Review #9 — Quorum/threshold/multi-authority

### Objective

Determine whether numerical agreement, threshold signatures, or multi-authority aggregation can manufacture authority that no exact applicable contract authorizes.

A conceptual aggregate contract was modeled as `Q = (M_g, R_g, K_g, W_g, X_g, F_g, V_g)` covering exact membership generation, roles/classes, threshold rules, weights/delegation, independence/intersection assumptions, freshness/revocation/order semantics, and exact contribution binding.

### Core principles

**Numerical agreement is not independent authority.**

**Consensus is not evidence of independence.**

A quorum certificate is evidence presented to an aggregate authority boundary. It is not automatically the authority boundary itself.

### Attack styles

- stale or superseded quorum certificates;
- duplicate or sybil identities;
- cloned verifiers;
- shared evidence roots and correlated failures;
- membership and threshold changes;
- revoked signers;
- identity or epoch changes;
- split and conflicting quorums;
- quorum-intersection failure;
- stale plus fresh vote sets;
- vote replay across artifact, state, or semantics;
- omission of negative votes;
- `UNAVAILABLE` treated as abstention;
- committee shopping and dynamic committees;
- assurance fallback;
- authority-class mismatch;
- weight mismatch or duplication;
- delegation and cycles;
- provenance-dropping aggregation;
- aggregator treated as authority;
- old certificate replay.

### Strongest near-counterexample

Conflicting 2-of-3 certificates exist for mutually exclusive outcomes: `{P1, P2}` for X and `{P2, P3}` for Y. If the contract requires mutual exclusion, the intersection participant's contribution, live state, and authoritative consume order must make at most one result current. If currentness cannot be established, the result is `UNAVAILABLE`.

### Principal invariants engaged

`INV-CONT`, `INV-BND`, `INV-EVD`, `INV-USE`.

### Surviving in-scope counterexample

None found.

### Seventh invariant required

No.

### Tightening required

No.

### Trust assumptions and implementation obligations exposed

- authoritative membership generation;
- independence attestation where independence is required;
- quorum-intersection safety;
- equivocation control;
- aggregate linearization;
- weight conservation;
- certificate provenance;
- explicit negative-result semantics;
- authoritative committee selection;
- evidence/authority typing.

### Verdict

Threshold count alone does not establish authority, independence, currentness, or scope.

---

## Review #10 — Evidence provenance/corroboration independence

### Objective

Determine whether multiple pieces of apparently distinct evidence can be created from one underlying observation and incorrectly counted as independent corroboration.

An evidence item was considered in terms of evidence identity, source, type, exact tuple, lineage, transformations, dependency ancestors, freshness, and strength. A conceptual evidence requirement was considered as `R = (types, quantity, independence, freshness, strength, lineage)`.

### Core principles

**Transformation can create a new artifact identity without creating a new independent observation.**

**Agreement is not independence.**

### Attack styles

- copied sources;
- re-signing the same root observation;
- multi-format transforms;
- multiple models or agents consuming the same upstream evidence;
- cached, mirrored, and replica sources;
- recursive or circular citations;
- hidden common ancestors;
- shared sensors, control domains, or failure domains;
- common generated/training origins where relevant to the claim;
- broker laundering, provenance stripping, and truncation;
- transformed identifiers;
- evidence reuse across decision/artifact/state/basis/epoch;
- historical evidence with fresh wrappers;
- source restart or recreation;
- recovery reconstruction;
- multiplication of weak evidence;
- strength upgrade across domains;
- quorum signatures over non-independent evidence;
- derived-object evidence;
- partial provenance;
- provenance fork/rejoin;
- restoration of historical provenance state.

### Strongest near-counterexample

One root observation O produces E1 directly and E2 through a transformation. Both are authentic and have distinct artifact identities. If a contract requires two independent observations, counting E1 and E2 as two independent roots violates the evidence requirement.

### Principal invariants engaged

`INV-EVD`, `INV-CLO`.

### Surviving in-scope counterexample

None found.

### Seventh invariant required

No.

### Tightening required

No.

### Trust assumptions and implementation obligations exposed

- stable ultimate-source identity;
- transformation transparency;
- trustworthy observation-time semantics;
- knowledge of principal/failure-domain relationships where independence depends on them;
- provenance completeness and durability;
- correlation disclosure;
- reevaluation when independence assumptions change;
- evidence-strength monotonicity;
- strict separation between evidence and authority.

### Verdict

Distinct signatures, files, models, agents, or transformed outputs do not by themselves prove independent corroboration.

---

## Review #11 — Temporal evidence/freshness/ordering

### Objective

Attack authority decisions that depend on time, freshness, expiration, sequencing, and delayed delivery.

The review distinguished observation time, record-creation time, signature time, receipt time, verification time, decision time, consume time, and authoritative ordering. A signed timestamp proves only that a signer signed a time claim unless the signer is trusted for the required time semantics.

### Attack styles

- stale observation with fresh wrapper;
- delayed or future-dated evidence;
- clock rollback or advance;
- skew;
- copied attacker-controlled time;
- receipt/verification/decision time confused with observation or consume time;
- fresh issuance followed by stale consumption;
- expiration;
- set-level temporal validity;
- reverse or incomparable ordering;
- partition delay;
- replay windows;
- snapshot-restored freshness;
- cache or transformation loss of temporal provenance;
- sequence reset or source recreation;
- epoch, identity-basis, revocation, artifact, or control-state changes;
- maximum allowed separation within evidence sets;
- dependency validity before/after decision;
- long verification-to-use gap;
- unavailable authoritative ordering.

### Strongest near-counterexample

Evidence is valid when the authority decision is issued but expires before consumption. At consumption, required temporal conditions must be reevaluated. If expiry is established, the applicable result is `DENIED`. If required freshness or ordering cannot be established, the result is `UNAVAILABLE`.

### Principal invariants engaged

`INV-CONT`, `INV-EVD`, `INV-USE`.

### Surviving in-scope counterexample

None found.

### Seventh invariant required

No.

### Tightening required

No.

### Trust assumptions and implementation obligations exposed

- authoritative freshness origin;
- trustworthy clock source where wall-clock semantics are required;
- consume-time time-source availability;
- monotonic expiry semantics;
- set-level temporal evaluation;
- observation identity continuity;
- ordering-source continuity;
- delay awareness;
- temporal provenance;
- fail-closed behavior when required time cannot be established.

### Verdict

Temporal validity at issuance does not automatically remain valid at consumption.

---

## Review #12 — Revocation/withdrawal/supersession

### Objective

Determine whether revocation, withdrawal, narrowing, or supersession can be bypassed by stale grants, caches, replicas, retries, alternate verifiers, or transformed authority paths.

A conceptual revocation was modeled as `R = (id, target, scope, generation, effective, order, issuer, semantics)`.

### Core principle

**Unused does not mean still authorized.**

### Attack styles

- subject, artifact, decision, and grant revocation;
- one-shot revocation and revocation/consume races;
- revocation/effect, handoff, quorum, and domain races;
- replica propagation delay;
- stale caches and last-known-good state;
- restart and backup restore;
- journal replay/reorder;
- policy/configuration supersession;
- identity-basis or boundary-epoch rotation;
- delete/recreate and key rotation;
- parent/child revocation;
- quorum-member revocation;
- evidence-source revocation;
- invalidated independence assumptions;
- narrowing and stricter/looser policy;
- contradictory revocation records;
- unavailable ordering;
- revocation-source unavailability or suppression;
- alternate-verifier retry;
- transferred/transformed revocation.

### Strongest near-counterexample

A decision D0 is valid and unused. A revocation R changes the applicable control state to C1. A consumer holding cached C0 sees D0 as unused and attempts consumption without proving current revocation state. Unused status does not establish current authorization. If effective revocation is established, the result is `DENIED`; if required revocation status or ordering cannot be established, the result is `UNAVAILABLE`.

### Principal invariants engaged

`INV-CONT`, `INV-EVD`, `INV-USE`.

### Surviving in-scope counterexample

None found.

### Seventh invariant required

No.

### Tightening required

No.

### Trust assumptions and implementation obligations exposed

- authoritative revocation source;
- durable effective ordering;
- monotonic generation where required;
- propagation/freshness proof;
- explicit dependency, handoff, quorum, and evidence-source revocation semantics;
- precise narrowing;
- explicit grandfathering where permitted.

### Verdict

Absence of a locally observed revocation is not proof that an authorization remains current.

---

## Review #13 — Resource exhaustion/adversarial availability

### Objective

Determine whether resource pressure can cause the system to weaken assurance requirements and accidentally convert unavailable verification into authority.

### Core principle

**Resource exhaustion may reduce availability. It must not reduce required assurance.**

### Attack styles

- verifier, evidence, revocation, identity, epoch, ordering, dependency, and provenance timeouts;
- quorum unavailability and threshold weakening;
- assurance fallback;
- queue delay crossing expiry/revocation/policy/basis/epoch changes;
- alternate-verifier retry;
- stale-cache fallback;
- circuit breaker;
- degraded, offline, or emergency mode;
- load-shedding of negative checks;
- partial evidence;
- rate limiting;
- freshness or consumption lookup failure;
- memory, disk, and WAL pressure;
- replica lag;
- stale quorum;
- partition;
- admission before authorization;
- external effect before durable consumption;
- ambiguous effect and retry storm;
- attacker-created denial of exactly the checks required for safety.

### Strongest near-counterexample

A valid, unused one-shot authorization passes ordinary checks. Disk exhaustion prevents creation of a durable consumption fence. The external effect path remains available. The system must not execute merely because the effect path is healthy. Without the required consumption guarantee, the result is `UNAVAILABLE`.

### Principal invariants engaged

`INV-CONT`, `INV-EVD`, `INV-USE`.

### Surviving in-scope counterexample

None found.

### Seventh invariant required

No.

### Tightening required

No.

### Trust assumptions and implementation obligations exposed

- integrity of dependency criticality classification;
- fencing between admission and effect;
- backpressure isolation;
- retry identity and status continuity;
- separately authorized fallback paths;
- cache freshness proof;
- durable one-shot fencing;
- retention of negative state;
- quorum generation integrity;
- fail-closed behavior under denial-of-service pressure.

### Verdict

Availability pressure is not authority to lower the contract.

---

## Review #14 — Cross-attack synthesis / kill-shot

### Objective

Combine attack families that individually failed and determine whether their interaction creates emergent authority not represented by the six frozen invariants.

The threat combined stale fragments, concurrent domains/replicas, partial persistence, recovery/failover, evidence transformation, quorum certificates, delayed revocation, identity/epoch changes, availability pressure, one-shot ambiguity, and cross-domain translation.

### Compound attacks

1. stale replica + revocation + quorum;
2. crash + lost consumption + retry storm;
3. handoff + revocation + partition;
4. provenance outage + degraded threshold;
5. identity rotation + rollback + subject recreation;
6. epoch change + cache + old-verifier retry;
7. quorum membership change + expiry + conflicting certificates;
8. restored old graph + current external world;
9. derived object + shared evidence source + handoff;
10. continuing grant + policy supersession + partition restart;
11. one-shot grant + disk exhaustion + ambiguous effect;
12. stale revocation + quorum shopping + weak fallback;
13. evidence independence later becomes false + pending handoff;
14. partial graph refresh + failover + old-leader return;
15. clock rollback + snapshot restore + revoked grant;
16. stale certificate + recreated participant + membership generation;
17. semantic mismatch + evidence promotion + provenance-dropping broker;
18. concurrency + partial persistence + replica promotion;
19. parent revocation + orphan + dependency metadata loss;
20. authority gap + stale recovery + operator forced-online action;
21. quorum + failover + expiry;
22. revoked evidence + transformation + rollback + new domain;
23. separately authorized lower-risk operations combined into a higher-risk derived result;
24. policy denial + evidence cycle + verifier recreation + retry;
25. weighted quorum rollback + duplicated weight;
26. temporal boundary + identity-basis change + handoff;
27. partial compensation + reparenting + hybrid state;
28. artifact replacement + stale quorum path/hash;
29. one handoff duplicated to two destination domains;
30. revocation durable on one leader + WAL omission + membership drift;
31. expired parent grant + wrapper + dependency-metadata loss + delegation;
32. old certificate + policy tightening + expiry + emergency restoration of old epoch.

### Strongest compound near-counterexample

A one-shot decision D is valid. Consumer C1 executes the external effect. A crash occurs before the consumption record is known durably to replica R2. R2 is promoted. Consumer C2 retries. R2 cannot establish whether the effect already occurred, whether D was consumed, or which ordering is authoritative. The correct result is `UNAVAILABLE`. Allowing the second effect would violate the existing continuity and consumption requirements.

### Principal invariants engaged

All six: `INV-CONT`, `INV-DISC`, `INV-BND`, `INV-EVD`, `INV-USE`, `INV-CLO`.

### Surviving in-scope counterexample

None found.

### Seventh invariant required

No.

### Tightening required

No.

### Emergent-authority determination

No new emergent-authority class survived. Apparent emergent authority reduced to stale, duplicated, widened, translated, transformed, hybrid, derived, replayed, or incompletely evaluated authority. Where a compound outcome itself differed from the exact authorized object, `INV-CLO` required its own applicable authority. Where currentness, identity, lineage, evidence, ordering, revocation, or consumption state could not be established, the existing invariants forced `UNAVAILABLE`.

### Interaction discipline exposed

Every authority-relevant interaction must be represented in the applicable decision contract or authority-relevant `control_state`, including dependencies, generations, exclusivity, ordering, revocation, evidence strength, transformation semantics, and consumption state where required. Omission of authority-relevant state makes evaluation incomplete. Incomplete required evaluation does not authorize a transition.

### Consolidated trust assumptions and implementation obligations

1. contract completeness;
2. type preservation between evidence, authority, identities, selectors, decisions, handoffs, revocations, and consumption state;
3. cross-mechanism generation binding;
4. atomic authority linearization or equivalent fencing;
5. durable uncertainty;
6. end-to-end provenance;
7. effect-side fencing;
8. no implicit scope repair;
9. compatible independence semantics between quorum membership and evidence-source independence;
10. integrity of currentness sources.

### Verdict

The compound attacks reduced to failures already represented by the frozen six-invariant contract. No seventh invariant was required. No tightening was required. The unrestricted design-only hostile-review cycle reached diminishing returns for the stated boundary. This is a bounded design-review result, not proof that all possible systems, interactions, implementations, or future changes are secure.

---

## Attack taxonomy

### Verification-to-use continuity

- verify A, consume B;
- mutate between verification and use;
- stale verification result or stale grant;
- stale current-state cache;
- fresh decision against stale consume-time state;
- continuing grant after state changes;
- race between verification and effect.

Primary coverage: `INV-CONT`, `INV-USE`.

### Selector and identity substitution

- same pathname, different object;
- rename/rebind;
- unlink/recreate;
- same bytes, different object;
- same content, changed identity;
- role/name/label reuse;
- process/session/replica-name reuse;
- subject, artifact, or identity-basis substitution.

Primary coverage: `INV-DISC`, `INV-CONT`.

### ABA, rollback, restore, and resurrection

- A→B→A state sequence;
- rollback to historical bytes;
- snapshot or backup restore;
- historical graph restore;
- old epoch restoration;
- old-leader resurrection;
- identifier resurrection;
- stale quorum restoration.

Primary coverage: `INV-CONT`, `INV-DISC`, `INV-BND`, `INV-USE`.

### Evidence reuse and promotion

- cross-decision/artifact/state/basis/epoch reuse;
- weak-to-strong promotion;
- multiple signatures over one observation;
- transformed evidence counted as new independent evidence;
- evidence treated as authority.

Primary coverage: `INV-EVD`, `INV-CLO`.

### Verifier shopping and collusive authority

- alternate-verifier retry;
- weaker-verifier fallback;
- reciprocal/cyclic/delegated/collusive approval;
- committee shopping;
- stale committee selection.

Primary coverage: `INV-BND`, `INV-EVD`.

### Replay and concurrent consumption

- one-shot replay;
- duplicate request;
- concurrent consumers;
- retry after timeout/crash;
- replica failover;
- lost consumption record;
- ambiguous effect;
- retry storm.

Primary coverage: `INV-CONT`, `INV-USE`.

### Transformation, composition, and derived objects

- wrapper, projection, partition, report, transform;
- composition and nested decision;
- hybrid object;
- lower-risk parts combined into higher-risk result;
- translated result.

Primary coverage: `INV-CLO`, `INV-EVD`, `INV-CONT`.

### Dependency and graph lifecycle attacks

- parent revoked after child issuance;
- stale parent/fresh child;
- fresh parent/stale child;
- orphan/reparent;
- graph fork/rejoin;
- partial refresh;
- dependency metadata loss;
- restored historical graph;
- partial policy rotation.

Primary coverage: `INV-CONT`, `INV-EVD`, `INV-CLO`.

### Crash, recovery, and persistence ambiguity

- crash around validation/effect;
- torn writes;
- partial persistence;
- stale checkpoint;
- journal/WAL omission, duplication, or reorder;
- ambiguous commit;
- compensation;
- world/store mismatch.

Primary coverage: `INV-CONT`, `INV-USE`.

### Restart and re-entry

- clean/dirty restart;
- dual primary;
- fenced-node return;
- stale replica promotion;
- partitioned startup;
- forced online;
- historical healthy state treated as current;
- old-leader return.

Primary coverage: `INV-CONT`, `INV-BND`, `INV-USE`.

### Cross-domain handoff and translation

- partial/duplicate/replayed/simultaneous handoff;
- authority gap;
- double-active domains;
- translation or evidence-strength mismatch;
- one-shot/continuing mismatch;
- destination duplication;
- brokered multi-hop transfer.

Primary coverage: `INV-BND`, `INV-EVD`, `INV-USE`, `INV-CLO`.

### Quorum and threshold attacks

- sybil/duplicate members;
- shared roots and correlated failures;
- stale membership generation;
- changed thresholds;
- stale votes;
- conflicting certificates;
- insufficient intersection;
- `UNAVAILABLE` treated as abstention;
- weight duplication;
- delegation cycles;
- aggregator promoted to authority.

Primary coverage: `INV-BND`, `INV-EVD`, `INV-CONT`.

### Provenance and independence attacks

- copies, mirrors, caches, replicas, re-signing, transforms;
- multiple agents with one upstream source;
- circular citations and hidden common ancestors;
- provenance laundering/truncation;
- shared sensors or failure domains;
- later-invalidated independence assumptions.

Primary coverage: `INV-EVD`, `INV-CLO`.

### Temporal attacks

- stale observation with fresh timestamp;
- future timestamp;
- clock rollback/advance/skew;
- delayed delivery;
- expiry after issuance;
- replay window;
- sequence reset;
- unavailable ordering source;
- stale or restored temporal provenance.

Primary coverage: `INV-CONT`, `INV-EVD`, `INV-USE`.

### Revocation and supersession attacks

- grant/subject/artifact/dependency/evidence-source revocation;
- policy/configuration supersession;
- basis/epoch rotation;
- stale revocation cache;
- alternate verifier missing revocation;
- transformed/transferred revocation loss.

Primary coverage: `INV-CONT`, `INV-EVD`, `INV-USE`.

### Resource exhaustion and degraded operation

- timeout and queue pressure;
- disk/memory/WAL exhaustion;
- unavailable provenance/revocation/ordering/identity;
- quorum shortage;
- threshold weakening;
- stale-cache fallback;
- degraded/emergency mode;
- effect path available while authority path is unavailable.

Primary coverage: `INV-CONT`, `INV-EVD`, `INV-USE`.

### Compound synthesis

- stale state + quorum;
- revocation + partition;
- crash + lost consumption + retry;
- handoff + failover;
- provenance outage + degraded threshold;
- identity rotation + rollback;
- epoch change + cache;
- temporal expiry + membership change;
- restored graph + current world;
- derived object + shared source + transfer;
- ambiguous effect + resource exhaustion;
- policy supersession + restart;
- revocation + quorum shopping + weak fallback.

Primary coverage: all six invariants as applicable.

---

## Strongest recurring near-counterexamples

### 1. Verify-one/use-another

A decision is verified against one exact tuple and consumed against another. Blocker: `INV-CONT`.

### 2. Same selector, replaced identity

A pathname, label, role, session, replica name, or other selector is reused after the underlying identity changes. Blockers: `INV-DISC`, `INV-CONT`.

### 3. Historical state restored as current

Old bytes, snapshots, graphs, grants, or epochs are restored and treated as though historical validity proves current authority. Blockers: `INV-CONT`, `INV-DISC`, `INV-BND`, `INV-USE` as applicable.

### 4. Two transformed copies counted as independent evidence

Distinct artifacts generated from one root observation are counted as independent corroboration. Blockers: `INV-EVD`, `INV-CLO`.

### 5. Concurrent one-shot consumption

Two consumers race to use the same one-shot authority. Blockers: `INV-CONT`, `INV-USE`. Implementation requires atomic consumption or equivalent fencing.

### 6. External effect committed, consumption state ambiguous

An effect may have occurred, but recovery cannot prove whether authority was consumed. Blockers: `INV-CONT`, `INV-USE`. Correct result: `UNAVAILABLE`.

### 7. Exclusive handoff produces two active domains

Destination acceptance occurs without provable source relinquishment. Blockers: `INV-BND`, `INV-CONT`, `INV-USE`, plus transfer-specific contract requirements.

### 8. Conflicting quorum certificates

Two threshold-valid certificates appear for mutually exclusive outcomes. Current membership, ordering, and live state must resolve the conflict under `INV-CONT`, `INV-BND`, and `INV-EVD`; otherwise `UNAVAILABLE`.

### 9. Revoked but unused decision

A stale consumer sees a never-consumed decision and assumes it remains authorized despite current revocation. Blockers: `INV-CONT`, `INV-USE`. Unused does not mean current.

### 10. Resource exhaustion prevents durable fencing

Logical checks pass, but the system cannot durably fence consumption before an external effect. Blockers: `INV-CONT`, `INV-USE`. Availability loss must not lower assurance.

---

## Cumulative design-review result

Reviews #3 through #14 attacked the frozen candidate authority-binding contract from multiple independent and compound directions.

Within the stated security objective and trust boundary:

- no reproducible in-scope counterexample survived;
- no seventh invariant was required;
- no tightening of the six frozen invariants was required;
- the strongest near-counterexamples reduced to continuity, identity, boundary, evidence, consumption, or transformation-closure failures already represented by the contract;
- compound review #14 did not expose a new semantic authority class;
- the unrestricted design-only enumeration cycle reached diminishing returns.

This result is intentionally bounded. It means the assigned hostile design reviews did not produce a surviving counterexample within the stated model.

It does **not** mean:

- the contract is mathematically proven;
- every implementation will preserve it;
- every trust assumption is solved;
- every future extension is safe;
- every composition with an external system is safe;
- production readiness is established;
- certification or compliance is established;
- formal verification has occurred;
- implementation is authorized.

Future review becomes materially useful when the contract, implementation, trust boundary, evidence model, authority model, deployment model, or claimed objective changes.

---

## Explicit unresolved and excluded boundaries

### Compromised live applicable authority boundary

If the live authority boundary itself is compromised, the current contract does not prove that the compromised boundary will behave correctly.

### Identity-basis collision, second-preimage, or corruption failure

The contract relies on the active identity basis retaining the properties required by the applicable authority design. Failure of those underlying assumptions is outside the reviewed objective.

### Explicit bearer contracts

A contract that intentionally defines possession of a bearer capability as sufficient authority has different semantics. Those semantics must be explicit; they are not inferred from the current tuple or evidence model.

### `DENIED` versus `UNAVAILABLE` confidentiality

The contract distinguishes `DENIED` from `UNAVAILABLE` for authority semantics. It does not claim that timing, diagnostics, availability behavior, or other side channels make those outcomes indistinguishable to an observer.

---

## Authority status

This catalog is hostile design-review evidence only.

Implementation remains unauthorized.

No later phase is authorized.

Roadmap state is unchanged.

A PASS review does not create implementation authority.

Human merge of this public documentation does not create implementation authority.

Evidence remains separate from authority.

The public exhibit remains separate from the private authoritative core.

No private-core implementation mechanics, hidden fixtures, private migrations, secrets, keys, private endpoints, or unpublished enforcement details are disclosed by this catalog.
