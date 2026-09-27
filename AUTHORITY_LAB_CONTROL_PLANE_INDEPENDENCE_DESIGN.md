# Authority Lab v1 Control-Plane Independence and Appraisal Closure Design

## 1. Baseline and defect

This design follows `FRONTIER_DELTA_CONTROL_PLANE_COLLUSION.md` at
`491a9491b4faea4e180334f2085ceeaac6cccda0`. The frontier demonstrated that
`LAB-V1-134` can return `AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED` while the
same admitted input is compatible with two materially different worlds:

* the supporting control-plane roles are independently controlled; or
* one controller owns the root, orderer, observer, verifier, commitment
  producer, anchor authority, reconciliation/recovery authority, and their
  records.

Protected domain membership currently covers anchor adapters and witness
sources, but not the complete authority path. The root issues the policy and
membership classifications without an independently admitted appraisal of the
root or other control-plane roles. Exact agreement therefore proves only
internal consistency with the admitted classifier, not operational
independence.

The repair objective is:

> Every authority role relied upon by an `AUTHORIZED` decision must have exact,
> current, scoped protected control-domain membership, and every required
> separation claim must close at an admitted independence-appraisal root without
> self-support, circular support, or nominal multiplicity.

## 2. Compatibility constraints

The repair preserves exactly:

* schema `authority-lab-v1`;
* six tuple coordinates;
* six invariants;
* `AUTHORIZED`, `DENIED`, and `UNAVAILABLE` only;
* objective binding, observation admission/completeness, commitment-envelope,
  shutdown/successor, verifier-state anchoring, adapter currentness, and
  witness-continuity semantics;
* deterministic, expectation-independent evaluation; and
* the rule that candidate fixtures cannot supply harness-trusted state.

Control-plane membership is internal authority-relevant relational evidence,
not a seventh tuple coordinate or seventh invariant. No schema version change
is required.

## 3. Roles in scope

One immutable role registry defines roles the evaluator actually consumes. It
must not infer roles from arbitrary labels.

| Canonical role | Exact executable referent | Required when |
|---|---|---|
| `POLICY_ROOT` | admitted `authority_root` identity/generation | Always |
| `ORDERER` | root's exact `ordering_source_id` | Always |
| `OBSERVER` | every observer contributing covered segments | Always for observation-backed authority |
| `COMMITMENT_PRODUCER` | exact envelope issuer/observer identity and key generation | Every selected commitment |
| `COMMITMENT_VERIFIER` | exact selected verifier identity/generation | Every selected commitment |
| `ANCHOR_SOURCE` | selected anchor source identity/generation | Every selected verifier-state anchor |
| `ANCHOR_ADAPTER` | selected protected adapter identity/generation | Every required anchor domain |
| `WITNESS_SOURCE` | each selected witness identity/generation | When witness policy requires it |
| `RECONCILIATION_AUTHORITY` | exact authority selecting a conflicting-domain head | Only when reconciliation is used |
| `RECOVERY_AUTHORITY` | exact recovery-installation authority | Only when recovery is used |
| `INDEPENDENCE_APPRAISER` | protected appraiser identity/generation | For every protected membership |

No conceptual role is added merely to populate the registry. Replica identities
and successor identities remain attributes of the existing verifier,
observer, or execution roles rather than new authority roles.

## 4. Harness-owned protected context

Extend each applicable entry in `trusted_anchor_state.json` with four immutable,
strictly typed collections:

1. `control_plane_policy` — one current root-applicable separation policy;
2. `control_plane_memberships` — exact role membership records;
3. `independence_appraisal_roots` — admitted external appraisal roots;
4. `control_plane_membership_transitions` — exact predecessor/successor changes.

Optional `authorized_consolidations` records are permitted only when the policy
explicitly allows two or more roles to share one effective domain.

These fields are harness-owned. The fixture loader rejects candidate keys such
as `_trusted_control_plane_context`; candidate JSON cannot override, append,
select, or reconstruct this state. Keeping the relations in the existing
protected anchor manifest is the smallest implementation surface and avoids a
parallel trust loader.

