# Frontier Delta: Control-Plane Collusion / Independence-Root Compromise

## 1. Exact baseline

This research slice starts from `19b6dd74a26026810ef53d32051d1d23e57db6b5`
on `fix/authority-lab-v1-anchor-currentness-independence`. Its parent is
`d5a19f8c36949d423cae92a30855d1cb16d34f3e`; the implementation parent is
`7eea7c85670c3d07ebaada61878c59b68dd6a2d0`.

At that exact state, 205/205 public tests and 186/186 maintained Authority Lab
fixtures pass. The schema remains `authority-lab-v1`, with six tuple
coordinates, six invariants, and three outcomes. The preceding hostile verdict
was:

> PASS — NO REPRODUCIBLE IN-SCOPE ADAPTER-CURRENTNESS, SOURCE-INDEPENDENCE, OR CROSS-DOMAIN RECONCILIATION COUNTEREXAMPLE FOUND

This delta does not modify executable code or maintained fixtures. It asks a
different question: whether the protected independence model covers the whole
control plane rather than only anchor adapters and witness sources.

## 2. Current authority roles

The implementation contains the following actual roles or relations. A name is
not treated as an independently controlled role unless the current model binds
it to protected control-domain facts.

| Role | Current executable representation | Protected control-domain appraisal? |
|---|---|---|
| Root / policy authority | `authority_root`, root-issued bindings and required-domain policy | No membership for the root itself |
| Orderer | `ordering_source_id`, ordering heads and event order | No |
| Verifier | `commitment_verifiers`, commitment verification, verifier-state anchor | No |
| Observer | observer admission, segments, lifecycle and handoff | No |
| Commitment producer | envelope observer/key/source relationships | No separate protected domain |
| Anchor | verifier-state anchor and harness-owned selected head | No protected domain for anchor authority; adapter is appraised |
| Anchor adapter | harness-owned adapter admission and `SOURCE_DOMAIN_MEMBERSHIP` | Yes |
| Witness | candidate admission joined to harness-owned witness membership | Yes, but the membership is root-issued |
| Reconciliation authority | root-issued `CROSS_DOMAIN_CHECKPOINT_RECONCILIATION` | No separate protected domain |
| Recovery authority | `recovery_authority_id` in recovery installation | No protected domain |

The current code correctly distinguishes role identity, key/credential
identity, process-like generations, source lineage, control domain, rollback
domain, independence domain, lifecycle, currentness, scope, and ordering **for
adapter and witness membership records**. It does not establish those
distinctions for every control-plane role.

## 3. Current independence model

The root selects an immutable required-domain policy. Harness-owned protected
contexts bind each required anchor adapter to identity, generation, source
lineage, upstream dependency, control domain, independence domain, rollback
domain, boundary, freshness, lifecycle, and event interval. Adapter source
tuples must be unique. Candidate fixtures cannot supply the protected context.

Witness admissions must exactly join protected witness membership. Witness
count alone is rejected; required nominal independence domains must be present,
and replacement requires an exact root-issued transition. Cross-domain anchor
disagreement returns `UNAVAILABLE` unless exact root-authorized reconciliation
applies.

The trust edge that remains is decisive: the root both selects the required
domains and issues the membership/appraisal facts, while the root, orderer,
verifier, observer, anchor, reconciliation authority, and recovery authority
have no corresponding protected domain membership. Thus protected membership
answers “what did this admitted root classify?” rather than independently
establishing whether that root and the classified roles share a controller.

## 4. Control domain versus role multiplicity

The following are distinct facts and are not interchangeable:

1. role identity;
2. credential or key identity;
3. process identity;
4. source lineage;
5. control domain;
6. rollback domain;
7. independence domain;
8. policy authority;
9. appraisal authority;
10. recovery authority;
11. reconciliation authority;
12. currentness;
13. lifecycle; and
14. authority scope.

Different role labels, keys, processes, machines, or organizational names can
still share one effective controller, one upstream source, or one rollback
domain. Conversely, co-location does not automatically prove common control.
The required fact is an authoritative, current, scoped relationship, not a
name-based inference or a naked `trusted=true` / `independent=true` flag.

## 5. Hostile matrix A–AV

“Current” describes executable behavior or, where the missing relationship
cannot be encoded, the outcome of the identical admitted input in both external
worlds. “Fits” means a repair appears expressible through existing v1 relational
facts and invariants.

