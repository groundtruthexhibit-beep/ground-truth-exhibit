# Composite Adversarial Control Continuity

## 1. Exact baseline

This final pre-freeze composite review starts from
`4e1eae61136fdda078c5e38f71e0f62f83fa92f9`, the reviewed Authority Lab v1
Canonical T3 Execution-Event Authority Convergence implementation. The baseline
has 257 public tests, 443 maintained fixtures, schema `authority-lab-v1`, six
tuple coordinates, six invariants, and the three outcomes `AUTHORIZED`,
`DENIED`, and `UNAVAILABLE`.

The review changes no executable oracle or model code. It adds independently
expected composite fixtures and tests that exercise already protected joins.

## 2. Composite question and threat model

The question is whether individually repaired controls remain correct when
legitimate and adversarial transitions are composed. The target is not a local
module failure. It is a chain in which each local record appears plausible but
the combined authority history should not authorize the terminal effect.

The common join point is the protected canonical T3 execution event. Human
approval, delegation, tool/connector use, successor and boundary state,
verifier/anchor state, control-plane membership, and terminal use must either
name that event or prove protected applicability across it. A historical
`AUTHORIZED` result is never a substitute for that convergence.

## 3. Composite cases C1-C18

| Case | Ordered composition | Expected and observed result | Controlling reason |
|---|---|---|---|
| C1 | Human approval -> delegation -> hidden backend -> T3 | `UNAVAILABLE` | Actual tool use does not match the protected execution target. |
| C1+ | Human approval -> delegation -> exact backend -> T3 | `AUTHORIZED` | All three layers converge on the same protected event and effect. |
| C2 | Approval -> queue cache -> revocation -> T3 | `DENIED` | Current authoritative approval revocation dominates the cached verdict. |
| C3 | Delegation -> successor -> rotated target -> T3 | `UNAVAILABLE` | Predecessor identity and tool context cannot transfer to the successor. |
| C3+ | Fresh successor -> fresh tool authority -> T3 | `AUTHORIZED` | Successor-specific protected authority is current. |
| C4 | Shutdown -> label ABA -> apparent predecessor state | `UNAVAILABLE` | Path discontinuity survives endpoint label restoration. |
| C5 | Verifier recovery -> anchor rotation -> coverage gap | `UNAVAILABLE` | Current protected control/source coverage is incomplete. |
| C6 | Snapshot restore -> stale approval and delegation | `UNAVAILABLE` | The authority heads do not converge at T3. |
| C7 | Control-plane rotation -> recovery -> stale membership | `UNAVAILABLE` | Protected control-plane membership does not cover T3. |
| C8 | Cross-domain reconciliation -> successor ABA | `UNAVAILABLE` | Reconciliation cannot launder identity discontinuity. |
| C9 | One-shot approval -> failed attempt -> retry | `UNAVAILABLE` | The protected approval use is already consumed. |
| C9+ | Retry -> fresh approval -> same exact composite effect | `AUTHORIZED` | Fresh use-specific approval converges at T3. |
| C10 | Partial execution -> approval revocation -> continuation | `DENIED` | The later material effect encounters current revocation. |
| C11 | Partial execution -> boundary change -> continuation | `UNAVAILABLE` | The later effect lacks exact boundary convergence. |
| C12 | Policy drift -> backend migration -> delayed execution | `UNAVAILABLE` | Old policy and target state cannot satisfy the current T3 join. |
| C13 | Two approvals -> one effective source domain -> delegation | `UNAVAILABLE` | Signature/count multiplicity is not approver independence. |
| C14 | Recovery -> stale pre-recovery verifier state -> T3 | `UNAVAILABLE` | T3 binds the wrong verifier-state digest. |
| C15 | Fresh approval -> candidate tool shopping | `UNAVAILABLE` | Candidate-selected favorable backend differs from protected selection. |
| C16 | Fresh delegation -> revoked approval -> T3 | `DENIED` | One valid layer cannot override approval revocation. |
| C17 | Fresh approval -> revoked delegation -> T3 | `DENIED` | One valid layer cannot override delegation revocation. |
| C18 | Fresh approval -> fresh delegation -> protected tool -> T3 | `AUTHORIZED` | Every required authority layer converges on one terminal event. |