## 5. Typed control-plane policy

`CONTROL_PLANE_SEPARATION_POLICY` has exactly:

* `policy_id`, `policy_generation`, `membership_epoch`;
* `required_roles`;
* `required_separation_sets` (sets of roles that must map to different
  effective-domain tuples);
* `allowed_consolidation_ids`;
* `required_appraisal_root_ids`;
* `selection_rule = ALL_APPLICABLE`;
* `boundary`, `boundary_epoch`;
* `source_id`, `authority_generation`, `ordering_source_id`;
* `freshness_challenge_id`, `lifecycle_state`.

The policy is root-applicable but is not sufficient to appraise the root. Its
role list is derived from the selected executable path and must equal the
applicable immutable registry set. Candidate-selected subsets, missing roles,
duplicate roles, unknown roles, and unselected additional policies return
`UNAVAILABLE`.

The policy may explicitly allow consolidation. Consolidation means those roles
are treated as one effective authority and do not count multiple times toward
any separation/quorum requirement. It never silently manufactures diversity.

## 6. Typed control-plane membership

Each `CONTROL_PLANE_ROLE_MEMBERSHIP` binds exactly:

* `role`, `member_id`, `member_generation`, `identity_basis`;
* `credential_or_key_id`, `credential_or_key_generation` where applicable;
* `process_or_instance_id`, `process_or_instance_generation` where applicable;
* `source_lineage`, `upstream_dependency`;
* `control_domain`, `rollback_domain`, `independence_domain`;
* `membership_epoch`;
* `authority_scope` and covered semantic families;
* `boundary`, `boundary_epoch`;
* `start_event_order`, `end_event_order`;
* `appraiser_id`, `appraiser_generation`, `appraisal_root_id`;
* `source_id`, `authority_generation`, `ordering_source_id`;
* `freshness_challenge_id`, `lifecycle_state`.

The effective-domain tuple is:

```text
(source_lineage, control_domain, upstream_dependency, rollback_domain)
```

`independence_domain` is a policy grouping label and is never counted without
the effective tuple. Role, key, process, machine, and organization names are
identity data only.

Every membership must join exactly to the role object used by the selected
decision path. A role object with no membership, two memberships, stale scope,
wrong boundary, incomplete interval, or mismatched generation is
`UNAVAILABLE`.

## 7. Independence-appraisal roots

An `INDEPENDENCE_APPRAISAL_ROOT_ADMISSION` binds:

* `appraisal_root_id`, `appraisal_root_generation`, `identity_basis`;
* exact appraisal scope;
* `source_lineage`, `control_domain`, `rollback_domain`,
  `independence_domain`;
* applicable membership epoch, boundary, and interval;
* ordering, freshness, lifecycle, and source authority;
* predecessor/rotation relationship when generation is greater than one.

An appraisal root is an admitted external trust/input root for this narrow
purpose. It cannot be the evaluated subject, a candidate-provided record, or a
role whose independence it is appraising. It may not share the effective-domain
tuple of a member it appraises when the policy requires separation. A locally
generated signature, self-declared timestamp, key distinction, or root-issued
statement cannot create appraisal-root status.

This terminates the authority graph at an explicit trust boundary. If the
appraisal root is itself compromised along with every comparison source, the
state is externally indistinguishable; the oracle does not claim to solve it.

## 8. Appraisal graph closure and cycle rejection

Build a directed graph from each membership to its exact appraiser and from
each appraiser to its admitted appraisal root. Authorization requires:

1. every applicable membership has exactly one current appraisal edge;
2. each edge is exact in identity, generation, boundary, scope, epoch,
   lifecycle, ordering, and freshness;
3. no member directly or indirectly appraises itself;
4. no two or more non-root nodes form a support cycle;
5. every chain terminates at one policy-required admitted appraisal root;
6. the terminal appraisal root does not share a prohibited effective domain
   with the appraised member; and