| ID | Hostile case | Current result | Desired result / classification | Fits 6/6/3? |
|---|---|---|---|---|
| A | Root + verifier share one controller | `AUTHORIZED` remains possible; relation absent | `UNAVAILABLE`; executable input-collapse defect | Yes |
| B | Root + orderer share one controller | `AUTHORIZED` remains possible | `UNAVAILABLE`; defect | Yes |
| C | Root + observer share one controller | `AUTHORIZED` remains possible | `UNAVAILABLE`; defect | Yes |
| D | Root + anchor adapter share one controller | Adapter is appraised by the same root; `AUTHORIZED` remains possible | `UNAVAILABLE`; circular appraisal defect | Yes |
| E | Verifier + witness share one controller | No verifier membership to compare; `AUTHORIZED` remains possible | `UNAVAILABLE`; defect | Yes |
| F | Verifier + anchor share one controller | Exact labels bind, effective control does not | `UNAVAILABLE`; defect | Yes |
| G | Observer + witness share one controller | No observer domain membership | `UNAVAILABLE`; defect | Yes |
| H | Anchor + witness share one controller | No anchor-authority domain membership | `UNAVAILABLE`; defect | Yes |
| I | Reconciler controlled by one conflicting domain | Root-issued reconciliation can select a head | `UNAVAILABLE` absent independent reconciliation appraisal; defect | Yes |
| J | Recovery authority controlled by selected anchor | ID inequality checks do not prove control separation | `UNAVAILABLE`; defect | Yes |
| K | Several role keys, one controller | Keys can all validate | `UNAVAILABLE`; key multiplicity is not independence | Yes |
| L | Several role IDs, one source lineage | Role relations can validate | `UNAVAILABLE`; defect | Yes |
| M | Several role processes, one rollback domain | Process generations can validate | `UNAVAILABLE`; defect | Yes |
| N | Several machines, common snapshot lineage | Locally current records can validate | `UNAVAILABLE`; defect unless independently anchored | Yes |
| O | Role rotation keeps hidden controller | Authorized rotation can remain `AUTHORIZED` | `UNAVAILABLE` until current domain transition established | Yes |
| P | Root rotation keeps hidden controller | Root generation changes do not prove separation | `UNAVAILABLE`; defect | Yes |
| Q | Verifier rotation keeps hidden controller | Rotation proves lineage, not controller diversity | `UNAVAILABLE`; defect | Yes |
| R | Anchor rotation keeps hidden controller | Rotation proves authorized continuity only | `UNAVAILABLE`; defect | Yes |
| S | Witness rotation keeps hidden controller | Exact handoff passes if root says so | `UNAVAILABLE` absent independent appraisal | Yes |
| T | All quorum roles share one failure domain | No general control-plane quorum model | `UNAVAILABLE`; quorum count cannot substitute | Yes |
| U | Majority share one failure domain | Majority is not used as authority, but correlated roles can support facts | `UNAVAILABLE` if independence is required | Yes |
| V | 2-of-3 nominal roles, two effective authorities are one | Nominal threshold is not an independence proof | `UNAVAILABLE` | Yes |
| W | 3-of-5 labels, one upstream controller | Nominal threshold is not an independence proof | `UNAVAILABLE` | Yes |
| X | Correlated roles fabricate one consistent history | Can be `AUTHORIZED` if all admitted relations agree | `UNAVAILABLE`; executable input-collapse defect | Yes |
| Y | Correlated roles suppress a conflict | Silence plus admitted coverage can support authority | `UNAVAILABLE` if independent coverage is not established | Yes |
| Z | Correlated root, policy, and witnesses select favorable evidence | Root-selected protected data can be internally exact | `UNAVAILABLE`; defect | Yes |
| AA | Correlated reconciler selects favorable head | Exact root-issued reconciliation can authorize | `UNAVAILABLE`; defect | Yes |
| AB | Correlated recovery authority selects favorable history | Exact recovery can authorize | `UNAVAILABLE`; defect | Yes |
| AC | One genuinely independent current source contradicts correlated majority | Existing required-domain conflict path returns `UNAVAILABLE` | Correctly blocked; no voting | Yes |
| AD | One independent current source exposes rollback | Existing survivor comparison returns `UNAVAILABLE` | Correctly blocked | Yes |
| AE | Two genuinely independent domains agree | `AUTHORIZED` positive paths exist | `AUTHORIZED` | Yes |
| AF | Two genuinely independent domains conflict | `UNAVAILABLE / CROSS_DOMAIN_CHECKPOINT_CONFLICTING` | `UNAVAILABLE` | Yes |
| AG | Authorized role consolidation | No exact control-plane consolidation relation | `AUTHORIZED` only if current policy explicitly permits reduced separation; implementation obligation | Yes |
| AH | Unauthorized role consolidation | Can be invisible for unappraised roles | `UNAVAILABLE`; defect | Yes |
| AI | Authorized separation into new domains | Adapter/witness transitions partly support this | `AUTHORIZED` with exact independent appraisal and transition | Yes |
| AJ | Stable role ID, changed control-domain membership | Invisible for most roles | `UNAVAILABLE`; defect | Yes |
| AK | Stale control-domain classification | Adapter/witness freshness is checked; other roles absent | `UNAVAILABLE`; partial block plus gap | Yes |
| AL | Candidate supplies classification | Candidate protected contexts are rejected | `UNAVAILABLE`; correctly blocked | Yes |
| AM | Appraiser is inside domain it appraises | Root currently appraises memberships without its own membership | `UNAVAILABLE`; circular-appraisal defect | Yes |
| AN | A says B independent; B says A independent | No explicit cycle detector; equivalent root-supported cycle can pass | `UNAVAILABLE`; defect | Yes |
| AO | Root self-declares independence | Root-issued membership is accepted; root itself is unappraised | `UNAVAILABLE`; defect | Yes |
| AP | Adapter self-declares upstream independence | Candidate assertion alone is blocked by protected join | `UNAVAILABLE`; correctly blocked | Yes |
| AQ | Witness self-declares independence | Candidate assertion alone is blocked by protected join | `UNAVAILABLE`; correctly blocked | Yes |
| AR | Every appraisal authority and history compromised/rolled back | Indistinguishable from legitimate state | External impossibility / trust boundary | No local repair |
| AS | Total compromise except one current independent comparison source | Existing survivor path rejects replay | `UNAVAILABLE`; correctly blocked | Yes |
| AT | Fresh genesis with established domain separation | Positive genesis remains reachable | `AUTHORIZED` | Yes |
| AU | Recovery using surviving independent authority | Positive survivor recovery remains reachable | `AUTHORIZED` | Yes |
| AV | Fresh successor after control-plane recovery | Positive successor path remains reachable | `AUTHORIZED` | Yes |