Fixtures `LAB-V1-444` through `LAB-V1-466` encode this matrix, including
unchanged delayed execution and successor-after-recovery positive controls.
Expectations were fixed before execution and are not derived from oracle output.

## 4. Cross-module conclusions

### Human Approval and Delegation

Approval authority and delegation authority remain separate. Neither can repair
the other. Revocation at either required layer is `DENIED`; stale, replayed, or
non-convergent evidence is `UNAVAILABLE`. A fresh exact approval and a fresh
exact delegation can compose positively.

### Tool, connector, and effect target

A stable logical label never replaces the protected logical-tool -> connector
-> backend -> effect-capable-target join. Approval and delegation may both be
locally valid while hidden backend substitution still fails at terminal use.
Candidate recomputation or tool shopping cannot alter the harness-owned current
context.

### Successor, shutdown, and boundary continuity

Predecessor authority does not transfer merely because labels, state, or an
execution context reappear. Shutdown and identity-discontinuous history remain
path-relevant. Fresh successor-specific authority remains reachable.

### Verifier, anchor, witness, and control-plane continuity

Recovery does not manufacture authority. The T3 event binds the selected
verifier state, while independently protected anchor and control-plane records
must remain current. Anchor rotation, recovery, or reconciliation cannot hide a
coverage gap or stale protected membership.

### Queue, retry, and partial execution

Queues may retain intent and evidence references, but not current authority.
Retries and later material effects receive a current terminal event and must
revalidate. A cached `AUTHORIZED` string loses to protected revocation state.
One-shot use state survives retry. Boundary or policy changes before a later
effect require fresh convergence.

## 5. Invariant and contract mapping

No new public primitive is necessary. `INV-CONT`, `INV-DISC`, `INV-BND`,
`INV-EVD`, `INV-USE`, and `INV-CLO` jointly cover the composite traces through
existing typed evidence, source authority, lifecycle, ordering, freshness,
mutation-registry, durable verifier, protected tool context, approval,
delegation, and canonical T3 relations.

The schema remains `authority-lab-v1`; the public tuple remains six-dimensional;
the invariant set remains six; outcomes remain three. Composite closure is a
join obligation, not a seventh invariant or coordinate.

## 6. Exact-head hostile review

The review independently attacked hidden backend substitution through a fully
valid approval and delegation chain; queue caching after revocation; successor
and shutdown ABA; verifier recovery with stale or incomplete protected context;
snapshot replay; one-shot retry; partial continuation; policy drift; shared-
source approver multiplicity; tool shopping; and attempts to let a valid layer
override a revoked one. Every hostile case failed closed with the specified
`DENIED` versus `UNAVAILABLE` discipline.

Positive controls established that the repair set is not vacuous: a complete
fresh approval/delegation/tool/T3 chain, delayed execution whose protected
authority actually covers T3, a fresh successor, retry after fresh reapproval,
and successor-after-recovery all reach `AUTHORIZED / CURRENT_AUTHORITY_ESTABLISHED`.

Verdict:

**PASS — NO REPRODUCIBLE IN-SCOPE COMPOSITE AUTHORITY-CONTINUITY COUNTEREXAMPLE FOUND**

This means failure to falsify the composed deterministic model within the
admitted scope. It is not proof of security in external runtimes.

## 7. Residual trust boundary and freeze decision

The oracle cannot detect a real-world event omitted before protected evidence is
constructed, compromise or coordinated falsehood of every admitted root and
independent source, failures in signature/appraisal truth, or effects executed
outside the modeled terminal-use path. Instrumentation completeness, durable
storage and anchor integrity, actual source independence, and faithful effect
execution remain external preconditions.

No new in-scope composite defect or contract gap was found. The next work is not
another authority frontier. It is research freeze, counterexample cataloging,
threat-model consolidation, reproducibility packaging, and paper preparation.

**RESEARCH FREEZE GATE — ELIGIBLE**