7. all policy-required appraisal roots are current and non-conflicting.

Cycle detection is performed over exact `(role, member_id,
member_generation)` nodes. An acyclic chain with no admitted terminal root is
also `UNAVAILABLE`.

## 9. Separation, quorum, and correlation

For every `required_separation_set`, map its roles to effective-domain tuples.
Unless an exact current `AUTHORIZED_ROLE_CONSOLIDATION` applies, tuple reuse
inside the set returns `UNAVAILABLE / CONTROL_PLANE_INDEPENDENCE_UNAVAILABLE`.

Any threshold or quorum counts distinct admitted effective-domain tuples, not
roles, keys, signatures, processes, machines, or `independence_domain` labels.
Multiple records sharing an upstream dependency or rollback domain count as one
effective authority even if their other labels differ.

One current independently appraised contradiction forces `UNAVAILABLE`.
Neither majority nor a larger correlated set can suppress it. Explicit current
authoritative resolution may select a head only if the reconciliation authority
itself has exact protected membership outside every competing domain required
by policy.

## 10. Authorized consolidation and separation

`AUTHORIZED_ROLE_CONSOLIDATION` binds:

* consolidation ID and generation;
* exact member roles and identities/generations;
* shared effective-domain tuple;
* policy and membership epoch;
* reduced independence/quorum effect;
* boundary, interval, ordering, freshness, lifecycle;
* exact source authority and appraisal-root approval.

It permits operation under a policy that does not claim those roles as
independent. It cannot satisfy a policy requiring their separation.

`CONTROL_PLANE_MEMBERSHIP_TRANSITION` binds old and new role memberships,
effective tuples, reason (`ROTATION`, `SEPARATION`, `CONSOLIDATION`, or
`RECOVERY`), policy/epoch, exact ordering, freshness, lifecycle, source
authority, and appraisal-root approval. This supports legitimate separation
into new independent domains.

## 11. Rotation semantics

Root, verifier, observer, anchor, adapter, witness, reconciliation, recovery,
and appraisal-root rotation must join to one exact membership transition.
Changing a key, label, process, or generation without changing the effective
tuple preserves the same effective authority. It is permitted as continuity but
does not create new independence.

Changing the effective tuple requires independently appraised transition
evidence. A stable role label with changed domain membership, or a new role
label with unchanged hidden controller, cannot silently satisfy separation.

## 12. Recovery and reconciliation

When recovery is used, `RECOVERY_AUTHORITY` membership must be current and
separate from the selected anchor/history domains wherever policy requires.
Recovery installation remains bound to the current external anchor, complete
ordered replay, fresh verifier/store generation, receipt, and post-installation
anchor. Protected role membership is an additional join, not a substitute.

When reconciliation is used, `RECONCILIATION_AUTHORITY` must be current,
independently appraised, and outside the conflicting effective domains required
by policy. The exact competing views and selected head remain mandatory.

One surviving independently appraised source can expose rollback and support a
fresh recovery chain. Candidate history cannot become its own appraisal source.

## 13. Outcome discipline

Return `UNAVAILABLE` for:

* missing, ambiguous, stale, conflicting, unordered, or wrong-scope policy,
  membership, appraisal, transition, consolidation, or root evidence;
* effective-domain reuse where separation is required;
* nominal quorum without enough effective domains;
* self-appraisal, circular appraisal, or an unclosed appraisal graph;
* correlated reconciliation/recovery authority;
* role rotation that claims new independence without an exact transition;
* candidate-supplied or candidate-reconstructed protected context; and
* one current independent contradiction.

Return `DENIED` only when current authoritative evidence explicitly revokes,
rejects, invalidates, supersedes, or prohibits a policy, membership, appraisal
root, transition, consolidation, recovery/reconciliation authority, or ordinary
execution authority.

Return `AUTHORIZED` only after every existing authority requirement and the
complete applicable control-plane policy/appraisal graph succeed.