## 6. Executable reproducers

### R1 — two external worlds collapse into one oracle input

`LAB-V1-134` is a maintained positive fixture. At the baseline it returns:

```text
AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED
```

Its protected source memberships cover only `ADAPTER` and `WITNESS_SOURCE`.
There is no protected membership for the root, orderer, verifier, observer,
commitment producer, anchor authority, reconciliation authority, or recovery
authority. Therefore these two worlds produce byte-identical oracle input:

* W1: root, verifier, observer, orderer, anchor authority, and appraisers are
  genuinely independently controlled;
* W2: one controller holds all those roles, keys, processes, and admitted
  records while preserving every identifier, digest, ordering, freshness, and
  lifecycle value.

W1 may legitimately authorize. W2 should be `UNAVAILABLE` when independence is
part of the authority objective, yet the current oracle returns `AUTHORIZED`
for the shared input. This is reproducible at the observation/control-plane
boundary: the defect is the missing protected relation, not malformed data.

### R2 — root appraisal is not independently appraised

For the same fixture, the harness-owned `required_domain_policy`, adapter
membership, and witness memberships all use
`source_id=ROOT-AUTH-BOUNDARY-1`. The root itself has no `control_domain`,
`rollback_domain`, `independence_domain`, or separately authorized appraisal
source. The code proves exact agreement with the root's classification; it
does not prove that the classifier is outside the classified control domain.
The result remains `AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED`.

### R3 — existing defenses are real but narrower

Direct hostile mutations confirm that candidate-supplied protected context,
shared adapter source tuples, missing required domains, conflicting protected
views, witness count without required protected domains, and a surviving
independent rollback report all fail closed. They do not repair R1/R2 because
the absent role-domain relationship cannot be compared.

## 7. Reproducible counterexample

Yes. R1/R2 establish an in-scope counterexample:

```text
schema-valid exact positive input
+ root-issued protected classifications
+ no protected appraisal of root/control-plane role membership
+ external world in which one controller owns the supporting roles
-> AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED
```

The expected result is `UNAVAILABLE`, not `DENIED`, because no authoritative
fact proves prohibition; the missing fact is independent, current appraisal of
effective control and rollback separation.

This is one semantic defect with many role-pair manifestations. It does not
justify one invariant per role or a blacklist of role combinations.

## 8. Quorum analysis

The lab correctly avoids ordinary majority voting for conflicting anchor
views. Nonetheless, a quorum or threshold over nominal roles would not close
this frontier. Quorum safety assumptions count independently failing members;
two keys or five process labels under one controller constitute one effective
failure domain for this purpose. Quorum intersection is useful only after the
membership and fault-domain assumptions are themselves established.

One independently current contradictory source must force `UNAVAILABLE`
regardless of a larger correlated majority. The existing protected-domain
conflict behavior already follows that rule.

## 9. Key-diversity analysis

Keys establish credential diversity and permit attribution to key identities.
They do not establish different operators, source lineages, machines, control
domains, rollback domains, or appraisal authorities. Threshold signatures can
distribute key operations, but their security assumptions still depend on who
controls the participants and their shares. Key count must never be promoted
to independence count.

## 10. Role-rotation analysis

Current rotation checks establish exact predecessor/successor identity,
generation, ordering, freshness, and root authorization for selected roles.
They do not prove that the successor moved to, or remained in, a separately
controlled domain. A safe rotation must bind old and new protected membership,
effective controller/source/rollback relationships, appraisal authority, and
policy scope. Stable hidden control across label/key rotation is not new
independence.

## 11. Independence-appraisal analysis

Independence must be a typed relation with at least: member role and exact
identity/generation, source lineage, control domain, rollback domain,
independence domain, applicable boundary, authority scope, membership epoch,
lifecycle, ordering, freshness, and appraisal source. The appraiser must itself
have an admitted authority chain suitable for this scope.

The current fields can carry those meanings; the defect is incomplete role
coverage and appraisal-root closure. `evidence_binding`,
`binding_source_authority`, `freshness`, `binding_ordering`,
`binding_lifecycle`, protected policy, verifier-state anchoring, and existing
membership/transition structures appear sufficient for a repair.

## 12. Circular-appraisal analysis

These chains must fail closed:

```text
root classifies adapter/witness as independent
-> classified roles support the root-selected current history
-> that history is used to treat the root classification as authoritative
```

and:

```text
A appraises B; B appraises A; no admitted external appraisal root
```

Cycle detection alone is insufficient: an acyclic chain ending at an
unappraised self-authorizing source has the same problem. The chain must end at
an explicitly admitted appraisal trust root or independently surviving source,
with its residual trust assumption stated.

## 13. Recovery and reconciliation collusion

Recovery and reconciliation are especially authority-sensitive because they
select one history after loss or conflict. Exact receipts and root signatures
prove what was selected, not that the selector was independent of the selected
branch. Their authority therefore needs exact scope plus protected controller,
source, rollback, and appraisal lineage. A recovery/reconciliation authority
inside the favored branch's effective control domain cannot alone resolve the
branch.

## 14. One surviving independent source

When one genuinely independent, current, correctly scoped source contradicts
a correlated set, the result is `UNAVAILABLE`; majority size does not erase the
conflict. Existing required-domain conflict and survivor rollback fixtures
already demonstrate the desired behavior. The repair should generalize that
rule to protected control-plane membership rather than replace it.

## 15. Total-collusion boundary

If every root, verifier, anchor, adapter, witness, reconciliation authority,
recovery authority, appraisal source, and candidate history is controlled or
rolled back together, and no contradictory state survives, a deterministic
local oracle receives the same input as in a legitimate current world. It
cannot distinguish them.

That is an external impossibility/trust boundary, not an excuse to accept
detectable partial correlation. A repair can require an admitted independent
appraisal root or survivor and fail closed when it is absent. It cannot create
independence from locally consistent assertions after total compromise.

## 16. Positive controls

The following must remain reachable after any repair:

| Positive control | Required result |
|---|---|
| Independently appraised root and verifier domains agree | `AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED` |
| Independently appraised verifier and witness agree | `AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED` |
| Authorized rotation preserves exact independent-domain membership | `AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED` |
| Explicit policy permits role consolidation and does not claim diversity | `AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED` |
| Authorized separation establishes new protected domains | `AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED` |
| One survivor exposes rollback | `UNAVAILABLE`, then recovery may re-establish authority |
| Recovery uses a surviving independent authority | `AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED` |
| Fresh successor satisfies all existing and independence requirements | `AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED` |
| Fresh genesis establishes appraisal root and role-domain policy | `AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED` |