## 14. Hostile fixture plan A–AV

Add fixtures beginning with the next available ID, one independently expected
case per frontier row. The expected reason classes are grouped below; fixture
expectations remain independent of oracle output.

| Cases | Required result | Primary reason class |
|---|---|---|
| A–J | `UNAVAILABLE` | `CONTROL_PLANE_INDEPENDENCE_UNAVAILABLE` or role-specific membership unavailable |
| K–N | `UNAVAILABLE` | `EFFECTIVE_AUTHORITY_CORRELATED` |
| O–S | `UNAVAILABLE` absent exact transition | `CONTROL_PLANE_MEMBERSHIP_TRANSITION_UNAVAILABLE` |
| T–W | `UNAVAILABLE` | `EFFECTIVE_AUTHORITY_QUORUM_UNAVAILABLE` |
| X–AB | `UNAVAILABLE` | independence, reconciliation, or recovery appraisal unavailable |
| AC–AD | `UNAVAILABLE` | current independent conflict/rollback survivor |
| AE | `AUTHORIZED` | `CURRENT_AUTHORITY_ESTABLISHED` |
| AF | `UNAVAILABLE` | `CROSS_DOMAIN_CHECKPOINT_CONFLICTING` |
| AG | `AUTHORIZED` only with exact allowed consolidation | `CURRENT_AUTHORITY_ESTABLISHED` |
| AH | `UNAVAILABLE` | `ROLE_CONSOLIDATION_UNAVAILABLE` |
| AI | `AUTHORIZED` with exact membership transition | `CURRENT_AUTHORITY_ESTABLISHED` |
| AJ–AK | `UNAVAILABLE` | membership/currentness unavailable |
| AL | malformed protected-key injection or `UNAVAILABLE` for candidate assertion | existing input/protected-state behavior |
| AM–AO | `UNAVAILABLE` | `INDEPENDENCE_APPRAISAL_CYCLE` / root unavailable |
| AP–AQ | `UNAVAILABLE` | existing protected join plus appraisal unavailable |
| AR | identical local input; explicit external trust boundary | not locally detectable |
| AS | `UNAVAILABLE` | independent survivor contradiction |
| AT–AV | `AUTHORIZED` | `CURRENT_AUTHORITY_ESTABLISHED` |

Additional focused fixtures must cover duplicate memberships, unknown roles,
unselected extra policy, partial scope, stale appraisal roots, appraisal-root
rotation, two roots that share an effective domain, prohibited membership,
prohibited appraisal root, policy-permitted consolidation that does not count as
diversity, and positive normal anchored progression.

## 15. Existing fixture migration

If control-plane policy becomes mandatory for all v1 decisions, migrate all 186
maintained fixtures atomically through the harness-owned manifest. Preserve
every existing expected outcome and normative intent. Positive fixtures receive
the smallest explicit current policy, complete applicable role memberships, and
admitted appraisal root. Negative fixtures receive the same neutral protected
baseline unless their hostile purpose targets this new layer.

No existing fixture may remain `AUTHORIZED` because a missing role membership
is treated as implicit separation. Migration is mechanical protected-context
addition, not a change to candidate fixture expectations.

## 16. Expected implementation surface

Expected files:

* `authority_lab/model.py` — strict immutable protected record parsers and role
  registry;
* `authority_lab/oracle.py` — exact role extraction, membership join,
  effective-domain comparison, appraisal closure/cycle checks, transitions,
  consolidation, and outcome reasons;
* `authority_lab/runner.py` — load/trace harness-owned context while rejecting
  candidate trusted-state injection;
* `authority_lab/README.md` — bounded semantics and trust boundary;
* `tests/test_authority_lab.py` — expectation-independent unit and hostile
  tests;
* `cases/authority_lab/trusted_anchor_state.json` — atomic protected migration;
* new fixtures continuing from `LAB-V1-186`.

No contract, architecture, schema-version, or invariant file should change.