Safety must not be defined as permanent refusal. Explicitly authorized
consolidation can be valid when policy requires no false multiplicity claim;
what is forbidden is using consolidated roles as if they were independent.

## 17. Invariant mapping

| Existing invariant | Application |
|---|---|
| `INV-CONT` | Role/domain membership, rotations, and appraisal lineage must remain continuous and current. |
| `INV-DISC` | Distinct labels/keys/processes must not manufacture distinct effective authorities. |
| `INV-BND` | Independence and appraisal apply only to exact boundaries and epochs. |
| `INV-EVD` | Independence claims require exact authoritative evidence and cannot self-support. |
| `INV-USE` | Recovery/reconciliation authority cannot be replayed or widened to a new controller/domain. |
| `INV-CLO` | The authority graph must close at an admitted appraisal root without cycles or missing role membership. |

The defect is coverage and closure within these invariants, not an absent
seventh invariant.

## 18. Contract sufficiency

The frozen public architecture remains sufficient. Control-plane independence
is authority-relevant relational evidence, not a seventh tuple coordinate.
Missing or ambiguous appraisal maps naturally to `UNAVAILABLE`; explicit
current prohibition remains `DENIED`; exact current independent establishment
can remain `AUTHORIZED`. No schema version change or fourth outcome is needed.

## 19. Possible repair directions

A design-only next slice is justified. The smallest plausible repair should:

1. extend the immutable protected membership model to every authority role
   actually relied upon by the selected decision path;
2. define a root-selected role-separation policy without allowing the root to
   prove its own separation;
3. require an admitted independence-appraisal root or surviving appraisal
   source, exact scope, freshness, lifecycle, ordering, and boundary;
4. compare effective tuples `(source_lineage, control_domain,
   upstream_dependency, rollback_domain)` across roles whenever policy requires
   separation;
5. reject appraisal cycles and chains ending in self-authorization;
6. bind rotation, consolidation, recovery, and reconciliation to current
   protected membership transitions; and
7. preserve explicit authorized consolidation and all positive paths.

No executable repair is authorized by this research commit.

## 20. Prior-art notes

These are bounded analogies, not claims that Ground Truth implements or
improves the cited systems.

* Byzantine state-machine replication assumes a set of mutually distrusting
  processes and explicit fault bounds; nominal replica count is not meaningful
  when failures are common-mode. NIST IR 8460 is useful background for the
  consensus and Byzantine-adversary assumptions.
* Quorum intersection constrains incompatible decisions only under its member
  and fault assumptions. It does not prove that nominal members are controlled
  independently.
* FROST (RFC 9591) distributes a signing operation across a threshold of
  participants. That is key-share distribution, not proof of operational or
  rollback-domain independence.
* Transparency-log witnesses and gossip motivate cross-view comparison; they
  still require meaningful source diversity and currentness.
* Remote-attestation systems separate evidence production and appraisal and
  depend on reliable device identity and appraisal roots. TCG materials are a
  useful analogy for identity/measurement chains, not evidence that a key or
  platform is independently governed.
* Separation of duties, N-version diversity, and independent monitoring all
  target common-mode control, but their benefit depends on independently
  established organizational, implementation, or fault-domain assumptions.

References consulted: NIST IR 8460 (state-machine replication and Byzantine
adversaries), RFC 9591 (FROST threshold signatures), and Trusted Computing
Group material on device identity and remote attestation.

## 21. Exact hostile-research verdict

**FAIL — REPRODUCIBLE IN-SCOPE CONTROL-PLANE COLLUSION OR INDEPENDENCE COUNTEREXAMPLE FOUND**

The current lab rigorously checks adapter and witness domain claims, but role
multiplicity does not prove independence, key multiplicity does not prove
independence, quorum cannot substitute for independence, and root-issued
membership is circular when the root/control plane itself is the object of the
independence claim. A single surviving independent contradiction already fails
closed. Total coordinated compromise with no surviving comparison source
remains externally indistinguishable and outside any deterministic local
repair.

PASS would mean only failure to falsify within the modeled scope, not proof of
security. This slice instead falsified the whole-control-plane independence
assumption and justifies a design-only repair.