## 17. Independent test obligations

Tests must establish independently of fixture expectations:

1. exact role extraction and immutable registry coverage;
2. candidate inability to supply protected control-plane state;
3. every selected role has exactly one current membership;
4. root, verifier, observer, orderer, anchor, adapter, witness,
   reconciliation, and recovery correlation fails closed where separation is
   required;
5. effective tuple equality defeats label/key/process multiplicity;
6. appraisal self-loops, two-node cycles, longer cycles, and unclosed chains
   fail closed;
7. appraisal roots cannot appraise a prohibited same-domain member;
8. quorum counts effective domains;
9. one independent contradiction cannot be outvoted;
10. hidden-controller-preserving rotation creates no independence;
11. authorized consolidation remains possible but counts once;
12. authorized separation and rotation remain possible;
13. recovery/reconciliation require independent membership;
14. prohibited current membership/appraiser yields `DENIED`;
15. fresh genesis, normal progression, survivor recovery, and fresh successor
    remain `AUTHORIZED`; and
16. all prior tests and fixtures preserve their outcomes.

## 18. Hostile design review

The proposed design was attacked as follows:

| Attack | Why it does not survive the design |
|---|---|
| Relabel one controller as many roles | Effective tuple, not role count, is compared. |
| Use many keys/signatures | Keys do not affect effective-domain count. |
| Use many processes/machines from one snapshot | Shared upstream/rollback tuple collapses them. |
| Root declares itself independent | Root requires a separate admitted appraisal root; self-edge fails. |
| A appraises B and B appraises A | Directed appraisal cycle fails closed. |
| Add a third node to hide the cycle | All cycles and unclosed chains fail. |
| Candidate supplies favorable membership | Candidate trusted-state keys are rejected; protected set is exact. |
| Root chooses only favorable domains | Applicable role registry and `ALL_APPLICABLE` policy prevent subsets. |
| Rotate labels while keeping controller | Transition preserves one effective authority and creates no diversity. |
| Rotate to a new controller without proof | Missing exact membership transition is `UNAVAILABLE`. |
| Consolidate roles silently | Missing exact allowed consolidation is `UNAVAILABLE`. |
| Use correlated reconciler/recovery authority | Membership comparison exposes same effective domain. |
| Outvote one independent contradiction | Conflict is fail-closed; no majority rule. |
| Compromise every appraisal source and history | Still locally indistinguishable; explicitly external, not falsely solved. |
| Block every positive path | Explicit appraisal-root admission, consolidation, separation, rotation, recovery, genesis, and successor paths remain. |

No reproducible in-scope collusion or circular-appraisal bypass survives these
rules. The only surviving case is total coordinated compromise/rollback of the
entire appraisal trust base with no independent contradictory state; that is
the stated external impossibility boundary.

## 19. Residual trust boundary

The implementation will still trust harness-owned protected context and the
admitted independence-appraisal root. Real controller ownership, key custody,
organizational independence, hardware isolation, rollback-domain truth,
instrumentation completeness, and external appraisal-root correctness remain
deployment preconditions. The deterministic oracle can validate exact admitted
relations and contradictions; it cannot observe a globally colluded world that
produces the same complete input as a legitimate world.

## 20. Frozen architecture determination

The six tuple coordinates, six invariants, three outcomes, and
`authority-lab-v1` schema are sufficient. The repair is an implementation of
existing evidence, discontinuity, boundary, use, continuity, and closure
semantics. No new public primitive is justified.

## 21. Exact hostile-design verdict

**PASS — NO REPRODUCIBLE IN-SCOPE CONTROL-PLANE COLLUSION, FALSE-INDEPENDENCE, OR CIRCULAR-APPRAISAL BYPASS SURVIVES THE PROPOSED DESIGN**

This is a design verdict, not proof of security. Executable implementation is
justified only as a separate atomic slice with migrated protected context,
hostile fixtures, independent tests, full validation, and exact-head review.
